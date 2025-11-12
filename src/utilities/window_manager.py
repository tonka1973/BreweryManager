"""
Window Manager Utility

Provides screen detection, window sizing, position management, and resize grips
for the Brewery Manager application.
"""

import json
import os
from pathlib import Path
import ttkbootstrap as ttk
from tkinter import Toplevel

# Global window manager instance
_window_manager = None


class WindowManager:
    """Manages window sizing, positioning, and screen detection"""

    CONFIG_FILE = ".brewery_window_config.json"

    def __init__(self, root):
        """
        Initialize the WindowManager

        Args:
            root: The root Tk window
        """
        self.root = root
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.config = self._load_config()

    def _load_config(self):
        """Load window configuration from file"""
        config_path = Path(self.CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_config(self):
        """Save window configuration to file"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass  # Silently fail if we can't save config

    def get_main_window_size(self):
        """
        Calculate optimal main window size based on screen resolution

        Returns:
            tuple: (width, height) as percentages of screen size
        """
        # Default: 80% width, 90% height
        width = int(self.screen_width * 0.80)
        height = int(self.screen_height * 0.90)

        # Check if we have saved preferences
        if 'main_window' in self.config:
            saved = self.config['main_window']
            if 'width' in saved and 'height' in saved:
                width = saved['width']
                height = saved['height']

        return width, height

    def get_main_window_position(self):
        """
        Calculate optimal main window position (centered)

        Returns:
            tuple: (x, y) position
        """
        width, height = self.get_main_window_size()

        # Default: centered
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2

        # Check if we have saved preferences
        if 'main_window' in self.config:
            saved = self.config['main_window']
            if 'x' in saved and 'y' in saved:
                x = saved['x']
                y = saved['y']

        return x, y

    def save_main_window_geometry(self, window):
        """
        Save current main window size and position

        Args:
            window: The main window
        """
        geometry = window.geometry()
        # Parse geometry string: "WIDTHxHEIGHT+X+Y"
        try:
            size, position = geometry.split('+', 1)
            width, height = map(int, size.split('x'))
            x, y = map(int, position.split('+'))

            self.config['main_window'] = {
                'width': width,
                'height': height,
                'x': x,
                'y': y
            }
            self._save_config()
        except Exception:
            pass

    def get_dialog_size(self, dialog_type, default_width_pct=0.4, default_height_pct=0.6):
        """
        Calculate optimal dialog size based on screen resolution

        Args:
            dialog_type: String identifier for the dialog (e.g., "recipe", "batch")
            default_width_pct: Default width as percentage of screen
            default_height_pct: Default height as percentage of screen

        Returns:
            tuple: (width, height) in pixels
        """
        # Calculate based on screen size
        width = int(self.screen_width * default_width_pct)
        height = int(self.screen_height * default_height_pct)

        # Check if we have saved preferences for this dialog
        if dialog_type in self.config:
            saved = self.config[dialog_type]
            if 'width' in saved and 'height' in saved:
                width = saved['width']
                height = saved['height']

        return width, height

    def get_dialog_position(self, dialog_type, width, height):
        """
        Calculate optimal dialog position (centered by default)

        Args:
            dialog_type: String identifier for the dialog
            width: Dialog width
            height: Dialog height

        Returns:
            tuple: (x, y) position
        """
        # Default: centered on screen
        x = (self.screen_width - width) // 2
        y = (self.screen_height - height) // 2

        # Check if we have saved preferences
        if dialog_type in self.config:
            saved = self.config[dialog_type]
            if 'x' in saved and 'y' in saved:
                x = saved['x']
                y = saved['y']

        return x, y

    def save_dialog_geometry(self, dialog_type, dialog):
        """
        Save current dialog size and position

        Args:
            dialog_type: String identifier for the dialog
            dialog: The dialog window
        """
        geometry = dialog.geometry()
        try:
            size, position = geometry.split('+', 1)
            width, height = map(int, size.split('x'))
            x, y = map(int, position.split('+'))

            self.config[dialog_type] = {
                'width': width,
                'height': height,
                'x': x,
                'y': y
            }
            self._save_config()
        except Exception:
            pass

    def add_resize_grip(self, window):
        """
        Add a visible resize grip to the bottom-right corner of a window

        Args:
            window: The window (Toplevel or Tk) to add grip to

        Returns:
            ttk.Sizegrip: The created grip widget
        """
        grip = ttk.Sizegrip(window)
        grip.pack(side='bottom', anchor='se')
        return grip

    def setup_main_window(self, window, save_on_close=True):
        """
        Setup main window with optimal size and position

        Args:
            window: The main window
            save_on_close: Whether to save geometry when window closes
        """
        width, height = self.get_main_window_size()
        x, y = self.get_main_window_position()

        window.geometry(f"{width}x{height}+{x}+{y}")

        if save_on_close:
            # Save geometry when window is closed
            window.protocol("WM_DELETE_WINDOW", lambda: self._on_main_close(window))

    def _on_main_close(self, window):
        """Handle main window close event"""
        self.save_main_window_geometry(window)
        window.destroy()

    def setup_dialog(self, dialog, dialog_type, width_pct=0.4, height_pct=0.6,
                     add_grip=True, save_on_close=True, resizable=True):
        """
        Setup dialog with optimal size, position, and resize grip

        Args:
            dialog: The dialog window (Toplevel)
            dialog_type: String identifier for the dialog
            width_pct: Width as percentage of screen (default 0.4 = 40%)
            height_pct: Height as percentage of screen (default 0.6 = 60%)
            add_grip: Whether to add resize grip (default True)
            save_on_close: Whether to save geometry on close (default True)
            resizable: Whether dialog should be resizable (default True)

        Returns:
            ttk.Sizegrip or None: The resize grip if added
        """
        width, height = self.get_dialog_size(dialog_type, width_pct, height_pct)
        x, y = self.get_dialog_position(dialog_type, width, height)

        dialog.geometry(f"{width}x{height}+{x}+{y}")

        if resizable:
            dialog.resizable(True, True)
        else:
            dialog.resizable(False, False)

        grip = None
        if add_grip and resizable:
            grip = self.add_resize_grip(dialog)

        if save_on_close:
            # Save geometry when dialog is closed
            original_destroy = dialog.destroy
            def on_close():
                self.save_dialog_geometry(dialog_type, dialog)
                original_destroy()
            dialog.destroy = on_close

        return grip

    def get_screen_info(self):
        """
        Get screen resolution information

        Returns:
            dict: Screen information
        """
        return {
            'width': self.screen_width,
            'height': self.screen_height,
            'aspect_ratio': round(self.screen_width / self.screen_height, 2)
        }


def set_window_manager(window_manager):
    """
    Set the global window manager instance

    Args:
        window_manager: WindowManager instance
    """
    global _window_manager
    _window_manager = window_manager


def get_window_manager():
    """
    Get the global window manager instance

    Returns:
        WindowManager or None: The global window manager
    """
    return _window_manager
