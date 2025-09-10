import logging
from pathlib import Path
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.case_access.base import (
    REPOSITORY_TYPE,
    SKIP_ENDPOINTS,
    VERBOSE,
)
from test.common.util import retrieve_db_data_from_file
from test.test_client.enum import TestType as EnumTestType
from typing import Any, Hashable, Type
from uuid import UUID

import pandas as pd
import pytest

from gen_epix.casedb.domain import command, model
from gen_epix.common.domain import exc
from gen_epix.fastapp.enum import CrudOperation


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=EnumTestType.CASEDB_INTEGRATION_CASE_VALIDATION.value,
        repository_type=REPOSITORY_TYPE,
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
        data_fixture_name="EMPTY",
    )


class CaseValidationSetup:
    ORDERED_MODEL_TO_SHEET_MAP: dict[Type[model.Model], str] = {
        model.Concept: "Concept",
        model.ConceptSet: "ConceptSet",
        model.ConceptSetMember: "ConceptSetMember",
        model.RegionSet: "RegionSet",
        model.Region: "Region",
        model.RegionRelation: "RegionRelation",
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
        self.excel_file = Path(__file__).parent / "test_case_validation.xlsx"
        self.pickle_file = Path(__file__).parent / "test_case_validation.pkl"
        self.case_crud_commands: pd.DataFrame | None = None
        self.retrieve_data_from_file(env)

    def retrieve_data_from_file(self, env: Env) -> None:
        retrieve_db_data_from_file(
            test_client=env,
            ordered_model_to_sheet_map=self.ORDERED_MODEL_TO_SHEET_MAP,
            excel_file=self.excel_file,
            pickle_file=self.pickle_file,
            extra_table_to_sheet_map={
                "validate_cases_command": "ValidateCasesCommand",
                "_case_data": "_CaseData",
                "_case_content_data": "_CaseContentData",
            },
        )


class TestCaseValidation(CaseValidationSetup):

    def _encode_pairing_function(self, x: int, y: int) -> int:
        """Only for y values < 100, otherwise switch to Cantor's pairing function"""
        return x * 100 + y

    def _decode_pairing_function(self, z: int) -> tuple[int, int]:
        return z // 100, z % 100

    def test_case_validation(self, env: Env) -> None:
        """
        Execute all case CRUD and similar commands in case_crud_commands
        """
        # Convert case content data to content and new_content dicts
        df: pd.DataFrame = env.props["_case_content_data"]
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
        df = env.props["_case_data"]
        all_cases: dict[UUID, model.CaseForCreateUpdate] = {}
        all_validated_cases: dict[UUID, model.CaseForCreateUpdate] = {}
        for row in df.to_dict(orient="records"):
            case_id = UUID(row["id"])
            all_cases.setdefault(
                case_id, model.CaseForCreateUpdate(**row, content=case_content.get(case_id, {}))  # type: ignore[misc]
            )
            all_validated_cases.setdefault(
                case_id, model.CaseForCreateUpdate(**row, content=validated_case_content.get(case_id, {}))  # type: ignore[misc]
            )

        # Parse validate case command data
        df = env.props["validate_cases_command"]
        if df is None:
            raise ValueError("Case CRUD commands DataFrame is not set.")
        # sort by index to have correct order and convert to rows
        mask = df["dm.is_active"] == True
        rows: list[dict[Hashable, Any]] = (
            df.loc[mask, :].sort_values(by="index", axis=0).to_dict(orient="records")
        )

        # Get unique users
        uq_user_ids = {x["user.id"] for x in rows if x["user.id"] is not None}
        uq_users_list: list[model.User] = env.app.handle(
            command.UserCrudCommand(
                user=env.get_root_user(),
                operation=CrudOperation.READ_SOME,
                obj_ids=list(uq_user_ids),
            )
        )
        uq_users = {str(x.id): x for x in uq_users_list}

        # Create and execute each command
        command_idx_to_test = None
        # command_idx_to_test = {6}  # For debugging, set set of indices, otherwise None
        n_cases = 1
        for row in rows:
            index = row["index"]
            case_ids = [
                UUID(row[f"case_id{i+1}"])
                for i in range(n_cases)
                if row[f"case_id{i+1}"] is not None
            ]
            if command_idx_to_test is not None and index not in command_idx_to_test:
                # For debugging, skip any commands not in the list
                continue
            user = uq_users[row["user.id"]]
            if env.verbose:
                print(f"Command {index}, user={user.name}): executing")
            # Create cases and expected new cases
            cases = [all_cases[x].model_copy() for x in case_ids]
            expected_validated_cases = [
                all_validated_cases[x].model_copy() for x in case_ids
            ]
            # Create command
            cmd: command.Command
            cmd = command.ValidateCasesCommand(
                user=user,
                case_type_id=row["case_type_id"],
                created_in_data_collection_id=row["created_in_data_collection_id"],
                is_update=row["is_update"],
                cases=cases,
                data_collection_ids=set(),
            )
            # Execute command
            is_allowed = row["is_allowed"]
            validation_report: model.CaseValidationReport | None = None
            try:
                if is_allowed:
                    validation_report = env.app.handle(cmd)
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
            if validation_report is not None:
                # Compare cases to new cases
                actual_validated_cases = [
                    x.case for x in validation_report.validated_cases
                ]
                case_differences = set()
                for actual_case, expected_case in zip(
                    actual_validated_cases, expected_validated_cases
                ):
                    actual_content = actual_case.content
                    expected_content = expected_case.content
                    keys = set(actual_content.keys()).union(expected_content.keys())
                    for key in keys:
                        actual_value = actual_content.get(key)
                        expected_value = expected_content.get(key)
                        if actual_value != expected_value:
                            case_differences.add((key, actual_value, expected_value))
                if case_differences:
                    case_differences_str = ", ".join(
                        sorted(f"{x}:{y}!={z}" for x, y, z in case_differences)
                    )
                    msg = f"Command {index} (allowed={is_allowed}) produced unexpected validated cases: {case_differences_str}"
                    if env.verbose:
                        print(f"\t{msg}")
                    raise AssertionError(msg)
