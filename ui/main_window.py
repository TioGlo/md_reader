"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QInputDialog, QMessageBox,
    QSplitter, QWidget, QVBoxLayout, QPushButton,
)
from PyQt6.QtCore import Qt, QEventLoop
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog

from core.markdown_renderer import MarkdownRenderer
from core.document_manager import DocumentManager
from config.settings_manager import SettingsManager
from config.theme_manager import ThemeManager
from ui.viewer_widget import ViewerWidget
from ui.menu_bar import MenuBar
from ui.export_manager import ExportManager
from ui.toc_widget import TOCWidget
from ui.search_dialog import SearchDialog
from ui.status_bar import StatusBarManager
from ui.bookmarks_widget import BookmarksWidget
from ui.presentation_mode import PresentationWindow


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
        self.export_manager = ExportManager()

        # Display state
        self.current_theme = self.settings.get("ui.theme", "light")
        self.font_size = self.settings.get("ui.font_size", 14)
        self.zoom_level = self.settings.get("ui.zoom_level", 100)
        self.toc_visible = self.settings.get("ui.toc_visible", True)
        self.toc_width = self.settings.get("ui.toc_width", 250)

        # Bookmarks state
        self.bookmarks_visible = self.settings.get("ui.bookmarks_visible", False)

        # Split view state
        self.split_view_active = False
        self.secondary_doc_manager = DocumentManager()

        # Search dialog
        self.search_dialog: SearchDialog | None = None

        # Presentation window
        self._presentation_window: PresentationWindow | None = None

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
        self.viewer.file_dropped.connect(self._load_file)

        # Create secondary viewer panel (for split view)
        self.secondary_panel = QWidget()
        secondary_layout = QVBoxLayout(self.secondary_panel)
        secondary_layout.setContentsMargins(0, 0, 0, 0)
        secondary_layout.setSpacing(0)

        self.secondary_open_btn = QPushButton("Open File...")
        self.secondary_open_btn.clicked.connect(self._on_open_file_secondary)
        secondary_layout.addWidget(self.secondary_open_btn)

        self.secondary_viewer = ViewerWidget()
        self.secondary_viewer.file_dropped.connect(self._load_file_secondary)
        secondary_layout.addWidget(self.secondary_viewer)

        # Inner splitter holds primary and secondary viewers
        self.viewer_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.viewer_splitter.addWidget(self.viewer)
        self.viewer_splitter.addWidget(self.secondary_panel)
        self.secondary_panel.setVisible(False)

        # Create bookmarks widget
        self.bookmarks_widget = BookmarksWidget()
        self.bookmarks_widget.setMinimumWidth(150)
        self.bookmarks_widget.setMaximumWidth(400)
        self.bookmarks_widget.bookmark_clicked.connect(self._on_bookmark_clicked)

        # Add widgets to outer splitter
        self.splitter.addWidget(self.toc_widget)
        self.splitter.addWidget(self.viewer_splitter)
        self.splitter.addWidget(self.bookmarks_widget)

        # Set splitter sizes
        bookmarks_width = 250 if self.bookmarks_visible else 0
        self.splitter.setSizes([self.toc_width, 1000 - self.toc_width - bookmarks_width, bookmarks_width])

        # Set TOC visibility
        self.toc_widget.setVisible(self.toc_visible)

        # Set bookmarks panel visibility
        self.bookmarks_widget.setVisible(self.bookmarks_visible)

        # Set splitter as central widget
        self.setCentralWidget(self.splitter)

        # Set up status bar
        self.status_bar_manager = StatusBarManager(self.statusBar())

        # Set up menu bar
        self.menu_bar_manager = MenuBar(self.menuBar())
        self.menu_bar_manager.setup_menus(
            on_open=self._on_open_file,
            on_recent_file=self._on_open_recent_file,
            on_exit=self.close,
        )

        # Set up export actions in File menu
        self.menu_bar_manager.setup_export_menu(
            on_export_html=self._on_export_html,
            on_export_pdf=self._on_export_pdf,
        )

        # Set up print actions in File menu
        self.menu_bar_manager.setup_print_menu(
            on_print=self._on_print,
            on_print_preview=self._on_print_preview,
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

        # Add split view toggle to View menu
        self.menu_bar_manager.add_split_view_toggle(
            view_menu=view_menu,
            on_toggle=self._on_split_view_toggle,
            is_active=self.split_view_active,
        )

        # Add fullscreen toggle to View menu
        view_menu.addSeparator()
        self.fullscreen_action = QAction("&Fullscreen", self)
        self.fullscreen_action.setShortcut(QKeySequence("F11"))
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self._on_toggle_fullscreen)
        view_menu.addAction(self.fullscreen_action)

        # Escape shortcut to exit fullscreen
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.escape_shortcut.activated.connect(self._on_escape)

        # Set up Bookmarks menu
        self.menu_bar_manager.setup_bookmarks_menu(
            on_add_bookmark=self._on_add_bookmark,
            on_toggle_bookmarks_panel=self._on_toggle_bookmarks_panel,
            on_clear_bookmarks=self._on_clear_bookmarks,
            panel_visible=self.bookmarks_visible,
        )

        # Set up Presentation Mode in View menu
        self.menu_bar_manager.setup_presentation_menu(
            on_present=self._on_presentation_mode,
        )

        # Load existing bookmarks into the panel
        self._refresh_bookmarks_display()

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
        <p><strong>File &rarr; Open</strong> or press <span class="shortcut">Ctrl+O</span></p>
        <p>You can also drag and drop a file onto this window.</p>
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

    def _on_export_html(self) -> None:
        """Handle File > Export as HTML action."""
        if not self.document_manager.current_content:
            QMessageBox.warning(
                self,
                "No Document",
                "Please open a markdown file before exporting.",
            )
            return

        default_name = ""
        current_path = self.document_manager.get_current_file_path()
        if current_path:
            from pathlib import Path
            default_name = str(Path(current_path).with_suffix(".html"))

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export as HTML",
            default_name,
            "HTML Files (*.html);;All Files (*)",
        )

        if not file_path:
            return

        try:
            html_content = self.renderer.render(self.document_manager.current_content)
            self.export_manager.export_html(html_content, file_path)
            QMessageBox.information(
                self,
                "Export Successful",
                f"HTML file saved to:\n{file_path}",
            )
        except OSError as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Could not save HTML file:\n{file_path}\n\nError: {e}",
            )

    def _on_export_pdf(self) -> None:
        """Handle File > Export as PDF action."""
        if not self.document_manager.current_content:
            QMessageBox.warning(
                self,
                "No Document",
                "Please open a markdown file before exporting.",
            )
            return

        default_name = ""
        current_path = self.document_manager.get_current_file_path()
        if current_path:
            from pathlib import Path
            default_name = str(Path(current_path).with_suffix(".pdf"))

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export as PDF",
            default_name,
            "PDF Files (*.pdf);;All Files (*)",
        )

        if not file_path:
            return

        def _on_pdf_finished(success: bool) -> None:
            if success:
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"PDF file saved to:\n{file_path}",
                )
            else:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Could not save PDF file:\n{file_path}",
                )

        self.export_manager.export_pdf(self.viewer, file_path, callback=_on_pdf_finished)

    def _on_print(self) -> None:
        """Handle File > Print action."""
        if not self.document_manager.current_content:
            QMessageBox.warning(
                self,
                "No Document",
                "Please open a markdown file before printing.",
            )
            return

        from PyQt6.QtPrintSupport import QPrintDialog

        printer = QPrinter(QPrinter.Mode.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            loop = QEventLoop()
            self.viewer.page().print(printer, lambda _success: loop.quit())
            loop.exec()

    def _on_print_preview(self) -> None:
        """Handle File > Print Preview action."""
        if not self.document_manager.current_content:
            QMessageBox.warning(
                self,
                "No Document",
                "Please open a markdown file before printing.",
            )
            return

        printer = QPrinter(QPrinter.Mode.HighResolution)
        dialog = QPrintPreviewDialog(printer, self)
        dialog.setWindowTitle("Print Preview")

        def handle_paint_requested(req_printer: QPrinter) -> None:
            """Render the web page to the printer synchronously using an event loop."""
            loop = QEventLoop()
            self.viewer.page().print(req_printer, lambda _success: loop.quit())
            loop.exec()

        dialog.paintRequested.connect(handle_paint_requested)
        dialog.exec()

    def _save_scroll_position(self) -> None:
        """Save scroll position for the current file."""
        file_path = self.document_manager.get_current_file_path()
        if file_path:
            self.viewer.page().runJavaScript(
                "window.scrollY",
                lambda pos: self._store_scroll_position(file_path, pos)
            )

    def _store_scroll_position(self, file_path: str, position: float | int | None) -> None:
        """Store scroll position in settings."""
        if position is not None:
            scroll_positions = self.settings.get("scroll_positions", {})
            scroll_positions[file_path] = int(position)
            self.settings.set("scroll_positions", scroll_positions)
            self.settings.save_settings()

    def _restore_scroll_position(self, file_path: str) -> None:
        """Restore scroll position for a file after content loads."""
        scroll_positions = self.settings.get("scroll_positions", {})
        position = scroll_positions.get(file_path, 0)
        if position > 0:
            self.viewer.page().loadFinished.connect(
                lambda ok, pos=position: self._do_scroll_restore(pos)
            )

    def _do_scroll_restore(self, position: int) -> None:
        """Execute the scroll restore after page load."""
        self.viewer.page().runJavaScript(f"window.scrollTo(0, {position})")
        # Disconnect to avoid restoring on every future load
        try:
            self.viewer.page().loadFinished.disconnect(self._do_scroll_restore)
        except TypeError:
            pass

    def _load_file(self, file_path: str) -> None:
        """
        Load and display a markdown file.

        Args:
            file_path: Path to the file to load
        """
        try:
            # Save scroll position of current file before loading new one
            self._save_scroll_position()

            # Read the file
            content = self.document_manager.open_file(file_path)

            # Render markdown to HTML
            html = self.renderer.render(content)

            # Display in viewer
            self.viewer.load_html_content(html)

            # Restore scroll position for this file
            self._restore_scroll_position(file_path)

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

            # Update status bar
            self.status_bar_manager.update_stats(content, file_path)

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
        self.renderer.set_theme_name(self.current_theme)
        self.renderer.set_font_size(self.font_size)

        # Apply theme to Qt widgets (TOC, status bar, menu bar)
        self._apply_widget_theme()

        # Set zoom level
        self.viewer.set_zoom_level(self.zoom_level)
        self.secondary_viewer.set_zoom_level(self.zoom_level)

        # Re-render current document if one is loaded
        if self.document_manager.current_content:
            html = self.renderer.render(self.document_manager.current_content)
            self.viewer.load_html_content(html)

        # Re-render secondary document if one is loaded
        if self.secondary_doc_manager.current_content:
            html = self.renderer.render(self.secondary_doc_manager.current_content)
            self.secondary_viewer.load_html_content(html)

    def _apply_widget_theme(self) -> None:
        """Apply the current theme to all Qt widgets."""
        if self.current_theme == "dark":
            widget_style = """
                QMainWindow { background-color: #0d1117; }
                QMenuBar { background-color: #161b22; color: #c9d1d9; }
                QMenuBar::item:selected { background-color: #30363d; }
                QMenu { background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; }
                QMenu::item:selected { background-color: #30363d; }
                QMenu::separator { background-color: #30363d; height: 1px; }
                QTreeWidget {
                    background-color: #0d1117;
                    color: #c9d1d9;
                    border: none;
                    font-size: 13px;
                }
                QTreeWidget::item:hover { background-color: #161b22; }
                QTreeWidget::item:selected { background-color: #1f6feb; color: #f0f6fc; }
                QSplitter::handle { background-color: #30363d; }
                QStatusBar { background-color: #161b22; color: #8b949e; }
                QStatusBar QLabel { color: #8b949e; }
                QPushButton { background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 4px 12px; }
                QPushButton:hover { background-color: #30363d; }
            """
        elif self.current_theme == "sepia":
            widget_style = """
                QMainWindow { background-color: #f4ecd8; }
                QMenuBar { background-color: #efe6d0; color: #5b4636; }
                QMenuBar::item:selected { background-color: #d4c5a9; }
                QMenu { background-color: #f4ecd8; color: #5b4636; border: 1px solid #d4c5a9; }
                QMenu::item:selected { background-color: #8b4513; color: #f4ecd8; }
                QMenu::separator { background-color: #d4c5a9; height: 1px; }
                QTreeWidget {
                    background-color: #f4ecd8;
                    color: #5b4636;
                    border: none;
                    font-size: 13px;
                }
                QTreeWidget::item:hover { background-color: #efe6d0; }
                QTreeWidget::item:selected { background-color: #8b4513; color: #f4ecd8; }
                QSplitter::handle { background-color: #d4c5a9; }
                QStatusBar { background-color: #efe6d0; color: #7a6652; }
                QStatusBar QLabel { color: #7a6652; }
                QPushButton { background-color: #efe6d0; color: #5b4636; border: 1px solid #d4c5a9; padding: 4px 12px; }
                QPushButton:hover { background-color: #d4c5a9; }
            """
        elif self.current_theme == "high_contrast":
            widget_style = """
                QMainWindow { background-color: #000000; }
                QMenuBar { background-color: #1a1a1a; color: #ffffff; }
                QMenuBar::item:selected { background-color: #333333; }
                QMenu { background-color: #1a1a1a; color: #ffffff; border: 1px solid #666666; }
                QMenu::item:selected { background-color: #ffff00; color: #000000; }
                QMenu::separator { background-color: #666666; height: 1px; }
                QTreeWidget {
                    background-color: #000000;
                    color: #ffffff;
                    border: none;
                    font-size: 13px;
                }
                QTreeWidget::item:hover { background-color: #1a1a1a; }
                QTreeWidget::item:selected { background-color: #ffff00; color: #000000; }
                QSplitter::handle { background-color: #666666; }
                QStatusBar { background-color: #1a1a1a; color: #e0e0e0; }
                QStatusBar QLabel { color: #e0e0e0; }
                QPushButton { background-color: #1a1a1a; color: #ffffff; border: 1px solid #666666; padding: 4px 12px; }
                QPushButton:hover { background-color: #333333; }
            """
        else:
            widget_style = """
                QMainWindow { background-color: #ffffff; }
                QMenuBar { background-color: #f6f8fa; color: #24292e; }
                QMenuBar::item:selected { background-color: #e1e4e8; }
                QMenu { background-color: #ffffff; color: #24292e; border: 1px solid #e1e4e8; }
                QMenu::item:selected { background-color: #0366d6; color: #ffffff; }
                QMenu::separator { background-color: #e1e4e8; height: 1px; }
                QTreeWidget {
                    background-color: #ffffff;
                    color: #24292e;
                    border: none;
                    font-size: 13px;
                }
                QTreeWidget::item:hover { background-color: #f6f8fa; }
                QTreeWidget::item:selected { background-color: #0366d6; color: #ffffff; }
                QSplitter::handle { background-color: #e1e4e8; }
                QStatusBar { background-color: #f6f8fa; color: #586069; }
                QStatusBar QLabel { color: #586069; }
                QPushButton { background-color: #f6f8fa; color: #24292e; border: 1px solid #e1e4e8; padding: 4px 12px; }
                QPushButton:hover { background-color: #e1e4e8; }
            """
        self.setStyleSheet(widget_style)

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

    def _on_toggle_fullscreen(self, checked: bool) -> None:
        """Toggle fullscreen reading mode."""
        if checked:
            self.menuBar().hide()
            self.statusBar().hide()
            self.toc_widget.hide()
            self.showFullScreen()
        else:
            self.menuBar().show()
            self.statusBar().show()
            if self.toc_visible:
                self.toc_widget.show()
            self.showNormal()

    def _on_escape(self) -> None:
        """Handle Escape key — exit fullscreen if active."""
        if self.isFullScreen():
            self.fullscreen_action.setChecked(False)
            self._on_toggle_fullscreen(False)

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

    # ------------------------------------------------------------------
    # Bookmarks
    # ------------------------------------------------------------------

    def _refresh_bookmarks_display(self) -> None:
        """Reload bookmarks from settings into the bookmarks widget."""
        bookmarks = self.settings.get("bookmarks", [])
        self.bookmarks_widget.update_bookmarks(bookmarks)

    def _on_add_bookmark(self) -> None:
        """Handle Bookmarks > Add Bookmark action."""
        file_path = self.document_manager.get_current_file_path()
        if not file_path:
            QMessageBox.warning(
                self,
                "No Document",
                "Please open a markdown file before adding a bookmark.",
            )
            return

        # JavaScript to find the nearest heading above the current scroll position
        js_code = """
        (function() {
            var scrollY = window.scrollY;
            var headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            var nearest = null;
            for (var i = 0; i < headings.length; i++) {
                var rect = headings[i].getBoundingClientRect();
                var absTop = rect.top + window.scrollY;
                if (absTop <= scrollY + 50) {
                    nearest = headings[i];
                } else {
                    break;
                }
            }
            return {
                anchor: nearest ? (nearest.id || '') : '',
                heading: nearest ? nearest.textContent : '',
                scrollY: scrollY
            };
        })()
        """
        self.viewer.page().runJavaScript(
            js_code,
            lambda result: self._finish_add_bookmark(file_path, result),
        )

    def _finish_add_bookmark(self, file_path: str, js_result: dict | None) -> None:
        """
        Complete the add-bookmark flow after JavaScript returns position info.

        Args:
            file_path: Path of the currently open file
            js_result: Dict with 'anchor', 'heading', 'scrollY' from JS
        """
        default_title = ""
        anchor = ""
        scroll_y = 0

        if js_result and isinstance(js_result, dict):
            default_title = js_result.get("heading", "")
            anchor = js_result.get("anchor", "")
            scroll_y = js_result.get("scrollY", 0)

        if not default_title:
            from pathlib import Path
            default_title = Path(file_path).stem

        title, ok = QInputDialog.getText(
            self,
            "Add Bookmark",
            "Bookmark title:",
            text=default_title,
        )

        if not ok or not title.strip():
            return

        # If there is no heading anchor, store a scroll-position-based anchor
        if not anchor:
            anchor = f"__scroll_{int(scroll_y)}"

        bookmark = {
            "file": file_path,
            "anchor": anchor,
            "title": title.strip(),
        }

        bookmarks = self.settings.get("bookmarks", [])
        bookmarks.append(bookmark)
        self.settings.set("bookmarks", bookmarks)
        self.settings.save_settings()

        self._refresh_bookmarks_display()

    def _on_toggle_bookmarks_panel(self, visible: bool) -> None:
        """
        Show or hide the bookmarks panel.

        Args:
            visible: Whether to show the panel
        """
        self.bookmarks_visible = visible
        self.bookmarks_widget.setVisible(visible)
        self.settings.set("ui.bookmarks_visible", visible)
        self.settings.save_settings()

    def _on_bookmark_clicked(self, file_path: str, anchor: str) -> None:
        """
        Handle a bookmark being clicked.

        Args:
            file_path: Path to the bookmarked file
            anchor: Anchor ID or scroll-position marker to navigate to
        """
        current_file = self.document_manager.get_current_file_path()

        if file_path != current_file:
            self._load_file(file_path)
            # After load finishes, scroll to the anchor
            self.viewer.page().loadFinished.connect(
                lambda ok, a=anchor: self._scroll_to_bookmark_anchor(a)
            )
        else:
            self._scroll_to_bookmark_anchor(anchor)

    def _scroll_to_bookmark_anchor(self, anchor: str) -> None:
        """
        Scroll to a bookmark anchor, handling both heading IDs and scroll offsets.

        Args:
            anchor: Either a heading element ID or '__scroll_<pixels>'
        """
        # Disconnect any one-shot loadFinished connection
        try:
            self.viewer.page().loadFinished.disconnect(self._scroll_to_bookmark_anchor)
        except TypeError:
            pass

        if anchor.startswith("__scroll_"):
            try:
                offset = int(anchor.replace("__scroll_", ""))
            except ValueError:
                offset = 0
            self.viewer.page().runJavaScript(f"window.scrollTo(0, {offset})")
        else:
            self.viewer.scroll_to_anchor(anchor)

    def _on_clear_bookmarks(self) -> None:
        """Handle Bookmarks > Clear All Bookmarks action."""
        bookmarks = self.settings.get("bookmarks", [])
        if not bookmarks:
            QMessageBox.information(self, "Bookmarks", "There are no bookmarks to clear.")
            return

        reply = QMessageBox.question(
            self,
            "Clear Bookmarks",
            f"Remove all {len(bookmarks)} bookmark(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings.set("bookmarks", [])
            self.settings.save_settings()
            self._refresh_bookmarks_display()

    # ------------------------------------------------------------------
    # Split View
    # ------------------------------------------------------------------

    def _on_split_view_toggle(self, is_visible: bool) -> None:
        """Toggle the split view secondary panel."""
        self.split_view_active = is_visible
        self.secondary_panel.setVisible(is_visible)
        if is_visible:
            self.viewer_splitter.setSizes([500, 500])

    def _on_open_file_secondary(self) -> None:
        """Open a file dialog for the secondary split view panel."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown File (Split View)",
            "",
            "Markdown Files (*.md *.markdown *.txt);;All Files (*)",
        )
        if file_path:
            self._load_file_secondary(file_path)

    def _load_file_secondary(self, file_path: str) -> None:
        """Load a markdown file into the secondary viewer."""
        try:
            content = self.secondary_doc_manager.open_file(file_path)
            html = self.renderer.render(content)
            self.secondary_viewer.load_html_content(html)

            from pathlib import Path
            self.secondary_open_btn.setText(Path(file_path).name)
        except (FileNotFoundError, IOError) as e:
            QMessageBox.critical(
                self, "Error", f"Could not open file:\n{e}"
            )

    def _on_presentation_mode(self) -> None:
        """Launch presentation mode for the current document."""
        if not self.document_manager.current_content:
            QMessageBox.warning(
                self,
                "No Document",
                "Please open a markdown file before starting a presentation.",
            )
            return

        html = self.renderer.render(self.document_manager.current_content)
        self._presentation_window = PresentationWindow(html, parent=self)
        self._presentation_window.showFullScreen()

    def closeEvent(self, event) -> None:
        """
        Handle window close event to save state.

        Args:
            event: Close event
        """
        # Save scroll position of current file
        file_path = self.document_manager.get_current_file_path()
        if file_path:
            self.viewer.page().runJavaScript(
                "window.scrollY",
                lambda pos: self._store_scroll_position(file_path, pos)
            )

        # Save window geometry
        if not self.isMaximized() and not self.isFullScreen():
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
