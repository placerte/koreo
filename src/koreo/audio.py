"""Qt Multimedia boundary for validating imported audio."""

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import struct

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioBuffer, QAudioDecoder, QAudioFormat

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


class WaveformExtractor(QObject):
    """Asynchronously reduce decoded PCM buffers to display peaks."""

    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._decoder = QAudioDecoder(self)
        self._peaks: list[tuple[float, float]] = []
        self._settled = True
        self._decoder.bufferReady.connect(self._read_buffer)
        self._decoder.finished.connect(self._finish)
        self._decoder.error.connect(self._error)

    def extract(self, path: Path) -> None:
        """Decode ``path`` and emit at most 1,200 deterministic peak pairs."""

        self.cancel()
        self._peaks = []
        self._settled = False
        self._decoder.setSource(QUrl.fromLocalFile(str(path)))
        self._decoder.start()

    def cancel(self) -> None:
        self._settled = True
        self._decoder.stop()
        self._peaks = []

    def _read_buffer(self) -> None:
        if self._settled:
            return
        buffer = self._decoder.read()
        peak = _mixed_peak(buffer)
        if peak is not None:
            self._peaks.append(peak)

    def _finish(self) -> None:
        if self._settled:
            return
        self._settled = True
        if not self._peaks:
            self.failed.emit("Waveform decoding produced no audio samples.")
            return
        self.succeeded.emit(_reduce_peaks(self._peaks, 1_200))

    def _error(self) -> None:
        if self._settled:
            return
        self._settled = True
        detail = self._decoder.errorString().strip() or "the decoder rejected it"
        self.failed.emit(f"Waveform decoding failed: {detail}.")


def _mixed_peak(buffer: QAudioBuffer) -> tuple[float, float] | None:
    if not buffer.isValid() or buffer.byteCount() <= 0:
        return None
    audio_format = buffer.format()
    channels = audio_format.channelCount()
    if channels <= 0:
        return None
    raw = bytes(buffer.constData())
    sample_format = audio_format.sampleFormat()
    if sample_format == QAudioFormat.SampleFormat.UInt8:
        samples = tuple((value - 128) / 128 for value in raw)
    else:
        format_codes = {
            QAudioFormat.SampleFormat.Int16: ("h", 32768.0),
            QAudioFormat.SampleFormat.Int32: ("i", 2147483648.0),
            QAudioFormat.SampleFormat.Float: ("f", 1.0),
        }
        details = format_codes.get(sample_format)
        if details is None:
            return None
        code, scale = details
        size = struct.calcsize(code)
        usable = len(raw) - len(raw) % size
        samples = tuple(
            value[0] / scale for value in struct.iter_unpack(f"<{code}", raw[:usable])
        )
    mixed = [
        sum(samples[index : index + channels]) / channels
        for index in range(0, len(samples) - channels + 1, channels)
    ]
    if not mixed:
        return None
    return max(-1.0, min(mixed)), min(1.0, max(mixed))


def _reduce_peaks(
    peaks: list[tuple[float, float]], limit: int
) -> tuple[tuple[float, float], ...]:
    if len(peaks) <= limit:
        return tuple(peaks)
    reduced: list[tuple[float, float]] = []
    for bucket in range(limit):
        start = bucket * len(peaks) // limit
        end = (bucket + 1) * len(peaks) // limit
        group = peaks[start:end]
        reduced.append((min(peak[0] for peak in group), max(peak[1] for peak in group)))
    return tuple(reduced)
