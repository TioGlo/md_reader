"""Markdown Reader - A simple GUI markdown viewer."""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main() -> None:
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Reader")
    app.setOrganizationName("md_reader")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
