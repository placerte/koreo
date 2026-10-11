"""Lightweight smoke tests for the Qt setup and editor shell."""

# [GH-7] [GH-8] [GH-9] [T-09]

from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtTest import QTest
from pytestqt.qtbot import QtBot

from koreo.fixtures import representative_project
from koreo.gui.main_window import MainWindow
from koreo.gui.setup_dialog import SetupDialog


def test_window_renders_both_views_and_switches_without_mutation(qtbot: QtBot) -> None:
    project = representative_project()
    snapshot = repr(project)
    window = MainWindow(project)
    qtbot.addWidget(window)
    window.show()

    assert window.tabs.count() == 2
    assert window.tabs.tabText(0) == "Timeline"
    assert window.tabs.tabText(1) == "Sheet"
    assert window.timeline_view.model.project_id == project.id
    assert window.sheet_view.model.project_id == project.id

    window.tabs.setCurrentIndex(1)
    assert window.tabs.currentWidget() is window.sheet_view
    window.tabs.setCurrentIndex(0)
    assert window.tabs.currentWidget() is window.timeline_view
    assert window.project is project
    assert repr(project) == snapshot


def test_both_view_canvases_render_to_images(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.show()

    timeline_image = window.timeline_view.canvas.grab().toImage()
    window.tabs.setCurrentIndex(1)
    sheet_image = window.sheet_view.canvas.grab().toImage()

    assert not timeline_image.isNull()
    assert not sheet_image.isNull()
    assert timeline_image.width() > 0
    assert sheet_image.height() > 0


def test_focused_spacebar_taps_bpm_without_starting_playback(qtbot: QtBot) -> None:
    timestamps = iter((0, 500_000_000))
    dialog = SetupDialog(representative_project(), clock_ns=lambda: next(timestamps))
    qtbot.addWidget(dialog)
    dialog.show()
    dialog.tap_button.setFocus()

    QTest.keyClick(dialog.tap_button, Qt.Key.Key_Space)
    QTest.keyClick(dialog.tap_button, Qt.Key.Key_Space)

    assert dialog.bpm_edit.text() == "120"
    assert dialog.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState
    assert dialog._tap_tempo.tap_count == 2
