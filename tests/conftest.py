"""
Pytest configuration and shared fixtures for Brewery Manager tests.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src directory to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


@pytest.fixture
def temp_config_dir():
    """Provide a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_theme_config():
    """Provide sample theme configuration data."""
    return {
        "mode": "light",
        "light_theme": "cosmo",
        "dark_theme": "darkly"
    }


@pytest.fixture
def mock_database_path(tmp_path):
    """Provide a temporary database file path."""
    db_path = tmp_path / "test_brewery.db"
    return str(db_path)


# Add more fixtures as needed for different test scenarios
