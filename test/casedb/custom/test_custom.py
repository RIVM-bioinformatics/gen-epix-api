import logging
import test.test_client.util as test_util
from test.test_client.enum import TestType as EnumTestType  # to avoid PyTest warning
from test.test_client.service_test_client import ServiceTestClient as Env
from uuid import UUID

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import (
    BooleanOperator,
    FilterType,
    TypedCompositeFilter,
    TypedStringSetFilter,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    test_util.set_log_level("casedb", logging.ERROR)
    # test_util.set_log_level("casedb", logging.WARN)
    # test_util.set_log_level("casedb", logging.INFO)

    return Env(
        test_type=EnumTestType.CASEDB_CUSTOM,
        repository_type=enum.RepositoryType.DICT,
        verbose=False,
        load_target="full",
    )
    # return Env(test_type=EnumTestType.CUSTOM, repository_type=enum.RepositoryType.SA_SQLITE, verbose=False, load_target="full")


class TestManual:
    USER_MAP = {
        1: "0191fb18-7eeb-b384-2d0f-c98e33960af2",
        2: "0191fb18-7eeb-4c49-db6d-4e0cfe52599a",
        3: "0191fb18-7eeb-49cb-2c20-3b47ad4eef4f",
        4: "0191fb18-7eeb-cb68-91c1-45aa6cb321e9",
        5: "0191fb18-7eeb-3cea-a84a-b1f3e6d9573b",
        6: "0191fb18-7eeb-70b6-4772-83c2290dd526",
        7: "0191fb18-7eeb-1afd-6a6c-d2158ee112c7",
        8: "0191fb18-7eeb-d203-3931-92122879a6e4",
        9: "0191fb18-7eeb-70fd-a4a1-bbb94b2141cc",
        10: "0191fb18-7eeb-2c0a-39f4-99c6c973c348",
    }
    USER_MAP = {x: UUID(y) for x, y in USER_MAP.items()}
    ROOT_USER_ID = USER_MAP[1]

    @classmethod
    def get_user(cls, env: Env, user_id: UUID) -> model.User:
        assert env.services[enum.ServiceType.AUTH].repository
        with env.services[enum.ServiceType.AUTH].repository.uow() as uow:
            return env.services[enum.ServiceType.AUTH].repository.crud(
                uow,
                TestManual.ROOT_USER_ID,
                model.User,
                objs=None,
                obj_ids=user_id,
                operation=CrudOperation.READ_ONE,
            )

    # TODO: add to test_build_db
    @pytest.mark.skip(reason="manual test")
    def test_retrieve_cases_by_query(self, env: Env) -> None:
        user = TestManual.get_user(env, TestManual.USER_MAP[4])
        case_ids = env.app.handle(
            command.RetrieveCasesByQueryCommand(
                user=user,
                case_query=model.CaseQuery(
                    case_type_ids=["018b8a3f-dd6e-b080-f0fb-ff724c3cb00a"],
                    filter=TypedCompositeFilter(
                        type=FilterType.COMPOSITE.value,
                        filters=[
                            TypedStringSetFilter(
                                type=FilterType.STRING_SET.value,
                                key=UUID("018d074d-ea0c-44bf-c104-1f8a70c02ff4"),
                                members=["018eff72-39aa-ff2a-110c-fff954f3dc56"],
                            )
                        ],
                        operator=BooleanOperator.AND,
                    ),
                ),
            )
        )
        print(f"Number of cases: {len(case_ids)}")
        cases = env.app.handle(
            command.RetrieveCasesByIdCommand(user=user, case_ids=case_ids)
        )
        pass

    @pytest.mark.skip(reason="manual test")
    def test_retrieve_genetic_sequence(self, env: Env) -> None:
        user = TestManual.get_user(env, TestManual.USER_MAP[5])
        genetic_sequence = env.app.handle(
            command.RetrieveGeneticSequenceByCaseCommand(
                user=user,
                genetic_sequence_case_type_col_id=UUID(
                    "0191c0e1-041b-360a-269d-8c5e6ebc4e42"
                ),
                case_ids=[UUID("018c3e98-5a42-b60b-9480-f3a2a04f4661")],
            )
        )
        pass

    @pytest.mark.skip(reason="manual test")
    def test_retrieve_phylogenetic_tree(self, env: Env) -> None:
        user = TestManual.get_user(env, TestManual.USER_MAP[5])
        phylogenetic_tree = env.app.handle(
            command.RetrievePhylogeneticTreeByCasesCommand(
                user=user,
                genetic_distance_case_type_col_id=UUID(
                    "0191c0e1-041b-f639-4e7f-59cd1fbf0b11"
                ),
                case_ids=[
                    UUID(x)
                    for x in [
                        "0191707a-1d95-1cbb-60be-ce527e498548",
                        "0191707a-1d95-25a2-e24f-34d798199fa7",
                        "0191707a-1d95-3da7-8305-7175a9f56470",
                        "0191707a-1d95-543c-712f-a4db06ba98fc",
                        "0191707a-1d95-6c28-c534-7b0673b63e59",
                        "0191707a-1d95-78b2-729e-a5e8ab9edd23",
                        "0191707a-1d95-7902-33ab-975937c423e3",
                        "0191707a-1d95-8d1a-60f9-0056ca512f0c",
                        "0191707a-1d95-98c1-979d-8a7c07de28a7",
                        "0191707a-1d95-acd3-3f99-b2e82680a302",
                        "0191707a-1d95-b0f2-737c-37069eb75757",
                        "0191707a-1d95-b718-6b4f-fe8ab1dc877a",
                        "0191707a-1d95-d2dc-9646-64e4407075be",
                        "0191707a-1d95-e080-7a82-fe30dfbc3c49",
                        "0191707a-1d95-e5bc-4e80-3f3a8b5cdbde",
                        "0191707a-1d95-e7cf-ff1a-cca40163f58f",
                    ]
                ],
                tree_algorithm=enum.TreeAlgorithmType.SLINK,
            )
        )
        pass

    # TODO: move to test_build_db
    @pytest.mark.skip(reason="manual test")
    def test_read_organization_admin_policy(self, env: Env) -> None:
        user = TestManual.get_user(env, TestManual.USER_MAP[6])
        organization_admin_policies = env.app.handle(
            command.OrganizationAdminPolicyCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        print(
            f"\nOrganization admin policies for user {user.id} (n={len(organization_admin_policies)}):\n"
            + "\n".join([str(x.id) for x in organization_admin_policies])
        )
        pass

    # TODO: move to test_build_db
    @pytest.mark.skip(reason="manual test")
    def test_read_organization_access_case_policy(self, env: Env) -> None:
        user = TestManual.get_user(env, TestManual.USER_MAP[4])
        organization_access_case_policies = env.app.handle(
            command.OrganizationAccessCasePolicyCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        print(
            f"\nOrganization access case policies for user {user.id} (n={len(organization_access_case_policies)}):\n"
            + "\n".join([str(x.id) for x in organization_access_case_policies])
        )
        pass

    # TODO: move to test_build_db
    @pytest.mark.skip(reason="manual test")
    def test_read_user_case_policy(self, env: Env) -> None:
        user = TestManual.get_user(env, TestManual.USER_MAP[6])
        user_access_case_policies = env.app.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=user,
                operation=CrudOperation.READ_ALL,
            )
        )
        print(
            f"\nUser access case policies for user {user.id} (n={len(user_access_case_policies)}):\n"
            + "\n".join([str(x.id) for x in user_access_case_policies])
        )
        pass
