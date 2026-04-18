import ast
import os
import re
from pathlib import Path

import pytest

# set to false to only print the duplicate codes without failing the test
SHOULD_FAIL = True


def _is_long_hex_string(string: str) -> bool:
    """
    Check if a string is a hexadecimal string of length 8 or longer.
    """
    # Regex for exactly hex characters, length 8+, start to end
    return bool(re.match(r"^[0-9a-fA-F]{8,}$", string))


def _get_python_files(root_dir: Path) -> list[Path]:
    """
    Recursively find all .py files in the directory, excluding common ignored dirs.
    """
    python_files: list[Path] = []
    # Ignoring common non-source/build directories
    skip_dirs = {
        ".git",
        ".venv",
        "venv",
        "env",
        ".pytest_cache",
        "__pycache__",
        "build",
        "dist",
        "site-packages",
        "Gen_EpiX.egg-info",
        "test",
    }

    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to prune walk
        dirs[:] = [x for x in dirs if x not in skip_dirs]

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    return python_files


def _extract_hex_strings_from_file(file_path: Path) -> list[tuple[str, int]]:
    """
    Parse a python file and find all string literals that match the hex criteria.
    Returns list of (hex_string, line_number).
    """
    results: list[tuple[str, int]] = []
    try:
        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            print(f"Skipping {file_path}: SyntaxError")
            return []

        # Walk AST for string literals
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, str):
                    if _is_long_hex_string(node.value):
                        results.append((node.value, node.lineno))

    except Exception as e:
        print(f"Could not process {file_path}: {e}")

    return results


def _hanlde_duplicate_hex_codes(duplicates: dict[str, list[str]]) -> None:
    msg_blocks = ["Unicity check failed. Duplicate hexadecimal strings found:"]

    for code in sorted(duplicates.keys()):
        locs = duplicates[code]
        msg_blocks.append(f"\nCode '{code}' found in {len(locs)} places:")
        for loc in locs:
            msg_blocks.append(f"  - {loc}")

    full_message = "\n".join(msg_blocks)

    if SHOULD_FAIL:
        pytest.fail(full_message)
    else:
        print(full_message)


def _get_all_seen_codes(
    current_file: Path, repo_root: Path, files: list[Path]
) -> dict[str, list[str]]:
    # Store found codes: {normalized_code: [list of "path:line"]}
    seen_codes: dict[str, list[str]] = {}
    for file_path in files:
        if file_path.name == current_file.name:
            continue

        found_strings = _extract_hex_strings_from_file(file_path)

        for code, line in found_strings:
            norm_code = code.lower()
            try:
                display_path = file_path.relative_to(repo_root)
            except ValueError:
                display_path = file_path

            location = f"{display_path}:{line}"

            if norm_code not in seen_codes:
                seen_codes[norm_code] = []
            seen_codes[norm_code].append(location)
    return seen_codes


def _get_repo_root(current_file: Path) -> Path:
    repo_root = current_file.parent
    while len(repo_root.parts) > 1:
        if (repo_root / "pyproject.toml").exists():
            break
        repo_root = repo_root.parent
    else:
        # Fallback if pyproject.toml not found: assume 3 levels up from test/general/code
        repo_root = current_file.parents[3]
    return repo_root


@pytest.mark.scenario_ids("TC-SEC-28-08")
def test_error_code_unicity() -> None:
    """
    Read all python modules (*.py). Extract hexadecimal strings of length 8 or longer. Check if unique.
    """
    current_file = Path(__file__).resolve()

    repo_root = _get_repo_root(current_file)
    files = _get_python_files(repo_root)
    seen_codes = _get_all_seen_codes(current_file, repo_root, files)

    duplicates = {x: y for x, y in seen_codes.items() if len(y) > 1}
    if duplicates:
        # Format failure message
        _hanlde_duplicate_hex_codes(duplicates)

    print(
        "Unicity check passed. Checked {} files, found {} unique codes.".format(
            len(files), len(seen_codes)
        )
    )
