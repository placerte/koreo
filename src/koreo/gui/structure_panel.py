"""Editable vertical song-structure rows."""

from collections.abc import Callable
from fractions import Fraction
import re

from PySide6.QtCore import QEvent, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QContextMenuEvent,
    QFocusEvent,
    QIcon,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPen,
    QPixmap,
    QShortcut,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QScrollArea,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from koreo.domain.models import MusicalRegion, Project
from koreo.domain.structure import (
    SECTION_PALETTE,
    DEFAULT_STRUCTURE_TEMPLATE,
    STRUCTURE_TEMPLATES,
    SectionPattern,
    StructureTemplate,
    StructureEditError,
    add_block,
    append_section,
    delete_block,
    delete_section,
    delete_sections,
    generate_structure_template,
    insert_section_after,
    insert_block_after,
    paste_sections,
    resize_block,
    section_patterns,
    update_block_label,
    update_section,
)
from koreo.settings import APPEARANCE
from koreo.gui.icons import IconRole, semantic_icon

_ROW_HEIGHT = 54
_LABEL_WIDTH = 140
_BEAT_WIDTH = 14
_MIN_BEAT_WIDTH = 6
_MAX_BEAT_WIDTH = 40
_RULER_HEIGHT = 28


class _InlineEdit(QLineEdit):
    """Single-line editor with explicit accept and cancel semantics."""

    accepted = Signal(str)
    cancelled = Signal()

    def __init__(self, value: str, parent: QWidget) -> None:
        super().__init__(value, parent)
        self._resolved = False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._accept()
            event.accept()
            return
        if event.key() == Qt.Key.Key_Escape:
            self._cancel()
            event.accept()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        self._accept()
        super().focusOutEvent(event)

    def _accept(self) -> None:
        if not self._resolved:
            self._resolved = True
            self.accepted.emit(self.text())

    def _cancel(self) -> None:
        if not self._resolved:
            self._resolved = True
            self.cancelled.emit()


class StructureCanvas(QWidget):
    selected = Signal(str)
    append_requested = Signal(int)
    rename_requested = Signal(str, str)
    color_requested = Signal(str, str)
    delete_requested = Signal(str)
    insert_requested = Signal(str)
    add_block_requested = Signal(str)
    resize_block_requested = Signal(str, int)
    delete_block_requested = Signal(str)
    anchor_block_requested = Signal(str)
    position_requested = Signal(object)
    block_label_requested = Signal(str, str)

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.selected_id: str | None = None
        self.selected_ids: set[str] = set()
        self.selected_block_id: str | None = None
        self.selection_anchor_id: str | None = None
        self._press: tuple[int, float, str | None] | None = None
        self._label_editor: _InlineEdit | None = None
        self._resize_preview: tuple[str, int] | None = None
        self.playhead_beat: Fraction | None = None
        self.selection_positions_playhead = APPEARANCE.selection_moves_playhead
        self.continuous_ruler_numbers = False
        self.beat_width = float(_BEAT_WIDTH)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(300)

    def set_project(self, project: Project) -> None:
        self.project = project
        maximum_beats = max((int(row.duration) for row in self._rows()), default=32)
        self.setMinimumWidth(round(_LABEL_WIDTH + maximum_beats * self.beat_width + 20))
        self.setMinimumHeight(
            _RULER_HEIGHT + (len(self._rows()) + 1) * _ROW_HEIGHT + 10
        )
        self.update()

    def set_horizontal_zoom(self, beat_width: float) -> None:
        """Change horizontal beat scale without affecting vertical scrolling."""

        self.beat_width = min(_MAX_BEAT_WIDTH, max(_MIN_BEAT_WIDTH, beat_width))
        self.set_project(self.project)

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.set_horizontal_zoom(self.beat_width * factor)
            event.accept()
            return
        super().wheelEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        self._paint_grid_and_ruler(painter)
        for row, region in enumerate(self._rows()):
            y = _RULER_HEIGHT + row * _ROW_HEIGHT
            base = QColor(region.color or "#bfdbfe")
            painter.fillRect(
                QRectF(2, y + 5, _LABEL_WIDTH - 8, _ROW_HEIGHT - 10),
                base.lighter(112),
            )
            painter.setPen(QPen(QColor("#334155")))
            painter.drawText(QRectF(6, y + 5, _LABEL_WIDTH - 10, 22), region.label)
            timestamp = _region_timestamp(self.project, region)
            if timestamp:
                painter.save()
                font = painter.font()
                font.setPointSizeF(max(7.0, font.pointSizeF() - 2.0))
                painter.setFont(font)
                painter.setPen(QPen(QColor("#64748b")))
                painter.drawText(QRectF(6, y + 27, _LABEL_WIDTH - 10, 18), timestamp)
                painter.restore()
            blocks = self._blocks(region.id)
            block_offset = Fraction(0)
            for block_index, block in enumerate(blocks):
                beats = (
                    Fraction(self._resize_preview[1])
                    if self._resize_preview is not None
                    and self._resize_preview[0] == block.id
                    else block.duration
                )
                rect = QRectF(
                    _LABEL_WIDTH + float(block_offset) * self.beat_width,
                    y + 5,
                    float(beats) * self.beat_width,
                    _ROW_HEIGHT - 10,
                )
                shade = base if block_index % 2 == 0 else _alternate_shade(base)
                painter.fillRect(rect, shade)
                painter.setPen(QPen(QColor("#64748b")))
                painter.drawRect(rect)
                leader, note = _parse_block_note(block.label)
                painter.drawText(
                    QRectF(rect.left(), rect.top() + 2, rect.width(), 15),
                    Qt.AlignmentFlag.AlignHCenter,
                    str(beats),
                )
                note_rect = QRectF(
                    rect.left() + 4,
                    rect.top() + 15,
                    rect.width() - 8,
                    rect.height() - 17,
                )
                tick = 1
                painter.setPen(QPen(QColor(71, 85, 105, 100), 1))
                while Fraction(tick) < beats:
                    tick_x = rect.left() + tick * self.beat_width
                    painter.drawLine(
                        round(tick_x),
                        round(rect.bottom()) - 6,
                        round(tick_x),
                        round(rect.bottom()),
                    )
                    tick += 1
                if leader is not None and 1 <= leader <= beats:
                    leader_x = rect.left() + (leader - 1) * self.beat_width
                    if note:
                        note_width = painter.fontMetrics().horizontalAdvance(note)
                        note_height = painter.fontMetrics().boundingRect(note).height()
                        points = _leader_points(
                            note_rect,
                            note_width,
                            note_height,
                            leader_x,
                            rect.bottom(),
                        )
                        painter.setPen(QPen(QColor("#334155"), 2))
                        for start, end in zip(points, points[1:]):
                            painter.drawLine(
                                round(start[0]),
                                round(start[1]),
                                round(end[0]),
                                round(end[1]),
                            )
                    else:
                        painter.setPen(QPen(QColor("#334155"), 3))
                        painter.drawLine(
                            round(leader_x),
                            round(rect.bottom()) - 11,
                            round(leader_x),
                            round(rect.bottom()),
                        )
                if note:
                    painter.setPen(QPen(QColor("#64748b")))
                    painter.drawText(
                        note_rect,
                        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                        note,
                    )
                if block.id == self.selected_block_id:
                    painter.setPen(QPen(QColor("#2563eb"), 3))
                    painter.drawRect(rect.adjusted(2, 2, -2, -2))
                if (
                    self.project.calibration is not None
                    and block.start == self.project.calibration.anchor_beat
                ):
                    painter.setPen(QPen(QColor("#15803d"), 5))
                    painter.drawLine(
                        round(rect.left()),
                        round(rect.top()),
                        round(rect.left()),
                        round(rect.bottom()),
                    )
                    painter.drawText(
                        round(rect.left()) + 5,
                        round(rect.top()) + 15,
                        "⚓",
                    )
                block_offset += beats
            if region.id in self.selected_ids:
                painter.setPen(QPen(QColor("#2563eb"), 3))
                selected_width = _LABEL_WIDTH + float(region.duration) * self.beat_width
                painter.drawRect(QRectF(1, y + 1, selected_width, _ROW_HEIGHT - 2))
            if (
                self.playhead_beat is not None
                and region.start <= self.playhead_beat < region.end
            ):
                playhead_x = (
                    _LABEL_WIDTH
                    + float(self.playhead_beat - region.start) * self.beat_width
                )
                painter.setPen(QPen(QColor("#dc2626"), 2))
                painter.drawLine(
                    int(playhead_x), y + 3, int(playhead_x), y + _ROW_HEIGHT - 3
                )
        blank_y = _RULER_HEIGHT + len(self._rows()) * _ROW_HEIGHT
        painter.setPen(QPen(QColor("#94a3b8"), 1, Qt.PenStyle.DashLine))
        painter.drawRect(
            QRectF(
                _LABEL_WIDTH,
                blank_y + 5,
                self.width() - _LABEL_WIDTH - 4,
                _ROW_HEIGHT - 10,
            )
        )
        painter.drawText(
            QRectF(6, blank_y, _LABEL_WIDTH - 10, _ROW_HEIGHT),
            Qt.AlignmentFlag.AlignVCenter,
            "New section",
        )
        painter.end()

    def _paint_grid_and_ruler(self, painter: QPainter) -> None:
        maximum_beats = max((int(row.duration) for row in self._rows()), default=32)
        maximum_x = _LABEL_WIDTH + maximum_beats * self.beat_width
        group = max(1, self.project.default_count_group)
        for beat in range(maximum_beats + 1):
            x = _LABEL_WIDTH + beat * self.beat_width
            primary = beat % group == 0
            alpha = (
                APPEARANCE.structure_primary_grid_alpha
                if primary
                else APPEARANCE.structure_grid_alpha
            )
            painter.setPen(
                QPen(
                    QColor.fromRgbF(0.28, 0.33, 0.41, alpha),
                    2 if primary else 1,
                )
            )
            painter.drawLine(round(x), _RULER_HEIGHT, round(x), self.height())
            label_alpha = (
                APPEARANCE.structure_primary_grid_label_alpha
                if primary
                else APPEARANCE.structure_grid_label_alpha
            )
            ruler_color = QColor("#475569")
            ruler_color.setAlphaF(label_alpha)
            painter.setPen(QPen(ruler_color, 2 if primary else 1))
            painter.drawText(
                QRectF(x - self.beat_width / 2, 1, self.beat_width, 18),
                Qt.AlignmentFlag.AlignHCenter,
                str(beat + 1 if self.continuous_ruler_numbers else beat % group + 1),
            )
            painter.drawLine(
                round(x),
                _RULER_HEIGHT - (8 if primary else 5),
                round(x),
                _RULER_HEIGHT,
            )
        painter.setPen(QPen(QColor("#64748b"), 1))
        painter.drawLine(
            _LABEL_WIDTH, _RULER_HEIGHT - 1, round(maximum_x), _RULER_HEIGHT - 1
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            if event.position().y() < _RULER_HEIGHT:
                event.accept()
                return
            row = int((event.position().y() - _RULER_HEIGHT) // _ROW_HEIGHT)
            rows = self._rows()
            boundary_block: str | None = None
            if row < len(rows):
                for block in self._blocks(rows[row].id):
                    endpoint = (
                        _LABEL_WIDTH
                        + float(block.end - rows[row].start) * self.beat_width
                    )
                    if abs(event.position().x() - endpoint) <= 6:
                        boundary_block = block.id
                        break
            self._press = (
                row,
                event.position().x(),
                boundary_block,
            )
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._press is None:
            return
        row, start_x, block_id = self._press
        self._press = None
        self._resize_preview = None
        rows = self._rows()
        if row >= len(rows):
            duration = max(
                1, round((event.position().x() - _LABEL_WIDTH) / self.beat_width)
            )
            self.append_requested.emit(duration)
            return
        region = rows[row]
        self.selected_id = region.id
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            anchor_id = self.selection_anchor_id or region.id
            row_ids = [item.id for item in rows]
            anchor_index = row_ids.index(anchor_id) if anchor_id in row_ids else row
            start, end = sorted((anchor_index, row))
            ranged = set(row_ids[start : end + 1])
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.selected_ids.update(ranged)
            else:
                self.selected_ids = ranged
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            if region.id in self.selected_ids:
                self.selected_ids.remove(region.id)
            else:
                self.selected_ids.add(region.id)
            self.selection_anchor_id = region.id
        else:
            self.selected_ids = {region.id}
            self.selection_anchor_id = region.id
        clicked_block = self._block_at(region, round(event.position().x()))
        self.selected_block_id = clicked_block.id if clicked_block is not None else None
        self.selected.emit(region.id)
        if (
            self.selection_positions_playhead
            and block_id is None
            and abs(event.position().x() - start_x) < 2
        ):
            target = clicked_block.start if clicked_block is not None else region.start
            self.position_requested.emit(target)
        if block_id is not None and abs(event.position().x() - start_x) >= 2:
            block = next(item for item in self.project.regions if item.id == block_id)
            block_x = _LABEL_WIDTH + float(block.start - region.start) * self.beat_width
            duration = max(1, round((event.position().x() - block_x) / self.beat_width))
            self.resize_block_requested.emit(block.id, duration)
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        row = int((event.position().y() - _RULER_HEIGHT) // _ROW_HEIGHT)
        rows = self._rows()
        if 0 <= row < len(rows) and event.position().x() >= _LABEL_WIDTH:
            block = self._block_at(rows[row], round(event.position().x()))
            if block is not None:
                self._begin_block_label_edit(rows[row], block, row)
                event.accept()
                return
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.position().x() < _LABEL_WIDTH
            and 0 <= row < len(rows)
        ):
            self._begin_label_edit(rows[row], row)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _begin_block_label_edit(
        self, section: MusicalRegion, block: MusicalRegion, row: int
    ) -> None:
        if self._label_editor is not None:
            self._label_editor.deleteLater()
        x = _LABEL_WIDTH + round(float(block.start - section.start) * self.beat_width)
        width = max(40, round(float(block.duration) * self.beat_width))
        value = "" if block.label == "8 count" else block.label
        editor = _InlineEdit(value, self)
        editor.setGeometry(x + 2, _RULER_HEIGHT + row * _ROW_HEIGHT + 17, width - 4, 28)
        editor.setPlaceholderText("note or 4: note")
        editor.selectAll()
        editor.show()
        editor.setFocus()
        self._label_editor = editor

        def finish(value: str) -> None:
            if self._label_editor is not editor:
                return
            editor.hide()
            editor.deleteLater()
            self._label_editor = None
            self.setFocus()
            self.block_label_requested.emit(block.id, value.strip())

        editor.accepted.connect(finish)
        editor.cancelled.connect(lambda: self._close_editor(editor))

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if (
            self._press is not None
            and self._press[2] is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            pressed_row, _, block_id = self._press
            rows = self._rows()
            if pressed_row < len(rows) and block_id is not None:
                block = next(
                    item for item in self.project.regions if item.id == block_id
                )
                block_x = (
                    _LABEL_WIDTH
                    + float(block.start - rows[pressed_row].start) * self.beat_width
                )
                duration = max(
                    1, round((event.position().x() - block_x) / self.beat_width)
                )
                self._resize_preview = (block_id, duration)
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                self.update()
                event.accept()
                return
        row = int((event.position().y() - _RULER_HEIGHT) // _ROW_HEIGHT)
        rows = self._rows()
        if 0 <= row < len(rows):
            endpoints = (
                _LABEL_WIDTH + float(block.end - rows[row].start) * self.beat_width
                for block in self._blocks(rows[row].id)
            )
            if any(abs(event.position().x() - endpoint) <= 6 for endpoint in endpoints):
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.unsetCursor()
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self.unsetCursor()
        super().leaveEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        if event.pos().y() < _RULER_HEIGHT:
            return
        row = int((event.pos().y() - _RULER_HEIGHT) // _ROW_HEIGHT)
        rows = self._rows()
        if row >= len(rows):
            return
        region = rows[row]
        self.selected_id = region.id
        if region.id not in self.selected_ids:
            self.selected_ids = {region.id}
        self.selected.emit(region.id)
        menu = QMenu(self)
        insert_action = menu.addAction("Insert section below")
        add_block_action = menu.addAction("Add 8-count block")
        block = self._block_at(region, event.pos().x())
        anchor_action = None
        delete_block_action = None
        if block is not None:
            self.selected_block_id = block.id
            anchor_action = menu.addAction("Align this block start to grid Anchor")
            delete_block_action = menu.addAction("Delete this count block")
        menu.addSeparator()
        color_menu = menu.addMenu("Section color")
        assert color_menu is not None
        for color in SECTION_PALETTE:
            action = color_menu.addAction(color)
            action.setData(color)
            swatch = QPixmap(14, 14)
            swatch.fill(QColor(color))
            action.setIcon(QIcon(swatch))
        color_menu.triggered.connect(
            lambda action: self.color_requested.emit(region.id, str(action.data()))
        )
        menu.addSeparator()
        delete_action = menu.addAction("Delete section")
        chosen = menu.exec(event.globalPos())
        if chosen is insert_action:
            self.insert_requested.emit(region.id)
        elif chosen is add_block_action:
            self.add_block_requested.emit(region.id)
        elif anchor_action is not None and chosen is anchor_action:
            assert block is not None
            self.anchor_block_requested.emit(block.id)
        elif delete_block_action is not None and chosen is delete_block_action:
            assert block is not None
            self.delete_block_requested.emit(block.id)
        elif chosen is delete_action:
            self.delete_requested.emit(region.id)
        event.accept()

    def _begin_label_edit(self, region: MusicalRegion, row: int) -> None:
        if self._label_editor is not None:
            self._label_editor.deleteLater()
        editor = _InlineEdit(region.label, self)
        editor.setGeometry(
            2,
            _RULER_HEIGHT + row * _ROW_HEIGHT + 5,
            _LABEL_WIDTH - 8,
            _ROW_HEIGHT - 10,
        )
        editor.selectAll()
        editor.show()
        editor.setFocus()
        self._label_editor = editor

        def finish(value: str) -> None:
            if self._label_editor is not editor:
                return
            editor.hide()
            editor.deleteLater()
            self._label_editor = None
            self.setFocus()
            value = value.strip()
            if value and value != region.label:
                self.rename_requested.emit(region.id, value)

        editor.accepted.connect(finish)
        editor.cancelled.connect(lambda: self._close_editor(editor))

    def _close_editor(self, editor: _InlineEdit) -> None:
        if self._label_editor is editor:
            self._label_editor = None
            editor.hide()
            editor.deleteLater()
            self.setFocus()

    def _rows(self) -> tuple[MusicalRegion, ...]:
        return tuple(
            sorted(
                (region for region in self.project.regions if region.parent_id is None),
                key=lambda region: (region.start, region.id),
            )
        )

    def _blocks(self, section_id: str) -> tuple[MusicalRegion, ...]:
        return tuple(
            sorted(
                (r for r in self.project.regions if r.parent_id == section_id),
                key=lambda r: (r.start, r.id),
            )
        )

    def _block_at(self, section: MusicalRegion, x: int) -> MusicalRegion | None:
        local_beat = Fraction(
            max(0.0, x - _LABEL_WIDTH) / self.beat_width
        ).limit_denominator(1000)
        beat = section.start + local_beat
        return next(
            (
                block
                for block in self._blocks(section.id)
                if block.start <= beat < block.end
            ),
            None,
        )


def _alternate_shade(base: QColor) -> QColor:
    factor = APPEARANCE.block_alternate_shade_factor
    return QColor(
        round(base.red() * factor + 255 * (1 - factor)),
        round(base.green() * factor + 255 * (1 - factor)),
        round(base.blue() * factor + 255 * (1 - factor)),
    )


def _parse_block_note(label: str) -> tuple[int | None, str]:
    if label == "8 count":
        return None, ""
    match = re.fullmatch(r"\s*(\d+)\s*:\s*(.*)", label)
    if match is None:
        return None, label
    return int(match.group(1)), match.group(2).strip()


def _leader_points(
    note_rect: QRectF,
    note_width: float,
    note_height: float,
    tick_x: float,
    tick_bottom: float,
) -> tuple[tuple[float, float], ...]:
    """Route a leader from one of the label's permitted anchors to a tick."""

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


def _region_timestamp(project: Project, region: MusicalRegion) -> str:
    if project.calibration is None:
        return ""
    start = max(0, int(project.calibration.seconds_at(region.start)))
    end = max(0, int(project.calibration.seconds_at(region.end)))
    return f"{start // 60}:{start % 60:02d}–{end // 60}:{end % 60:02d}"


class StructurePanel(QWidget):
    project_changed = Signal(object)
    anchor_block_requested = Signal(str)
    position_requested = Signal(object)

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self._clipboard: tuple[SectionPattern, ...] = ()
        self._history: list[Project] = []
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        content = QWidget()
        layout = QVBoxLayout(content)
        generator = QHBoxLayout()
        self._selected_template = DEFAULT_STRUCTURE_TEMPLATE
        self.generate_button = QToolButton()
        self.generate_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.MenuButtonPopup
        )
        self.generate_button.setIcon(
            semantic_icon(self.generate_button, IconRole.STRUCTURE_TEMPLATE)
        )
        self.generate_button.setIconSize(QSize(20, 20))
        self.generate_button.setAccessibleName("Generate structure from template")
        self.generate_button.clicked.connect(self._generate)
        template_menu = QMenu(self.generate_button)
        template_menu.addSection("Full-song arrangements")
        self._add_template_action(template_menu, DEFAULT_STRUCTURE_TEMPLATE)
        template_menu.addSection("Phrase and form templates")
        for template in STRUCTURE_TEMPLATES[1:]:
            self._add_template_action(template_menu, template)
        template_menu.addSeparator()
        custom_action = template_menu.addAction(
            "Custom · draw or add sections manually"
        )
        custom_action.setEnabled(False)
        self.generate_button.setMenu(template_menu)
        self._update_template_button()
        self.anchor_button = QToolButton()
        self.anchor_button.setIcon(
            semantic_icon(self.anchor_button, IconRole.ALIGN_TO_ANCHOR)
        )
        self.anchor_button.setIconSize(QSize(20, 20))
        self.anchor_button.setAccessibleName("Align selected block to grid Anchor")
        self.anchor_button.setToolTip("Align selected block to grid Anchor")
        self.anchor_button.clicked.connect(self._anchor_selected)
        self.position_toggle = QToolButton()
        self.position_toggle.setIcon(
            semantic_icon(self.position_toggle, IconRole.SELECTION_SEEKS)
        )
        self.position_toggle.setIconSize(QSize(20, 20))
        self.position_toggle.setAccessibleName("Selection moves playhead")
        self.position_toggle.setToolTip("Selection moves playhead")
        self.position_toggle.setCheckable(True)
        self.position_toggle.setChecked(APPEARANCE.selection_moves_playhead)
        self.position_toggle.toggled.connect(self._position_toggle_changed)
        self.ruler_numbers_toggle = QToolButton()
        self.ruler_numbers_toggle.setIcon(
            semantic_icon(self.ruler_numbers_toggle, IconRole.CONTINUOUS_COUNTS)
        )
        self.ruler_numbers_toggle.setIconSize(QSize(20, 20))
        self.ruler_numbers_toggle.setAccessibleName("Continuous ruler numbers")
        self.ruler_numbers_toggle.setToolTip("Continuous ruler numbers")
        self.ruler_numbers_toggle.setCheckable(True)
        self.ruler_numbers_toggle.toggled.connect(self._ruler_numbers_toggle_changed)
        self.zoom_out_button = self._toolbar_button(
            IconRole.ZOOM_OUT,
            "Zoom Structure board out (Ctrl+Mouse Wheel Down)",
            self._zoom_out,
        )
        self.zoom_in_button = self._toolbar_button(
            IconRole.ZOOM_IN,
            "Zoom Structure board in (Ctrl+Mouse Wheel Up)",
            self._zoom_in,
        )
        self.zoom_fit_button = self._toolbar_button(
            IconRole.ZOOM_FIT, "Fit Structure board width", self._zoom_fit
        )
        self.add_section_button = self._toolbar_button(
            IconRole.ADD_SECTION,
            "Add section after selection (Enter)",
            self._add_section,
        )
        self.add_block_button = self._toolbar_button(
            IconRole.ADD_BLOCK,
            "Add 8-count block (Ctrl+Enter)",
            self._add_count_at_selection,
        )
        self.undo_button = self._toolbar_button(
            IconRole.UNDO, "Undo (Ctrl+Z)", self._undo
        )
        self.copy_button = self._toolbar_button(
            IconRole.COPY, "Copy selected sections (Ctrl+C)", self._copy_selected
        )
        self.paste_button = self._toolbar_button(
            IconRole.PASTE,
            "Paste sections after selection (Ctrl+V)",
            self._paste_after_selected,
        )
        self.delete_button = self._toolbar_button(
            IconRole.DELETE, "Delete selection (Delete)", self._delete_selection
        )
        generator.addWidget(QLabel("View:"))
        generator.addWidget(self.zoom_out_button)
        generator.addWidget(self.zoom_in_button)
        generator.addWidget(self.zoom_fit_button)
        generator.addWidget(self.position_toggle)
        generator.addWidget(self.ruler_numbers_toggle)
        generator.addWidget(self._toolbar_separator())
        generator.addWidget(QLabel("Edit:"))
        generator.addWidget(self.generate_button)
        generator.addWidget(self.add_section_button)
        generator.addWidget(self.add_block_button)
        generator.addWidget(self.undo_button)
        generator.addWidget(self.copy_button)
        generator.addWidget(self.paste_button)
        generator.addWidget(self.delete_button)
        generator.addWidget(self.anchor_button)
        generator.addStretch(1)
        outer_layout.addLayout(generator)
        self.canvas = StructureCanvas(project)
        self.canvas.append_requested.connect(self._append)
        self.canvas.rename_requested.connect(self._rename)
        self.canvas.color_requested.connect(self._recolor)
        self.canvas.delete_requested.connect(self._delete_id)
        self.canvas.insert_requested.connect(self._insert)
        self.canvas.add_block_requested.connect(self._add_block)
        self.canvas.resize_block_requested.connect(self._resize_block)
        self.canvas.delete_block_requested.connect(self._delete_block)
        self.canvas.anchor_block_requested.connect(self.anchor_block_requested)
        self.canvas.block_label_requested.connect(self._rename_block)
        self.canvas.position_requested.connect(self.position_requested)
        layout.addWidget(self.canvas, 1)
        self.status = QLabel("Drag on the blank row to append a section.")
        layout.addWidget(self.status)
        self.scroll_area.setWidget(content)
        outer_layout.addWidget(self.scroll_area)
        self.copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.canvas)
        self.copy_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.copy_shortcut.activated.connect(self._copy_selected)
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self.canvas)
        self.paste_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.paste_shortcut.activated.connect(self._paste_after_selected)
        self.undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self.canvas)
        self.undo_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.undo_shortcut.activated.connect(self._undo)
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.canvas)
        self.delete_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.delete_shortcut.activated.connect(self._delete_selection)
        self.enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self.canvas)
        self.enter_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.enter_shortcut.activated.connect(self._add_section)
        self.keypad_enter_shortcut = QShortcut(
            QKeySequence(Qt.Key.Key_Enter), self.canvas
        )
        self.keypad_enter_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.keypad_enter_shortcut.activated.connect(self._add_section)
        self.ctrl_enter_shortcut = QShortcut(
            QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Return),
            self.canvas,
        )
        self.ctrl_enter_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.ctrl_enter_shortcut.activated.connect(self._add_count_at_selection)
        self.ctrl_keypad_enter_shortcut = QShortcut(
            QKeySequence(Qt.KeyboardModifier.ControlModifier | Qt.Key.Key_Enter),
            self.canvas,
        )
        self.ctrl_keypad_enter_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.ctrl_keypad_enter_shortcut.activated.connect(self._add_count_at_selection)

    def _toolbar_button(
        self, role: IconRole, name: str, callback: Callable[[], None]
    ) -> QToolButton:
        button = QToolButton(self)
        button.setIcon(semantic_icon(button, role))
        button.setIconSize(QSize(20, 20))
        button.setAccessibleName(name)
        button.setToolTip(name)
        button.clicked.connect(callback)
        return button

    def _toolbar_separator(self) -> QFrame:
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def set_project(self, project: Project) -> None:
        self.project = project
        existing = {region.id for region in project.regions}
        self.canvas.selected_ids.intersection_update(existing)
        if self.canvas.selected_id not in existing:
            self.canvas.selected_id = None
        if self.canvas.selected_block_id not in existing:
            self.canvas.selected_block_id = None
        self.canvas.set_project(project)

    def set_playhead_beat(self, beat: Fraction | None) -> None:
        self.canvas.playhead_beat = beat
        self.canvas.update()

    def _commit(self, project: Project, *, record_history: bool = True) -> None:
        if record_history and project != self.project:
            self._history.append(self.project)
        self.set_project(project)
        self.project_changed.emit(project)

    def remember_project(self, project: Project) -> None:
        """Make an externally coordinated Structure change undoable."""

        if not self._history or self._history[-1] != project:
            self._history.append(project)

    def _zoom_in(self) -> None:
        self.canvas.set_horizontal_zoom(self.canvas.beat_width * 1.2)

    def _zoom_out(self) -> None:
        self.canvas.set_horizontal_zoom(self.canvas.beat_width / 1.2)

    def _zoom_fit(self) -> None:
        longest = max(
            (float(row.duration) for row in self.canvas._rows()), default=32.0
        )
        available = max(1, self.scroll_area.viewport().width() - _LABEL_WIDTH - 20)
        self.canvas.set_horizontal_zoom(available / longest)
        self.scroll_area.horizontalScrollBar().setValue(0)

    def _add_section(self) -> None:
        selected = [
            region
            for region in self.project.regions
            if region.parent_id is None and region.id in self.canvas.selected_ids
        ]
        if selected:
            after = max(selected, key=lambda region: region.start)
            self._insert(after.id)
        else:
            self._append(32)

    def _generate(self) -> None:
        self._commit(generate_structure_template(self.project, self._selected_template))

    def _add_template_action(self, menu: QMenu, template: StructureTemplate) -> None:
        action = menu.addAction(template.name)
        action.triggered.connect(
            lambda checked=False, item=template: self._select_template(item)
        )

    def _select_template(self, template: StructureTemplate) -> None:
        self._selected_template = template
        self._update_template_button()
        self._generate()

    def _update_template_button(self) -> None:
        self.generate_button.setToolTip(
            f"Generate {self._selected_template.name} · "
            f"{self._selected_template.section_beats} beats per section; "
            "use the arrow for alternatives"
        )

    def _append(self, duration: int) -> None:
        self._commit(append_section(self.project, duration))

    def _anchor_selected(self) -> None:
        if self.canvas.selected_block_id is None:
            self.status.setText("Select a count block first.")
            return
        self.anchor_block_requested.emit(self.canvas.selected_block_id)

    def _position_toggle_changed(self, enabled: bool) -> None:
        self.canvas.selection_positions_playhead = enabled

    def _ruler_numbers_toggle_changed(self, enabled: bool) -> None:
        self.canvas.continuous_ruler_numbers = enabled
        self.canvas.update()

    def _editing_text(self) -> bool:
        return isinstance(QApplication.focusWidget(), (QLineEdit, QSpinBox))

    def _undo(self) -> None:
        if self._editing_text():
            return
        if not self._history:
            self.status.setText("Nothing to undo.")
            return
        previous = self._history.pop()
        self._commit(previous, record_history=False)
        self.status.setText("Undid the last Structure command.")

    def _delete_selection(self) -> None:
        if self._editing_text():
            return
        block_id = self.canvas.selected_block_id
        if block_id is not None:
            self._delete_block(block_id)
            self.canvas.selected_block_id = None
            return
        if self.canvas.selected_ids:
            self._commit(delete_sections(self.project, tuple(self.canvas.selected_ids)))
            self.canvas.selected_ids.clear()
            self.canvas.selected_id = None
            self.status.setText("Deleted selected section(s).")

    def _add_count_at_selection(self) -> None:
        if self._editing_text():
            return
        previous_ids = {region.id for region in self.project.regions}
        if self.canvas.selected_block_id is not None:
            project = insert_block_after(self.project, self.canvas.selected_block_id)
        elif self.canvas.selected_id in self.canvas.selected_ids:
            assert self.canvas.selected_id is not None
            project = add_block(self.project, self.canvas.selected_id)
        else:
            self.status.setText("Select a section or count block first.")
            return
        self._commit(project)
        new_blocks = [
            region
            for region in project.regions
            if region.parent_id is not None and region.id not in previous_ids
        ]
        self.canvas.selected_block_id = new_blocks[0].id
        self.canvas.update()
        self.status.setText("Added an 8-count block.")

    def _copy_selected(self) -> None:
        if not self.canvas.selected_ids:
            self.status.setText("Select one or more sections to copy.")
            return
        self._clipboard = section_patterns(
            self.project, tuple(self.canvas.selected_ids)
        )
        self.status.setText(f"Copied {len(self._clipboard)} section(s).")

    def _paste_after_selected(self) -> None:
        if not self._clipboard:
            self.status.setText("Copy one or more sections first.")
            return
        selected = [
            region
            for region in self.project.regions
            if region.parent_id is None and region.id in self.canvas.selected_ids
        ]
        if not selected:
            self.status.setText("Select the row after which to paste.")
            return
        after = max(selected, key=lambda region: region.start)
        previous_ids = {region.id for region in self.project.regions}
        pasted = paste_sections(self.project, self._clipboard, after.id)
        new_ids = {
            region.id
            for region in pasted.regions
            if region.parent_id is None and region.id not in previous_ids
        }
        self._commit(pasted)
        self.canvas.selected_ids = new_ids
        self.canvas.selected_id = next(iter(new_ids), None)
        self.canvas.update()
        self.status.setText(f"Pasted {len(new_ids)} section(s).")

    def _insert(self, section_id: str) -> None:
        self._commit(insert_section_after(self.project, section_id))

    def _add_block(self, section_id: str) -> None:
        self._commit(add_block(self.project, section_id))

    def _resize_block(self, block_id: str, duration: int) -> None:
        try:
            self._commit(resize_block(self.project, block_id, duration))
        except StructureEditError as error:
            self.status.setText(str(error))

    def _delete_block(self, block_id: str) -> None:
        try:
            self._commit(delete_block(self.project, block_id))
        except StructureEditError as error:
            self.status.setText(str(error))

    def _rename_block(self, block_id: str, label: str) -> None:
        self._commit(update_block_label(self.project, block_id, label))

    def _rename(self, region_id: str, label: str) -> None:
        region = self._region(region_id)
        self._update(region, label=label, color=region.color or "#bfdbfe")

    def _recolor(self, region_id: str, color: str) -> None:
        region = self._region(region_id)
        self._update(region, label=region.label, color=color)

    def _delete_id(self, region_id: str) -> None:
        self._commit(delete_section(self.project, region_id))
        self.canvas.selected_id = None

    def _region(self, region_id: str) -> MusicalRegion:
        return next(region for region in self.project.regions if region.id == region_id)

    def _update(self, region: MusicalRegion, *, label: str, color: str) -> None:
        try:
            self._commit(
                update_section(
                    self.project,
                    region.id,
                    label=label,
                    duration=int(region.duration),
                    color=color,
                )
            )
        except StructureEditError as error:
            self.status.setText(str(error))
