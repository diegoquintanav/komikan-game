"""Tests for package entry points."""

from importlib.metadata import entry_points


def test_api_main_is_callable():
    """komikan.api.main must expose the main function used by the console script."""
    from komikan.api.main import main

    assert callable(main)


def test_komikan_api_script_points_at_main():
    """The komikan-api console script must target an existing callable."""
    scripts = {ep.name: ep.value for ep in entry_points(group="console_scripts")}
    assert scripts["komikan-api"] == "komikan.api.main:main"
