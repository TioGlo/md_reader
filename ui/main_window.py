"""Main application window."""

from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

from core.markdown_renderer import MarkdownRenderer
from core.document_manager import DocumentManager
from config.settings_manager import SettingsManager
from ui.viewer_widget import ViewerWidget
from ui.menu_bar import MenuBar


class MainWindow(QMainWindow):
    """Main application window coordinating all components."""

    def __init__(self) -> None:
        """Initialize the main window."""
        super().__init__()

        # Initialize core components
        self.renderer = MarkdownRenderer()
        self.document_manager = DocumentManager()
        self.settings = SettingsManager()

        # Set up UI
        self._init_ui()
        self._restore_window_state()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Markdown Reader")

        # Create viewer widget
        self.viewer = ViewerWidget()
        self.setCentralWidget(self.viewer)

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
        self.settings.save_settings()

        event.accept()
