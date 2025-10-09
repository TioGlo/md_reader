"""Main application window."""

from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QSplitter, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from core.markdown_renderer import MarkdownRenderer
from core.document_manager import DocumentManager
from config.settings_manager import SettingsManager
from config.theme_manager import ThemeManager
from ui.viewer_widget import ViewerWidget
from ui.menu_bar import MenuBar
from ui.toc_widget import TOCWidget
from ui.search_dialog import SearchDialog


class MainWindow(QMainWindow):
    """Main application window coordinating all components."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        # Initialize core components
        self.renderer = MarkdownRenderer()
        self.document_manager = DocumentManager()
        self.settings = SettingsManager()
        self.theme_manager = ThemeManager()

        # Display state
        self.current_theme = self.settings.get("ui.theme", "light")
        self.font_size = self.settings.get("ui.font_size", 14)
        self.zoom_level = self.settings.get("ui.zoom_level", 100)
        self.toc_visible = self.settings.get("ui.toc_visible", True)
        self.toc_width = self.settings.get("ui.toc_width", 250)

        # Search dialog
        self.search_dialog: SearchDialog | None = None

        # Set up UI
        self._init_ui()
        self._restore_window_state()
        self._apply_display_settings()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Markdown Reader")

        # Create main splitter with TOC and viewer
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Create TOC widget
        self.toc_widget = TOCWidget()
        self.toc_widget.setMinimumWidth(150)
        self.toc_widget.setMaximumWidth(400)
        self.toc_widget.anchor_clicked.connect(self._on_toc_item_clicked)

        # Create viewer widget
        self.viewer = ViewerWidget()

        # Add widgets to splitter
        self.splitter.addWidget(self.toc_widget)
        self.splitter.addWidget(self.viewer)

        # Set splitter sizes
        self.splitter.setSizes([self.toc_width, 1000 - self.toc_width])

        # Set TOC visibility
        self.toc_widget.setVisible(self.toc_visible)

        # Set splitter as central widget
        self.setCentralWidget(self.splitter)

        # Set up menu bar
        self.menu_bar_manager = MenuBar(self.menuBar())
        self.menu_bar_manager.setup_menus(
            on_open=self._on_open_file,
            on_recent_file=self._on_open_recent_file,
            on_exit=self.close,
        )

        # Update recent files menu
        recent_files = self.settings.get_recent_files()
        self.menu_bar_manager.update_recent_files(recent_files, self._on_open_recent_file)

        # Set up Edit menu
        self.menu_bar_manager.setup_edit_menu(on_find=self._on_find)

        # Set up View menu
        view_menu = self.menu_bar_manager.setup_view_menu(
            on_increase_font=self._on_increase_font,
            on_decrease_font=self._on_decrease_font,
            on_reset_font=self._on_reset_font,
            on_zoom_in=self._on_zoom_in,
            on_zoom_out=self._on_zoom_out,
            on_reset_zoom=self._on_reset_zoom,
            on_theme_change=self._on_theme_change,
            available_themes=self.theme_manager.get_available_themes(),
            current_theme=self.current_theme,
        )

        # Add TOC toggle to View menu
        self.menu_bar_manager.add_toc_toggle(
            view_menu=view_menu, on_toggle=self._on_toc_toggle, is_visible=self.toc_visible
        )

        # Show welcome message
        self._show_welcome_message()

    def _show_welcome_message(self) -> None:
        """Display a welcome message in the viewer."""
        welcome_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        .welcome {
            text-align: center;
            padding: 40px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        p {
            color: #666;
            font-size: 16px;
            line-height: 1.6;
        }
        .shortcut {
            background-color: #f0f0f0;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="welcome">
        <h1>Welcome to Markdown Reader</h1>
        <p>To get started, open a markdown file:</p>
        <p><strong>File → Open</strong> or press <span class="shortcut">Ctrl+O</span></p>
    </div>
</body>
</html>
"""
        self.viewer.load_html_content(welcome_html)

    def _on_open_file(self) -> None:
        """Handle File > Open action."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File",
            "",
            "Markdown Files (*.md *.markdown *.txt);;All Files (*)",
        )

        if file_path:
            self._load_file(file_path)

    def _on_open_recent_file(self, file_path: str) -> None:
        """
        Handle opening a recent file.

        Args:
            file_path: Path to the file to open
        """
        self._load_file(file_path)

    def _load_file(self, file_path: str) -> None:
        """
        Load and display a markdown file.

        Args:
            file_path: Path to the file to load
        """
        try:
            # Read the file
            content = self.document_manager.open_file(file_path)

            # Render markdown to HTML
            html = self.renderer.render(content)

            # Display in viewer
            self.viewer.load_html_content(html)

            # Update window title
            file_name = self.document_manager.get_current_file_name()
            self.setWindowTitle(f"{file_name} - Markdown Reader")

            # Add to recent files
            self.settings.add_recent_file(file_path)

            # Update recent files menu
            recent_files = self.settings.get_recent_files()
            self.menu_bar_manager.update_recent_files(recent_files, self._on_open_recent_file)

            # Update TOC
            toc_items = self.renderer.get_toc()
            self.toc_widget.update_toc(toc_items)

        except FileNotFoundError:
            QMessageBox.warning(
                self, "File Not Found", f"The file could not be found:\n{file_path}"
            )
            # Remove from recent files if it doesn't exist
            recent_files = self.settings.get_recent_files()
            if file_path in recent_files:
                recent_files.remove(file_path)
                self.settings.settings["recent_files"] = recent_files
                self.settings.save_settings()
                self.menu_bar_manager.update_recent_files(recent_files, self._on_open_recent_file)

        except IOError as e:
            QMessageBox.critical(
                self, "Error Opening File", f"Could not open the file:\n{file_path}\n\nError: {e}"
            )

    def _restore_window_state(self) -> None:
        """Restore window size and position from settings."""
        width = self.settings.get("window.width", 1000)
        height = self.settings.get("window.height", 700)
        x = self.settings.get("window.x", 100)
        y = self.settings.get("window.y", 100)

        self.resize(width, height)
        self.move(x, y)

        if self.settings.get("window.maximized", False):
            self.showMaximized()

    def _apply_display_settings(self) -> None:
        """Apply theme, font size, and zoom settings."""
        # Load and set theme
        theme_css = self.theme_manager.get_theme_css(self.current_theme)
        self.renderer.set_theme_css(theme_css)
        self.renderer.set_font_size(self.font_size)

        # Set zoom level
        self.viewer.set_zoom_level(self.zoom_level)

        # Re-render current document if one is loaded
        if self.document_manager.current_content:
            html = self.renderer.render(self.document_manager.current_content)
            self.viewer.load_html_content(html)

    def _on_increase_font(self) -> None:
        """Increase font size."""
        self.font_size = min(self.font_size + 2, 32)
        self.settings.set("ui.font_size", self.font_size)
        self.settings.save_settings()
        self._apply_display_settings()

    def _on_decrease_font(self) -> None:
        """Decrease font size."""
        self.font_size = max(self.font_size - 2, 8)
        self.settings.set("ui.font_size", self.font_size)
        self.settings.save_settings()
        self._apply_display_settings()

    def _on_reset_font(self) -> None:
        """Reset font size to default."""
        self.font_size = 14
        self.settings.set("ui.font_size", self.font_size)
        self.settings.save_settings()
        self._apply_display_settings()

    def _on_zoom_in(self) -> None:
        """Zoom in."""
        self.zoom_level = min(self.zoom_level + 10, 400)
        self.settings.set("ui.zoom_level", self.zoom_level)
        self.settings.save_settings()
        self.viewer.set_zoom_level(self.zoom_level)

    def _on_zoom_out(self) -> None:
        """Zoom out."""
        self.zoom_level = max(self.zoom_level - 10, 25)
        self.settings.set("ui.zoom_level", self.zoom_level)
        self.settings.save_settings()
        self.viewer.set_zoom_level(self.zoom_level)

    def _on_reset_zoom(self) -> None:
        """Reset zoom to 100%."""
        self.zoom_level = 100
        self.settings.set("ui.zoom_level", self.zoom_level)
        self.settings.save_settings()
        self.viewer.set_zoom_level(self.zoom_level)

    def _on_theme_change(self, theme_name: str) -> None:
        """
        Handle theme change.

        Args:
            theme_name: Name of the new theme
        """
        self.current_theme = theme_name
        self.settings.set("ui.theme", theme_name)
        self.settings.save_settings()
        self.theme_manager.set_current_theme(theme_name)
        self.menu_bar_manager.update_theme_selection(theme_name)
        self._apply_display_settings()

    def _on_toc_item_clicked(self, anchor: str) -> None:
        """
        Handle TOC item click.

        Args:
            anchor: Anchor ID to scroll to
        """
        self.viewer.scroll_to_anchor(anchor)

    def _on_toc_toggle(self, is_visible: bool) -> None:
        """
        Handle TOC visibility toggle.

        Args:
            is_visible: New visibility state
        """
        self.toc_visible = is_visible
        self.toc_widget.setVisible(is_visible)
        self.settings.set("ui.toc_visible", is_visible)
        self.settings.save_settings()

    def _on_find(self) -> None:
        """Handle Find action (Ctrl+F)."""
        # Create search dialog if it doesn't exist
        if self.search_dialog is None:
            self.search_dialog = SearchDialog(self)
            self.search_dialog.find_next.connect(self._on_search_next)
            self.search_dialog.find_previous.connect(self._on_search_previous)

        # Show and focus the dialog
        self.search_dialog.show_and_focus()

    def _on_search_next(self, search_text: str, case_sensitive: bool) -> None:
        """
        Handle find next search.

        Args:
            search_text: Text to search for
            case_sensitive: Whether search is case-sensitive
        """
        self.viewer.find_text(search_text, case_sensitive, backward=False)

    def _on_search_previous(self, search_text: str, case_sensitive: bool) -> None:
        """
        Handle find previous search.

        Args:
            search_text: Text to search for
            case_sensitive: Whether search is case-sensitive
        """
        self.viewer.find_text(search_text, case_sensitive, backward=True)

    def closeEvent(self, event) -> None:
        """
        Handle window close event to save state.

        Args:
            event: Close event
        """
        # Save window geometry
        if not self.isMaximized():
            self.settings.set("window.width", self.width())
            self.settings.set("window.height", self.height())
            self.settings.set("window.x", self.x())
            self.settings.set("window.y", self.y())

        self.settings.set("window.maximized", self.isMaximized())

        # Save TOC width if visible
        if self.toc_visible:
            sizes = self.splitter.sizes()
            if sizes[0] > 0:
                self.settings.set("ui.toc_width", sizes[0])

        self.settings.save_settings()

        event.accept()
