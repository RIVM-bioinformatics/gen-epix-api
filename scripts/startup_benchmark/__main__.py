"""Expose benchmark, independent diagnostics, and offline report regeneration."""

import argparse
import dataclasses
import datetime
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from .diagnostics import parse_imports, parse_phases
from .metadata import capture, configuration_snapshot, file_fingerprints, fingerprint
from .models import (
    APPLICATIONS,
    IDP_MODES,
    REPOSITORY_MODES,
    ROOT,
    SCHEMA_VERSION,
    Artifact,
    Options,
    RunRecord,
)
from .reporting import generate, load_json, save_json
from .runner import child_environment, launch_command, run_once, tls_context


def parser() -> argparse.ArgumentParser:
    """Construct an explicit-mode CLI without importing application packages."""
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("benchmark", "diagnose"):
        command = sub.add_parser(name)
        command.add_argument("application", type=str.lower, choices=APPLICATIONS)
        command.add_argument(
            "--idp-mode", required=True, type=str.upper, choices=IDP_MODES
        )
        command.add_argument(
            "--repository-mode", required=True, type=str.upper, choices=REPOSITORY_MODES
        )
        command.add_argument(
            "--runs", type=int, default=30 if name == "benchmark" else 1
        )
        if name == "benchmark":
            command.add_argument("--warmups", type=int, default=0)
        else:
            command.set_defaults(warmups=0)
        for flag, default in (
            ("readiness-timeout", 60),
            ("poll-interval", 0.05),
            ("request-timeout", 0.25),
            ("settle-seconds", 1),
        ):
            command.add_argument("--" + flag, type=float, default=default)
        command.add_argument("--output", type=Path)
        tls = command.add_mutually_exclusive_group()
        tls.add_argument("--ca-file")
        tls.add_argument("--insecure", action="store_true")
        if name == "benchmark":
            command.add_argument("--check-target", action="store_true")
        else:
            command.add_argument(
                "--kind", choices=("imports", "phases", "both"), default="both"
            )
    report = sub.add_parser("report")
    report.add_argument("results", type=Path)
    report.add_argument("--diagnostics", type=Path)
    report.add_argument("--output", required=True, type=Path)
    return root


def execute(args: Any) -> int:
    """Persist each attempt and generate complete or partial reports.

    Returns:
        CLI exit status, including startup failures and requested target gating.

    Raises:
        ValueError: If configuration is incompatible with trustworthy measurement.
    """
    options = Options(
        APPLICATIONS[args.application],
        args.idp_mode,
        args.repository_mode,
        args.runs,
        args.warmups,
        args.readiness_timeout,
        args.poll_interval,
        args.request_timeout,
        args.settle_seconds,
        args.ca_file,
        args.insecure,
    )
    options.validate()
    if sys.version_info < (3, 14) or not sys.platform.startswith("linux"):
        raise ValueError("Startup benchmarking requires Python 3.14+ on Linux/WSL")
    env = dict(os.environ)
    if args.command == "benchmark" and (
        "importtime" in sys._xoptions
        or any(
            env.get(k)
            for k in (
                "PYTHONPROFILEIMPORTTIME",
                "COVERAGE_PROCESS_START",
                "COV_CORE_SOURCE",
                "COV_CORE_CONFIG",
                "COV_CORE_DATAFILE",
            )
        )
    ):
        raise ValueError(
            "Normal measurements refuse inherited import profiling or subprocess coverage"
        )
    tls_context(options)
    # Validate dictionary overrides before creating artifacts or processes.
    child_environment(env, options, "validation")
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    output = (
        args.output
        or ROOT
        / "test/output/startup_benchmark"
        / f"{args.application}-{stamp}-{uuid.uuid4().hex[:8]}"
    ).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if (output / "results.json").exists():
        raise ValueError("Output already contains results; choose a new directory")
    metadata = capture(options, env)
    data: Artifact = {
        "schema_version": SCHEMA_VERSION,
        "application": args.application,
        "command": args.command,
        "options": dataclasses.asdict(options),
        "metadata": metadata,
        "configuration_valid": True,
        "series_completed": False,
        "configuration_fingerprint": None,
        "records": [],
        "diagnostics": [],
        "commands": {},
        "configuration_changes": [],
    }
    kinds = (
        ["warmup"] * options.warmups + ["measured"] * options.runs
        if args.command == "benchmark"
        else [
            kind
            for kind in ("imports", "phases")
            if args.kind in (kind, "both")
            for _ in range(options.runs)
        ]
    )
    data["records"] = [
        dataclasses.asdict(RunRecord(i + 1, kind)) for i, kind in enumerate(kinds)
    ]
    status = 0
    save_json(output / "results.json", data)
    try:
        # Configuration preflight prevents debug mode from silently disabling identity.
        before = configuration_snapshot(
            options, env, output / "configuration-before.json"
        )
        if before["debug"]:
            raise ValueError(
                "debug=True omits nonce middleware; benchmark requires debug=False"
            )
        for i, kind in enumerate(kinds):
            current = file_fingerprints()
            if current != metadata["files"]:
                data["configuration_valid"] = False
                data["configuration_changes"].append(
                    {"before_run": i + 1, "files": current}
                )
                status = 1
                break
            record = run_once(options, output, i + 1, kind, env)
            data["records"][i] = dataclasses.asdict(record)
            data["commands"][str(i + 1)] = launch_command(
                options, kind, Path(record.phases) if record.phases else None
            )
            if kind in ("imports", "phases") and record.stderr:
                analysis = (
                    parse_imports(Path(record.stderr).read_text(errors="replace"))
                    if kind == "imports"
                    else parse_phases(
                        (
                            Path(record.phases).read_text()
                            if record.phases and Path(record.phases).exists()
                            else ""
                        ),
                        record.started_ns,
                        record.ready_ns,
                    )
                )
                data["diagnostics"].append(
                    {"kind": kind, "run": i + 1, "analysis": analysis}
                )
            save_json(output / "results.json", data)
            print(
                f"{kind} {i+1}/{len(kinds)}: {record.status}, seconds={record.seconds}, cleanup={record.cleanup}",
                flush=True,
            )
            if record.status != "success":
                status = 1
            if record.status == "interrupted":
                status = 130
                break
            if record.status in (
                "occupied_port",
                "identity_failure",
            ) or record.cleanup not in ("ok", "not_needed"):
                data["configuration_valid"] = False
                break
            time.sleep(options.settle_seconds)
    except KeyboardInterrupt:
        status = 130
    except (ValueError, subprocess.TimeoutExpired) as error:
        data["configuration_valid"] = False
        data["configuration_error"] = str(error)
        status = 2
    finally:
        try:
            after = configuration_snapshot(
                options, env, output / "configuration-after.json"
            )
            data["configuration"] = after
            data["configuration_fingerprint"] = fingerprint(
                {
                    "configuration": after,
                    "files": metadata["files"],
                    "environment": metadata["environment"],
                    "modes": [options.idp_mode, options.repository_mode],
                }
            )
            if (
                "before" not in locals()
                or before != after
                or file_fingerprints() != metadata["files"]
            ):
                data["configuration_valid"] = False
                data["configuration_changes"].append({"after_series": True})
                if status == 0:
                    status = 1
        except (ValueError, subprocess.TimeoutExpired) as error:
            data["configuration_valid"] = False
            data["configuration_error"] = str(error)
            if status == 0:
                status = 1
        except KeyboardInterrupt:
            data["configuration_valid"] = False
            status = 130
        data["series_completed"] = status not in (2, 130) and all(
            r["status"] != "not_attempted" for r in data["records"]
        )
        data["series_exit_code"] = status
        print(generate(data, output), flush=True)
        print(f"Report: {output / 'report.md'}", flush=True)
    if (
        getattr(args, "check_target", False)
        and not data["statistics"]["target_pass"]
        and status == 0
    ):
        status = 1
    return status


def main() -> int:
    """Dispatch the CLI with stable configuration and interruption exit codes."""
    args = parser().parse_args()
    try:
        if args.command == "report":
            print(
                generate(
                    load_json(args.results),
                    args.output,
                    load_json(args.diagnostics) if args.diagnostics else None,
                )
            )
            return 0
        return execute(args)
    except KeyboardInterrupt:
        return 130
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
