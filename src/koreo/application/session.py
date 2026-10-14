"""Shared project command history and document dirty state."""

from dataclasses import dataclass

from koreo.domain.models import Project
from koreo.domain.validation import validate_project


@dataclass(frozen=True, slots=True)
class ProjectCommand:
    """One reversible, already-planned project transition."""

    label: str
    before: Project
    after: Project

    def apply(self, current: Project) -> Project:
        """Apply only to the state for which this command was created."""

        if current != self.before:
            raise ValueError("Command does not apply to the current project")
        return self.after

    def revert(self, current: Project) -> Project:
        """Reverse only its own applied state."""

        if current != self.after:
            raise ValueError("Command cannot reverse the current project")
        return self.before


class ProjectSession:
    """Own one project, shared history, and its saved revision."""

    def __init__(self, project: Project) -> None:
        validate_project(project)
        self.project = project
        self._clean_project = project
        self._undo: list[ProjectCommand] = []
        self._redo: list[ProjectCommand] = []
        self._external_dirty = False

    @property
    def dirty(self) -> bool:
        return self.project != self._clean_project or self._external_dirty

    @property
    def can_undo(self) -> bool:
        return bool(self._undo)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo)

    def execute(self, command: ProjectCommand) -> bool:
        candidate = command.apply(self.project)
        validate_project(candidate)
        if candidate == self.project:
            return False
        self.project = candidate
        self._undo.append(command)
        self._redo.clear()
        return True

    def replace(self, project: Project, label: str) -> bool:
        return self.execute(ProjectCommand(label, self.project, project))

    def undo(self) -> bool:
        if not self._undo:
            return False
        command = self._undo.pop()
        self.project = command.revert(self.project)
        self._redo.append(command)
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        command = self._redo.pop()
        self.project = command.apply(self.project)
        self._undo.append(command)
        return True

    def load(self, project: Project) -> None:
        validate_project(project)
        self.project = project
        self._clean_project = project
        self._undo.clear()
        self._redo.clear()
        self._external_dirty = False

    def mark_external_change(self) -> None:
        self._external_dirty = True

    def mark_clean(self) -> None:
        self._clean_project = self.project
        self._external_dirty = False
