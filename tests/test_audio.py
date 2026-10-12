"""Tests for the Qt audio validation boundary."""

# [GH-13] [GH-14] [S-M2-01] [S-M2-05] [T-M2-05] [T-M2-07]

import wave
from pathlib import Path

from pytestqt.qtbot import QtBot

from koreo.audio import AudioProbe, AudioSource, WaveformExtractor


def _write_silent_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(8_000)
        output.writeframes(bytes(1_600))


def test_real_qt_decoder_accepts_a_valid_wav(qtbot: QtBot, tmp_path: Path) -> None:
    path = tmp_path / "known.wav"
    _write_silent_wav(path)
    probe = AudioProbe()

    with qtbot.waitSignal(probe.succeeded, timeout=5_000) as result:
        probe.probe(path)

    source = result.args[0]
    assert isinstance(source, AudioSource)
    assert source.path == path.resolve()
    assert source.sample_rate == 8_000
    assert source.channel_count == 1


def test_probe_rejects_an_empty_or_wrong_extension(
    qtbot: QtBot, tmp_path: Path
) -> None:
    probe = AudioProbe()
    empty = tmp_path / "empty.mp3"
    empty.touch()
    wrong_extension = tmp_path / "audio.ogg"
    wrong_extension.write_bytes(b"not audio")

    with qtbot.waitSignal(probe.failed) as empty_result:
        probe.probe(empty)
    with qtbot.waitSignal(probe.failed) as extension_result:
        probe.probe(wrong_extension)

    assert "empty" in empty_result.args[0]
    assert "MP3 or WAV" in extension_result.args[0]


def test_real_qt_decoder_extracts_bounded_waveform_peaks(
    qtbot: QtBot, tmp_path: Path
) -> None:
    path = tmp_path / "waveform.wav"
    _write_silent_wav(path)
    extractor = WaveformExtractor()

    with qtbot.waitSignal(extractor.succeeded, timeout=5_000) as result:
        extractor.extract(path)

    peaks = result.args[0]
    assert peaks
    assert len(peaks) <= 30_000
    assert all(-1.0 <= minimum <= maximum <= 1.0 for minimum, maximum in peaks)
