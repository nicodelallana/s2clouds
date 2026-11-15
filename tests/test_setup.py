"""Basic setup and import tests."""

import s2clouds
from s2clouds.cli import main


def test_version_defined():
    """Check that s2clouds has a valid version string."""
    assert s2clouds.__version__ == "1.0.0"


def test_cli_help(capsys):
    """Check that CLI parser can run without arguments."""
    exit_code = main([])
    assert exit_code == 0
