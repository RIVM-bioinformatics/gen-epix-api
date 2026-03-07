import logging
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.case_access.base import (
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
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

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


class CaseAccessSetup:
    ORDERED_MODEL_TO_SHEET_MAP: dict[type[model.Model], str] = {
        model.Organization: "Organization",
        model.User: "User",
        model.UserInvitation: "UserInvitation",
        model.DataCollection: "DataCollection",
        model.CaseTypeSetCategory: "CaseTypeSetCategory",
        model.RefDim: "RefDim",
        model.RefCol: "RefCol",
        model.Disease: "Disease",
        model.EtiologicalAgent: "EtiologicalAgent",
        model.CaseType: "CaseType",
        model.CaseTypeSet: "CaseTypeSet",
        model.CaseTypeSetMember: "CaseTypeSetMember",
        model.Dim: "Dim",
        model.Col: "Col",
        model.ColSet: "ColSet",
        model.ColSetMember: "ColSetMember",
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


@pytest.mark.scenario_ids(
    "TC-RBAC-04-07",
    "TC-RBAC-04-01",
    "TC-BIO-04-01",
    "TC-BIO-04-01",
    "TC-RBAC-02-02",
    "TC-RBAC-02-04",
    "TC-RBAC-05-01",
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
        # command_idx_to_test = None
        command_idx_to_test = {6}  # For debugging, set set of indices, otherwise None
        n_cols = 3
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
            row: dict[str, Any], for_upload: bool = False, is_create: bool = True
        ) -> model.Case | model.CaseForUpload:
            case_content = {}
            for i in range(1, n_cols):
                col_id = row[f"case.content.col_id{i}"]
                if col_id is None:
                    continue
                value = row[f"case.content.col_value{i}"]
                case_content[col_id] = value
            if for_upload:
                return model.CaseForUpload(
                    id=row["case.id"],
                    case=model.Case(
                        case_type_id=row["case.case_type_id"],
                        created_in_data_collection_id=row[
                            "case.created_in_data_collection_id"
                        ],
                        content=case_content,
                    ),
                )
            return model.Case(
                id=row["case.id"],
                case_type_id=row["case.case_type_id"],
                created_in_data_collection_id=row["case.created_in_data_collection_id"],
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
                cmd = command.UploadCasesCommand(
                    id=row["id"],
                    user=user,
                    case_type_id=row["case.case_type_id"],
                    created_in_data_collection_id=row[
                        "case.created_in_data_collection_id"
                    ],
                    case_batch=model.CaseBatchForUpload(
                        cases=[
                            _create_case(  # type: ignore[list-item]
                                row, for_upload=True
                            )
                        ]
                    ),
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
