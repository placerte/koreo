"""Continuous read-only Timeline widget."""

from fractions import Fraction

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPaintEvent, QPainter, QPen
from PySide6.QtWidgets import QScrollArea, QWidget

from koreo.gui.colors import text_color, translucent
from koreo.presentation.models import TimelineModel

_HEADER_WIDTH = 120
_BEAT_WIDTH = 34
_RULER_HEIGHT = 42
_REGION_HEIGHT = 28
_TRACK_HEIGHT = 58


class TimelineCanvas(QWidget):
    """Paint a continuous beat axis without editing affordances."""

    # [GH-7] [S-M1-04] Continuous read-only view over mapped beat intervals.

    def __init__(self, model: TimelineModel) -> None:
        super().__init__()
        self.model = model
        region_rows = 1 + max((region.depth for region in model.regions), default=0)
        width = _HEADER_WIDTH + int(float(model.end - model.start) * _BEAT_WIDTH) + 30
        height = (
            _RULER_HEIGHT
            + region_rows * _REGION_HEIGHT
            + len(model.tracks) * _TRACK_HEIGHT
            + 30
        )
        self.setMinimumSize(width, height)
        self.setAccessibleName("Continuous choreography timeline")

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render the mapped timeline model."""

        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        self._paint_ruler(painter)
        self._paint_regions(painter)
        self._paint_tracks(painter)
        painter.end()

    def x_for_beat(self, beat: Fraction) -> float:
        """Map an exact beat to a pixel coordinate."""

        return _HEADER_WIDTH + float(beat - self.model.start) * _BEAT_WIDTH

    def _paint_ruler(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor("#64748b")))
        painter.drawText(12, 25, "Beat")
        for beat in range(int(self.model.start), int(self.model.end) + 1):
            x = self.x_for_beat(Fraction(beat))
            major = (beat - int(self.model.count_origin)) % self.model.count_group == 0
            painter.setPen(QPen(QColor("#94a3b8"), 2 if major else 1))
            painter.drawLine(int(x), 18 if major else 27, int(x), self.height() - 12)
            count = ((beat - int(self.model.count_origin)) % self.model.count_group) + 1
            painter.setPen(QPen(QColor("#334155")))
            painter.drawText(
                QRectF(x - 14, 2, 28, 18), Qt.AlignmentFlag.AlignCenter, str(count)
            )

    def _paint_regions(self, painter: QPainter) -> None:
        for gap in self.model.gaps:
            rect = QRectF(
                self.x_for_beat(gap.start),
                _RULER_HEIGHT,
                self.x_for_beat(gap.end) - self.x_for_beat(gap.start),
                _REGION_HEIGHT,
            )
            painter.fillRect(rect, QColor("#e2e8f0"))
            painter.setPen(QPen(QColor("#64748b"), 1, Qt.PenStyle.DashLine))
            painter.drawRect(rect)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "Unassigned")

        palette = ("#dbeafe", "#dcfce7", "#fef3c7")
        for region in self.model.regions:
            y = _RULER_HEIGHT + region.depth * _REGION_HEIGHT
            rect = QRectF(
                self.x_for_beat(region.start),
                y,
                self.x_for_beat(region.end) - self.x_for_beat(region.start),
                _REGION_HEIGHT - 2,
            )
            painter.fillRect(rect, QColor(palette[region.depth % len(palette)]))
            painter.setPen(QPen(QColor("#475569")))
            painter.drawRect(rect)
            painter.drawText(
                rect.adjusted(6, 0, -4, 0), Qt.AlignmentFlag.AlignVCenter, region.label
            )

    def _paint_tracks(self, painter: QPainter) -> None:
        region_rows = 1 + max(
            (region.depth for region in self.model.regions), default=0
        )
        top = _RULER_HEIGHT + region_rows * _REGION_HEIGHT
        painter.setFont(QFont(painter.font().family(), 9))
        for row_index, track in enumerate(self.model.tracks):
            y = top + row_index * _TRACK_HEIGHT
            painter.fillRect(
                QRectF(0, y, self.width(), _TRACK_HEIGHT),
                QColor("#ffffff" if row_index % 2 == 0 else "#f1f5f9"),
            )
            painter.setPen(QPen(QColor(track.color), 3))
            painter.drawLine(8, y + 8, 8, y + _TRACK_HEIGHT - 8)
            painter.setPen(QPen(QColor("#0f172a")))
            painter.drawText(
                QRectF(16, y, _HEADER_WIDTH - 20, _TRACK_HEIGHT),
                Qt.AlignmentFlag.AlignVCenter,
                track.name,
            )
            for move in track.moves:
                rect = QRectF(
                    self.x_for_beat(move.start) + 1,
                    y + 9,
                    self.x_for_beat(move.end) - self.x_for_beat(move.start) - 2,
                    _TRACK_HEIGHT - 18,
                )
                background = translucent(move.color)
                painter.fillRect(rect, background)
                painter.setPen(QPen(QColor(move.color).darker(125)))
                painter.drawRoundedRect(rect, 4, 4)
                painter.setPen(QPen(text_color(background)))
                painter.drawText(
                    rect.adjusted(5, 2, -5, -2),
                    Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                    move.label,
                )


class TimelineView(QScrollArea):
    """Scrollable host for a :class:`TimelineCanvas`."""

    def __init__(self, model: TimelineModel) -> None:
        super().__init__()
        self.model = model
        self.canvas = TimelineCanvas(model)
        self.setWidget(self.canvas)
        self.setWidgetResizable(False)
        self.setAccessibleName("Timeline view")
