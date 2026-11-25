"""Test helpers for commondb test utilities."""

from types import SimpleNamespace

from gen_epix.commondb.test.util import parse_stats


def test_parse_stats_uses_cumulative_time_per_call() -> None:
    """Store the profiler's per-call value rather than cumulative total."""
    profile = SimpleNamespace(
        ncalls="2",
        tottime=0.4,
        percall_tottime=0.2,
        cumtime=1.6,
        percall_cumtime=0.8,
        file_name="module.py",
        line_number=12,
    )
    stats = SimpleNamespace(
        get_stats_profile=lambda: SimpleNamespace(func_profiles={"function": profile})
    )
    rows: list[dict] = []

    parse_stats(rows, stats, run_id="run-1")

    assert rows[0]["cumulative_time"] == 1.6
    assert rows[0]["cumulative_time_per_call"] == 0.8
    assert rows[0]["run_id"] == "run-1"
