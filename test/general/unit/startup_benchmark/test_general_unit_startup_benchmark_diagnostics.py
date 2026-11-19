import asyncio
import inspect
import json

import pytest

from scripts.startup_benchmark.bootstrap import Recorder
from scripts.startup_benchmark.diagnostics import analyze_phases, parse_imports


def test_postorder_and_repeated_modules():
    parsed = parse_imports(
        "noise\nimport time: self [us] | cumulative | imported package\nimport time: 10 | 10 |     leaf\nimport time: 20 | 30 |   branch\nimport time: 5 | 5 |   branch\nimport time: 7 | 42 | root\n"
    )
    assert not parsed["warnings"]
    assert parsed["records"][0]["chain"] == ["root", "branch", "leaf"]
    assert len([r for r in parsed["records"] if r["module"] == "branch"]) == 2
    assert parsed["top_self"][0]["self_us"] == 20
    assert parsed["top_cumulative"][0]["cumulative_us"] == 42


def test_malformed_and_incomplete():
    parsed = parse_imports(
        "import time: garbage\nimport time: 1 | 1 |     orphan\nimport time: 2 | 3 | root\nimport time: 1 | 1 |   incomplete"
    )
    assert len(parsed["warnings"]) == 3
    assert parsed["records"][0]["parent"] is None


def test_wrappers_preserve_nested_async_errors_and_signatures(tmp_path):
    recorder = Recorder(tmp_path / "events")

    def child(x: int = 3):
        return x + 1

    wrapped = recorder.wrap(child, "child")
    parent = recorder.wrap(lambda: wrapped(4), "parent")
    assert inspect.signature(child) == inspect.signature(wrapped)
    assert parent() == 5

    async def asynchronous():
        await asyncio.sleep(0)
        return wrapped()

    assert asyncio.run(recorder.wrap(asynchronous, "async")()) == 4

    def broken():
        raise LookupError("expected")

    with pytest.raises(LookupError):
        recorder.wrap(broken, "broken")()
    recorder.stream.close()
    analysis = analyze_phases(
        [json.loads(line) for line in (tmp_path / "events").read_text().splitlines()]
    )
    assert analysis["spans"][1]["parent"] == analysis["spans"][0]["id"]
    assert analysis["spans"][0]["exclusive_seconds"] >= 0
    assert analysis["spans"][2]["exclusive_seconds"] is None
    assert analysis["spans"][-1]["state"] == "error"
    assert analysis["incomplete"] == 0


def test_classmethod_and_hook_validation(tmp_path):
    class Owner:
        @classmethod
        def call(cls, value):
            return cls, value

    recorder = Recorder(tmp_path / "events")
    recorder.hook(Owner, "call", "class method")
    assert Owner.call(2) == (Owner, 2)
    with pytest.raises(RuntimeError):
        recorder.hook(Owner, "missing", "bad")
    recorder.stream.close()


def test_incomplete_span():
    analysis = analyze_phases(
        [
            {
                "event": "start",
                "id": 1,
                "parent": None,
                "name": "x",
                "label": None,
                "async": False,
                "time_ns": 1,
            }
        ]
    )
    assert analysis["incomplete"] == 1
    assert analysis["spans"][0]["exclusive_seconds"] is None


def test_phase_stream_retains_incomplete_evidence():
    from scripts.startup_benchmark.diagnostics import parse_phases

    event = {
        "event": "start",
        "id": 1,
        "parent": None,
        "name": "started",
        "label": "seqdb",
        "async": False,
        "time_ns": 1,
    }
    result = parse_phases(json.dumps(event) + '\n{"event":')
    assert result["incomplete"] == 1
    assert len(result["warnings"]) == 1


def test_unattributed_launch_and_response_intervals():
    events = [
        {
            "event": "start",
            "id": 1,
            "parent": None,
            "name": "span",
            "label": "seqdb",
            "async": False,
            "time_ns": 20,
        },
        {"event": "end", "id": 1, "time_ns": 80, "state": "complete"},
    ]
    result = analyze_phases(events, started_ns=10, ready_ns=100)
    assert result["unattributed_intervals"] == [
        {"start_ns": 10, "end_ns": 20},
        {"start_ns": 80, "end_ns": 100},
    ]
