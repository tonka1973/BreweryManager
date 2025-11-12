"""
Unit tests for Theme Manager

Tests the theme switching and persistence functionality.
"""

import json
from pathlib import Path

import pytest

from utilities.theme_manager import ThemeManager, get_theme_manager


class TestThemeManager:
    """Test suite for ThemeManager class."""

    def test_initialization_default(self, temp_config_dir):
        """Test theme manager initializes with default values."""
        tm = ThemeManager(temp_config_dir)
        assert tm.current_mode == "light"
        assert tm.current_theme == "cosmo"
        assert tm.is_light_mode() is True
        assert tm.is_dark_mode() is False

    def test_toggle_mode(self, temp_config_dir):
        """Test toggling between light and dark modes."""
        tm = ThemeManager(temp_config_dir)

        # Start in light mode
        assert tm.current_mode == "light"

        # Toggle to dark
        new_theme = tm.toggle_mode()
        assert tm.current_mode == "dark"
        assert new_theme == "darkly"
        assert tm.is_dark_mode() is True

        # Toggle back to light
        new_theme = tm.toggle_mode()
        assert tm.current_mode == "light"
        assert new_theme == "cosmo"
        assert tm.is_light_mode() is True

    def test_set_mode(self, temp_config_dir):
        """Test setting specific theme mode."""
        tm = ThemeManager(temp_config_dir)

        # Set to dark
        theme = tm.set_mode("dark")
        assert tm.current_mode == "dark"
        assert theme == "darkly"

        # Set to light
        theme = tm.set_mode("light")
        assert tm.current_mode == "light"
        assert theme == "cosmo"

    def test_set_mode_invalid(self, temp_config_dir):
        """Test that invalid mode raises error."""
        tm = ThemeManager(temp_config_dir)

        with pytest.raises(ValueError):
            tm.set_mode("invalid")

    def test_set_light_theme(self, temp_config_dir):
        """Test setting custom light theme."""
        tm = ThemeManager(temp_config_dir)

        tm.set_light_theme("flatly")
        assert tm.current_theme == "flatly"

    def test_set_dark_theme(self, temp_config_dir):
        """Test setting custom dark theme."""
        tm = ThemeManager(temp_config_dir)

        tm.set_dark_theme("cyborg")
        tm.set_mode("dark")
        assert tm.current_theme == "cyborg"

    def test_set_invalid_light_theme(self, temp_config_dir):
        """Test that invalid light theme raises error."""
        tm = ThemeManager(temp_config_dir)

        with pytest.raises(ValueError):
            tm.set_light_theme("invalid")

    def test_set_invalid_dark_theme(self, temp_config_dir):
        """Test that invalid dark theme raises error."""
        tm = ThemeManager(temp_config_dir)

        with pytest.raises(ValueError):
            tm.set_dark_theme("invalid")

    def test_persistence(self, temp_config_dir):
        """Test that theme preferences persist across instances."""
        # Create first instance and set preferences
        tm1 = ThemeManager(temp_config_dir)
        tm1.set_mode("dark")
        tm1.set_dark_theme("superhero")

        # Create second instance and verify preferences loaded
        tm2 = ThemeManager(temp_config_dir)
        assert tm2.current_mode == "dark"
        assert tm2.current_theme == "superhero"

    def test_config_file_created(self, temp_config_dir):
        """Test that configuration file is created."""
        tm = ThemeManager(temp_config_dir)
        config_file = Path(temp_config_dir) / "theme_config.json"

        assert config_file.exists()

    def test_config_file_format(self, temp_config_dir):
        """Test that configuration file has correct format."""
        tm = ThemeManager(temp_config_dir)
        tm.set_mode("dark")
        tm.set_light_theme("minty")
        tm.set_dark_theme("cyborg")

        config_file = Path(temp_config_dir) / "theme_config.json"
        with open(config_file, "r") as f:
            config = json.load(f)

        assert config["mode"] == "dark"
        assert config["light_theme"] == "minty"
        assert config["dark_theme"] == "cyborg"

    def test_get_available_themes_light(self, temp_config_dir):
        """Test getting available light themes."""
        tm = ThemeManager(temp_config_dir)
        themes = tm.get_available_themes("light")

        assert isinstance(themes, list)
        assert "cosmo" in themes
        assert "flatly" in themes
        assert "darkly" not in themes

    def test_get_available_themes_dark(self, temp_config_dir):
        """Test getting available dark themes."""
        tm = ThemeManager(temp_config_dir)
        themes = tm.get_available_themes("dark")

        assert isinstance(themes, list)
        assert "darkly" in themes
        assert "cyborg" in themes
        assert "cosmo" not in themes

    def test_get_available_themes_current(self, temp_config_dir):
        """Test getting themes for current mode."""
        tm = ThemeManager(temp_config_dir)

        # In light mode
        tm.set_mode("light")
        themes = tm.get_available_themes()
        assert "cosmo" in themes

        # In dark mode
        tm.set_mode("dark")
        themes = tm.get_available_themes()
        assert "darkly" in themes


class TestThemeManagerSingleton:
    """Test the global theme manager singleton."""

    def test_singleton_returns_same_instance(self):
        """Test that get_theme_manager returns same instance."""
        tm1 = get_theme_manager()
        tm2 = get_theme_manager()

        assert tm1 is tm2


# Add pytest markers
pytestmark = [pytest.mark.unit, pytest.mark.theme]
