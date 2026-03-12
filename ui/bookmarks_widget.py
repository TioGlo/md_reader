"""Bookmarks widget with tree view for saved document positions."""

from pathlib import Path

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt


class BookmarksWidget(QTreeWidget):
    """Tree widget displaying user bookmarks across documents."""

    # Signal emitted when a bookmark is clicked (file_path, anchor)
    bookmark_clicked = pyqtSignal(str, str)

    def __init__(self) -> None:
        """Initialize the bookmarks widget."""
        super().__init__()

        # Configure tree widget
        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setIndentation(10)

        # Connect item click to signal emission
        self.itemClicked.connect(self._on_item_clicked)

    def update_bookmarks(self, bookmarks: list[dict]) -> None:
        """
        Refresh the bookmarks display.

        Args:
            bookmarks: List of bookmark dicts, each with keys:
                       "file" (str), "anchor" (str), "title" (str)
        """
        self.clear()

        for bookmark in bookmarks:
            item = QTreeWidgetItem(self)
            item.setText(0, bookmark.get("title", "Untitled"))

            # Show the file name as tooltip
            file_path = bookmark.get("file", "")
            file_name = Path(file_path).name if file_path else ""
            item.setToolTip(0, f"{file_name} - {file_path}")

            # Store file path and anchor in item data
            item.setData(0, Qt.ItemDataRole.UserRole, bookmark.get("file", ""))
            item.setData(0, Qt.ItemDataRole.UserRole + 1, bookmark.get("anchor", ""))

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handle tree item click.

        Args:
            item: Clicked tree item
            column: Column index (always 0)
        """
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        anchor = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if file_path is not None:
            self.bookmark_clicked.emit(file_path, anchor or "")
