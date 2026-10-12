"""Core immutable entities for beat-based choreography planning.

Beat coordinates are zero-based, song-relative, exact ``Fraction`` values.
Intervals use half-open semantics: ``[start, end)``. A negative start is valid
and represents pickup material before the display count origin.
"""

from dataclasses import dataclass
from fractions import Fraction

from koreo.domain.calibration import BeatCalibration

# [GH-4] [S-M1-01] [S-M1-02] Exact immutable domain entities.


@dataclass(frozen=True, slots=True)
class MusicalRegion:
    """A named interval in an arbitrarily deep musical hierarchy."""

    id: str
    label: str
    start: Fraction
    duration: Fraction
    parent_id: str | None = None
    count_group: int | None = None
    count_restart: bool = True
    color: str | None = None

    @property
    def end(self) -> Fraction:
        """Return the exclusive end beat."""

        return self.start + self.duration


@dataclass(frozen=True, slots=True)
class ChoreographyTrack:
    """An independently timed row of choreography moves."""

    id: str
    name: str
    display_order: int
    color: str


@dataclass(frozen=True, slots=True)
class Move:
    """A labeled choreography interval assigned to one track."""

    id: str
    track_id: str
    start: Fraction
    duration: Fraction
    label: str
    notes: str | None = None

    @property
    def end(self) -> Fraction:
        """Return the exclusive end beat."""

        return self.start + self.duration


@dataclass(frozen=True, slots=True)
class Project:
    """The complete in-memory source of truth for the prototype."""

    id: str
    name: str
    tracks: tuple[ChoreographyTrack, ...]
    regions: tuple[MusicalRegion, ...]
    moves: tuple[Move, ...]
    default_count_group: int = 8
    count_origin: Fraction = Fraction(0)
    calibration: BeatCalibration | None = None
