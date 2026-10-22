import dataclasses
import subprocess
import sys

import pytest

from scripts.startup_benchmark.__main__ import parser
from scripts.startup_benchmark.models import (
    APPLICATIONS,
    IDP_MODES,
    REPOSITORY_MODES,
    Options,
)
from scripts.startup_benchmark.runner import child_environment, launch_command


def test_descriptor_and_modes_match_launcher():
    from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
    from run import Run

    assert set(IDP_MODES) == set(DevIdpConfig.__members__)
    assert set(REPOSITORY_MODES) == set(DevRepositoryConfig.__members__)
    for name, descriptor in APPLICATIONS.items():
        actual = Run.APP_URI[AppType[name.upper()]]
        assert descriptor.port == actual["port"]
        assert descriptor.target == actual["app"]
        assert descriptor.prefix == name.upper()


def test_entrypoint_has_no_application_imports():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            'import sys; import scripts.startup_benchmark.__main__; assert not any(k == "gen_epix" or k.startswith("gen_epix.") for k in sys.modules)',
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["benchmark", "unknown"],
        ["benchmark", "seqdb"],
        ["benchmark", "seqdb", "--idp-mode", "BAD", "--repository-mode", "DICT_EMPTY"],
    ],
)
def test_cli_rejects_invalid_selection(arguments):
    with pytest.raises(SystemExit) as error:
        parser().parse_args(arguments)
    assert error.value.code == 2


def test_cli_normalizes_and_launches():
    args = parser().parse_args(
        ["benchmark", "SeQdB", "--idp-mode", "none", "--repository-mode", "dict_empty"]
    )
    assert args.application == "seqdb"
    options = Options(
        APPLICATIONS[args.application], args.idp_mode, args.repository_mode
    )
    assert launch_command(options) == [
        sys.executable,
        "run.py",
        "api",
        "seqdb",
        "NONE",
        "DICT_EMPTY",
        "--noreload",
    ]
    assert launch_command(options, "imports")[1:3] == ["-X", "importtime"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("runs", 0),
        ("warmups", -1),
        ("poll_interval", 0),
        ("request_timeout", float("nan")),
        ("readiness_timeout", -1),
        ("settle_seconds", float("inf")),
        ("idp_mode", "invalid"),
    ],
)
def test_options_validation(field, value):
    options = dataclasses.replace(
        Options(APPLICATIONS["seqdb"], "NONE", "DICT_EMPTY"), **{field: value}
    )
    with pytest.raises(ValueError):
        options.validate()


def test_headers_preserved_and_input_not_mutated():
    options = Options(APPLICATIONS["seqdb"], "NONE", "DICT_EMPTY")
    base = {
        "SEQDB_API__HTTP_HEADER__GENERAL": '@json {"X-Existing": "yes", "x-startup-benchmark-instance": "old"}',
        "WEB_CONCURRENCY": "9",
    }
    actual = child_environment(base, options, "fresh")
    assert "yes" in actual["SEQDB_API__HTTP_HEADER__GENERAL"]
    assert "fresh" in actual["SEQDB_API__HTTP_HEADER__GENERAL"]
    assert "old" not in actual["SEQDB_API__HTTP_HEADER__GENERAL"]
    assert actual["WEB_CONCURRENCY"] == "1"
    assert base["WEB_CONCURRENCY"] == "9"
    with pytest.raises(ValueError):
        child_environment({"SEQDB_API__HTTP_HEADER__GENERAL": "@json []"}, options, "x")
