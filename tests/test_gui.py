"""Lightweight smoke tests for the Qt setup and editor shell."""

# [GH-7] [GH-8] [GH-9] [T-09]

from fractions import Fraction
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtTest import QTest
from pytestqt.qtbot import QtBot

from koreo.audio import AudioSource
from koreo.fixtures import representative_project
from koreo.gui.bpm_dialog import BpmDialog
from koreo.gui.main_window import MainWindow


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

    assert window.choose_song_button.text() == "Choose song…"
    assert window.song_label.text() == "No song selected"
    assert window.tap_bpm_button.text() == "Tap BPM"
    assert not window.tap_bpm_button.isEnabled()
    assert window.bpm_edit.text() == "120"
    assert window.tempo_bpm == Fraction(120)

    window.bpm_edit.setText("118.75")
    window.bpm_edit.editingFinished.emit()
    assert window.tempo_bpm == Fraction(475, 4)

    window.bpm_edit.setText("not a tempo")
    window.bpm_edit.editingFinished.emit()
    assert window.bpm_edit.text() == "118.75"


def test_main_waveform_transport_and_anchor_render(qtbot: QtBot) -> None:
    window = MainWindow(representative_project())
    qtbot.addWidget(window)
    window.transport.setVisible(True)
    window.waveform.set_duration(60_000)
    window.waveform.set_peaks(((-0.5, 0.75), (-1.0, 1.0), (-0.25, 0.4)))
    window._position_changed(15_000)
    window._set_anchor()

    image = window.waveform.grab().toImage()
    assert not image.isNull()
    assert window.time_label.alignment() & Qt.AlignmentFlag.AlignRight
    assert window.time_label.minimumWidth() == window.time_label.maximumWidth()
    assert window.project.calibration is not None
    assert window.project.calibration.anchor_seconds == Fraction(0)
    assert window.waveform.anchor_ms == 0
