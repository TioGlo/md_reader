"""Status bar widget showing document statistics."""

from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import Qt


class StatusBarManager:
    """Manages the status bar with document statistics."""

    def __init__(self, status_bar: QStatusBar) -> None:
        """
        Initialize the status bar manager.

        Args:
            status_bar: QStatusBar instance from the main window
        """
        self.status_bar = status_bar

        # Create labels for each statistic
        self.file_label = QLabel()
        self.word_count_label = QLabel()
        self.char_count_label = QLabel()
        self.reading_time_label = QLabel()

        # Style the labels
        separator_style = "padding: 0 8px; color: #888;"
        for label in (self.file_label, self.word_count_label,
                      self.char_count_label, self.reading_time_label):
            label.setStyleSheet("padding: 0 6px;")

        # Add permanent widgets (right-aligned)
        self.status_bar.addPermanentWidget(self.reading_time_label)
        self.status_bar.addPermanentWidget(self._separator())
        self.status_bar.addPermanentWidget(self.char_count_label)
        self.status_bar.addPermanentWidget(self._separator())
        self.status_bar.addPermanentWidget(self.word_count_label)

        # File path on the left
        self.status_bar.addWidget(self.file_label)

        self.clear()

    def _separator(self) -> QLabel:
        """Create a separator label."""
        sep = QLabel("|")
        sep.setStyleSheet("padding: 0 2px; color: #aaa;")
        return sep

    def update_stats(self, content: str, file_path: str | None = None) -> None:
        """
        Update status bar with document statistics.

        Args:
            content: Raw markdown content
            file_path: Path to the current file
        """
        if file_path:
            self.file_label.setText(file_path)

        words = len(content.split()) if content.strip() else 0
        chars = len(content)
        reading_minutes = max(1, round(words / 200))

        self.word_count_label.setText(f"{words:,} words")
        self.char_count_label.setText(f"{chars:,} chars")

        if reading_minutes == 1:
            self.reading_time_label.setText("~1 min read")
        else:
            self.reading_time_label.setText(f"~{reading_minutes} min read")

    def clear(self) -> None:
        """Clear all status bar statistics."""
        self.file_label.setText("")
        self.word_count_label.setText("")
        self.char_count_label.setText("")
        self.reading_time_label.setText("")
