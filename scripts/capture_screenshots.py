"""Capture review screenshots from the actual Qt application widgets."""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from koreo.fixtures import representative_project
from koreo.gui.main_window import MainWindow


def main() -> int:
    """Render both tabs and save their window captures."""

    # [GH-10] [I-06] Review evidence is captured from real Qt widgets.
    application = QApplication.instance() or QApplication([])
    output_directory = Path("docs/reviews/milestone-1")
    output_directory.mkdir(parents=True, exist_ok=True)
    window = MainWindow(representative_project())
    window.show()

    captures = ((0, "timeline.png"), (1, "sheet.png"))
    for tab_index, filename in captures:
        window.tabs.setCurrentIndex(tab_index)
        application.processEvents()
        destination = output_directory / filename
        if not window.grab().save(str(destination), "PNG"):
            raise RuntimeError(f"Could not save screenshot to {destination}")

    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
