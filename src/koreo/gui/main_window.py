"""Application shell sharing one project and playback session between views."""

from dataclasses import replace
from fractions import Fraction
from pathlib import Path

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QProgressBar,
    QSlider,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from koreo.audio import AudioProbe, AudioSource, WaveformExtractor
from koreo.domain.calibration import BeatCalibration, CalibrationError, parse_bpm
from koreo.domain.models import Project
from koreo.domain.structure import rebase_structure
from koreo.gui.bpm_dialog import BpmDialog
from koreo.gui.sheet import SheetView
from koreo.gui.structure_panel import StructurePanel
from koreo.gui.timeline import TimelineView
from koreo.gui.waveform import WaveformWidget
from koreo.playback import PlaybackController
from koreo.presentation.mapping import build_sheet, build_timeline


class MainWindow(QMainWindow):
    """Host Timeline and Sheet tabs for one immutable project instance."""

    play_pause_requested = Signal()

    # [GH-9] [S-M1-06] Both tabs derive from the same Project object.

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.audio_source: AudioSource | None = None
        self.tempo_bpm = Fraction(120)
        self._probe = AudioProbe(self)
        self._probe.succeeded.connect(self._audio_ready)
        self._probe.failed.connect(self._audio_failed)
        self._waveform_extractor = WaveformExtractor(self)
        self._waveform_extractor.succeeded.connect(self._waveform_ready)
        self._waveform_extractor.failed.connect(self._waveform_failed)
        self.playback = PlaybackController(self)
        self.playback.position_changed.connect(self._position_changed)
        self.playback.duration_changed.connect(self._duration_changed)
        self.playback.state_changed.connect(self._playback_state_changed)
        self.playback.failed.connect(self._playback_failed)
        application = QApplication.instance()
        assert application is not None
        application.installEventFilter(self)
        self.play_pause_requested.connect(self._toggle_playback)
        self.timeline_view = TimelineView(build_timeline(project))
        self.sheet_view = SheetView(build_sheet(project))
        self.structure_panel = StructurePanel(project)
        self.structure_panel.project_changed.connect(self._structure_project_changed)
        self.structure_panel.anchor_block_requested.connect(
            self._anchor_structure_block
        )
        self.structure_panel.position_requested.connect(self._seek_to_structure_beat)
        self.choose_song_button = QPushButton("Choose song…")
        self.choose_song_button.clicked.connect(self._choose_song)
        self.song_label = QLabel("No song selected")
        self.song_label.setWordWrap(True)
        self.tap_bpm_button = QPushButton("Tap BPM")
        self.tap_bpm_button.setEnabled(False)
        self.tap_bpm_button.clicked.connect(self._open_bpm_dialog)
        self.bpm_edit = QLineEdit("120")
        self.bpm_edit.setAccessibleName("Manual BPM")
        self.bpm_edit.setMaximumWidth(90)
        self.bpm_edit.editingFinished.connect(self._manual_bpm_changed)
        self.continuous_counts = QCheckBox("Continuous beat numbers")
        self.continuous_counts.toggled.connect(
            self.timeline_view.set_show_continuous_counts
        )
        self.continuous_counts.toggled.connect(
            self.sheet_view.set_show_continuous_counts
        )

        song_bar = QHBoxLayout()
        song_bar.addWidget(self.choose_song_button)
        song_bar.addWidget(self.song_label, 1)
        song_bar.addWidget(QLabel("BPM:"))
        song_bar.addWidget(self.bpm_edit)
        song_bar.addWidget(self.tap_bpm_button)

        count_bar = QHBoxLayout()
        count_bar.addWidget(QLabel("Count origin:"))
        self.count_origin_edit = QLineEdit(str(project.count_origin))
        self.count_origin_edit.setMaximumWidth(80)
        self.count_origin_edit.editingFinished.connect(self._count_origin_changed)
        count_bar.addWidget(self.count_origin_edit)
        count_bar.addWidget(QLabel("Default group:"))
        self.count_group_spin = QSpinBox()
        self.count_group_spin.setRange(1, 64)
        self.count_group_spin.setValue(project.default_count_group)
        self.count_group_spin.valueChanged.connect(self._count_group_changed)
        count_bar.addWidget(self.count_group_spin)
        count_bar.addWidget(self.continuous_counts)
        count_bar.addStretch(1)

        self.transport = QWidget()
        transport_layout = QVBoxLayout(self.transport)
        transport_layout.setContentsMargins(0, 0, 0, 0)
        controls = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self._toggle_playback)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.playback.stop)
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderMoved.connect(self.playback.seek)
        self.time_label = QLabel("0:00.000 / 0:00.000")
        self.time_label.setFixedWidth(
            self.time_label.fontMetrics().horizontalAdvance("99:59.999 / 99:59.999")
        )
        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        controls.addWidget(self.play_button)
        controls.addWidget(self.stop_button)
        controls.addWidget(self.seek_slider, 1)
        controls.addWidget(self.time_label)
        transport_layout.addLayout(controls)

        self.waveform = WaveformWidget()
        self.waveform.set_bpm(float(self.tempo_bpm))
        self.waveform.seek_requested.connect(self.playback.seek)
        transport_layout.addWidget(self.waveform)
        calibration_controls = QHBoxLayout()
        self.processing_indicator = QProgressBar()
        self.processing_indicator.setRange(0, 0)
        self.processing_indicator.setFormat("Processing song…")
        self.processing_indicator.setMaximumWidth(170)
        self.processing_indicator.setVisible(False)
        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.setToolTip("Zoom waveform out")
        self.zoom_out_button.clicked.connect(self.waveform.zoom_out)
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setToolTip("Zoom waveform in")
        self.zoom_in_button.clicked.connect(self.waveform.zoom_in)
        self.zoom_fit_button = QPushButton("Fit")
        self.zoom_fit_button.setToolTip("Show the full waveform")
        self.zoom_fit_button.clicked.connect(self.waveform.zoom_to_fit)
        self.follow_button = QPushButton("Follow")
        self.follow_button.setCheckable(True)
        self.follow_button.setChecked(True)
        self.follow_button.setToolTip("Keep the playhead at a fixed offset")
        self.follow_button.toggled.connect(self.waveform.set_follow_playhead)
        self.waveform.follow_changed.connect(self.follow_button.setChecked)
        self.anchor_button = QPushButton("Set playhead as grid anchor")
        self.anchor_button.clicked.connect(self._set_anchor)
        self.anchor_label = QLabel("Grid anchor not set")
        self.refine_beat_edit = QLineEdit()
        self.refine_beat_edit.setPlaceholderText("Later beat, e.g. 128")
        self.refine_beat_edit.setMaximumWidth(150)
        self.refine_button = QPushButton("Match beat to playhead")
        self.refine_button.setEnabled(False)
        self.refine_button.clicked.connect(self._set_calibration_point)
        calibration_controls.addWidget(self.processing_indicator)
        calibration_controls.addWidget(QLabel("Waveform zoom:"))
        calibration_controls.addWidget(self.zoom_out_button)
        calibration_controls.addWidget(self.zoom_in_button)
        calibration_controls.addWidget(self.zoom_fit_button)
        calibration_controls.addWidget(self.follow_button)
        calibration_controls.addSpacing(12)
        calibration_controls.addWidget(self.anchor_button)
        calibration_controls.addWidget(self.anchor_label)
        calibration_controls.addStretch(1)
        calibration_controls.addWidget(self.refine_beat_edit)
        calibration_controls.addWidget(self.refine_button)
        transport_layout.addLayout(calibration_controls)
        self.transport.setVisible(False)

        self.tabs = QTabWidget()
        self.tabs.setAccessibleName("Project view selector")
        self.tabs.addTab(self.timeline_view, "Timeline")
        self.tabs.addTab(self.sheet_view, "Sheet")
        self.tabs.addTab(self.structure_panel, "Structure")
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(song_bar)
        layout.addLayout(count_bar)
        layout.addWidget(self.transport)
        layout.addWidget(self.tabs, 1)
        self.setCentralWidget(central)
        self.setWindowTitle(f"Koreo — {project.name}")
        self.resize(1100, 700)

    def _choose_song(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "Choose song", "", "Audio files (*.mp3 *.wav)"
        )
        if selected:
            self.load_song(Path(selected))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Reserve Space for main-window playback across focused controls."""

        del watched
        application = QApplication.instance()
        assert application is None or isinstance(application, QApplication)
        if (
            event.type() == QEvent.Type.KeyPress
            and event.key() == Qt.Key.Key_Space  # type: ignore[attr-defined]
            and self.isActiveWindow()
            and application is not None
            and application.activeModalWidget() is None
        ):
            if not event.isAutoRepeat():  # type: ignore[attr-defined]
                self.play_pause_requested.emit()
            return True
        return False

    def load_song(self, path: Path) -> None:
        """Validate a selected song without replacing the last valid source."""

        self.choose_song_button.setEnabled(False)
        self.song_label.setText(f"Checking {path.name}…")
        self._probe.probe(path)

    def _audio_ready(self, source: object) -> None:
        assert isinstance(source, AudioSource)
        self.audio_source = source
        self.project = replace(self.project, calibration=None)
        self.waveform.set_peaks(())
        self.waveform.set_anchor(None)
        self.waveform.zoom_to_fit()
        self.waveform.set_follow_playhead(True)
        self.anchor_label.setText("Grid anchor not set")
        self.refine_button.setEnabled(False)
        self.song_label.setText(
            f"{source.display_name} — {source.sample_rate} Hz, "
            f"{source.channel_count} channel(s)"
        )
        self.choose_song_button.setEnabled(True)
        self.tap_bpm_button.setEnabled(True)
        self.transport.setVisible(True)
        self.playback.load(source.path)
        self.processing_indicator.setVisible(True)
        self.song_label.setText(f"{self.song_label.text()} · building waveform…")
        self._waveform_extractor.extract(source.path)

    def _audio_failed(self, message: str) -> None:
        if self.audio_source is None:
            self.song_label.setText(message)
        else:
            self.song_label.setText(
                f"{self.audio_source.display_name} — new selection failed: {message}"
            )
        self.choose_song_button.setEnabled(True)

    def _open_bpm_dialog(self) -> None:
        if self.audio_source is None:
            return
        dialog = BpmDialog(self.audio_source, self)
        if dialog.exec() and dialog.result_bpm is not None:
            self.tempo_bpm = dialog.result_bpm
            self.bpm_edit.setText(
                f"{float(self.tempo_bpm):.3f}".rstrip("0").rstrip(".")
            )
            self.waveform.set_bpm(float(self.tempo_bpm))
            self._update_calibration_bpm()

    def _manual_bpm_changed(self) -> None:
        try:
            self.tempo_bpm = parse_bpm(self.bpm_edit.text())
            self.waveform.set_bpm(float(self.tempo_bpm))
            self._update_calibration_bpm()
        except CalibrationError:
            self.bpm_edit.setText(
                f"{float(self.tempo_bpm):.3f}".rstrip("0").rstrip(".")
            )

    def _count_origin_changed(self) -> None:
        try:
            origin = Fraction(self.count_origin_edit.text().strip())
        except (ValueError, ZeroDivisionError):
            self.count_origin_edit.setText(str(self.project.count_origin))
            return
        self.project = replace(self.project, count_origin=origin)
        self._refresh_count_views()

    def _count_group_changed(self, group_size: int) -> None:
        self.project = replace(self.project, default_count_group=group_size)
        self._refresh_count_views()

    def _refresh_count_views(self) -> None:
        timeline_model = build_timeline(self.project)
        sheet_model = build_sheet(self.project)
        self.timeline_view.model = timeline_model
        self.timeline_view.canvas.model = timeline_model
        self.timeline_view.canvas.update()
        self.sheet_view.model = sheet_model
        self.sheet_view.canvas.model = sheet_model
        self.sheet_view.canvas.update()
        self.structure_panel.set_project(self.project)

    def _structure_project_changed(self, project: object) -> None:
        assert isinstance(project, Project)
        self.project = project
        self._refresh_count_views()
        self._refresh_structure_mapping()

    def _anchor_structure_block(self, block_id: str) -> None:
        calibration = self.project.calibration
        if calibration is None:
            self.structure_panel.status.setText(
                "Set the grid Anchor on the waveform first."
            )
            return
        block = next(region for region in self.project.regions if region.id == block_id)
        anchor_seconds = calibration.anchor_seconds
        self.project = rebase_structure(self.project, block.start)
        assert self.project.calibration is not None
        assert self.project.calibration.anchor_seconds == anchor_seconds
        self.structure_panel.status.setText("Selected block starts at the grid Anchor.")
        self._refresh_count_views()
        self._refresh_structure_mapping()

    def _seek_to_structure_beat(self, beat: object) -> None:
        assert isinstance(beat, Fraction)
        calibration = self.project.calibration
        if calibration is None:
            self.structure_panel.status.setText(
                "Set the grid Anchor before seeking by structure."
            )
            return
        milliseconds = round(calibration.seconds_at(beat) * 1000)
        self.playback.seek(max(0, milliseconds))

    def _toggle_playback(self) -> None:
        if self.playback.is_playing:
            self.playback.pause()
        else:
            self.playback.play()

    def _position_changed(self, position_ms: int) -> None:
        if not self.seek_slider.isSliderDown():
            self.seek_slider.setValue(position_ms)
        self.waveform.set_position(position_ms)
        if self.project.calibration is None:
            self.structure_panel.set_playhead_beat(None)
        else:
            self.structure_panel.set_playhead_beat(
                self.project.calibration.beat_at(Fraction(position_ms, 1000))
            )
        self.time_label.setText(
            f"{_format_ms(position_ms)} / {_format_ms(self.playback.duration)}"
        )

    def _duration_changed(self, duration_ms: int) -> None:
        self.seek_slider.setMaximum(max(duration_ms, 0))
        self.waveform.set_duration(duration_ms)
        self._position_changed(self.playback.position)

    def _playback_state_changed(self, state: str) -> None:
        self.play_button.setText("Pause" if state == "playing" else "Play")

    def _playback_failed(self, message: str) -> None:
        self.song_label.setText(f"Playback error: {message}")

    def _waveform_ready(self, peaks: object) -> None:
        assert isinstance(peaks, tuple)
        self.waveform.set_peaks(peaks)
        self.processing_indicator.setVisible(False)
        if self.audio_source is not None:
            self.song_label.setText(
                f"{self.audio_source.display_name} — waveform ready"
            )

    def _waveform_failed(self, message: str) -> None:
        self.processing_indicator.setVisible(False)
        self.song_label.setText(message)

    def _set_anchor(self) -> None:
        anchor_ms = self.playback.position
        calibration = BeatCalibration(
            bpm=self.tempo_bpm,
            anchor_seconds=Fraction(anchor_ms, 1000),
        )
        self.project = replace(self.project, calibration=calibration)
        self.waveform.set_anchor(anchor_ms)
        self.anchor_label.setText(f"Grid anchor at {_format_ms(anchor_ms)}")
        self.refine_button.setEnabled(True)
        self._refresh_structure_mapping()

    def _set_calibration_point(self) -> None:
        if self.project.calibration is None:
            return
        try:
            beat = Fraction(self.refine_beat_edit.text().strip())
            calibration = self.project.calibration.with_calibration_point(
                beat, Fraction(self.playback.position, 1000)
            )
        except (ValueError, ZeroDivisionError, CalibrationError) as error:
            self.anchor_label.setText(f"Refinement rejected: {error}")
            return
        self.project = replace(self.project, calibration=calibration)
        self.tempo_bpm = calibration.bpm
        self.waveform.set_bpm(float(self.tempo_bpm))
        self.bpm_edit.setText(f"{float(self.tempo_bpm):.6f}".rstrip("0").rstrip("."))
        self.anchor_label.setText(
            f"Grid anchor at {_format_ms(int(calibration.anchor_seconds * 1000))}; "
            f"beat {beat} matched"
        )
        self._refresh_structure_mapping()

    def _update_calibration_bpm(self) -> None:
        if self.project.calibration is not None:
            self.project = replace(
                self.project,
                calibration=self.project.calibration.with_bpm(self.tempo_bpm),
            )
            self._refresh_structure_mapping()

    def _refresh_structure_mapping(self) -> None:
        calibration = self.project.calibration
        if calibration is None:
            self.waveform.set_structure_bands(())
            return
        bands = tuple(
            (
                round(calibration.seconds_at(region.start) * 1000),
                round(calibration.seconds_at(region.end) * 1000),
                region.color or "#bfdbfe",
            )
            for region in self.project.regions
            if region.parent_id is None
        )
        self.waveform.set_structure_bands(bands)


def _format_ms(milliseconds: int) -> str:
    minutes, remainder = divmod(max(milliseconds, 0), 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{minutes}:{seconds:02d}.{millis:03d}"
