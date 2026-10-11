"""Qt Multimedia boundary for validating imported audio."""

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioDecoder

# [GH-13] [S-M2-01] Actual decoder output, not an extension, validates audio.


@dataclass(frozen=True, slots=True)
class AudioSource:
    """Metadata retained for one validated local audio source."""

    display_name: str
    path: Path
    duration_seconds: Fraction
    sample_rate: int
    channel_count: int
    sample_format: str


class AudioProbe(QObject):
    """Asynchronously confirm that a local MP3/WAV yields decoded PCM."""

    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._decoder = QAudioDecoder(self)
        self._path: Path | None = None
        self._settled = True
        self._decoder.bufferReady.connect(self._on_buffer_ready)
        self._decoder.error.connect(self._on_error)
        self._decoder.finished.connect(self._on_finished)

    def probe(self, path: Path) -> None:
        """Validate ``path`` and emit exactly one terminal result."""

        self.cancel()
        try:
            resolved = path.expanduser().resolve(strict=True)
        except (OSError, RuntimeError) as error:
            self.failed.emit(f"Cannot open that file: {error}")
            return
        if resolved.suffix.lower() not in {".mp3", ".wav"}:
            self.failed.emit("Choose an MP3 or WAV file.")
            return
        try:
            if not resolved.is_file() or resolved.stat().st_size == 0:
                self.failed.emit("The selected audio file is empty or unreadable.")
                return
        except OSError as error:
            self.failed.emit(f"Cannot read that file: {error}")
            return

        self._path = resolved
        self._settled = False
        self._decoder.setSource(QUrl.fromLocalFile(str(resolved)))
        self._decoder.start()

    def cancel(self) -> None:
        """Stop any active probe without emitting a result."""

        self._settled = True
        self._decoder.stop()
        self._path = None

    def _on_buffer_ready(self) -> None:
        if self._settled or self._path is None:
            return
        buffer = self._decoder.read()
        if not buffer.isValid() or buffer.byteCount() <= 0:
            return
        audio_format = buffer.format()
        source = AudioSource(
            display_name=self._path.name,
            path=self._path,
            duration_seconds=Fraction(max(self._decoder.duration(), 0), 1000),
            sample_rate=audio_format.sampleRate(),
            channel_count=audio_format.channelCount(),
            sample_format=str(audio_format.sampleFormat()).rsplit(".", 1)[-1],
        )
        self._settled = True
        self._decoder.stop()
        self.succeeded.emit(source)

    def _on_error(self) -> None:
        if self._settled:
            return
        detail = self._decoder.errorString().strip() or "the decoder rejected it"
        self._reject(f"Could not decode this audio file: {detail}.")

    def _on_finished(self) -> None:
        if not self._settled:
            self._reject(
                "Could not decode this audio file: it contained no audio samples."
            )

    def _reject(self, message: str) -> None:
        self._settled = True
        self._decoder.stop()
        self._path = None
        self.failed.emit(message)
