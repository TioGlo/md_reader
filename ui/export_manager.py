"""Export functionality for HTML and PDF output."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from PyQt6.QtWebEngineWidgets import QWebEngineView


class ExportManager:
    """Manages exporting rendered markdown to HTML and PDF formats."""

    def export_html(self, html_content: str, file_path: str) -> None:
        """
        Save rendered HTML as a standalone file.

        Args:
            html_content: Full HTML string to write
            file_path: Destination file path

        Raises:
            OSError: If the file cannot be written
        """
        path = Path(file_path)
        path.write_text(html_content, encoding="utf-8")

    def export_pdf(
        self,
        viewer: QWebEngineView,
        file_path: str,
        callback: Callable[[bool], None] | None = None,
    ) -> None:
        """
        Export the current web view content as a PDF file.

        Uses QWebEnginePage.printToPdf which renders the page to PDF.
        The pdfPrintingFinished signal is emitted when the operation completes.

        Args:
            viewer: The QWebEngineView displaying the content
            file_path: Destination PDF file path
            callback: Optional callback receiving True on success, False on failure
        """
        page = viewer.page()

        if callback is not None:
            def _on_finished(result_path: str, success: bool) -> None:
                page.pdfPrintingFinished.disconnect(_on_finished)
                callback(success)

            page.pdfPrintingFinished.connect(_on_finished)

        page.printToPdf(file_path)
