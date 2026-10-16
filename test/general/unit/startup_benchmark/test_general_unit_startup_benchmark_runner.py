import dataclasses
import ssl

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

    original = signal.getsignal(signal.SIGALRM)
    with pytest.raises(TimeoutError), request_deadline(0.01):
        time.sleep(0.1)
    assert signal.getsignal(signal.SIGALRM) == original
    assert signal.getitimer(signal.ITIMER_REAL) == (0, 0)
