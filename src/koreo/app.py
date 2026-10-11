"""Application entry point for the Koreo prototype."""

import sys

from PySide6.QtWidgets import QApplication, QDialog

from koreo.fixtures import representative_project
from koreo.gui.main_window import MainWindow
from koreo.gui.setup_dialog import SetupDialog


def main() -> int:
    """Run guided audio setup followed by the editor prototype."""

    application = QApplication.instance() or QApplication(sys.argv)
    setup = SetupDialog(representative_project())
    if setup.exec() != QDialog.DialogCode.Accepted or setup.result_project is None:
        return 0
    window = MainWindow(setup.result_project)
    window.audio_source = setup.audio_source
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
