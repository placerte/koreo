"""Native project archive round-trip and failure tests."""

from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from koreo.audio import AudioSource
from koreo.domain.calibration import BeatCalibration
from koreo.fixtures import representative_project
from koreo.persistence import ProjectFileError, load_project, save_project


def test_project_and_embedded_audio_round_trip_exactly(tmp_path: Path) -> None:
    audio_path = tmp_path / "song.wav"
    audio_path.write_bytes(b"RIFF-test-audio")
    audio = AudioSource("song.wav", audio_path, Fraction(123, 2), 44_100, 2, "Int16")
    project = replace(
        representative_project(),
        calibration=BeatCalibration(Fraction(279, 2), Fraction(14081, 1000)),
    )
    destination = tmp_path / "dance.kro"

    save_project(destination, project, Fraction(279, 2), audio)
    loaded = load_project(destination, tmp_path / "extracted")

    assert loaded.project == project
    assert loaded.tempo_bpm == Fraction(279, 2)
    assert loaded.audio_source is not None
    assert loaded.audio_source.path.read_bytes() == b"RIFF-test-audio"


def test_project_without_audio_round_trips(tmp_path: Path) -> None:
    destination = tmp_path / "structure.kro"
    project = representative_project()
    save_project(destination, project, Fraction(120), None)
    assert load_project(destination, tmp_path / "extract").project == project


def test_unsupported_version_is_rejected_without_extraction(tmp_path: Path) -> None:
    destination = tmp_path / "future.kro"
    with ZipFile(destination, "w") as archive:
        archive.writestr("project.json", json.dumps({"format_version": "9.0"}))

    with pytest.raises(ProjectFileError, match="Unsupported"):
        load_project(destination, tmp_path / "extract")
    assert not (tmp_path / "extract").exists()


def test_failed_save_preserves_previous_project_file(tmp_path: Path) -> None:
    destination = tmp_path / "safe.kro"
    project = representative_project()
    save_project(destination, project, Fraction(120), None)
    original = destination.read_bytes()
    missing_audio = AudioSource(
        "missing.mp3",
        tmp_path / "missing.mp3",
        Fraction(10),
        44_100,
        2,
        "Int16",
    )

    with pytest.raises(ProjectFileError, match="no longer available"):
        save_project(destination, project, Fraction(120), missing_audio)

    assert destination.read_bytes() == original
