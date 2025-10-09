"""Markdown to HTML rendering engine."""

import markdown2
from pygments.formatters import HtmlFormatter


class MarkdownRenderer:
    """Converts markdown text to HTML."""

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

    def render(self, markdown_text: str) -> str:
        """
        Convert markdown text to HTML.

        Args:
            markdown_text: Raw markdown content

        Returns:
            HTML string with basic styling
        """
        # Convert markdown to HTML with syntax highlighting enabled
        html_content = markdown2.markdown(
            markdown_text,
            extras=self.extras + ["fenced-code-blocks", "code-color"]
        )

        # Wrap in a complete HTML document with theme CSS and base styling
        full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        /* Base styling */
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 900px;
            margin: 0 auto;
            font-size: {self.font_size}px;
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

        /* Theme-specific colors */
        {self.theme_css}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
        return full_html
