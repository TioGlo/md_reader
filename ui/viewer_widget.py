"""Markdown viewer widget using QWebEngineView."""

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSignal, QTimer
from PyQt6.QtGui import QDesktopServices


class _ViewerPage(QWebEnginePage):
    """Custom page that intercepts file:// navigations from drag & drop."""

    file_dropped = pyqtSignal(str)

    def acceptNavigationRequest(self, url: QUrl, nav_type: QWebEnginePage.NavigationType, is_main_frame: bool) -> bool:
        """Intercept navigation requests to catch dropped files and external links."""
        if url.isLocalFile():
            file_path = url.toLocalFile()
            if file_path.lower().endswith((".md", ".markdown", ".txt")):
                # Defer the signal to avoid re-entrant page loading
                QTimer.singleShot(0, lambda p=file_path: self.file_dropped.emit(p))
                return False
        # Block external navigations — open in system browser instead
        if url.scheme() in ("http", "https"):
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)


class ViewerWidget(QWebEngineView):
    """HTML viewer for rendered markdown content."""

    file_dropped = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize the viewer widget."""
        super().__init__()

        # Set up custom page that intercepts dropped file navigations
        page = _ViewerPage(self)
        page.linkHovered.connect(self._on_link_hovered)
        page.file_dropped.connect(self.file_dropped)
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
