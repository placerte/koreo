"""Read-only view data derived from the domain model."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class RegionSpan:
    id: str
    label: str
    start: Fraction
    end: Fraction
    depth: int


@dataclass(frozen=True, slots=True)
class GapSpan:
    start: Fraction
    end: Fraction


@dataclass(frozen=True, slots=True)
class MoveSpan:
    id: str
    track_id: str
    label: str
    start: Fraction
    end: Fraction
    color: str


@dataclass(frozen=True, slots=True)
class TrackRow:
    id: str
    name: str
    color: str
    moves: tuple[MoveSpan, ...]


@dataclass(frozen=True, slots=True)
class TimelineModel:
    project_id: str
    project_name: str
    start: Fraction
    end: Fraction
    count_origin: Fraction
    count_group: int
    regions: tuple[RegionSpan, ...]
    gaps: tuple[GapSpan, ...]
    tracks: tuple[TrackRow, ...]
    counts: tuple["CountCell", ...]


@dataclass(frozen=True, slots=True)
class CountCell:
    start: Fraction
    end: Fraction
    label: str
    region_id: str | None
    region_label: str | None
    continuous_label: str
    group_size: int
    restarted: bool


@dataclass(frozen=True, slots=True)
class MoveSegment:
    move_id: str
    track_id: str
    label: str
    start: Fraction
    end: Fraction
    color: str
    continues_before: bool
    continues_after: bool


@dataclass(frozen=True, slots=True)
class SheetTrackRow:
    track_id: str
    track_name: str
    color: str
    segments: tuple[MoveSegment, ...]


@dataclass(frozen=True, slots=True)
class SheetLine:
    index: int
    start: Fraction
    end: Fraction
    counts: tuple[CountCell, ...]
    tracks: tuple[SheetTrackRow, ...]


@dataclass(frozen=True, slots=True)
class SheetModel:
    project_id: str
    project_name: str
    beats_per_line: int
    regions: tuple[RegionSpan, ...]
    lines: tuple[SheetLine, ...]
