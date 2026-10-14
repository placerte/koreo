"""Deterministic in-code projects shared by the app and tests."""

from dataclasses import replace
from fractions import Fraction

from koreo.domain.models import ChoreographyTrack, Move, MusicalRegion, Project
from koreo.domain.validation import validate_project


def representative_project() -> Project:
    """Return the Milestone 1 representative project fixture."""

    # [GH-6] [S-M1-07] One source project feeds both views and their tests.
    project = Project(
        id="project-swing-demo",
        name="Swing Demo",
        default_count_group=8,
        count_origin=Fraction(0),
        tracks=(ChoreographyTrack("choreography", "Choreography", 0, "#3b82f6"),),
        regions=(
            MusicalRegion("intro", "Intro", Fraction(0), Fraction(6), count_group=6),
            MusicalRegion("a-1", "A", Fraction(6), Fraction(16)),
            MusicalRegion("a-1-phrase-1", "Phrase 1", Fraction(6), Fraction(8), "a-1"),
            MusicalRegion("a-1-phrase-2", "Phrase 2", Fraction(14), Fraction(8), "a-1"),
            MusicalRegion("b", "B", Fraction(24), Fraction(12), count_group=6),
            MusicalRegion("a-2", "A", Fraction(36), Fraction(16)),
        ),
        moves=(
            Move(
                "lead-rock",
                "choreography",
                Fraction(0),
                Fraction(4),
                "Rock step",
            ),
            Move(
                "lead-triple",
                "choreography",
                Fraction(11, 2),
                Fraction(9, 2),
                "Triple-step variation",
                "Stay grounded through the final half beat.",
            ),
            Move(
                "lead-cross-section",
                "choreography",
                Fraction(20),
                Fraction(6),
                "Send out",
            ),
            Move(
                "lead-cross-wrap",
                "choreography",
                Fraction(30),
                Fraction(5),
                "Cross-line turn",
            ),
            Move(
                "follow-finish",
                "choreography",
                Fraction(38),
                Fraction(10),
                "Final partnered phrase",
            ),
        ),
    )
    validate_project(project)
    return project


def starter_project() -> Project:
    """Return the prototype's unprogrammed startup project."""

    return replace(representative_project(), moves=())
