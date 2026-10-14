"""Tests for shared application project history."""

from dataclasses import replace

import pytest

from koreo.application.session import ProjectCommand, ProjectSession
from koreo.fixtures import representative_project


def test_session_executes_undoes_redoes_and_tracks_saved_revision() -> None:
    original = representative_project()
    changed = replace(original, name="Routine")
    session = ProjectSession(original)

    assert session.execute(ProjectCommand("Rename", original, changed))
    assert session.project.name == "Routine"
    assert session.dirty
    assert session.undo()
    assert session.project is original
    assert not session.dirty
    assert session.redo()
    session.mark_clean()
    assert not session.dirty


def test_session_rejects_command_for_another_revision() -> None:
    project = representative_project()
    session = ProjectSession(project)
    other = replace(project, name="Other")

    with pytest.raises(ValueError, match="does not apply"):
        session.execute(ProjectCommand("Wrong base", other, project))

    assert session.project is project
    assert not session.can_undo


def test_load_resets_history_and_external_dirty_state() -> None:
    project = representative_project()
    session = ProjectSession(project)
    session.replace(replace(project, name="Draft"), "Rename")
    session.mark_external_change()

    session.load(project)

    assert not session.dirty
    assert not session.can_undo
    assert not session.can_redo
