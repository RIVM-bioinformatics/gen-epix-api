"""Verify settings-manager access after loading explicit files."""

from pathlib import Path

from gen_epix.commondb.config.settings_manager import SettingsManager


def test_constructor_settings_files_populate_manager_cache(tmp_path: Path) -> None:
    """Expose explicitly loaded settings through settings and get_setting."""
    settings_file = tmp_path / "settings.toml"
    settings_file.write_text("answer = 42\n", encoding="utf-8")
    manager = SettingsManager(prefix="TEST_", settings_files=[str(settings_file)])

    loaded_settings = manager.load_settings()

    assert manager.settings is loaded_settings
    assert manager.get_setting("answer") == 42
