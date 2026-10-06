import subprocess
from pathlib import Path


def test_ruff_docstring_formatting() -> None:
    """Ensure package docstrings pass the Ruff checks used in CI."""
    project_root = Path(__file__).resolve().parents[3]
    result = subprocess.run(
        ["ruff", "check", "--select", "D", "--ignore", "D212,D417", "gen_epix"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    output = "\n".join(
        message for message in (result.stdout.strip(), result.stderr.strip()) if message
    )
    assert result.returncode == 0, output
