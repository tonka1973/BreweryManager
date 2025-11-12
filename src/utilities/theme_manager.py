"""
Theme Manager for Brewery Management System

Handles theme switching between light and dark modes using ttkbootstrap.
Persists user theme preferences to configuration file.
"""

import json
import os
from pathlib import Path
from typing import Literal

ThemeType = Literal["light", "dark"]


class ThemeManager:
    """Manages application theme settings and persistence."""

    # Available ttkbootstrap themes
    LIGHT_THEMES = [
        "cosmo",      # Default light - clean and modern
        "flatly",     # Flat design
        "journal",    # Classic
        "litera",     # Simple and clean
        "lumen",      # Bright and airy
        "minty",      # Fresh green accent
        "pulse",      # Purple accent
        "sandstone",  # Warm tones
        "united",     # Orange accent
        "yeti",       # Blue accent
    ]

    DARK_THEMES = [
        "darkly",     # Default dark - Bootstrap dark
        "cyborg",     # Tron-inspired
        "superhero",  # Comic book style
        "solar",      # Solarized dark
        "vapor",      # Synthwave inspired
    ]

    DEFAULT_LIGHT_THEME = "cosmo"
    DEFAULT_DARK_THEME = "darkly"

    def __init__(self, config_dir: str = "config"):
        """
        Initialize theme manager.

        Args:
            config_dir: Directory to store theme configuration
        """
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "theme_config.json"
        self._current_mode: ThemeType = "light"
        self._current_light_theme = self.DEFAULT_LIGHT_THEME
        self._current_dark_theme = self.DEFAULT_DARK_THEME

        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)

        # Load saved preferences
        self._load_preferences()

    def _load_preferences(self) -> None:
        """Load theme preferences from configuration file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self._current_mode = config.get("mode", "light")
                    self._current_light_theme = config.get(
                        "light_theme", self.DEFAULT_LIGHT_THEME
                    )
                    self._current_dark_theme = config.get(
                        "dark_theme", self.DEFAULT_DARK_THEME
                    )
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load theme config: {e}")
                self._save_preferences()  # Save defaults

    def _save_preferences(self) -> None:
        """Save current theme preferences to configuration file."""
        config = {
            "mode": self._current_mode,
            "light_theme": self._current_light_theme,
            "dark_theme": self._current_dark_theme,
        }

        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            print(f"Warning: Could not save theme config: {e}")

    @property
    def current_mode(self) -> ThemeType:
        """Get current theme mode (light or dark)."""
        return self._current_mode

    @property
    def current_theme(self) -> str:
        """Get current active theme name."""
        if self._current_mode == "light":
            return self._current_light_theme
        else:
            return self._current_dark_theme

    def toggle_mode(self) -> str:
        """
        Toggle between light and dark mode.

        Returns:
            The new theme name to apply
        """
        self._current_mode = "dark" if self._current_mode == "light" else "light"
        self._save_preferences()
        return self.current_theme

    def set_mode(self, mode: ThemeType) -> str:
        """
        Set specific theme mode.

        Args:
            mode: "light" or "dark"

        Returns:
            The theme name to apply
        """
        if mode not in ("light", "dark"):
            raise ValueError(f"Invalid theme mode: {mode}")

        self._current_mode = mode
        self._save_preferences()
        return self.current_theme

    def set_light_theme(self, theme: str) -> None:
        """
        Set preferred light theme.

        Args:
            theme: Name of light theme from LIGHT_THEMES
        """
        if theme not in self.LIGHT_THEMES:
            raise ValueError(f"Invalid light theme: {theme}")

        self._current_light_theme = theme
        self._save_preferences()

    def set_dark_theme(self, theme: str) -> None:
        """
        Set preferred dark theme.

        Args:
            theme: Name of dark theme from DARK_THEMES
        """
        if theme not in self.DARK_THEMES:
            raise ValueError(f"Invalid dark theme: {theme}")

        self._current_dark_theme = theme
        self._save_preferences()

    def get_available_themes(self, mode: ThemeType = None) -> list[str]:
        """
        Get list of available themes.

        Args:
            mode: "light", "dark", or None for current mode

        Returns:
            List of available theme names
        """
        if mode is None:
            mode = self._current_mode

        return self.LIGHT_THEMES if mode == "light" else self.DARK_THEMES

    def is_dark_mode(self) -> bool:
        """Check if currently in dark mode."""
        return self._current_mode == "dark"

    def is_light_mode(self) -> bool:
        """Check if currently in light mode."""
        return self._current_mode == "light"


# Global theme manager instance
_theme_manager = None


def get_theme_manager(config_dir: str = "config") -> ThemeManager:
    """
    Get the global theme manager instance.

    Args:
        config_dir: Configuration directory (used only on first call)

    Returns:
        ThemeManager instance
    """
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager(config_dir)
    return _theme_manager
