"""Table of Contents generator for markdown documents."""

import re
from typing import TypedDict


class TOCItem(TypedDict):
    """Represents a single item in the table of contents."""

    level: int  # Header level (1-6)
    text: str  # Header text
    anchor: str  # URL-safe anchor ID
    children: list["TOCItem"]  # Nested headers


class TOCGenerator:
    """Generates a hierarchical table of contents from markdown text."""

    def __init__(self) -> None:
        """Initialize the TOC generator."""
        # Regex to match markdown headers (both ATX and Setext style)
        self.atx_pattern = re.compile(r"^(#{1,6})\s+(.+?)(?:\s*#+\s*)?$", re.MULTILINE)
        self.setext_h1_pattern = re.compile(r"^(.+)\n=+\s*$", re.MULTILINE)
        self.setext_h2_pattern = re.compile(r"^(.+)\n-+\s*$", re.MULTILINE)

    def generate_toc(self, markdown_text: str) -> list[TOCItem]:
        """
        Generate table of contents from markdown text.

        Args:
            markdown_text: Raw markdown content

        Returns:
            Hierarchical list of TOC items
        """
        # Extract all headers
        headers = self._extract_headers(markdown_text)

        # Build hierarchical structure
        return self._build_hierarchy(headers)

    def _extract_headers(self, markdown_text: str) -> list[tuple[int, str]]:
        """
        Extract all headers from markdown text.

        Args:
            markdown_text: Raw markdown content

        Returns:
            List of (level, text) tuples in document order
        """
        headers: list[tuple[int, str, int]] = []  # (level, text, position)

        # Find ATX-style headers (# Header)
        for match in self.atx_pattern.finditer(markdown_text):
            level = len(match.group(1))
            text = match.group(2).strip()
            headers.append((level, text, match.start()))

        # Find Setext-style H1 headers (underlined with =)
        for match in self.setext_h1_pattern.finditer(markdown_text):
            text = match.group(1).strip()
            headers.append((1, text, match.start()))

        # Find Setext-style H2 headers (underlined with -)
        for match in self.setext_h2_pattern.finditer(markdown_text):
            text = match.group(1).strip()
            headers.append((2, text, match.start()))

        # Sort by position in document to maintain order
        headers.sort(key=lambda x: x[2])

        # Return just level and text
        return [(level, text) for level, text, _ in headers]

    def _build_hierarchy(self, headers: list[tuple[int, str]]) -> list[TOCItem]:
        """
        Build hierarchical TOC structure from flat header list.

        Args:
            headers: List of (level, text) tuples

        Returns:
            Hierarchical list of TOC items
        """
        if not headers:
            return []

        # Track anchor IDs to ensure uniqueness
        anchor_counts: dict[str, int] = {}

        def create_toc_item(level: int, text: str) -> TOCItem:
            """Create a TOC item with a unique anchor."""
            anchor = self._generate_anchor(text)

            # Ensure unique anchors by adding suffix if needed
            if anchor in anchor_counts:
                anchor_counts[anchor] += 1
                anchor = f"{anchor}-{anchor_counts[anchor]}"
            else:
                anchor_counts[anchor] = 0

            return TOCItem(level=level, text=text, anchor=anchor, children=[])

        # Build hierarchy using a stack-based approach
        root_items: list[TOCItem] = []
        stack: list[TOCItem] = []

        for level, text in headers:
            item = create_toc_item(level, text)

            # Find parent in stack
            while stack and stack[-1]["level"] >= level:
                stack.pop()

            if stack:
                # Add as child of current parent
                stack[-1]["children"].append(item)
            else:
                # Add as root item
                root_items.append(item)

            # Add to stack for potential children
            stack.append(item)

        return root_items

    def _generate_anchor(self, text: str) -> str:
        """
        Generate a URL-safe anchor ID from header text.

        Args:
            text: Header text

        Returns:
            URL-safe anchor string (lowercase, hyphenated)
        """
        # Convert to lowercase
        anchor = text.lower()

        # Remove special characters and replace spaces with hyphens
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        anchor = re.sub(r"[\s_]+", "-", anchor)

        # Remove leading/trailing hyphens
        anchor = anchor.strip("-")

        return anchor or "header"

    def inject_anchors(self, markdown_text: str) -> str:
        """
        Inject anchor IDs into markdown headers for linking.

        Args:
            markdown_text: Raw markdown content

        Returns:
            Markdown with anchor IDs injected
        """
        headers = self._extract_headers(markdown_text)
        anchor_counts: dict[str, int] = {}

        def replace_header(match: re.Match) -> str:
            """Replace header with anchored version."""
            level = len(match.group(1))
            text = match.group(2).strip()

            # Generate anchor
            anchor = self._generate_anchor(text)
            if anchor in anchor_counts:
                anchor_counts[anchor] += 1
                anchor = f"{anchor}-{anchor_counts[anchor]}"
            else:
                anchor_counts[anchor] = 0

            # Return header with anchor
            hashes = "#" * level
            return f'{hashes} <a id="{anchor}"></a>{text}'

        # Replace ATX-style headers
        result = self.atx_pattern.sub(replace_header, markdown_text)

        return result
