"""Guided audio and beat-grid setup dialog."""

from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from time import monotonic_ns
from typing import Callable

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from koreo.audio import AudioProbe, AudioSource
from koreo.domain.calibration import (
    BeatCalibration,
    CalibrationError,
    TapTempo,
    parse_bpm,
)
from koreo.domain.models import Project

# [GH-13] [GH-15] [S-M2-01] [S-M2-03] Guided import and calibration.


class TapButton(QPushButton):
    """Button that reports focused spacebar taps without key auto-repeat."""

    tapped = Signal()

    def __init__(self) -> None:
        super().__init__("Tap BPM (focus, then press Space)")
        self.clicked.connect(self.tapped)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                self.tapped.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Space:
            event.accept()
            return
        super().keyReleaseEvent(event)


class SetupDialog(QDialog):
    """Collect a validated source and exact constant-tempo calibration."""

    def __init__(
        self,
        project: Project,
        parent: QWidget | None = None,
        *,
        clock_ns: Callable[[], int] = monotonic_ns,
    ) -> None:
        super().__init__(parent)
        self.project = project
        self.result_project: Project | None = None
        self.audio_source: AudioSource | None = None
        self._clock_ns = clock_ns
        self._tap_tempo = TapTempo()
        self._anchor_seconds: Fraction | None = None
        self._calibration: BeatCalibration | None = None
        self._probe = AudioProbe(self)
        self._probe.succeeded.connect(self._audio_ready)
        self._probe.failed.connect(self._audio_failed)
        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.durationChanged.connect(self._duration_changed)
        self.player.positionChanged.connect(self._position_changed)

        self.setWindowTitle("Set up audio and beat grid")
        self.resize(680, 390)
        self._build_ui()
        self._refresh_acceptance()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        heading = QLabel(
            "1. Choose audio  ·  2. Set BPM  ·  3. Play to a musical one  ·  4. Set anchor"
        )
        heading.setWordWrap(True)
        layout.addWidget(heading)

        file_row = QHBoxLayout()
        self.file_name = QLineEdit()
        self.file_name.setReadOnly(True)
        self.file_name.setPlaceholderText("No MP3 or WAV selected")
        self.browse_button = QPushButton("Choose audio…")
        self.browse_button.clicked.connect(self._choose_audio)
        file_row.addWidget(self.file_name, 1)
        file_row.addWidget(self.browse_button)
        layout.addLayout(file_row)
        self.status_label = QLabel("Choose a local MP3 or WAV file.")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        transport = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self._toggle_playback)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.player.stop)
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.player.setPosition)
        self.position_label = QLabel("0:00.000 / 0:00.000")
        transport.addWidget(self.play_button)
        transport.addWidget(self.stop_button)
        transport.addWidget(self.position_slider, 1)
        transport.addWidget(self.position_label)
        layout.addLayout(transport)

        form = QFormLayout()
        bpm_row = QHBoxLayout()
        self.bpm_edit = QLineEdit("120")
        self.bpm_edit.setAccessibleName("BPM")
        self.bpm_edit.textChanged.connect(self._bpm_changed)
        self.tap_button = TapButton()
        self.tap_button.tapped.connect(self._record_tap)
        self.reset_taps_button = QPushButton("Reset taps")
        self.reset_taps_button.clicked.connect(self._reset_taps)
        bpm_row.addWidget(self.bpm_edit)
        bpm_row.addWidget(self.tap_button)
        bpm_row.addWidget(self.reset_taps_button)
        form.addRow("Tempo:", bpm_row)

        anchor_row = QHBoxLayout()
        self.anchor_button = QPushButton("Set current position as beat 0")
        self.anchor_button.setEnabled(False)
        self.anchor_button.clicked.connect(self._set_anchor)
        self.anchor_label = QLabel("Not set")
        anchor_row.addWidget(self.anchor_button)
        anchor_row.addWidget(self.anchor_label, 1)
        form.addRow("Primary anchor:", anchor_row)

        calibration_row = QHBoxLayout()
        self.calibration_beat = QLineEdit()
        self.calibration_beat.setPlaceholderText("Optional beat, e.g. 128")
        self.calibration_button = QPushButton("Match to current position")
        self.calibration_button.setEnabled(False)
        self.calibration_button.clicked.connect(self._set_calibration_point)
        calibration_row.addWidget(self.calibration_beat)
        calibration_row.addWidget(self.calibration_button)
        form.addRow("Refine:", calibration_row)
        layout.addLayout(form)

        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Enter editor")
        self.buttons.accepted.connect(self._accept_setup)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _choose_audio(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "Choose audio", "", "Audio files (*.mp3 *.wav)"
        )
        if selected:
            self.load_audio(Path(selected))

    def load_audio(self, path: Path) -> None:
        """Start transactional validation of a selected source."""

        self.audio_source = None
        self.file_name.setText(str(path))
        self.status_label.setText("Checking that Qt can decode this file…")
        self.play_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.anchor_button.setEnabled(False)
        self._probe.probe(path)
        self._refresh_acceptance()

    def _audio_ready(self, source: object) -> None:
        assert isinstance(source, AudioSource)
        self.audio_source = source
        self.player.setSource(QUrl.fromLocalFile(str(source.path)))
        self.status_label.setText(
            f"Ready: {source.display_name} — {source.sample_rate} Hz, "
            f"{source.channel_count} channel(s), {source.sample_format}"
        )
        self.play_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.anchor_button.setEnabled(True)
        self._refresh_acceptance()

    def _audio_failed(self, message: str) -> None:
        self.audio_source = None
        self.player.stop()
        self.player.setSource(QUrl())
        self.status_label.setText(message)
        self._refresh_acceptance()

    def _duration_changed(self, duration_ms: int) -> None:
        self.position_slider.setMaximum(max(duration_ms, 0))
        if self.audio_source is not None and duration_ms > 0:
            self.audio_source = replace(
                self.audio_source, duration_seconds=Fraction(duration_ms, 1000)
            )
        self._position_changed(self.player.position())

    def _position_changed(self, position_ms: int) -> None:
        if not self.position_slider.isSliderDown():
            self.position_slider.setValue(position_ms)
        self.position_label.setText(
            f"{_format_ms(position_ms)} / {_format_ms(self.player.duration())}"
        )

    def _toggle_playback(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_button.setText("Play")
        else:
            self.player.play()
            self.play_button.setText("Pause")

    def _record_tap(self) -> None:
        estimate = self._tap_tempo.tap(Fraction(self._clock_ns(), 1_000_000_000))
        if estimate is not None:
            self.bpm_edit.setText(_format_fraction(estimate, 3))
        else:
            self.validation_label.setText("Tap once more to estimate BPM.")

    def _reset_taps(self) -> None:
        self._tap_tempo.reset()
        self.validation_label.setText("Tap session reset.")

    def _bpm_changed(self) -> None:
        if self._anchor_seconds is not None:
            self._rebuild_calibration()
        self._refresh_acceptance()

    def _set_anchor(self) -> None:
        self._anchor_seconds = Fraction(self.player.position(), 1000)
        self.anchor_label.setText(f"Beat 0 at {_format_ms(self.player.position())}")
        self._rebuild_calibration()
        self.calibration_button.setEnabled(self._calibration is not None)

    def _set_calibration_point(self) -> None:
        if self._calibration is None:
            return
        try:
            beat = Fraction(self.calibration_beat.text().strip())
            self._calibration = self._calibration.with_calibration_point(
                beat, Fraction(self.player.position(), 1000)
            )
        except (ValueError, ZeroDivisionError, CalibrationError) as error:
            self.validation_label.setText(f"Calibration point not accepted: {error}")
            return
        self.bpm_edit.setText(_format_fraction(self._calibration.bpm, 6))
        self.validation_label.setText(
            f"Calibration point accepted; refined BPM is {_format_fraction(self._calibration.bpm, 6)}."
        )
        self._refresh_acceptance()

    def _rebuild_calibration(self) -> None:
        assert self._anchor_seconds is not None
        try:
            self._calibration = BeatCalibration(
                bpm=parse_bpm(self.bpm_edit.text()),
                anchor_seconds=self._anchor_seconds,
            )
            self.validation_label.setText("BPM and anchor are valid.")
        except CalibrationError as error:
            self._calibration = None
            self.validation_label.setText(str(error))

    def _refresh_acceptance(self) -> None:
        try:
            parse_bpm(self.bpm_edit.text())
            bpm_valid = True
        except CalibrationError:
            bpm_valid = False
        ready = (
            self.audio_source is not None
            and self._anchor_seconds is not None
            and bpm_valid
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ready)

    def _accept_setup(self) -> None:
        if self.audio_source is None or self._calibration is None:
            return
        self.result_project = replace(self.project, calibration=self._calibration)
        self.player.stop()
        self.accept()


def _format_ms(milliseconds: int) -> str:
    minutes, remainder = divmod(max(milliseconds, 0), 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{minutes}:{seconds:02d}.{millis:03d}"


def _format_fraction(value: Fraction, decimal_places: int) -> str:
    return f"{float(value):.{decimal_places}f}".rstrip("0").rstrip(".")
