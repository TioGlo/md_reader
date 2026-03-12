"""Markdown to HTML rendering engine."""

import re

import markdown2
from pygments.formatters import HtmlFormatter

from core.toc_generator import TOCGenerator


class MarkdownRenderer:
    """Converts markdown text to HTML."""

    # Regex to extract mermaid fenced code blocks from raw markdown before
    # markdown2 processes them (markdown2 strips the language class).
    _MERMAID_FENCE_RE = re.compile(
        r'```mermaid\s*\n(.*?)```',
        re.DOTALL,
    )

    def __init__(self) -> None:
        """Initialize the renderer with basic settings."""
        # Enable common markdown extensions including syntax highlighting
        self.extras = [
            "fenced-code-blocks",  # ```code``` blocks
            "tables",  # GFM tables
            "strike",  # ~~strikethrough~~
            "task_list",  # - [ ] task items
            "code-friendly",  # Disable _ and __ for em and strong
            "footnotes",  # [^1] footnote references
        ]

        # Current rendering settings
        self.theme_css = ""
        self.font_size = 14
        self.current_theme_name = "light"

        # TOC generator for header anchors
        self.toc_generator = TOCGenerator()

        # Store current TOC structure
        self.current_toc: list = []

    def set_theme_css(self, theme_css: str) -> None:
        """
        Set the theme CSS to inject into rendered HTML.

        Args:
            theme_css: CSS content for the theme
        """
        self.theme_css = theme_css

    def set_font_size(self, font_size: int) -> None:
        """
        Set the base font size.

        Args:
            font_size: Font size in pixels
        """
        self.font_size = font_size

    def set_theme_name(self, theme_name: str) -> None:
        """
        Set the current theme name for theme-aware rendering.

        This affects Mermaid diagram theming (light vs dark).

        Args:
            theme_name: Name of the active theme (e.g. 'light', 'dark')
        """
        self.current_theme_name = theme_name

    def render(self, markdown_text: str) -> str:
        """
        Convert markdown text to HTML.

        Args:
            markdown_text: Raw markdown content

        Returns:
            HTML string with basic styling
        """
        # Generate TOC structure and store it
        self.current_toc = self.toc_generator.generate_toc(markdown_text)

        # Inject anchors into headers for TOC linking
        markdown_with_anchors = self.toc_generator.inject_anchors(markdown_text)

        # Extract mermaid blocks before markdown2 processing (it strips language classes)
        mermaid_blocks: list[str] = []
        def _replace_mermaid(match: re.Match) -> str:
            mermaid_blocks.append(match.group(1).strip())
            return f"<!--MERMAID_PLACEHOLDER_{len(mermaid_blocks) - 1}-->"

        markdown_with_anchors = self._MERMAID_FENCE_RE.sub(
            _replace_mermaid, markdown_with_anchors
        )

        # Convert markdown to HTML with syntax highlighting enabled
        html_content = markdown2.markdown(
            markdown_with_anchors,
            extras=self.extras + ["fenced-code-blocks", "code-color"]
        )

        # Re-inject mermaid blocks as <div class="mermaid"> elements
        for i, block in enumerate(mermaid_blocks):
            placeholder = f"<!--MERMAID_PLACEHOLDER_{i}-->"
            html_content = html_content.replace(
                placeholder,
                f'<div class="mermaid">\n{block}\n</div>'
            )

        # Select mermaid theme based on current application theme
        mermaid_theme = "dark" if self.current_theme_name == "dark" else "default"

        # Wrap in a complete HTML document with theme CSS and base styling
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <!-- KaTeX for LaTeX math rendering -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css">
    <script src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js"></script>
    <!-- Mermaid for diagram rendering -->
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{startOnLoad: true, theme: '{mermaid_theme}'}});
    </script>
    <style>
        /* Base styling */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            font-size: {self.font_size}px;
            scroll-behavior: smooth;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
            line-height: 1.25;
        }}
        h1 {{ font-size: 2em; border-bottom: 1px solid; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.5em; border-bottom: 1px solid; padding-bottom: 0.3em; }}
        h3 {{ font-size: 1.25em; }}
        /* Anchor links should be invisible */
        h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {{
            text-decoration: none;
            color: inherit;
        }}
        code {{
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid;
            padding-left: 16px;
            margin-left: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }}
        table th, table td {{
            border: 1px solid;
            padding: 8px 12px;
            text-align: left;
        }}
        table th {{
            font-weight: 600;
        }}
        img {{
            max-width: 100%;
            height: auto;
        }}
        a {{
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        ul, ol {{
            padding-left: 2em;
        }}
        li {{
            margin: 0.25em 0;
        }}
        hr {{
            border: 0;
            border-top: 2px solid;
            margin: 24px 0;
        }}
        /* Mermaid diagram container */
        .mermaid {{
            text-align: center;
            margin: 16px 0;
        }}

        /* Theme-specific colors */
        {self.theme_css}
    </style>
</head>
<body>
{html_content}
<script>
    document.addEventListener("DOMContentLoaded", function() {{
        renderMathInElement(document.body, {{
            delimiters: [
                {{left: "$$", right: "$$", display: true}},
                {{left: "$", right: "$", display: false}}
            ]
        }});
    }});
</script>
</body>
</html>
"""
        return full_html

    def get_toc(self) -> list:
        """
        Get the table of contents for the currently rendered document.

        Returns:
            Hierarchical list of TOC items
        """
        return self.current_toc
