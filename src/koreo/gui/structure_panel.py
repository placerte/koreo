"""Editable vertical song-structure rows."""

from fractions import Fraction

from PySide6.QtCore import QEvent, QRectF, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QContextMenuEvent,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import (
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
    StructureEditError,
    append_section,
    delete_section,
    generate_aaba,
    update_section,
)

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

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.selected_id: str | None = None
        self._press: tuple[int, float] | None = None
        self._label_editor: QLineEdit | None = None
        self.setMouseTracking(True)
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
            blocks = max(1, (region.duration.numerator + 7) // 8)
            for block in range(blocks):
                beats = min(Fraction(8), region.duration - block * 8)
                rect = QRectF(
                    _LABEL_WIDTH + block * 8 * _BEAT_WIDTH,
                    y + 5,
                    float(beats) * _BEAT_WIDTH,
                    _ROW_HEIGHT - 10,
                )
                shade = base if block % 2 == 0 else base.lighter(118)
                painter.fillRect(rect, shade)
                painter.setPen(QPen(QColor("#64748b")))
                painter.drawRect(rect)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(beats))
            if region.id == self.selected_id:
                painter.setPen(QPen(QColor("#2563eb"), 3))
                painter.drawRect(QRectF(1, y + 1, self.width() - 2, _ROW_HEIGHT - 2))
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
            self._press = (
                int(event.position().y() // _ROW_HEIGHT),
                event.position().x(),
            )
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton or self._press is None:
            return
        row, start_x = self._press
        self._press = None
        rows = self._rows()
        if row >= len(rows):
            duration = max(
                1, round((event.position().x() - _LABEL_WIDTH) / _BEAT_WIDTH)
            )
            self.append_requested.emit(duration)
            return
        region = rows[row]
        self.selected_id = region.id
        self.selected.emit(region.id)
        if abs(event.position().x() - start_x) >= 6:
            duration = max(
                1, round((event.position().x() - _LABEL_WIDTH) / _BEAT_WIDTH)
            )
            self.resize_requested.emit(region.id, duration)
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
        row = int(event.position().y() // _ROW_HEIGHT)
        rows = self._rows()
        if row < len(rows):
            endpoint = _LABEL_WIDTH + float(rows[row].duration) * _BEAT_WIDTH
            if abs(event.position().x() - endpoint) <= 6:
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
        self.selected.emit(region.id)
        menu = QMenu(self)
        color_menu = menu.addMenu("Section color")
        assert color_menu is not None
        for color in SECTION_PALETTE:
            action = color_menu.addAction(color)
            action.setData(color)
        color_menu.triggered.connect(
            lambda action: self.color_requested.emit(region.id, str(action.data()))
        )
        menu.addSeparator()
        delete_action = menu.addAction("Delete section")
        chosen = menu.exec(event.globalPos())
        if chosen is delete_action:
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


class StructurePanel(QWidget):
    project_changed = Signal(object)

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
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
        generator.addWidget(QLabel("Section beats:"))
        generator.addWidget(self.template_duration)
        generator.addWidget(self.generate_button)
        generator.addStretch(1)
        layout.addLayout(generator)
        self.canvas = StructureCanvas(project)
        self.canvas.selected.connect(self._select)
        self.canvas.append_requested.connect(self._append)
        self.canvas.resize_requested.connect(self._resize)
        self.canvas.rename_requested.connect(self._rename)
        self.canvas.color_requested.connect(self._recolor)
        self.canvas.delete_requested.connect(self._delete_id)
        layout.addWidget(self.canvas, 1)
        editor = QHBoxLayout()
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Selected section label")
        self.duration_edit = QSpinBox()
        self.duration_edit.setRange(1, 4096)
        self.color_edit = QLineEdit("#bfdbfe")
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete)
        editor.addWidget(self.label_edit)
        editor.addWidget(QLabel("Beats:"))
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

    def set_project(self, project: Project) -> None:
        self.project = project
        self.canvas.set_project(project)

    def _commit(self, project: Project) -> None:
        self.set_project(project)
        self.project_changed.emit(project)

    def _generate(self) -> None:
        self._commit(generate_aaba(self.project, self.template_duration.value()))

    def _append(self, duration: int) -> None:
        self._commit(append_section(self.project, duration))

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
