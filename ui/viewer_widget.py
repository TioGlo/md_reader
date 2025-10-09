"""Markdown viewer widget using QWebEngineView."""

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices


class ViewerWidget(QWebEngineView):
    """HTML viewer for rendered markdown content."""

    def __init__(self) -> None:
        """Initialize the viewer widget."""
        super().__init__()

        # Set up custom page to handle link clicks
        page = QWebEnginePage(self)
        page.linkHovered.connect(self._on_link_hovered)
        self.setPage(page)

        # Enable dev tools for debugging (can be removed in production)
        self.page().settings().setAttribute(
            self.page().settings().WebAttribute.LocalContentCanAccessRemoteUrls, True
        )

    def load_html_content(self, html: str) -> None:
        """
        Load HTML content into the viewer.

        Args:
            html: HTML string to display
        """
        self.setHtml(html)

    def _on_link_hovered(self, url: str) -> None:
        """
        Handle link hover events.

        Args:
            url: URL that was hovered
        """
        # Could show URL in status bar (Phase 4 feature)
        pass

    def createWindow(self, window_type: QWebEnginePage.WebWindowType) -> QWebEngineView:
        """
        Handle external links by opening them in default browser.

        Args:
            window_type: Type of window to create

        Returns:
            Self (prevents new window from opening)
        """
        # This is called when a link is clicked
        # We'll handle external links in acceptNavigationRequest instead
        return self
