import logging
import pickle
from pathlib import Path
from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.casedb.integration.case_access.base import (
    REPOSITORY_TYPE,
    SKIP_ENDPOINTS,
    VERBOSE,
)
from test.test_client.enum import TestType as EnumTestType
from typing import Any, Type
from uuid import UUID

import numpy as np
import pandas as pd
import pytest

from gen_epix.casedb.domain import command, model
from gen_epix.common.domain import exc
from gen_epix.fastapp.enum import CrudOperation


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(
        test_type=EnumTestType.CASEDB_INTEGRATION_CASE_ACCESS,
        repository_type=REPOSITORY_TYPE,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=SKIP_ENDPOINTS,
        load_target="EMPTY",
    )
    # return Env.get_env(test_type=EnumTestType.CASEDB_INTEGRATION_CASE_ACCESS, repository_type=enum.RepositoryType.SA_SQLITE, verbose=False, log_level=logging.ERROR)


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
        self.excel_file = Path(__file__).parent / "test_case_access.xlsx"
        self.pickle_file = Path(__file__).parent / "test_case_access.pkl"
        self.case_crud_commands: pd.DataFrame | None = None
        self.retrieve_data_from_file(env)

    def retrieve_data_from_file(self, env: Env) -> None:
        is_loaded_from_pkl = False
        db: dict[Type[model.Model] | str, dict[UUID, model.Model] | pd.DataFrame] = {}
        # Load from pickle if possible
        if (
            self.pickle_file.exists()
            and self.pickle_file.stat().st_mtime > self.excel_file.stat().st_mtime
        ):
            with open(self.pickle_file, "rb") as f:
                db = pickle.load(f)
            is_loaded_from_pkl = True

        # Load from excel if necessary
        if not is_loaded_from_pkl:
            for model_class, sheet_name in self.ORDERED_MODEL_TO_SHEET_MAP.items():
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                df.replace({np.nan: None}, inplace=True)
                df = df.map(lambda x: {} if x == "{}" else x)
                objs = [model_class(**x) for x in df.to_dict(orient="records")]  # type: ignore[misc]
                db[model_class] = {x.id: x for x in objs}  # type: ignore[misc]
            df = pd.read_excel(self.excel_file, sheet_name="CaseCrudCommand")
            df.replace({np.nan: None}, inplace=True)
            db["case_crud_command"] = df
            with self.pickle_file.open("wb") as file_handle:
                pickle.dump(db, file_handle)

        # Populate the environment with the loaded data
        root_user = env.get_root_user()
        for model_class, df in db.items():
            if model_class not in self.ORDERED_MODEL_TO_SHEET_MAP:
                continue
            objs = list(df.values())
            if model_class == model.Organization:
                # Update the root organization
                cmd = env.app.domain.get_crud_command_for_model(model_class)(
                    user=root_user,
                    operation=CrudOperation.UPDATE_ONE,
                    objs=[x for x in objs if x.id == root_user.organization_id][0],
                )
                env.app.handle(cmd)
                # Remove root organization from objs to create
                objs = [x for x in objs if x.id != root_user.organization_id]
            if model_class == model.User:
                # Update the root user
                cmd = env.app.domain.get_crud_command_for_model(model_class)(
                    user=root_user,
                    operation=CrudOperation.UPDATE_ONE,
                    objs=[x for x in objs if x.id == root_user.id][0],
                )
                env.app.handle(cmd)
                # Remove root user from objs to create
                objs = [x for x in objs if x.id != root_user.id]
            # Create the objects
            cmd = env.app.domain.get_crud_command_for_model(model_class)(
                user=root_user,
                operation=CrudOperation.CREATE_SOME,
                objs=objs,
                props={"id_present": "keep"},
            )
            env.app.handle(cmd)
        env.props["case_crud_commands"] = db["case_crud_command"]


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
        df = env.props["case_crud_commands"]
        if df is None:
            raise ValueError("Case CRUD commands DataFrame is not set.")
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
        def _create_case(row: dict[str, Any]) -> model.Case:
            case_content = {}
            for i in range(1, n_case_type_cols):
                case_type_col_id = row[f"case.content.case_type_col_id{i}"]
                if case_type_col_id is None:
                    continue
                value = row[f"case.content.case_type_col_value{i}"]
                case_content[case_type_col_id] = value
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
            elif row_operation == "CASES_CREATE":
                cmd = command.CasesCreateCommand(
                    id=row["id"],
                    user=user,
                    cases=[_create_case(row)],
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
