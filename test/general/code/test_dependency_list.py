import re
import tomllib
from pathlib import Path

import pytest


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent.parent


def _parse_requirements_line(line: str) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    line = re.sub(r"\s+#.*$", "", line).strip()
    return line


def _read_requirements(requirements_file_path: Path) -> set[str]:
    if not requirements_file_path.exists():
        return set()
    items: set[str] = set()
    for raw in requirements_file_path.read_text(encoding="utf-8").splitlines():
        norm = _parse_requirements_line(raw)
        if norm:
            items.add(norm)
    return items


def _parse_pyproject_dependency(dep: str) -> str:
    # Keep full specifier for exact comparison; collapse spaces
    return re.sub(r"\s+", " ", dep.strip())


def _read_pyproject_dependencies(pyproject_file_path: Path) -> set[str]:
    if not pyproject_file_path.exists():
        return set()
    data = tomllib.loads(pyproject_file_path.read_text(encoding="utf-8"))
    deps: list[str] = data.get("project", {}).get("dependencies", [])
    dependencies: set[str] = {_parse_pyproject_dependency(x) for x in deps}
    return dependencies


def test_dependency_list_matches() -> None:
    """Ensure requirements.txt and pyproject.toml dependencies are identical."""
    root = get_project_root()

    reqs = _read_requirements(root / "requirements.txt")
    pydeps = _read_pyproject_dependencies(root / "pyproject.toml")

    missing_from_pyproject = sorted(reqs - pydeps)
    missing_from_requirements = sorted(pydeps - reqs)

    # Remove report file writing; fail directly with a concise diff
    if missing_from_pyproject or missing_from_requirements:
        msg_lines = [
            "Dependency mismatch detected between requirements.txt and pyproject.toml."
        ]
        if missing_from_pyproject:
            msg_lines.append("Only in requirements.txt:")
            msg_lines.extend(f"  - {x}" for x in missing_from_pyproject)
        if missing_from_requirements:
            msg_lines.append("Only in pyproject.toml:")
            msg_lines.extend(f"  - {x}" for x in missing_from_requirements)

        pytest.fail("\n".join(msg_lines))
