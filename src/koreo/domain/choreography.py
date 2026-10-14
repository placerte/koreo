"""Pure choreography editing and same-track conflict resolution."""

from dataclasses import replace
from fractions import Fraction
from uuid import uuid4

from koreo.domain.models import Move, Project
from koreo.domain.validation import validate_project

# GitHub issues #27 and #28: direct move editing with atomic overlap resolution.


class ChoreographyEditError(ValueError):
    """Raised when a requested move edit cannot produce a valid project."""


def create_move(
    project: Project,
    track_id: str,
    start: Fraction,
    duration: Fraction,
    *,
    label: str = "New move",
    move_id: str | None = None,
) -> Project:
    move = Move(move_id or f"move-{uuid4().hex}", track_id, start, duration, label)
    return _replace_move(project, move, None)


def update_move(
    project: Project,
    move_id: str,
    *,
    start: Fraction | None = None,
    duration: Fraction | None = None,
    label: str | None = None,
    notes: str | None = None,
) -> Project:
    move = _move(project, move_id)
    updated = replace(
        move,
        start=move.start if start is None else start,
        duration=move.duration if duration is None else duration,
        label=move.label if label is None else label,
        notes=move.notes if notes is None else notes,
    )
    return _replace_move(project, updated, move_id)


def delete_move(project: Project, move_id: str) -> Project:
    _move(project, move_id)
    result = replace(project, moves=tuple(m for m in project.moves if m.id != move_id))
    validate_project(result)
    return result


def trim_edited_move(
    project: Project,
    move_id: str | None,
    track_id: str,
    start: Fraction,
    duration: Fraction,
    release_beat: Fraction,
    *,
    label: str = "New move",
) -> Project:
    """Fit the edited move into the free interval containing release_beat."""

    end = start + duration
    others = sorted(
        (
            move
            for move in project.moves
            if move.track_id == track_id and move.id != move_id
        ),
        key=lambda move: move.start,
    )
    free_start, free_end = start, end
    for other in others:
        if other.end <= release_beat:
            free_start = max(free_start, other.end)
        elif other.start >= release_beat:
            free_end = min(free_end, other.start)
            break
        elif other.start <= release_beat < other.end:
            raise ChoreographyEditError("No free interval contains the drop position")
    if free_end <= free_start:
        raise ChoreographyEditError("Trimming would remove the edited move")
    if move_id is None:
        return create_move(
            project, track_id, free_start, free_end - free_start, label=label
        )
    return update_move(
        project, move_id, start=free_start, duration=free_end - free_start
    )


def ripple_later_moves(
    project: Project,
    edited: Move,
    *,
    original_id: str | None,
) -> Project:
    """Insert edited and move colliding/later moves forward without changing gaps."""

    others = sorted(
        (
            move
            for move in project.moves
            if move.track_id == edited.track_id and move.id != original_id
        ),
        key=lambda move: move.start,
    )
    shifted: list[Move] = []
    following = [move for move in others if move.end > edited.start]
    delta = (
        max(Fraction(0), edited.end - following[0].start) if following else Fraction(0)
    )
    for move in others:
        shifted.append(
            move
            if move.end <= edited.start
            else replace(move, start=move.start + delta)
        )
    unaffected = tuple(
        move for move in project.moves if move.track_id != edited.track_id
    )
    result = replace(project, moves=unaffected + tuple(shifted) + (edited,))
    validate_project(result)
    return result


def _replace_move(project: Project, move: Move, old_id: str | None) -> Project:
    if move.duration <= 0:
        raise ChoreographyEditError("Move duration must be positive")
    if not any(track.id == move.track_id for track in project.tracks):
        raise ChoreographyEditError(f"Unknown choreography track: {move.track_id}")
    moves = tuple(item for item in project.moves if item.id != old_id) + (move,)
    result = replace(project, moves=moves)
    try:
        validate_project(result)
    except ValueError as error:
        raise ChoreographyEditError(str(error)) from error
    return result


def _move(project: Project, move_id: str) -> Move:
    try:
        return next(move for move in project.moves if move.id == move_id)
    except StopIteration as error:
        raise ChoreographyEditError(f"Unknown move: {move_id}") from error
