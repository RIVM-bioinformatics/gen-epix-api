import logging
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.case_access.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    VERBOSE,
)
from test.commondb.util import retrieve_db_data_from_file
from test.test_client.enum import TestType as EnumTestType
from typing import Any, Type
from uuid import UUID

import pandas as pd
import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.config.cfg import AppCfg
from gen_epix.commondb.domain import exc
from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
from gen_epix.commondb.util import set_env_variables
from gen_epix.fastapp.enum import CrudOperation

APP_CFGS: dict[str, AppCfg] = {}
for dev_repository_config in DevRepositoryConfig:
    name = (
        f"{EnumTestType.CASEDB_INTEGRATION_CASE_ACCESS}_{dev_repository_config.value}"
    )
    set_env_variables(AppType.CASEDB, DevIdpConfig.MOCK, dev_repository_config)
    APP_CFGS[name] = AppCfg(
        AppType.CASEDB,
        enum.ServiceType,
        enum.RepositoryType,
        name=name,
        log_setup=False,
    )


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=EnumTestType.CASEDB_INTEGRATION_CASE_ACCESS.value,
        app_cfg=APP_CFGS[
            f"{EnumTestType.CASEDB_INTEGRATION_CASE_ACCESS}_{DEV_REPOSITORY_CONFIG.value}"
        ],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=EnumTestType.CASEDB_INTEGRATION_CASE_ACCESS.value,
        repository_type=REPOSITORY_TYPE,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
        data_fixture_name="EMPTY",
    )


class CaseAccessSetup:
    ORDERED_MODEL_TO_SHEET_MAP: dict[Type[model.Model], str] = {
        model.Organization: "Organization",
        model.User: "User",
        model.UserInvitation: "UserInvitation",
        model.DataCollection: "DataCollection",
        model.CaseTypeSetCategory: "CaseTypeSetCategory",
        model.Dim: "Dim",
        model.Col: "Col",
        model.Disease: "Disease",
        model.EtiologicalAgent: "EtiologicalAgent",
        model.CaseType: "CaseType",
        model.CaseTypeSet: "CaseTypeSet",
        model.CaseTypeSetMember: "CaseTypeSetMember",
        model.CaseTypeCol: "CaseTypeCol",
        model.CaseTypeColSet: "CaseTypeColSet",
        model.CaseTypeColSetMember: "CaseTypeColSetMember",
        model.OrganizationAdminPolicy: "OrganizationAdminPolicy",
        model.OrganizationAccessCasePolicy: "OrganizationAccessCasePolicy",
        model.UserAccessCasePolicy: "UserAccessCasePolicy",
        model.OrganizationShareCasePolicy: "OrganizationShareCasePolicy",
        model.UserShareCasePolicy: "UserShareCasePolicy",
    }

    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        self.excel_file = Path(__file__).parent / "test_casedb_case_access.xlsx"
        self.pickle_file = Path(__file__).parent / "test_casedb_case_access.pkl"
        self.case_crud_commands: pd.DataFrame | None = None
        self.retrieve_data_from_file(env)

    def retrieve_data_from_file(self, env: Env) -> None:
        retrieve_db_data_from_file(
            test_client=env,
            ordered_model_to_sheet_map=self.ORDERED_MODEL_TO_SHEET_MAP,
            excel_file=self.excel_file,
            pickle_file=self.pickle_file,
            extra_table_to_sheet_map={"case_crud_command": "CaseCrudCommand"},
        )


class TestCaseAccess(CaseAccessSetup):

    def _encode_pairing_function(self, x: int, y: int) -> int:
        """Only for y values < 100, otherwise switch to Cantor's pairing function"""
        return x * 100 + y

    def _decode_pairing_function(self, z: int) -> tuple[int, int]:
        return z // 100, z % 100

    def test_case_access(self, env: Env) -> None:
        """
        Execute all case CRUD and similar commands in case_crud_commands
        """
        df = env.props["case_crud_command"]
        if df is None:
            raise ValueError("Case CRUD commands DataFrame is not set.")
        df = df.loc[df["dm.is_active"] == True, :]
        command_idx_to_test = None
        # command_idx_to_test = {6}  # For debugging, set set of indices, otherwise None
        n_case_type_cols = 3
        # Sort by index to have correct order
        df = df.sort_values(by="index", axis=0).to_dict(orient="records")
        # Get unique users
        uq_user_ids = {x["user.id"] for x in df if x["user.id"] is not None}
        uq_users_list = env.app.handle(
            command.UserCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.READ_SOME,
                obj_ids=list(uq_user_ids),
            )
        )
        uq_users = {str(x.id): x for x in uq_users_list}

        # Function to create a case
        def _create_case(
            row: dict[str, Any], for_create_upload: bool = False
        ) -> model.Case | model.CaseForCreateUpdate:
            case_content = {}
            for i in range(1, n_case_type_cols):
                case_type_col_id = row[f"case.content.case_type_col_id{i}"]
                if case_type_col_id is None:
                    continue
                value = row[f"case.content.case_type_col_value{i}"]
                case_content[case_type_col_id] = value
            if for_create_upload:
                return model.CaseForCreateUpdate(
                    id=row["case.id"],
                    subject_id=row["case.subject_id"],
                    case_date=row["case.case_date"],
                    content=case_content,
                )
            return model.Case(
                id=row["case.id"],
                case_type_id=row["case.case_type_id"],
                subject_id=row["case.subject_id"],
                created_in_data_collection_id=row["case.created_in_data_collection_id"],
                case_date=row["case.case_date"],
                content=case_content,
            )

        # Create and execute each command
        for row in df:
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
                    objs=_create_case(row),
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
                    objs=_create_case(row),
                )
            elif row_operation == "DELETE":
                cmd = command.CaseCrudCommand(
                    id=row["id"],
                    user=user,
                    operation=CrudOperation.DELETE_ONE,
                    obj_ids=UUID(row["case.id"]),
                )
            elif row_operation == "CREATE_CASES":
                cmd = command.CreateCasesCommand(
                    id=row["id"],
                    user=user,
                    case_type_id=row["case.case_type_id"],
                    created_in_data_collection_id=row[
                        "case.created_in_data_collection_id"
                    ],
                    is_update=False,
                    cases=[_create_case(row, for_create_upload=True)],  # type: ignore[list-item]
                    data_collection_ids=set(),
                    props={"id_present": "keep"},
                )
            elif row_operation == "RETRIEVE_CASES_BY_ID":
                cmd = command.RetrieveCasesByIdCommand(
                    id=row["id"],
                    user=user,
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
