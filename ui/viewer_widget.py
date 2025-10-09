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

    def set_zoom_level(self, zoom_percent: int) -> None:
        """
        Set the zoom level for the page.

        Args:
            zoom_percent: Zoom percentage (100 = 100%, 200 = 200%, etc.)
        """
        zoom_factor = zoom_percent / 100.0
        self.setZoomFactor(zoom_factor)

    def get_zoom_level(self) -> int:
        """
        Get the current zoom level.

        Returns:
            Current zoom percentage (100 = 100%)
        """
        return int(self.zoomFactor() * 100)

    def scroll_to_anchor(self, anchor: str) -> None:
        """
        Scroll to a specific anchor in the document.

        Args:
            anchor: Anchor ID to scroll to
        """
        # Execute JavaScript to scroll to the anchor
        scroll_script = f"""
            var element = document.getElementById('{anchor}');
            if (element) {{
                element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }}
        """
        self.page().runJavaScript(scroll_script)

    def find_text(self, text: str, case_sensitive: bool = False, backward: bool = False) -> None:
        """
        Search for text in the document.

        Args:
            text: Text to search for
            case_sensitive: Whether search should be case-sensitive
            backward: Whether to search backward (previous occurrence)
        """
        from PyQt6.QtWebEngineCore import QWebEnginePage

        # Build find flags
        flags = QWebEnginePage.FindFlag(0)
        if case_sensitive:
            flags |= QWebEnginePage.FindFlag.FindCaseSensitively
        if backward:
            flags |= QWebEnginePage.FindFlag.FindBackward

        # Perform search
        self.findText(text, flags)
