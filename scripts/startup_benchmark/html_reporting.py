"""Render saved startup evidence as an offline HTML dashboard.

generate_html validates presentation data and uses the shared statistics and
compatibility rules. It neither launches applications nor reads referenced logs.
Dashboard dependencies are loaded only when generating HTML.
"""

import math
import os
import tempfile
from pathlib import Path

from .models import APPLICATIONS, SCHEMA_VERSION
from .reporting import NOTES, compatible
from .statistics import summarize

ASSETS = Path(__file__).with_name("dashboard")


def _number(value: object, integer: bool = False) -> bool:
    if (
        not isinstance(value, int if integer else (int, float))
        or isinstance(value, bool)
        or value < 0
    ):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _validate(data: dict) -> None:
    """Check the version-one fields consumed by the dashboard."""
    if (
        not isinstance(data, dict)
        or data.get("schema_version") != SCHEMA_VERSION
        or not isinstance(data.get("application"), str)
        or data.get("application") not in APPLICATIONS
        or data.get("command") not in ("benchmark", "diagnose")
        or not isinstance(data.get("options"), dict)
        or not isinstance(data.get("metadata"), dict)
        or not isinstance(data.get("records"), list)
    ):
        raise ValueError("Invalid startup benchmark artifact")
    if "commit" not in data["metadata"] or (
        data["metadata"]["commit"] is not None
        and not isinstance(data["metadata"]["commit"], str)
    ):
        raise ValueError("Invalid benchmark commit metadata")
    for key in ("idp_mode", "repository_mode"):
        if not isinstance(data["options"].get(key), str):
            raise ValueError(f"Invalid benchmark option: {key}")  # noqa: TRY004
    for key in ("configuration_valid", "series_completed"):
        if key in data and not isinstance(data[key], bool):
            raise ValueError(f"Invalid benchmark field: {key}")
    indices = set()
    for record in data["records"]:
        if (
            not isinstance(record, dict)
            or not _number(record.get("index"), integer=True)
            or record["index"] in indices
            or any(
                not isinstance(record.get(key), str)
                for key in ("kind", "status", "cleanup")
            )
            or (record.get("seconds") is not None and not _number(record["seconds"]))
            or (record["status"] == "success" and record.get("seconds") is None)
            or (
                record.get("error") is not None and not isinstance(record["error"], str)
            )
        ):
            raise ValueError("Invalid benchmark run record")
        indices.add(record["index"])


def _imports(data: dict) -> list[dict]:
    """Select full import occurrences without aggregating cumulative costs."""
    details = data.get("diagnostics", [])
    if not isinstance(details, list):
        raise ValueError("Invalid diagnostics list")  # noqa: TRY004
    result = []
    for index, detail in enumerate(details):
        if not isinstance(detail, dict):
            raise ValueError("Invalid diagnostic record")  # noqa: TRY004
        if detail.get("kind") != "imports":
            continue
        analysis = detail.get("analysis")
        if not isinstance(analysis, dict) or not isinstance(
            analysis.get("records"), list
        ):
            raise ValueError("Invalid import analysis")  # noqa: TRY004
        if (
            not _number(detail.get("run", index + 1), integer=True)
            or not isinstance(analysis.get("warnings", []), list)
            or any(not isinstance(w, str) for w in analysis.get("warnings", []))
            or not isinstance(analysis.get("interpretation", ""), str)
        ):
            raise ValueError("Invalid import diagnostic metadata")
        for record in analysis["records"]:
            if (
                not isinstance(record, dict)
                or not _number(record.get("id"), integer=True)
                or not isinstance(record.get("module"), str)
                or not _number(record.get("self_us"), integer=True)
                or not _number(record.get("cumulative_us"), integer=True)
                or not isinstance(record.get("chain"), list)
                or any(not isinstance(item, str) for item in record["chain"])
            ):
                raise ValueError("Invalid import occurrence")
        result.append(
            {
                "run": detail.get("run", index + 1),
                "records": [
                    {
                        key: r[key]
                        for key in ("id", "module", "self_us", "cumulative_us", "chain")
                    }
                    for r in analysis["records"]
                ],
                "warnings": analysis.get("warnings", []),
                "interpretation": analysis.get("interpretation", ""),
            }
        )
    return result


def generate_html(data: dict, output: Path, diagnostics: dict | None = None) -> str:
    """Write one standalone dashboard using saved version-one evidence.

    Overall statistics describe successful measured runs and stay fixed during
    browser filtering. Supplied dictionaries are not modified. Dependencies and
    assets are embedded in the file, which can be opened without a server.

    Args:
        data: Benchmark or diagnostic artifact loaded from saved JSON.
        output: Destination HTML file; missing parent directories are created.
        diagnostics: Optional separately collected, compatible diagnostic artifact.

    Returns:
        A message identifying the generated dashboard.

    Raises:
        ValueError: If artifacts, compatibility, or the output suffix are invalid,
            or Jinja2 or Plotly is unavailable.
        OSError: If the dashboard cannot be written.
    """
    if output.suffix.lower() not in (".html", ".htm"):
        raise ValueError("HTML report --output must end in .html or .htm")
    _validate(data)
    if diagnostics is not None:
        _validate(diagnostics)
        if not compatible(data, diagnostics):
            raise ValueError(
                "Diagnostics application, commit, or configuration evidence does not match"
            )
    stats = summarize(
        data["records"],
        data.get("configuration_valid", False),
        data.get("series_completed", True),
    )
    payload = {
        "records": [
            {
                key: record.get(key)
                for key in ("index", "kind", "status", "seconds", "cleanup", "error")
            }
            for record in data["records"]
        ],
        "statistics": stats,
        "imports": _imports(diagnostics if diagnostics is not None else data),
    }
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        from plotly.offline import get_plotlyjs
    except ImportError as error:
        raise ValueError(
            "HTML reporting requires Jinja2 and Plotly; install with "
            "python -m pip install -r dev-requirements.txt"
        ) from error
    environment = Environment(
        loader=FileSystemLoader(ASSETS), autoescape=select_autoescape(["html"])
    )
    rendered = environment.get_template("report.html").render(
        data=data,
        stats=stats,
        payload=payload,
        notes=NOTES,
        css=(ASSETS / "report.css").read_text(encoding="utf-8"),
        javascript=(ASSETS / "report.js").read_text(encoding="utf-8"),
        plotly_js=get_plotlyjs(),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=output.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(rendered)
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return f"HTML report: {output}"
