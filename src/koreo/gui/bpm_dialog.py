"""Tap-tempo playback dialog."""

from fractions import Fraction
from time import monotonic_ns
from typing import Callable

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QKeyEvent, QShowEvent
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from koreo.audio import AudioSource
from koreo.domain.calibration import TapTempo

# [GH-15] [S-M2-03] Focused playback/tap session per KOR-DEC-001.


class BpmDialog(QDialog):
    """Play the selected song and collect a BPM estimate from taps."""

    def __init__(
        self,
        source: AudioSource,
        parent: QWidget | None = None,
        *,
        clock_ns: Callable[[], int] = monotonic_ns,
    ) -> None:
        super().__init__(parent)
        self.result_bpm: Fraction | None = None
        self._clock_ns = clock_ns
        self._tap_tempo = TapTempo()
        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(str(source.path)))
        self.player.durationChanged.connect(self._duration_changed)
        self.player.positionChanged.connect(self._position_changed)
        self.player.errorOccurred.connect(self._playback_error)

        self.setWindowTitle("Tap BPM")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Now playing: {source.display_name}"))
        playhead_row = QHBoxLayout()
        self.playhead = QSlider(Qt.Orientation.Horizontal)
        self.playhead.setRange(0, 0)
        self.playhead.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.playhead.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.time_label = QLabel("0:00.000 / 0:00.000")
        self.time_label.setFixedWidth(
            self.time_label.fontMetrics().horizontalAdvance("99:59.999 / 99:59.999")
        )
        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        playhead_row.addWidget(self.playhead, 1)
        playhead_row.addWidget(self.time_label)
        layout.addLayout(playhead_row)

        self.tap_button = QPushButton("Tap here or press Space")
        self.tap_button.clicked.connect(self._record_tap)
        self.tap_button.setDefault(True)
        layout.addWidget(self.tap_button)
        action_row = QHBoxLayout()
        self.estimate_label = QLabel("Tap twice to estimate BPM")
        self.reset_button = QPushButton("Reset taps")
        self.reset_button.clicked.connect(self._reset_taps)
        action_row.addWidget(self.estimate_label, 1)
        action_row.addWidget(self.reset_button)
        layout.addLayout(action_row)

        self.status_label = QLabel(
            "Playback starts automatically. Space records a tap."
        )
        layout.addWidget(self.status_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Use tapped BPM"
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        self.buttons.accepted.connect(self._accept_bpm)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        super().showEvent(event)
        self.tap_button.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self.player.play()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                self._record_tap()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() == Qt.Key.Key_Space:
            event.accept()
            return
        super().keyReleaseEvent(event)

    def done(self, result: int) -> None:
        """Stop playback whenever the tap session closes."""

        self.player.stop()
        super().done(result)

    def _record_tap(self) -> None:
        estimate = self._tap_tempo.tap(Fraction(self._clock_ns(), 1_000_000_000))
        if estimate is None:
            self.estimate_label.setText("Tap once more…")
            return
        self.result_bpm = estimate
        self.estimate_label.setText(
            f"{_format_fraction(estimate, 3)} BPM · {self._tap_tempo.tap_count} taps"
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)

    def _reset_taps(self) -> None:
        self._tap_tempo.reset()
        self.result_bpm = None
        self.estimate_label.setText("Tap twice to estimate BPM")
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

    def _accept_bpm(self) -> None:
        if self.result_bpm is not None:
            self.accept()

    def _duration_changed(self, duration_ms: int) -> None:
        self.playhead.setMaximum(max(duration_ms, 0))
        self._position_changed(self.player.position())

    def _position_changed(self, position_ms: int) -> None:
        self.playhead.setValue(position_ms)
        self.time_label.setText(
            f"{_format_ms(position_ms)} / {_format_ms(self.player.duration())}"
        )

    def _playback_error(self) -> None:
        detail = self.player.errorString().strip() or "unknown playback error"
        self.status_label.setText(f"Playback failed: {detail}")


def _format_ms(milliseconds: int) -> str:
    minutes, remainder = divmod(max(milliseconds, 0), 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{minutes}:{seconds:02d}.{millis:03d}"


def _format_fraction(value: Fraction, decimal_places: int) -> str:
    return f"{float(value):.{decimal_places}f}".rstrip("0").rstrip(".")
