"""Markdown Reader - A simple GUI markdown viewer."""

import os
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main() -> None:
    """Application entry point."""
    # Work around Vulkan compositing issues on some Linux GPU drivers
    os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")

    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Reader")
    app.setOrganizationName("md_reader")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
