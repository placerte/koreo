"""Map one validated project into Timeline and Sheet view data."""

from fractions import Fraction

from koreo.domain.models import Move, MusicalRegion, Project
from koreo.domain.validation import validate_project
from koreo.presentation.models import (
    CountCell,
    GapSpan,
    MoveSegment,
    MoveSpan,
    RegionSpan,
    SheetLine,
    SheetModel,
    SheetTrackRow,
    TimelineModel,
    TrackRow,
)


def build_timeline(project: Project) -> TimelineModel:
    """Build a continuous read-only timeline from ``project``."""

    # [GH-6] [S-M1-08] Presentation data is derived outside the GUI.
    validate_project(project)
    start, end = _project_bounds(project)
    regions_by_id = {region.id: region for region in project.regions}
    regions = tuple(
        RegionSpan(
            id=region.id,
            label=region.label,
            start=region.start,
            end=region.end,
            depth=_region_depth(region, regions_by_id),
        )
        for region in sorted(project.regions, key=lambda item: (item.start, item.id))
    )
    tracks = tuple(
        TrackRow(
            id=track.id,
            name=track.name,
            color=track.color,
            moves=tuple(
                MoveSpan(
                    id=move.id,
                    track_id=move.track_id,
                    label=move.label,
                    start=move.start,
                    end=move.end,
                    color=track.color,
                )
                for move in _moves_for_track(project, track.id)
            ),
        )
        for track in sorted(project.tracks, key=lambda item: item.display_order)
    )
    return TimelineModel(
        project_id=project.id,
        project_name=project.name,
        start=start,
        end=end,
        count_origin=project.count_origin,
        count_group=project.default_count_group,
        regions=regions,
        gaps=_top_level_gaps(project, start, end),
        tracks=tracks,
    )


def build_sheet(project: Project, *, beats_per_line: int = 16) -> SheetModel:
    """Build deterministic wrapped sheet lines from ``project``."""

    # [GH-6] [S-M1-08] Segments preserve source identity across line wraps.
    validate_project(project)
    if beats_per_line <= 0:
        raise ValueError("beats_per_line must be positive")
    start, end = _project_bounds(project)
    regions_by_id = {region.id: region for region in project.regions}
    regions = tuple(
        RegionSpan(
            id=region.id,
            label=region.label,
            start=region.start,
            end=region.end,
            depth=_region_depth(region, regions_by_id),
        )
        for region in sorted(project.regions, key=lambda item: (item.start, item.id))
    )
    line_start = Fraction(_floor_fraction(start))
    final_end = Fraction(_ceil_fraction(end))
    lines: list[SheetLine] = []
    index = 0
    while line_start < final_end:
        line_end = min(line_start + beats_per_line, final_end)
        counts = tuple(
            _count_cell(project, Fraction(beat), Fraction(beat + 1))
            for beat in range(int(line_start), int(line_end))
        )
        rows = tuple(
            SheetTrackRow(
                track_id=track.id,
                track_name=track.name,
                color=track.color,
                segments=tuple(
                    segment
                    for move in _moves_for_track(project, track.id)
                    if (
                        segment := _segment_move(
                            move, track.color, line_start, line_end
                        )
                    )
                    is not None
                ),
            )
            for track in sorted(project.tracks, key=lambda item: item.display_order)
        )
        lines.append(SheetLine(index, line_start, line_end, counts, rows))
        index += 1
        line_start = line_end
    return SheetModel(
        project_id=project.id,
        project_name=project.name,
        beats_per_line=beats_per_line,
        regions=regions,
        lines=tuple(lines),
    )


def _project_bounds(project: Project) -> tuple[Fraction, Fraction]:
    starts = [region.start for region in project.regions]
    starts.extend(move.start for move in project.moves)
    ends = [region.end for region in project.regions]
    ends.extend(move.end for move in project.moves)
    if not starts:
        return Fraction(0), Fraction(project.default_count_group)
    return min(starts), max(ends)


def _region_depth(
    region: MusicalRegion, regions_by_id: dict[str, MusicalRegion]
) -> int:
    depth = 0
    parent_id = region.parent_id
    while parent_id is not None:
        depth += 1
        parent_id = regions_by_id[parent_id].parent_id
    return depth


def _moves_for_track(project: Project, track_id: str) -> tuple[Move, ...]:
    return tuple(
        sorted(
            (move for move in project.moves if move.track_id == track_id),
            key=lambda item: (item.start, item.id),
        )
    )


def _top_level_gaps(
    project: Project, start: Fraction, end: Fraction
) -> tuple[GapSpan, ...]:
    top_level = sorted(
        (region for region in project.regions if region.parent_id is None),
        key=lambda item: item.start,
    )
    gaps: list[GapSpan] = []
    cursor = start
    for region in top_level:
        if cursor < region.start:
            gaps.append(GapSpan(cursor, region.start))
        cursor = max(cursor, region.end)
    if cursor < end:
        gaps.append(GapSpan(cursor, end))
    return tuple(gaps)


def _count_cell(project: Project, start: Fraction, end: Fraction) -> CountCell:
    top_regions = tuple(
        region
        for region in project.regions
        if region.parent_id is None and region.start <= start < region.end
    )
    region = top_regions[0] if top_regions else None
    group = (
        region.count_group
        if region and region.count_group
        else project.default_count_group
    )
    relative = start - project.count_origin
    label = str(int(relative % group) + 1)
    return CountCell(
        start=start,
        end=end,
        label=label,
        region_id=region.id if region else None,
        region_label=region.label if region else None,
    )


def _segment_move(
    move: Move,
    color: str,
    line_start: Fraction,
    line_end: Fraction,
) -> MoveSegment | None:
    start = max(move.start, line_start)
    end = min(move.end, line_end)
    if start >= end:
        return None
    return MoveSegment(
        move_id=move.id,
        track_id=move.track_id,
        label=move.label,
        start=start,
        end=end,
        color=color,
        continues_before=move.start < line_start,
        continues_after=move.end > line_end,
    )


def _floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def _ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)
