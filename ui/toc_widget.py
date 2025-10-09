"""Table of Contents widget with hierarchical tree view."""

from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import pyqtSignal, Qt


class TOCWidget(QTreeWidget):
    """Tree widget displaying document table of contents."""

    # Signal emitted when a TOC item is clicked (emits anchor ID)
    anchor_clicked = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize the TOC widget."""
        super().__init__()

        # Configure tree widget
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setIndentation(15)

        # Connect item click to signal emission
        self.itemClicked.connect(self._on_item_clicked)

    def update_toc(self, toc_items: list) -> None:
        """
        Update the TOC display with new items.

        Args:
            toc_items: Hierarchical list of TOC items from TOCGenerator
        """
        # Clear existing items
        self.clear()

        # Build tree from TOC structure
        self._build_tree_items(toc_items, self)

        # Expand all items by default
        self.expandAll()

    def _build_tree_items(self, toc_items: list, parent) -> None:
        """
        Recursively build tree items from TOC structure.

        Args:
            toc_items: List of TOC items (potentially nested)
            parent: Parent QTreeWidget or QTreeWidgetItem
        """
        for item_data in toc_items:
            # Create tree item
            tree_item = QTreeWidgetItem(parent)
            tree_item.setText(0, item_data["text"])

            # Store anchor ID in item data for click handling
            tree_item.setData(0, Qt.ItemDataRole.UserRole, item_data["anchor"])

            # Add visual indication of header level with indentation prefix
            level_indicator = "  " * (item_data["level"] - 1)
            tree_item.setText(0, f"{level_indicator}{item_data['text']}")

            # Recursively add children
            if item_data["children"]:
                self._build_tree_items(item_data["children"], tree_item)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handle tree item click.

        Args:
            item: Clicked tree item
            column: Column index (always 0 for us)
        """
        # Get anchor ID from item data
        anchor = item.data(0, Qt.ItemDataRole.UserRole)
        if anchor:
            self.anchor_clicked.emit(anchor)
