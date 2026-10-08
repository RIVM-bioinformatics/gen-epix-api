"""Tests for common domain configuration utilities."""

from pathlib import Path

import pytest

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import (
    _resolve_extra_settings_files,
    get_app_cfg_class,
)


@pytest.mark.parametrize("settings_files", [None, []])
def test_resolve_extra_settings_files_returns_none_when_absent(
    settings_files: list[Path] | None,
) -> None:
    """Normalize absent and empty optional settings-file inputs to None."""
    assert _resolve_extra_settings_files(settings_files) is None


def test_resolve_extra_settings_files_accepts_single_path_and_file_list(
    tmp_path: Path,
) -> None:
    """Resolve a single path or list of existing files to absolute paths."""
    first = tmp_path / "first.toml"
    second = tmp_path / "second.toml"
    first.touch()
    second.touch()

    assert _resolve_extra_settings_files(first) == [first.resolve()]
    assert _resolve_extra_settings_files([str(first), second]) == [
        first.resolve(),
        second.resolve(),
    ]


@pytest.mark.parametrize("is_directory", [False, True])
def test_resolve_extra_settings_files_rejects_non_files(
    tmp_path: Path, is_directory: bool
) -> None:
    """Reject paths that do not identify an existing regular file."""
    path = tmp_path / "missing.toml"
    if is_directory:
        path.mkdir()

    with pytest.raises(ValueError, match="does not exist or is not a file"):
        _resolve_extra_settings_files(path)


def test_get_app_cfg_class_resolves_shared_and_app_specific_classes() -> None:
    """Use AppCfg for commondb and each app's own configuration subclass."""
    assert get_app_cfg_class(AppType.COMMONDB) is AppCfg
    assert get_app_cfg_class("CASEDB").__name__ == "CasedbAppCfg"
