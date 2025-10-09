"""Menu bar for the main window."""

from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction, QKeySequence
from typing import Callable


class MenuBar:
    """Manages the application menu bar."""

    def __init__(self, menu_bar: QMenuBar) -> None:
        """
        Initialize the menu bar.

        Args:
            menu_bar: QMenuBar instance from the main window
        """
        self.menu_bar = menu_bar
        self.recent_file_actions: list[QAction] = []

    def setup_menus(
        self,
        on_open: Callable[[], None],
        on_recent_file: Callable[[str], None],
        on_exit: Callable[[], None],
    ) -> None:
        """
        Set up all menus and connect their actions.

        Args:
            on_open: Callback for File > Open
            on_recent_file: Callback for recent file selection (receives file path)
            on_exit: Callback for File > Exit
        """
        # File menu
        file_menu = self.menu_bar.addMenu("&File")

        # Open action
        open_action = QAction("&Open...", self.menu_bar)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open a markdown file")
        open_action.triggered.connect(on_open)
        file_menu.addAction(open_action)

        # Recent files submenu
        file_menu.addSeparator()
        self.recent_files_menu = file_menu.addMenu("Recent Files")

        # We'll populate recent files dynamically
        self._update_recent_files_menu([], on_recent_file)

        # Exit action
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self.menu_bar)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(on_exit)
        file_menu.addAction(exit_action)

    def update_recent_files(
        self, recent_files: list[str], on_recent_file: Callable[[str], None]
    ) -> None:
        """
        Update the recent files menu.

        Args:
            recent_files: List of recent file paths
            on_recent_file: Callback for recent file selection
        """
        self._update_recent_files_menu(recent_files, on_recent_file)

    def _update_recent_files_menu(
        self, recent_files: list[str], on_recent_file: Callable[[str], None]
    ) -> None:
        """
        Rebuild the recent files menu.

        Args:
            recent_files: List of recent file paths
            on_recent_file: Callback for recent file selection
        """
        # Clear existing actions
        self.recent_files_menu.clear()
        self.recent_file_actions.clear()

        if not recent_files:
            # Show "No recent files" if list is empty
            no_files_action = QAction("No recent files", self.menu_bar)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)
        else:
            # Add actions for each recent file
            for i, file_path in enumerate(recent_files):
                # Show just the filename, keep full path in data
                from pathlib import Path

                display_name = Path(file_path).name

                # Add keyboard shortcut for first 9 files
                if i < 9:
                    action = QAction(f"&{i+1}. {display_name}", self.menu_bar)
                    action.setShortcut(f"Alt+{i+1}")
                else:
                    action = QAction(display_name, self.menu_bar)

                # Store full path in action data
                action.setData(file_path)
                action.setStatusTip(file_path)

                # Connect to callback with the file path
                action.triggered.connect(lambda checked, path=file_path: on_recent_file(path))

                self.recent_files_menu.addAction(action)
                self.recent_file_actions.append(action)
