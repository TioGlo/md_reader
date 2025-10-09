"""Search dialog for finding text in documents."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QLabel,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QKeySequence, QShortcut


class SearchDialog(QDialog):
    """Dialog for searching text in the markdown viewer."""

    # Signals for search operations
    find_next = pyqtSignal(str, bool)  # search_text, case_sensitive
    find_previous = pyqtSignal(str, bool)  # search_text, case_sensitive

    def __init__(self, parent=None) -> None:
        """
        Initialize the search dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.setWindowTitle("Find")
        self.setModal(False)  # Non-modal so user can interact with document

        # Initialize UI
        self._init_ui()

        # Set up keyboard shortcuts
        self._setup_shortcuts()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Search input row
        search_layout = QHBoxLayout()
        search_label = QLabel("Find:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search text...")
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Options row
        options_layout = QHBoxLayout()
        self.case_sensitive_checkbox = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Buttons row
        button_layout = QHBoxLayout()
        self.find_next_button = QPushButton("Find Next")
        self.find_previous_button = QPushButton("Find Previous")
        self.close_button = QPushButton("Close")

        self.find_next_button.setDefault(True)

        button_layout.addWidget(self.find_previous_button)
        button_layout.addWidget(self.find_next_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Connect signals
        self.find_next_button.clicked.connect(self._on_find_next)
        self.find_previous_button.clicked.connect(self._on_find_previous)
        self.close_button.clicked.connect(self.close)
        self.search_input.returnPressed.connect(self._on_find_next)

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # F3 for find next
        find_next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_F3), self)
        find_next_shortcut.activated.connect(self._on_find_next)

        # Shift+F3 for find previous
        find_prev_shortcut = QShortcut(
            QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_F3), self
        )
        find_prev_shortcut.activated.connect(self._on_find_previous)

        # Escape to close
        close_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        close_shortcut.activated.connect(self.close)

    def _on_find_next(self) -> None:
        """Handle find next button click."""
        search_text = self.search_input.text()
        if not search_text:
            self.status_label.setText("Please enter search text")
            return

        case_sensitive = self.case_sensitive_checkbox.isChecked()
        self.find_next.emit(search_text, case_sensitive)
        self.status_label.setText("")

    def _on_find_previous(self) -> None:
        """Handle find previous button click."""
        search_text = self.search_input.text()
        if not search_text:
            self.status_label.setText("Please enter search text")
            return

        case_sensitive = self.case_sensitive_checkbox.isChecked()
        self.find_previous.emit(search_text, case_sensitive)
        self.status_label.setText("")

    def show_and_focus(self) -> None:
        """Show the dialog and focus the search input."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()
        self.search_input.selectAll()

    def set_search_text(self, text: str) -> None:
        """
        Set the search input text.

        Args:
            text: Text to set in search input
        """
        self.search_input.setText(text)
        self.search_input.selectAll()
