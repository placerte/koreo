"""Native project archive round-trip and failure tests."""

from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from koreo.audio import AudioSource
from koreo.domain.calibration import BeatCalibration
from koreo.domain.models import ChoreographyTrack, Move
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

    peaks = ((-0.5, 0.75), (-1.0, 1.0))
    save_project(destination, project, Fraction(279, 2), audio, peaks)
    loaded = load_project(destination, tmp_path / "extracted")

    assert loaded.project == project
    assert loaded.tempo_bpm == Fraction(279, 2)
    assert loaded.audio_source is not None
    assert loaded.audio_source.path.read_bytes() == b"RIFF-test-audio"
    assert loaded.waveform_peaks == peaks


def test_project_without_audio_round_trips(tmp_path: Path) -> None:
    destination = tmp_path / "structure.kro"
    project = representative_project()
    save_project(destination, project, Fraction(120), None)
    assert load_project(destination, tmp_path / "extract").project == project


def test_legacy_demo_tracks_and_moves_migrate_to_empty_choreography_track(
    tmp_path: Path,
) -> None:
    project = representative_project()
    legacy = replace(
        project,
        tracks=(
            ChoreographyTrack("lead", "Lead", 0, "#3b82f6"),
            ChoreographyTrack("follow", "Follow", 1, "#f97316"),
        ),
        moves=(
            Move("lead-rock", "lead", Fraction(0), Fraction(1), "Rock step"),
            Move("lead-triple", "lead", Fraction(2), Fraction(1), "Triple"),
            Move("lead-cross-section", "lead", Fraction(4), Fraction(1), "Send"),
            Move("lead-cross-wrap", "lead", Fraction(6), Fraction(1), "Cross"),
            Move("follow-basic", "follow", Fraction(0), Fraction(1), "Basic"),
            Move("follow-tuck", "follow", Fraction(2), Fraction(1), "Tuck"),
            Move("follow-gap", "follow", Fraction(4), Fraction(1), "Travel"),
            Move("follow-finish", "follow", Fraction(6), Fraction(1), "Finish"),
        ),
    )
    destination = tmp_path / "legacy.kro"
    save_project(destination, legacy, Fraction(140), None)

    loaded = load_project(destination, tmp_path / "extract")

    assert loaded.migrated
    assert loaded.project.regions == project.regions
    assert loaded.project.moves == ()
    assert tuple((track.id, track.name) for track in loaded.project.tracks) == (
        ("choreography", "Choreography"),
    )


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
