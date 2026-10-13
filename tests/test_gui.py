"""Lightweight smoke tests for the Qt setup and editor shell."""

# [GH-7] [GH-8] [GH-9] [T-09]

from fractions import Fraction
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QKeySequence, QWheelEvent
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtTest import QSignalSpy, QTest
from PySide6.QtWidgets import QApplication
from pytest import MonkeyPatch
from pytestqt.qtbot import QtBot

from koreo.audio import AudioSource
from koreo.fixtures import representative_project
from koreo.gui.bpm_dialog import BpmDialog
from koreo.gui.main_window import MainWindow
from koreo.gui.structure_panel import _leader_points
from koreo.persistence import load_project


def test_window_uses_structure_as_its_single_workspace(qtbot: QtBot) -> None:
    project = representative_project()
    snapshot = repr(project)
    window = MainWindow(project)
    qtbot.addWidget(window)
    window.show()

    assert window.structure_panel.isVisible()
    assert window.project is project
    assert repr(project) == snapshot
    assert window.export_creation_sheet_action.text() == "Export Creation Sheet PDF…"
    assert not window.project_toolbar.isMovable()
    assert not window.project_toolbar.isFloatable()
    assert not window.open_action.icon().isNull()
    assert not window.save_action.icon().isNull()


def test_creation_sheet_export_cancel_and_unsaved_filename(
    qtbot: QtBot, monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    calls: list[tuple[Path, str]] = []

    def capture_export(project: object, path: Path, *, project_filename: str) -> None:
        del project
        calls.append((path, project_filename))

    monkeypatch.setattr(
        "koreo.gui.main_window.export_creation_sheet_pdf", capture_export
    )
    monkeypatch.setattr(
        "koreo.gui.main_window.QFileDialog.getSaveFileName",
        lambda *args: ("", ""),
    )
    window._export_creation_sheet()
    assert calls == []

    target = tmp_path / "practice"
    monkeypatch.setattr(
        "koreo.gui.main_window.QFileDialog.getSaveFileName",
        lambda *args: (str(target), "PDF files (*.pdf)"),
    )
    window._export_creation_sheet()
    assert calls == [(target.with_suffix(".pdf"), "Unsaved project")]


def test_project_name_editor_updates_authoritative_project(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)

    window.project_name_edit.setText("  Practice Draft  ")
    window.project_name_edit.editingFinished.emit()

    assert window.project.name == "Practice Draft"
    assert window.project_name_edit.text() == "Practice Draft"
    assert window.project_name_edit.font().bold()
    assert window.project_name_edit.minimumWidth() >= 320
    assert window.dirty is True

    window._set_clean()
    window.project_name_edit.setText("   ")
    window.project_name_edit.editingFinished.emit()
    assert window.project.name == "Practice Draft"
    assert window.project_name_edit.text() == "Practice Draft"
    assert window.dirty is False


def test_structure_panel_generates_aaba_rows(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.structure_panel.generate_button.click()

    assert [
        region.label for region in window.project.regions if region.parent_id is None
    ] == [
        "Intro",
        "A",
        "A",
        "B",
        "A",
        "Interlude",
        "A",
        "A",
        "B",
        "A",
        "Outro",
    ]
    assert window.structure_panel.canvas.grab().toImage().isNull() is False

    selected = window.project.regions[0]
    window.structure_panel.canvas.selected_id = selected.id
    window.structure_panel.canvas.rename_requested.emit(selected.id, "Opening")
    window.structure_panel.canvas.color_requested.emit(selected.id, "#123456")

    section = next(
        region for region in window.project.regions if region.id == selected.id
    )
    assert section.label == "Opening"
    assert section.duration == 32
    assert section.color == "#123456"

    window.structure_panel.canvas.rename_requested.emit(selected.id, "Intro 2")
    window.structure_panel.canvas.color_requested.emit(selected.id, "#bbf7d0")
    section = next(
        region for region in window.project.regions if region.id == selected.id
    )
    assert section.label == "Intro 2"
    assert section.color == "#bbf7d0"

    window.structure_panel.canvas.delete_requested.emit(selected.id)
    assert all(region.id != selected.id for region in window.project.regions)


def test_structure_block_annotation_updates_without_timing_change(
    qtbot: QtBot,
) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    panel = window.structure_panel
    panel.generate_button.click()
    block = next(region for region in window.project.regions if region.parent_id)
    original_timing = (block.start, block.duration)

    panel.canvas.block_label_requested.emit(block.id, "4: break")

    changed = next(region for region in window.project.regions if region.id == block.id)
    assert changed.label == "4: break"
    assert (changed.start, changed.duration) == original_timing
    assert panel.canvas.grab().toImage().isNull() is False


def test_note_leader_uses_left_right_and_bottom_text_anchors() -> None:
    note_rect = QRectF(0, 0, 100, 40)

    assert _leader_points(note_rect, 20, 10, 20, 50) == (
        (40, 20),
        (20, 20),
        (20, 50),
    )
    assert _leader_points(note_rect, 20, 10, 80, 50) == (
        (60, 20),
        (80, 20),
        (80, 50),
    )
    assert _leader_points(note_rect, 20, 10, 55, 50) == (
        (50, 25),
        (50, 43),
        (55, 43),
        (55, 50),
    )


def test_inline_block_edit_accepts_enter_and_escape_cancels(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.show()
    window.activateWindow()
    QApplication.processEvents()
    panel = window.structure_panel
    panel.generate_button.click()
    section = next(
        region for region in window.project.regions if region.parent_id is None
    )
    block = next(
        region for region in window.project.regions if region.parent_id == section.id
    )
    assert panel.position_toggle.isChecked()

    panel.canvas._begin_block_label_edit(section, block, 0)
    editor = panel.canvas._label_editor
    assert editor is not None
    editor.clear()
    QTest.keyClicks(editor, "4: break here")
    assert " " in editor.text()
    QTest.keyClick(editor, Qt.Key.Key_Return)
    assert editor.isVisible() is False
    assert panel.canvas._label_editor is None
    assert panel.canvas.hasFocus()
    changed = next(region for region in window.project.regions if region.id == block.id)
    assert changed.label == "4: break here"

    panel.canvas._begin_block_label_edit(section, changed, 0)
    editor = panel.canvas._label_editor
    assert editor is not None
    editor.setText("1: keypad accepted")
    QTest.keyClick(editor, Qt.Key.Key_Enter)
    assert editor.isVisible() is False
    keypad_changed = next(
        region for region in window.project.regions if region.id == block.id
    )
    assert keypad_changed.label == "1: keypad accepted"

    panel.canvas._begin_block_label_edit(section, keypad_changed, 0)
    editor = panel.canvas._label_editor
    assert editor is not None
    editor.setText("discard me")
    QTest.keyClick(editor, Qt.Key.Key_Escape)
    assert editor.isVisible() is False
    assert panel.canvas._label_editor is None
    unchanged = next(
        region for region in window.project.regions if region.id == block.id
    )
    assert unchanged.label == "1: keypad accepted"

    panel.ruler_numbers_toggle.setChecked(True)
    assert panel.canvas.continuous_ruler_numbers is True
    panel.ruler_numbers_toggle.setChecked(False)
    assert panel.canvas.continuous_ruler_numbers is False


def test_structure_panel_scrolls_when_window_is_constrained(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.structure_panel.generate_button.click()
    window.resize(900, 480)
    window.show()
    QApplication.processEvents()

    scroll_bar = window.structure_panel.scroll_area.verticalScrollBar()
    assert scroll_bar.maximum() > 0
    assert window.structure_panel.status.parent() is not None
    assert not window.structure_panel.scroll_area.isAncestorOf(
        window.structure_panel.zoom_in_button
    )


def test_structure_board_toolbar_exposes_commands_and_horizontal_zoom(
    qtbot: QtBot,
) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    panel = window.structure_panel
    panel.generate_button.click()

    buttons = (
        panel.zoom_out_button,
        panel.zoom_in_button,
        panel.zoom_fit_button,
        panel.position_toggle,
        panel.ruler_numbers_toggle,
        panel.generate_button,
        panel.add_section_button,
        panel.add_block_button,
        panel.undo_button,
        panel.copy_button,
        panel.paste_button,
        panel.delete_button,
        panel.anchor_button,
    )
    assert all(not button.icon().isNull() for button in buttons)
    assert all(button.toolTip() for button in buttons)

    initial_width = panel.canvas.beat_width
    panel.zoom_in_button.click()
    assert panel.canvas.beat_width > initial_width

    ctrl_wheel = QWheelEvent(
        QPointF(300, 100),
        QPointF(300, 100),
        QPoint(),
        QPoint(0, -120),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.ControlModifier,
        Qt.ScrollPhase.NoScrollPhase,
        False,
    )
    QApplication.sendEvent(panel.canvas, ctrl_wheel)
    assert panel.canvas.beat_width < initial_width * 1.2

    section_count = len(
        [region for region in window.project.regions if region.parent_id is None]
    )
    panel.canvas.selected_ids.clear()
    panel.add_section_button.click()
    assert (
        len([region for region in window.project.regions if region.parent_id is None])
        == section_count + 1
    )


def test_structure_template_split_button_selects_forms(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    panel = window.structure_panel

    assert panel.generate_button.accessibleName() == "Generate structure from template"
    assert panel.generate_button.menu() is not None
    abab = next(
        action
        for action in panel.generate_button.menu().actions()
        if action.text() == "ABAB"
    )
    abab.trigger()
    assert [
        region.label for region in window.project.regions if region.parent_id is None
    ] == ["A", "B", "A", "B"]

    blues = next(
        action
        for action in panel.generate_button.menu().actions()
        if action.text() == "AAB · 12-bar blues"
    )
    blues.trigger()
    sections = [region for region in window.project.regions if region.parent_id is None]
    assert [region.label for region in sections] == ["A", "A", "B"]
    assert all(region.duration == 16 for region in sections)
    abab.trigger()
    sections = [region for region in window.project.regions if region.parent_id is None]
    assert all(region.duration == 32 for region in sections)


def test_structure_block_aligns_to_existing_waveform_anchor(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.structure_panel.generate_button.click()
    sections = [r for r in window.project.regions if r.parent_id is None]
    first_a_block = next(
        region
        for region in window.project.regions
        if region.parent_id == sections[1].id
    )
    window._set_anchor()
    assert window.project.calibration is not None
    original_anchor_seconds = window.project.calibration.anchor_seconds
    original_anchor_ms = window.waveform.anchor_ms

    window._anchor_structure_block(first_a_block.id)

    rebased = [r for r in window.project.regions if r.parent_id is None]
    assert rebased[0].start == -32
    assert rebased[1].start == 0
    assert window.project.calibration is not None
    assert window.project.calibration.anchor_seconds == original_anchor_seconds
    assert window.waveform.anchor_ms == original_anchor_ms
    assert len(window.waveform.structure_bands) == 11
    assert window.waveform.structure_bands[0][3] == "Intro"
    assert window.section_labels_toggle.isChecked()
    assert window.waveform.show_structure_labels is True
    window.section_labels_toggle.setChecked(False)
    assert window.waveform.show_structure_labels is False
    window.section_labels_toggle.setChecked(True)
    assert window.waveform.show_structure_labels is True
    window._position_changed(0)
    assert window.structure_panel.canvas.playhead_beat == 0


def test_structure_selection_can_seek_section_or_block(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.structure_panel.generate_button.click()
    window._set_anchor()
    window.structure_panel.position_toggle.setChecked(True)
    seek_spy = QSignalSpy(window.structure_panel.position_requested)
    canvas = window.structure_panel.canvas
    canvas.resize(800, 400)

    QTest.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(30, 98))
    QTest.mouseClick(canvas, Qt.MouseButton.LeftButton, pos=QPoint(150, 98))

    assert seek_spy.count() == 2
    assert seek_spy.at(0)[0] == Fraction(32)
    assert seek_spy.at(1)[0] == Fraction(32)


def test_structure_rows_support_multi_copy_and_paste(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    panel = window.structure_panel
    panel.generate_button.click()
    sections = [r for r in window.project.regions if r.parent_id is None]
    panel.canvas.selected_ids = {sections[1].id, sections[2].id}

    panel._copy_selected()
    panel.canvas.selected_ids = {sections[3].id}
    panel._paste_after_selected()

    pasted_sections = sorted(
        (r for r in window.project.regions if r.parent_id is None),
        key=lambda region: region.start,
    )
    assert [region.label for region in pasted_sections[4:6]] == ["A", "A"]
    assert len(pasted_sections) == 13
    assert len(panel.canvas.selected_ids) == 2


def test_structure_keyboard_commands_add_delete_and_undo(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    panel = window.structure_panel
    panel.generate_button.click()
    sections = sorted(
        (r for r in window.project.regions if r.parent_id is None),
        key=lambda region: region.start,
    )
    first_block = next(
        r for r in window.project.regions if r.parent_id == sections[0].id
    )
    panel.canvas.selected_ids = {sections[0].id}
    panel.canvas.selected_id = sections[0].id
    panel.canvas.selected_block_id = first_block.id
    window.show()
    panel.canvas.setFocus()
    QApplication.processEvents()

    section_count = len(sections)
    QTest.keyClick(panel.canvas, Qt.Key.Key_Return)
    assert (
        len([region for region in window.project.regions if region.parent_id is None])
        == section_count + 1
    )

    QTest.keyClick(
        panel.canvas,
        Qt.Key.Key_Return,
        Qt.KeyboardModifier.ControlModifier,
    )
    assert (
        next(r for r in window.project.regions if r.id == sections[0].id).duration == 40
    )
    panel._delete_selection()
    assert (
        next(r for r in window.project.regions if r.id == sections[0].id).duration == 32
    )
    panel._undo()
    assert (
        next(r for r in window.project.regions if r.id == sections[0].id).duration == 40
    )
    assert panel.add_section_button.toolTip().endswith("(Enter)")
    assert panel.add_block_button.toolTip().endswith("(Ctrl+Enter)")
    assert panel.undo_button.toolTip().endswith("(Ctrl+Z)")
    assert panel.copy_button.toolTip().endswith("(Ctrl+C)")
    assert panel.paste_button.toolTip().endswith("(Ctrl+V)")
    assert panel.delete_button.toolTip().endswith("(Delete)")


def test_structure_ctrl_and_shift_row_selection(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    panel = window.structure_panel
    panel.generate_button.click()
    panel.canvas.resize(800, 400)

    QTest.mouseClick(panel.canvas, Qt.MouseButton.LeftButton, pos=QPoint(30, 48))
    QTest.mouseClick(
        panel.canvas,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.ShiftModifier,
        QPoint(30, 156),
    )
    assert len(panel.canvas.selected_ids) == 3

    QTest.mouseClick(
        panel.canvas,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.ControlModifier,
        QPoint(30, 264),
    )
    assert len(panel.canvas.selected_ids) == 4


def test_main_window_saves_current_structure_and_tracks_dirty_state(
    qtbot: QtBot, tmp_path: Path
) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    destination = tmp_path / "saved.kro"
    window.project_path = destination

    window.project_name_edit.setText("Saved project title")
    window.project_name_edit.editingFinished.emit()
    window.structure_panel.generate_button.click()
    assert window.dirty
    assert window.windowTitle().endswith("*")
    assert window._save()

    loaded = load_project(destination, tmp_path / "extract")
    assert loaded.project == window.project
    reopened = MainWindow(representative_project())
    qtbot.addWidget(reopened)
    reopened._apply_loaded_project(loaded, destination)
    assert reopened.project_name_edit.text() == "Saved project title"
    assert not window.dirty
    assert not window.windowTitle().endswith("*")
    assert window.open_action.shortcut() == QKeySequence.StandardKey.Open
    assert window.save_action.shortcut() == QKeySequence.StandardKey.Save


def test_spacebar_taps_bpm_and_cancel_stops_playback(qtbot: QtBot) -> None:
    timestamps = iter((0, 500_000_000))
    source = AudioSource(
        display_name="song.wav",
        path=Path("/tmp/song.wav"),
        duration_seconds=Fraction(60),
        sample_rate=44_100,
        channel_count=2,
        sample_format="Int16",
    )
    dialog = BpmDialog(source, clock_ns=lambda: next(timestamps))
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.tap_button.setFocus()

    QTest.keyClick(dialog, Qt.Key.Key_Space)
    QTest.keyClick(dialog, Qt.Key.Key_Space)

    assert dialog.result_bpm == Fraction(120)
    assert dialog._tap_tempo.tap_count == 2
    assert dialog.time_label.alignment() & Qt.AlignmentFlag.AlignRight
    assert dialog.time_label.minimumWidth() == dialog.time_label.maximumWidth()
    dialog.reject()
    assert dialog.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState


def test_main_window_exposes_song_and_tempo_actions(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)

    assert window.choose_song_button.text() == ""
    assert window.choose_song_button.accessibleName() == "Choose audio track"
    assert not window.choose_song_button.icon().isNull()
    for button, name in (
        (window.play_button, "Play"),
        (window.stop_button, "Stop"),
        (window.zoom_out_button, "Zoom waveform out"),
        (window.zoom_in_button, "Zoom waveform in"),
        (window.zoom_fit_button, "Fit the full waveform"),
        (window.follow_button, "Follow playhead"),
        (window.anchor_button, "Set playhead as grid Anchor"),
        (
            window.structure_panel.anchor_button,
            "Align selected block to grid Anchor",
        ),
    ):
        assert button.text() == ""
        assert button.accessibleName() == name
        assert button.toolTip()
        assert not button.icon().isNull()
        assert button.iconSize().width() == 20
        assert button.iconSize().height() == 20
    window._playback_state_changed("playing")
    assert window.play_button.accessibleName() == "Pause"
    assert window.play_button.toolTip() == "Pause"
    window._playback_state_changed("paused")
    assert window.play_button.accessibleName() == "Play"
    assert window.song_label.text() == "No song selected"
    assert window.tap_bpm_button.text() == ""
    assert window.tap_bpm_button.accessibleName() == "Tap BPM"
    assert not window.tap_bpm_button.isEnabled()
    assert window.bpm_edit.value() == 120.0
    assert window.bpm_edit.decimals() == 2
    assert window.bpm_edit.singleStep() == 0.5
    window.bpm_edit.setValue(212.477474)
    assert window.bpm_edit.text() == "212.48"
    window.bpm_edit.setValue(120.0)
    assert window.tempo_bpm == Fraction(120)
    window.count_origin_edit.setValue(-2)
    window.count_group_spin.setValue(6)
    assert window.project.count_origin == Fraction(-2)
    assert window.project.default_count_group == 6
    assert window.timeline_view.model.count_origin == Fraction(-2)

    window.bpm_edit.setValue(118.75)
    window.bpm_edit.editingFinished.emit()
    assert window.tempo_bpm == Fraction(475, 4)

    editor = window.bpm_edit.lineEdit()
    assert editor is not None
    editor.selectAll()
    QTest.keyClicks(editor, "not a tempo")
    assert not any(character.isalpha() for character in editor.text())


def test_main_waveform_transport_and_anchor_render(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.transport.setVisible(True)
    window.waveform.set_duration(60_000)
    window.waveform.resize(800, 150)
    window.waveform.set_peaks(((-0.5, 0.75), (-1.0, 1.0), (-0.25, 0.4)))
    window._position_changed(15_000)
    original_x = window.waveform._time_to_x(15_000)
    window.waveform.zoom_in()
    assert window.waveform.zoom_factor == 1.25
    assert window.waveform._time_to_x(15_000) == original_x
    window.waveform.set_follow_playhead(False)
    assert not window.follow_button.isChecked()
    window.follow_button.setChecked(True)
    assert window.waveform.follow_playhead
    window.waveform.zoom_to_fit()
    assert window.waveform.zoom_factor == 1.0
    assert window.waveform.view_start_ms == 0
    window._set_anchor()

    image = window.waveform.grab().toImage()
    assert not image.isNull()
    assert window.time_label.alignment() & Qt.AlignmentFlag.AlignRight
    assert window.time_label.minimumWidth() == window.time_label.maximumWidth()
    assert window.project.calibration is not None
    assert window.project.calibration.anchor_seconds == Fraction(15)
    assert window.waveform.anchor_ms == 15_000

    seek_spy = QSignalSpy(window.waveform.seek_requested)
    expected_time = round(window.waveform._x_to_time(400))
    QTest.mouseClick(window.waveform, Qt.MouseButton.LeftButton, pos=QPoint(400, 75))
    assert seek_spy.count() == 1
    assert seek_spy.at(0)[0] == expected_time
    window._set_anchor()
    assert window.project.calibration is not None
    assert window.project.calibration.anchor_seconds == Fraction(expected_time, 1000)

    window.waveform.zoom_in()
    drag_seek_spy = QSignalSpy(window.waveform.seek_requested)
    start_view = window.waveform.view_start_ms
    QTest.mousePress(window.waveform, Qt.MouseButton.LeftButton, pos=QPoint(500, 75))
    QTest.mouseMove(window.waveform, QPoint(300, 75))
    QTest.mouseRelease(window.waveform, Qt.MouseButton.LeftButton, pos=QPoint(300, 75))
    assert drag_seek_spy.count() == 0
    assert window.waveform.view_start_ms != start_view
    assert not window.waveform.follow_playhead

    playback_spy = QSignalSpy(window.play_pause_requested)
    window.show()
    window.activateWindow()
    QApplication.processEvents()
    window.bpm_edit.setFocus()
    window.bpm_edit.lineEdit().end(False)
    bpm_text = window.bpm_edit.text()
    QTest.keyClick(window.bpm_edit, Qt.Key.Key_Space)
    assert playback_spy.count() == 0
    assert window.bpm_edit.text() == bpm_text

    window.play_button.setFocus()
    QTest.keyClick(window.play_button, Qt.Key.Key_Space)
    assert playback_spy.count() == 1
