"""Test that the client side of gen_epix can be imported without server packages.

A consumer that only calls the applications over HTTP installs gen_epix without
the ``server`` extra. Each test runs in a fresh interpreter in which importing
any of the server-only packages fails, as it would in such an installation.
"""

import subprocess
import sys
import textwrap

import pytest

from gen_epix.util import get_package_root

SERVER_ONLY_PACKAGES = (
    "fastapi",
    "starlette",
    "slowapi",
    "sqlalchemy",
    "sqlalchemy_utils",
    "alembic",
    "gunicorn",
    "uvicorn",
    "multipart",
    "python_multipart",
    "cryptography",
    "oauthlib",
)

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


def test_server_side_export_requires_server_packages() -> None:
    """Ensure that the blocker works, by importing something that needs the server."""
    with pytest.raises(pytest.fail.Exception, match="server-only package imported"):
        _run_without_server_packages("from gen_epix import CasedbAppComposer")
