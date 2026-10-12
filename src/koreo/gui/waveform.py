"""Zoomable waveform with shared playhead and anchor marker."""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PySide6.QtWidgets import QWidget

_MAX_ZOOM = 64.0


class WaveformWidget(QWidget):
    """Render normalized peak buckets against media time."""

    def __init__(self) -> None:
        super().__init__()
        self.peaks: tuple[tuple[float, float], ...] = ()
        self.duration_ms = 0
        self.position_ms = 0
        self.anchor_ms: int | None = None
        self.zoom_factor = 1.0
        self.view_start_ms = 0.0
        self._pan_x: float | None = None
        self.setMinimumHeight(150)
        self.setAccessibleName("Song waveform and playhead")

    def set_peaks(self, peaks: tuple[tuple[float, float], ...]) -> None:
        self.peaks = peaks
        self.update()

    def set_duration(self, duration_ms: int) -> None:
        self.duration_ms = max(duration_ms, 0)
        self._clamp_view()
        self.update()

    def set_position(self, position_ms: int) -> None:
        self.position_ms = max(position_ms, 0)
        self.update()

    def set_anchor(self, anchor_ms: int | None) -> None:
        self.anchor_ms = anchor_ms
        self.update()

    @property
    def visible_duration_ms(self) -> float:
        """Return the media duration represented by the widget width."""

        if self.duration_ms <= 0:
            return 0.0
        return self.duration_ms / self.zoom_factor

    def zoom_in(self) -> None:
        """Zoom around the current playhead, or the view center if offscreen."""

        self._zoom_at_time(1.25, self._preferred_zoom_time())

    def zoom_out(self) -> None:
        """Zoom out around the current playhead or view center."""

        self._zoom_at_time(0.8, self._preferred_zoom_time())

    def zoom_to_fit(self) -> None:
        """Show the complete song."""

        self.zoom_factor = 1.0
        self.view_start_ms = 0.0
        self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        if self.duration_ms <= 0 or event.angleDelta().y() == 0:
            event.ignore()
            return
        focus_time = self._x_to_time(event.position().x())
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self._zoom_at_time(factor, focus_time, event.position().x())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_x = event.position().x()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._pan_x is not None and self.width() > 0:
            delta_x = event.position().x() - self._pan_x
            self.view_start_ms -= delta_x * self.visible_duration_ms / self.width()
            self._pan_x = event.position().x()
            self._clamp_view()
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_x is not None:
            self._pan_x = None
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        center = self.height() / 2
        painter.setPen(QPen(QColor("#94a3b8"), 1))
        painter.drawLine(0, int(center), self.width(), int(center))
        if self.peaks and self.duration_ms > 0:
            top: list[QPointF] = []
            bottom: list[QPointF] = []
            start_index = max(
                0, int(self.view_start_ms / self.duration_ms * len(self.peaks)) - 1
            )
            end_time = self.view_start_ms + self.visible_duration_ms
            end_index = min(
                len(self.peaks),
                int(end_time / self.duration_ms * len(self.peaks)) + 2,
            )
            for index in range(start_index, end_index):
                minimum, maximum = self.peaks[index]
                time_ms = index * self.duration_ms / max(len(self.peaks) - 1, 1)
                x = self._time_to_x(time_ms)
                top.append(QPointF(x, center - maximum * (center - 10)))
                bottom.append(QPointF(x, center - minimum * (center - 10)))
            polygon = QPolygonF(top + list(reversed(bottom)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#60a5fa"))
            painter.drawPolygon(polygon)
        if self.duration_ms > 0:
            if self.anchor_ms is not None and self._is_visible(self.anchor_ms):
                anchor_x = self._time_to_x(self.anchor_ms)
                painter.setPen(QPen(QColor("#16a34a"), 3))
                painter.drawLine(int(anchor_x), 0, int(anchor_x), self.height())
                painter.drawText(int(anchor_x) + 5, 16, "Beat 0")
            if self._is_visible(self.position_ms):
                playhead_x = self._time_to_x(self.position_ms)
                painter.setPen(QPen(QColor("#dc2626"), 2))
                painter.drawLine(int(playhead_x), 0, int(playhead_x), self.height())
        painter.end()

    def _preferred_zoom_time(self) -> float:
        if self._is_visible(self.position_ms):
            return float(self.position_ms)
        return self.view_start_ms + self.visible_duration_ms / 2

    def _zoom_at_time(
        self, factor: float, focus_time: float, focus_x: float | None = None
    ) -> None:
        if self.duration_ms <= 0 or self.width() <= 0:
            return
        old_visible = self.visible_duration_ms
        if focus_x is None:
            focus_x = (focus_time - self.view_start_ms) / old_visible * self.width()
        ratio = min(max(focus_x / self.width(), 0.0), 1.0)
        self.zoom_factor = min(_MAX_ZOOM, max(1.0, self.zoom_factor * factor))
        self.view_start_ms = focus_time - ratio * self.visible_duration_ms
        self._clamp_view()
        self.update()

    def _clamp_view(self) -> None:
        maximum_start = max(0.0, self.duration_ms - self.visible_duration_ms)
        self.view_start_ms = min(max(self.view_start_ms, 0.0), maximum_start)

    def _x_to_time(self, x: float) -> float:
        if self.width() <= 0:
            return self.view_start_ms
        return self.view_start_ms + x / self.width() * self.visible_duration_ms

    def _time_to_x(self, milliseconds: float) -> float:
        if self.visible_duration_ms <= 0:
            return 0.0
        return (
            (milliseconds - self.view_start_ms)
            / self.visible_duration_ms
            * self.width()
        )

    def _is_visible(self, milliseconds: float) -> bool:
        return (
            self.view_start_ms
            <= milliseconds
            <= self.view_start_ms + self.visible_duration_ms
        )
