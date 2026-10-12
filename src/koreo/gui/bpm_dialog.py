"""Small manual and tapped BPM dialog."""

from fractions import Fraction
from time import monotonic_ns
from typing import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from koreo.domain.calibration import CalibrationError, TapTempo, parse_bpm

# [GH-15] [S-M2-03] Focused manual/tap tempo UI per KOR-DEC-001.


class TapButton(QPushButton):
    """Report focused spacebar taps without accepting key auto-repeat."""

    tapped = Signal()

    def __init__(self) -> None:
        super().__init__("Tap here or press Space")
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


class BpmDialog(QDialog):
    """Edit one exact BPM manually or by tapping."""

    def __init__(
        self,
        initial_bpm: Fraction = Fraction(120),
        parent: QWidget | None = None,
        *,
        clock_ns: Callable[[], int] = monotonic_ns,
    ) -> None:
        super().__init__(parent)
        self.result_bpm: Fraction | None = None
        self._clock_ns = clock_ns
        self._tap_tempo = TapTempo()
        self.setWindowTitle("Tap BPM")
        self.setModal(True)
        self.setMinimumWidth(430)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("Enter a tempo, or focus the tap button and tap Space.")
        )

        bpm_row = QHBoxLayout()
        bpm_row.addWidget(QLabel("BPM:"))
        self.bpm_edit = QLineEdit(_format_fraction(initial_bpm, 6))
        self.bpm_edit.setAccessibleName("BPM")
        self.bpm_edit.textChanged.connect(self._validate)
        bpm_row.addWidget(self.bpm_edit, 1)
        layout.addLayout(bpm_row)

        tap_row = QHBoxLayout()
        self.tap_button = TapButton()
        self.tap_button.tapped.connect(self._record_tap)
        self.reset_button = QPushButton("Reset taps")
        self.reset_button.clicked.connect(self._reset_taps)
        tap_row.addWidget(self.tap_button, 1)
        tap_row.addWidget(self.reset_button)
        layout.addLayout(tap_row)

        self.status_label = QLabel("Two taps produce the first estimate.")
        layout.addWidget(self.status_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._accept_bpm)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self._validate()

    def _record_tap(self) -> None:
        estimate = self._tap_tempo.tap(Fraction(self._clock_ns(), 1_000_000_000))
        if estimate is None:
            self.status_label.setText("Tap once more to estimate BPM.")
            return
        self.bpm_edit.setText(_format_fraction(estimate, 3))
        self.status_label.setText(
            f"Estimate from {self._tap_tempo.tap_count} taps. Keep tapping to refine it."
        )

    def _reset_taps(self) -> None:
        self._tap_tempo.reset()
        self.status_label.setText("Tap session reset. Tap twice to estimate BPM.")

    def _validate(self) -> None:
        try:
            parse_bpm(self.bpm_edit.text())
            valid = True
        except CalibrationError:
            valid = False
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(valid)

    def _accept_bpm(self) -> None:
        try:
            self.result_bpm = parse_bpm(self.bpm_edit.text())
        except CalibrationError as error:
            self.status_label.setText(str(error))
            return
        self.accept()


def _format_fraction(value: Fraction, decimal_places: int) -> str:
    return f"{float(value):.{decimal_places}f}".rstrip("0").rstrip(".")
