"""Document file management and I/O operations."""

from pathlib import Path
from typing import Optional


class DocumentManager:
    """Handles file operations for markdown documents."""

    def __init__(self) -> None:
        """Initialize the document manager."""
        self.current_file: Optional[Path] = None
        self.current_content: str = ""

    def open_file(self, file_path: str) -> str:
        """
        Open and read a markdown file.

        Args:
            file_path: Path to the markdown file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise IOError(f"Path is not a file: {file_path}")

        # Try different encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as f:
                    content = f.read()

                self.current_file = path
                self.current_content = content
                return content

            except UnicodeDecodeError:
                continue

        # If all encodings fail
        raise IOError(f"Could not decode file: {file_path}")

    def get_current_file_path(self) -> Optional[str]:
        """
        Get the absolute path of the currently opened file.

        Returns:
            Absolute file path as string, or None if no file is opened
        """
        return str(self.current_file.absolute()) if self.current_file else None

    def get_current_file_name(self) -> Optional[str]:
        """
        Get the name of the currently opened file.

        Returns:
            File name, or None if no file is opened
        """
        return self.current_file.name if self.current_file else None
