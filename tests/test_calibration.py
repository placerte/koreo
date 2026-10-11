"""Tests for exact beat/media calibration and tap tempo."""

# [GH-15] [S-M2-02] [S-M2-03] [T-M2-01] [T-M2-04]

from dataclasses import replace
from fractions import Fraction

import pytest

from koreo.domain.calibration import (
    BeatCalibration,
    CalibrationError,
    TapTempo,
    parse_bpm,
)
from koreo.fixtures import representative_project


def test_decimal_bpm_parses_exactly() -> None:
    assert parse_bpm("118.76") == Fraction(2969, 25)


@pytest.mark.parametrize("text", ["", "nope", "0", "-120", "NaN", "Infinity"])
def test_invalid_bpm_text_is_rejected(text: str) -> None:
    with pytest.raises(CalibrationError, match="BPM"):
        parse_bpm(text)


def test_exact_beat_seconds_round_trip_including_negative_beats() -> None:
    calibration = BeatCalibration(
        bpm=Fraction(2969, 25),
        anchor_beat=Fraction(0),
        anchor_seconds=Fraction(7, 5),
    )

    for beat in (Fraction(-3, 2), Fraction(0), Fraction(17, 3), Fraction(64)):
        assert calibration.beat_at(calibration.seconds_at(beat)) == beat


def test_calibration_point_refines_one_global_bpm() -> None:
    initial = BeatCalibration(Fraction(120), Fraction(2))
    refined = initial.with_calibration_point(Fraction(256), Fraction(130))

    assert refined.bpm == Fraction(120)
    assert refined.calibration_beat == Fraction(256)
    assert refined.calibration_seconds == Fraction(130)


@pytest.mark.parametrize(
    ("beat", "seconds"),
    [
        (Fraction(0), Fraction(10)),
        (Fraction(8), Fraction(10)),
        (Fraction(8), Fraction(9)),
        (Fraction(-8), Fraction(11)),
    ],
)
def test_invalid_calibration_points_are_rejected_atomically(
    beat: Fraction, seconds: Fraction
) -> None:
    original = BeatCalibration(Fraction(120), Fraction(10))

    with pytest.raises(CalibrationError):
        original.with_calibration_point(beat, seconds)

    assert original == BeatCalibration(Fraction(120), Fraction(10))


def test_bpm_and_anchor_changes_do_not_rewrite_project_beats() -> None:
    project = representative_project()
    beats_before = (
        tuple((region.start, region.duration) for region in project.regions),
        tuple((move.start, move.duration) for move in project.moves),
    )
    calibrated = replace(
        project,
        calibration=BeatCalibration(Fraction(120), Fraction(2)).with_bpm(Fraction(118)),
    )
    moved = replace(
        calibrated,
        calibration=(
            calibrated.calibration.with_anchor(Fraction(5))
            if calibrated.calibration
            else None
        ),
    )

    assert (
        tuple((region.start, region.duration) for region in moved.regions),
        tuple((move.start, move.duration) for move in moved.moves),
    ) == beats_before


def test_tap_tempo_uses_first_to_last_interval() -> None:
    tempo = TapTempo()

    assert tempo.tap(Fraction(10)) is None
    assert tempo.tap(Fraction(21, 2)) == Fraction(120)
    assert tempo.tap(Fraction(111, 10)) == Fraction(1200, 11)
    assert tempo.tap_count == 3


def test_tap_timeout_reset_explicit_reset_and_auto_repeat() -> None:
    tempo = TapTempo()
    tempo.tap(Fraction(0))
    assert tempo.tap(Fraction(1, 2), auto_repeat=True) is None
    assert tempo.tap_count == 1
    assert tempo.tap(Fraction(1, 2)) == Fraction(120)

    assert tempo.tap(Fraction(7, 2)) is None
    assert tempo.tap_count == 1
    tempo.reset()
    assert tempo.tap_count == 0
    assert tempo.estimate is None


def test_tap_timestamps_must_increase() -> None:
    tempo = TapTempo()
    tempo.tap(Fraction(1))

    with pytest.raises(CalibrationError, match="increase"):
        tempo.tap(Fraction(1))
