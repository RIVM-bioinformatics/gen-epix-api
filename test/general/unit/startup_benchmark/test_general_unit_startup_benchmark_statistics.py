import pytest

from scripts.startup_benchmark.statistics import summarize


def records(values):
    return [
        {"kind": "measured", "status": "success", "seconds": v, "cleanup": "ok"}
        for v in values
    ]


def test_nearest_rank_and_threshold():
    result = summarize(records(range(1, 31)))
    assert result["p90"] == 27
    assert result["p95"] == 29
    assert result["mean"] == result["median"] == 15.5
    assert result["margin"] == -14
    assert result["above_target"] == 15
    assert result["above_target_percent"] == 50
    assert result["evidence_valid"]
    assert not result["target_pass"]
    assert not summarize(records([15] * 30))["target_pass"]
    assert summarize(records([14] * 30))["target_pass"]


@pytest.mark.parametrize("values", [[], [1], [1, 2], [1] * 29])
def test_exploratory_and_empty(values):
    result = summarize(records(values))
    assert not result["evidence_valid"]
    assert not result["target_pass"]
    if not values:
        assert result["p95"] is result["mean"] is result["margin"] is None


@pytest.mark.parametrize("failure", ["timeout", "not_attempted", "identity_failure"])
def test_failures_invalidate_evidence(failure):
    runs = records([1] * 30)
    runs.append(
        {"kind": "measured", "status": failure, "seconds": None, "cleanup": "ok"}
    )
    assert not summarize(runs)["target_pass"]
    assert not summarize(records([1] * 30), False)["target_pass"]


def test_warmups_and_diagnostics_excluded():
    runs = records([1] * 30)
    runs += [
        {"kind": k, "status": "success", "seconds": 100, "cleanup": "ok"}
        for k in ("warmup", "imports", "phases")
    ]
    assert summarize(runs)["p95"] == 1
    runs[-1]["cleanup"] = "failed"
    assert not summarize(runs)["target_pass"]


def test_interrupted_complete_sample_is_not_valid_evidence():
    assert not summarize(records([1] * 30), series_completed=False)["target_pass"]
