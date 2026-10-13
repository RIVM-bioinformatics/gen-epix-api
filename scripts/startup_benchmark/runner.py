"""Launch isolated process groups and verify instance-specific health readiness."""

import errno
import http.client
import json
import os
import signal
import socket
import ssl
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

from .models import HEADER, ROOT, Options, RunRecord


def child_environment(
    base: dict[str, str], options: Options, nonce: str
) -> dict[str, str]:
    """Copy caller overrides and merge the nonce into general response headers.

    Raises:
        ValueError: If the supplied general-header override is not a dictionary.
    """
    env = dict(base)
    key = f"{options.application.prefix}_API__HTTP_HEADER__GENERAL"
    headers = {}
    if key in env:
        from dynaconf.utils.parse_conf import parse_conf_data

        headers = parse_conf_data(env[key], tomlfy=True)
        if not isinstance(headers, dict):
            raise ValueError(f"{key} must be a dictionary")
    headers = {k: v for k, v in headers.items() if k.lower() != HEADER.lower()}
    headers[HEADER] = nonce
    env[key] = "@json " + json.dumps(headers)
    env["WEB_CONCURRENCY"] = "1"
    return env


def launch_command(
    options: Options, kind: str = "measured", phases: Path | None = None
) -> list[str]:
    """Build the existing reload-disabled launcher arguments."""
    command = [sys.executable]
    if kind == "imports":
        command += ["-X", "importtime"]
    if kind == "phases":
        command += ["-m", "scripts.startup_benchmark.bootstrap", str(phases)]
    else:
        command += ["run.py"]
    return command + [
        "api",
        options.application.name,
        options.idp_mode,
        options.repository_mode,
        "--noreload",
    ]


def tls_context(options: Options) -> ssl.SSLContext | None:
    """Select launcher-compatible TLS and reject incomplete certificate pairs.

    Raises:
        ValueError: If only one launcher certificate file exists.
    """
    key, cert = ROOT / "cert/key.pem", ROOT / "cert/cert.pem"
    if key.exists() != cert.exists():
        raise ValueError("Launcher TLS requires both cert/key.pem and cert/cert.pem")
    if not key.exists():
        return None
    if options.insecure:
        return ssl._create_unverified_context()
    return ssl.create_default_context(cafile=options.ca_file)


def port_available(port: int) -> bool:
    """Check the wildcard listener using Uvicorn's address-reuse behavior.

    Raises:
        OSError: If the listener cannot be checked for a reason other than use.
    """
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", port))
            return True
        except OSError as error:
            if error.errno == errno.EADDRINUSE:
                return False
            raise


@contextmanager
def request_deadline(seconds: float):
    """Bound the complete blocking HTTP exchange, including slow trickle reads.

    This Linux CLI helper runs on the main thread and restores any existing
    SIGALRM handler and timer. Socket timeouts alone bound idle time, not an
    entire response whose peer keeps sending small packets.

    Raises:
        TimeoutError: If the whole request exceeds its allowed duration.
    """

    def expired(signum, frame):
        """Stop an overdue HTTP exchange.

        Raises:
            TimeoutError: Whenever the request timer fires.
        """
        raise TimeoutError("HTTP request deadline exceeded")

    previous_handler = signal.getsignal(signal.SIGALRM)
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    started = time.monotonic()
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
        if previous_timer[0]:
            signal.setitimer(
                signal.ITIMER_REAL,
                max(0.000001, previous_timer[0] - (time.monotonic() - started)),
                previous_timer[1],
            )


def cleanup(process: subprocess.Popen, grace: float = 10) -> bool:
    """Terminate the entire child session, escalate, and reap the direct child.

    Linux zombie descendants no longer own resources and count as terminated.
    Live descendants must disappear before the next run can proceed.
    """

    def alive() -> bool:
        for entry in Path("/proc").glob("[0-9]*/stat"):
            try:
                fields = entry.read_text().rsplit(")", 1)[1].split()
                if int(fields[2]) == process.pid and fields[0] != "Z":
                    return True
            except (OSError, ValueError, IndexError):
                continue
        return False

    for sig, wait in ((signal.SIGTERM, grace), (signal.SIGKILL, 2)):
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + wait
        while time.monotonic() < deadline:
            process.poll()
            if not alive():
                process.wait(timeout=2)
                return True
            time.sleep(0.02)
    process.poll()
    return process.returncode is not None and not alive()


def run_once(
    options: Options,
    directory: Path,
    index: int,
    kind: str,
    base_env: dict[str, str],
    command: list[str] | None = None,
) -> RunRecord:
    """Measure launch through the first verified response, then clean up.

    Args:
        options: Polling and application settings.
        directory: Existing output directory for per-attempt logs.
        index: Stable run index.
        kind: Measurement, warmup, or diagnostic category.
        base_env: Frozen caller environment.
        command: Optional controlled-process command used by lifecycle tests.

    Returns:
        A record retaining launch, readiness, interruption, and cleanup outcomes.
    """
    record = RunRecord(index, kind)
    nonce = uuid.uuid4().hex
    env = child_environment(base_env, options, nonce)
    context = tls_context(options)
    record.stdout = str(directory / f"{kind}-{index}.stdout.log")
    record.stderr = str(directory / f"{kind}-{index}.stderr.log")
    record.phases = (
        str(directory / f"{kind}-{index}.phases.jsonl") if kind == "phases" else None
    )
    if not port_available(options.application.port):
        record.status = "occupied_port"
        return record
    process = None
    connection_type = (
        http.client.HTTPSConnection if context else http.client.HTTPConnection
    )
    argv = command or launch_command(
        options, kind, Path(record.phases) if record.phases else None
    )
    with open(record.stdout, "wb") as out, open(record.stderr, "wb") as err:
        try:
            start = time.perf_counter_ns()
            process = subprocess.Popen(
                argv,
                cwd=ROOT,
                env=env,
                stdout=out,
                stderr=err,
                start_new_session=True,
            )
            record.pid = process.pid
            record.started_ns = start
            deadline = start / 1e9 + options.readiness_timeout
            record.status = "timeout"
            while time.perf_counter() < deadline:
                if process.poll() is not None:
                    record.status = "premature_exit"
                    break
                remaining = deadline - time.perf_counter()
                if remaining <= 0:
                    break
                kwargs = {"timeout": min(options.request_timeout, remaining)}
                if context:
                    kwargs["context"] = context
                connection = connection_type(
                    "127.0.0.1", options.application.port, **kwargs
                )
                try:
                    with request_deadline(
                        min(
                            options.request_timeout,
                            max(0.000001, deadline - time.perf_counter()),
                        )
                    ):
                        connection.request("GET", "/v1/health")
                        response = connection.getresponse()
                        response.read()
                        completed = time.perf_counter_ns()
                    if response.status == 200:
                        if response.getheader(HEADER) != nonce:
                            record.status = "identity_failure"
                        elif process.poll() is not None:
                            record.status = "premature_exit"
                        elif completed / 1e9 <= deadline:
                            record.status = "success"
                            record.ready_ns = completed
                            record.seconds = (completed - start) / 1e9
                        break
                except (OSError, http.client.HTTPException) as error:
                    record.error = type(error).__name__
                finally:
                    connection.close()
                time.sleep(
                    min(options.poll_interval, max(0, deadline - time.perf_counter()))
                )
        except KeyboardInterrupt:
            record.status = "interrupted"
        except OSError as error:
            record.status = "launch_failure"
            record.error = str(error)
        finally:
            if process is not None:
                # Ignore repeated Ctrl-C only while guaranteeing process cleanup.
                previous_interrupt = signal.signal(signal.SIGINT, signal.SIG_IGN)
                try:
                    record.cleanup = "ok" if cleanup(process) else "failed"
                except (OSError, subprocess.TimeoutExpired) as error:
                    record.cleanup = "failed"
                    record.error = str(error)
                finally:
                    signal.signal(signal.SIGINT, previous_interrupt)
                record.exit_code = process.returncode
    if record.cleanup == "ok" and not port_available(options.application.port):
        record.cleanup = "port_still_occupied"
    return record
