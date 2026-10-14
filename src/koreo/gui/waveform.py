"""Zoomable waveform with beat grid, following playhead, and anchor marker."""

import math

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import (
    QColor,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPen,
    QPolygonF,
    QWheelEvent,
)
from PySide6.QtWidgets import QApplication, QWidget

from koreo.settings import APPEARANCE

_MAX_ZOOM = 64.0


class WaveformWidget(QWidget):
    """Render normalized peak buckets against media time."""

    follow_changed = Signal(bool)
    seek_requested = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.peaks: tuple[tuple[float, float], ...] = ()
        self.duration_ms = 0
        self.position_ms = 0
        self.anchor_ms: int | None = None
        self.bpm = 120.0
        self.count_group = 8
        self.zoom_factor = 1.0
        self.view_start_ms = 0.0
        self.follow_playhead = True
        self.show_structure_labels = APPEARANCE.show_waveform_section_labels
        self.simplified = False
        self.structure_bands: tuple[tuple[int, int, str, str], ...] = ()
        self._press_x: float | None = None
        self._pan_x: float | None = None
        self._dragging = False
        self._dragging_playhead = False
        self.setMouseTracking(True)
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
        if not self.simplified and self.follow_playhead and self.zoom_factor > 1.0:
            self.view_start_ms = self.position_ms - self.visible_duration_ms * 0.35
            self._clamp_view()
        self.update()

    def set_anchor(self, anchor_ms: int | None) -> None:
        self.anchor_ms = anchor_ms
        self.update()

    def set_bpm(self, bpm: float) -> None:
        """Set the constant-tempo grid spacing."""

        if bpm > 0:
            self.bpm = bpm
            self.update()

    def set_count_group(self, count_group: int) -> None:
        """Set the project count grouping used by the simplified overview."""

        if count_group > 0:
            self.count_group = count_group
            self.update()

    def set_structure_bands(self, bands: tuple[tuple[int, int, str, str], ...]) -> None:
        """Set calibrated top-level section backgrounds in media time."""

        self.structure_bands = bands
        self.update()

    def set_show_structure_labels(self, enabled: bool) -> None:
        """Show or hide section names without changing structure bands."""

        self.show_structure_labels = enabled
        self.update()

    def set_simplified(self, enabled: bool) -> None:
        """Show only Structure bands, labels, and the playhead when enabled."""

        self.simplified = enabled
        self.update()

    def set_follow_playhead(self, enabled: bool) -> None:
        """Enable or suspend automatic waveform scrolling."""

        changed = self.follow_playhead != enabled
        self.follow_playhead = enabled
        if enabled:
            self.set_position(self.position_ms)
        if changed:
            self.follow_changed.emit(enabled)

    @property
    def visible_duration_ms(self) -> float:
        """Return the media duration represented by the widget width."""

        if self.duration_ms <= 0:
            return 0.0
        if self.simplified:
            return float(self.duration_ms)
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
        if self.simplified or self.duration_ms <= 0 or event.angleDelta().y() == 0:
            event.ignore()
            return
        focus_time = self._x_to_time(event.position().x())
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.set_follow_playhead(False)
        self._zoom_at_time(factor, focus_time, event.position().x())
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            playhead_x = self._time_to_x(self.position_ms)
            if self.simplified or abs(event.position().x() - playhead_x) <= 7:
                self._dragging_playhead = True
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                requested = round(self._x_to_time(event.position().x()))
                self.seek_requested.emit(max(0, min(requested, self.duration_ms)))
                event.accept()
                return
            self._press_x = event.position().x()
            self._pan_x = event.position().x()
            self._dragging = False
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._dragging_playhead and event.buttons() & Qt.MouseButton.LeftButton:
            requested = round(self._x_to_time(event.position().x()))
            self.seek_requested.emit(max(0, min(requested, self.duration_ms)))
            event.accept()
            return
        if (
            self._pan_x is not None
            and self._press_x is not None
            and event.buttons() & Qt.MouseButton.LeftButton
            and self.width() > 0
        ):
            if (
                not self._dragging
                and abs(event.position().x() - self._press_x)
                >= QApplication.startDragDistance()
            ):
                self._dragging = True
                self.set_follow_playhead(False)
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            if not self._dragging:
                event.accept()
                return
            delta_x = event.position().x() - self._pan_x
            self.view_start_ms -= delta_x * self.visible_duration_ms / self.width()
            self._pan_x = event.position().x()
            self._clamp_view()
            self.update()
            event.accept()
            return
        if (
            self.duration_ms > 0
            and abs(event.position().x() - self._time_to_x(self.position_ms)) <= 7
        ):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.unsetCursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._dragging_playhead:
            self._dragging_playhead = False
            requested = round(self._x_to_time(event.position().x()))
            self.seek_requested.emit(max(0, min(requested, self.duration_ms)))
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self._pan_x is not None:
            was_dragging = self._dragging
            self._pan_x = None
            self._press_x = None
            self._dragging = False
            self.unsetCursor()
            if not was_dragging:
                requested = round(self._x_to_time(event.position().x()))
                self.seek_requested.emit(max(0, min(requested, self.duration_ms)))
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        if not self._dragging_playhead:
            self.unsetCursor()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        center = self.height() / 2
        self._paint_structure_bands(painter)
        if self.simplified:
            self._paint_simplified_beat_grid(painter)
        else:
            self._paint_beat_grid(painter)
            painter.setPen(QPen(QColor("#94a3b8"), 1))
            painter.drawLine(0, int(center), self.width(), int(center))
        if not self.simplified and self.peaks and self.duration_ms > 0:
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
            step = max(1, (end_index - start_index) // max(self.width(), 1))
            for index in range(start_index, end_index, step):
                group = self.peaks[index : min(index + step, end_index)]
                minimum = min(item[0] for item in group)
                maximum = max(item[1] for item in group)
                time_ms = index * self.duration_ms / max(len(self.peaks) - 1, 1)
                x = self._time_to_x(time_ms)
                top.append(QPointF(x, center - maximum * (center - 10)))
                bottom.append(QPointF(x, center - minimum * (center - 10)))
            polygon = QPolygonF(top + list(reversed(bottom)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#60a5fa"))
            painter.drawPolygon(polygon)
        anchor_x: float | None = None
        if self.duration_ms > 0:
            if (
                not self.simplified
                and self.anchor_ms is not None
                and self._is_visible(self.anchor_ms)
            ):
                anchor_x = self._time_to_x(self.anchor_ms)
                painter.setPen(QPen(QColor("#16a34a"), 3))
                painter.drawLine(int(anchor_x), 0, int(anchor_x), self.height())
            if self._is_visible(self.position_ms):
                playhead_x = self._time_to_x(self.position_ms)
                painter.setPen(QPen(QColor("#dc2626"), 2))
                painter.drawLine(int(playhead_x), 0, int(playhead_x), self.height())
        if not self.simplified:
            self._paint_rulers(painter)
        if self.show_structure_labels or self.simplified:
            self._paint_structure_labels(painter)
        if anchor_x is not None:
            painter.setPen(QPen(QColor("#16a34a"), 2))
            painter.drawText(int(anchor_x) + 5, self.height() - 25, "⚓")
        painter.end()

    def _paint_structure_bands(self, painter: QPainter) -> None:
        for start_ms, end_ms, color, _label in self.structure_bands:
            if (
                end_ms < self._display_start_ms
                or start_ms > self._display_start_ms + self.visible_duration_ms
            ):
                continue
            left = self._time_to_x(start_ms)
            right = self._time_to_x(end_ms)
            shade = QColor(color)
            shade.setAlphaF(1.0 - APPEARANCE.waveform_region_transparency)
            painter.fillRect(QRectF(left, 0, right - left, self.height()), shade)
            if self.simplified:
                painter.setPen(QPen(QColor(shade).darker(135), 1))
                painter.drawRect(QRectF(left, 0, right - left, self.height() - 1))

    def _paint_structure_labels(self, painter: QPainter) -> None:
        """Draw section names above the waveform so they remain legible."""

        for start_ms, end_ms, _color, label in self.structure_bands:
            if (
                end_ms < self._display_start_ms
                or start_ms > self._display_start_ms + self.visible_duration_ms
            ):
                continue
            if self._is_visible(start_ms):
                left = self._time_to_x(start_ms)
                painter.setPen(QPen(QColor("#475569"), 1))
                if self.simplified:
                    width = max(0, round(self._time_to_x(end_ms) - left) - 8)
                    elided = painter.fontMetrics().elidedText(
                        label, Qt.TextElideMode.ElideRight, width
                    )
                    painter.drawText(
                        QRectF(left + 4, 0, width, self.height()),
                        Qt.AlignmentFlag.AlignVCenter,
                        elided,
                    )
                else:
                    painter.drawText(round(left) + 4, 36, label)

    def _paint_simplified_beat_grid(self, painter: QPainter) -> None:
        if self.duration_ms <= 0 or self.bpm <= 0:
            return
        beat_ms = 60_000 / self.bpm
        origin_ms = float(self.anchor_ms or 0)
        first_beat = math.ceil(-origin_ms / beat_ms)
        last_beat = math.floor((self.duration_ms - origin_ms) / beat_ms)
        for beat in range(first_beat, last_beat + 1):
            if beat % self.count_group != 0:
                continue
            x = round(self._time_to_x(origin_ms + beat * beat_ms))
            painter.setPen(QPen(QColor(71, 85, 105, 70), 1))
            painter.drawLine(x, 0, x, self.height())

    def _paint_beat_grid(self, painter: QPainter) -> None:
        if self.duration_ms <= 0 or self.bpm <= 0:
            return
        beat_ms = 60_000 / self.bpm
        origin_ms = float(self.anchor_ms or 0)
        first_beat = math.ceil((self.view_start_ms - origin_ms) / beat_ms)
        last_time = self.view_start_ms + self.visible_duration_ms
        beat = first_beat
        while origin_ms + beat * beat_ms <= last_time:
            time_ms = origin_ms + beat * beat_ms
            x = self._time_to_x(time_ms)
            major = beat % 4 == 0
            painter.setPen(QPen(QColor(99, 102, 241, 70 if major else 35), 1))
            painter.drawLine(int(x), 0, int(x), self.height())
            beat += 1

    def _paint_rulers(self, painter: QPainter) -> None:
        if self.duration_ms <= 0 or self.width() <= 0:
            return
        painter.fillRect(QRectF(0, 0, self.width(), 20), QColor(248, 250, 252, 215))
        painter.fillRect(
            QRectF(0, self.height() - 20, self.width(), 20),
            QColor(248, 250, 252, 215),
        )
        painter.setPen(QPen(QColor("#64748b"), 1))
        painter.drawLine(0, 19, self.width(), 19)
        painter.drawLine(0, self.height() - 20, self.width(), self.height() - 20)

        minimum_time_step = self.visible_duration_ms * 80 / max(self.width(), 1)
        time_step = next(
            (
                step
                for step in (
                    1_000,
                    2_000,
                    5_000,
                    10_000,
                    15_000,
                    30_000,
                    60_000,
                    120_000,
                    300_000,
                    600_000,
                )
                if step >= minimum_time_step
            ),
            600_000,
        )
        time_ms = math.ceil(self.view_start_ms / time_step) * time_step
        view_end = self.view_start_ms + self.visible_duration_ms
        while time_ms <= view_end:
            x = round(self._time_to_x(time_ms))
            painter.drawLine(x, 13, x, 19)
            painter.drawText(x + 3, 12, _format_ruler_time(time_ms))
            time_ms += time_step

        beat_ms = 60_000 / self.bpm
        origin_ms = float(self.anchor_ms or 0)
        first_beat = math.ceil((self.view_start_ms - origin_ms) / beat_ms)
        last_beat = math.floor((view_end - origin_ms) / beat_ms)
        label_every = max(
            1, math.ceil(70 / max(beat_ms / self.visible_duration_ms * self.width(), 1))
        )
        for beat in range(first_beat, last_beat + 1):
            x = round(self._time_to_x(origin_ms + beat * beat_ms))
            major = beat % 8 == 0
            painter.drawLine(
                x,
                self.height() - 20,
                x,
                self.height() - (8 if major else 14),
            )
            if major or beat % label_every == 0:
                painter.drawText(x + 3, self.height() - 3, str(beat + 1))

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
            return self._display_start_ms
        return self._display_start_ms + x / self.width() * self.visible_duration_ms

    def _time_to_x(self, milliseconds: float) -> float:
        if self.visible_duration_ms <= 0:
            return 0.0
        return (
            (milliseconds - self._display_start_ms)
            / self.visible_duration_ms
            * self.width()
        )

    def _is_visible(self, milliseconds: float) -> bool:
        return (
            self._display_start_ms
            <= milliseconds
            <= self._display_start_ms + self.visible_duration_ms
        )

    @property
    def _display_start_ms(self) -> float:
        return 0.0 if self.simplified else self.view_start_ms


def _format_ruler_time(milliseconds: float) -> str:
    seconds = max(0, round(milliseconds / 1000))
    return f"{seconds // 60}:{seconds % 60:02d}"
