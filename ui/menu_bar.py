"""Menu bar for the main window."""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence, QActionGroup
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
        self.theme_actions: dict[str, QAction] = {}
        self.toc_toggle_action: QAction | None = None
        self.file_menu: QMenu | None = None

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
        self.file_menu = file_menu

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

    def setup_export_menu(
        self,
        on_export_html: Callable[[], None],
        on_export_pdf: Callable[[], None],
    ) -> None:
        """
        Add export actions to the File menu after the Open action.

        Args:
            on_export_html: Callback for Export as HTML
            on_export_pdf: Callback for Export as PDF
        """
        if self.file_menu is None:
            return

        # Get the list of existing actions to insert before the first separator
        actions = self.file_menu.actions()

        # Find the first separator (after Open action)
        insert_before = None
        for action in actions:
            if action.isSeparator():
                insert_before = action
                break

        export_html_action = QAction("Export as &HTML...", self.menu_bar)
        export_html_action.setShortcut("Ctrl+Shift+H")
        export_html_action.setStatusTip("Export the document as a standalone HTML file")
        export_html_action.triggered.connect(on_export_html)

        export_pdf_action = QAction("Export as &PDF...", self.menu_bar)
        export_pdf_action.setShortcut("Ctrl+Shift+P")
        export_pdf_action.setStatusTip("Export the document as a PDF file")
        export_pdf_action.triggered.connect(on_export_pdf)

        if insert_before is not None:
            self.file_menu.insertAction(insert_before, export_html_action)
            self.file_menu.insertAction(insert_before, export_pdf_action)
        else:
            self.file_menu.addAction(export_html_action)
            self.file_menu.addAction(export_pdf_action)

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

    def setup_view_menu(
        self,
        on_increase_font: Callable[[], None],
        on_decrease_font: Callable[[], None],
        on_reset_font: Callable[[], None],
        on_zoom_in: Callable[[], None],
        on_zoom_out: Callable[[], None],
        on_reset_zoom: Callable[[], None],
        on_theme_change: Callable[[str], None],
        available_themes: list[str],
        current_theme: str,
    ) -> QMenu:
        """
        Set up the View menu with display controls.

        Args:
            on_increase_font: Callback for increasing font size
            on_decrease_font: Callback for decreasing font size
            on_reset_font: Callback for resetting font size
            on_zoom_in: Callback for zooming in
            on_zoom_out: Callback for zooming out
            on_reset_zoom: Callback for resetting zoom
            on_theme_change: Callback for theme changes (receives theme name)
            available_themes: List of available theme names
            current_theme: Currently active theme name

        Returns:
            The created View menu
        """
        view_menu = self.menu_bar.addMenu("&View")

        # Font Size submenu
        font_menu = view_menu.addMenu("Font Size")

        increase_font_action = QAction("Increase", self.menu_bar)
        increase_font_action.setShortcut("Ctrl++")
        increase_font_action.triggered.connect(on_increase_font)
        font_menu.addAction(increase_font_action)

        decrease_font_action = QAction("Decrease", self.menu_bar)
        decrease_font_action.setShortcut("Ctrl+-")
        decrease_font_action.triggered.connect(on_decrease_font)
        font_menu.addAction(decrease_font_action)

        font_menu.addSeparator()

        reset_font_action = QAction("Reset", self.menu_bar)
        reset_font_action.setShortcut("Ctrl+0")
        reset_font_action.triggered.connect(on_reset_font)
        font_menu.addAction(reset_font_action)

        # Zoom submenu
        zoom_menu = view_menu.addMenu("Zoom")

        zoom_in_action = QAction("Zoom In", self.menu_bar)
        zoom_in_action.setShortcut("Ctrl+=")
        zoom_in_action.triggered.connect(on_zoom_in)
        zoom_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self.menu_bar)
        zoom_out_action.setShortcut("Ctrl+_")
        zoom_out_action.triggered.connect(on_zoom_out)
        zoom_menu.addAction(zoom_out_action)

        zoom_menu.addSeparator()

        reset_zoom_action = QAction("Reset Zoom", self.menu_bar)
        reset_zoom_action.setShortcut("Ctrl+)")
        reset_zoom_action.triggered.connect(on_reset_zoom)
        zoom_menu.addAction(reset_zoom_action)

        # Theme submenu
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("Theme")

        # Create action group for themes (only one can be checked at a time)
        theme_group = QActionGroup(self.menu_bar)
        theme_group.setExclusive(True)

        for theme_name in available_themes:
            action = QAction(theme_name.capitalize(), self.menu_bar)
            action.setCheckable(True)
            action.setChecked(theme_name == current_theme)
            action.triggered.connect(lambda checked, t=theme_name: on_theme_change(t))

            theme_group.addAction(action)
            theme_menu.addAction(action)
            self.theme_actions[theme_name] = action

        return view_menu

    def update_theme_selection(self, theme_name: str) -> None:
        """
        Update which theme is checked in the menu.

        Args:
            theme_name: Name of the theme to mark as selected
        """
        for name, action in self.theme_actions.items():
            action.setChecked(name == theme_name)

    def setup_edit_menu(self, on_find: Callable[[], None]) -> None:
        """
        Set up the Edit menu with search functionality.

        Args:
            on_find: Callback for Find action
        """
        edit_menu = self.menu_bar.addMenu("&Edit")

        # Find action
        find_action = QAction("&Find...", self.menu_bar)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.setStatusTip("Search for text in the document")
        find_action.triggered.connect(on_find)
        edit_menu.addAction(find_action)

    def add_toc_toggle(
        self, view_menu: QMenu, on_toggle: Callable[[bool], None], is_visible: bool
    ) -> None:
        """
        Add TOC visibility toggle to View menu.

        Args:
            view_menu: The View menu to add the toggle to
            on_toggle: Callback for TOC toggle (receives visibility state)
            is_visible: Initial TOC visibility state
        """
        # Add separator before TOC toggle
        view_menu.addSeparator()

        # Create TOC toggle action
        self.toc_toggle_action = QAction("Show &Table of Contents", self.menu_bar)
        self.toc_toggle_action.setCheckable(True)
        self.toc_toggle_action.setChecked(is_visible)
        self.toc_toggle_action.setShortcut("Ctrl+T")
        self.toc_toggle_action.setStatusTip("Toggle table of contents sidebar")
        self.toc_toggle_action.triggered.connect(on_toggle)

        view_menu.addAction(self.toc_toggle_action)

    def update_toc_toggle(self, is_visible: bool) -> None:
        """
        Update the TOC toggle state.

        Args:
            is_visible: Whether TOC is visible
        """
        if self.toc_toggle_action:
            self.toc_toggle_action.setChecked(is_visible)
