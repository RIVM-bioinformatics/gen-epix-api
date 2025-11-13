import logging
from pathlib import Path
from test.omopdb.omopdb_endpoint_test_client import OmopdbEndpointTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from typing import Any

from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg, BaseAppCfg
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.omopdb.api.router import create_routers
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.env import AppComposer


class OmopdbTestClient(TestClient):
    TEST_CLIENTS: dict[str, "OmopdbTestClient"] = {}

    MODEL_KEY_MAP = TestClient.MODEL_KEY_MAP | {
        model.User: "name",
        model.UserInvitation: "email",
        model.OrganizationAdminPolicy: ("organization_id", "user_id"),
        model.DataCollection: "name",
    }

    DUMMY_VALUES = {}

    @classmethod
    def get_test_client(
        cls,
        test_type: str,
        app_cfg: AppCfg,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        **kwargs: Any,
    ) -> "TestClient":
        """
        Create a test environment for the given test type and repository type. A
        single environment, with a common test directory, is kept for each test type.
        """
        if app_cfg.name not in cls.TEST_CLIENTS:
            test_name = get_test_name(test_type)
            test_dir = get_test_output_dir(test_name)
            is_new_test_dir = True
            # Find existing test dir for same test type and use that if found,
            # so all results come in the same dir
            for stored_name, stored_env in cls.TEST_CLIENTS.items():
                if stored_name.startswith(test_type):
                    test_name = stored_env.test_name
                    test_dir = stored_env.test_dir
                    is_new_test_dir = False
                    break
            # Adjust config to new dir and copy any repository files there
            if is_new_test_dir:
                app_cfg.copy_repository_files(test_dir)
            cls.TEST_CLIENTS[app_cfg.name] = cls(
                test_name,
                test_dir,
                app_cfg,
                verbose=verbose,
                log_level=log_level,
                log_setup=log_setup,
                **kwargs,
            )
        return cls.TEST_CLIENTS[app_cfg.name]  # type: ignore[no-any-return]

    def __init__(
        self,
        test_name: str,
        test_dir: Path,
        app_cfg: BaseAppCfg,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        use_endpoints: bool = False,
        default_route_prefix: str | None = None,
        **kwargs: Any,
    ):
        # Set and adjust cfg
        app_cfg.cfg["app"]["debug"] = True
        curr_cfg = app_cfg.cfg["service"]["auth"]["props"]["root"]
        curr_cfg["organization"]["name"] = "org1"
        curr_cfg["user"]["key"] = "root1_1@org1.org"
        curr_cfg["user"]["email"] = "root1_1@org1.org"
        curr_cfg["user"]["name"] = "root1_1"

        # Create app
        TestClient._set_log_level(app_cfg, log_level)
        app_composer = AppComposer(app_cfg, log_setup=log_setup, **kwargs)

        # Create endpoint test client if endpoints are to be used (including own
        # app_composer), otherwise construct app env separately
        endpoint_test_client: OmopdbEndpointTestClient | None = None
        app_last_handled_exception: dict | None = None
        if use_endpoints:
            fast_api = create_fast_api(
                app=app_composer.app,
                create_routers_fn=create_routers,
                setup_logger=app_cfg.setup_logger if log_setup else None,
                api_logger=app_cfg.api_logger,
                debug=True,
                update_openapi_schema=True,
            )
            app_last_handled_exception = LAST_HANDLED_EXCEPTION
            endpoint_test_client = OmopdbEndpointTestClient(
                app_composer.app,
                fast_api,
                app_last_handled_exception,
                **kwargs,
            )

        # Call base class constructor
        super().__init__(
            test_name,
            test_dir,
            app_cfg,
            app_composer,
            verbose=verbose,
            log_level=log_level,
            use_endpoints=use_endpoints,
            endpoint_test_client=endpoint_test_client,
            app_last_handled_exception=app_last_handled_exception,
            **kwargs,
        )

    # def create_concept(
    #     self,
    #     user_or_str: str | model.User,
    #     code: str,
    #     concept_set_or_str: str | model.ConceptSet | None = None,
    #     set_dummy_concept_set: bool = False,
    # ) -> model.Concept:
    #     user: model.User = self._get_obj(
    #         model.User, user_or_str
    #     )  # type:ignore[assignment]
    #     concept_set: model.ConceptSet = (
    #         self._get_obj(model.ConceptSet, concept_set_or_str)
    #         if concept_set_or_str
    #         else None
    #     )  # type:ignore[assignment]
    #     if set_dummy_concept_set:
    #         if concept_set:
    #             raise ValueError(
    #                 "concept_set_or_str must be None if set_dummy_concept_set is True"
    #             )
    #         concept_set_id = self.generate_id()
    #     else:
    #         concept_set_id = concept_set.id
    #     concept = self.handle(
    #         command.ConceptCrudCommand(
    #             user=user,
    #             operation=CrudOperation.CREATE_ONE,
    #             objs=model.Concept(
    #                 concept_set_id=concept_set_id,
    #                 code=code,
    #             ),
    #         )
    #     )
    #     return self._set_obj(concept)  # type:ignore[return-value]
