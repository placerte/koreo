"""Editable choreography board over a read-only musical Structure reference."""

from dataclasses import dataclass
from fractions import Fraction
from collections.abc import Callable
from typing import Literal

from PySide6.QtCore import QEvent, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QContextMenuEvent,
    QFocusEvent,
    QKeyEvent,
    QKeySequence,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPen,
    QShortcut,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from koreo.domain.models import Move, MusicalRegion, Project
from koreo.gui.colors import text_color, translucent
from koreo.gui.icons import IconRole, semantic_icon
from koreo.gui.sticky_ruler import StickyRuler
from koreo.settings import APPEARANCE

_LABEL_WIDTH = 145
_RULER_HEIGHT = 28
_SECTION_HEADER = 25
_TRACK_HEIGHT = 34
_BEAT_WIDTH = 28.0
_MIN_BEAT_WIDTH = 6.0
_MAX_BEAT_WIDTH = 80.0


@dataclass(frozen=True, slots=True)
class MoveEditRequest:
    """A proposed timing edit awaiting validation/conflict resolution."""

    action: Literal["create", "move", "resize"]
    track_id: str
    start: Fraction
    duration: Fraction
    release_beat: Fraction
    move_id: str | None = None


@dataclass(frozen=True, slots=True)
class _Drag:
    action: Literal["create", "move", "resize"]
    track_id: str
    origin_beat: Fraction
    move_id: str | None = None
    original_start: Fraction = Fraction(0)
    original_duration: Fraction = Fraction(0)
    edge: Literal["start", "end"] | None = None


class _InlineMoveEditor(QLineEdit):
    """Single-line editor with explicit accept and cancel semantics."""

    accepted = Signal()
    cancelled = Signal()

    def __init__(self, text: str, parent: QWidget) -> None:
        super().__init__(text, parent)
        self._finished = False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._finished = True
            self.accepted.emit()
            return
        if event.key() == Qt.Key.Key_Escape:
            self._finished = True
            self.cancelled.emit()
            return
        super().keyPressEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:  # noqa: N802
        super().focusOutEvent(event)
        if not self._finished:
            self._finished = True
            self.accepted.emit()


class ChoreographyCanvas(QWidget):
    """Paint Structure rows and directly manipulate smaller move overlays."""

    edit_requested = Signal(object)
    selected = Signal(object)
    position_requested = Signal(object)
    label_requested = Signal(str, str)
    delete_requested = Signal(str)
    zoom_changed = Signal()

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.selected_move_id: str | None = None
        self.playhead_beat: Fraction | None = None
        self.selection_positions_playhead = True
        self.continuous_ruler_numbers = False
        self.beat_width = _BEAT_WIDTH
        self._drag: _Drag | None = None
        self._dragging_playhead = False
        self._preview: tuple[Fraction, Fraction, str] | None = None
        self._editor: _InlineMoveEditor | None = None
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.set_project(project)

    def set_project(self, project: Project) -> None:
        self.project = project
        if self.selected_move_id not in {move.id for move in project.moves}:
            self.selected_move_id = None
        longest = max((float(row.duration) for row in self._rows()), default=32.0)
        height = _RULER_HEIGHT + sum(self._row_height() for _ in self._rows()) + 20
        self.setMinimumSize(_LABEL_WIDTH + int(longest * self.beat_width) + 24, height)
        self.updateGeometry()
        self.update()

    def set_horizontal_zoom(self, beat_width: float) -> None:
        """Change horizontal beat scale without affecting vertical scrolling."""

        self.beat_width = min(_MAX_BEAT_WIDTH, max(_MIN_BEAT_WIDTH, beat_width))
        self.set_project(self.project)
        self.zoom_changed.emit()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.set_horizontal_zoom(self.beat_width * factor)
            event.accept()
            return
        super().wheelEvent(event)

    def _rows(self) -> tuple[MusicalRegion, ...]:
        return tuple(
            sorted(
                (region for region in self.project.regions if region.parent_id is None),
                key=lambda region: region.start,
            )
        )

    def _row_height(self) -> int:
        return (
            self._section_header_height()
            + max(1, len(self.project.tracks)) * _TRACK_HEIGHT
            + 5
        )

    def _section_header_height(self) -> int:
        return _SECTION_HEADER if len(self.project.tracks) > 1 else 0

    def _row_at(self, y: float) -> tuple[MusicalRegion, int] | None:
        top = _RULER_HEIGHT
        for row in self._rows():
            bottom = top + self._row_height()
            if top <= y < bottom:
                track_index = max(
                    0,
                    int((y - top - self._section_header_height()) // _TRACK_HEIGHT),
                )
                return row, min(track_index, max(0, len(self.project.tracks) - 1))
            top = bottom
        return None

    def _beat_at(self, point: QPointF, *, snapped: bool) -> tuple[Fraction, str] | None:
        hit = self._row_at(point.y())
        if hit is None or not self.project.tracks:
            return None
        row, track_index = hit
        raw = max(
            0.0, min(float(row.duration), (point.x() - _LABEL_WIDTH) / self.beat_width)
        )
        beat = row.start + Fraction(raw).limit_denominator(1000)
        if snapped:
            beat = Fraction(round(float(beat)))
        return (
            beat,
            sorted(self.project.tracks, key=lambda track: track.display_order)[
                track_index
            ].id,
        )

    def _segment_rects(self) -> list[tuple[Move, QRectF]]:
        result: list[tuple[Move, QRectF]] = []
        top = _RULER_HEIGHT
        tracks = sorted(self.project.tracks, key=lambda track: track.display_order)
        track_index = {track.id: index for index, track in enumerate(tracks)}
        for row in self._rows():
            for move in self.project.moves:
                if move.track_id not in track_index:
                    continue
                start = max(move.start, row.start)
                end = min(move.end, row.end)
                if start >= end:
                    continue
                lane_y = (
                    top
                    + self._section_header_height()
                    + track_index[move.track_id] * _TRACK_HEIGHT
                )
                result.append(
                    (
                        move,
                        QRectF(
                            _LABEL_WIDTH + float(start - row.start) * self.beat_width,
                            lane_y + 5,
                            max(2.0, float(end - start) * self.beat_width),
                            _TRACK_HEIGHT - 10,
                        ),
                    )
                )
            top += self._row_height()
        return result

    def _move_hit(self, point: QPointF) -> tuple[Move, QRectF] | None:
        hits = [
            (move, rect)
            for move, rect in reversed(self._segment_rects())
            if rect.contains(point)
        ]
        if len(hits) > 1 and self.selected_move_id is not None:
            selected = next(
                (item for item in hits if item[0].id == self.selected_move_id), None
            )
            if selected is not None:
                return selected
        return hits[0] if hits else None

    def _playhead_hit(self, point: QPointF) -> bool:
        if self.playhead_beat is None:
            return False
        hit = self._row_at(point.y())
        if hit is None:
            return False
        row, _track_index = hit
        if not row.start <= self.playhead_beat <= row.end:
            return False
        x = _LABEL_WIDTH + float(self.playhead_beat - row.start) * self.beat_width
        return abs(point.x() - x) <= 6

    def _playhead_beat_at(self, point: QPointF) -> Fraction | None:
        hit = self._row_at(point.y())
        if hit is None:
            return None
        row, _track_index = hit
        local = max(
            0.0, min(float(row.duration), (point.x() - _LABEL_WIDTH) / self.beat_width)
        )
        return row.start + Fraction(local).limit_denominator(1000)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#f8fafc"))
        rows = self._rows()
        self._paint_ruler(painter)
        top = _RULER_HEIGHT
        tracks = sorted(self.project.tracks, key=lambda track: track.display_order)
        children = [
            region for region in self.project.regions if region.parent_id is not None
        ]
        for row in rows:
            base = QColor(row.color or "#dbeafe")
            painter.fillRect(
                QRectF(0, top, _LABEL_WIDTH - 5, self._row_height() - 4),
                base.lighter(108),
            )
            painter.setPen(QPen(QColor("#475569")))
            header_height = self._section_header_height()
            if header_height:
                painter.drawText(
                    QRectF(8, top, _LABEL_WIDTH - 16, header_height),
                    Qt.AlignmentFlag.AlignVCenter,
                    row.label,
                )
            row_rect = QRectF(
                _LABEL_WIDTH,
                top,
                float(row.duration) * self.beat_width,
                self._row_height() - 4,
            )
            painter.fillRect(row_rect, base.lighter(125))
            for child in children:
                if child.parent_id != row.id:
                    continue
                rect = QRectF(
                    _LABEL_WIDTH + float(child.start - row.start) * self.beat_width,
                    top,
                    float(child.duration) * self.beat_width,
                    self._row_height() - 4,
                )
                painter.fillRect(
                    rect,
                    base.lighter(
                        112 if int(child.start - row.start) % 16 == 0 else 135
                    ),
                )
                painter.setPen(QPen(base.darker(125)))
                painter.drawRect(rect)
            group = max(1, self.project.default_count_group)
            for beat in range(int(row.duration) + 1):
                x = _LABEL_WIDTH + beat * self.beat_width
                painter.setPen(
                    QPen(
                        QColor(90, 110, 135, 105 if beat % group == 0 else 48),
                        2 if beat % group == 0 else 1,
                    )
                )
                painter.drawLine(int(x), top, int(x), top + self._row_height() - 4)
            for index, track in enumerate(tracks):
                lane_y = top + header_height + index * _TRACK_HEIGHT
                painter.setPen(QPen(QColor(track.color), 1))
                painter.drawText(
                    QRectF(8, lane_y, _LABEL_WIDTH - 16, _TRACK_HEIGHT),
                    Qt.AlignmentFlag.AlignVCenter,
                    row.label if len(tracks) == 1 else track.name,
                )
                painter.setPen(QPen(QColor(100, 116, 139, 70)))
                painter.drawLine(
                    _LABEL_WIDTH,
                    lane_y + _TRACK_HEIGHT,
                    int(row_rect.right()),
                    lane_y + _TRACK_HEIGHT,
                )
            top += self._row_height()
        for move, rect in self._segment_rects():
            track = next(
                track for track in self.project.tracks if track.id == move.track_id
            )
            background = translucent(track.color, 205)
            painter.fillRect(rect, background)
            selected = move.id == self.selected_move_id
            painter.setPen(
                QPen(
                    QColor("#2563eb") if selected else QColor(track.color).darker(130),
                    3 if selected else 1,
                )
            )
            painter.drawRoundedRect(rect, 3, 3)
            painter.setPen(QPen(text_color(background)))
            label = painter.fontMetrics().elidedText(
                move.label,
                Qt.TextElideMode.ElideRight,
                max(0, int(rect.width()) - 12),
            )
            painter.drawText(
                rect.adjusted(5, 1, -5, -1), Qt.AlignmentFlag.AlignCenter, label
            )
            if move.start < self._row_for_rect(rect).start:
                painter.drawText(
                    rect.adjusted(2, 0, 0, 0),
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                    "‹",
                )
            if move.end > self._row_for_rect(rect).end:
                painter.drawText(
                    rect.adjusted(0, 0, -2, 0),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    "›",
                )
        if self._preview is not None:
            start, duration, track_id = self._preview
            self._paint_preview(painter, start, duration, track_id)
        if self.playhead_beat is not None:
            self._paint_playhead(painter)
        painter.end()

    def _paint_ruler(self, painter: QPainter) -> None:
        longest = max((int(row.duration) for row in self._rows()), default=0)
        group = max(1, self.project.default_count_group)
        painter.fillRect(0, 0, self.width(), _RULER_HEIGHT, QColor("#f8fafc"))
        for beat in range(longest + 1):
            x = _LABEL_WIDTH + beat * self.beat_width
            primary = beat % group == 0
            label_alpha = (
                APPEARANCE.structure_primary_grid_label_alpha
                if primary
                else APPEARANCE.structure_grid_label_alpha
            )
            ruler_color = QColor("#475569")
            ruler_color.setAlphaF(label_alpha)
            painter.setPen(QPen(ruler_color, 2 if primary else 1))
            label = beat + 1 if self.continuous_ruler_numbers else beat % group + 1
            painter.drawText(
                QRectF(x - 12, 2, 24, 20), Qt.AlignmentFlag.AlignCenter, str(label)
            )
            painter.drawLine(
                round(x),
                _RULER_HEIGHT - (8 if primary else 5),
                round(x),
                _RULER_HEIGHT,
            )
        painter.setPen(QPen(QColor("#64748b"), 1))
        painter.drawLine(
            _LABEL_WIDTH,
            _RULER_HEIGHT - 1,
            round(_LABEL_WIDTH + longest * self.beat_width),
            _RULER_HEIGHT - 1,
        )

    def _row_for_rect(self, rect: QRectF) -> MusicalRegion:
        hit = self._row_at(rect.center().y())
        assert hit is not None
        return hit[0]

    def _paint_preview(
        self, painter: QPainter, start: Fraction, duration: Fraction, track_id: str
    ) -> None:
        temporary = Move("preview", track_id, start, duration, "")
        original = self.project
        self.project = Project(
            original.id,
            original.name,
            original.tracks,
            original.regions,
            original.moves + (temporary,),
            original.default_count_group,
            original.count_origin,
            original.calibration,
        )
        rects = [rect for move, rect in self._segment_rects() if move.id == "preview"]
        self.project = original
        painter.setPen(QPen(QColor("#2563eb"), 2, Qt.PenStyle.DashLine))
        for rect in rects:
            painter.drawRect(rect)

    def _paint_playhead(self, painter: QPainter) -> None:
        assert self.playhead_beat is not None
        top = _RULER_HEIGHT
        for row in self._rows():
            if row.start <= self.playhead_beat <= row.end:
                x = (
                    _LABEL_WIDTH
                    + float(self.playhead_beat - row.start) * self.beat_width
                )
                painter.setPen(QPen(QColor("#ef4444"), 2))
                painter.drawLine(int(x), top, int(x), top + self._row_height() - 4)
            top += self._row_height()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        self.setFocus()
        if self._playhead_hit(event.position()):
            self._dragging_playhead = True
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            event.accept()
            return
        snapped = not bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        beat_track = self._beat_at(event.position(), snapped=snapped)
        if beat_track is None:
            return
        beat, track_id = beat_track
        hit = self._move_hit(event.position())
        if hit is None:
            self.selected_move_id = None
            self.selected.emit(None)
            self._drag = _Drag("create", track_id, beat)
            return
        move, rect = hit
        self.selected_move_id = move.id
        self.selected.emit(move.id)
        if self.selection_positions_playhead:
            self.position_requested.emit(move.start)
        edge: Literal["start", "end"] | None = None
        if abs(event.position().x() - rect.left()) <= 6:
            edge = "start"
        elif abs(event.position().x() - rect.right()) <= 6:
            edge = "end"
        action: Literal["move", "resize"] = "resize" if edge else "move"
        self.setCursor(
            Qt.CursorShape.SizeHorCursor if edge else Qt.CursorShape.ClosedHandCursor
        )
        self._drag = _Drag(
            action, move.track_id, beat, move.id, move.start, move.duration, edge
        )
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._dragging_playhead and event.buttons() & Qt.MouseButton.LeftButton:
            beat = self._playhead_beat_at(event.position())
            if beat is not None:
                self.position_requested.emit(beat)
            event.accept()
            return
        if self._drag is None or not event.buttons() & Qt.MouseButton.LeftButton:
            self._update_hover_cursor(event.position())
            super().mouseMoveEvent(event)
            return
        snapped = not bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        beat_track = self._beat_at(event.position(), snapped=snapped)
        if beat_track is None:
            return
        beat, track_id = beat_track
        drag = self._drag
        if drag.action == "create":
            start, end = sorted((drag.origin_beat, beat))
            self._preview = (
                start,
                max(Fraction(1) if snapped else Fraction(1, 1000), end - start),
                track_id,
            )
        elif drag.action == "move":
            self._preview = (
                drag.original_start + beat - drag.origin_beat,
                drag.original_duration,
                track_id,
            )
        elif drag.edge == "start":
            end = drag.original_start + drag.original_duration
            self._preview = (
                min(beat, end - Fraction(1, 1000)),
                end - min(beat, end - Fraction(1, 1000)),
                drag.track_id,
            )
        else:
            self._preview = (
                drag.original_start,
                max(Fraction(1, 1000), beat - drag.original_start),
                drag.track_id,
            )
        self.update()

    def _update_hover_cursor(self, point: QPointF) -> None:
        if self._playhead_hit(point):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            return
        hit = self._move_hit(point)
        if hit is None:
            self.setCursor(Qt.CursorShape.CrossCursor)
            return
        _move, rect = hit
        if abs(point.x() - rect.left()) <= 6 or abs(point.x() - rect.right()) <= 6:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._dragging_playhead:
            self._dragging_playhead = False
            beat = self._playhead_beat_at(event.position())
            if beat is not None:
                self.position_requested.emit(beat)
            self._update_hover_cursor(event.position())
            event.accept()
            return
        if event.button() != Qt.MouseButton.LeftButton or self._drag is None:
            return super().mouseReleaseEvent(event)
        drag = self._drag
        preview = self._preview
        snapped = not bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        beat_track = self._beat_at(event.position(), snapped=snapped)
        self._drag = None
        self._preview = None
        if preview is not None:
            start, duration, track_id = preview
            release_beat = beat_track[0] if beat_track is not None else start
            self.edit_requested.emit(
                MoveEditRequest(
                    drag.action,
                    track_id,
                    start,
                    duration,
                    release_beat,
                    drag.move_id,
                )
            )
        self._update_hover_cursor(event.position())
        self.update()

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self.unsetCursor()
        super().leaveEvent(event)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:  # noqa: N802
        menu = QMenu(self)
        hit = self._move_hit(QPointF(event.pos()))
        if hit is None:
            beat_track = self._beat_at(QPointF(event.pos()), snapped=True)
            if beat_track is None:
                return
            beat, track_id = beat_track
            row_hit = self._row_at(event.pos().y())
            assert row_hit is not None
            duration = min(Fraction(8), row_hit[0].end - beat)
            if duration <= 0:
                return
            add_action = menu.addAction("Add move here")
            chosen = menu.exec(event.globalPos())
            if chosen is add_action:
                self.edit_requested.emit(
                    MoveEditRequest("create", track_id, beat, duration, beat)
                )
            return
        move, _rect = hit
        self.selected_move_id = move.id
        self.selected.emit(move.id)
        rename_action = menu.addAction("Rename move")
        delete_action = menu.addAction("Delete move")
        chosen = menu.exec(event.globalPos())
        if chosen is rename_action:
            self.begin_label_edit(move.id)
        elif chosen is delete_action:
            self.delete_requested.emit(move.id)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        hit = self._move_hit(event.position())
        if hit is None:
            return super().mouseDoubleClickEvent(event)
        self.begin_label_edit(hit[0].id, hit[1])

    def begin_label_edit(self, move_id: str, rect: QRectF | None = None) -> None:
        """Select a move and open its inline label editor."""

        move = next((item for item in self.project.moves if item.id == move_id), None)
        if move is None:
            return
        if rect is None:
            rect = next(
                (
                    segment
                    for item, segment in self._segment_rects()
                    if item.id == move_id
                ),
                None,
            )
        if rect is None:
            return
        if self._editor is not None:
            self._finish_editor(move_id, False)
        self.selected_move_id = move_id
        self.selected.emit(move_id)
        editor = _InlineMoveEditor(move.label, self)
        editor.setGeometry(rect.toRect())
        editor.selectAll()
        editor.show()
        editor.setFocus()
        editor.accepted.connect(lambda: self._finish_editor(move.id, True))
        editor.cancelled.connect(lambda: self._finish_editor(move.id, False))
        self._editor = editor

    def _finish_editor(self, move_id: str, accept: bool) -> None:
        if self._editor is None:
            return
        editor = self._editor
        self._editor = None
        label = editor.text().strip()
        editor.deleteLater()
        if accept and label:
            self.label_requested.emit(move_id, label)


class ChoreographyPanel(QWidget):
    """Board, editing tools, and selected-move inspector."""

    edit_requested = Signal(object)
    details_requested = Signal(object)
    delete_requested = Signal(str)
    undo_requested = Signal()
    redo_requested = Signal()
    position_requested = Signal(object)

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        tools = QHBoxLayout()
        tools.addWidget(QLabel("View:"))
        self.zoom_out_button = self._button(
            IconRole.ZOOM_OUT,
            "Zoom Choreography board out (Ctrl+Mouse Wheel Down)",
            self._zoom_out,
        )
        self.zoom_in_button = self._button(
            IconRole.ZOOM_IN,
            "Zoom Choreography board in (Ctrl+Mouse Wheel Up)",
            self._zoom_in,
        )
        self.zoom_fit_button = self._button(
            IconRole.ZOOM_FIT,
            "Fit Choreography board width",
            self._zoom_fit,
        )
        tools.addWidget(self.zoom_out_button)
        tools.addWidget(self.zoom_in_button)
        tools.addWidget(self.zoom_fit_button)
        self.ruler_numbers_toggle = QToolButton(self)
        self.ruler_numbers_toggle.setIcon(
            semantic_icon(self.ruler_numbers_toggle, IconRole.CONTINUOUS_COUNTS)
        )
        self.ruler_numbers_toggle.setIconSize(QSize(20, 20))
        self.ruler_numbers_toggle.setAccessibleName("Continuous ruler numbers")
        self.ruler_numbers_toggle.setToolTip("Continuous ruler numbers")
        self.ruler_numbers_toggle.setCheckable(True)
        self.ruler_numbers_toggle.toggled.connect(self._ruler_numbers_toggle_changed)
        tools.addWidget(self.ruler_numbers_toggle)
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        tools.addWidget(separator)
        tools.addWidget(QLabel("Edit:"))
        self.inspector_button = self._button(
            IconRole.PANEL_RIGHT_OPEN,
            "Open move details panel",
            self._toggle_inspector,
        )
        self.undo_button = self._button(
            IconRole.UNDO, "Undo (Ctrl+Z)", self.undo_requested.emit
        )
        self.redo_button = self._button(
            IconRole.REDO, "Redo (Ctrl+Shift+Z)", self.redo_requested.emit
        )
        self.delete_button = self._button(
            IconRole.DELETE, "Delete selected move (Delete)", self._delete
        )
        self.add_button = self._button(IconRole.ADD_BLOCK, "Add move", self._add_move)
        self.rename_button = self._button(
            IconRole.EDIT, "Rename selected move", self._rename
        )
        tools.addWidget(self.add_button)
        tools.addWidget(self.rename_button)
        tools.addWidget(self.undo_button)
        tools.addWidget(self.redo_button)
        tools.addWidget(self.delete_button)
        tools.addStretch(1)
        tools.addWidget(self.inspector_button)
        layout.addLayout(tools)
        splitter = QSplitter()
        self.splitter = splitter
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.canvas = ChoreographyCanvas(project)
        self.scroll_area.setWidget(self.canvas)
        self.ruler = StickyRuler(
            self.scroll_area, _RULER_HEIGHT, self.canvas._paint_ruler
        )
        self.canvas.zoom_changed.connect(self.ruler.refresh)
        splitter.addWidget(self.scroll_area)
        self.inspector = QWidget()
        self.inspector.setMinimumWidth(230)
        self.inspector.setMaximumWidth(330)
        form = QFormLayout(self.inspector)
        self.selection_label = QLabel("No move selected")
        self.label_edit = QLineEdit()
        self.notes_edit = QPlainTextEdit()
        self.notes_edit.setMaximumHeight(120)
        self.start_edit = QLineEdit()
        self.duration_edit = QLineEdit()
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_details)
        form.addRow(self.selection_label)
        form.addRow("Label:", self.label_edit)
        form.addRow("Notes:", self.notes_edit)
        form.addRow("Start beat:", self.start_edit)
        form.addRow("Duration:", self.duration_edit)
        form.addRow(self.apply_button)
        splitter.addWidget(self.inspector)
        splitter.setStretchFactor(0, 1)
        self.inspector.hide()
        layout.addWidget(splitter, 1)
        self.canvas.edit_requested.connect(self.edit_requested)
        self.canvas.selected.connect(self._selection_changed)
        self.canvas.position_requested.connect(self.position_requested)
        self.canvas.label_requested.connect(self._label_changed)
        self.canvas.delete_requested.connect(self.delete_requested)
        self._set_inspector_enabled(False)
        self._shortcut(QKeySequence(Qt.Key.Key_Delete), self._delete)

    def _button(
        self, role: IconRole, tooltip: str, callback: Callable[[], None]
    ) -> QToolButton:
        button = QToolButton(self)
        button.setIcon(semantic_icon(button, role))
        button.setIconSize(QSize(20, 20))
        button.setToolTip(tooltip)
        button.setAccessibleName(tooltip)
        button.clicked.connect(callback)
        return button

    def _toggle_inspector(self) -> None:
        visible = not self.inspector.isVisible()
        self.inspector.setVisible(visible)
        role = IconRole.PANEL_RIGHT_CLOSE if visible else IconRole.PANEL_RIGHT_OPEN
        name = "Close move details panel" if visible else "Open move details panel"
        self.inspector_button.setIcon(semantic_icon(self.inspector_button, role))
        self.inspector_button.setToolTip(name)
        self.inspector_button.setAccessibleName(name)
        if visible:
            self.splitter.setSizes([max(1, self.width() - 280), 280])

    def _shortcut(self, sequence: QKeySequence, callback: Callable[[], None]) -> None:
        shortcut = QShortcut(sequence, self.canvas)
        shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        shortcut.activated.connect(callback)

    def set_project(self, project: Project) -> None:
        self.project = project
        self.canvas.set_project(project)
        self.ruler.refresh()
        self._selection_changed(self.canvas.selected_move_id)

    def set_playhead_beat(self, beat: Fraction | None) -> None:
        self.canvas.playhead_beat = beat
        self.canvas.update()

    def _zoom_in(self) -> None:
        self.canvas.set_horizontal_zoom(self.canvas.beat_width * 1.2)

    def _zoom_out(self) -> None:
        self.canvas.set_horizontal_zoom(self.canvas.beat_width / 1.2)

    def _zoom_fit(self) -> None:
        longest = max(
            (float(row.duration) for row in self.canvas._rows()), default=32.0
        )
        available = max(1, self.scroll_area.viewport().width() - _LABEL_WIDTH - 24)
        self.canvas.set_horizontal_zoom(available / longest)
        self.scroll_area.horizontalScrollBar().setValue(0)

    def _ruler_numbers_toggle_changed(self, enabled: bool) -> None:
        self.canvas.continuous_ruler_numbers = enabled
        self.canvas.update()
        self.ruler.refresh()

    def _selection_changed(self, move_id: object) -> None:
        self.canvas.selected_move_id = move_id if isinstance(move_id, str) else None
        move = next((move for move in self.project.moves if move.id == move_id), None)
        self._set_inspector_enabled(move is not None)
        if move is None:
            self.selection_label.setText("No move selected")
            return
        self.selection_label.setText("Selected move")
        self.label_edit.setText(move.label)
        self.notes_edit.setPlainText(move.notes or "")
        self.start_edit.setText(str(move.start))
        self.duration_edit.setText(str(move.duration))
        self.canvas.update()

    def _set_inspector_enabled(self, enabled: bool) -> None:
        for widget in (
            self.label_edit,
            self.notes_edit,
            self.start_edit,
            self.duration_edit,
            self.apply_button,
        ):
            widget.setEnabled(enabled)

    def _apply_details(self) -> None:
        move_id = self.canvas.selected_move_id
        if move_id is None:
            return
        try:
            start = Fraction(self.start_edit.text())
            duration = Fraction(self.duration_edit.text())
        except (ValueError, ZeroDivisionError):
            return
        self.details_requested.emit(
            (
                move_id,
                self.label_edit.text().strip(),
                self.notes_edit.toPlainText() or None,
                start,
                duration,
            )
        )

    def _label_changed(self, move_id: str, label: str) -> None:
        move = next(move for move in self.project.moves if move.id == move_id)
        self.details_requested.emit(
            (move_id, label, move.notes, move.start, move.duration)
        )

    def _delete(self) -> None:
        if self.canvas.selected_move_id is not None:
            self.delete_requested.emit(self.canvas.selected_move_id)

    def _rename(self) -> None:
        if self.canvas.selected_move_id is not None:
            self.canvas.begin_label_edit(self.canvas.selected_move_id)

    def _add_move(self) -> None:
        rows = self.canvas._rows()
        tracks = sorted(self.project.tracks, key=lambda item: item.display_order)
        if not rows or not tracks:
            return
        row = next(
            (
                item
                for item in rows
                if self.canvas.playhead_beat is not None
                and item.start <= self.canvas.playhead_beat < item.end
            ),
            rows[0],
        )
        start = self.canvas.playhead_beat or row.start
        start = max(row.start, min(start, row.end - 1))
        duration = min(Fraction(8), row.end - start)
        self.edit_requested.emit(
            MoveEditRequest("create", tracks[0].id, start, duration, start)
        )
