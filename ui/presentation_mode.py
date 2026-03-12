"""Presentation mode for displaying markdown as a slideshow."""

import os
import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QMainWindow

os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu")


class PresentationWindow(QMainWindow):
    """Fullscreen presentation window that displays markdown content as slides."""

    def __init__(self, html: str, parent: QMainWindow | None = None) -> None:
        """
        Initialize the presentation window.

        Args:
            html: Rendered HTML content from the markdown renderer
            parent: Parent window reference
        """
        super().__init__(parent)
        self.setWindowTitle("Presentation Mode")

        self.slides: list[str] = self._split_into_slides(html)
        self.current_index: int = 0

        # Create the web view for slide display
        self.web_view = QWebEngineView()
        self.web_view.page().settings().setAttribute(
            self.web_view.page().settings().WebAttribute.LocalContentCanAccessRemoteUrls,
            True,
        )
        self.setCentralWidget(self.web_view)

        # Set up keyboard navigation
        self._setup_shortcuts()

        # Show the first slide
        if self.slides:
            self._show_slide(0)

    def _setup_shortcuts(self) -> None:
        """Configure keyboard shortcuts for slide navigation."""
        # Next slide: Right arrow, Space, Down arrow, Page Down
        for key in (Qt.Key.Key_Right, Qt.Key.Key_Space, Qt.Key.Key_Down, Qt.Key.Key_PageDown):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(self._next_slide)

        # Previous slide: Left arrow, Backspace, Up arrow, Page Up
        for key in (Qt.Key.Key_Left, Qt.Key.Key_Backspace, Qt.Key.Key_Up, Qt.Key.Key_PageUp):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(self._previous_slide)

        # Exit: Escape
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self.close)

    def _split_into_slides(self, html: str) -> list[str]:
        """
        Split rendered HTML into individual slides at H1/H2 boundaries.

        Extracts the body content from the full HTML document and splits it
        wherever an ``<h1`` or ``<h2`` tag appears. Each resulting fragment
        becomes one slide.

        Args:
            html: Full HTML document string produced by MarkdownRenderer

        Returns:
            List of HTML fragment strings, one per slide
        """
        # Extract body content between <body> and </body>
        body_match = re.search(r"<body>(.*?)</body>", html, re.DOTALL)
        if not body_match:
            return [html]

        body_content = body_match.group(1).strip()
        if not body_content:
            return ["<p>No content</p>"]

        # Split at H1 or H2 tags (case-insensitive)
        # The pattern keeps the delimiter (the heading tag) with the following content
        parts = re.split(r"(?=<h[12][\s>])", body_content, flags=re.IGNORECASE)

        # Filter out empty strings
        slides = [part.strip() for part in parts if part.strip()]

        if not slides:
            return ["<p>No content</p>"]

        return slides

    def _show_slide(self, index: int) -> None:
        """
        Render and display a specific slide by index.

        Wraps the slide HTML fragment in a complete HTML document with
        presentation-specific CSS styling and a slide counter overlay.

        Args:
            index: Zero-based slide index to display
        """
        if not self.slides or index < 0 or index >= len(self.slides):
            return

        self.current_index = index
        slide_content = self.slides[index]
        total = len(self.slides)
        display_num = index + 1

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        html, body {{
            width: 100%;
            height: 100%;
            background-color: #1a1a1a;
            color: #f0f0f0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                         'Helvetica Neue', Arial, sans-serif;
            font-size: 28px;
            line-height: 1.5;
        }}
        .slide-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 60px 80px;
        }}
        .slide-content {{
            max-width: 1200px;
            width: 100%;
            text-align: left;
        }}
        h1 {{
            font-size: 2.4em;
            margin-bottom: 0.6em;
            color: #ffffff;
            border-bottom: 2px solid #444;
            padding-bottom: 0.3em;
        }}
        h2 {{
            font-size: 1.8em;
            margin-bottom: 0.5em;
            color: #e0e0e0;
            border-bottom: 1px solid #444;
            padding-bottom: 0.3em;
        }}
        h3 {{
            font-size: 1.4em;
            margin-bottom: 0.4em;
            color: #d0d0d0;
        }}
        p {{
            margin-bottom: 0.8em;
        }}
        ul, ol {{
            padding-left: 1.5em;
            margin-bottom: 0.8em;
        }}
        li {{
            margin-bottom: 0.4em;
        }}
        code {{
            background-color: #2d2d2d;
            padding: 0.15em 0.4em;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.85em;
        }}
        pre {{
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 0.8em;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #555;
            padding-left: 20px;
            color: #bbb;
            margin-bottom: 0.8em;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 0.8em;
        }}
        table th, table td {{
            border: 1px solid #555;
            padding: 10px 14px;
            text-align: left;
        }}
        table th {{
            background-color: #2d2d2d;
            font-weight: 600;
        }}
        a {{
            color: #6db3f2;
            text-decoration: none;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        hr {{
            border: 0;
            border-top: 1px solid #444;
            margin: 1em 0;
        }}
        .slide-counter {{
            position: fixed;
            bottom: 20px;
            right: 30px;
            font-size: 16px;
            color: #666;
            font-variant-numeric: tabular-nums;
        }}
    </style>
</head>
<body>
    <div class="slide-container">
        <div class="slide-content">
            {slide_content}
        </div>
    </div>
    <div class="slide-counter">{display_num} / {total}</div>
</body>
</html>"""
        self.web_view.setHtml(full_html)

    def _next_slide(self) -> None:
        """Navigate to the next slide if not at the end."""
        if self.current_index < len(self.slides) - 1:
            self._show_slide(self.current_index + 1)

    def _previous_slide(self) -> None:
        """Navigate to the previous slide if not at the beginning."""
        if self.current_index > 0:
            self._show_slide(self.current_index - 1)
