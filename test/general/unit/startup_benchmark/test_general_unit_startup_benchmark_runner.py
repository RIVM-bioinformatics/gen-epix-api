import dataclasses
import ssl
from collections.abc import Callable
from typing import cast

import pytest

from scripts.startup_benchmark.models import APPLICATIONS, Options
from scripts.startup_benchmark.runner import tls_context


def test_tls_selection(tmp_path, monkeypatch):
    from scripts.startup_benchmark import runner

    monkeypatch.setattr(runner, "ROOT", tmp_path)
    options = Options(APPLICATIONS["seqdb"], "NONE", "DICT_EMPTY")
    assert tls_context(options) is None
    (tmp_path / "cert").mkdir()
    (tmp_path / "cert/key.pem").touch()
    with pytest.raises(ValueError):
        tls_context(options)
    (tmp_path / "cert/cert.pem").touch()
    context = tls_context(dataclasses.replace(options, insecure=True))
    assert context.verify_mode == ssl.CERT_NONE
    called = []
    monkeypatch.setattr(
        ssl,
        "create_default_context",
        lambda **kwargs: called.append(kwargs) or "verified",
    )
    assert tls_context(dataclasses.replace(options, ca_file="ca.pem")) == "verified"
    assert called == [{"cafile": "ca.pem"}]


def test_request_deadline_restores_signal_handler():
    import signal
    import time

    from scripts.startup_benchmark.runner import request_deadline

    signal_api = vars(signal)
    sigalrm = signal_api.get("SIGALRM")
    itimer_real = signal_api.get("ITIMER_REAL")
    getsignal = signal_api.get("getsignal")
    getitimer = signal_api.get("getitimer")
    setitimer = signal_api.get("setitimer")
    if any(
        value is None
        for value in (sigalrm, itimer_real, getsignal, getitimer, setitimer)
    ):
        pytest.skip("request deadlines use POSIX interval timers")
    getsignal = cast(Callable[..., object], getsignal)
    getitimer = cast(Callable[..., object], getitimer)

    original = getsignal(sigalrm)
    with pytest.raises(TimeoutError), request_deadline(0.01):
        time.sleep(0.1)
    assert getsignal(sigalrm) == original
    assert getitimer(itimer_real) == (0, 0)
