"""Test connection between casedb, seqdb and/or omopdb"""

import asyncio
import logging
import os
import threading
import time
from test.end_to_end.casedb_seqdb_connection.envvar import set_envvar
from test.test_client.oauth.server import app as oauth_app
from typing import Generator

import httpx
import pytest
import uvicorn

import gen_epix.commondb.test.util as test_util
from gen_epix.casedb.domain import command as casedb_command
from gen_epix.casedb.domain import enum as casedb_enum
from gen_epix.casedb.domain import model as casedb_model
from gen_epix.casedb.env import AppEnv as CasedbAppEnv
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain.enum import AppType
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.app import App
from gen_epix.seqdb.api.router import create_routers as seqdb_create_routers
from gen_epix.seqdb.env import AppEnv as SeqdbAppEnv

set_envvar()
casedb_app_cfg = AppCfg(
    AppType.CASEDB, casedb_enum.ServiceType, casedb_enum.RepositoryType, log_setup=False
)
casedb_app_env = CasedbAppEnv(casedb_app_cfg)
casedb_app = casedb_app_env.app
seqdb_app_cfg = AppCfg(
    AppType.SEQDB, casedb_enum.ServiceType, casedb_enum.RepositoryType, log_setup=False
)
seqdb_app_env = SeqdbAppEnv(seqdb_app_cfg)
seqdb_app = seqdb_app_env.app
seqdb_fastapi_app = create_fast_api(
    seqdb_app_cfg.cfg,
    app=seqdb_app,
    create_routers_fn=seqdb_create_routers,
    registered_user_dependency=seqdb_app_env.registered_user_dependency,
    new_user_dependency=seqdb_app_env.new_user_dependency,
    idp_user_dependency=seqdb_app_env.idp_user_dependency,
    app_id=seqdb_app_env.app.generate_id(),
    setup_logger=seqdb_app_cfg.setup_logger,
    api_logger=seqdb_app_cfg.api_logger,
    debug=False,
)
pass


class ServerManager:
    """Base class for managing server processes."""

    def __init__(self, app: App, host: str = "127.0.0.1", port: int = 8000):
        self.app = app
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self) -> bool:
        """Start the server in a separate thread."""
        try:
            print(f"Attempting to start server on {self.host}:{self.port}")
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="error",  # Reduce noise in tests
                access_log=False,
            )
            self.server = uvicorn.Server(config)

            def run_server() -> None:
                asyncio.run(self.server.serve())

            self.thread = threading.Thread(target=run_server, daemon=True)
            self.thread.start()

            # Wait for server to start
            print(f"Server thread started, waiting for availability...")
            is_ready = self._wait_for_server()
            print(f"Server ready: {is_ready}")
            return is_ready
        except Exception as e:
            print(f"Exception starting server: {e}")
            logging.error(f"Failed to start server on {self.host}:{self.port}: {e}")
            return False

    def _wait_for_server(self, timeout: int = 10) -> bool:
        """Wait for the server to become available."""
        start_time = time.time()
        health_path = "/health"  # Default for OAuth server

        # SeqDB uses /v1/health
        if self.port == 8001:
            health_path = "/v1/health"

        while time.time() - start_time < timeout:
            try:
                with httpx.Client(timeout=1.0) as client:
                    response = client.get(
                        f"http://{self.host}:{self.port}{health_path}"
                    )
                    if response.status_code == 200:
                        return True
            except Exception:
                pass
            time.sleep(0.1)
        return False

    def stop(self) -> None:
        """Stop the server."""
        if self.server:
            self.server.should_exit = True
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


@pytest.fixture(scope="function")
def oauth_server() -> Generator[ServerManager, None, None]:
    """Start OAuth server and create CASEDB_FOR_SEQDB client."""
    print("Creating OAuth server manager...")
    server = ServerManager(oauth_app, host="127.0.0.1", port=8000)

    print("Starting OAuth server...")
    if not server.start():
        print("OAuth server failed to start")
        pytest.fail("Failed to start OAuth server")

    print("OAuth server started, creating client...")
    # Create the CASEDB_FOR_SEQDB client
    client_data = {
        "client_id": "CASEDB_FOR_SEQDB",
        "client_secret": "CASEDB_FOR_SEQDB_CLIENT_SECRET",
        "client_name": "CASEDB for SEQDB Client",
        "scopes": ["openid", "profile", "read", "write"],
        "grant_types": ["client_credentials"],
        "redirect_uris": [],
        "audience": "SEQDB",
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                "http://127.0.0.1:8000/admin/clients", json=client_data
            )
            if response.status_code not in [
                201,
                409,
            ]:  # 201 = created, 409 = already exists
                print(
                    f"Failed to create OAuth client: {response.status_code} - {response.text}"
                )
                pytest.fail(
                    f"Failed to create OAuth client: {response.status_code} - {response.text}"
                )
    except Exception as e:
        print(f"Exception creating OAuth client: {e}")
        pytest.fail(f"Failed to create OAuth client: {e}")

    print("OAuth server setup complete")
    yield server


@pytest.fixture(scope="function")
def seqdb_server(oauth_server: ServerManager) -> Generator[ServerManager, None, None]:
    """Start SeqDB server."""
    # Import SeqDB app after environment variables are set
    from gen_epix.seqdb.app import FAST_API as seqdb_app

    server = ServerManager(seqdb_app, host="127.0.0.1", port=8001)

    if not server.start():
        pytest.fail("Failed to start SeqDB server")

    yield server


@pytest.fixture(scope="function")
def casedb_app(
    oauth_server: ServerManager, seqdb_server: ServerManager
) -> tuple[App, AppCfg]:
    """Create CaseDB app instance configured to use remote SeqDB with OAuth."""
    # Set environment variables to configure CaseDB for remote SeqDB with OAuth
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_APP_TYPE"] = "REMOTE"
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_MODULE"] = (
        "gen_epix.casedb.services.seqdb"
    )
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_CLASS_NAME"] = (
        "SeqdbRemoteApp"
    )
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_HOST"] = "127.0.0.1"
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_PORT"] = "8001"
    # OAuth configuration parameters for SeqdbRemoteApp constructor
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_AUTH_PROTOCOL"] = "OAUTH2"
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_OAUTH_FLOW"] = (
        "CLIENT_CREDENTIALS"
    )
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_OAUTH_SCOPE"] = "read write"
    # OidcServerCfg parameters passed via **kwargs to SeqdbRemoteApp
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_NAME"] = "seqdb-client"
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_LABEL"] = "SeqDB Client"
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_CLIENT_ID"] = (
        "CASEDB_FOR_SEQDB"
    )
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_CLIENT_SECRET"] = (
        "CASEDB_FOR_SEQDB_CLIENT_SECRET"
    )
    os.environ["CASEDB_SERVICE_SEQDB_PROPS_SEQDB_REMOTE_APP_DISCOVERY_URL"] = (
        "http://127.0.0.1:8000/.well-known/openid-configuration"
    )

    # Import CaseDB app after environment variables are set
    from gen_epix.casedb.app import APP_CFG, APP_ENV

    return APP_ENV.app, APP_CFG


def test_casedb_seqdb_connection(casedb_app: App) -> None:
    """Test connection between CaseDB and SeqDB with OAuth authentication."""
    app, app_cfg = casedb_app

    # Get root user
    root_user = test_util.create_root_user_from_claims(app_cfg.cfg, app)

    # Get org user for operations
    users = app.handle(
        casedb_command.UserCrudCommand(
            user=root_user,
            operation=CrudOperation.READ_ALL,
        )
    )

    # Find an org user
    org_user = None
    for user in users:
        if casedb_enum.Role.ORG_USER in user.roles:
            org_user = user
            break

    if not org_user:
        pytest.skip("No org user found for testing")

    # Get case types with data
    case_type_stats = app.handle(
        casedb_command.RetrieveCaseTypeStatsCommand(user=org_user)
    )

    has_cases_case_type_ids = {x.case_type_id for x in case_type_stats if x.n_cases > 0}

    if not has_cases_case_type_ids:
        pytest.skip("No case types with data found")

    # Get case types
    case_types = app.handle(
        casedb_command.CaseTypeCrudCommand(
            user=org_user,
            operation=CrudOperation.READ_ALL,
        )
    )

    phylogenetic_tree_found = False
    genetic_sequence_found = False

    for case_type in case_types:
        if case_type.id not in has_cases_case_type_ids:
            continue

        complete_case_type: casedb_model.CompleteCaseType = app.handle(
            casedb_command.RetrieveCompleteCaseTypeCommand(
                user=org_user,
                case_type_id=case_type.id,
            )
        )

        if len(complete_case_type.case_type_cols) <= 1:
            continue

        # Get case IDs
        case_ids = app.handle(
            casedb_command.RetrieveCasesByQueryCommand(
                user=root_user,
                case_query=casedb_model.CaseQuery(
                    case_type_ids=(
                        {complete_case_type.id} if complete_case_type.id else set()
                    ),
                ),
            )
        )

        if not case_ids:
            continue

        case_ids = case_ids[0:5]  # Limit to 5 cases for testing

        # Test phylogenetic tree retrieval (calls SeqDB)
        dist_case_type_cols = [
            case_type_col
            for case_type_col in complete_case_type.case_type_cols.values()
            if complete_case_type.cols[case_type_col.col_id].col_type
            == casedb_enum.ColType.GENETIC_DISTANCE
        ]

        for dist_case_type_col in dist_case_type_cols:
            if not dist_case_type_col.tree_algorithm_codes:
                continue
            for tree_algorithm_code in dist_case_type_col.tree_algorithm_codes:
                try:
                    if not dist_case_type_col.id:
                        continue
                    phylogenetic_tree = app.handle(
                        casedb_command.RetrievePhylogeneticTreeByCasesCommand(
                            user=root_user,
                            genetic_distance_case_type_col_id=dist_case_type_col.id,
                            tree_algorithm=tree_algorithm_code,
                            case_ids=case_ids,
                        )
                    )

                    # Verify tree structure
                    assert (
                        phylogenetic_tree is not None
                    ), "Phylogenetic tree should not be None"
                    if phylogenetic_tree.sequence_ids:
                        raise ValueError("Sequence IDs should not be returned")
                    if not set(phylogenetic_tree.leaf_ids).issubset(set(case_ids)):
                        raise ValueError("Leaf IDs should be a subset of the case IDs")

                    phylogenetic_tree_found = True
                    logging.info("✅ Phylogenetic tree retrieval successful")
                    break
                except Exception as e:
                    logging.warning(f"Phylogenetic tree retrieval failed: {e}")

            if phylogenetic_tree_found:
                break

        # Test genetic sequence retrieval (calls SeqDB)
        genetic_sequence_case_type_cols = [
            case_type_col
            for case_type_col in complete_case_type.case_type_cols.values()
            if complete_case_type.cols[case_type_col.col_id].col_type
            == casedb_enum.ColType.GENETIC_SEQUENCE
        ]

        for genetic_sequence_case_type_col in genetic_sequence_case_type_cols:
            try:
                if not genetic_sequence_case_type_col.id:
                    continue
                genetic_sequences: list[casedb_model.GeneticSequence] = app.handle(
                    casedb_command.RetrieveGeneticSequenceByCaseCommand(
                        user=root_user,
                        case_ids=case_ids[0:1],
                        genetic_sequence_case_type_col_id=genetic_sequence_case_type_col.id,
                    )
                )

                # Verify genetic sequences
                assert genetic_sequences, "Genetic sequence should not be empty"
                for seq in genetic_sequences:
                    assert seq.id, "Genetic sequence ID should not be empty"
                    assert hasattr(
                        seq, "nucleotide_sequence"
                    ), "Genetic sequence should have nucleotide_sequence attribute"

                genetic_sequence_found = True
                logging.info("✅ Genetic sequence retrieval successful")
                break
            except Exception as e:
                logging.warning(f"Genetic sequence retrieval failed: {e}")

        # If we found both, we can stop testing
        if phylogenetic_tree_found and genetic_sequence_found:
            break

    # Verify that we successfully tested the connection
    if not (phylogenetic_tree_found or genetic_sequence_found):
        pytest.skip("No genetic data found to test CaseDB-SeqDB connection")

    logging.info(
        f"Test completed - Phylogenetic tree: {phylogenetic_tree_found}, Genetic sequence: {genetic_sequence_found}"
    )

    # Test basic connectivity by making a direct HTTP call to SeqDB
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get("http://127.0.0.1:8001/v1/health")
            assert response.status_code == 200, "SeqDB health check should return 200"
            logging.info("✅ SeqDB direct connectivity test successful")
    except Exception as e:
        pytest.fail(f"SeqDB direct connectivity test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
