"""Application playback controller around Qt Multimedia."""

from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

# [GH-14] [S-M2-04] One application playback state owner.


class PlaybackController(QObject):
    """Own one media player and expose primitive playback state."""

    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(str)
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._output = QAudioOutput(self)
        self._player = QMediaPlayer(self)
        self._player.setAudioOutput(self._output)
        self._player.positionChanged.connect(self._on_position)
        self._player.durationChanged.connect(self._on_duration)
        self._player.playbackStateChanged.connect(self._on_state)
        self._player.errorOccurred.connect(self._on_error)

    @property
    def position(self) -> int:
        return self._player.position()

    @property
    def duration(self) -> int:
        return self._player.duration()

    @property
    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def load(self, path: Path) -> None:
        self.stop()
        self._player.setSource(QUrl.fromLocalFile(str(path)))

    def play(self) -> None:
        self._player.play()

    def pause(self) -> None:
        self._player.pause()

    def stop(self) -> None:
        self._player.stop()
        self._player.setPosition(0)

    def seek(self, milliseconds: int) -> None:
        self._player.setPosition(max(0, min(milliseconds, self.duration)))

    def _on_state(self, state: QMediaPlayer.PlaybackState) -> None:
        names = {
            QMediaPlayer.PlaybackState.PlayingState: "playing",
            QMediaPlayer.PlaybackState.PausedState: "paused",
            QMediaPlayer.PlaybackState.StoppedState: "stopped",
        }
        self.state_changed.emit(names[state])

    def _on_position(self, position: int) -> None:
        self.position_changed.emit(position)

    def _on_duration(self, duration: int) -> None:
        self.duration_changed.emit(duration)

    def _on_error(self) -> None:
        detail = self._player.errorString().strip() or "unknown playback error"
        self.failed.emit(detail)
