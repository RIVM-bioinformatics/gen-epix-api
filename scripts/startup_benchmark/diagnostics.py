"""Parse independent import traces and classify captured phase spans."""

import re

_IMPORT = re.compile(r"^import time:\s*(\d+)\s*\|\s*(\d+)\s*\|( +)(\S.*?)\s*$")


def parse_imports(stderr: str) -> dict:
    """Reconstruct postorder import occurrences without summing cumulative costs.

    Returns:
        Occurrences, observed chains, ranked costs, and malformed-tree warnings.
    """
    records, warnings, pending = [], [], []
    for line in stderr.splitlines():
        match = _IMPORT.match(line)
        if not match:
            if line.startswith("import time:") and "self [us]" not in line:
                warnings.append("Malformed import record: " + line)
            continue
        self_us, cumulative_us, spaces, module = match.groups()
        depth = (len(spaces) - 1) // 2
        if len(spaces) % 2 != 1:
            warnings.append("Unexpected import indentation: " + module)
        index = len(records)
        record = {
            "id": index,
            "module": module,
            "depth": depth,
            "self_us": int(self_us),
            "cumulative_us": int(cumulative_us),
            "parent": None,
        }
        children = []
        while pending and records[pending[-1]]["depth"] > depth:
            child = pending.pop()
            if records[child]["depth"] != depth + 1:
                warnings.append(
                    "Missing intermediate parent: " + records[child]["module"]
                )
            else:
                records[child]["parent"] = index
                children.append(child)
        record["children"] = list(reversed(children))
        records.append(record)
        pending.append(index)
    for index in pending:
        if records[index]["depth"]:
            warnings.append("Incomplete root: " + records[index]["module"])
    for record in records:
        chain = [record["module"]]
        parent = record["parent"]
        while parent is not None:
            chain.append(records[parent]["module"])
            parent = records[parent]["parent"]
        record["chain"] = list(reversed(chain))
    return {
        "records": records,
        "top_self": sorted(records, key=lambda r: (-r["self_us"], r["id"]))[:20],
        "top_cumulative": sorted(records, key=lambda r: (-r["cumulative_us"], r["id"]))[
            :20
        ],
        "warnings": warnings,
        "interpretation": "Observed execution chains, not a complete dependency graph; cumulative times must not be summed.",
    }


def analyze_phases(
    events: list[dict], started_ns: int | None = None, ready_ns: int | None = None
) -> dict:
    """Pair span events and derive exclusive times only from synchronous children."""
    starts = {e["id"]: dict(e) for e in events if e["event"] == "start"}
    for event in events:
        if event["event"] == "end" and event["id"] in starts:
            starts[event["id"]].update(end_ns=event["time_ns"], state=event["state"])
    spans = list(starts.values())
    for span in spans:
        span["inclusive_seconds"] = (
            (span["end_ns"] - span["time_ns"]) / 1e9 if "end_ns" in span else None
        )
        span["exclusive_seconds"] = None
        children = [s for s in spans if s["parent"] == span["id"]]
        if (
            span["inclusive_seconds"] is not None
            and not span["async"]
            and all(
                "end_ns" in s
                and not s["async"]
                and span["time_ns"] <= s["time_ns"] <= s["end_ns"] <= span["end_ns"]
                for s in children
            )
        ):
            intervals = sorted((s["time_ns"], s["end_ns"]) for s in children)
            covered, end = 0, span["time_ns"]
            for left, right in intervals:
                covered += max(0, right - max(left, end))
                end = max(end, right)
            span["exclusive_seconds"] = max(
                0, span["inclusive_seconds"] - covered / 1e9
            )
        span["classification"] = (
            "direct inclusive; derived synchronous exclusive"
            if span["exclusive_seconds"] is not None
            else "direct inclusive; exclusive unavailable"
        )
    complete = sorted((s["time_ns"], s["end_ns"]) for s in spans if "end_ns" in s)
    gaps, end = [], (
        started_ns if started_ns is not None else (complete[0][0] if complete else 0)
    )
    for left, right in complete:
        if ready_ns is not None:
            left, right = min(left, ready_ns), min(right, ready_ns)
        if left > end:
            gaps.append({"start_ns": end, "end_ns": left})
        end = max(end, right)
    if ready_ns is not None and ready_ns > end:
        gaps.append({"start_ns": end, "end_ns": ready_ns})
    return {
        "spans": spans,
        "measurement_start_ns": started_ns,
        "verified_response_ns": ready_ns,
        "unattributed_intervals": gaps,
        "incomplete": sum("end_ns" not in s for s in spans),
        "interpretation": "Instrumented run; preparation changes import order. Spans overlap and do not partition normal startup.",
    }


def parse_phases(
    stream: str, started_ns: int | None = None, ready_ns: int | None = None
) -> dict:
    """Recover phase evidence from a stream that may end in a truncated event."""
    import json

    events, warnings = [], []
    for number, line in enumerate(stream.splitlines(), 1):
        try:
            event = json.loads(line)
            required = {"event", "id", "time_ns"}
            if event.get("event") == "start":
                required |= {"parent", "name", "label", "async"}
            elif event.get("event") == "end":
                required.add("state")
            else:
                raise ValueError("Unknown event type")
            if not required <= event.keys():
                raise ValueError("Missing event fields")
            events.append(event)
        except (ValueError, AttributeError) as error:
            warnings.append(f"Malformed phase event at line {number}: {error}")
    result = analyze_phases(events, started_ns, ready_ns)
    result["warnings"] = warnings
    return result
