"""Application shell sharing one project and session between two views."""

from fractions import Fraction
from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from koreo.audio import AudioProbe, AudioSource
from koreo.domain.calibration import CalibrationError, parse_bpm
from koreo.domain.models import Project
from koreo.gui.bpm_dialog import BpmDialog
from koreo.gui.sheet import SheetView
from koreo.gui.timeline import TimelineView
from koreo.presentation.mapping import build_sheet, build_timeline


class MainWindow(QMainWindow):
    """Host Timeline and Sheet tabs for one immutable project instance."""

    # [GH-9] [S-M1-06] Both tabs derive from the same Project object.

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.audio_source: AudioSource | None = None
        self.tempo_bpm = Fraction(120)
        self._probe = AudioProbe(self)
        self._probe.succeeded.connect(self._audio_ready)
        self._probe.failed.connect(self._audio_failed)
        self.timeline_view = TimelineView(build_timeline(project))
        self.sheet_view = SheetView(build_sheet(project))
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

        song_bar = QHBoxLayout()
        song_bar.addWidget(self.choose_song_button)
        song_bar.addWidget(self.song_label, 1)
        song_bar.addWidget(QLabel("BPM:"))
        song_bar.addWidget(self.bpm_edit)
        song_bar.addWidget(self.tap_bpm_button)

        self.tabs = QTabWidget()
        self.tabs.setAccessibleName("Project view selector")
        self.tabs.addTab(self.timeline_view, "Timeline")
        self.tabs.addTab(self.sheet_view, "Sheet")
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(song_bar)
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

    def load_song(self, path: Path) -> None:
        """Validate a selected song without replacing the last valid source."""

        self.choose_song_button.setEnabled(False)
        self.song_label.setText(f"Checking {path.name}…")
        self._probe.probe(path)

    def _audio_ready(self, source: object) -> None:
        assert isinstance(source, AudioSource)
        self.audio_source = source
        self.song_label.setText(
            f"{source.display_name} — {source.sample_rate} Hz, "
            f"{source.channel_count} channel(s)"
        )
        self.choose_song_button.setEnabled(True)
        self.tap_bpm_button.setEnabled(True)

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

    def _manual_bpm_changed(self) -> None:
        try:
            self.tempo_bpm = parse_bpm(self.bpm_edit.text())
        except CalibrationError:
            self.bpm_edit.setText(
                f"{float(self.tempo_bpm):.3f}".rstrip("0").rstrip(".")
            )
