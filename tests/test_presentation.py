"""Tests for GUI-independent Timeline and Sheet mappings."""

# [GH-6] [GH-7] [GH-8] [T-07] [T-08]

from fractions import Fraction

import pytest

from koreo.fixtures import representative_project
from koreo.presentation.mapping import build_sheet, build_timeline


def test_timeline_exposes_hierarchy_tracks_moves_and_gap() -> None:
    project = representative_project()
    timeline = build_timeline(project)

    assert timeline.project_id == project.id
    assert {region.id for region in timeline.regions} == {
        region.id for region in project.regions
    }
    assert any(region.depth == 1 for region in timeline.regions)
    assert {row.id for row in timeline.tracks} == {track.id for track in project.tracks}
    assert {move.id for row in timeline.tracks for move in row.moves} == {
        move.id for move in project.moves
    }
    assert any(
        gap.start == Fraction(22) and gap.end == Fraction(24) for gap in timeline.gaps
    )


def test_sheet_segments_crossing_move_without_changing_identity_or_interval() -> None:
    project = representative_project()
    sheet = build_sheet(project, beats_per_line=16)
    segments = [
        segment
        for line in sheet.lines
        for row in line.tracks
        for segment in row.segments
        if segment.move_id == "lead-cross-wrap"
    ]

    assert len(segments) == 2
    assert segments[0].continues_after
    assert segments[1].continues_before
    assert not segments[0].continues_before
    assert not segments[1].continues_after
    assert segments[0].start == Fraction(30)
    assert segments[0].end == segments[1].start == Fraction(32)
    assert segments[1].end == Fraction(35)
    assert {segment.move_id for segment in segments} == {"lead-cross-wrap"}


def test_timeline_and_sheet_share_source_identity_and_intervals() -> None:
    project = representative_project()
    snapshot = repr(project)
    timeline = build_timeline(project)
    sheet = build_sheet(project)

    timeline_moves = {
        move.id: (move.start, move.end) for row in timeline.tracks for move in row.moves
    }
    sheet_moves: dict[str, tuple[Fraction, Fraction]] = {}
    for move in project.moves:
        matching = sorted(
            (
                segment
                for line in sheet.lines
                for row in line.tracks
                for segment in row.segments
                if segment.move_id == move.id
            ),
            key=lambda segment: segment.start,
        )
        sheet_moves[move.id] = (matching[0].start, matching[-1].end)

    assert timeline_moves == sheet_moves
    assert {region.id: (region.start, region.end) for region in timeline.regions} == {
        region.id: (region.start, region.end) for region in sheet.regions
    }
    assert repr(project) == snapshot


def test_sheet_distinguishes_unassigned_gap_from_empty_move_cell() -> None:
    sheet = build_sheet(representative_project())
    cells = {cell.start: cell for line in sheet.lines for cell in line.counts}

    assert cells[Fraction(22)].region_id is None
    assert cells[Fraction(22)].region_label is None
    assert cells[Fraction(26)].region_id == "b"


def test_sheet_uses_region_count_group_and_partial_final_line() -> None:
    sheet = build_sheet(representative_project(), beats_per_line=16)
    cells = {cell.start: cell for line in sheet.lines for cell in line.counts}

    assert cells[Fraction(5)].label == "6"
    assert cells[Fraction(30)].label == "1"
    assert sheet.lines[-1].end == Fraction(52)


def test_sheet_rejects_non_positive_wrap_size() -> None:
    with pytest.raises(ValueError, match="positive"):
        build_sheet(representative_project(), beats_per_line=0)
