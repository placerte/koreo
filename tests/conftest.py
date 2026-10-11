"""Shared test factories."""

import os
from fractions import Fraction

from koreo.domain.models import ChoreographyTrack, Move, MusicalRegion, Project

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def make_project(
    *,
    regions: tuple[MusicalRegion, ...] = (),
    moves: tuple[Move, ...] = (),
    tracks: tuple[ChoreographyTrack, ...] | None = None,
) -> Project:
    """Return a small project suitable for validation tests."""

    if tracks is None:
        tracks = (ChoreographyTrack("track-1", "Lead", 0, "#3366cc"),)
    return Project(
        id="project-test",
        name="Test project",
        tracks=tracks,
        regions=regions,
        moves=moves,
        default_count_group=8,
        count_origin=Fraction(0),
    )
