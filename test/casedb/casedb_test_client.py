# Prevent removing unused imports, which are needed
# ruff: noqa: F401
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from test.casedb.casedb_endpoint_test_client import CasedbEndpointTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from time import sleep
from typing import Any, cast
from uuid import UUID

from gen_epix.casedb.api.router import create_routers
from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.model.case.case_data import CaseDataCollectionLink
from gen_epix.casedb.env import AppComposer
from gen_epix.commondb.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg, BaseAppCfg
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.test.test_client import TestClient
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import FilterType, TypedEqualsUuidFilter, TypedUuidSetFilter
from gen_epix.seqdb.domain import enum as seqdb_enum
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
        model.ColSetMember: ("col_set_id", "col_id"),
        model.RegionSet: "code",
        model.RegionSetShape: ("region_set_id", "scale"),
        model.Region: ("region_set_id", "code"),
        model.GeneticDistanceProtocol: "name",
        model.RefDim: "code",
        model.RefCol: "code",
        model.Col: "code",
        model.Dim: "code",
        model.ColSet: "name",
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
        enum.ColType.ID_PERSON: "name1",
        enum.ColType.ID_SAMPLE: "sample1",
        enum.ColType.ID_CASE: "case1",
        enum.ColType.ID_EVENT: "event1",
        enum.ColType.ID_GENETIC_SEQUENCE: "seq1",
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

    def get_fixed_created_at(self) -> datetime:
        return datetime(2023, 1, 1, tzinfo=UTC)

    def get_fixed_modified_at(self) -> datetime:
        return datetime(2023, 6, 1, tzinfo=UTC)

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
                props = app_cfg.cfg["service"]["seqdb"]["props"]
                # Copy any seqdb local repository files as well in case of a local setup
                if props["seqdb_app_type"].upper() == "LOCAL":
                    props["seqdb_local_app"]["app_cfg"].copy_repository_files(test_dir)
            cls.TEST_CLIENTS[app_cfg.name] = cls(
                test_name,
                test_dir,
                app_cfg,
                verbose=verbose,
                log_level=log_level,
                log_setup=log_setup,
                **kwargs,
            )
        return cls.TEST_CLIENTS[app_cfg.name]

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
        app_composer = AppComposer(app_cfg, log_setup=log_setup, **kwargs)  #

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
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        concept_set: model.ConceptSet = (
            self.get_obj(model.ConceptSet, concept_set_or_str)  # type: ignore[assignment]
            if concept_set_or_str
            else None
        )
        if set_dummy_concept_set:
            if concept_set:
                raise ValueError(
                    "concept_set_or_str must be None if set_dummy_concept_set is True"
                )
            concept_set_id = self.generate_id()
        else:
            concept_set_id = concept_set.id  # type: ignore[assignment]
        concept = self.handle(
            command.ConceptCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Concept(
                    concept_set_id=concept_set_id,  # type: ignore[assignment]
                    code=code,
                ),
            )
        )
        return self.set_obj(concept)  # type: ignore[return-value]

    def create_concept_set(
        self,
        user_or_str: str | model.User,
        code: str,
        concept_set_type: enum.ConceptSetType,
        concepts: set[str | model.Concept] | None = None,
        set_dummy_concepts: bool = False,
    ) -> model.ConceptSet:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        concept_set = self.handle(
            command.ConceptSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.ConceptSet(
                    code=code,
                    name=code,
                    type=concept_set_type,
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
        return self.set_obj(concept_set)  # type: ignore[return-value]

    def create_region_set(
        self,
        user_or_str: str | model.User,
        code: str,
        resolution: int = 1,
    ) -> model.RegionSet:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
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
        return self.set_obj(region_set)  # type: ignore[return-value]

    def create_region_set_shape(
        self,
        user_or_str: str | model.User,
        region_set: str | model.RegionSet,
        scale: float,
        set_dummy_region_set: bool = False,
    ) -> model.RegionSetShape:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        region_set_shape = self.handle(
            command.RegionSetShapeCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.RegionSetShape(
                    region_set_id=(
                        self.generate_id()  # type: ignore[arg-type]
                        if set_dummy_region_set
                        else self.get_obj(model.RegionSet, region_set).id
                    ),
                    scale=scale,
                    geo_json="{}",
                ),
            )
        )
        return self.set_obj(region_set_shape)  # type: ignore[return-value]

    def create_region(
        self,
        user_or_str: str | model.User,
        code: str,
        region_set: str | model.RegionSet,
        set_dummy_region_set: bool = False,
    ) -> model.Region:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        region = self.handle(
            command.RegionCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Region(
                    region_set_id=(
                        self.generate_id()  # type: ignore[arg-type]
                        if set_dummy_region_set
                        else self.get_obj(model.RegionSet, region_set).id
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
        return self.set_obj(region)  # type: ignore[return-value]

    def create_genetic_distance_protocol(
        self,
        user_or_str: str | model.User,
        name: str,
        seqdb_seq_distance_protocol_id: UUID | None = None,
        seqdb_seq_distance_type: seqdb_enum.SeqDistanceType = seqdb_enum.SeqDistanceType.KMER_EUCLIDEAN,
        min_scale_unit: float = 1,
    ) -> model.GeneticDistanceProtocol:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        seqdb_seq_distance_protocol_id = (
            self.generate_id()
            if not seqdb_seq_distance_protocol_id
            else seqdb_seq_distance_protocol_id
        )
        protocol = self.handle(
            command.GeneticDistanceProtocolCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.GeneticDistanceProtocol(
                    name=name,
                    seqdb_seq_distance_protocol_id=seqdb_seq_distance_protocol_id,
                    seqdb_seq_distance_type=seqdb_seq_distance_type,
                    seqdb_is_integer_distance=True,
                    min_scale_unit=min_scale_unit,
                ),
            )
        )
        return self.set_obj(protocol)  # type: ignore[return-value]

    def create_ref_dim(
        self,
        user_or_str: str | model.User,
        code: str,
        dim_type: enum.DimType,
        rank: int = 1,
    ) -> model.RefDim:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        ref_dim = self.handle(
            command.RefDimCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.RefDim(
                    code=code,
                    label=code,
                    dim_type=dim_type,
                    rank=rank,
                ),
            )
        )
        return self.set_obj(ref_dim)  # type: ignore[return-value]

    def create_ref_col(
        self,
        user_or_str: str | model.User,
        code: str,
        col_type: enum.ColType = enum.ColType.TEXT,
        concept_set: str | model.ConceptSet | None = None,
        region_set: str | model.RegionSet | None = None,
        genetic_distance_protocol: str | model.GeneticDistanceProtocol | None = None,
        regex: str | None = None,
        schema_definition: str | None = None,
        schema_uri: str | None = None,
        set_dummy_ref_dim: bool = False,
        set_dummy_concept_set: bool = False,
        set_dummy_region_set: bool = False,
        set_dummy_genetic_distance_protocol: bool = False,
    ) -> model.RefCol:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)_?(.*)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        ref_dim = "ref_dim" + m.group(2)
        rank = int(m.group(3))
        if set_dummy_ref_dim:
            ref_dim_id = self.generate_id()
        else:
            ref_dim_obj: model.RefDim = self.get_obj(  # type: ignore[assignment]
                model.RefDim, ref_dim
            )
            assert ref_dim_obj.id is not None
            ref_dim_id = ref_dim_obj.id
        concept_set_id: UUID | None = (
            self.generate_id()
            if set_dummy_concept_set
            else (
                None
                if not concept_set
                else self.get_obj(model.ConceptSet, concept_set).id  # type: ignore[union-attr]
            )
        )
        region_set_id: UUID | None = (
            self.generate_id()
            if set_dummy_region_set
            else (
                None
                if not region_set
                else self.get_obj(model.RegionSet, region_set).id  # type: ignore[union-attr]
            )
        )
        genetic_distance_protocol_id = (
            self.generate_id()
            if set_dummy_genetic_distance_protocol
            else (
                None
                if not genetic_distance_protocol
                else self.get_obj(
                    model.GeneticDistanceProtocol,
                    genetic_distance_protocol,
                ).id  # type: ignore[union-attr]
            )
        )
        ref_col = self.handle(
            command.RefColCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.RefCol(
                    code=code,
                    label=code,
                    ref_dim_id=ref_dim_id,
                    col_type=col_type,
                    rank=rank,
                    concept_set_id=concept_set_id,
                    region_set_id=region_set_id,
                    genetic_distance_protocol_id=genetic_distance_protocol_id,
                    regex=regex,
                    schema_definition=schema_definition,
                    schema_uri=schema_uri,
                ),
            )
        )
        return self.set_obj(ref_col)  # type: ignore[return-value]

    def create_disease(
        self, user_or_str: str | model.User, disease_name: str
    ) -> model.Disease:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        disease = self.handle(
            command.DiseaseCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Disease(name=disease_name),
            )
        )
        return self.set_obj(disease)  # type: ignore[return-value]

    def create_etiological_agent(
        self, user_or_str: str | model.User, etiological_agent_name: str
    ) -> model.EtiologicalAgent:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        etiological_agent = self.app.handle(
            command.EtiologicalAgentCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.EtiologicalAgent(
                    name=etiological_agent_name, type=OrganismType.ORGANISM.value
                ),
            )
        )
        return self.set_obj(etiological_agent)  # type: ignore[return-value]

    def create_etiology(
        self,
        user_or_str: str | model.User,
        disease: str | model.Disease | None,
        etiological_agent: str | model.EtiologicalAgent | None,
        set_dummy_disease: bool = False,
        set_dummy_etiological_agent: bool = False,
    ) -> model.Etiology:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        etiology = self.app.handle(
            command.EtiologyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Etiology(  # type: ignore[call-arg]
                    disease_id=(
                        self.generate_id()  # type: ignore[arg-type]
                        if set_dummy_disease
                        else (
                            None
                            if not disease
                            else self.get_obj(model.Disease, disease).id
                        )
                    ),
                    etiological_agent_id=(
                        self.generate_id()  # type: ignore[arg-type]
                        if set_dummy_etiological_agent
                        else (
                            None
                            if not etiological_agent
                            else self.get_obj(
                                model.EtiologicalAgent, etiological_agent
                            ).id  # type: ignore[union-attr]
                        )
                    ),
                ),
            )
        )
        return self.set_obj(etiology)  # type: ignore[return-value]

    # Note: improve setting of dummy process metadata (created_at, modified_at, modified_by) in create_case_type and create_case_type_set,
    # which is currently only done to allow testing of the metadata policy in the test cases, but is a bit hacky.
    # Maybe we can add an optional parameter to the command handler to bypass the metadata policy for setting these fields,
    # or to set them to specific values for testing purposes, which would be cleaner than setting dummy values here and then overriding them in the test cases.
    def create_case_type(
        self,
        user_or_str: str | model.User,
        case_type_or_str: str | model.CaseType,
        disease: str | model.Disease | None,
        etiological_agent: str | model.EtiologicalAgent | None,
        set_dummy_disease: bool = False,
        set_dummy_etiological_agent: bool = False,
    ) -> model.CaseType:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        case_type: model.CaseType = self.handle(
            command.CaseTypeCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseType(
                    name=case_type_or_str,
                    disease_id=(
                        self.generate_id()
                        if set_dummy_disease
                        else (
                            None
                            if not disease
                            else self.get_obj(model.Disease, disease).id  # type: ignore[union-attr]
                        )
                    ),
                    etiological_agent_id=(
                        self.generate_id()
                        if set_dummy_etiological_agent
                        else (
                            None
                            if not etiological_agent
                            else self.get_obj(
                                model.EtiologicalAgent, etiological_agent
                            ).id  # type: ignore[union-attr]
                        )
                    ),
                ),
            )
        )
        return self.set_obj(case_type)  # type: ignore[return-value]

    def create_case_type_set_member(
        self,
        user_or_str: str | model.User,
        case_type_set_or_str: str | model.CaseTypeSet,
        case_type_or_str: str | model.CaseType,
        set_dummy_case_type_set: bool = False,
        set_dummy_case_type: bool = False,
    ) -> model.CaseTypeSetMember:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        if set_dummy_case_type_set:
            case_type_set_id = self.generate_id()
        else:
            case_type_set_id: UUID = self.get_obj(model.CaseTypeSet, case_type_set_or_str).id  # type: ignore[union-attr]
        if set_dummy_case_type:
            case_type_id: UUID = self.generate_id()
        else:
            case_type_id = self.get_obj(model.CaseType, case_type_or_str).id  # type: ignore[union-attr]

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
        return self.set_obj(case_type_set_member)  # type: ignore[return-value]

    def create_case_type_set_category(
        self,
        user_or_str: str | model.User,
        case_type_set_category_or_str: str | model.CaseTypeSetCategory,
        rank: int = 0,
    ) -> model.CaseTypeSetCategory:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        case_type_set_category: model.CaseTypeSetCategory = self.handle(
            command.CaseTypeSetCategoryCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeSetCategory(
                    name=case_type_set_category_or_str,
                    rank=rank,
                ),
            )
        )
        return self.set_obj(case_type_set_category)  # type: ignore[return-value]

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
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        if set_dummy_case_type_set_category:
            case_type_set_category_id = self.generate_id()
        else:
            case_type_set_category_id = self.get_obj(
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
            case_type_ids = [self.get_obj(model.CaseType, x).id for x in case_types]
        if case_type_ids:
            # Create members only if there are some, since this has different ABAC rights
            case_type_set_members = self.handle(
                command.CaseTypeSetMemberCrudCommand(
                    user=user,
                    operation=CrudOperation.CREATE_SOME,
                    objs=[
                        model.CaseTypeSetMember(  # type: ignore[call-arg]
                            case_type_set_id=case_type_set.id,
                            case_type_id=x,
                        )
                        for x in case_type_ids
                    ],
                )
            )
            for case_type_set_member in case_type_set_members:
                self.set_obj(case_type_set_member)
        return self.set_obj(case_type_set)  # type: ignore[return-value]

    def create_dim(
        self,
        user_or_str: str | model.User,
        code: str,
        rank: int = 0,
        is_case_date_dim: bool = False,
        set_dummy_case_type: bool = False,
        set_dummy_ref_dim: bool = False,
    ) -> model.Dim:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)_(\d+)$", code.lower())
        # (case_type)(ref_dim)(occurrence)
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_str = "case_type" + m.group(2)
        ref_dim_str = "ref_dim" + m.group(3)
        occurrence = int(m.group(4))
        case_type_id: UUID = (
            self.generate_id()
            if set_dummy_case_type
            else cast(
                model.CaseType, self.get_obj(model.CaseType, case_type_str)
            ).id  # type: ignore[assignment]
        )
        ref_dim_id = (
            self.generate_id()
            if set_dummy_ref_dim
            else cast(model.RefDim, self.get_obj(model.RefDim, ref_dim_str)).id
        )
        dim: model.Dim = self.handle(
            command.DimCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Dim(
                    case_type_id=case_type_id,
                    ref_dim_id=ref_dim_id,
                    occurrence=occurrence,
                    code=code,
                    rank=rank,
                    is_case_date_dim=is_case_date_dim,
                ),
            )
        )

        return self.set_obj(dim)  # type: ignore[return-value]

    def create_col(
        self,
        user_or_str: str | model.User,
        code: str,
        genetic_sequence_col_id: UUID | None = None,
        tree_algorithm_codes: set[enum.TreeAlgorithmType] | None = None,
        set_dummy_case_type: bool = False,
        set_dummy_dim: bool = False,
        set_dummy_ref_col: bool = False,
    ) -> model.Col:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)_(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_str = "case_type" + m.group(2)
        dim_str = "dim" + m.group(2) + "_" + m.group(3) + "_" + m.group(4)
        ref_col_str = "ref_col" + m.group(3) + "_" + m.group(5)
        if set_dummy_case_type:
            case_type_id = self.generate_id()
        else:
            case_type = self.get_obj(model.CaseType, case_type_str)
            case_type_id = case_type.id
        if set_dummy_dim:
            dim_id = self.generate_id()
        else:
            dim = self.get_obj(model.Dim, dim_str)
            dim_id = dim.id
        if set_dummy_ref_col:
            ref_col_id = self.generate_id()
        else:
            ref_col = self.get_obj(model.RefCol, ref_col_str)
            ref_col_id = ref_col.id
        col: model.Col = self.handle(
            command.ColCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Col(
                    case_type_id=case_type_id,
                    dim_id=dim_id,
                    ref_col_id=ref_col_id,
                    code=code,
                    rank=0,
                    genetic_sequence_col_id=genetic_sequence_col_id,
                    tree_algorithm_codes=tree_algorithm_codes,
                ),
            )
        )
        return self.set_obj(col)  # type: ignore[return-value]

    def create_col_set(
        self,
        user_or_str: str | model.User,
        col_set_or_str: str | model.ColSet,
        cols_or_str: set[str | model.Col],
        set_dummy_cols: bool = False,
    ) -> model.ColSet:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        col_set: model.ColSet = self.handle(  # type: ignore[assignment]
            command.ColSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.ColSet(
                    name=col_set_or_str,
                    description=col_set_or_str,
                ),
            )
        )
        if set_dummy_cols:
            col_ids = [self.generate_id() for _ in cols_or_str]
        else:
            col_ids = [self.get_obj(model.Col, x).id for x in cols_or_str]
        if col_ids:
            # Create members only if there are some, since this has different ABAC rights
            col_set_members: list[model.ColSetMember] = self.handle(  # type: ignore[assignment]
                command.ColSetMemberCrudCommand(
                    user=user,
                    operation=CrudOperation.CREATE_SOME,
                    objs=[  # type: ignore[assignment]
                        model.ColSetMember(
                            col_set_id=col_set.id,
                            col_id=x,
                        )
                        for x in col_ids
                    ],
                )
            )
            for col_set_member in col_set_members:
                self.set_obj(col_set_member)
        return self.set_obj(col_set)  # type: ignore[return-value]

    def create_col_set_member(
        self,
        user_or_str: str | model.User,
        col_set_or_str: str | model.ColSet,
        col_or_str: str | model.Col,
    ) -> model.ColSetMember:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        col_set: model.ColSet = self.get_obj(model.ColSet, col_set_or_str)  # type: ignore[assignment]
        col: model.Col = self.get_obj(model.Col, col_or_str)  # type: ignore[assignment]

        col_set_member: model.ColSetMember = self.handle(  # type: ignore[assignment]
            command.ColSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.ColSetMember(
                    col_set_id=col_set.id,
                    col_id=col.id,
                ),
            )
        )
        return self.set_obj(col_set_member)  # type: ignore[return-value]

    def create_organization_access_case_policy(
        self,
        user_or_str: str | model.User,
        name: str,
        case_type_set: str | model.CaseTypeSet,
        is_active: bool = True,
        is_private: bool = False,
        add_case: bool = True,
        remove_case: bool = True,
        read_col_set_or_str: str | model.ColSet | None = None,
        write_col_set_or_str: str | model.ColSet | None = None,
        add_case_set: bool = True,
        remove_case_set: bool = True,
        read_case_set: bool = True,
        write_case_set: bool = True,
    ) -> model.OrganizationAccessCasePolicy:
        """
        Create an organization access case policy with the given parameters.
        The name should be in the format "PREFIX_Y_Z" where PREFIX can be any string,
        Y is the organization number, and Z is the data collection number,
        e.g. "policy2_3" for org2 and data_collection3,
        or "org_case_policy1_1" for org1 and data_collection1.

        Note: it assumes that the organization and data collection with the given numbers already exist, and will raise an error if not.
        This is to ensure that the created policy is linked to valid objects.

        """
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+.*)$", name.lower())
        if not m:
            raise ValueError(f"Invalid code {name}")
        organization: model.Organization = self.get_obj(
            model.Organization, f"org{m.group(2)}"
        )  # type: ignore[assignment]
        data_collection: model.DataCollection = (
            self.get_obj(  # type: ignore[assignment]
                model.DataCollection, f"data_collection{m.group(3)}"
            )
        )
        case_type_set: model.CaseTypeSet = self.get_obj(
            model.CaseTypeSet, case_type_set
        )  # type: ignore[assignment]
        read_col_set: model.ColSet | None = (
            cast(model.ColSet, self.get_obj(model.ColSet, read_col_set_or_str))
            if read_col_set_or_str
            else None
        )
        read_col_set_id = read_col_set.id if read_col_set else None
        write_col_set: model.ColSet | None = (
            cast(model.ColSet, self.get_obj(model.ColSet, write_col_set_or_str))
            if write_col_set_or_str
            else None
        )
        write_col_set_id = write_col_set.id if write_col_set else None
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
                    read_col_set_id=read_col_set_id,
                    write_col_set_id=write_col_set_id,
                    remove_case_set=remove_case_set,
                    read_case_set=read_case_set,
                    write_case_set=write_case_set,
                ),
            )
        )
        # print(
        #     f"Created organization_case_policy: {organization.name}, {data_collection.name}, {col_set.name} ({organization_case_policy.organization_id}, {organization_case_policy.data_collection_id}, {organization_case_policy.col_set_id})"
        # )
        return self.set_obj(
            organization_access_case_policy
        )  # type: ignore[return-value]

    def create_user_access_case_policy(
        self,
        user_or_str: str | model.User,
        tgt_user_or_str: str | model.User,
        data_collection_or_str: str | model.DataCollection,
        case_type_set_or_str: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        read_col_set_or_str: str | model.ColSet | None = None,
        write_col_set_or_str: str | model.ColSet | None = None,
        add_case_set: bool = True,
        remove_case_set: bool = True,
        read_case_set: bool = True,
        write_case_set: bool = True,
    ) -> model.UserAccessCasePolicy:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        tgt_user: model.User = self.get_obj(model.User, tgt_user_or_str)  # type: ignore[assignment]
        data_collection: model.DataCollection = self.get_obj(model.DataCollection, data_collection_or_str)  # type: ignore[assignment]
        case_type_set: model.CaseTypeSet = self.get_obj(model.CaseTypeSet, case_type_set_or_str)  # type: ignore[assignment]
        read_col_set: model.ColSet | None = (
            cast(model.ColSet, self.get_obj(model.ColSet, read_col_set_or_str))
            if read_col_set_or_str
            else None
        )
        read_col_set_id = read_col_set.id if read_col_set else None
        write_col_set: model.ColSet | None = (
            cast(model.ColSet, self.get_obj(model.ColSet, write_col_set_or_str))
            if write_col_set_or_str
            else None
        )
        write_col_set_id = write_col_set.id if write_col_set else None
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
                    read_col_set_id=read_col_set_id,
                    write_col_set_id=write_col_set_id,
                    add_case_set=add_case_set,
                    remove_case_set=remove_case_set,
                    read_case_set=read_case_set,
                    write_case_set=write_case_set,
                ),
            )
        )
        return self.set_obj(user_access_case_policy)  # type: ignore[return-value]

    def create_organization_share_case_policy(
        self,
        user_or_str: str | model.User,
        name: str,
        case_type_set_or_str: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        add_case_set: bool = True,
        remove_case_set: bool = True,
    ) -> model.OrganizationShareCasePolicy:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        m = re.match(r"^(.*?)(\d+)_(\d+)_(\d+)$", name.lower())
        if not m:
            raise ValueError(f"Invalid code {name}")
        organization = self.get_obj(model.Organization, f"org{m.group(2)}")
        data_collection = self.get_obj(
            model.DataCollection, f"data_collection{m.group(3)}"
        )
        from_data_collection = self.get_obj(
            model.DataCollection, f"data_collection{m.group(4)}"
        )
        case_type_set: model.CaseTypeSet = self.get_obj(model.CaseTypeSet, case_type_set_or_str)  # type: ignore[assignment]
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
        return self.set_obj(
            organization_share_case_policy
        )  # type: ignore[return-value]

    def create_user_share_case_policy(
        self,
        user_or_str: str | model.User,
        tgt_user_or_str: str | model.User,
        data_collection_or_str: str | model.DataCollection,
        from_data_collection_or_str: str | model.DataCollection,
        case_type_set_or_str: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        add_case_set: bool = True,
        remove_case_set: bool = True,
    ) -> model.UserShareCasePolicy:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        tgt_user: model.User = self.get_obj(model.User, tgt_user_or_str)  # type: ignore[assignment]
        data_collection: model.DataCollection = self.get_obj(model.DataCollection, data_collection_or_str)  # type: ignore[assignment]
        from_data_collection: model.DataCollection = self.get_obj(model.DataCollection, from_data_collection_or_str)  # type: ignore[assignment]
        case_type_set: model.CaseTypeSet = self.get_obj(model.CaseTypeSet, case_type_set_or_str)  # type: ignore[assignment]
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
        return self.set_obj(user_share_case_policy)  # type: ignore[return-value]

    def create_case(
        self,
        user_or_str: str | model.User,
        code: str,
        data_collections_or_str: (
            str | model.DataCollection | list[str] | list[model.DataCollection]
        ),
        col_index_pattern: str | None = None,
    ) -> model.Case:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]

        if not isinstance(data_collections_or_str, list):
            data_collections_or_str = [data_collections_or_str]

        data_collections: list[model.DataCollection] = self.get_obj(model.DataCollection, data_collections_or_str)  # type: ignore[assignment]
        data_collection_ids = [x.id for x in data_collections]
        created_in_data_collection_id = data_collection_ids[0]
        data_collection_ids = data_collection_ids[1:]

        root_user: model.User = self.get_root_user()

        m = re.match(r"^([a-z_]*)(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_index = int(m.group(2))
        case_index = int(m.group(3))
        case_type: model.CaseType = self.get_obj(
            model.CaseType, f"case_type{case_type_index}"
        )  # type: ignore[assignment]

        # TODO: get Cols from CompleteCaseType
        cols: list[model.Col] = self.read_some_by_property(  # type: ignore[assignment]
            root_user,
            model.Col,
            "case_type_id",
            case_type.id,
            cascade=True,
        )
        # Fill in a value for all Cols
        content = {}
        col_index_pattern = (
            col_index_pattern if col_index_pattern else r"^.*[a-z]*(\d+)_?\w*$"
        )
        # The case is filled in completely
        # should be a parameter of create case for ABAC access
        for col in cols:
            ref_col: model.RefCol = col.ref_col
            m = re.match(col_index_pattern, ref_col.code.lower())
            col_index = int(m.group(1))
            value = self.DUMMY_VALUES[ref_col.col_type]
            if ref_col.col_type == enum.ColType.TEXT:
                value = f"{case_index}_{col_index}"
            elif ref_col.col_type in {
                enum.ColType.NOMINAL,
                enum.ColType.ORDINAL,
                enum.ColType.INTERVAL,
            }:
                concept_set_members = self.read_some_by_property(
                    root_user,
                    model.ConceptRelation,
                    "concept_set_id",
                    ref_col.concept_set_id,
                )
                value = concept_set_members[0].concept_id
            elif ref_col.col_type == enum.ColType.GEO_REGION:
                regions = self.read_some_by_property(
                    root_user, model.Region, "region_set_id", ref_col.region_set_id
                )
                value = regions[0].id
            content[col.id] = str(value)

        # Create the case, encoding the case_type_index and case_index in the case_date as resp. month and days since 1900-01-01
        case_batch_upload_result: model.CaseBatchUploadResult = self.handle(
            command.UploadCasesCommand(
                user=user,
                case_type_id=case_type.id,
                created_in_data_collection_id=created_in_data_collection_id,
                case_batch=model.CaseBatchForUpload(
                    cases=[
                        model.CaseForUpload(
                            id=self.generate_id(),
                            case=model.Case(
                                code=code,
                                case_type_id=case_type.id,
                                created_in_data_collection_id=created_in_data_collection_id,
                                content=content,
                            ),
                        )
                    ]
                ),
            )
        )

        #
        case_result = case_batch_upload_result.cases[0]

        case: model.Case = self.app.handle(
            command.CaseCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ONE,
                obj_ids=case_result.id,
            )
        )

        case: model.Case = self.set_obj(case)  # type: ignore[assignment]

        # Create data collection links
        for data_collection_id in data_collection_ids:
            self.create_case_data_collection_link(
                root_user, case.code, data_collection_in=data_collection_id
            )

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

        # # Verify the data collection associations
        stored_data_collection_ids: list[CaseDataCollectionLink] = {  # type: ignore[assignment]
            x.data_collection_id for x in stored_case_data_collection_links
        }
        if stored_data_collection_ids != set(data_collection_ids):
            raise ValueError(f"Data collection associations mismatch")

        return case

    def create_case_data_collection_link(
        self,
        user_in: str | model.User,
        case_in: str | model.Case,
        data_collection_in: str | model.DataCollection,
    ) -> model.CaseDataCollectionLink:
        user: model.User = self.get_obj(model.User, user_in)  # type: ignore[assignment]
        case: model.Case = self.get_obj(model.Case, case_in)  # type: ignore[assignment]
        data_collection: model.DataCollection = self.get_obj(
            model.DataCollection, data_collection_in
        )  # type: ignore[assignment]
        case_data_collection_link = self.handle(
            command.CaseDataCollectionLinkCrudCommand(
                user=user,
                objs=model.CaseDataCollectionLink(
                    case_id=case.id, data_collection_id=data_collection.id
                ),
                operation=CrudOperation.CREATE_ONE,
            )
        )
        return self.set_obj(case_data_collection_link)  # type: ignore[return-value]

    def create_case_set_category(
        self,
        user_or_str: str | model.User,
        name_or_enum: str | model.CaseSetCategory,
        rank: int = 0,
    ) -> model.CaseSetCategory:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        name: str = name_or_enum if isinstance(name_or_enum, str) else name_or_enum.name  # type: ignore[assignment]
        case_set_category = self.handle(
            command.CaseSetCategoryCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseSetCategory(name=name, description=name, rank=rank),
            )
        )
        return self.set_obj(case_set_category)  # type: ignore[return-value]

    def create_case_set_status(
        self,
        user_or_str: str | model.User,
        name_or_enum: str | model.CaseSetStatus,
        rank: int = 0,
    ) -> model.CaseSetStatus:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        name: str = name_or_enum if isinstance(name_or_enum, str) else name_or_enum.name  # type: ignore[assignment]
        case_set_status = self.handle(
            command.CaseSetStatusCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseSetStatus(name=name, description=name, rank=rank),
            )
        )
        return self.set_obj(case_set_status)  # type: ignore[return-value]

    # TODO LSP-2883 not used anywhere yet, uses a key for cases as date. Why?
    def create_case_set(
        self,
        user_or_str: str | model.User,
        code: str,
        case_set_category: str | model.CaseSetCategory,
        case_set_status: str | model.CaseSetStatus,
        data_collections_or_str: (
            str | model.DataCollection | list[str] | list[model.DataCollection]
        ),
        cases_or_str: list[model.Case] | list[str] | None = None,
    ) -> model.Case:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(model.User, "root1_1")  # type: ignore[assignment]
        # Get the data collections
        if not isinstance(data_collections_or_str, list):
            data_collections_or_str = [data_collections_or_str]
        data_collections: list[model.DataCollection] = self.get_obj(model.DataCollection, data_collections_or_str)  # type: ignore[assignment]
        data_collection_ids = [x.id for x in data_collections]
        created_in_data_collection_id = data_collection_ids[0]
        data_collection_ids = data_collection_ids[1:]
        # Get the CaseType
        m = re.match(r"^([a-z_]*)(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_index = int(m.group(2))
        case_type = self.get_obj(model.CaseType, f"case_type{case_type_index}")
        # Get the case set category and status
        case_set_category = self.get_obj(model.CaseSetCategory, case_set_category)
        case_set_status = self.get_obj(model.CaseSetStatus, case_set_status)
        # Get the cases
        if cases_or_str and isinstance(cases_or_str[0], str):
            cases: list[model.Case] = self.get_obj(  # type: ignore[assignment]
                model.Case,
                [self._convert_case_code_to_date(x) for x in cases_or_str],
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
                    code=code,
                    description=code,
                ),
                data_collection_ids=data_collection_ids,
                case_ids=case_ids,
            )
        )
        case_set: model.CaseSet = self.set_obj(case_set)  # type: ignore[return-value]
        # Get the data collection associations
        stored_case_set_data_collection_links: list[model.CaseSetDataCollectionLink] = self.handle(  # type: ignore[assignment]
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
            self.set_obj(x) for x in stored_case_set_data_collection_links
        ]
        # Get the case associations
        stored_case_set_members: list[model.CaseSetMember] = self.handle(  # type: ignore[assignment]
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
    ) -> model.Site:
        user: model.User = self.get_obj(  # type: ignore[assignment]
            model.User, user_or_str
        )  # type: ignore[arg-type]
        m = re.match(r"^([a-z_]*)(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        organization = self.get_obj(model.Organization, f"org{m.group(2)}")
        site = self.handle(
            command.SiteCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Site(
                    organization_id=organization.id,  # type: ignore[arg-type]
                    name=code,
                ),
            )
        )
        return self.set_obj(site)  # type: ignore[return-value]

    def create_contact(
        self,
        user_or_str: str | model.User,
        code: str,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> model.Contact:
        user: model.User = self.get_obj(  # type: ignore[assignment]
            model.User, user_or_str
        )  # type: ignore[arg-type]
        m = re.match(r"^([a-z_]*)(\d+)_(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        site: model.Site = self.get_obj(  # type: ignore[assignment]
            model.Site, f"site{m.group(2)}_{m.group(3)}"
        )  # type: ignore[arg-type]
        contact = self.handle(
            command.ContactCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Contact(
                    site_id=site.id,  # type: ignore[arg-type]
                    name=name or code,
                    email=email,
                    phone=phone,
                ),
            )
        )
        return self.set_obj(contact)  # type: ignore[return-value]

    # TODO LSP-2883 this is not used anywhere yet
    def read_organization_access_case_policies_with_any_right(
        self,
        user_or_str: str | model.User,
    ) -> list[model.OrganizationAccessCasePolicy]:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(
            model.User, "root1_1"
        )  # type: ignore[assignment]
        policies: list[model.OrganizationAccessCasePolicy] = self.app.handle(
            command.OrganizationAccessCasePolicyCrudCommand(  # type: ignore[assignment]
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
                x.read_col_set_id
                or x.write_col_set_id
                or x.read_case_set
                or x.write_case_set
            )
        ]

    def read_user_access_case_policies_with_any_right(
        self,
        user_or_str: str | model.User,
    ) -> list[model.UserAccessCasePolicy]:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(
            model.User, "root1_1"
        )  # type: ignore[assignment]
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
                x.read_col_set_id
                or x.write_col_set_id
                or x.read_case_set
                or x.write_case_set
            )
        ]

    def read_organization_share_case_policies(
        self,
        user_or_str: str | model.User,
    ) -> list[model.OrganizationShareCasePolicy]:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(
            model.User, "root1_1"
        )  # type: ignore[assignment]
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
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(
            model.User, "root1_1"
        )  # type: ignore[assignment]
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
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(
            model.User, "root1_1"
        )  # type: ignore[assignment]
        # Admin users have access to all CaseTypes
        if (
            self.role_map[CommonRole.ROOT] in user.roles
            or self.role_map[CommonRole.APP_ADMIN] in user.roles
            or self.role_map[CommonRole.REFDATA_ADMIN] in user.roles
        ):
            case_types: list[model.CaseType] = self.app.handle(
                command.CaseTypeCrudCommand(
                    user=root_user,
                    operation=CrudOperation.READ_ALL,
                )
            )
            return {x.id for x in case_types}  # type: ignore
        # Other users have access only to CaseTypes in CaseTypeSets assigned via policies
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
        case_type_set_members: list[model.CaseTypeSetMember] = self.app.handle(
            command.CaseTypeSetMemberCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return {
            x.case_type_id
            for x in case_type_set_members
            if x.case_type_set_id in case_type_set_ids
        }

    # TODO LSP-2883 not used anywhere yet
    def read_cols_with_any_right(
        self,
        user_or_str: str | model.User,
    ) -> set[UUID]:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(
            model.User, "root1_1"
        )  # type: ignore[assignment]
        # Admin users have access to all Cols
        if (
            self.role_map[CommonRole.ROOT] in user.roles
            or self.role_map[CommonRole.APP_ADMIN] in user.roles
            or self.role_map[CommonRole.REFDATA_ADMIN] in user.roles
        ):
            cols: list[model.Col] = self.app.handle(
                command.ColCrudCommand(
                    user=root_user,
                    operation=CrudOperation.READ_ALL,
                )
            )
            return {x.id for x in cols}  # type: ignore
        # Other users have access only to Cols in CaseTypeSets assigned via policies
        access_case_policies = self.read_user_access_case_policies_with_any_right(user)
        col_set_ids = set()
        for policy in access_case_policies:
            if policy.read_col_set_id:
                col_set_ids.add(policy.read_col_set_id)
            if policy.write_col_set_id:
                col_set_ids.add(policy.write_col_set_id)
        col_set_members: list[model.ColSetMember] = self.app.handle(
            command.ColSetMemberCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        return {x.col_id for x in col_set_members if x.col_set_id in col_set_ids}

    # TODO LSP-2883 not used anywhere yet, uses a key for cases as date. Why?
    def update_association_case_data_collection(
        self,
        user_or_str: str | model.User,
        cases_or_str: str | model.Case | list[str | model.Case],
        data_collections_or_str: set[str | model.DataCollection],
    ) -> list[model.CaseDataCollectionLink]:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(model.User, "root1_1")  # type: ignore[assignment]
        if not isinstance(cases_or_str, list):
            cases_or_str = [cases_or_str]
        cases: list[model.Case] = self.get_obj(  # type: ignore[assignment]
            model.Case, [self._convert_case_code_to_date(x) for x in cases_or_str]
        )
        data_collections: list[model.DataCollection] = self.get_obj(model.DataCollection, list(data_collections_or_str))  # type: ignore[assignment]
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
            self.set_obj(x)
        return resulting_case_data_collection_links

    def update_col_set_member(
        self,
        user_in: str | model.User,
        col_set_member: model.ColSetMember,
    ) -> model.ColSetMember:
        user: model.User = self.get_obj(model.User, user_in)  # type: ignore[assignment]
        updated_col_set_member: model.ColSetMember = self.handle(  # type: ignore[assignment]
            command.ColSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.UPDATE_ONE,
                objs=col_set_member,
            ),
        )
        return self.set_obj(
            updated_col_set_member, update=True
        )  # type: ignore[return-value]

    def update_user_own_organization(
        self,
        user_or_str: str | model.User,
        organization_or_str: str | None = None,
        set_dummy_organization: bool = False,
    ) -> model.User:
        user: model.User = self.get_obj(
            model.User, user_or_str
        )  # type: ignore[assignment]
        root_user: model.User = self.get_obj(
            model.User, "root1_1"
        )  # type: ignore[assignment]
        orig_organization_id = user.organization_id
        if not organization_or_str:
            if set_dummy_organization:
                organization_id: UUID = self.generate_id()
            else:
                raise ValueError(
                    "Organization not given and set_dummy_organization False"
                )
        else:
            if set_dummy_organization:
                raise ValueError("Organization given and set_dummy_organization True")
            organization_id = self.get_obj(model.Organization, organization_or_str).id
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
        return self.set_obj(user, update=True)  # type: ignore[return-value]

    # TODO LSP-2883 nit used anywhere yet, uses a key for cases as date. Why?
    def verify_case_content_access(
        self,
        expected_access: dict[tuple[str, str], list[str]],
    ) -> None:
        for key, expected_case_content in expected_access.items():
            user, case_code = key
            user: model.User = self.get_obj(
                model.User, user_or_str
            )  # type: ignore[assignment]
            full_case: model.Case = self.get_obj(  # type: ignore[assignment]
                model.Case, self._convert_case_code_to_date(case_code)
            )
            cases: list[model.Case] = self.handle(  # type: ignore[assignment]
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
            user: model.User = self.get_obj(
                model.User, user_str
            )  # type: ignore[assignment]
            case_types: list[model.CaseType] = self.handle(  # type: ignore[assignment]
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
                msg = f"User {user.name} CaseTypes mismatch. Missing: {missing_case_types}. Extra: {extra_case_types}."
                if self.verbose:
                    print(msg)
                raise ValueError(msg)

    def print_case_data_collection_links(self) -> None:

        root_user = self.get_root_user()
        cases: list[model.Case] = self.read_all(root_user, model.Case, cascade=True)  # type: ignore[assignment]
        data_collections: dict[UUID, model.DataCollection] = {
            x.id: x
            for x in self.read_all(root_user, model.DataCollection, cascade=True)  # type: ignore[assignment]
        }
        case_data_collection_links: list[model.CaseDataCollectionLink] = self.read_all(  # type: ignore[assignment]
            root_user, model.CaseDataCollectionLink, cascade=True
        )
        print("\nCaseDataCollectionLinks:")

        case_data_collection_link_sets: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
            ((x.case_id, x.data_collection_id) for x in case_data_collection_links),
            as_set=True,
        )
        for x in sorted(
            cases, key=lambda x: self._convert_case_date_to_code(x.case_date)
        ):
            if x.id in case_data_collection_link_sets:
                data_collection_str = ", ".join(
                    [
                        data_collections[y].name
                        for y in sorted(
                            case_data_collection_link_sets[x.id],
                            key=lambda z: data_collections[z].name,
                        )
                    ]
                )
                case_name = self._convert_case_date_to_code(x.case_date)

                print(f"{case_name}: {data_collection_str} ({x.id})")

    def print_case_types(self) -> None:
        root_user = self.get_root_user()
        case_types: list[model.CaseType] = self.read_all(root_user, model.CaseType, cascade=True)  # type: ignore[assignment]
        print("\nCaseTypes:")
        for x in sorted(case_types, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

    def print_case_type_sets(self) -> None:
        case_types: list[model.CaseType] = self.read_all(
            "root1_1", model.CaseType
        )  # type: ignore[assignment]
        case_type_map: dict[UUID, model.CaseType] = {
            x.id: x for x in case_types
        }  # type: ignore[assignment]
        case_type_sets: list[model.CaseTypeSet] = self.read_all(
            "root1_1", model.CaseTypeSet
        )  # type: ignore[assignment]
        case_type_set_members: list[model.CaseTypeSetMember] = (
            self.read_all(  # type: ignore[assignment]
                "root1_1", model.CaseTypeSetMember, cascade=False
            )
        )
        case_type_set_member_map: dict[UUID, set[UUID]] = (
            map_paired_elements(  # type: ignore[assignment]
                ((x.case_type_set_id, x.case_type_id) for x in case_type_set_members),
                as_set=True,
            )
        )
        print("\nCaseTypeSets:")
        for x in sorted(case_type_sets, key=lambda x: x.name):
            case_types_str = ", ".join(
                [
                    case_type_map[y].name
                    for y in sorted(
                        case_type_set_member_map.get(x.id, set()),
                        key=lambda z: case_type_map[z].name,
                    )
                ]
            )
            print(f"{x.name}: {case_types_str} ({x.id})")

    def print_cols(self) -> None:
        cols: list[model.Col] = self.read_all(
            "root1_1", model.Col
        )  # type: ignore[assignment]
        case_types: list[model.CaseType] = self.read_all(
            "root1_1", model.CaseType
        )  # type: ignore[assignment]
        case_type_map: dict[UUID, model.CaseType] = {
            x.id: x for x in case_types
        }  # type: ignore[assignment]
        ref_cols: list[model.RefCol] = self.read_all(
            "root1_1", model.RefCol
        )  # type: ignore[assignment]
        ref_col_map: dict[UUID, model.RefCol] = {
            x.id: x for x in ref_cols
        }  # type: ignore[assignment]
        print("\nCols:")
        for x in sorted(
            cols, key=lambda x: (case_type_map[x.case_type_id].name, x.code)
        ):
            case_type = case_type_map[x.case_type_id]
            ref_col = ref_col_map[x.ref_col_id]
            print(f"{x.code}: {case_type.name}, {ref_col.col_type.value} ({x.id})")

    def print_col_sets(self) -> None:
        cols: list[model.Col] = self.read_all(
            "root1_1", model.Col
        )  # type: ignore[assignment]
        col_map: dict[UUID, model.Col] = {  # type: ignore[assignment]
            x.id: x for x in cols
        }
        col_sets: list[model.ColSet] = self.read_all(
            "root1_1", model.ColSet
        )  # type: ignore[assignment]
        col_set_members: list[model.ColSetMember] = self.read_all(
            "root1_1", model.ColSetMember
        )  # type: ignore[assignment]
        col_set_member_map: dict[UUID, set[UUID]] = (
            map_paired_elements(  # type: ignore[assignment]
                ((x.col_set_id, x.col_id) for x in col_set_members),
                as_set=True,
            )
        )
        print("\nColSets:")
        for x in sorted(col_sets, key=lambda x: x.name):
            col_ids_str = ", ".join(
                [
                    str(col_map[y].id)
                    for y in sorted(
                        col_set_member_map.get(x.id, set()),
                        key=lambda z: col_map[z].code,
                    )
                ]
            )
            cols_str = ", ".join(
                [
                    col_map[y].code
                    for y in sorted(
                        col_set_member_map.get(x.id, set()),
                        key=lambda z: col_map[z].code,
                    )
                ]
            )
            print(f"{x.name}: {cols_str}\n({x.id}: {col_ids_str})")

    def print_organization_access_case_policies(self) -> None:

        root_user = self.get_root_user()
        organization_access_case_policies: list[model.OrganizationAccessCasePolicy] = (  # type: ignore[assignment]
            self.read_all(root_user, model.OrganizationAccessCasePolicy, cascade=True)
        )
        organizations: list[model.Organization] = self.read_all(  # type: ignore[assignment]
            root_user, model.Organization
        )
        organization_map = {x.id: x for x in organizations}
        data_collections: list[model.DataCollection] = self.read_all(  # type: ignore[assignment]
            root_user, model.DataCollection
        )
        data_collection_map = {x.id: x for x in data_collections}
        case_type_sets: list[model.CaseTypeSet] = self.read_all(  # type: ignore[assignment]
            root_user, model.CaseTypeSet
        )
        case_type_set_map = {x.id: x for x in case_type_sets}
        col_sets: list[model.ColSet] = self.read_all("root1_1", model.ColSet)  # type: ignore[assignment]
        col_set_map = {x.id: x for x in col_sets}
        print("\nOrganizationAccessCasePolicies:")
        for x in sorted(
            organization_access_case_policies,
            key=lambda x: (
                organization_map[x.organization_id].name,
                data_collection_map[x.data_collection_id].name,
            ),
        ):
            read_col_set_name = (
                col_set_map[x.read_col_set_id].name if x.read_col_set_id else None
            )
            write_col_set_name = (
                col_set_map[x.write_col_set_id].name if x.write_col_set_id else None
            )
            print(
                f"{organization_map[x.organization_id].name}/{data_collection_map[x.data_collection_id].name}: case_type_set={case_type_set_map[x.case_type_set_id].name}, is_private={x.is_private}, add/remove_case={x.add_case}/{x.remove_case}, read/write_col_set={read_col_set_name}/{write_col_set_name}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, read/write_case_set={x.read_case_set}/{x.write_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_user_access_case_policies(self) -> None:
        root_user = self.get_root_user()
        user_access_case_policies: list[model.UserAccessCasePolicy] = self.read_all(  # type: ignore[assignment]
            root_user, model.UserAccessCasePolicy, cascade=True
        )
        for user_access_case_policy in user_access_case_policies:
            # Get user with name filled in
            user: model.User = self.get_obj(  # type: ignore[assignment]
                model.User, user_access_case_policy.user.id
            )
            user_access_case_policy.user = user
        data_collections: list[model.DataCollection] = self.read_all(  # type: ignore[assignment]
            root_user, model.DataCollection
        )
        data_collection_map = {x.id: x for x in data_collections}
        case_type_sets: list[model.CaseTypeSet] = self.read_all(  # type: ignore[assignment]
            root_user, model.CaseTypeSet
        )
        case_type_set_map = {x.id: x for x in case_type_sets}
        col_sets: list[model.ColSet] = self.read_all(root_user, model.ColSet)
        col_set_map = {x.id: x for x in col_sets}
        print("\nUserAccessCasePolicies:")
        for x in sorted(
            user_access_case_policies,
            key=lambda x: (
                x.user.name,
                data_collection_map[x.data_collection_id].name,
            ),
        ):
            read_col_set_name = (
                col_set_map[x.read_col_set_id].name if x.read_col_set_id else None
            )
            write_col_set_name = (
                col_set_map[x.write_col_set_id].name if x.write_col_set_id else None
            )
            print(
                f"{x.user.name}/{data_collection_map[x.data_collection_id].name}: case_type_set={case_type_set_map[x.case_type_set_id].name}, add/remove_case={x.add_case}/{x.remove_case}, read/write_col_set={read_col_set_name}/{write_col_set_name}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, read/write_case_set={x.read_case_set}/{x.write_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_organization_share_case_policies(self) -> None:
        root_user = self.get_root_user()
        organization_share_case_policies: list[model.OrganizationShareCasePolicy] = (  # type: ignore[assignment]
            self.read_all(root_user, model.OrganizationShareCasePolicy)
        )
        organizations: list[model.Organization] = self.read_all(  # type: ignore[assignment]
            root_user, model.Organization
        )
        organization_map = {x.id: x for x in organizations}
        data_collections: list[model.DataCollection] = self.read_all(  # type: ignore[assignment]
            root_user, model.DataCollection
        )
        data_collection_map = {x.id: x for x in data_collections}
        case_type_sets: list[model.CaseTypeSet] = self.read_all(  # type: ignore[assignment]
            root_user, model.CaseTypeSet
        )
        case_type_set_map = {x.id: x for x in case_type_sets}
        print("\nOrganizationShareCasePolicies:")
        for x in sorted(
            organization_share_case_policies,
            key=lambda x: (
                organization_map[x.organization_id].name,
                data_collection_map[x.data_collection_id].name,
                data_collection_map[x.from_data_collection_id].name,
            ),
        ):
            print(
                f"{organization_map[x.organization_id].name}/{data_collection_map[x.data_collection_id].name}<-{data_collection_map[x.from_data_collection_id].name}: case_type_set={case_type_set_map[x.case_type_set_id].name}, add/remove_case={x.add_case}/{x.remove_case}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_user_share_case_policies(self) -> None:
        root_user = self.get_root_user()
        user_share_case_policies: list[model.UserShareCasePolicy] = self.read_all(  # type: ignore[assignment]
            root_user, model.UserShareCasePolicy
        )
        for user_share_case_policy in user_share_case_policies:
            # Get user with name filled in
            user: model.User = self.get_obj(  # type: ignore[assignment]
                model.User, user_share_case_policy.user_id
            )
            user_share_case_policy.user = user
        case_type_sets: list[model.CaseTypeSet] = self.read_all(  # type: ignore[assignment]
            root_user, model.CaseTypeSet
        )
        case_type_set_map = {x.id: x for x in case_type_sets}
        data_collections: list[model.DataCollection] = self.read_all(  # type: ignore[assignment]
            root_user, model.DataCollection
        )
        data_collection_map: dict[UUID, model.DataCollection] = {
            x.id: x
            for x in cast(
                list[model.DataCollection],
                self.read_all(root_user, model.DataCollection),
            )
        }
        print("\nUserShareCasePolicies:")
        for x in sorted(
            user_share_case_policies,
            key=lambda x: (
                x.user.name,
                data_collection_map[x.data_collection_id].name,
                data_collection_map[x.from_data_collection_id].name,
            ),
        ):
            print(
                f"{x.user.name}/{data_collection_map[x.data_collection_id].name}<-{data_collection_map[x.from_data_collection_id].name}: case_type_set={case_type_set_map[x.case_type_set_id].name}, , add/remove_case={x.add_case}/{x.remove_case}, add/remove_case_set={x.add_case_set}/{x.remove_case_set}, is_active={x.is_active} ({x.id})"
            )

    def print_cases(self, case_codes: list[str] | None = None) -> None:

        root_user = self.get_root_user()

        cases: list[model.Case] = self.read_all(root_user, model.Case)  # type: ignore[assignment]
        if case_codes:
            cases = [
                x.code
                for x in cases
                # if self._convert_case_date_to_code(x.case_date) in case_codes
            ]
        case_data_collection_links: list[model.CaseDataCollectionLink] = self.read_all(  # type: ignore[assignment]
            root_user, model.CaseDataCollectionLink
        )
        data_collections: list[model.DataCollection] = self.read_all(  # type: ignore[assignment]
            root_user, model.DataCollection
        )
        data_collection_map = {x.id: x for x in data_collections}
        cols: list[model.Col] = self.read_all(root_user, model.Col)  # type: ignore[assignment]
        col_map = {x.id: x for x in cols}
        case_date_collections = map_paired_elements(
            ((x.case_id, x.data_collection_id) for x in case_data_collection_links),
            as_set=True,
        )
        print("\nCases:")
        for x in sorted(cases, key=lambda x: x.case_date):
            curr_data_collections = sorted(
                [
                    data_collection_map[x].name
                    for x in case_date_collections.get(x.id, set())
                ]
            )
            curr_data_collections = ", ".join(curr_data_collections)
            curr_content = sorted([(col_map[x].code, y) for x, y in x.content.items()])
            curr_content = ", ".join([f"{x[0]}={x[1]}" for x in curr_content])
            print(
                f"{self._convert_case_date_to_code(x.case_date)}: {curr_content}; {curr_data_collections} ({x.id})"
            )

    def get_obj(
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
    ) -> model.Model | list[model.Model] | None:
        if isinstance(obj, list):
            return [self.get_obj(model_class, x) for x in obj]
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key = self._get_obj_key(table, model_class, obj, on_missing)
        if model_class == model.CaseDataCollectionLink:
            dc_id = key[0]
            case_id = key[1]

            case_data_collection_links: list[model.CaseDataCollectionLink] = self.read_all(  # type: ignore[assignment]
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

    # TODO LSP-2883 is used by a lot of methods that are not used anywhere yet, and uses a key for cases as date. Why?
    @staticmethod
    def _convert_case_code_to_date(code: str) -> datetime:
        m = re.match(r"^([a-z_]*)(\d+)_(\d+)$", code.lower())
        if not m:
            raise ValueError(f"Invalid code {code}")
        case_type_index = int(m.group(2))
        assert case_type_index < 13
        case_index = int(m.group(3))
        return datetime(
            year=1900 + case_index,  # Store case_index in year
            month=case_type_index,  # Store case_type_index in month
            day=1,  # Fixed day value
        )

    @staticmethod
    def _convert_case_date_to_code(case_date: datetime) -> str:
        case_type_index = int(case_date.month)  # Get case_type_index from month
        case_index = int(case_date.year - 1900)  # Get case_index from year offset
        return f"case{case_type_index}_{case_index}"
        return f"case{case_type_index}_{case_index}"
        return f"case{case_type_index}_{case_index}"
