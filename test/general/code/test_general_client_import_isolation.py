"""Test that the client side of gen_epix can be imported without server packages.

A consumer that only calls the applications over HTTP installs gen_epix without
the ``server`` extra. Each test runs in a fresh interpreter in which importing
any of the server-only packages fails, as it would in such an installation.

Uses only pytest besides gen_epix's base dependencies, so the ``client-install``
CI job also runs it in a real installation without the extra.
"""

import importlib.metadata
import re
import subprocess
import sys
import textwrap
import tomllib

import pytest

from gen_epix.util import get_package_root

# Import names that are not those of a distribution in the server extra
_OTHER_SERVER_ONLY_PACKAGES = (
    # Installed by fastapi[standard]
    "uvicorn",
    # Not in the server extra either: a development dependency
    "pyinstrument",
)


def _normalize(distribution_name: str) -> str:
    return re.sub(r"[-_.]+", "-", distribution_name).lower()


def _get_server_only_packages() -> tuple[str, ...]:
    """Return the import names of the server extra's packages that are installed.

    In an installation without the extra none of them are installed, and none
    need to be blocked.
    """
    project = tomllib.loads(
        (get_package_root() / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    server = {
        _normalize(re.split(r"[\[<>=!~;\s]", x.strip(), maxsplit=1)[0])
        for x in project["optional-dependencies"]["server"]
    }
    installed = importlib.metadata.packages_distributions()
    return tuple(
        sorted(
            {
                package
                for package, distributions in installed.items()
                if any(_normalize(x) in server for x in distributions)
            }
            | set(_OTHER_SERVER_ONLY_PACKAGES)
        )
    )


SERVER_ONLY_PACKAGES = _get_server_only_packages()

_BLOCK_SERVER_ONLY_PACKAGES = f"""
import sys


class _Blocker:
    BLOCKED = {SERVER_ONLY_PACKAGES!r}

    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in self.BLOCKED:
            # As if the package is not installed, which is also what packages that
            # treat one of these as optional (pyjwt and cryptography) check for
            raise ModuleNotFoundError(f"server-only package imported: {{name}}")
        return None


sys.meta_path.insert(0, _Blocker())
"""


def _run_without_server_packages(code: str) -> None:
    """Run code in a fresh interpreter that cannot import server-only packages."""
    result = subprocess.run(
        [sys.executable, "-c", _BLOCK_SERVER_ONLY_PACKAGES + textwrap.dedent(code)],
        cwd=get_package_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.fail(result.stderr[-4000:])


def test_import_gen_epix_loads_nothing() -> None:
    """Ensure that importing the facade does not import what it exports."""
    _run_without_server_packages("""
        import gen_epix

        loaded = sorted(
            x for x in sys.modules if x.startswith("gen_epix.") and x != "gen_epix._lazy"
        )
        assert not loaded, loaded
        """)


@pytest.mark.parametrize(
    "client_name", ["CasedbClient", "SeqdbClient", "OmopdbClient", "CommondbClient"]
)
def test_import_client_without_server_packages(client_name: str) -> None:
    """Ensure that each remote client can be imported on its own."""
    _run_without_server_packages(f"""
        from gen_epix import {client_name}

        assert isinstance({client_name}, type)
        """)


def test_import_client_side_api_without_server_packages() -> None:
    """Ensure that what a client works with can be imported together."""
    _run_without_server_packages("""
        from gen_epix import (
            CASEDB_DOMAIN,
            COMMONDB_DOMAIN,
            NULL_ID,
            OMOPDB_DOMAIN,
            SEQDB_DOMAIN,
            CasedbClient,
            CommondbClient,
            OmopdbClient,
            SeqdbClient,
            casedb_command,
            casedb_enum,
            casedb_model,
            commondb_command,
            commondb_enum,
            commondb_model,
            etl,
            etl_model,
            exc,
            fastapp,
            filter,
            literal,
            omopdb_command,
            omopdb_enum,
            omopdb_model,
            seqdb_command,
            seqdb_enum,
            seqdb_model,
            util,
        )
        from gen_epix.casedb import api as casedb_api
        from gen_epix.commondb import api as commondb_api
        from gen_epix.omopdb import api as omopdb_api
        from gen_epix.seqdb import api as seqdb_api

        fastapp.App, fastapp.Client, fastapp.Command, fastapp.DictRepository
        fastapp.services.auth.OauthTokenClient
        """)


def test_server_only_packages_follow_server_extra() -> None:
    """Ensure that the blocked packages include the server extra's, if installed."""
    try:
        importlib.metadata.version("numpy")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("installed without the server extra")
    assert {"Bio", "cachetools", "fire", "numpy", "scipy", "tomli_w"} <= set(
        SERVER_ONLY_PACKAGES
    )


def test_server_side_export_requires_server_packages() -> None:
    """Ensure that the blocker works, by importing something that needs the server.

    Without the server extra installed, the blocker does not know the package and
    the import fails with the usual message.
    """
    with pytest.raises(
        pytest.fail.Exception,
        match=r"server-only package imported|No module named",
    ):
        _run_without_server_packages("from gen_epix import CasedbAppComposer")
