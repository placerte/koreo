"""Read-only application shell sharing one Project between two views."""

from PySide6.QtWidgets import QMainWindow, QTabWidget

from koreo.domain.models import Project
from koreo.gui.sheet import SheetView
from koreo.gui.timeline import TimelineView
from koreo.presentation.mapping import build_sheet, build_timeline


class MainWindow(QMainWindow):
    """Host Timeline and Sheet tabs for one immutable project instance."""

    # [GH-9] [S-M1-06] Both tabs derive from the same Project object.

    def __init__(self, project: Project) -> None:
        super().__init__()
        self.project = project
        self.audio_source: object | None = None
        self.timeline_view = TimelineView(build_timeline(project))
        self.sheet_view = SheetView(build_sheet(project))
        self.tabs = QTabWidget()
        self.tabs.setAccessibleName("Project view selector")
        self.tabs.addTab(self.timeline_view, "Timeline")
        self.tabs.addTab(self.sheet_view, "Sheet")
        self.setCentralWidget(self.tabs)
        self.setWindowTitle(f"Koreo — {project.name}")
        self.resize(1100, 700)
