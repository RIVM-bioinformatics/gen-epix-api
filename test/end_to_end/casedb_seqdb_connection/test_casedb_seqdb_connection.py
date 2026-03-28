"""Test connection between casedb, seqdb and/or omopdb"""

import logging
from collections.abc import Generator
from pathlib import Path
from test.end_to_end.casedb_seqdb_connection.envvar import set_envvar
from test.test_client.enum import ServerType
from test.test_client.server_manager import ServerManager
from uuid import UUID

import pytest
import yaml

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


@pytest.mark.scenario_ids("TC-LOG-01-01")
def test_logging_config_contract_includes_uvicorn_json_loggers() -> None:
    # Config-contract test: validating the E2E logging.yaml shape directly instead of booting servers
    config_path = Path(__file__).with_name("logging.yaml")
    with config_path.open("rt", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    # Uvicorn logger names must be present so server logs use the same
    # handler/formatter strategy as app logs in end-to-end runs.
    loggers = config["loggers"]
    assert "uvicorn.error" in loggers
    assert "uvicorn.access" in loggers
    assert loggers["uvicorn.error"]["handlers"] == ["console"]
    assert loggers["uvicorn.access"]["handlers"] == ["console"]

    # Console handler must route through the JSON formatter contract that emits
    # the structured fields used downstream (ts/level/logger/etc.).
    handlers = config["handlers"]
    formatters = config["formatters"]
    assert handlers["console"]["formatter"] == "json"
    assert (
        formatters["json"]["()"]
        == "gen_epix.commondb.config.json_logging.JsonFormatter"
    )
    assert formatters["json"]["redacted_value"] == "[REDACTED]"
    assert "client_secret" in formatters["json"]["sensitive_keys"]

    # The uvicorn.access logger must declare the structured access-log filter
    # so HTTP fields (method/path/status) land as proper JSON keys in Monitoring Platform.
    filters = config.get("filters", {})
    assert "uvicorn_access_structured" in filters
    assert (
        filters["uvicorn_access_structured"]["()"]
        == "gen_epix.commondb.config.json_logging.UvicornAccessLogFilter"
    )
    assert loggers["uvicorn.access"].get("filters") == ["uvicorn_access_structured"]


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
    """Start seqdb server on port 8001."""
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
        debug=True,
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
            pytest.fail("Failed to start seqdb server")
        yield server


@pytest.mark.scenario_ids("TC-SEC-28-06", "TC-SEC-31-01", "TC-SEC-07-01")
def test_casedb_seqdb_connection(
    oauth_server: ServerManager, seqdb_server: ServerManager
) -> None:
    """Test casedb to seqdb connection with OAuth authentication."""
    # Set environment variables for both casedb and seqdb
    set_envvar()
    protocol = "https" if SSL_CERTFILE and SSL_KEYFILE else "http"

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
            response = client.get(f"{protocol}://localhost:9000/health")
            assert response.status_code == 200
            logging.info("✅ OAuth server is accessible")
    except Exception as e:
        pytest.fail(f"OAuth server health check failed: {e}")

    # Test that the seqdb server is accessible
    try:
        with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
            response = client.get(f"{protocol}://127.0.0.1:8003/v1/health")
            assert response.status_code == 200
            logging.info("✅ seqdb server is accessible")
    except Exception as e:
        pytest.fail(f"seqdb server health check failed: {e}")

    # Verify OAuth discovery endpoint
    try:
        with httpx.Client(timeout=5.0, verify=SSL_CERTFILE) as client:
            response = client.get(
                f"{protocol}://localhost:9000/.well-known/openid-configuration"
            )
            assert response.status_code == 200
            discovery_data = response.json()
            assert "token_endpoint" in discovery_data
            logging.info("✅ OAuth discovery endpoint is accessible")
    except Exception as e:
        pytest.fail(f"OAuth discovery endpoint failed: {e}")

    # Create root user
    root_user = test_util.create_root_user_from_claims(
        casedb_app_composer.cfg, casedb_app
    )

    # Get all RefCols, Cols and Cases
    ref_cols: dict[UUID, model.RefCol] = {
        x.id: x
        for x in casedb_app.handle(
            command.RefColCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
    }
    cols: dict[UUID, model.Col] = {
        x.id: x
        for x in casedb_app.handle(
            command.ColCrudCommand(
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

    # Test phylogenetic tree retrieval (which calls seqdb)
    is_phylogenetic_tree_retrieved = False
    is_similar_cases_retrieved = False
    genetic_distance_col_ids: list[UUID] = [
        x.id  # type: ignore[misc]
        for x in cols.values()
        if ref_cols[x.ref_col_id].col_type == enum.ColType.GENETIC_DISTANCE
    ]
    for col_id in genetic_distance_col_ids:
        col = cols[col_id]
        assert col.genetic_sequence_col_id is not None
        col = cols[col_id]
        genetic_sequence_col_id: UUID = (
            col.genetic_sequence_col_id  # type: ignore[assignment]
        )
        case_ids: list[UUID] = [
            x.id for x in cases if x.content.get(genetic_sequence_col_id)
        ]
        if len(case_ids) < 2:
            continue
        if len(case_ids) > 5:
            case_ids = case_ids[0:5]
        if col.tree_algorithm_codes and col.id:
            for tree_algorithm_code in col.tree_algorithm_codes:
                phylogenetic_tree = casedb_app.handle(
                    command.RetrievePhylogeneticTreeByCasesCommand(
                        user=root_user,
                        case_type_id=col.case_type_id,
                        genetic_distance_col_id=col.id,
                        tree_algorithm=tree_algorithm_code,
                        case_ids=case_ids,
                    )
                )
                is_phylogenetic_tree_retrieved = True
                similar_case_ids: list[UUID] = casedb_app.handle(
                    command.RetrieveSimilarCasesCommand(
                        user=root_user,
                        case_type_id=col.case_type_id,
                        genetic_distance_col_id=col.id,
                        case_ids=case_ids[0:5],
                        max_distance=5,
                    )
                )
                if len(similar_case_ids) > 0:
                    is_similar_cases_retrieved = True
                break
        if is_phylogenetic_tree_retrieved and is_similar_cases_retrieved:
            break

    assert isinstance(phylogenetic_tree, model.PhylogeneticTree)
    assert isinstance(similar_case_ids, list)
    assert len(similar_case_ids) > 0
    assert any(isinstance(case_id, UUID) for case_id in similar_case_ids)

    genetic_sequence_cols = [
        x
        for x in cols.values()
        if ref_cols[x.ref_col_id].col_type == enum.ColType.GENETIC_SEQUENCE
    ]
    has_seq_case_ids: list[UUID] = []
    for genetic_sequence_col in genetic_sequence_cols:
        assert genetic_sequence_col.id is not None
        has_seq_case_ids: list[UUID] = [
            UUID(x.content[genetic_sequence_col.id])
            for x in cases
            if x.content.get(genetic_sequence_col.id)
        ]
        if has_seq_case_ids:
            break

    fasta_retrieved: bool = False
    if has_seq_case_ids:
        fasta_iter = casedb_app.handle(
            command.RetrieveGeneticSequenceFastaByIdCommand(
                user=root_user,
                seq_ids=has_seq_case_ids,
                wrap=50,
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
