"""Wrapped read-only choreography Sheet widget."""

from fractions import Fraction

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPaintEvent, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QScrollArea, QWidget

from koreo.gui.colors import text_color, translucent
from koreo.presentation.models import MoveSegment, SheetLine, SheetModel

_HEADER_WIDTH = 120
_CELL_WIDTH = 45
_COUNT_HEIGHT = 48
_TRACK_HEIGHT = 54
_LINE_GAP = 24
_MARGIN = 18


class SheetCanvas(QWidget):
    """Paint deterministic wrapped count lines and move segments."""

    # [GH-8] [S-M1-05] Wrapped read-only view with continuation cues.

    def __init__(self, model: SheetModel) -> None:
        super().__init__()
        self.model = model
        track_count = len(model.lines[0].tracks) if model.lines else 0
        line_height = _COUNT_HEIGHT + track_count * _TRACK_HEIGHT + _LINE_GAP
        width = _MARGIN * 2 + _HEADER_WIDTH + model.beats_per_line * _CELL_WIDTH
        height = _MARGIN * 2 + len(model.lines) * line_height
        self.setMinimumSize(width, height)
        self.setAccessibleName("Wrapped choreography sheet")

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render the mapped sheet model."""

        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        y = _MARGIN
        for line in self.model.lines:
            self._paint_line(painter, line, y)
            y += _COUNT_HEIGHT + len(line.tracks) * _TRACK_HEIGHT + _LINE_GAP
        painter.end()

    def _paint_line(self, painter: QPainter, line: SheetLine, y: int) -> None:
        painter.setPen(QPen(QColor("#334155")))
        painter.setFont(QFont(painter.font().family(), 9, QFont.Weight.Bold))
        painter.drawText(
            QRectF(_MARGIN, y, _HEADER_WIDTH - 8, _COUNT_HEIGHT),
            Qt.AlignmentFlag.AlignVCenter,
            f"Beats {line.start}–{line.end}",
        )
        painter.setFont(QFont(painter.font().family(), 8))
        for index, cell in enumerate(line.counts):
            x = _MARGIN + _HEADER_WIDTH + index * _CELL_WIDTH
            rect = QRectF(x, y, _CELL_WIDTH, _COUNT_HEIGHT)
            if cell.region_id is None:
                painter.fillRect(rect, QColor("#e2e8f0"))
                label = "Gap"
            else:
                painter.fillRect(rect, QColor("#e0f2fe"))
                label = cell.region_label or ""
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor("#94a3b8")))
            painter.drawRect(rect)
            painter.setPen(QPen(QColor("#0f172a")))
            painter.drawText(
                rect.adjusted(0, 3, 0, -18), Qt.AlignmentFlag.AlignCenter, label
            )
            painter.drawText(
                rect.adjusted(0, 20, 0, -2), Qt.AlignmentFlag.AlignCenter, cell.label
            )

        for row_index, row in enumerate(line.tracks):
            row_y = y + _COUNT_HEIGHT + row_index * _TRACK_HEIGHT
            painter.fillRect(
                QRectF(
                    _MARGIN,
                    row_y,
                    _HEADER_WIDTH + len(line.counts) * _CELL_WIDTH,
                    _TRACK_HEIGHT,
                ),
                QColor("#ffffff" if row_index % 2 == 0 else "#f1f5f9"),
            )
            painter.setPen(QPen(QColor(row.color), 3))
            painter.drawLine(
                _MARGIN + 2, row_y + 8, _MARGIN + 2, row_y + _TRACK_HEIGHT - 8
            )
            painter.setPen(QPen(QColor("#0f172a")))
            painter.drawText(
                QRectF(_MARGIN + 10, row_y, _HEADER_WIDTH - 14, _TRACK_HEIGHT),
                Qt.AlignmentFlag.AlignVCenter,
                row.track_name,
            )
            for segment in row.segments:
                self._paint_segment(painter, line, segment, row_y)

    def _paint_segment(
        self, painter: QPainter, line: SheetLine, segment: MoveSegment, row_y: int
    ) -> None:
        x = _MARGIN + _HEADER_WIDTH + float(segment.start - line.start) * _CELL_WIDTH
        width = float(segment.end - segment.start) * _CELL_WIDTH
        rect = QRectF(x + 2, row_y + 8, width - 4, _TRACK_HEIGHT - 16)
        background = translucent(segment.color)
        painter.setBrush(background)
        painter.setPen(QPen(QColor(segment.color).darker(125)))
        painter.drawRoundedRect(rect, 4, 4)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(text_color(background)))
        prefix = "◀ " if segment.continues_before else ""
        suffix = " ▶" if segment.continues_after else ""
        painter.drawText(
            rect.adjusted(6, 1, -6, -1),
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            f"{prefix}{segment.label}{suffix}",
        )
        self._paint_continuation_cues(
            painter, rect, segment.continues_before, segment.continues_after
        )

    @staticmethod
    def _paint_continuation_cues(
        painter: QPainter, rect: QRectF, before: bool, after: bool
    ) -> None:
        if not before and not after:
            return
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(Qt.PenStyle.NoPen)
        middle = rect.center().y()
        if before:
            painter.drawPolygon(
                QPolygonF(
                    [
                        QPointF(rect.left(), middle),
                        QPointF(rect.left() + 7, middle - 6),
                        QPointF(rect.left() + 7, middle + 6),
                    ]
                )
            )
        if after:
            painter.drawPolygon(
                QPolygonF(
                    [
                        QPointF(rect.right(), middle),
                        QPointF(rect.right() - 7, middle - 6),
                        QPointF(rect.right() - 7, middle + 6),
                    ]
                )
            )
        painter.setBrush(Qt.BrushStyle.NoBrush)


class SheetView(QScrollArea):
    """Scrollable host for a :class:`SheetCanvas`."""

    def __init__(self, model: SheetModel) -> None:
        super().__init__()
        self.model = model
        self.canvas = SheetCanvas(model)
        self.setWidget(self.canvas)
        self.setWidgetResizable(False)
        self.setAccessibleName("Sheet view")
