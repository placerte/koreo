"""Non-editable waveform with shared playhead and anchor marker."""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPaintEvent, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """Render normalized peak buckets against media time."""

    def __init__(self) -> None:
        super().__init__()
        self.peaks: tuple[tuple[float, float], ...] = ()
        self.duration_ms = 0
        self.position_ms = 0
        self.anchor_ms: int | None = None
        self.setMinimumHeight(150)
        self.setAccessibleName("Song waveform and playhead")

    def set_peaks(self, peaks: tuple[tuple[float, float], ...]) -> None:
        self.peaks = peaks
        self.update()

    def set_duration(self, duration_ms: int) -> None:
        self.duration_ms = max(duration_ms, 0)
        self.update()

    def set_position(self, position_ms: int) -> None:
        self.position_ms = max(position_ms, 0)
        self.update()

    def set_anchor(self, anchor_ms: int | None) -> None:
        self.anchor_ms = anchor_ms
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        center = self.height() / 2
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.drawLine(0, int(center), self.width(), int(center))
        if self.peaks:
            top: list[QPointF] = []
            bottom: list[QPointF] = []
            for index, (minimum, maximum) in enumerate(self.peaks):
                x = index * self.width() / max(len(self.peaks) - 1, 1)
                top.append(QPointF(x, center - maximum * (center - 10)))
                bottom.append(QPointF(x, center - minimum * (center - 10)))
            polygon = QPolygonF(top + list(reversed(bottom)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#60a5fa"))
            painter.drawPolygon(polygon)
        if self.duration_ms > 0:
            if self.anchor_ms is not None:
                anchor_x = self.anchor_ms * self.width() / self.duration_ms
                painter.setPen(QPen(QColor("#16a34a"), 3))
                painter.drawLine(int(anchor_x), 0, int(anchor_x), self.height())
                painter.drawText(int(anchor_x) + 5, 16, "Beat 0")
            playhead_x = self.position_ms * self.width() / self.duration_ms
            painter.setPen(QPen(QColor("#dc2626"), 2))
            painter.drawLine(int(playhead_x), 0, int(playhead_x), self.height())
        painter.end()
