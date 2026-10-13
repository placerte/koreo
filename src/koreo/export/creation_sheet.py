"""Printable, handwriting-friendly Structure creation-sheet PDF export."""

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from PySide6.QtCore import QLineF, QMarginsF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QPageLayout,
    QPageSize,
    QPainter,
    QPdfWriter,
    QPen,
)

from koreo.domain.models import MusicalRegion, Project
from koreo.settings import CREATION_SHEET, CreationSheetSettings

# GitHub issue #45: export a writable Structure creation sheet.
_MARGIN_MM = 12.0
_HEADER_HEIGHT = 72.0
_RULER_HEIGHT = 28.0
_ROW_HEIGHT = 58.0
_LABEL_WIDTH = 132.0


class CreationSheetExportError(RuntimeError):
    """Raised when a creation-sheet PDF cannot be produced."""


@dataclass(frozen=True, slots=True)
class CreationSheetPlan:
    """Deterministic page geometry independent of painter state."""

    page_count: int
    rows_per_page: int
    maximum_beats: int


def plan_creation_sheet(
    project: Project, *, printable_height: float
) -> CreationSheetPlan:
    """Calculate row pagination for a given printable page height."""

    rows = _sections(project)
    available = max(0.0, printable_height - _HEADER_HEIGHT - _RULER_HEIGHT)
    rows_per_page = max(1, int(available // _ROW_HEIGHT))
    page_count = max(1, (len(rows) + rows_per_page - 1) // rows_per_page)
    maximum_beats = max((int(row.duration) for row in rows), default=1)
    return CreationSheetPlan(page_count, rows_per_page, maximum_beats)


def export_creation_sheet_pdf(
    project: Project,
    path: Path,
    *,
    project_filename: str,
    settings: CreationSheetSettings = CREATION_SHEET,
) -> CreationSheetPlan:
    """Render a Structure creation sheet and return its page plan."""

    writer = QPdfWriter(str(path))
    writer.setResolution(144)
    page_id = (
        QPageSize.PageSizeId.Letter
        if settings.page_size == "Letter"
        else QPageSize.PageSizeId.A4
    )
    layout = QPageLayout(
        QPageSize(page_id),
        QPageLayout.Orientation.Landscape,
        QMarginsF(_MARGIN_MM, _MARGIN_MM, _MARGIN_MM, _MARGIN_MM),
        QPageLayout.Unit.Millimeter,
    )
    if not writer.setPageLayout(layout):
        raise CreationSheetExportError("The requested PDF page layout is unsupported.")
    writer.setTitle(f"{project.name} — Creation sheet")
    painter = QPainter()
    if not painter.begin(writer):
        raise CreationSheetExportError(f"Could not create PDF: {path}")
    try:
        width = float(writer.width())
        height = float(writer.height())
        plan = plan_creation_sheet(project, printable_height=height)
        rows = _sections(project)
        for page_index in range(plan.page_count):
            if page_index and not writer.newPage():
                raise CreationSheetExportError("Could not add a PDF page.")
            start = page_index * plan.rows_per_page
            page_rows = rows[start : start + plan.rows_per_page]
            _paint_page(
                painter,
                project,
                page_rows,
                width,
                height,
                project_filename,
                page_index + 1,
                plan,
                settings,
            )
    finally:
        painter.end()
    if not path.exists() or path.stat().st_size == 0:
        raise CreationSheetExportError(f"PDF was not written: {path}")
    return plan


def _paint_page(
    painter: QPainter,
    project: Project,
    rows: tuple[MusicalRegion, ...],
    width: float,
    height: float,
    project_filename: str,
    page_number: int,
    plan: CreationSheetPlan,
    settings: CreationSheetSettings,
) -> None:
    painter.fillRect(QRectF(0, 0, width, height), Qt.GlobalColor.white)
    title_font = QFont(painter.font())
    title_font.setPointSize(16)
    title_font.setBold(True)
    painter.setFont(title_font)
    painter.setPen(QColor("#111827"))
    painter.drawText(QRectF(0, 0, width, 30), project.name)
    meta_font = QFont(painter.font())
    meta_font.setPointSize(9)
    meta_font.setBold(False)
    painter.setFont(meta_font)
    painter.setPen(QColor("#475569"))
    painter.drawText(QRectF(0, 34, width, 20), f"Project file: {project_filename}")
    painter.drawText(
        QRectF(0, 34, width, 20),
        Qt.AlignmentFlag.AlignRight,
        f"Page {page_number} / {plan.page_count}",
    )
    beat_width = max(1.0, (width - _LABEL_WIDTH) / plan.maximum_beats)
    _paint_ruler(painter, beat_width, plan.maximum_beats)
    y = _HEADER_HEIGHT + _RULER_HEIGHT
    for row in rows:
        _paint_row(painter, project, row, y, beat_width, settings.playground_opacity)
        y += _ROW_HEIGHT


def _paint_ruler(painter: QPainter, beat_width: float, maximum_beats: int) -> None:
    group = 8
    y = _HEADER_HEIGHT
    painter.setPen(QPen(QColor("#64748b"), 1))
    painter.drawLine(
        QLineF(
            _LABEL_WIDTH,
            y + _RULER_HEIGHT - 1,
            _LABEL_WIDTH + maximum_beats * beat_width,
            y + _RULER_HEIGHT - 1,
        )
    )
    for beat in range(maximum_beats + 1):
        x = _LABEL_WIDTH + beat * beat_width
        major = beat % group == 0
        painter.setPen(QPen(QColor("#64748b"), 2 if major else 1))
        painter.drawLine(
            QLineF(
                x,
                y + _RULER_HEIGHT - (9 if major else 6),
                x,
                y + _RULER_HEIGHT,
            )
        )
        if beat < maximum_beats:
            painter.drawText(
                QRectF(x - beat_width / 2, y + 1, beat_width, 18),
                Qt.AlignmentFlag.AlignHCenter,
                str(beat % group + 1),
            )


def _paint_row(
    painter: QPainter,
    project: Project,
    row: MusicalRegion,
    y: float,
    beat_width: float,
    opacity: float,
) -> None:
    base = QColor(row.color or "#bfdbfe")
    painter.fillRect(
        QRectF(0, y + 4, _LABEL_WIDTH - 6, _ROW_HEIGHT - 8), base.lighter(112)
    )
    painter.setPen(QColor("#334155"))
    painter.drawText(QRectF(6, y + 7, _LABEL_WIDTH - 12, 20), row.label)
    timestamp = _timestamp(project, row)
    if timestamp:
        painter.setPen(QColor("#64748b"))
        painter.drawText(QRectF(6, y + 29, _LABEL_WIDTH - 12, 18), timestamp)
    blocks = tuple(
        sorted(
            (region for region in project.regions if region.parent_id == row.id),
            key=lambda region: (region.start, region.id),
        )
    )
    offset = Fraction(0)
    for index, block in enumerate(blocks):
        rect = QRectF(
            _LABEL_WIDTH + float(offset) * beat_width,
            y + 4,
            float(block.duration) * beat_width,
            _ROW_HEIGHT - 8,
        )
        color = base if index % 2 == 0 else base.lighter(112)
        color.setAlphaF(opacity)
        painter.fillRect(rect, color)
        ink = QColor("#475569")
        ink.setAlphaF(opacity)
        painter.setPen(QPen(ink, 1))
        painter.drawRect(rect)
        painter.drawText(
            QRectF(rect.left(), rect.top() + 2, rect.width(), 16),
            Qt.AlignmentFlag.AlignHCenter,
            str(block.duration),
        )
        leader, note = _parse_note(block.label)
        note_rect = QRectF(rect.left() + 4, rect.top() + 17, rect.width() - 8, 22)
        for beat in range(1, int(block.duration)):
            x = rect.left() + beat * beat_width
            painter.drawLine(QLineF(x, rect.bottom() - 6, x, rect.bottom()))
        if leader is not None and 1 <= leader <= block.duration:
            x = rect.left() + (leader - 1) * beat_width
            painter.setPen(QPen(ink, 2))
            if note:
                points = _leader_points(
                    note_rect,
                    painter.fontMetrics().horizontalAdvance(note),
                    painter.fontMetrics().boundingRect(note).height(),
                    x,
                    rect.bottom(),
                )
                for start, end in zip(points, points[1:]):
                    painter.drawLine(QLineF(start[0], start[1], end[0], end[1]))
            else:
                painter.drawLine(QLineF(x, rect.bottom() - 12, x, rect.bottom()))
        if note:
            painter.setPen(QPen(ink, 1))
            painter.drawText(note_rect, Qt.AlignmentFlag.AlignCenter, note)
        offset += block.duration


def _sections(project: Project) -> tuple[MusicalRegion, ...]:
    return tuple(
        sorted(
            (region for region in project.regions if region.parent_id is None),
            key=lambda region: (region.start, region.id),
        )
    )


def _parse_note(label: str) -> tuple[int | None, str]:
    if label == "8 count":
        return None, ""
    prefix, separator, note = label.partition(":")
    if separator and prefix.strip().isdigit():
        return int(prefix.strip()), note.strip()
    return None, label


def _leader_points(
    note_rect: QRectF,
    note_width: float,
    note_height: float,
    tick_x: float,
    tick_bottom: float,
) -> tuple[tuple[float, float], ...]:
    center_x = note_rect.center().x()
    center_y = note_rect.center().y()
    left = center_x - note_width / 2
    right = center_x + note_width / 2
    if tick_x < left:
        return ((left, center_y), (tick_x, center_y), (tick_x, tick_bottom))
    if tick_x > right:
        return ((right, center_y), (tick_x, center_y), (tick_x, tick_bottom))
    bottom = center_y + note_height / 2
    elbow_y = max(bottom + 3, tick_bottom - 7)
    return (
        (center_x, bottom),
        (center_x, elbow_y),
        (tick_x, elbow_y),
        (tick_x, tick_bottom),
    )


def _timestamp(project: Project, row: MusicalRegion) -> str:
    if project.calibration is None:
        return ""
    start = max(0, int(project.calibration.seconds_at(row.start)))
    end = max(0, int(project.calibration.seconds_at(row.end)))
    return f"{start // 60}:{start % 60:02d}–{end // 60}:{end % 60:02d}"
