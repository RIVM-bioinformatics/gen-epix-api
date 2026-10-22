"""Calculate empirical percentiles and assess failure-aware startup evidence."""

import math
import statistics


def summarize(
    records: list[dict], configuration_valid: bool = True, series_completed: bool = True
) -> dict:
    """Calculate statistics over successful measured runs and assess the target.

    Args:
        records: Run records, including warmups and unattempted measurements.
        configuration_valid: Whether configuration and cleanup evidence is valid.
        series_completed: Whether orchestration finished without interruption.

    Returns:
        Statistics and separate observed-performance and evidence assessments.
    """
    measured = [r for r in records if r["kind"] == "measured"]
    values = sorted(r["seconds"] for r in measured if r["status"] == "success")
    n = len(values)
    p95 = values[math.ceil(0.95 * n) - 1] if n else None
    failures = sum(r["status"] not in ("success", "not_attempted") for r in measured)
    unattempted = sum(r["status"] == "not_attempted" for r in measured)
    valid = (
        series_completed
        and n >= 30
        and not failures
        and not unattempted
        and configuration_valid
        and all(r["status"] == "success" and r["cleanup"] == "ok" for r in records)
    )
    above = sum(v > 15 for v in values)
    return {
        "requested": len(measured),
        "attempted": len(measured) - unattempted,
        "successes": n,
        "failures": failures,
        "unattempted": unattempted,
        "mean": statistics.mean(values) if n else None,
        "median": statistics.median(values) if n else None,
        "minimum": min(values) if n else None,
        "maximum": max(values) if n else None,
        "p90": values[math.ceil(0.9 * n) - 1] if n else None,
        "p95": p95,
        "target_seconds": 15.0,
        "margin": 15 - p95 if n else None,
        "above_target": above,
        "above_target_percent": 100 * above / n if n else None,
        "observed_below_target": p95 < 15 if n else None,
        "evidence_valid": valid,
        "target_pass": valid and p95 < 15,
        "statistics_population": "successful measured runs",
    }
