import logging
from collections.abc import Hashable
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.case_upload.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.commondb.util import retrieve_db_data_from_file
from typing import Any
from uuid import UUID

import pandas as pd
import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.domain import exc
from gen_epix.commondb.domain import model as commondb_model
from gen_epix.commondb.enum import AppType
from gen_epix.commondb.domain.service.organization import BaseOrganizationService
from gen_epix.commondb.env import App
from gen_epix.commondb.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.seqdb.domain.service.seq import BaseSeqService
from gen_epix.util import map_paired_elements

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


class CaseUploadSetup:
    ORDERED_MODEL_TO_SHEET_MAP: dict[type[model.Model], str] = {
        model.ConceptSet: "ConceptSet",
        model.Concept: "Concept",
        model.ConceptRelation: "ConceptRelation",
        model.RegionSet: "RegionSet",
        model.Region: "Region",
        model.RegionRelation: "RegionRelation",
        model.GeneticDistanceProtocol: "GeneticDistanceProtocol",
        model.Organization: "Organization",
        model.User: "User",
        model.UserInvitation: "UserInvitation",
        model.DataCollection: "DataCollection",
        model.IdentifierIssuer: "IdentifierIssuer",
        model.CaseTypeSetCategory: "CaseTypeSetCategory",
        model.Dim: "Dim",
        model.Col: "Col",
        model.Disease: "Disease",
        model.EtiologicalAgent: "EtiologicalAgent",
        model.CaseType: "CaseType",
        model.CaseTypeSet: "CaseTypeSet",
        model.CaseTypeSetMember: "CaseTypeSetMember",
        model.CaseTypeDim: "CaseTypeDim",
        model.CaseTypeCol: "CaseTypeCol",
        model.CaseTypeColSet: "CaseTypeColSet",
        model.CaseTypeColSetMember: "CaseTypeColSetMember",
        model.OrganizationAdminPolicy: "OrganizationAdminPolicy",
        model.OrganizationAccessCasePolicy: "OrganizationAccessCasePolicy",
        model.UserAccessCasePolicy: "UserAccessCasePolicy",
        model.OrganizationShareCasePolicy: "OrganizationShareCasePolicy",
        model.UserShareCasePolicy: "UserShareCasePolicy",
    }
    EXTRA_TABLE_TO_SHEET_MAP: dict[str, str] = {
        "command.validate_cases": "ValidateCasesCommand",
        "command.upload_cases": "UploadCasesCommand",
        "command._case_data": "_CaseData",
        "command._case_content_data": "_CaseContentData",
        "seqdb.SequencingProtocol": "SequencingProtocol",
        "seqdb.AssemblyProtocol": "AssemblyProtocol",
    }
    FIXTURE_DATA_EXCEL_FILE = Path(__file__).parent / "test_casedb_case_upload.xlsx"
    FIXTURE_DATA_PICKLE_FILE = Path(__file__).parent / "test_casedb_case_upload.pkl"

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        self.excel_file = self.FIXTURE_DATA_EXCEL_FILE
        self.pickle_file = self.FIXTURE_DATA_PICKLE_FILE
        self.case_crud_commands: pd.DataFrame | None = None
        self._setup_casedb_app(env)
        self._setup_seqdb_app(env)

    def _setup_casedb_app(self, env: Env) -> None:
        retrieve_db_data_from_file(
            test_client=env,
            ordered_model_to_sheet_map=self.ORDERED_MODEL_TO_SHEET_MAP,
            excel_file=self.excel_file,
            pickle_file=self.pickle_file,
            extra_table_to_sheet_map=self.EXTRA_TABLE_TO_SHEET_MAP,
        )

    def _setup_seqdb_app(self, env: Env) -> None:
        """Add sequencing and assembly protocols to seqdb, as well as identifier issuers."""
        # Get casedb/seqdb organization and seqdb seq service
        casedb_organization_service: BaseOrganizationService = env.app.impl.services[
            enum.ServiceType.ORGANIZATION
        ]
        seqdb_app: App = env.app.impl.services[enum.ServiceType.SEQDB]._seqdb_app
        seqdb_organization_service: BaseOrganizationService = seqdb_app.impl.services[
            seqdb_enum.ServiceType.ORGANIZATION
        ]
        seqdb_seq_service: BaseSeqService = seqdb_app.impl.services[seqdb_enum.ServiceType.SEQ]  # type: ignore[assignment]
        # Get identifier issuers
        with casedb_organization_service.repository.uow() as uow:
            identifier_issuers: list[model.IdentifierIssuer] = (
                casedb_organization_service.repository.crud(  # type: ignore[assignment]
                    uow,
                    None,
                    model.IdentifierIssuer,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                )
            )
        # Get sequencing and assembly protocols from props
        sequencing_protocol_df: pd.DataFrame = env.props["seqdb.SequencingProtocol"]
        assembly_protocol_df: pd.DataFrame = env.props["seqdb.AssemblyProtocol"]
        sequencing_protocols: list[seqdb_model.SequencingProtocol] = [
            seqdb_model.SequencingProtocol(**x)
            for x in sequencing_protocol_df.to_dict(orient="records")
        ]
        assembly_protocols: list[seqdb_model.AssemblyProtocol] = [
            seqdb_model.AssemblyProtocol(**x)
            for x in assembly_protocol_df.to_dict(orient="records")
        ]
        # Add to seqdb
        with seqdb_organization_service.repository.uow() as uow:
            seqdb_organization_service.repository.crud(
                uow,
                None,
                model.IdentifierIssuer,
                [
                    seqdb_model.IdentifierIssuer(**x.model_dump())
                    for x in identifier_issuers
                ],
                None,
                CrudOperation.CREATE_SOME,
            )
        with seqdb_seq_service.repository.uow() as uow:

            seqdb_seq_service.repository.crud(
                uow,
                None,
                seqdb_model.SequencingProtocol,
                sequencing_protocols,
                None,
                CrudOperation.CREATE_SOME,
            )
            seqdb_seq_service.repository.crud(
                uow,
                None,
                seqdb_model.AssemblyProtocol,
                assembly_protocols,
                None,
                CrudOperation.CREATE_SOME,
            )


@pytest.mark.scenario_ids(
    "TC-RBAC-02-01",
    "TC-RBAC-04-01",
    "TC-BIO-04-01",
    "TC-BIO-04-01",
    "TC-RBAC-02-02",
    "TC-RBAC-02-04",
    "TC-11-09-01",
)
class TestCaseUpload(CaseUploadSetup):
    FILE_CASE_TYPE_COL_VALUE = "(FILE)"

    def _encode_pairing_function(self, x: int, y: int) -> int:
        """Only for y values < 100, otherwise switch to Cantor's pairing function"""
        return x * 100 + y

    def _decode_pairing_function(self, z: int) -> tuple[int, int]:
        return z // 100, z % 100

    def test_case_upload(self, env: Env) -> None:
        """
        Execute all case CRUD and similar commands in case_crud_commands
        """
        # For debugging, set set of indices, otherwise None
        command_idx_to_test = None
        # command_idx_to_test = {6}

        # Get sorted active test cases df
        df: pd.DataFrame | None = env.props["command.upload_cases"]
        if df is None:
            raise ValueError("Case CRUD commands DataFrame is not set.")
        df = df.loc[df["dm.is_active"] == True, :]
        rows = df.sort_values(by="index", axis=0).to_dict(orient="records")

        # Get unique users
        root_user = env.get_root_user()
        uq_user_ids = {x["user.id"] for x in rows if x["user.id"] is not None}
        uq_users_list = env.app.handle(
            command.UserCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_SOME,
                obj_ids=list(uq_user_ids),
            )
        )
        uq_users = {str(x.id): x for x in uq_users_list}

        # Get read set and seq case type columns
        cols: list[model.Col] = env.app.handle(
            command.ColCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        col_map: dict[UUID, model.Col] = {x.id: x for x in cols}
        case_type_cols: list[model.CaseTypeCol] = env.app.handle(  # type: ignore[assignment]
            command.CaseTypeColCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        sample_id_case_type_col_ids: set[UUID] = {x.id for x in case_type_cols if col_map[x.col_id].col_type == enum.ColType.ID_SAMPLE}  # type: ignore[assignment]
        read_set_case_type_col_ids: set[UUID] = {x.id for x in case_type_cols if col_map[x.col_id].col_type == enum.ColType.GENETIC_READS}  # type: ignore[assignment]
        seq_case_type_col_ids: set[UUID] = {x.id for x in case_type_cols if col_map[x.col_id].col_type == enum.ColType.GENETIC_SEQUENCE}  # type: ignore[assignment]

        # Create and execute each command
        for row in rows:
            index = row["index"]
            if command_idx_to_test is not None and index not in command_idx_to_test:
                # For debugging, skip any commands not in the list
                continue
            row_operation = row["operation"].upper()
            user = uq_users[row["user.id"]]
            is_allowed = row["is_allowed"]
            if env.verbose:
                print(
                    f"Command {index} (is_allowed={is_allowed}, row_operation={row_operation}, user={user.name}): executing"
                )
            cmd: command.Command
            # Create command
            if row_operation == "CREATE":
                cmd = command.CaseCrudCommand(
                    id=row["id"],
                    user=user,
                    operation=CrudOperation.CREATE_ONE,
                    objs=self._create_case(row),
                    props={"id_present": "keep"},
                )
            elif row_operation == "READ":
                cmd = command.CaseCrudCommand(
                    id=row["id"],
                    user=user,
                    operation=CrudOperation.READ_ONE,
                    obj_ids=UUID(row["case.id"]),
                )
            elif row_operation == "UPDATE":
                cmd = command.CaseCrudCommand(
                    id=row["id"],
                    user=user,
                    operation=CrudOperation.UPDATE_ONE,
                    objs=self._create_case(row),
                )
            elif row_operation == "DELETE":
                cmd = command.CaseCrudCommand(
                    id=row["id"],
                    user=user,
                    operation=CrudOperation.DELETE_ONE,
                    obj_ids=UUID(row["case.id"]),
                )
            elif row_operation == "CREATE_CASES":
                cmd = command.UploadCasesCommand(
                    id=row["id"],
                    user=user,
                    case_type_id=row["case.case_type_id"],
                    created_in_data_collection_id=row[
                        "case.created_in_data_collection_id"
                    ],
                    case_batch=model.CaseBatchForUpload(
                        cases=[
                            self._create_case(  # type: ignore[list-item]
                                row,
                                for_upload=True,
                                sample_id_case_type_col_ids=sample_id_case_type_col_ids,
                                read_set_case_type_col_ids=read_set_case_type_col_ids,
                                seq_case_type_col_ids=seq_case_type_col_ids,
                            )
                        ]  # type: ignore[arg-type]
                    ),
                    props={"id_present": "keep"},
                )
            elif row_operation == "RETRIEVE_CASES_BY_ID":
                cmd = command.RetrieveCasesByIdCommand(
                    id=row["id"],
                    user=user,
                    case_type_id=row["case.case_type_id"],
                    case_ids=[UUID(row["case.id"])],
                )
            elif row_operation == "CASES_DELETE":
                raise NotImplementedError(
                    f"Operation {row_operation} not yet implemented"
                )
            else:
                raise ValueError(f"Command {index}, unknown operation: {row_operation}")
            # Execute command
            try:
                if is_allowed:
                    env.app.handle(cmd)
                else:
                    with pytest.raises(exc.UnauthorizedAuthError):
                        env.app.handle(cmd)
            except Exception as e:
                if is_allowed:
                    msg = (
                        f"Command {index} (allowed={is_allowed}) raised exception: {e}"
                    )
                else:
                    msg = f"Command {index} (allowed={is_allowed}) did not raise (correct) exception: {e}"
                if env.verbose:
                    print(f"\t{msg}")
                raise AssertionError(msg)

    def test_case_validation(self, env: Env) -> None:
        """
        Execute all case CRUD and similar commands in case_crud_commands
        """
        # Convert case content data to content and new_content dicts
        df: pd.DataFrame = env.props["command._case_content_data"]
        df["value"] = df["value"].apply(lambda x: None if x is None else str(x))
        df["validated_value"] = df["validated_value"].apply(
            lambda x: None if x is None else str(x)
        )
        case_content: dict[UUID, dict[UUID, str | None]] = {}
        validated_case_content: dict[UUID, dict[UUID, str | None]] = {}
        for row in df.to_dict(orient="records"):
            case_id = UUID(row["case_id"])
            case_type_col_id = UUID(row["case_type_col_id"])
            case_content.setdefault(case_id, {})
            case_content[case_id][case_type_col_id] = row["value"]
            validated_case_content.setdefault(case_id, {})
            validated_case_content[case_id][case_type_col_id] = row["validated_value"]

        # Convert case data to cases and new_cases
        df = env.props["command._case_data"]
        all_cases: dict[UUID, model.Case] = {}
        all_cases_for_upload: dict[UUID, model.CaseForUpload] = {}
        all_validated_cases: dict[UUID, model.Case] = {}
        all_validated_cases_for_upload: dict[UUID, model.CaseForUpload] = {}
        for row in df.to_dict(orient="records"):
            case_id = UUID(row["id"])
            case_type_id = UUID(row["case_type_id"])
            created_in_data_collection_id = UUID(row["created_in_data_collection_id"])
            case = model.Case(
                id=case_id,
                case_type_id=case_type_id,
                created_in_data_collection_id=created_in_data_collection_id,
                content=case_content.get(case_id, {}),
            )
            all_cases.setdefault(case_id, case)
            all_cases_for_upload.setdefault(
                case_id, model.CaseForUpload(id=case_id, case=case)
            )
            validated_case = model.Case(
                id=case_id,
                case_type_id=case_type_id,
                created_in_data_collection_id=created_in_data_collection_id,
                content=validated_case_content.get(case_id, {}),
            )
            all_validated_cases.setdefault(case_id, validated_case)
            all_validated_cases_for_upload.setdefault(
                case_id, model.CaseForUpload(id=case_id, case=validated_case)
            )

        # Parse validate case command data
        df = env.props["command.validate_cases"]
        if df is None:
            raise ValueError("Case CRUD commands DataFrame is not set.")
        # sort by index to have correct order and convert to rows
        mask = df["dm.is_active"] == True
        rows: list[dict[Hashable, Any]] = (
            df.loc[mask, :].sort_values(by="index", axis=0).to_dict(orient="records")
        )

        # Get unique users
        root_user = env.get_root_user()
        uq_user_ids = {x["user.id"] for x in rows if x["user.id"] is not None}
        uq_users_list: list[model.User] = env.app.handle(
            command.UserCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_SOME,
                obj_ids=list(uq_user_ids),
            )
        )
        uq_users = {str(x.id): x for x in uq_users_list}
        for user in uq_users.values():
            env._set_obj(user)
        env._set_obj(root_user, update=True)

        # Get policies and case type col ids
        organization_access_case_policies: dict[
            tuple[UUID, UUID], model.OrganizationAccessCasePolicy
        ] = {
            (x.organization_id, x.data_collection_id): x  # type: ignore[attr-defined,misc]
            for x in env.read_all(root_user, model.OrganizationAccessCasePolicy)
        }
        user_access_case_policies: dict[
            tuple[UUID, UUID], model.UserAccessCasePolicy
        ] = {
            (x.user_id, x.data_collection_id): x  # type: ignore[attr-defined,misc]
            for x in env.read_all(root_user, model.UserAccessCasePolicy)
        }
        case_type_col_ids: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
            [
                (x.case_type_col_set_id, x.case_type_col_id)  # type: ignore[attr-defined]
                for x in env.read_all(root_user, model.CaseTypeColSetMember)
            ],
            as_set=True,
        )
        all_case_type_col_ids = set.union(set(), *case_type_col_ids.values())

        # Create and execute each command
        command_idx_to_test = None
        # command_idx_to_test = {5}  # For debugging, set set of indices, otherwise None
        n_cases = 1
        for row in rows:
            index = float(row["index"])
            case_type_id = UUID(row["case_type_id"])
            created_in_data_collection_id = UUID(row["created_in_data_collection_id"])
            is_update = bool(row["is_update"])
            case_ids = [
                UUID(row[f"case_id{i+1}"])
                for i in range(n_cases)
                if row[f"case_id{i+1}"] is not None
            ]
            if command_idx_to_test is not None and index not in command_idx_to_test:
                # For debugging, skip any commands not in the list
                continue
            user = uq_users[row["user.id"]]
            assert user.id is not None

            # Get writable case type col ids
            if user.roles.intersection(env.role_set_map[enum.RoleSet.GE_APP_ADMIN]):
                write_case_type_col_ids = all_case_type_col_ids
            else:
                org_policy: model.OrganizationAccessCasePolicy | None = (
                    organization_access_case_policies.get(
                        (user.organization_id, created_in_data_collection_id)
                    )
                )
                write_case_type_col_ids = set()
                if (
                    org_policy
                    and org_policy.is_active
                    and org_policy.is_private
                    and org_policy.add_case
                    and org_policy.write_case_type_col_set_id is not None
                ):
                    user_policy: model.UserAccessCasePolicy | None = (
                        user_access_case_policies.get(
                            (user.id, created_in_data_collection_id)
                        )
                    )
                    if (
                        user_policy
                        and user_policy.is_active
                        and user_policy.add_case
                        and user_policy.write_case_type_col_set_id
                    ):
                        write_case_type_col_ids = case_type_col_ids[
                            org_policy.write_case_type_col_set_id
                        ].intersection(
                            case_type_col_ids[user_policy.write_case_type_col_set_id]
                        )

            if env.verbose:
                print(f"Command {index}, user={user.name}): executing")

            # Create cases and expected new cases
            case_batch = model.CaseBatchForUpload(
                cases=[all_cases_for_upload[x].model_copy() for x in case_ids]
            )
            expected_validated_cases = [
                all_validated_cases_for_upload[x].model_copy() for x in case_ids
            ]
            for expected_validated_case in expected_validated_cases:
                # Keep only writable case type cols in expected validated case
                expected_validated_case.case.content = {
                    x: y
                    for x, y in expected_validated_case.case.content.items()
                    if x in write_case_type_col_ids
                }

            # Create command
            cmd = command.UploadCasesCommand(
                user=user,
                case_type_id=case_type_id,
                created_in_data_collection_id=created_in_data_collection_id,
                verify_only=True,
                case_batch=case_batch,
            )
            # Execute command
            is_allowed = row["is_allowed"]
            upload_result: model.CaseBatchUploadResult | None = None
            try:
                if is_allowed:
                    upload_result = env.app.handle(cmd)
                else:
                    with pytest.raises(exc.UnauthorizedAuthError):
                        env.app.handle(cmd)
            except Exception as e:
                if is_allowed:
                    msg = (
                        f"Command {index} (allowed={is_allowed}) raised exception: {e}"
                    )
                else:
                    msg = f"Command {index} (allowed={is_allowed}) did not raise (correct) exception: {e}"
                if env.verbose:
                    print(f"\t{msg}")
                raise AssertionError(msg)
            if upload_result is not None:
                # Collect derived/conflict case_type_col_ids from validation report
                # Both DERIVED and CONFLICT are acceptable differences since they represent
                # values that were correctly transformed or overwritten
                acceptable_difference_col_ids: set[UUID] = set()
                for case_result in upload_result.cases:
                    for data_issue in case_result.data_issues:
                        if data_issue.data_issue_type in (
                            enum.DataIssueType.DERIVED,
                            enum.DataIssueType.CONFLICT,
                        ):
                            acceptable_difference_col_ids.add(
                                data_issue.case_type_col_id
                            )
                if env.verbose and acceptable_difference_col_ids:
                    print(
                        f"\t  Found acceptable difference columns: {acceptable_difference_col_ids}"
                    )

                # Compare cases to new cases
                actual_validated_cases = [
                    model.Case(
                        id=x.id,
                        case_type_id=case_type_id,
                        created_in_data_collection_id=created_in_data_collection_id,
                        content=x.validated_content,
                    )
                    for x in upload_result.cases
                ]
                case_differences: set[tuple[UUID, str | None, str | None]] = set()
                acceptable_differences: set[tuple[UUID, str | None, str | None]] = set()
                for actual_case, expected_case in zip(
                    actual_validated_cases, expected_validated_cases
                ):
                    actual_content = actual_case.content
                    expected_content = expected_case.case.content
                    keys = set(actual_content.keys()).union(expected_content.keys())
                    for key in keys:
                        actual_value = actual_content.get(key)
                        expected_value = expected_content.get(key)
                        if actual_value != expected_value:
                            if key in acceptable_difference_col_ids:
                                # This is an acceptable difference (derived or conflict)
                                acceptable_differences.add(
                                    (key, actual_value, expected_value)
                                )
                            else:
                                # This is an unexpected difference
                                case_differences.add(
                                    (key, actual_value, expected_value)
                                )

                if env.verbose and acceptable_differences:
                    acceptable_differences_str = ", ".join(
                        sorted(f"{x}:{y}!={z}" for x, y, z in acceptable_differences)
                    )
                    print(
                        f"\t  Accepting acceptable differences: {acceptable_differences_str}"
                    )

                if case_differences:
                    case_differences_str = ", ".join(
                        sorted(f"{x}:{y}!={z}" for x, y, z in case_differences)
                    )
                    msg = f"Command {index} (allowed={is_allowed}) produced unexpected validated cases: {case_differences_str}"
                    if env.verbose:
                        print(f"\t{msg}")
                        if acceptable_difference_col_ids:
                            print(
                                f"\t  (Note: {len(acceptable_differences)} acceptable differences were ignored)"
                            )
                    raise AssertionError(msg)

    def _create_case(
        self,
        row: dict[str, Any],
        for_upload: bool = False,
        sample_id_case_type_col_ids: set[UUID] | None = None,
        read_set_case_type_col_ids: set[UUID] | None = None,
        seq_case_type_col_ids: set[UUID] | None = None,
    ) -> model.Case | model.CaseForUpload:
        sample_id_case_type_col_ids = sample_id_case_type_col_ids or set()
        read_set_case_type_col_ids = read_set_case_type_col_ids or set()
        seq_case_type_col_ids = seq_case_type_col_ids or set()
        case_content: dict[UUID, str | None] = {}
        found_read_set_case_type_col_ids: list[UUID] = []
        read_sets: list[model.ReadSetForUpload] = []
        found_seq_case_type_col_ids: list[UUID] = []
        seqs: list[model.SeqForUpload] = []
        i = 0
        while True:
            i += 1
            # Get case type col and value
            case_type_col_id_key = f"case.content.case_type_col_id{i}"
            if case_type_col_id_key not in row:
                break
            case_type_col_value_key = f"case.content.case_type_col_value{i}"
            case_type_col_id_str = row[case_type_col_id_key]
            if case_type_col_id_str is None:
                continue
            case_type_col_id = UUID(case_type_col_id_str)
            value = row[case_type_col_value_key]
            # Handle to be created read sets and seqs
            if case_type_col_id in read_set_case_type_col_ids:
                if value == self.FILE_CASE_TYPE_COL_VALUE:
                    found_read_set_case_type_col_ids.append(case_type_col_id)
                    value = None
            elif case_type_col_id in seq_case_type_col_ids:
                if value == self.FILE_CASE_TYPE_COL_VALUE:
                    seqs.append(
                        model.SeqForUpload(
                            case_type_col_id=case_type_col_id,
                        )
                    )
                    value = None
            # Set case content
            if value is not None:
                case_content[case_type_col_id] = value
        # Add read sets and seqs if applicable
        external_identifier: commondb_model.ExternalIdentifierForUpload | None = None
        if found_read_set_case_type_col_ids or found_seq_case_type_col_ids:
            # Get external identifier if applicable
            identifier_issuer_id = UUID(row["seqdb.identifier_issuer_id"])
            sample_id_case_type_col_id = UUID(row["seqdb.sample_id_case_type_col_id"])
            sample_id = case_content.get(sample_id_case_type_col_id)
            external_identifier = (
                commondb_model.ExternalIdentifierForUpload(
                    identifier_issuer_id=identifier_issuer_id, external_id=sample_id
                )
                if sample_id is not None
                else None
            )
            value = row["seqdb.sequencing_protocol_id"]
            sequencing_protocol_id = None if value is None else UUID(value)
            value = row["seqdb.assembly_protocol_id"]
            assembly_protocol_id = None if value is None else UUID(value)
            for case_type_col_id in found_read_set_case_type_col_ids:
                read_sets.append(
                    model.ReadSetForUpload(
                        case_type_col_id=case_type_col_id,
                        external_sample_id=external_identifier,
                        sequencing_protocol_id=sequencing_protocol_id,
                    )
                )
            for case_type_col_id in found_seq_case_type_col_ids:
                seqs.append(
                    model.SeqForUpload(
                        case_type_col_id=case_type_col_id,
                        external_sample_id=external_identifier,
                        assembly_protocol_id=assembly_protocol_id,
                    )
                )
        # Create case or case for upload
        case = model.Case(
            id=row["case.id"],
            case_type_id=row["case.case_type_id"],
            created_in_data_collection_id=row["case.created_in_data_collection_id"],
            code=row["case.code"],
            content=case_content,
        )
        if for_upload:
            return model.CaseForUpload(
                id=case.id,
                external_identifiers=(
                    None if external_identifier is None else [external_identifier]
                ),
                case=case,
                read_sets=read_sets,
                seqs=seqs,
            )
        return case
