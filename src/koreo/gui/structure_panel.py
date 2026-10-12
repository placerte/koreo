"""Editable vertical song-structure rows."""

from fractions import Fraction

from PySide6.QtCore import QEvent, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QContextMenuEvent,
    QIcon,
    QKeySequence,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPen,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from koreo.domain.models import MusicalRegion, Project
from koreo.domain.structure import (
    SECTION_PALETTE,
    SectionPattern,
    StructureEditError,
    add_block,
    append_section,
    delete_block,
    delete_section,
    delete_sections,
    generate_aaba,
    insert_section_after,
    insert_block_after,
    paste_sections,
    resize_block,
    section_patterns,
    update_section,
)
from koreo.settings import APPEARANCE

_ROW_HEIGHT = 54
_LABEL_WIDTH = 100
_BEAT_WIDTH = 14


class StructureCanvas(QWidget):
    selected = Signal(str)
    append_requested = Signal(int)
    resize_requested = Signal(str, int)
    rename_requested = Signal(str, str)
    color_requested = Signal(str, str)
    delete_requested = Signal(str)
    insert_requested = Signal(str)
    add_block_requested = Signal(str)
    resize_block_requested = Signal(str, int)
    delete_block_requested = Signal(str)
    anchor_block_requested = Signal(str)
    position_requested = Signal(object)

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.selected_id: str | None = None
        self.selected_ids: set[str] = set()
        self.selected_block_id: str | None = None
        self.selection_anchor_id: str | None = None
        self._press: tuple[int, float, str | None] | None = None
        self._label_editor: QLineEdit | None = None
        self._resize_preview: tuple[str, int] | None = None
        self.playhead_beat: Fraction | None = None
        self.selection_positions_playhead = False
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(300)

    def set_project(self, project: Project) -> None:
        self.project = project
        self.setMinimumHeight((len(self._rows()) + 1) * _ROW_HEIGHT + 10)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        for row, region in enumerate(self._rows()):
            y = row * _ROW_HEIGHT
            base = QColor(region.color or "#bfdbfe")
            painter.fillRect(
                QRectF(2, y + 5, _LABEL_WIDTH - 8, _ROW_HEIGHT - 10),
                base.lighter(112),
            )
            painter.setPen(QPen(QColor("#334155")))
            painter.drawText(
                QRectF(6, y, _LABEL_WIDTH - 10, _ROW_HEIGHT),
                Qt.AlignmentFlag.AlignVCenter,
                region.label,
            )
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
                    _LABEL_WIDTH + float(block_offset) * _BEAT_WIDTH,
                    y + 5,
                    float(beats) * _BEAT_WIDTH,
                    _ROW_HEIGHT - 10,
                )
                shade = base if block_index % 2 == 0 else _alternate_shade(base)
                painter.fillRect(rect, shade)
                painter.setPen(QPen(QColor("#64748b")))
                painter.drawRect(rect)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(beats))
                tick = 1
                painter.setPen(QPen(QColor(71, 85, 105, 100), 1))
                while Fraction(tick) < beats:
                    tick_x = rect.left() + tick * _BEAT_WIDTH
                    painter.drawLine(
                        round(tick_x),
                        round(rect.bottom()) - 6,
                        round(tick_x),
                        round(rect.bottom()),
                    )
                    tick += 1
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
                selected_width = _LABEL_WIDTH + float(region.duration) * _BEAT_WIDTH
                painter.drawRect(QRectF(1, y + 1, selected_width, _ROW_HEIGHT - 2))
            if (
                self.playhead_beat is not None
                and region.start <= self.playhead_beat < region.end
            ):
                playhead_x = (
                    _LABEL_WIDTH
                    + float(self.playhead_beat - region.start) * _BEAT_WIDTH
                )
                painter.setPen(QPen(QColor("#dc2626"), 2))
                painter.drawLine(
                    int(playhead_x), y + 3, int(playhead_x), y + _ROW_HEIGHT - 3
                )
        blank_y = len(self._rows()) * _ROW_HEIGHT
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.setFocus()
            row = int(event.position().y() // _ROW_HEIGHT)
            rows = self._rows()
            boundary_block: str | None = None
            if row < len(rows):
                for block in self._blocks(rows[row].id):
                    endpoint = (
                        _LABEL_WIDTH + float(block.end - rows[row].start) * _BEAT_WIDTH
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
                1, round((event.position().x() - _LABEL_WIDTH) / _BEAT_WIDTH)
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
            block_x = _LABEL_WIDTH + float(block.start - region.start) * _BEAT_WIDTH
            duration = max(1, round((event.position().x() - block_x) / _BEAT_WIDTH))
            self.resize_block_requested.emit(block.id, duration)
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        row = int(event.position().y() // _ROW_HEIGHT)
        rows = self._rows()
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.position().x() < _LABEL_WIDTH
            and row < len(rows)
        ):
            self._begin_label_edit(rows[row], row)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

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
                    + float(block.start - rows[pressed_row].start) * _BEAT_WIDTH
                )
                duration = max(1, round((event.position().x() - block_x) / _BEAT_WIDTH))
                self._resize_preview = (block_id, duration)
                self.setCursor(Qt.CursorShape.SizeHorCursor)
                self.update()
                event.accept()
                return
        row = int(event.position().y() // _ROW_HEIGHT)
        rows = self._rows()
        if row < len(rows):
            endpoints = (
                _LABEL_WIDTH + float(block.end - rows[row].start) * _BEAT_WIDTH
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
        row = int(event.pos().y() // _ROW_HEIGHT)
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
        editor = QLineEdit(region.label, self)
        editor.setGeometry(2, row * _ROW_HEIGHT + 5, _LABEL_WIDTH - 8, _ROW_HEIGHT - 10)
        editor.selectAll()
        editor.show()
        editor.setFocus()
        self._label_editor = editor

        def finish() -> None:
            if self._label_editor is not editor:
                return
            value = editor.text().strip()
            editor.deleteLater()
            self._label_editor = None
            if value and value != region.label:
                self.rename_requested.emit(region.id, value)

        editor.editingFinished.connect(finish)

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
        beat = section.start + Fraction(max(0, x - _LABEL_WIDTH), _BEAT_WIDTH)
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
        self.template_duration = QSpinBox()
        self.template_duration.setRange(1, 512)
        self.template_duration.setValue(32)
        self.generate_button = QPushButton("Generate AABA")
        self.generate_button.clicked.connect(self._generate)
        self.anchor_button = QPushButton("Align selected block to grid Anchor")
        self.anchor_button.clicked.connect(self._anchor_selected)
        self.position_toggle = QCheckBox("Selection moves playhead")
        self.position_toggle.toggled.connect(self._position_toggle_changed)
        generator.addWidget(QLabel("Section beats:"))
        generator.addWidget(self.template_duration)
        generator.addWidget(self.generate_button)
        generator.addWidget(self.anchor_button)
        generator.addWidget(self.position_toggle)
        generator.addStretch(1)
        layout.addLayout(generator)
        self.canvas = StructureCanvas(project)
        self.canvas.selected.connect(self._select)
        self.canvas.append_requested.connect(self._append)
        self.canvas.resize_requested.connect(self._resize)
        self.canvas.rename_requested.connect(self._rename)
        self.canvas.color_requested.connect(self._recolor)
        self.canvas.delete_requested.connect(self._delete_id)
        self.canvas.insert_requested.connect(self._insert)
        self.canvas.add_block_requested.connect(self._add_block)
        self.canvas.resize_block_requested.connect(self._resize_block)
        self.canvas.delete_block_requested.connect(self._delete_block)
        self.canvas.anchor_block_requested.connect(self.anchor_block_requested)
        self.canvas.position_requested.connect(self.position_requested)
        layout.addWidget(self.canvas, 1)
        editor = QHBoxLayout()
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Selected section label")
        self.duration_edit = QSpinBox()
        self.duration_edit.setRange(1, 4096)
        self.duration_edit.setReadOnly(True)
        self.duration_edit.setToolTip("Derived from the section's count blocks")
        self.color_edit = QLineEdit("#bfdbfe")
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete)
        editor.addWidget(self.label_edit)
        editor.addWidget(QLabel("Total beats:"))
        editor.addWidget(self.duration_edit)
        editor.addWidget(QLabel("Color:"))
        editor.addWidget(self.color_edit)
        editor.addWidget(self.apply_button)
        editor.addWidget(self.delete_button)
        layout.addLayout(editor)
        self.status = QLabel("Drag on the blank row to append a section.")
        layout.addWidget(self.status)
        self.scroll_area.setWidget(content)
        outer_layout.addWidget(self.scroll_area)
        self.copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self)
        self.copy_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.copy_shortcut.activated.connect(self._copy_selected)
        self.paste_shortcut = QShortcut(QKeySequence.StandardKey.Paste, self)
        self.paste_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.paste_shortcut.activated.connect(self._paste_after_selected)
        self.undo_shortcut = QShortcut(QKeySequence.StandardKey.Undo, self)
        self.undo_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.undo_shortcut.activated.connect(self._undo)
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), self)
        self.delete_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.delete_shortcut.activated.connect(self._delete_selection)
        self.enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.enter_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.enter_shortcut.activated.connect(self._add_count_at_selection)
        self.keypad_enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        self.keypad_enter_shortcut.setContext(
            Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        self.keypad_enter_shortcut.activated.connect(self._add_count_at_selection)

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

    def _generate(self) -> None:
        self._commit(generate_aaba(self.project, self.template_duration.value()))

    def _append(self, duration: int) -> None:
        self._commit(append_section(self.project, duration))

    def _anchor_selected(self) -> None:
        if self.canvas.selected_block_id is None:
            self.status.setText("Select a count block first.")
            return
        self.anchor_block_requested.emit(self.canvas.selected_block_id)

    def _position_toggle_changed(self, enabled: bool) -> None:
        self.canvas.selection_positions_playhead = enabled

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
        self._commit(
            insert_section_after(
                self.project, section_id, self.template_duration.value()
            )
        )

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

    def _select(self, region_id: str) -> None:
        region = next(
            region for region in self.project.regions if region.id == region_id
        )
        self.label_edit.setText(region.label)
        self.duration_edit.setValue(int(region.duration))
        self.color_edit.setText(region.color or "#bfdbfe")

    def _resize(self, region_id: str, duration: int) -> None:
        region = next(
            region for region in self.project.regions if region.id == region_id
        )
        try:
            self._commit(
                update_section(
                    self.project,
                    region_id,
                    label=region.label,
                    duration=duration,
                    color=region.color or "#bfdbfe",
                )
            )
        except StructureEditError as error:
            self.status.setText(str(error))

    def _rename(self, region_id: str, label: str) -> None:
        region = self._region(region_id)
        self._update(region, label=label, color=region.color or "#bfdbfe")

    def _recolor(self, region_id: str, color: str) -> None:
        region = self._region(region_id)
        self._update(region, label=region.label, color=color)

    def _apply(self) -> None:
        if self.canvas.selected_id is None:
            return
        try:
            self._commit(
                update_section(
                    self.project,
                    self.canvas.selected_id,
                    label=self.label_edit.text(),
                    duration=self.duration_edit.value(),
                    color=self.color_edit.text(),
                )
            )
        except StructureEditError as error:
            self.status.setText(str(error))

    def _delete(self) -> None:
        if self.canvas.selected_id is None:
            return
        self._delete_id(self.canvas.selected_id)

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
