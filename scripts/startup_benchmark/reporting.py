"""Write deterministic JSON, Markdown, and standalone SVG report artifacts."""

import html
import json
from pathlib import Path

from .models import SCHEMA_VERSION
from .statistics import summarize

NOTES = (
    "Fresh-process startup with ordinary system caches. Filesystem, shared-library, "
    "bytecode, and external service caches are not reset. Health verifies this "
    "instance serves the endpoint, not database or business readiness. Timings "
    "include polling and request overhead. Thirty samples yield a coarse empirical "
    "p95, not a high-confidence population p95. The nonce header can cause an "
    "unrecognized-key configuration warning; middleware still reads it. "
    "Diagnostic durations never enter normal statistics."
)


def save_json(path: Path, data: dict) -> None:
    """Atomically persist a versioned artifact before the next process starts."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    temporary.replace(path)


def load_json(path: Path) -> dict:
    """Read a supported artifact schema.

    Raises:
        ValueError: If the artifact uses an unsupported schema version.
    """
    data = json.loads(path.read_text())
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported startup benchmark schema version")
    return data


def compatible(results: dict, diagnostics: dict) -> bool:
    """Compare application, commit, and non-secret configuration evidence."""
    return (
        all(
            results.get(k) == diagnostics.get(k)
            for k in ("application", "configuration_fingerprint")
        )
        and bool(results.get("configuration_fingerprint"))
        and results["metadata"]["commit"] == diagnostics["metadata"]["commit"]
        and results.get("configuration_valid", False)
        and diagnostics.get("configuration_valid", False)
    )


def _svg(path: Path, height: int, elements: list[str]) -> None:
    path.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" font-size="12">'
        + "".join(elements)
        + "</g></svg>\n"
    )


def _text(x, y, value) -> str:
    return f'<text x="{x}" y="{y}">{html.escape(str(value))}</text>'


def startup_chart(records: list[dict], stats: dict, path: Path) -> None:
    """Plot successful samples, failure markers, and a sorted distribution."""
    runs = [r for r in records if r["kind"] == "measured"]
    values = sorted(r["seconds"] for r in runs if r["status"] == "success")
    scale = 200 / max([15, *values])
    elements = [
        _text(
            30,
            25,
            "Startup seconds: attempts (left) and sorted successful samples (right)",
        )
    ]
    for offset, population in (
        (40, runs),
        (630, [{"seconds": v, "status": "success"} for v in values]),
    ):
        for threshold, color, label in (
            (15, "red", "15s target"),
            (stats["p95"], "purple", "p95"),
        ):
            if threshold is not None:
                y = 260 - threshold * scale
                elements.append(
                    f'<path d="M{offset} {y}h520" stroke="{color}" stroke-dasharray="4 3"/>'
                )
                elements.append(_text(offset, y - 4, label))
        for i, record in enumerate(population):
            x = offset + 510 * (i + 0.5) / max(1, len(population))
            if record["status"] == "success":
                y = 260 - record["seconds"] * scale
                elements.append(
                    f'<circle cx="{x}" cy="{y}" r="3" fill="steelblue"><title>{html.escape(str(record))}</title></circle>'
                )
            else:
                elements.append(
                    _text(x, 285, "×" if record["status"] != "not_attempted" else "·")
                )
    elements += [
        _text(40, 315, "× failure; · not attempted. Neither is assigned a duration."),
        _text(
            40,
            335,
            "All values include process launch through verified health-response completion.",
        ),
    ]
    _svg(path, 360, elements)


def import_chart(parsed: dict, path: Path) -> None:
    """Draw top self costs with cumulative costs and observed chains alongside."""
    top = parsed["top_self"]
    maximum = max([1, *(r["self_us"] for r in top)])
    elements = [_text(20, 25, "Import self time (ms); cumulative (ms); observed chain")]
    for i, record in enumerate(top):
        y = 55 + i * 27
        elements += [
            _text(10, y, record["module"]),
            f'<rect x="350" y="{y-12}" width="{300*record["self_us"]/maximum}" height="15" fill="steelblue"/>',
            _text(
                660,
                y,
                f'{record["self_us"]/1000:.2f} / {record["cumulative_us"]/1000:.2f}',
            ),
            _text(790, y, " → ".join(record["chain"])),
        ]
    _svg(path, 80 + 27 * len(top), elements)


def phase_chart(analysis: dict, path: Path) -> None:
    """Draw nested and overlapping spans without implying a normal-time partition."""
    spans = analysis["spans"]
    first = analysis.get("measurement_start_ns") or min(
        (s["time_ns"] for s in spans), default=0
    )
    last = max((s.get("end_ns", s["time_ns"]) for s in spans), default=first + 1)
    last = max(last, analysis.get("verified_response_ns") or last)
    elements = [
        _text(
            20,
            25,
            "Instrumented timeline: inclusive spans; overlaps retained; incomplete spans marked",
        )
    ]
    for i, span in enumerate(spans):
        y = 55 + 23 * i
        x = 450 + 720 * (span["time_ns"] - first) / max(1, last - first)
        width = (
            720
            * (span.get("end_ns", span["time_ns"]) - span["time_ns"])
            / max(1, last - first)
        )
        elements += [
            _text(
                10,
                y,
                f'{span["id"]} parent={span["parent"]} {span["label"] or ""} {span["name"]}',
            ),
            f'<rect x="{x}" y="{y-11}" width="{max(2,width)}" height="13" fill="{"steelblue" if "end_ns" in span else "red"}"><title>{html.escape(str(span))}</title></rect>',
        ]
    _svg(path, 80 + 23 * len(spans), elements)


def _cell(value) -> str:
    return html.escape(str(value)).replace("|", "&#124;").replace("\n", "<br>")


def generate(data: dict, output: Path, diagnostics: dict | None = None) -> str:
    """Generate reports from saved records without starting application processes.

    Raises:
        ValueError: If attached diagnostic evidence does not match the benchmark.
    """
    if diagnostics is not None and not compatible(data, diagnostics):
        raise ValueError(
            "Diagnostics application, commit, or configuration evidence does not match"
        )
    output.mkdir(parents=True, exist_ok=True)
    stats = summarize(
        data["records"],
        data.get("configuration_valid", False),
        data.get("series_completed", True),
    )
    data["statistics"] = stats
    save_json(output / "results.json", data)
    summary = f'{data["application"]} {data["options"]["idp_mode"]}/{data["options"]["repository_mode"]}: {stats["successes"]}/{stats["requested"]} successful, {stats["failures"]} failed, {stats["unattempted"]} not attempted; p95={stats["p95"]}; margin={stats["margin"]}; evidence={stats["evidence_valid"]}; target_pass={stats["target_pass"]}'
    summary += f'; attempted={stats["attempted"]}; mean={stats["mean"]}; median={stats["median"]}; min={stats["minimum"]}; max={stats["maximum"]}; p90={stats["p90"]}; target<15s; above_target={stats["above_target"]} ({stats["above_target_percent"]}%)'
    if data["command"] == "diagnose":
        successes = sum(r["status"] == "success" for r in data["records"])
        attempted = sum(r["status"] != "not_attempted" for r in data["records"])
        summary = f'{data["application"]} diagnostics {data["options"]["idp_mode"]}/{data["options"]["repository_mode"]}: {successes}/{len(data["records"])} successful, {attempted-successes} failed, {len(data["records"])-attempted} not attempted. Diagnostic durations are excluded from normal statistics.'
    lines = [
        "# Startup benchmark",
        "",
        summary,
        "",
        NOTES,
        "",
        "## Statistics",
        "",
        "| Metric | Value |",
        "| --- | --- |",
    ]
    lines += [f"| {_cell(k)} | {_cell(v)} |" for k, v in stats.items()]
    lines += [
        "",
        "## Attempts",
        "",
        "| Run | Kind | Status | Seconds | Cleanup | Logs |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in data["records"]:
        lines.append(
            f'| {r["index"]} | {_cell(r["kind"])} | {_cell(r["status"])} | {r["seconds"]} | {_cell(r["cleanup"])} | {_cell(r["stderr"])} |'
        )
    startup_chart(data["records"], stats, output / "startup.svg")
    lines += [
        "",
        "![Startup](startup.svg)",
        "",
        "## Reproducibility",
        "",
        "See results.json for options, commands, redacted configuration, host metadata, and configuration-change evidence.",
    ]
    attached = diagnostics or (data if data["command"] == "diagnose" else None)
    if attached:
        save_json(output / "diagnostics.json", attached)
        for i, detail in enumerate(attached.get("diagnostics", [])):
            lines += [
                "",
                f'## Diagnostic {i + 1}: {_cell(detail["kind"])}',
                "",
                _cell(detail["analysis"]["interpretation"]),
            ]
            chart = f"diagnostic-{i+1}.svg"
            if detail["kind"] == "imports":
                import_chart(detail["analysis"], output / chart)
                lines += [
                    "",
                    "| Module | Self ms | Cumulative ms | Observed chain |",
                    "| --- | --- | --- | --- |",
                ]
                lines += [
                    f'| {_cell(r["module"])} | {r["self_us"]/1000:.3f} | {r["cumulative_us"]/1000:.3f} | {_cell(" → ".join(r["chain"]))} |'
                    for r in detail["analysis"]["top_self"]
                ]
                lines += ["", "Expensive cumulative subtrees (do not sum):", ""]
                lines += [
                    f'- {_cell(r["module"])}: {r["cumulative_us"]/1000:.3f} ms'
                    for r in detail["analysis"]["top_cumulative"]
                ]
                lines += ["", *[_cell(w) for w in detail["analysis"]["warnings"]]]
            else:
                phase_chart(detail["analysis"], output / chart)
                lines += [
                    "",
                    "| Span | Inclusive seconds | Derived exclusive seconds | State |",
                    "| --- | --- | --- | --- |",
                ]
                lines += [
                    f'| {_cell(s["name"])} | {s["inclusive_seconds"]} | {s["exclusive_seconds"]} | {_cell(s.get("state", "incomplete"))} |'
                    for s in detail["analysis"]["spans"]
                ]
                lines += [
                    "",
                    f'Incomplete spans: {detail["analysis"]["incomplete"]}. Unattributed intervals: {_cell(detail["analysis"]["unattributed_intervals"])}',
                ]
            lines += ["", f"![Diagnostic]({chart})"]
    (output / "report.md").write_text("\n".join(lines) + "\n")
    return summary
