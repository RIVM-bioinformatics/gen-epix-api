import datetime
import logging
import re
from test.casedb.casedb_endpoint_test_client import CasedbEndpointTestClient
from test.test_client.enum import RepositoryType as TestClientRepositoryType
from test.test_client.enum import TestType
from test.test_client.service_test_client import ServiceTestClient
from test.test_client.util import get_test_name, get_test_output_dir
from time import sleep
from typing import Type, TypeVar
from uuid import UUID

import gen_epix.casedb.domain.model.case.case
from gen_epix.casedb.app_setup import create_fast_api
from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.command.role import RoleGenerator
from gen_epix.casedb.domain.enum import RepositoryType, Role, ServiceType
from gen_epix.casedb.env import AppEnv
from gen_epix.common.api.exc import LAST_HANDLED_EXCEPTION
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import FilterType, TypedEqualsUuidFilter, TypedUuidSetFilter
from util.cfg import AppCfg
from util.util import map_paired_elements

APP_NAME = "CASEDB"
APP_CFG = AppCfg(APP_NAME, enum.ServiceType, enum.RepositoryType)
APP_CFG.setup_logger.setLevel(logging.WARNING)

BASE_MODEL_TYPE = TypeVar("T", bound=model.Model)


class OrganismType(enum.Enum):
    ORGANISM = "ORGANISM"
    TOXIN = "TOXIN"
    UNKNOWN = "UNKNOWN"


class CasedbServiceTestClient(ServiceTestClient):
    DEFAULT_LOAD_TARGET = "empty"

    MODEL_KEY_MAP = {
        model.User: "name",
        model.UserInvitation: "email",
        model.Organization: "name",
        model.OrganizationAdminPolicy: ("organization_id", "user_id"),
        model.Disease: "name",
        model.EtiologicalAgent: "name",
        model.Etiology: ("disease_id", "etiological_agent_id"),
        model.CaseType: "name",
        model.CaseTypeSetCategory: "name",
        model.CaseTypeSet: "name",
        model.Concept: "abbreviation",
        model.ConceptSet: "name",
        model.CaseTypeSetMember: ("case_type_set_id", "case_type_id"),
        model.CaseTypeColSetMember: ("case_type_col_set_id", "case_type_col_id"),
        model.ConceptSetMember: ("concept_set_id", "concept_id"),
        model.RegionSet: "code",
        model.RegionSetShape: ("region_set_id", "scale"),
        model.Region: ("region_set_id", "code"),
        gen_epix.casedb.domain.model.case.case.GeneticDistanceProtocol: "name",
        model.Dim: "code",
        model.Col: "code",
        model.CaseTypeCol: "code",
        model.CaseTypeColSet: "name",
        model.DataCollection: "name",
        model.DataCollectionRelation: (
            "from_data_collection_id",
            "to_data_collection_id",
        ),
        model.Case: "case_date",
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
        enum.ColType.REGEX: ".*",
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
        test_type: TestType = TestType.CASEDB_CUSTOM,
        repository_type: enum.RepositoryType = enum.RepositoryType.DICT,
        load_target: str = DEFAULT_LOAD_TARGET,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        **kwargs: dict,
    ) -> "ServiceTestClient":
        """
        Create a test environment for the given test type and repository type. A
        single environment, with a common test directory, is kept for each test type.
        """
        key = (test_type, repository_type, load_target)
        if key not in ServiceTestClient.TEST_CLIENTS:
            test_dir = None
            for stored_key, stored_env in ServiceTestClient.TEST_CLIENTS.items():
                stored_test_type, _, _ = stored_key
                if stored_test_type == test_type:
                    test_dir = stored_env.test_dir
                    break
            ServiceTestClient.TEST_CLIENTS[key] = CasedbServiceTestClient(
                test_type=test_type,
                repository_type=repository_type,
                load_target=load_target,
                verbose=verbose,
                log_level=log_level,
                log_setup=log_setup,
                test_dir=test_dir,
                **kwargs,
            )
        return ServiceTestClient.TEST_CLIENTS[key]

    def __init__(
        self,
        test_type: TestType = TestType.UNDEFINED,
        repository_type: RepositoryType = RepositoryType.DICT,
        load_target: str = DEFAULT_LOAD_TARGET,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        log_setup: bool = False,
        test_dir: str | None = None,
        **kwargs: bool | str | int | dict,
    ):
        test_client_repository_type = TestClientRepositoryType(repository_type.value)

        # Set up test name and directory
        app_cfg = APP_CFG
        cfg = app_cfg.cfg
        test_name = get_test_name(test_type)
        test_dir: str = test_dir or get_test_output_dir(test_name)

        # Set and adjust cfg
        app_cfg.cfg.app.debug = True
        app_cfg.cfg.secret["db"]["repository_type"] = repository_type
        # Adjust cfg for root user
        curr_cfg = app_cfg.cfg.secret.root
        curr_cfg.organization.name = "org1"
        curr_cfg.user.email = "root1_1@org1.org"
        # Copy any repository files to test directory
        ServiceTestClient._init_repositories(
            app_cfg.cfg.secret.repository[repository_type.value],
            set(ServiceType),
            test_client_repository_type,
            load_target,
            test_dir,
        )

        # Create app
        ServiceTestClient._set_log_level(app_cfg, log_level)
        app_env = AppEnv(app_cfg, log_setup=log_setup, **kwargs)

        # Create endpoint test client if endpoints are to be used (including own
        # app_env), otherwise construct app env separately
        use_endpoints: bool = kwargs.pop("use_endpoints", False)
        endpoint_test_client: CasedbEndpointTestClient | None = None
        app_last_handled_exception: dict | None = None
        if use_endpoints:
            fast_api = create_fast_api(
                cfg,
                app=app_env.app,
                registered_user_dependency=app_env.registered_user_dependency,
                new_user_dependency=app_env.new_user_dependency,
                idp_user_dependency=app_env.idp_user_dependency,
                app_id=app_env.app.generate_id(),
                setup_logger=app_cfg.setup_logger if log_setup else None,
                api_logger=app_cfg.api_logger,
                debug=True,
                update_openapi_schema=True,
            )
            app_last_handled_exception = LAST_HANDLED_EXCEPTION
            endpoint_test_client = CasedbEndpointTestClient(
                app_env.app, fast_api, app_last_handled_exception, **kwargs
            )

        # Call base class constructor
        super().__init__(
            app_env,
            app_cfg,
            test_type=test_type,
            test_name=test_name,
            test_dir=test_dir,
            repository_type=test_client_repository_type,
            load_target=load_target,
            roles=enum.Role,
            role_hierarchy=RoleGenerator.ROLE_HIERARCHY,
            user_class=model.User,
            verbose=verbose,
            log_level=log_level,
            use_endpoints=use_endpoints,
            endpoint_test_client=endpoint_test_client,
            app_last_handled_exception=app_last_handled_exception,
            **kwargs,
        )

    def create_organization(
        self, user: str | model.User, organization_name: str
    ) -> model.Organization:
        user = self._get_obj(model.User, user)
        organization = self.app.handle(
            command.OrganizationCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Organization(
                    name=organization_name, legal_entity_code=organization_name
                ),
            )
        )
        return self._set_obj(organization)

    def invite_and_register_user(
        self,
        user: str | model.User,
        user_name: str,
        # by_admin: bool = False,
        set_dummy_organization: bool = False,
        set_dummy_token: bool = False,
    ) -> model.User:
        user: model.User = self._get_obj(model.User, user)
        m = re.match(r"^(.*?)(\d+)_(\d+)$", user_name.lower())
        if not m:
            raise ValueError(f"Invalid user name {user_name}")
        role = [x for x in Role if x.value.lower() == m.group(1).lower()][0]
        organization_name = "org" + m.group(2)
        if organization_name not in self.db[model.Organization]:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                raise ValueError(f"Organization {organization_name} not found")
        else:
            organization_id = self.db[model.Organization][organization_name].id
        cmd_class = command.InviteUserCommand
        user_invitation = self.handle(
            cmd_class(
                user=user,
                email=f"{user_name}@{organization_name}.org",
                roles={role},
                organization_id=organization_id,
            )
        )
        if set_dummy_token:
            user_invitation.token = str(self.generate_id())
        tgt_user = self.handle(
            command.RegisterInvitedUserCommand(
                user=model.User(
                    email=f"{user_name}@{organization_name}.org",
                    organization_id=organization_id,
                    roles={role},
                ),
                token=user_invitation.token,
            )
        )
        tgt_user.name = user_name
        return self._set_obj(tgt_user)

    def create_org_admin_policy(
        self,
        user: str | model.User,
        tgt_user: str | model.User,
        organization: str | model.Organization,
        is_active: bool = True,
    ) -> model.OrganizationAdminPolicy:
        user = self._get_obj(model.User, user)
        tgt_user = self._get_obj(model.User, tgt_user)
        organization = self._get_obj(model.Organization, organization)
        organization_admin_policy = self.app.handle(
            command.OrganizationAdminPolicyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.OrganizationAdminPolicy(
                    organization_id=organization.id,
                    user_id=tgt_user.id,
                    is_active=is_active,
                ),
            )
        )
        return self._set_obj(organization_admin_policy)

    def create_concept(
        self,
        user: str | model.User,
        abbreviation: str,
    ) -> model.Concept:
        user: model.User = self._get_obj(model.User, user)
        concept = self.handle(
            command.ConceptCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Concept(
                    abbreviation=abbreviation,
                ),
            )
        )
        return self._set_obj(concept)

    def create_concept_set(
        self,
        user: str | model.User,
        code: str,
        concepts: set[str | model.Concept],
        concept_set_type: enum.ConceptSetType,
        regex: str | None = None,
        schema_definition: str | None = None,
        schema_uri: str | None = None,
        set_dummy_concepts: bool = False,
    ) -> model.ConceptSet:
        user: model.User = self._get_obj(model.User, user)
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
        if set_dummy_concepts:
            concept_ids = [self.generate_id() for _ in concepts]
        else:
            concept_ids = [self._get_obj(model.Concept, x).id for x in concepts]
        concept_set_members = self.handle(
            command.ConceptSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_SOME,
                objs=[
                    model.ConceptSetMember(
                        concept_set_id=concept_set.id,
                        concept_id=x,
                        rank=(
                            i
                            if concept_set_type
                            in {
                                enum.ConceptSetType.ORDINAL,
                                enum.ConceptSetType.INTERVAL,
                            }
                            else None
                        ),
                    )
                    for i, x in enumerate(concept_ids)
                ],
            )
        )
        return self._set_obj(concept_set)

    def create_region_set(
        self,
        user: str | model.User,
        code: str,
    ) -> model.RegionSet:
        user: model.User = self._get_obj(model.User, user)
        region_set = self.handle(
            command.RegionSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.RegionSet(
                    code=code,
                    name=code,
                    region_code_as_label=False,
                ),
            )
        )
        return self._set_obj(region_set)

    def create_region_set_shape(
        self,
        user: str | model.User,
        region_set: str | model.RegionSet,
        scale: float,
        set_dummy_region_set: bool = False,
    ) -> model.RegionSetShape:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(region_set_shape)

    def create_region(
        self,
        user: str | model.User,
        code: str,
        region_set: str | model.RegionSet,
        set_dummy_region_set: bool = False,
    ) -> model.Region:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(region)

    def create_genetic_distance_protocol(
        self,
        user: str | model.User,
        name: str,
        seqdb_seq_distance_protocol_id: UUID | None = None,
        min_scale_unit: float = 1,
    ) -> gen_epix.casedb.domain.model.case.case.GeneticDistanceProtocol:
        user: model.User = self._get_obj(model.User, user)
        seqdb_seq_distance_protocol_id = (
            self.generate_id()
            if not seqdb_seq_distance_protocol_id
            else seqdb_seq_distance_protocol_id
        )
        genetic_distance_protocol = self.handle(
            command.GeneticDistanceProtocolCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=gen_epix.casedb.domain.model.case.case.GeneticDistanceProtocol(
                    name=name,
                    seqdb_seq_distance_protocol_id=seqdb_seq_distance_protocol_id,
                    min_scale_unit=min_scale_unit,
                ),
            )
        )
        return self._set_obj(genetic_distance_protocol)

    def create_dim(
        self,
        user: str | model.User,
        code: str,
        dim_type: enum.DimType,
    ) -> model.Dim:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(dim)

    def create_col(
        self,
        user: str | model.User,
        code: str,
        col_type: enum.ColType,
        concept_set: str | model.ConceptSet | None = None,
        region_set: str | model.RegionSet | None = None,
        genetic_distance_protocol: (
            str | gen_epix.casedb.domain.model.case.case.GeneticDistanceProtocol | None
        ) = None,
        set_dummy_dim: bool = False,
        set_dummy_concept_set: bool = False,
        set_dummy_region_set: bool = False,
        set_dummy_genetic_distance_protocol: bool = False,
    ) -> model.Col:
        user: model.User = self._get_obj(model.User, user)
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
                    gen_epix.casedb.domain.model.case.case.GeneticDistanceProtocol,
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
        return self._set_obj(col)

    def create_disease(
        self, user: str | model.User, disease_name: str
    ) -> model.Disease:
        user: model.User = self._get_obj(model.User, user)
        disease = self.handle(
            command.DiseaseCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Disease(name=disease_name),
            )
        )
        return self._set_obj(disease)

    def create_etiological_agent(
        self, user: str | model.User, etiological_agent_name: str
    ) -> model.EtiologicalAgent:
        user = self._get_obj(model.User, user)
        etiological_agent = self.app.handle(
            command.EtiologicalAgentCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.EtiologicalAgent(
                    name=etiological_agent_name, type=OrganismType.ORGANISM.value
                ),
            )
        )
        return self._set_obj(etiological_agent)

    def create_etiology(
        self,
        user: str | model.User,
        disease: str | model.Disease | None,
        etiological_agent: str | model.EtiologicalAgent | None,
        set_dummy_disease: bool = False,
        set_dummy_etiological_agent: bool = False,
    ) -> model.Etiology:
        user = self._get_obj(model.User, user)
        etiology = self.app.handle(
            command.EtiologyCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.Etiology(
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
        return self._set_obj(etiology)

    def create_data_collection(
        self,
        user: str | model.User,
        name: str,
    ) -> model.DataCollection:
        user: model.User = self._get_obj(model.User, user)
        data_collection = self.handle(
            command.DataCollectionCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.DataCollection(
                    name=name,
                ),
            )
        )
        return self._set_obj(data_collection)

    def create_case_type(
        self,
        user: str | model.User,
        case_type: str | model.CaseType,
        disease: str | model.Disease | None,
        etiological_agent: str | model.EtiologicalAgent | None,
        set_dummy_disease: bool = False,
        set_dummy_etiological_agent: bool = False,
    ) -> model.CaseType:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(case_type)

    def create_case_type_set_member(
        self,
        user: str | model.User,
        case_type_set: str | model.CaseTypeSet,
        case_type: str | model.CaseType,
        set_dummy_case_type_set: bool = False,
        set_dummy_case_type: bool = False,
    ) -> model.CaseTypeSetMember:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(case_type_set_member)

    def create_case_type_set_category(
        self,
        user: str | model.User,
        case_type_set_category: str | model.CaseTypeSetCategory,
        rank: int = 0,
    ) -> model.CaseTypeSetCategory:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(case_type_set_category)

    def create_case_type_set(
        self,
        user: str | model.User,
        case_type_set: str | model.CaseTypeSet,
        case_types: set[str | model.CaseType],
        case_type_set_category: str | model.CaseTypeSetCategory | None,
        rank: int = 0,
        set_dummy_case_type_set_category: bool = False,
        set_dummy_case_types: bool = False,
    ) -> model.CaseTypeSet:
        user: model.User = self._get_obj(model.User, user)
        if set_dummy_case_type_set_category:
            case_type_set_category_id = self.generate_id()
        else:
            case_type_set_category_id = self._get_obj(
                model.CaseTypeSetCategory, case_type_set_category
            ).id
        case_type_set = self.handle(
            command.CaseTypeSetCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseTypeSet(
                    name=case_type_set,
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
                    model.CaseTypeSetMember(
                        case_type_set_id=case_type_set.id,
                        case_type_id=x,
                    )
                    for x in case_type_ids
                ],
            )
        )
        for case_type_set_member in case_type_set_members:
            self._set_obj(case_type_set_member)
        return self._set_obj(case_type_set)

    def create_case_type_col(
        self,
        user: str | model.User,
        code: str,
        genetic_sequence_case_type_col_id: UUID | None = None,
        tree_algorithm_codes: set[enum.TreeAlgorithmType] | None = None,
        occurrence: int | None = None,
        col: str | model.Col | None = None,
        set_dummy_case_type: bool = False,
        set_dummy_col: bool = False,
    ) -> model.CaseTypeCol:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(case_type_col)

    def create_case_type_col_set(
        self,
        user: str | model.User,
        case_type_col_set: str | model.CaseTypeColSet,
        case_type_cols: set[str | model.CaseTypeCol],
        set_dummy_case_type_cols: bool = False,
    ) -> model.CaseTypeColSet:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(case_type_col_set)

    def create_case_type_col_set_member(
        self,
        user: str | model.User,
        case_type_col_set: str | model.CaseTypeColSet,
        case_type_col: str | model.CaseTypeCol,
    ) -> model.CaseTypeColSetMember:
        user: model.User = self._get_obj(model.User, user)
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
        return self._set_obj(case_type_col_set_member)

    def create_organization_access_case_policy(
        self,
        user: str | model.User,
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
        user = self._get_obj(model.User, user)
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
        return self._set_obj(organization_access_case_policy)

    def create_user_access_case_policy(
        self,
        user: str | model.User,
        tgt_user: str | model.User,
        data_collection: str | model.DataCollection,
        case_type_set: str | model.CaseTypeSet,
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
        user: model.User = self._get_obj(model.User, user)
        tgt_user: model.User = self._get_obj(model.User, tgt_user)
        case_type_set = self._get_obj(model.CaseTypeSet, case_type_set)
        data_collection = self._get_obj(model.DataCollection, data_collection)
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
        return self._set_obj(user_access_case_policy)

    def create_organization_share_case_policy(
        self,
        user: str | model.User,
        name: str,
        case_type_set: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        add_case_set: bool = True,
        remove_case_set: bool = True,
    ) -> model.OrganizationShareCasePolicy:
        user = self._get_obj(model.User, user)
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
        return self._set_obj(organization_share_case_policy)

    def create_user_share_case_policy(
        self,
        user: str | model.User,
        tgt_user: str | model.User,
        data_collection: str | model.DataCollection,
        from_data_collection: str | model.DataCollection,
        case_type_set: str | model.CaseTypeSet,
        is_active: bool = True,
        add_case: bool = True,
        remove_case: bool = True,
        add_case_set: bool = True,
        remove_case_set: bool = True,
    ) -> model.UserShareCasePolicy:
        user: model.User = self._get_obj(model.User, user)
        tgt_user: model.User = self._get_obj(model.User, tgt_user)
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
        return self._set_obj(user_share_case_policy)

    def create_case(
        self,
        user: str | model.User,
        code: str,
        data_collections: (
            str | model.DataCollection | list[str] | list[model.DataCollection]
        ),
        col_index_pattern: str | None = None,
    ) -> model.Case:
        user: model.User = self._get_obj(model.User, user)
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
            value = ServiceTestClient.DUMMY_VALUES[col.col_type]
            if col.col_type == enum.ColType.TEXT:
                value = f"{case_index}_{col_index}"
            elif col.col_type in {
                enum.ColType.NOMINAL,
                enum.ColType.ORDINAL,
                enum.ColType.INTERVAL,
            }:
                concept_set_members = self.read_some_by_property(
                    root_user,
                    model.ConceptSetMember,
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
            command.CasesCreateCommand(
                user=user,
                cases=[
                    model.Case(
                        case_type_id=case_type.id,
                        # subject_id=self.generate_id(),
                        created_in_data_collection_id=created_in_data_collection_id,
                        case_date=ServiceTestClient._convert_case_code_to_date(code),
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
        return self._set_obj(case)

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
        return self._set_obj(case_data_collection_link)

    def create_case_set_category(
        self,
        user: str | model.User,
        name: str | model.CaseSetCategory,
    ) -> model.CaseSetCategory:
        user: model.User = self._get_obj(model.User, user)
        case_set_category = self.handle(
            command.CaseSetCategoryCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseSetCategory(name=name, description=name),
            )
        )
        return self._set_obj(case_set_category)

    def create_case_set_status(
        self,
        user: str | model.User,
        name: str | model.CaseSetStatus,
    ) -> model.CaseSetStatus:
        user: model.User = self._get_obj(model.User, user)
        case_set_status = self.handle(
            command.CaseSetStatusCrudCommand(
                user=user,
                operation=CrudOperation.CREATE_ONE,
                objs=model.CaseSetStatus(name=name, description=name),
            )
        )
        return self._set_obj(case_set_status)

    def create_case_set(
        self,
        user: str | model.User,
        code: str,
        case_set_category: str | model.CaseSetCategory,
        case_set_status: str | model.CaseSetStatus,
        data_collections: (
            str | model.DataCollection | list[str] | list[model.DataCollection]
        ),
        cases: list[model.Case] | list[str] | None = None,
    ) -> model.Case:
        user: model.User = self._get_obj(model.User, user)
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
                [ServiceTestClient._convert_case_code_to_date(x) for x in cases],
            )
            case_ids = [x.id for x in cases]
        else:
            case_ids = None
        # Create the case set
        case_set = self.handle(
            command.CaseSetCreateCommand(
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
        case_set = self._set_obj(case_set)
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

    def update_user(
        self,
        user: str | model.User,
        tgt_user: str | model.User,
        is_active: bool | None = None,
        roles: set[enum.Role] | None = None,
        organization: str | None = None,
        set_dummy_organization: bool = False,
    ) -> model.User:
        user = self._get_obj(model.User, user)
        tgt_user = self._get_obj(model.User, tgt_user, copy=True)
        if not organization:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                organization_id = None
        else:
            if set_dummy_organization:
                raise ValueError("Organization given and set_dummy_organization True")
            organization_id = self._get_obj(model.Organization, organization).id
        has_updates = False
        if is_active is not None and tgt_user.is_active != is_active:
            has_updates = True
            tgt_user.is_active = is_active
        if roles is not None and tgt_user.roles != roles:
            has_updates = True
            tgt_user.roles = roles
        if organization_id is not None and tgt_user.organization_id != organization_id:
            has_updates = True
            tgt_user.organization_id = organization_id
        sleep(0.000000001)  # To avoid having same _modified_at as tgt_user
        updated_tgt_user = self.handle(
            command.UpdateUserCommand(
                user=user,
                tgt_user_id=tgt_user.id,
                is_active=is_active,
                roles=roles,
                organization_id=organization_id,
            )
        )
        updated_tgt_user.name = tgt_user.name
        ServiceTestClient._verify_updated_obj(
            tgt_user, updated_tgt_user, user.id, verify_modified=has_updates
        )
        return self._set_obj(updated_tgt_user, update=True)

    def temp_update_user_own_organization(
        self,
        user: str | model.User,
        organization: str | None = None,
        set_dummy_organization: bool = False,
    ) -> model.User:
        user: model.User = self._get_obj(model.User, user)
        root_user: model.User = self._get_obj(model.User, "root1_1")
        orig_organization_id = user.organization_id
        if not organization:
            if set_dummy_organization:
                organization_id = self.generate_id()
            else:
                raise ValueError(
                    "Organization not given and set_dummy_organization False"
                )
        else:
            if set_dummy_organization:
                raise ValueError("Organization given and set_dummy_organization True")
            organization_id = self._get_obj(model.Organization, organization).id
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
        return self._set_obj(user, update=True)

    # def update_user_access_case_policy(
    #     self,
    #     user: str | model.User,
    #     props: dict[str, Any | None],
    #     set_dummy_link: dict[str, bool] | bool = False,
    #     exclude_none: bool = True,
    #     new_case_type_set: str | model.CaseTypeSet | None = None,
    #     new_data_collection: str | model.DataCollection | None = None,
    #     new_is_active: bool | None = None,
    #     new_add_case: bool | None = None,
    #     new_remove_case: bool | None = None,
    #     new_read_case_type_col_set: str | model.CaseTypeColSet | None = None,
    #     new_write_case_type_col_set: str | model.CaseTypeColSet | None = None,
    #     new_add_case_set: bool | None = None,
    #     new_remove_case_set: bool | None = None,
    #     new_read_case_set: bool | None = None,
    #     new_write_case_set: bool | None = None,
    # ) -> model.UserAccessCasePolicy:
    #     root_user: model.User = self._get_obj(model.User, "root1_1")
    #     user: model.User = self._get_obj(model.User, user)
    #     tgt_user: model.User = self._get_obj(model.User, props["tgt_user"])
    #     data_collection: model.DataCollection = self._get_obj(
    #         model.DataCollection, props["data_collection"]
    #     )
    #     case_type_set: model.CaseTypeSet = self._get_obj(
    #         model.CaseTypeSet, props["case_type_set"]
    #     )
    #     read_case_type_col_set: model.CaseTypeColSet = self._get_obj(
    #         model.CaseTypeColSet, props["read_case_type_col_set"]
    #     )
    #     write_case_type_col_set: model.CaseTypeColSet = self._get_obj(
    #         model.CaseTypeColSet, props["write_case_type_col_set"]
    #     )
    #     user_access_case_policies = self.handle(
    #         command.UserAccessCasePolicyCrudCommand(
    #             user=root_user,
    #             operation=CrudOperation.READ_ALL,
    #         )
    #     )
    #     user_access_case_policies = [
    #         x
    #         for x in user_access_case_policies
    #         if x.user_id == tgt_user.id and x.data_collection_id == data_collection.id
    #     ]
    #     if len(user_access_case_policies) == 0:
    #         raise exc.UnauthorizedAuthError(
    #             f"User case policy not found: {tgt_user.name}, {data_collection.name}"
    #         )
    #     user_access_case_policy = user_access_case_policies[0]
    #     # Update policy
    #     props.pop("tgt_user")
    #     props["user"] = tgt_user
    #     props["data_collection"] = new_data_collection or data_collection
    #     props["case_type_set"] = new_case_type_set or case_type_set
    #     props["is_active"] = new_is_active or user_access_case_policy.is_active
    #     props["add_case"] = new_add_case or user_access_case_policy.add_case
    #     props["remove_case"] = new_remove_case or user_access_case_policy.remove_case
    #     props["read_case_type_col_set"] = (
    #         new_read_case_type_col_set or read_case_type_col_set
    #     )
    #     props["write_case_type_col_set"] = (
    #         new_write_case_type_col_set or write_case_type_col_set
    #     )
    #     props["add_case_set"] = new_add_case_set or user_access_case_policy.add_case_set
    #     props["remove_case_set"] = (
    #         new_remove_case_set or user_access_case_policy.remove_case_set
    #     )
    #     props["read_case_set"] = (
    #         new_read_case_set or user_access_case_policy.read_case_set
    #     )
    #     props["write_case_set"] = (
    #         new_write_case_set or user_access_case_policy.write_case_set
    #     )
    #     return self.update_object(  # type: ignore
    #         user,
    #         model.UserAccessCasePolicy,
    #         user_access_case_policy,
    #         props,
    #         set_dummy_link=set_dummy_link,
    #         exclude_none=exclude_none,
    #     )

    def update_association_case_data_collection(
        self,
        user: str | model.User,
        cases: str | model.Case | list[str | model.Case],
        data_collections: set[str | model.DataCollection],
    ) -> list[model.CaseDataCollectionLink]:
        user: model.User = self._get_obj(model.User, user)
        root_user: model.User = self._get_obj(model.User, "root1_1")
        if not isinstance(cases, list):
            cases = [cases]
        cases = self._get_obj(
            model.Case, [ServiceTestClient._convert_case_code_to_date(x) for x in cases]
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
        resulting_case_data_collection_links = self.handle(
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
        case_type_col_set_member_in: str | model.CaseTypeColSetMember,
    ) -> model.CaseTypeColSetMember:
        user = self._get_obj(model.User, user_in)
        case_type_col_set_member = self._get_obj(
            model.CaseTypeColSetMember, case_type_col_set_member_in
        )
        sleep(0.000000001)
        updated_case_type_col_set_member = self.handle(
            command.CaseTypeColSetMemberCrudCommand(
                user=user,
                operation=CrudOperation.UPDATE_ONE,
                objs=case_type_col_set_member,
            ),
        )
        return self._set_obj(updated_case_type_col_set_member, update=True)

    def read_all_users(self) -> list[model.User]:
        return self.services[ServiceType.ORGANIZATION].crud(
            command.UserCrudCommand(
                user=None,
                operation=CrudOperation.READ_ALL,
            )
        )

    def read_users_by_role(self, role: enum.Role) -> list[model.User]:
        users = self.read_all_users()
        return [x for x in users if role in x.roles]

    def verify_case_content_access(
        self,
        expected_access: dict[tuple[str, str], list[str]],
    ) -> None:
        for key, expected_case_content in expected_access.items():
            user, case_code = key
            user: model.User = self._get_obj(model.User, user)
            full_case = self._get_obj(
                model.Case, ServiceTestClient._convert_case_code_to_date(case_code)
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
        for user, expected_case_types in expected_access.items():
            user: model.User = self._get_obj(model.User, user)
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

    def get_org_ids_for_org_admin(
        self,
        user: str | model.User,
        include_self: bool = False,
        on_no_admin: str = "raise",
    ) -> list[model.Organization]:
        user: model.User = self._get_obj(model.User, user)
        org_admin_policies = [
            x
            for x in self.db[model.OrganizationAdminPolicy].values()
            if x.user_id == user.id
        ]
        if not org_admin_policies:
            if on_no_admin == "raise":
                raise ValueError(f"User {user.name} is not an organization admin")
            elif on_no_admin == "return":
                return []
        organization_ids = {x.organization_id for x in org_admin_policies}
        if include_self:
            organization_ids.add(user.organization_id)
        return organization_ids

    def get_users_for_org_admin(
        self,
        user: str | model.User,
        include_self: bool = False,
        on_no_admin: str = "raise",
    ) -> list[model.User]:
        user: model.User = self._get_obj(model.User, user)
        org_admin_policies = [
            x
            for x in self.db[model.OrganizationAdminPolicy].values()
            if x.user_id == user.id
        ]
        if not org_admin_policies:
            if on_no_admin == "raise":
                raise ValueError(f"User {user.name} is not an organization admin")
            elif on_no_admin == "return":
                return []
        organization_ids = {x.organization_id for x in org_admin_policies}
        if include_self:
            organization_ids.add(user.organization_id)
        tgt_users = list(self.db[model.User].values())
        return [x for x in tgt_users if x.organization_id in organization_ids] + (
            [user] if include_self else []
        )

    def check_user_has_role(
        self, user: str | model.User, role: Role, exclusive: bool = True
    ) -> bool:
        user: model.User = self._get_obj(model.User, user)
        roles = user.roles
        if exclusive:
            return role in roles and len(roles) == 1
        return role in roles

    def print_organizations(self) -> None:
        organizations = self.read_all("root1_1", model.Organization, cascade=True)
        print("\nOrganizations:")
        for x in sorted(organizations, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

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

    def print_data_collections(self) -> None:
        data_collections = self.read_all("root1_1", model.DataCollection, cascade=True)
        print("\nDataCollections:")
        for x in sorted(data_collections, key=lambda x: x.name):
            print(f"{x.name} ({x.id})")

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

    def print_org_admin_policies(self) -> None:
        org_admin_policies = self.read_all(
            "root1_1", model.OrganizationAdminPolicy, cascade=True
        )
        print("\nOrganizationAdminPolicies:")
        for x in sorted(
            org_admin_policies, key=lambda x: (x.organization.name, x.user.name)
        ):
            print(
                f"{x.organization.name}: user={x.user.name} (is_active={x.is_active}) ({x.id})"
            )

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
                if ServiceTestClient._convert_case_date_to_code(x.case_date)
                in case_codes
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
                f"{ServiceTestClient._convert_case_date_to_code(x.case_date)}: {curr_content}; {curr_data_collections} ({x.id})"
            )

    def print_users(self) -> None:
        user: model.User = self._get_obj(model.User, "root1_1")
        users = self.read_all(user, model.User)
        organizations = {x.id: x for x in self.read_all(user, model.Organization)}
        print("\nUsers:")
        for x in sorted(
            users, key=lambda x: (organizations[x.organization_id].name, x.email)
        ):
            print(
                f"{organizations[x.organization_id].name} / {x.email}: "
                + ", ".join([z for z in sorted(y.name for y in x.roles)])
                + f" ({x.id})"
            )

    def print_user_permissions(self, user: str | model.User) -> None:
        user: model.User = self._get_obj(model.User, user)
        user_permissions = self.app.user_manager.get_user_permissions(user)
        command_permissions = map_paired_elements(
            ((x.command_name, x.permission_type) for x in user_permissions), as_set=True
        )
        print(
            f"\nPermissions for user {user.name} (n_commands={len(command_permissions)}):"
        )
        model.Permission
        for x in sorted(user_permissions, key=lambda x: x.sort_key):
            print(f"{x}")

    def _get_obj(
        self,
        model_class: Type[model.Model],
        obj: (
            str
            | UUID
            | model.Model
            | list[str | UUID | model.Model]
            | tuple[UUID, UUID]
        ),
        copy: bool = False,
        on_missing: str = "raise",
    ) -> BASE_MODEL_TYPE | list[BASE_MODEL_TYPE]:
        if isinstance(obj, list):
            return [self._get_obj(model_class, x) for x in obj]
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        if model_class == model.Case:
            if not isinstance(key, datetime.datetime):
                key = ServiceTestClient._convert_case_code_to_date(key)
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
        else:
            key = self._get_obj_key(table, model_class, obj, on_missing)

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
