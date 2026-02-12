import logging
import time
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from test.end_to_end.casedb_seqdb_connection.envvar import (
    set_envvar as set_environment_variables,
)
from test.test_client.enum import ServerType
from test.test_client.server_manager import ServerManager

import pytest

from gen_epix.casedb.api.router import create_routers as casedb_create_routers
from gen_epix.casedb.domain import enum as casedb_enum
from gen_epix.casedb.env import AppComposer as CasedbAppComposer
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.enum import AppType
from gen_epix.omopdb.api.router import create_routers as omopdb_create_routers
from gen_epix.omopdb.domain import enum as omopdb_enum
from gen_epix.omopdb.env import AppComposer as OmopdbAppComposer
from gen_epix.seqdb.api.router import create_routers as seqdb_create_routers
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.env import AppComposer as SeqdbAppComposer

SSL_CERTFILE = Path("cert/cert.pem").absolute().as_posix()
SSL_KEYFILE = Path("cert/key.pem").absolute().as_posix()

# Set environment variables for casedb, seqdb, and omopdb
set_environment_variables()


@contextmanager
def oauth_server() -> Generator[ServerManager, None, None]:
    """Start OAuth server and create CASEDB_FOR_SEQDB client."""
    with ServerManager(
        service=ServerType.OAUTH,
        port=9000,
        ssl_keyfile=SSL_KEYFILE,
        ssl_certfile=SSL_CERTFILE,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start OAuth server")

        # Add the CASEDB_FOR_SEQDB client
        success = server.add_client(
            client_id="CASEDB_FOR_SEQDB",
            client_secret="CASEDB_FOR_SEQDB_CLIENT_SECRET",
            audience="SEQDB",
            scopes=["openid", "profile", "aud"],
        )
        if not success:
            pytest.fail("Failed to add CASEDB_FOR_SEQDB client")

        yield server


@contextmanager
def omopdb_server(use_dict_repository: bool) -> Generator[ServerManager, None, None]:
    """Start OmopDB server"""

    omopdb_app_cfg = AppCfg(
        AppType.OMOPDB,
        omopdb_enum.ServiceType,
        (
            omopdb_enum.RepositoryType.DICT
            if use_dict_repository
            else omopdb_enum.RepositoryType.SA_SQL
        ),
        log_setup=True,
    )
    omopdb_app_composer = OmopdbAppComposer(omopdb_app_cfg, log_setup=True)
    omopdb_app = omopdb_app_composer.app
    omopdb_fastapi_app = create_fast_api(
        app=omopdb_app,
        create_routers_fn=omopdb_create_routers,
        app_id=omopdb_app_composer.app.generate_id(),
        setup_logger=omopdb_app_cfg.setup_logger,
        api_logger=omopdb_app_cfg.api_logger,
        debug=False,
    )
    with ServerManager(
        service=ServerType.OMOPDB,
        app=omopdb_fastapi_app,
        host="127.0.0.1",
        port=8002,
        ssl_certfile=SSL_CERTFILE,
        ssl_keyfile=SSL_KEYFILE,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start OmopDB server")
        yield server


@contextmanager
def seqdb_server(use_dict_repository: bool) -> Generator[ServerManager, None, None]:
    """Start SeqDB server"""

    # Create seqdb app and fastapi instance
    seqdb_app_cfg = AppCfg(
        AppType.SEQDB,
        seqdb_enum.ServiceType,
        (
            seqdb_enum.RepositoryType.DICT
            if use_dict_repository
            else seqdb_enum.RepositoryType.SA_SQL
        ),
        log_setup=True,
    )
    seqdb_app_composer = SeqdbAppComposer(seqdb_app_cfg, log_setup=True)
    seqdb_app = seqdb_app_composer.app
    seqdb_fastapi_app = create_fast_api(
        app=seqdb_app,
        create_routers_fn=seqdb_create_routers,
        app_id=seqdb_app_composer.app.generate_id(),
        setup_logger=seqdb_app_cfg.setup_logger,
        api_logger=seqdb_app_cfg.api_logger,
        debug=False,
    )

    with ServerManager(
        service=ServerType.SEQDB,
        app=seqdb_fastapi_app,
        host="127.0.0.1",
        port=8003,
        ssl_certfile=SSL_CERTFILE,
        ssl_keyfile=SSL_KEYFILE,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start SeqDB server")
        yield server


@contextmanager
def casedb_server(use_dict_repository: bool) -> Generator[ServerManager, None, None]:
    """Start CaseDB server"""

    # Create casedb app and fastapi instance
    casedb_app_cfg = AppCfg(
        AppType.CASEDB,
        casedb_enum.ServiceType,
        (
            casedb_enum.RepositoryType.DICT
            if use_dict_repository
            else casedb_enum.RepositoryType.SA_SQL
        ),
        log_setup=True,
    )
    casedb_app_composer = CasedbAppComposer(casedb_app_cfg, log_setup=True)
    casedb_app = casedb_app_composer.app
    casedb_fastapi_app = create_fast_api(
        app=casedb_app,
        create_routers_fn=casedb_create_routers,
        app_id=casedb_app_composer.app.generate_id(),
        setup_logger=casedb_app_cfg.setup_logger,
        api_logger=casedb_app_cfg.api_logger,
        debug=False,
    )

    with ServerManager(
        service=ServerType.CASEDB,
        app=casedb_fastapi_app,
        host="127.0.0.1",
        port=8000,
        ssl_certfile=SSL_CERTFILE,
        ssl_keyfile=SSL_KEYFILE,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start CaseDB server")
        yield server


@contextmanager
def platform_mock_dict_demo(
    use_dict_repository: bool, start_omopdb: bool
) -> Generator[dict[str, ServerManager], None, None]:
    """Start OAuth, SeqDB, and CaseDB (and optionally OmopDB) for local platform.

    - OAuth (mock) on 9000 with TLS using cert/ and key/.
    - SeqDB on 8003 (MOCK + DICT_DEMO).
    - CaseDB on 8000 (MOCK + DICT_DEMO) configured to use remote SeqDB.
    - OmopDB on 8002 (optional placeholder for now).

    Returns a dict of running ServerManager instances keyed by service name.
    """

    # Make server logs visible during local development
    ServerManager.LOGGER.setLevel(logging.INFO)

    servers: dict[str, ServerManager] = {}
    try:
        with oauth_server() as oauth:
            servers["oauth"] = oauth
            with seqdb_server(use_dict_repository) as seqdb:
                servers["seqdb"] = seqdb
                with casedb_server(use_dict_repository) as casedb:
                    servers["casedb"] = casedb
                    if start_omopdb:
                        with omopdb_server(use_dict_repository) as omop:
                            servers["omopdb"] = omop
                            yield servers
                    else:
                        yield servers
    finally:
        # Context managers handle shutdown; this block is for symmetry/clarity
        pass


def run_platform(use_dict_repository: bool, start_omopdb: bool) -> None:
    """CLI runner to start the local platform and block until Ctrl+C."""
    print("Starting local platform (mock.dict_demo)...")
    print(" - OAuth:   https://127.0.0.1:9000")
    print(" - SeqDB:   https://127.0.0.1:8003")
    print(" - CaseDB:  https://127.0.0.1:8000")
    if start_omopdb:
        print(" - OmopDB:  https://127.0.0.1:8002")
    else:
        print(" - OmopDB:  [disabled placeholder]")

    stop = False
    with platform_mock_dict_demo(use_dict_repository, start_omopdb):
        print("All services are up. Press Ctrl+C to stop.")
        try:
            while not stop:
                time.sleep(0.5)
        finally:
            # Context managers will stop services
            pass
