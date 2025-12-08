import datetime
import logging
import re
from pathlib import Path
from test.casedb.casedb_endpoint_test_client import CasedbEndpointTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from time import sleep
from typing import Any
from uuid import UUID

import gen_epix.casedb.domain.model.case.persistable
from gen_epix.casedb.api.router import create_routers
from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.env import AppComposer
from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg, BaseAppCfg
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import FilterType, TypedEqualsUuidFilter, TypedUuidSetFilter
from gen_epix.util import map_paired_elements


class OrganismType(enum.Enum):
    ORGANISM = "ORGANISM"
    TOXIN = "TOXIN"
    UNKNOWN = "UNKNOWN"


class CasedbTestClient(TestClient):
    TEST_CLIENTS: dict[str, "CasedbTestClient"] = {}

    MODEL_KEY_MAP = TestClient.MODEL_KEY_MAP | {
        model.User: "name",
        model.UserInvitation: "email",
        model.OrganizationAdminPolicy: ("organization_id", "user_id"),
        model.Disease: "name",
        model.EtiologicalAgent: "name",
        model.Etiology: ("disease_id", "etiological_agent_id"),
        model.CaseType: "name",
        model.CaseTypeSetCategory: "name",
        model.CaseTypeSet: "name",
        model.Concept: "code",
        model.ConceptSet: "name",
        model.CaseTypeSetMember: ("case_type_set_id", "case_type_id"),
        model.CaseTypeColSetMember: ("case_type_col_set_id", "case_type_col_id"),
        model.RegionSet: "code",
        model.RegionSetShape: ("region_set_id", "scale"),
        model.Region: ("region_set_id", "code"),
        model.GeneticDistanceProtocol: "name",
        model.Dim: "code",
        model.Col: "code",
        model.CaseTypeCol: "code",
        model.CaseTypeColSet: "name",
        model.DataCollection: "name",
        model.Case: "code",
        model.CaseSetCategory: "name",
        model.CaseSetStatus: "name",
        model.CaseSet: "name",
        model.CaseSetMember: ("case_set_id", "case_id"),
        model.CaseDataCollectionLink: ("data_collection_id", "case_id"),
        model.CaseSetDataCollectionLink: ("data_collection_id", "case_set_id"),
        model.OrganizationAccessCasePolicy: ("organization_id", "data_collection_id"),
        model.UserAccessCasePolicy: ("user_id", "data_collection_id"),
        model.OrganizationShareCasePolicy: (
            "organization_id",
            "data_collection_id",
            "from_data_collection_id",
        ),
        model.UserShareCasePolicy: (
            "user_id",
            "data_collection_id",
            "from_data_collection_id",
        ),
    }

    DUMMY_VALUES = {
        enum.ColType.TEXT: "TEXT",
        enum.ColType.CONTEXT_FREE_GRAMMAR_JSON: '{"key": "value"}',
        enum.ColType.CONTEXT_FREE_GRAMMAR_XML: "<tag>value</tag>",
        enum.ColType.REGULAR_LANGUAGE: ".*",
        enum.ColType.NOMINAL: None,
        enum.ColType.ORDINAL: None,
        enum.ColType.INTERVAL: None,
        enum.ColType.TIME_DAY: "1900-01-01",
        enum.ColType.TIME_WEEK: "1900-W01",
        enum.ColType.TIME_MONTH: "1900-01",
        enum.ColType.TIME_QUARTER: "1900-Q1",
        enum.ColType.TIME_YEAR: "1900",
        enum.ColType.GEO_LATLON: "-90.000, -180.0000",
        enum.ColType.GEO_REGION: None,
        enum.ColType.ID_DIRECT: "name1",
        enum.ColType.ID_PSEUDONYMISED: "id1",
        enum.ColType.ID_ANONYMISED: "bd11ae5c",
        enum.ColType.DECIMAL_0: "1",
        enum.ColType.DECIMAL_1: "1.1",
        enum.ColType.DECIMAL_2: "1.22",
        enum.ColType.DECIMAL_3: "1.333",
        enum.ColType.DECIMAL_4: "1.4444",
        enum.ColType.DECIMAL_5: "1.55555",
        enum.ColType.DECIMAL_6: "1.666666",
        enum.ColType.GENETIC_SEQUENCE: "acgt",
        enum.ColType.GENETIC_DISTANCE: None,
        enum.ColType.ORGANIZATION: None,
        enum.ColType.OTHER: None,
    }

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
        endpoint_test_client: CasedbEndpointTestClient | None = None
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
            endpoint_test_client = CasedbEndpointTestClient(
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

    def create_concept(
        self,
        user_or_str: str | model.User,
        code: str,
        concept_set_or_str: str | model.ConceptSet | None = None,
        set_dummy_concept_set: bool = False,
    ) -> model.Concept:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        concept_set: model.ConceptSet = (
            self._get_obj(model.ConceptSet, concept_set_or_str)
            if concept_set_or_str
            else None
        )  # type:ignore[assignment]
        if set_dummy_concept_set:
            if concept_set:
                raise ValueError(
                    "concept_set_or_str must be None if set_dummy_concept_set is True"
                )
            concept_set_id = self.generate_id()
        else:
            concept_set_id = concept_set.id
        concept = self.handle(
            command.ConceptCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Concept(
                    concept_set_id=concept_set_id,
                    code=code,
                ),
            )
        )
        return self._set_obj(concept)  # type:ignore[return-value]

    def create_concept_set(
        self,
        user_or_str: str | model.User,
        code: str,
        concept_set_type: enum.ConceptSetType,
        concepts: set[str | model.Concept] | None = None,
        regex: str | None = None,
        schema_definition: str | None = None,
        schema_uri: str | None = None,
        set_dummy_concepts: bool = False,
    ) -> model.ConceptSet:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        concept_set = self.handle(
            command.ConceptSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.ConceptSet(
                    code=code,
                    name=code,
                    type=concept_set_type,
                    regex=regex,
                    schema_definition=schema_definition,
                    schema_uri=schema_uri,
                ),
            )
        )
        if concepts and set_dummy_concepts:
            for x in concepts:
                if isinstance(x, str):
                    self.create_concept(user, x, concept_set)
                else:
                    # If a Concept object is passed, replicate by code
                    self.create_concept(user, x.code, concept_set)
        return self._set_obj(concept_set)  # type:ignore[return-value]

    def create_region_set(
        self,
        user_or_str: str | model.User,
        code: str,
        resolution: int = 1,
    ) -> model.RegionSet:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        region_set = self.handle(
            command.RegionSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.RegionSet(
                    code=code,
                    name=code,
                    region_code_as_label=False,
                    resolution=resolution,
                ),
            )
        )
        return self._set_obj(region_set)  # type:ignore[return-value]

    def create_region_set_shape(
        self,
        user_or_str: str | model.User,
        region_set: str | model.RegionSet,
        scale: float,
        set_dummy_region_set: bool = False,
    ) -> model.RegionSetShape:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        region_set_shape = self.handle(
            command.RegionSetShapeCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.RegionSetShape(
                    region_set_id=(
                        self.generate_id()
                        if set_dummy_region_set
                        else self._get_obj(model.RegionSet, region_set).id
                    ),
                    scale=scale,
                    geo_json="{}",
                ),
            )
        )
        return self._set_obj(region_set_shape)  # type:ignore[return-value]

    def create_region(
        self,
        user_or_str: str | model.User,
        code: str,
        region_set: str | model.RegionSet,
        set_dummy_region_set: bool = False,
    ) -> model.Region:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        region = self.handle(
            command.RegionCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Region(
                    region_set_id=(
                        self.generate_id()
                        if set_dummy_region_set
                        else self._get_obj(model.RegionSet, region_set).id
                    ),
                    code=code,
                    name=code,
                    centroid_lat=0,
                    centroid_lon=0,
                    center_lat=0,
                    center_lon=0,
                ),
            )
        )
        return self._set_obj(region)  # type:ignore[return-value]

    def create_genetic_distance_protocol(
        self,
        user_or_str: str | model.User,
        name: str,
        seqdb_seq_distance_protocol_id: UUID | None = None,
        min_scale_unit: float = 1,
    ) -> gen_epix.casedb.domain.model.case.persistable.GeneticDistanceProtocol:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        seqdb_seq_distance_protocol_id = (
            self.generate_id()
            if not seqdb_seq_distance_protocol_id
            else seqdb_seq_distance_protocol_id
        )
        genetic_distance_protocol = self.handle(
            command.GeneticDistanceProtocolCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=gen_epix.casedb.domain.model.case.persistable.GeneticDistanceProtocol(
                    name=name,
                    seqdb_seq_distance_protocol_id=seqdb_seq_distance_protocol_id,
                    min_scale_unit=min_scale_unit,
                ),
            )
        )
        return self._set_obj(genetic_distance_protocol)  # type:ignore[return-value]

    def create_dim(
        self,
        user_or_str: str | model.User,
        code: str,
        dim_type: enum.DimType,
    ) -> model.Dim:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        dim = self.handle(
            command.DimCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Dim(
                    code=code,
                    label=code,
                    dim_type=dim_type,
                ),
            )
        )
        return self._set_obj(dim)  # type:ignore[return-value]

    def create_col(
        self,
        user_or_str: str | model.User,
        code: str,
        col_type: enum.ColType,
        concept_set: str | model.ConceptSet | None = None,
        region_set: str | model.RegionSet | None = None,
        genetic_distance_protocol: (
            str
            | gen_epix.casedb.domain.model.case.persistable.GeneticDistanceProtocol
            | None
        ) = None,
        set_dummy_dim: bool = False,
        set_dummy_concept_set: bool = False,
        set_dummy_region_set: bool = False,
        set_dummy_genetic_distance_protocol: bool = False,
    ) -> model.Col:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)_?(.*)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        dim = m.group(1) + m.group(2)
        rank_in_dim = int(m.group(3))
        dim_id = (
            self.generate_id() if set_dummy_dim else self._get_obj(model.Dim, dim).id
        )
        concept_set_id = (
            self.generate_id()
            if set_dummy_concept_set
            else (
                None
                if not concept_set
                else self._get_obj(model.ConceptSet, concept_set).id
            )
        )
        region_set_id = (
            self.generate_id()
            if set_dummy_region_set
            else (
                None
                if not region_set
                else self._get_obj(model.RegionSet, region_set).id
            )
        )
        genetic_distance_protocol_id = (
            self.generate_id()
            if set_dummy_genetic_distance_protocol
            else (
                None
                if not genetic_distance_protocol
                else self._get_obj(
                    gen_epix.casedb.domain.model.case.persistable.GeneticDistanceProtocol,
                    genetic_distance_protocol,
                ).id
            )
        )
        col = self.handle(
            command.ColCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Col(
                    code=code,
                    label=code,
                    dim_id=dim_id,
                    col_type=col_type,
                    rank_in_dim=rank_in_dim,
                    concept_set_id=concept_set_id,
                    region_set_id=region_set_id,
                    genetic_distance_protocol_id=genetic_distance_protocol_id,
                ),
            )
        )
        return self._set_obj(col)  # type:ignore[return-value]

    def create_disease(
        self, user_or_str: str | model.User, disease_name: str
    ) -> model.Disease:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        disease = self.handle(
            command.DiseaseCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Disease(name=disease_name),
            )
        )
        return self._set_obj(disease)  # type:ignore[return-value]

    def create_etiological_agent(
        self, user_or_str: str | model.User, etiological_agent_name: str
    ) -> model.EtiologicalAgent:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        etiological_agent = self.app.handle(
            command.EtiologicalAgentCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.EtiologicalAgent(
                    name=etiological_agent_name, type=OrganismType.ORGANISM.value
                ),
            )
        )
        return self._set_obj(etiological_agent)  # type:ignore[return-value]

    def create_etiology(
        self,
        user_or_str: str | model.User,
        disease: str | model.Disease | None,
        etiological_agent: str | model.EtiologicalAgent | None,
        set_dummy_disease: bool = False,
        set_dummy_etiological_agent: bool = False,
    ) -> model.Etiology:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        etiology = self.app.handle(
            command.EtiologyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Etiology(  # type:ignore[call-arg]
                    disease_id=(
                        self.generate_id()  # type:ignore[arg-type]
                        if set_dummy_disease
                        else (
                            None
                            if not disease
                            else self._get_obj(model.Disease, disease).id
                        )
                    ),
                    etiological_agent_id=(
                        self.generate_id()  # type:ignore[arg-type]
                        if set_dummy_etiological_agent
                        else (
                            None
                            if not etiological_agent
                            else self._get_obj(
                                model.EtiologicalAgent, etiological_agent
                            ).id
                        )
                    ),
                ),
            )
        )
        return self._set_obj(etiology)  # type:ignore[return-value]

    def create_case_type(
        self,
        user_or_str: str | model.User,
        case_type: str | model.CaseType,
        disease: str | model.Disease | None,
        etiological_agent: str | model.EtiologicalAgent | None,
        set_dummy_disease: bool = False,
        set_dummy_etiological_agent: bool = False,
    ) -> model.CaseType:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        case_type = self.handle(
            command.CaseTypeCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseType(
                    name=case_type,
                    disease_id=(
                        self.generate_id()
                        if set_dummy_disease
                        else (
                            None
                            if not disease
                            else self._get_obj(model.Disease, disease).id
                        )
                    ),
                    etiological_agent_id=(
                        self.generate_id()
                        if set_dummy_etiological_agent
                        else (
                            None
                            if not etiological_agent
                            else self._get_obj(
                                model.EtiologicalAgent, etiological_agent
                            ).id
                        )
                    ),
                ),
            )
        )
        return self._set_obj(case_type)  # type:ignore[return-value]

    def create_case_type_settings(
        self,
        user_or_str: str | model.User,
        case_type: str | model.CaseType,
        stats_time_case_type_col: str | model.CaseTypeCol,
        stats_geo_case_type_col: str | model.CaseTypeCol,
        create_max_n_cases: int = 1000,
        read_max_n_cases: int = 1000,
        read_max_tree_size: int = 1000,
        update_max_n_cases: int = 1000,
        delete_max_n_cases: int = 1000,
    ) -> model.CaseTypeSettings:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        case_type_settings = self.handle(
            command.CaseTypeSettingsCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeSettings(
                    case_type_id=self._get_obj(model.CaseType, case_type).id,
                    stats_time_case_type_col_id=self._get_obj(
                        model.CaseTypeCol, stats_time_case_type_col
                    ).id,
                    stats_geo_case_type_col_id=self._get_obj(
                        model.CaseTypeCol, stats_geo_case_type_col
                    ).id,
                    create_max_n_cases=create_max_n_cases,
                    read_max_n_cases=read_max_n_cases,
                    read_max_tree_size=read_max_tree_size,
                    update_max_n_cases=update_max_n_cases,
                    delete_max_n_cases=delete_max_n_cases,
                ),
            )
        )
        return self._set_obj(case_type_settings)  # type:ignore[return-value]

    def create_case_type_set_member(
        self,
        user_or_str: str | model.User,
        case_type_set: str | model.CaseTypeSet,
        case_type: str | model.CaseType,
        set_dummy_case_type_set: bool = False,
        set_dummy_case_type: bool = False,
    ) -> model.CaseTypeSetMember:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        if set_dummy_case_type_set:
            case_type_set_id = self.generate_id()
        else:
            case_type_set_id = self._get_obj(model.CaseTypeSet, case_type_set).id
        if set_dummy_case_type:
            case_type_id = self.generate_id()
        else:
            case_type_id = self._get_obj(model.CaseType, case_type).id

        case_type_set_member = self.handle(
            command.CaseTypeSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeSetMember(
                    case_type_set_id=case_type_set_id,
                    case_type_id=case_type_id,
                ),
            )
        )
        return self._set_obj(case_type_set_member)  # type:ignore[return-value]

    def create_case_type_set_category(
        self,
        user_or_str: str | model.User,
        case_type_set_category: str | model.CaseTypeSetCategory,
        rank: int = 0,
    ) -> model.CaseTypeSetCategory:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        case_type_set_category = self.handle(
            command.CaseTypeSetCategoryCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeSetCategory(
                    name=case_type_set_category,
                    rank=rank,
                ),
            )
        )
        return self._set_obj(case_type_set_category)  # type:ignore[return-value]

    def create_case_type_set(
        self,
        user_or_str: str | model.User,
        case_type_set_name: str | model.CaseTypeSet,
        case_types: set[str | model.CaseType],
        case_type_set_category_or_str: str | model.CaseTypeSetCategory | None,
        rank: int = 0,
        set_dummy_case_type_set_category: bool = False,
        set_dummy_case_types: bool = False,
    ) -> model.CaseTypeSet:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        if set_dummy_case_type_set_category:
            case_type_set_category_id = self.generate_id()
        else:
            case_type_set_category_id = self._get_obj(
                model.CaseTypeSetCategory, case_type_set_category_or_str
            ).id
        case_type_set: model.CaseTypeSet = self.handle(
            command.CaseTypeSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeSet(
                    name=case_type_set_name,
                    case_type_set_category_id=case_type_set_category_id,
                    rank=rank,
                ),
            )
        )
        if set_dummy_case_types:
            case_type_ids = [self.generate_id() for _ in case_types]
        else:
            case_type_ids = [self._get_obj(model.CaseType, x).id for x in case_types]
        case_type_set_members = self.handle(
            command.CaseTypeSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_SOME,
                objs=[
                    model.CaseTypeSetMember(  # type:ignore[call-arg]
                        case_type_set_id=case_type_set.id,
                        case_type_id=x,
                    )
                    for x in case_type_ids
                ],
            )
        )
        for case_type_set_member in case_type_set_members:
            self._set_obj(case_type_set_member)
        return self._set_obj(case_type_set)  # type:ignore[return-value]

    def create_case_type_col(
        self,
        user_or_str: str | model.User,
        code: str,
        genetic_sequence_case_type_col_id: UUID | None = None,
        tree_algorithm_codes: set[enum.TreeAlgorithmType] | None = None,
        occurrence: int | None = None,
        col: str | model.Col | None = None,
        set_dummy_case_type: bool = False,
        set_dummy_col: bool = False,
    ) -> model.CaseTypeCol:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        m = re.match(r"^([a-z_]*\d+?)_(.*)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        if set_dummy_case_type:
            case_type_id = self.generate_id()
        else:
            case_type = self._get_obj(model.CaseType, m.group(1))
            case_type_id = case_type.id
        if set_dummy_col:
            col_id = self.generate_id()
        else:
            if col:
                col: model.Col = self._get_obj(model.Col, col)
            else:
                col: model.Col = self._get_obj(model.Col, m.group(2))
            col_id = col.id
        case_type_col = self.handle(
            command.CaseTypeColCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeCol(
                    case_type_id=case_type_id,
                    col_id=col_id,
                    code=code,
                    genetic_sequence_case_type_col_id=genetic_sequence_case_type_col_id,
                    tree_algorithm_codes=tree_algorithm_codes,
                    occurrence=occurrence,
                ),
            )
        )
        return self._set_obj(case_type_col)  # type:ignore[return-value]

    def create_case_type_col_set(
        self,
        user_or_str: str | model.User,
        case_type_col_set: str | model.CaseTypeColSet,
        case_type_cols: set[str | model.CaseTypeCol],
        set_dummy_case_type_cols: bool = False,
    ) -> model.CaseTypeColSet:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        case_type_col_set = self.handle(
            command.CaseTypeColSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeColSet(
                    name=case_type_col_set,
                    description=case_type_col_set,
                ),
            )
        )
        if set_dummy_case_type_cols:
            case_type_col_ids = [self.generate_id() for _ in case_type_cols]
        else:
            case_type_col_ids = [
                self._get_obj(model.CaseTypeCol, x).id for x in case_type_cols
            ]
        case_type_col_set_members = self.handle(
            command.CaseTypeColSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_SOME,
                objs=[
                    model.CaseTypeColSetMember(
                        case_type_col_set_id=case_type_col_set.id,
                        case_type_col_id=x,
                    )
                    for x in case_type_col_ids
                ],
            )
        )
        return self._set_obj(case_type_col_set)  # type:ignore[return-value]

    def create_case_type_col_set_member(
        self,
        user_or_str: str | model.User,
        case_type_col_set: str | model.CaseTypeColSet,
        case_type_col: str | model.CaseTypeCol,
    ) -> model.CaseTypeColSetMember:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        case_type_col_set: model.CaseTypeColSet = self._get_obj(
            model.CaseTypeColSet, case_type_col_set
        )
        case_type_col: model.CaseTypeCol = self._get_obj(
            model.CaseTypeCol, case_type_col
        )

        case_type_col_set_member = self.handle(
            command.CaseTypeColSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeColSetMember(
                    case_type_col_set_id=case_type_col_set.id,
                    case_type_col_id=case_type_col.id,
                ),
            )
        )
        return self._set_obj(case_type_col_set_member)  # type:ignore[return-value]

    def create_organization_access_case_policy(
        self,
        user_or_str: str | model.User,
        name: str,
        case_type_set: str | model.CaseTypeSet,
        is_active: bool = True,
        is_private: bool = False,
        add_case: bool = True,
        remove_case: bool = True,
        read_case_type_col_set: str | model.CaseTypeColSet | None = None,
        write_case_type_col_set: str | model.CaseTypeColSet | None = None,
        add_case_set: bool = True,
        remove_case_set: bool = True,
        read_case_set: bool = True,
        write_case_set: bool = True,
    ) -> model.OrganizationAccessCasePolicy:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+.*)$", name.lower())
        if not m:
            raise ValueError(f"Invalid code {name}")
        organization = self._get_obj(model.Organization, f"org{m.group(2)}")
        data_collection = self._get_obj(
            model.DataCollection, f"data_collection{m.group(3)}"
        )
        case_type_set = self._get_obj(model.CaseTypeSet, case_type_set)
        read_case_type_col_set_id = (
            self._get_obj(model.CaseTypeColSet, read_case_type_col_set).id
            if read_case_type_col_set
            else None
        )
        write_case_type_col_set_id = (
            self._get_obj(model.CaseTypeColSet, write_case_type_col_set).id
            if write_case_type_col_set
            else None
        )
        organization_access_case_policy = self.app.handle(
            command.OrganizationAccessCasePolicyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.OrganizationAccessCasePolicy(
                    organization_id=organization.id,
                    data_collection_id=data_collection.id,
                    is_active=is_active,
                    case_type_set_id=case_type_set.id,
                    is_private=is_private,
                    add_case=add_case,
                    remove_case=remove_case,
                    add_case_set=add_case_set,
                    read_case_type_col_set_id=read_case_type_col_set_id,
                    write_case_type_col_set_id=write_case_type_col_set_id,
                    remove_case_set=remove_case_set,
                    read_case_set=read_case_set,
                    write_case_set=write_case_set,
                ),
            )
        )
        # print(
        #     f"Created organization_case_policy: {organization.name}, {data_collection.name}, {case_type_col_set.name} ({organization_case_policy.organization_id}, {organization_case_policy.data_collection_id}, {organization_case_policy.case_type_col_set_id})"
        # )
        return self._set_obj(
            organization_access_case_policy
        )  # type:ignore[return-value]

    def create_user_access_case_policy(
        self,
        user_or_str: str | model.User,
        tgt_user_or_str: str | model.User,
        data_collection_or_str: str | model.DataCollection,
        case_type_set_or_str: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        read_case_type_col_set: str | model.CaseTypeColSet | None = None,
        write_case_type_col_set: str | model.CaseTypeColSet | None = None,
        add_case_set: bool = True,
        remove_case_set: bool = True,
        read_case_set: bool = True,
        write_case_set: bool = True,
    ) -> model.UserAccessCasePolicy:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        tgt_user: model.User = self._get_obj(model.User, tgt_user_or_str)
        data_collection = self._get_obj(model.DataCollection, data_collection_or_str)
        case_type_set = self._get_obj(model.CaseTypeSet, case_type_set_or_str)
        read_case_type_col_set_id = (
            self._get_obj(model.CaseTypeColSet, read_case_type_col_set).id
            if read_case_type_col_set
            else None
        )
        write_case_type_col_set_id = (
            self._get_obj(model.CaseTypeColSet, write_case_type_col_set).id
            if write_case_type_col_set
            else None
        )
        user_access_case_policy = self.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.UserAccessCasePolicy(
                    user_id=tgt_user.id,
                    data_collection_id=data_collection.id,
                    case_type_set_id=case_type_set.id,
                    is_active=is_active,
                    add_case=add_case,
                    remove_case=remove_case,
                    read_case_type_col_set_id=read_case_type_col_set_id,
                    write_case_type_col_set_id=write_case_type_col_set_id,
                    add_case_set=add_case_set,
                    remove_case_set=remove_case_set,
                    read_case_set=read_case_set,
                    write_case_set=write_case_set,
                ),
            )
        )
        return self._set_obj(user_access_case_policy)  # type:ignore[return-value]

    def create_organization_share_case_policy(
        self,
        user_or_str: str | model.User,
        name: str,
        case_type_set: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        add_case_set: bool = True,
        remove_case_set: bool = True,
    ) -> model.OrganizationShareCasePolicy:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)_(\d+)$", name.lower())
        if not m:
            raise ValueError(f"Invalid code {name}")
        organization = self._get_obj(model.Organization, f"org{m.group(2)}")
        data_collection = self._get_obj(
            model.DataCollection, f"data_collection{m.group(3)}"
        )
        from_data_collection = self._get_obj(
            model.DataCollection, f"data_collection{m.group(4)}"
        )
        case_type_set = self._get_obj(model.CaseTypeSet, case_type_set)
        organization_share_case_policy = self.app.handle(
            command.OrganizationShareCasePolicyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.OrganizationShareCasePolicy(
                    organization_id=organization.id,
                    data_collection_id=data_collection.id,
                    from_data_collection_id=from_data_collection.id,
                    is_active=is_active,
                    case_type_set_id=case_type_set.id,
                    add_case=add_case,
                    remove_case=remove_case,
                    add_case_set=add_case_set,
                    remove_case_set=remove_case_set,
                ),
            )
        )
        # print(
        #     f"Created organization_data_collection_policy: {organization.name}, {data_collection.name}, {source_data_collection.name}"
        # )
        return self._set_obj(
            organization_share_case_policy
        )  # type:ignore[return-value]

    def create_user_share_case_policy(
        self,
        user_or_str: str | model.User,
        tgt_user_or_str: str | model.User,
        data_collection: str | model.DataCollection,
        from_data_collection: str | model.DataCollection,
        case_type_set: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        add_case_set: bool = True,
        remove_case_set: bool = True,
    ) -> model.UserShareCasePolicy:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        tgt_user: model.User = self._get_obj(model.User, tgt_user_or_str)
        data_collection = self._get_obj(model.DataCollection, data_collection)
        from_data_collection = self._get_obj(model.DataCollection, from_data_collection)
        case_type_set = self._get_obj(model.CaseTypeSet, case_type_set)
        user_share_case_policy = self.handle(
            command.UserShareCasePolicyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.UserShareCasePolicy(
                    user_id=tgt_user.id,
                    data_collection_id=data_collection.id,
                    from_data_collection_id=from_data_collection.id,
                    case_type_set_id=case_type_set.id,
                    is_active=is_active,
                    add_case=add_case,
                    remove_case=remove_case,
                    add_case_set=add_case_set,
                    remove_case_set=remove_case_set,
                ),
            )
        )
        return self._set_obj(user_share_case_policy)  # type:ignore[return-value]

    def create_case(
        self,
        user_or_str: str | model.User,
        code: str,
        data_collections: (
            str | model.DataCollection | list[str] | list[model.DataCollection]
        ),
        col_index_pattern: str | None = None,
    ) -> model.Case:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        if not isinstance(data_collections, list):
            data_collections = [data_collections]
        data_collections = self._get_obj(model.DataCollection, data_collections)
        data_collection_ids = [x.id for x in data_collections]
        created_in_data_collection_id = data_collection_ids[0]
        data_collection_ids = data_collection_ids[1:]
        root_user: model.User = self._get_obj(model.User, "root1_1")
        m = re.match(r"^([a-z_]*)(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_index = int(m.group(2))
        case_index = int(m.group(3))
        case_type = self._get_obj(model.CaseType, f"case_type{case_type_index}")
        # TODO: get case_type_cols from complete_case_type
        case_type_cols = self.read_some_by_property(
            root_user,
            model.CaseTypeCol,
            "case_type_id",
            case_type.id,
            cascade=True,
        )
        # Fill in a value for all case_type_cols
        content = {}
        col_index_pattern = (
            col_index_pattern if col_index_pattern else r"^.*[a-z]*(\d+)_?\w*$"
        )
        for case_type_col in case_type_cols:
            col = case_type_col.col
            m = re.match(col_index_pattern, col.code.lower())
            col_index = int(m.group(1))
            value = self.DUMMY_VALUES[col.col_type]
            if col.col_type == enum.ColType.TEXT:
                value = f"{case_index}_{col_index}"
            elif col.col_type in {
                enum.ColType.NOMINAL,
                enum.ColType.ORDINAL,
                enum.ColType.INTERVAL,
            }:
                concept_set_members = self.read_some_by_property(
                    root_user,
                    model.ConceptRelation,
                    "concept_set_id",
                    col.concept_set_id,
                )
                value = concept_set_members[0].concept_id
            elif col.col_type == enum.ColType.GEO_REGION:
                regions = self.read_some_by_property(
                    root_user, model.Region, "region_set_id", col.region_set_id
                )
                value = regions[0].id
            content[case_type_col.id] = str(value)
        # Create the case, encoding the case_type_index and case_index in the case_date as resp. month and days since 1900-01-01
        cases = self.handle(
            command.CreateCasesCommand(
                user=user,
                cases=[
                    model.Case(
                        case_type_id=case_type.id,
                        # subject_id=self.generate_id(),
                        created_in_data_collection_id=created_in_data_collection_id,
                        # case_date=self._convert_case_code_to_date(code),
                        code=code,
                        content=content,
                    )
                ],
                data_collection_ids=data_collection_ids,
            )
        )
        case = cases[0]
        # Get the data collection associations
        stored_case_data_collection_links = self.handle(
            command.CaseDataCollectionLinkCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
                query_filter=TypedEqualsUuidFilter(
                    type=FilterType.EQUALS_UUID.value,
                    key="case_id",
                    value=case.id,
                ),
            ),
        )
        stored_case_data_collection_links = [
            self._set_obj(x) for x in stored_case_data_collection_links
        ]
        # Verify the data collection associations
        stored_data_collection_ids = {
            x.data_collection_id for x in stored_case_data_collection_links
        }
        if stored_data_collection_ids != set(data_collection_ids):
            raise ValueError(f"Data collection associations mismatch")
        return self._set_obj(case)  # type:ignore[return-value]

    def create_case_data_collection_link(
        self,
        user_in: str | model.User,
        case_in: str | model.Case,
        data_collection_in: str | model.DataCollection,
    ) -> model.CaseDataCollectionLink:
        user: model.User = self._get_obj(model.User, user_in)
        case: model.Case = self._get_obj(model.Case, case_in)
        data_collection: model.DataCollection = self._get_obj(
            model.DataCollection, data_collection_in
        )
        case_data_collection_link = self.handle(
            command.CaseDataCollectionLinkCrudCommand(
                user=user,
                objs=model.CaseDataCollectionLink(
                    case_id=case.id, data_collection_id=data_collection.id
                ),
                operation=CrudOperation.CREATE_ONE,
            )
        )
        return self._set_obj(case_data_collection_link)  # type:ignore[return-value]

    def create_case_set_category(
        self,
        user_or_str: str | model.User,
        name: str | model.CaseSetCategory,
    ) -> model.CaseSetCategory:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        case_set_category = self.handle(
            command.CaseSetCategoryCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseSetCategory(name=name, description=name),
            )
        )
        return self._set_obj(case_set_category)  # type:ignore[return-value]

    def create_case_set_status(
        self,
        user_or_str: str | model.User,
        name: str | model.CaseSetStatus,
    ) -> model.CaseSetStatus:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        case_set_status = self.handle(
            command.CaseSetStatusCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseSetStatus(name=name, description=name),
            )
        )
        return self._set_obj(case_set_status)  # type:ignore[return-value]

    def create_case_set(
        self,
        user_or_str: str | model.User,
        code: str,
        case_set_category: str | model.CaseSetCategory,
        case_set_status: str | model.CaseSetStatus,
        data_collections: (
            str | model.DataCollection | list[str] | list[model.DataCollection]
        ),
        cases: list[model.Case] | list[str] | None = None,
    ) -> model.Case:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(model.User, "root1_1")
        # Get the data collections
        if not isinstance(data_collections, list):
            data_collections = [data_collections]
        data_collections = self._get_obj(model.DataCollection, data_collections)
        data_collection_ids = [x.id for x in data_collections]
        created_in_data_collection_id = data_collection_ids[0]
        data_collection_ids = data_collection_ids[1:]
        # Get the case type
        m = re.match(r"^([a-z_]*)(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_index = int(m.group(2))
        case_type = self._get_obj(model.CaseType, f"case_type{case_type_index}")
        # Get the case set category and status
        case_set_category = self._get_obj(model.CaseSetCategory, case_set_category)
        case_set_status = self._get_obj(model.CaseSetStatus, case_set_status)
        # Get the cases
        if cases and isinstance(cases[0], str):
            cases = self._get_obj(
                model.Case,
                [self._convert_case_code_to_date(x) for x in cases],
            )
            case_ids = [x.id for x in cases]
        else:
            case_ids = None
        # Create the case set
        case_set = self.handle(
            command.CreateCaseSetCommand(
                user=user,
                case_set=model.CaseSet(
                    case_type_id=case_type.id,
                    created_in_data_collection_id=created_in_data_collection_id,
                    case_set_category_id=case_set_category.id,
                    case_set_status_id=case_set_status.id,
                    name=code,
                    description=code,
                ),
                data_collection_ids=data_collection_ids,
                case_ids=case_ids,
            )
        )
        case_set: model.CaseSet = self._set_obj(case_set)  # type:ignore[return-value]
        # Get the data collection associations
        stored_case_set_data_collection_links = self.handle(
            command.CaseSetDataCollectionLinkCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
                query_filter=TypedEqualsUuidFilter(
                    type=FilterType.EQUALS_UUID.value,
                    key="case_set_id",
                    value=case_set.id,
                ),
            ),
        )
        stored_case_set_data_collection_links = [
            self._set_obj(x) for x in stored_case_set_data_collection_links
        ]
        # Get the case associations
        stored_case_set_members = self.handle(
            command.CaseSetMemberCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
                query_filter=TypedEqualsUuidFilter(
                    type=FilterType.EQUALS_UUID.value,
                    key="case_set_id",
                    value=case_set.id,
                ),
            )
        )
        # Verify the data collection associations
        stored_data_collection_ids = {
            x.data_collection_id for x in stored_case_set_data_collection_links
        }
        if stored_data_collection_ids != set(data_collection_ids):
            raise ValueError(f"Data collection associations mismatch")
        # Verify the case associations
        stored_member_case_ids = {x.case_id for x in stored_case_set_members}
        if cases:
            if stored_member_case_ids != set(case_ids):
                raise ValueError(f"Case associations mismatch")
        else:
            if stored_member_case_ids:
                raise ValueError(f"Case associations mismatch")
        return case_set

    def create_site(
        self,
        user_or_str: str | model.User,
        code: str,
        organization: str | model.Organization = "org1",
    ) -> model.Site:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[arg-type]
        org: model.Organization = self._get_obj(
            model.Organization, organization
        )  # type:ignore[arg-type]
        site = self.handle(
            command.SiteCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Site(
                    organization_id=org.id,  # type:ignore[arg-type]
                    name=code,
                ),
            )
        )
        return self._set_obj(site)  # type:ignore[return-value]

    def create_contact(
        self,
        user_or_str: str | model.User,
        name: str,
        site: model.Site | str,
        email: str | None = None,
        phone: str | None = None,
    ) -> model.Contact:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[arg-type]
        site: model.Site = self._get_obj(model.Site, site)  # type:ignore[arg-type]
        contact = self.handle(
            command.ContactCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Contact(
                    site_id=site.id,  # type:ignore[arg-type]
                    name=name,
                    email=email,
                    phone=phone,
                ),
            )
        )
        return self._set_obj(contact)  # type:ignore[return-value]

    def read_organization_access_case_policies_with_any_right(
        self,
        user_or_str: str | model.User,
    ) -> list[model.OrganizationAccessCasePolicy]:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        policies: list[model.OrganizationAccessCasePolicy] = self.app.handle(
            command.OrganizationAccessCasePolicyCrudCommand(  # type:ignore[assignment]
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return [
            x
            for x in policies
            if x.is_active
            and x.organization_id == user.organization_id
            and (
                x.read_case_type_col_set_id
                or x.write_case_type_col_set_id
                or x.read_case_set
                or x.write_case_set
            )
        ]

    def read_user_access_case_policies_with_any_right(
        self,
        user_or_str: str | model.User,
    ) -> list[model.UserAccessCasePolicy]:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        policies: list[model.UserAccessCasePolicy] = self.app.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return [
            x
            for x in policies
            if x.is_active
            and x.user_id == user.id
            and (
                x.read_case_type_col_set_id
                or x.write_case_type_col_set_id
                or x.read_case_set
                or x.write_case_set
            )
        ]

    def read_organization_share_case_policies(
        self,
        user_or_str: str | model.User,
    ) -> list[model.OrganizationShareCasePolicy]:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        policies: list[model.OrganizationShareCasePolicy] = self.app.handle(
            command.OrganizationShareCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return [
            x
            for x in policies
            if x.is_active and x.organization_id == user.organization_id
        ]

    def read_user_share_case_policies(
        self,
        user_or_str: str | model.User,
    ) -> list[model.UserShareCasePolicy]:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        policies: list[model.UserShareCasePolicy] = self.app.handle(
            command.UserShareCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return [x for x in policies if x.is_active and x.user_id == user.id]

    def read_case_types_with_any_right(
        self,
        user_or_str: str | model.User,
    ) -> set[UUID]:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        # Admin users have access to all case type set members
        if (
            self.role_map[CommonRole.ROOT] in user.roles
            or self.role_map[CommonRole.APP_ADMIN] in user.roles
            or self.role_map[CommonRole.REFDATA_ADMIN] in user.roles
        ):
            policies: list[model.CaseType] = self.app.handle(
                command.CaseTypeCrudCommand(
                    user=root_user,
                    operation=CrudOperation.READ_ALL,
                )
            )
            return {x.id for x in policies}  # type:ignore
        case_type_set_ids = (
            {
                x.case_type_set_id
                for x in self.read_organization_share_case_policies(user)
            }
            | {
                x.case_type_set_id
                for x in self.read_user_access_case_policies_with_any_right(user)
            }
            | {x.case_type_set_id for x in self.read_user_share_case_policies(user)}
            | {
                x.case_type_set_id
                for x in self.read_user_access_case_policies_with_any_right(user)
            }
        )
        members: list[model.CaseTypeSetMember] = self.app.handle(
            command.CaseTypeSetMemberCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return {
            x.case_type_id for x in members if x.case_type_set_id in case_type_set_ids
        }

    def update_association_case_data_collection(
        self,
        user_or_str: str | model.User,
        cases: str | model.Case | list[str | model.Case],
        data_collections: set[str | model.DataCollection],
    ) -> list[model.CaseDataCollectionLink]:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(model.User, "root1_1")
        if not isinstance(cases, list):
            cases = [cases]
        cases = self._get_obj(
            model.Case, [self._convert_case_code_to_date(x) for x in cases]
        )
        data_collections = self._get_obj(model.DataCollection, list(data_collections))
        case_ids = [x.id for x in cases]
        data_collection_ids = {x.id for x in data_collections}
        curr_case_data_collection_links = self.handle(
            command.CaseDataCollectionLinkCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
                query_filter=TypedUuidSetFilter(
                    type=FilterType.UUID_SET.value,
                    key="case_id",
                    members=case_ids,
                ),
            )
        )
        curr_case_data_collections = {
            (x.case_id, x.data_collection_id) for x in curr_case_data_collection_links
        }
        to_create_case_data_collection_links = [
            model.CaseDataCollectionLink(case_id=x, data_collection_id=y)
            for x in case_ids
            for y in data_collection_ids
            if (x, y) not in curr_case_data_collections
        ]
        to_delete_case_data_collection_link_ids = [
            x.id
            for x in curr_case_data_collection_links
            if x.data_collection_id not in data_collection_ids
        ]
        # Create new associations
        new_case_data_collection_links = self.handle(
            command.CaseDataCollectionLinkCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_SOME,
                objs=to_create_case_data_collection_links,
            )
        )
        # Delete existing associations
        self.handle(
            command.CaseDataCollectionLinkCrudCommand(
                user=user,
                operation=CrudOperation.DELETE_SOME,
                obj_ids=to_delete_case_data_collection_link_ids,
            )
        )
        # Verify associations
        resulting_case_data_collection_links: list[model.CaseDataCollectionLink] = (
            self.handle(
                command.CaseDataCollectionLinkCrudCommand(
                    user=user,
                    operation=CrudOperation.READ_ALL,
                    query_filter=TypedUuidSetFilter(
                        type=FilterType.UUID_SET.value,
                        key="case_id",
                        members=case_ids,
                    ),
                )
            )
        )
        expected_case_data_collections = {
            (x, y) for x in case_ids for y in data_collection_ids
        }
        resulting_case_data_collections = {
            (x.case_id, x.data_collection_id)
            for x in resulting_case_data_collection_links
        }
        if expected_case_data_collections != resulting_case_data_collections:
            raise ValueError(f"Case data collection associations mismatch")
        for x in new_case_data_collection_links:
            self._set_obj(x)
        return resulting_case_data_collection_links

    def update_case_type_col_set_member(
        self,
        user_in: str | model.User,
        case_type_col_set_member: model.CaseTypeColSetMember,
    ) -> model.CaseTypeColSetMember:
        user = self._get_obj(model.User, user_in)
        updated_case_type_col_set_member = self.handle(
            command.CaseTypeColSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.UPDATE_ONE,
                objs=case_type_col_set_member,
            ),
        )
        return self._set_obj(
            updated_case_type_col_set_member, update=True
        )  # type:ignore[return-value]

    def temp_update_user_own_organization(
        self,
        user_or_str: str | model.User,
        organization_or_str: str | None = None,
        set_dummy_organization: bool = False,
    ) -> model.User:
        user: model.User = self._get_obj(
            model.User, user_or_str
        )  # type:ignore[assignment]
        root_user: model.User = self._get_obj(
            model.User, "root1_1"
        )  # type:ignore[assignment]
        orig_organization_id = user.organization_id
        if not organization_or_str:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                raise ValueError(
                    "Organization not given and set_dummy_organization False"
                )
        else:
            if set_dummy_organization:
                raise ValueError("Organization given and set_dummy_organization True")
            organization_id = self._get_obj(model.Organization, organization_or_str).id
        # Get current policies
        prev_user_access_case_policies = self.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        prev_user_access_case_policy_ids = {
            x.id for x in prev_user_access_case_policies if x.user_id == user.id
        }
        prev_user_share_case_policies = self.handle(
            command.UserShareCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        prev_user_share_case_policy_ids = {
            x.id for x in prev_user_share_case_policies if x.user_id == user.id
        }
        # Update user organization
        sleep(0.000000001)  # To avoid having same _modified_at as tgt_user
        user = self.handle(
            command.UpdateUserOwnOrganizationCommand(
                user=user,
                organization_id=organization_id,
            )
        )
        # Verify outcome
        if user.organization_id != organization_id:
            raise ValueError(f"organization_id not updated")
        new_user_access_case_policies = self.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        new_user_access_case_policy_ids = {
            x.id for x in new_user_access_case_policies if x.user_id == user.id
        }
        new_user_share_case_policies = self.handle(
            command.UserShareCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        new_user_share_case_policy_ids = {
            x.id for x in new_user_share_case_policies if x.user_id == user.id
        }
        if new_user_access_case_policy_ids.intersection(
            prev_user_access_case_policy_ids
        ):
            raise ValueError(f"User case policies not updated")
        if new_user_share_case_policy_ids.intersection(prev_user_share_case_policy_ids):
            raise ValueError(f"User data collection policies not updated")
        return self._set_obj(user, update=True)  # type:ignore[return-value]

    def verify_case_content_access(
        self,
        expected_access: dict[tuple[str, str], list[str]],
    ) -> None:
        for key, expected_case_content in expected_access.items():
            user, case_code = key
            user: model.User = self._get_obj(
                model.User, user_or_str
            )  # type:ignore[assignment]
            full_case = self._get_obj(
                model.Case, self._convert_case_code_to_date(case_code)
            )
            cases = self.handle(
                command.RetrieveCasesByIdCommand(
                    user=user,
                    case_ids=[full_case.id],
                )
            )
            case = cases[0]
            actual_case_content = case.content
            expected_case_content = sorted(
                [x for x in expected_case_content if x is not None]
            )
            actual_case_content = sorted(
                [x for x in actual_case_content.values() if x is not None]
            )
            if len(expected_case_content) != len(actual_case_content):
                if self.verbose:
                    print(
                        f"User {user.name}. Case {case_code}. Expected: {expected_case_content}. Actual: {actual_case_content}."
                    )
                raise ValueError(f"Case {case_code} content length mismatch")
            elif any(
                x != y for x, y in zip(expected_case_content, actual_case_content)
            ):
                if self.verbose:
                    print(
                        f"User {user.name}. Case {case_code}. Expected: {expected_case_content}. Actual: {actual_case_content}."
                    )
                raise ValueError(f"Case {case_code} content mismatch")

    def verify_case_type_access(
        self,
        expected_access: dict[str, list[str]],
    ) -> None:
        for user_str, expected_case_types in expected_access.items():
            user: model.User = self._get_obj(
                model.User, user_str
            )  # type:ignore[assignment]
            case_types = self.handle(
                command.CaseTypeCrudCommand(
                    user=user,
                    operation=CrudOperation.READ_ALL,
                )
            )
            expected_case_types = set([f"case_type{x}" for x in expected_case_types])
            actual_case_types = {x.name for x in case_types}
            missing_case_types = expected_case_types - actual_case_types
            extra_case_types = actual_case_types - expected_case_types
            if missing_case_types or extra_case_types:
                msg = f"User {user.name} case types mismatch. Missing: {missing_case_types}. Extra: {extra_case_types}."
                if self.verbose:
                    print(msg)
                raise ValueError(msg)

    def print_case_data_collection_links(self) -> None:
        cases = self.read_all("root1_1", model.Case, cascade=True)
        data_collections = {
            x.id: x
            for x in self.read_all("root1_1", model.DataCollection, cascade=True)
        }
        case_data_collection_links = self.read_all(
            "root1_1", model.CaseDataCollectionLink, cascade=True
        )
        print("\nCaseDataCollectionLinks:")

        case_data_collection_links = map_paired_elements(
            ((x.case_id, x.data_collection_id) for x in case_data_collection_links),
            as_set=True,
        )
        for x in sorted(
            cases, key=lambda x: self._convert_case_date_to_code(x.case_date)
        ):
            if x.id in case_data_collection_links:
                data_collection_str = ", ".join(
                    [
                        data_collections[y].name
                        for y in sorted(
                            case_data_collection_links[x.id],
                            key=lambda z: data_collections[z].name,
                        )
                    ]
                )
                case_name = self._convert_case_date_to_code(x.case_date)

                print(f"{case_name}: {data_collection_str} ({x.id})")

    def print_case_types(self) -> None:
        case_types = self.read_all("root1_1", model.CaseType, cascade=True)
        print("\nCaseTypes:")
        for x in sorted(case_types, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_case_type_sets(self) -> None:
        case_types = {
            x.id: x for x in self.read_all("root1_1", model.CaseType, cascade=True)
        }
        case_type_sets = self.read_all("root1_1", model.CaseTypeSet, cascade=True)
        case_type_set_members = self.read_all(
            "root1_1", model.CaseTypeSetMember, cascade=False
        )
        case_type_set_members = map_paired_elements(
            ((x.case_type_set_id, x.case_type_id) for x in case_type_set_members),
            as_set=True,
        )
        print("\nCaseTypeSets:")
        for x in sorted(case_type_sets, key=lambda x: x.name):
            case_types_str = ", ".join(
                [
                    case_types[y].name
                    for y in sorted(
                        case_type_set_members[x.id], key=lambda z: case_types[z].name
                    )
                ]
            )
            print(f"{x.name}: {case_types_str} ({x.id})")

    def print_case_type_cols(self) -> None:
        case_type_cols = self.read_all("root1_1", model.CaseTypeCol, cascade=True)
        print("\nCaseTypeCols:")
        for x in sorted(case_type_cols, key=lambda x: (x.case_type.name, x.code)):
            print(f"{x.code}: {x.case_type.name}, {x.col.col_type.value} ({x.id})")

    def print_case_type_col_sets(self) -> None:
        case_type_cols = {
            x.id: x for x in self.read_all("root1_1", model.CaseTypeCol, cascade=True)
        }
        case_type_col_sets = self.read_all(
            "root1_1", model.CaseTypeColSet, cascade=True
        )
        case_type_col_set_members = self.read_all(
            "root1_1", model.CaseTypeColSetMember, cascade=False
        )
        case_type_col_set_members = map_paired_elements(
            (
                (x.case_type_col_set_id, x.case_type_col_id)
                for x in case_type_col_set_members
            ),
            as_set=True,
        )
        print("\nCaseTypeColSets:")
        for x in sorted(case_type_col_sets, key=lambda x: x.name):
            case_type_col_ids_str = ", ".join(
                [
                    str(case_type_cols[y].id)
                    for y in sorted(
                        case_type_col_set_members[x.id],
                        key=lambda z: case_type_cols[z].code,
                    )
                ]
            )
            case_type_cols_str = ", ".join(
                [
                    case_type_cols[y].code
                    for y in sorted(
                        case_type_col_set_members[x.id],
                        key=lambda z: case_type_cols[z].code,
                    )
                ]
            )
            print(f"{x.name}: {case_type_cols_str}\n({x.id}: {case_type_col_ids_str})")

    def print_organization_access_case_policies(self) -> None:
        organization_access_case_policies = self.read_all(
            "root1_1", model.OrganizationAccessCasePolicy, cascade=True
        )
        organizations = {x.id: x for x in self.read_all("root1_1", model.Organization)}
        data_collections = {
            x.id: x for x in self.read_all("root1_1", model.DataCollection)
        }
        case_type_sets = {x.id: x for x in self.read_all("root1_1", model.CaseTypeSet)}
        case_type_col_sets = {
            x.id: x for x in self.read_all("root1_1", model.CaseTypeColSet)
        }
        print("\nOrganizationAccessCasePolicies:")
        for x in sorted(
            organization_access_case_policies,
            key=lambda x: (
                organizations[x.organization_id].name,
                data_collections[x.data_collection_id].name,
            ),
        ):
            read_case_type_col_set_name = (
                case_type_col_sets[x.read_case_type_col_set_id].name
                if x.read_case_type_col_set_id
                else None
            )
            write_case_type_col_set_name = (
                case_type_col_sets[x.write_case_type_col_set_id].name
                if x.write_case_type_col_set_id
                else None
            )
            print(
                f"{organizations[x.organization_id].name}/{data_collections[x.data_collection_id].name}: case_type_set={case_type_sets[x.case_type_set_id].name}, is_private={x.is_private}, add/remove_case={x.add_case}/{x.remove_case}, read/write_case_type_col_set={read_case_type_col_set_name}/{write_case_type_col_set_name}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, read/write_case_set={x.read_case_set}/{x.write_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_user_access_case_policies(self) -> None:
        user_access_case_policies = self.read_all(
            "root1_1", model.UserAccessCasePolicy, cascade=True
        )
        for user_access_case_policy in user_access_case_policies:
            # Get user with name filled in
            user_access_case_policy.user = self._get_obj(
                model.User, user_access_case_policy.user.id
            )
        data_collections = {
            x.id: x for x in self.read_all("root1_1", model.DataCollection)
        }
        case_type_sets = {x.id: x for x in self.read_all("root1_1", model.CaseTypeSet)}
        case_type_col_sets = {
            x.id: x for x in self.read_all("root1_1", model.CaseTypeColSet)
        }
        print("\nUserAccessCasePolicies:")
        for x in sorted(
            user_access_case_policies,
            key=lambda x: (
                x.user.name,
                data_collections[x.data_collection_id].name,
            ),
        ):
            read_case_type_col_set_name = (
                case_type_col_sets[x.read_case_type_col_set_id].name
                if x.read_case_type_col_set_id
                else None
            )
            write_case_type_col_set_name = (
                case_type_col_sets[x.write_case_type_col_set_id].name
                if x.write_case_type_col_set_id
                else None
            )
            print(
                f"{x.user.name}/{data_collections[x.data_collection_id].name}: case_type_set={case_type_sets[x.case_type_set_id].name}, add/remove_case={x.add_case}/{x.remove_case}, read/write_case_type_col_set={read_case_type_col_set_name}/{write_case_type_col_set_name}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, read/write_case_set={x.read_case_set}/{x.write_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_organization_share_case_policies(self) -> None:
        organization_share_case_policies = self.read_all(
            "root1_1", model.OrganizationShareCasePolicy
        )
        organizations = {x.id: x for x in self.read_all("root1_1", model.Organization)}
        data_collections = {
            x.id: x for x in self.read_all("root1_1", model.DataCollection)
        }
        case_type_sets = {x.id: x for x in self.read_all("root1_1", model.CaseTypeSet)}
        print("\nOrganizationShareCasePolicies:")
        for x in sorted(
            organization_share_case_policies,
            key=lambda x: (
                organizations[x.organization_id].name,
                data_collections[x.data_collection_id].name,
                data_collections[x.from_data_collection_id].name,
            ),
        ):
            print(
                f"{organizations[x.organization_id].name}/{data_collections[x.data_collection_id].name}<-{data_collections[x.from_data_collection_id].name}: case_type_set={case_type_sets[x.case_type_set_id].name}, add/remove_case={x.add_case}/{x.remove_case}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_user_share_case_policies(self) -> None:
        user_share_case_policies = self.read_all("root1_1", model.UserShareCasePolicy)
        for user_share_case_policy in user_share_case_policies:
            # Get user with name filled in
            user_share_case_policy.user = self._get_obj(
                model.User, user_share_case_policy.user_id
            )
        case_type_sets = {x.id: x for x in self.read_all("root1_1", model.CaseTypeSet)}
        data_collections = {
            x.id: x for x in self.read_all("root1_1", model.DataCollection)
        }
        print("\nUserShareCasePolicies:")
        for x in sorted(
            user_share_case_policies,
            key=lambda x: (
                x.user.name,
                data_collections[x.data_collection_id].name,
                data_collections[x.from_data_collection_id].name,
            ),
        ):
            print(
                f"{x.user.name}/{data_collections[x.data_collection_id].name}<-{data_collections[x.from_data_collection_id].name}: case_type_set={case_type_sets[x.case_type_set_id].name}, , add/remove_case={x.add_case}/{x.remove_case}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_cases(self, case_codes: list[str] | None = None) -> None:
        user: model.User = self._get_obj(model.User, "root1_1")
        cases = self.read_all(user, model.Case)
        if case_codes:
            cases = [
                x
                for x in cases
                if TestClient._convert_case_date_to_code(x.case_date) in case_codes
            ]
        case_data_collection_links = self.read_all(user, model.CaseDataCollectionLink)
        data_collections = {x.id: x for x in self.read_all(user, model.DataCollection)}
        case_type_cols = {x.id: x for x in self.read_all(user, model.CaseTypeCol)}
        case_date_collections = map_paired_elements(
            ((x.case_id, x.data_collection_id) for x in case_data_collection_links),
            as_set=True,
        )
        print("\nCases:")
        for x in sorted(cases, key=lambda x: x.case_date):
            curr_data_collections = sorted(
                [
                    data_collections[x].name
                    for x in case_date_collections.get(x.id, set())
                ]
            )
            curr_data_collections = ", ".join(curr_data_collections)
            curr_content = sorted(
                [(case_type_cols[x].code, y) for x, y in x.content.items()]
            )
            curr_content = ", ".join([f"{x[0]}={x[1]}" for x in curr_content])
            print(
                f"{TestClient._convert_case_date_to_code(x.case_date)}: {curr_content}; {curr_data_collections} ({x.id})"
            )

    def _get_obj(
        self,
        model_class: type[model.Model],
        obj: (
            str
            | UUID
            | model.Model
            | list[str | UUID | model.Model]
            | tuple[UUID, UUID]
        ),
        copy: bool = False,
        on_missing: str = "raise",
    ) -> model.Model | list[model.Model]:
        if isinstance(obj, list):
            return [self._get_obj(model_class, x) for x in obj]
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key = self._get_obj_key(table, model_class, obj, on_missing)
        if model_class == model.Case:
            if not isinstance(key, datetime.datetime):
                key = self._convert_case_code_to_date(key)
        if model_class == model.CaseDataCollectionLink:
            dc_id = key[0]
            case_id = key[1]

            case_data_collection_links = self.read_all(
                "root1_1", model.CaseDataCollectionLink, cascade=True
            )
            good_case_data_collection_links_list = []
            for y in case_data_collection_links:
                if y.case_id == case_id and y.data_collection_id == dc_id:
                    good_case_data_collection_links_list.append(y)

            if not good_case_data_collection_links_list:
                return None

            assert (
                len(good_case_data_collection_links_list) == 1
            ), "currently designed for one at a time"
            if copy:
                return table[key].model_copy()
            return table[key]

        if key not in table:
            if on_missing == "raise":
                raise ValueError(f"{model_class.__name__} {obj} not found")
            elif on_missing == "return_none":
                return None
            else:
                raise NotImplementedError()
        return table[key] if not copy else table[key].model_copy()

    @staticmethod
    def _convert_case_code_to_date(code: str) -> datetime.datetime:
        m = re.match(r"^([a-z_]*)(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_index = int(m.group(2))
        assert case_type_index < 13
        case_index = int(m.group(3))
        return datetime.datetime(
            year=1900 + case_index,  # Store case_index in year
            month=case_type_index,  # Store case_type_index in month
            day=1,  # Fixed day value
        )

    @staticmethod
    def _convert_case_date_to_code(case_date: datetime.datetime) -> str:
        case_type_index = int(case_date.month)  # Get case_type_index from month
        case_index = int(case_date.year - 1900)  # Get case_index from year offset
        return f"case{case_type_index}_{case_index}"
