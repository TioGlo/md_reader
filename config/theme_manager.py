"""Theme management for the markdown reader."""

from pathlib import Path
from typing import Optional


class ThemeManager:
    """Manages theme loading and CSS generation."""

    def __init__(self) -> None:
        """Initialize the theme manager."""
        self.themes_dir = Path(__file__).parent.parent / "resources" / "themes"
        self.available_themes = ["light", "dark", "sepia", "high_contrast"]
        self.current_theme = "light"

    def get_theme_css(self, theme_name: str) -> str:
        """
        Load CSS for the specified theme.

        Args:
            theme_name: Name of the theme ('light' or 'dark')

        Returns:
            CSS content as string

        Raises:
            FileNotFoundError: If theme file doesn't exist
        """
        if theme_name not in self.available_themes:
            theme_name = "light"  # Fallback to light theme

        theme_file = self.themes_dir / f"{theme_name}.css"

        if not theme_file.exists():
            # Return minimal CSS if theme file missing
            return """
                body { background: white; color: black; }
            """

        try:
            with open(theme_file, "r") as f:
                return f.read()
        except IOError:
            # Return minimal CSS on read error
            return """
                body { background: white; color: black; }
            """

    def set_current_theme(self, theme_name: str) -> None:
        """
        Set the current theme.

        Args:
            theme_name: Name of the theme to set
        """
        if theme_name in self.available_themes:
            self.current_theme = theme_name

    def get_current_theme(self) -> str:
        """Get the name of the current theme."""
        return self.current_theme

    def get_available_themes(self) -> list[str]:
        """Get list of available theme names."""
        return self.available_themes.copy()
