"""Application entry point for the Koreo prototype."""

import sys

from PySide6.QtWidgets import QApplication

from koreo.fixtures import starter_project
from koreo.gui.main_window import MainWindow


def main() -> int:
    """Run the Koreo editor prototype."""

    application = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow(starter_project())
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
