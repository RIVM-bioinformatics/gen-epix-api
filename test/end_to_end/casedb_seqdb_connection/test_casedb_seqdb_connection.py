"""Test connection between casedb, seqdb and/or omopdb"""

import logging
from collections.abc import Generator
from pathlib import Path
from test.end_to_end.casedb_seqdb_connection.envvar import set_envvar
from test.test_client.enum import ServerType
from test.test_client.server_manager import ServerManager
from uuid import UUID

import pytest

import gen_epix.commondb.test.util as test_util
from gen_epix.casedb.domain import command
from gen_epix.casedb.domain import enum as enum
from gen_epix.casedb.domain import model
from gen_epix.casedb.env import AppComposer as CasedbAppComposer
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import AppType
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.api.router import create_routers as seqdb_create_routers
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.env import AppComposer as SeqdbAppComposer

SSL_CERTFILE = Path("cert/cert.pem").absolute().as_posix()
SSL_KEYFILE = Path("cert/key.pem").absolute().as_posix()


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def seqdb_server(
    oauth_server: ServerManager,
) -> Generator[ServerManager, None, None]:
    """Start SeqDB server on port 8001."""
    # Set environment variables for both casedb and seqdb
    set_envvar()

    # Create seqdb app and fastapi instance
    seqdb_app_cfg = AppCfg(
        AppType.SEQDB,
        seqdb_enum.ServiceType,
        seqdb_enum.RepositoryType,
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
        port=8001,
        ssl_certfile=SSL_CERTFILE,
        ssl_keyfile=SSL_KEYFILE,
    ) as server:
        if not server.start():
            pytest.fail("Failed to start SeqDB server")
        yield server


def test_casedb_seqdb_connection(
    oauth_server: ServerManager, seqdb_server: ServerManager
) -> None:
    """Test CaseDB to SeqDB connection with OAuth authentication."""
    # Set environment variables for both casedb and seqdb
    set_envvar()
    http_protocol = "https" if SSL_CERTFILE and SSL_KEYFILE else "http"

    # Create casedb app instance
    casedb_app_cfg = AppCfg(
        AppType.CASEDB,
        enum.ServiceType,
        enum.RepositoryType,
        log_setup=False,
    )
    casedb_app_composer = CasedbAppComposer(casedb_app_cfg, log_setup=False)
    casedb_app = casedb_app_composer.app

    # Test that the OAuth server is accessible
    import httpx

    try:
        with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
            response = client.get(f"{http_protocol}://localhost:9000/health")
            assert response.status_code == 200
            logging.info("✅ OAuth server is accessible")
    except Exception as e:
        pytest.fail(f"OAuth server health check failed: {e}")

    # Test that the SeqDB server is accessible
    try:
        with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
            response = client.get(f"{http_protocol}://127.0.0.1:8001/v1/health")
            assert response.status_code == 200
            logging.info("✅ SeqDB server is accessible")
    except Exception as e:
        pytest.fail(f"SeqDB server health check failed: {e}")

    # Verify OAuth discovery endpoint
    try:
        with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
            response = client.get(
                f"{http_protocol}://localhost:9000/.well-known/openid-configuration"
            )
            assert response.status_code == 200
            discovery_data = response.json()
            assert "token_endpoint" in discovery_data
            logging.info("✅ OAuth discovery endpoint is accessible")
    except Exception as e:
        pytest.fail(f"OAuth discovery endpoint failed: {e}")

    # Create root user
    root_user: model.User = test_util.get_existing_root_user(
        casedb_app_composer.cfg, casedb_app
    )

    # Get all cols, case_type_cols and cases
    cols: dict[UUID, model.Col] = {
        x.id: x
        for x in casedb_app.handle(
            command.ColCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
    }
    case_type_cols: dict[UUID, model.CaseTypeCol] = {
        x.id: x
        for x in casedb_app.handle(
            command.CaseTypeColCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
    }
    cases: list[model.Case] = casedb_app.handle(
        command.CaseCrudCommand(
            user=root_user,
            operation=CrudOperation.READ_ALL,
        )
    )

    # Test phylogenetic tree retrieval (which calls SeqDB)
    phylogenetic_tree_retrieved = False
    genetic_distance_case_type_col_ids = [
        x.id
        for x in case_type_cols.values()
        if cols[x.col_id].col_type == enum.ColType.GENETIC_DISTANCE
    ]
    for case_type_col_id in genetic_distance_case_type_col_ids:
        case_type_col = case_type_cols[case_type_col_id]
        genetic_sequence_case_type_col_id = (
            case_type_col.genetic_sequence_case_type_col_id
        )
        case_ids: list[UUID] = [
            x.id for x in cases if x.content.get(genetic_sequence_case_type_col_id)
        ]
        if len(case_ids) < 2:
            continue
        if len(case_ids) > 5:
            case_ids = case_ids[0:5]
        if case_type_col.tree_algorithm_codes and case_type_col.id:
            for tree_algorithm_code in case_type_col.tree_algorithm_codes:
                phylogenetic_tree = casedb_app.handle(
                    command.RetrievePhylogeneticTreeByCasesCommand(
                        user=root_user,  # type: ignore[arg-type]
                        genetic_distance_case_type_col_id=case_type_col.id,
                        tree_algorithm=tree_algorithm_code,
                        case_ids=case_ids,
                    )
                )
                phylogenetic_tree_retrieved = True
                break
        if phylogenetic_tree_retrieved:
            break

    # Log results
    assert phylogenetic_tree_retrieved

    genetic_sequence_case_type_cols = [
        x
        for x in case_type_cols.values()
        if cols[x.col_id].col_type == enum.ColType.GENETIC_SEQUENCE
    ]
    for genetic_sequence_case_type_col in genetic_sequence_case_type_cols:
        has_seq_case_ids = [
            x.content[genetic_sequence_case_type_col.id]
            for x in cases
            if x.content.get(genetic_sequence_case_type_col.id)
        ]
        if not has_seq_case_ids:
            continue

    fasta_retrieved: bool = False
    if has_seq_case_ids:
        fasta_iter = casedb_app.handle(
            command.RetrieveGeneticSequenceFastaByIdCommand(
                user=root_user,  # type: ignore[arg-type]
                seq_ids=has_seq_case_ids,
                wrap=False,
            )
        )

        # Read a few chunks to validate FASTA-like content
        chunks_read = 0
        for chunk in fasta_iter:
            # Expect FASTA header or sequence lines
            if chunk.strip():
                assert chunk.startswith(">") or chunk.strip().isalpha()
                fasta_retrieved = True
            chunks_read += 1
            if chunks_read >= 10:
                break

    assert fasta_retrieved
