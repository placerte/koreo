"""Capture review screenshots from the actual Qt application widgets."""

from pathlib import Path

from PySide6.QtWidgets import QApplication

from koreo.fixtures import representative_project
from koreo.gui.main_window import MainWindow


def main() -> int:
    """Render the current Structure workspace and save its window capture."""

    # [GH-10] [I-06] Review evidence is captured from real Qt widgets.
    application = QApplication.instance() or QApplication([])
    output_directory = Path("docs/reviews/milestone-3")
    output_directory.mkdir(parents=True, exist_ok=True)
    window = MainWindow(representative_project())
    window.show()

    application.processEvents()
    destination = output_directory / "structure-current.png"
    if not window.grab().save(str(destination), "PNG"):
        raise RuntimeError(f"Could not save screenshot to {destination}")

    window.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
