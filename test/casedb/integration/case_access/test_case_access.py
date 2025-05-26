import logging
import pickle
import test.test_client.util as test_util
from itertools import combinations, product
from pathlib import Path
from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.casedb.integration.case_access.base import (
    REPOSITORY_TYPE,
    SKIP_ENDPOINTS,
    VERBOSE,
)
from test.test_client.enum import TestType as EnumTestType
from typing import cast
from uuid import UUID

import numpy as np
import pandas as pd
import pytest

from gen_epix.casedb.domain import enum, exc, model


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
    @pytest.fixture(scope="module", autouse=True)
    def setup(self, env: Env) -> None:
        self.excel_file = Path(__file__).parent / "test_case_access.xlsx"
        self.pickle_file = Path(__file__).parent / "test_case_access.pkl"
        self.retrieve_data_from_file(env)

        # if you use save_db, you manually need to modify the excel in 6 ways:
        # 1. add =VLOOKUP(C2,Organization!$A:$B,2,0) to all organization-like columns
        # 2. add a dm. in front of all columns where you add a lookup
        # 3. change all enums to strings  (ColType.TEXT -> "TEXT")
        # 4. in User, add =LEFT(B2,FIND("@",B2)-1) to the name column
        # 5. replace ' to " in the roles columns of User and UserInvitation
        # self.save_db(env)

    def retrieve_data_from_file(self, env: Env) -> None:
        model_to_sheet_map = {
            model.OrganizationAccessCasePolicy: "OrganizationAccessCasePolicy",
            model.UserAccessCasePolicy: "UserAccessCasePolicy",
            model.OrganizationShareCasePolicy: "OrganizationShareCasePolicy",
            model.UserShareCasePolicy: "UserShareCasePolicy",
            model.OrganizationAdminPolicy: "OrganizationAdminPolicy",
            model.CaseTypeSetMember: "CaseTypeSetMember",
            model.CaseTypeSetCategory: "CaseTypeSetCategory",
            model.CaseTypeColSet: "CaseTypeColSet",
            model.CaseTypeCol: "CaseTypeCol",
            model.Col: "Col",
            model.CaseTypeColSetMember: "CaseTypeColSetMember",
            model.Dim: "Dim",
            model.CaseType: "CaseType",
            model.CaseTypeSet: "CaseTypeSet",
            model.DataCollectionRelation: "DataCollectionRelation",
            model.DataCollection: "DataCollection",
            model.Organization: "Organization",
            model.User: "User",
            model.UserInvitation: "UserInvitation",
        }
        is_loaded_from_file = False
        content = {}
        if (
            self.pickle_file.exists()
            and self.pickle_file.stat().st_mtime > self.excel_file.stat().st_mtime
        ):
            with open(self.pickle_file, "rb") as f:
                content = pickle.load(f)
            is_loaded_from_file = True

        if not is_loaded_from_file:
            for model_class, sheet_name in model_to_sheet_map.items():
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                df = df.replace({np.nan: None})

                def replace_str_dict(x: str) -> dict:
                    if x == "{}":
                        return {}
                    return x

                df = df.applymap(replace_str_dict)

                objs = [model_class(**x) for x in df.to_dict(orient="records")]
                service_type = env.app.domain.get_service_type_for_model(model_class)
                if service_type not in content:
                    content[service_type] = {}
                content[service_type][model_class] = {x.id: x for x in objs}
            with self.pickle_file.open("wb") as file_handle:
                pickle.dump(content, file_handle)

        for service_type, data in content.items():
            repository = env.repositories[service_type]
            for model_class, objs in data.items():
                repository._db[model_class].update(objs)
                for obj in objs.values():
                    env._set_obj(obj)

    def _fill_db(self, env: Env) -> None:
        n_orgs = 5  # organizations
        n_users = 4  # users per organization
        n_dcs = 11  # data_collections
        n_cts = 5  # case types
        n_dims = 3
        # Create users
        # Create a first root user and organization
        user = test_util.create_root_user_from_claims(env.cfg, env.app)
        env._set_obj(user)
        env._set_obj(
            env.read_one_by_property("root1_1", model.Organization, "name", "org1")
        )
        # Create app_admins
        env.invite_and_register_user("root1_1", "app_admin1_1")
        # Create remaining organizations
        for i in range(2, n_orgs + 1):
            env.create_organization("app_admin1_1", f"org{i}")
        # Create metadata_admin
        env.invite_and_register_user("app_admin1_1", "metadata_admin1_1")
        # Create org_admins and policies
        for i in range(1, n_orgs + 1):
            env.invite_and_register_user("app_admin1_1", f"org_admin{i}_1")
            env.create_org_admin_policy("app_admin1_1", f"org_admin{i}_1", f"org{i}")
        # Create org_users
        for i, j in product(range(1, n_orgs + 1), range(1, n_users + 1)):
            env.invite_and_register_user("app_admin1_1", f"org_user{i}_{j}")

        # Create reference data
        # Create data_collections
        for i in range(1, n_dcs + 1):
            env.create_data_collection("app_admin1_1", f"data_collection{i}")
        # Create diseases
        for i in range(1, n_cts + 1):
            env.create_disease("metadata_admin1_1", f"disease{i}")
        # Create etiological_agents
        for i in range(1, n_cts + 1):
            env.create_etiological_agent("metadata_admin1_1", f"etiological_agent{i}")
        # Create etiologies
        for i in range(1, n_cts + 1):
            env.create_etiology(
                "metadata_admin1_1",
                f"disease{i}",
                f"etiological_agent{i}",
            )
        # Create case_types
        for i in range(1, n_cts + 1):
            env.create_case_type(
                "metadata_admin1_1",
                f"case_type{i}",
                f"disease{i}",
                f"etiological_agent{i}",
            )
        # Create dims
        for i in range(1, n_dims + 1):
            env.create_dim("metadata_admin1_1", f"dim{i}", enum.DimType.TEXT)
        # Create cols
        for i, j in product(range(1, n_dims + 1), range(1, 4)):
            env.create_col("metadata_admin1_1", f"dim{i}_{j}_text", enum.ColType.TEXT)
        # Create case_type_cols
        for i, j, k in product(range(1, n_cts + 1), range(1, n_dims + 1), range(1, 4)):
            env.create_case_type_col(
                "metadata_admin1_1", f"case_type{i}_dim{j}_{k}_text"
            )
        # Create case_type_set_categories
        env.create_case_type_set_category("app_admin1_1", "case_type_set_category1")
        # Create case_type_sets
        # Notation: case_type_set{",".join(case_type_ids)}
        for i in range(1, n_cts + 1):
            TestCaseAccess._create_case_type_set(env, f"{i}")
        for i, j in combinations(range(1, n_cts + 1), 2):
            TestCaseAccess._create_case_type_set(env, f"{i},{j}")
        # Create case_type_col_sets
        # Notation: {case_type_ids}_{dim_ids}_{col_ids}
        for i, j, k in product(range(1, n_cts + 1), range(1, n_dims + 1), range(1, 4)):
            TestCaseAccess._create_case_type_col_set(env, f"{i}_{j}_{k}")

        # Create policies
        # Create data_collection_relations
        for i in range(1, 6):
            # first 5 data_collections are related to themselves
            env.create_data_collection_relation(
                "app_admin1_1", f"data_collection{i}", f"data_collection{i}"
            )
            # next 5 data_collections are related to the first 5
            env.create_data_collection_relation(
                "app_admin1_1", f"data_collection{i}", f"data_collection{i+5}"
            )
        # the last data_collection can only be shared from dc6
        env.create_data_collection_relation(
            "app_admin1_1", f"data_collection6", f"data_collection11"
        )

        # Create organization_data_collection_policies
        # Naming scheme:
        # org_data_collection_policy{organization_id}_{data_collection_id}
        for i in range(1, 6):
            # first 5 orgs have full rights to their own data_collection
            env.create_organization_share_case_policy(
                "app_admin1_1", f"org_data_collection_policy{i}_{i}"
            )

        env.create_organization_share_case_policy(
            "app_admin1_1",
            "org_data_collection_policy1_6",
            add_case=True,
            remove_case=True,
        )
        env.create_organization_share_case_policy(
            "app_admin1_1",
            "org_data_collection_policy1_8",
            add_case=True,
            remove_case=True,
        )
        env.create_organization_share_case_policy(
            "app_admin1_1",
            "org_data_collection_policy2_7",
            add_case=True,
            remove_case=False,
        )
        env.create_organization_share_case_policy(
            "app_admin1_1",
            "org_data_collection_policy3_8",
            add_case=False,
            remove_case=True,
        )
        env.create_organization_share_case_policy(
            "app_admin1_1",
            "org_data_collection_policy4_9",
            add_case=False,
            remove_case=False,
        )
        for i in range(6, 12):
            env.create_organization_share_case_policy(
                "app_admin1_1",
                f"org_data_collection_policy5_{i}",
                add_case=True,
                remove_case=True,
            )
        env.create_organization_share_case_policy(
            "app_admin1_1",
            "org_data_collection_policy5_1",
            add_case=True,
            remove_case=True,
        )

        # Create organization_case_policies
        # TODO add org 1 dc 8
        # org{i} has full access to (data_collection{i}, case_type{j}_dim{1}_{1}_text)
        for i, j in product(range(1, n_orgs + 1), range(1, n_cts + 1)):
            env.create_organization_access_case_policy(
                "app_admin1_1",
                f"org_case_policy{i}_{i}_{j}_{j}_1_1",
                read=True,
                write=True,
            )
        # org{i} has read/update access to (data_collection{n_orgs+i}, case_type{j}_dim{2}_{1}_text)
        for i, j in product(range(1, n_orgs + 1), range(1, n_cts + 1)):
            env.create_organization_access_case_policy(
                "app_admin1_1",
                f"org_case_policy{i}_{n_orgs+i}_{j}_{j}_1_1",
                read=True,
                write=True,
            )
        # Create user_data_collection_policies
        # Naming scheme:
        # user_data_collection_policy{organization_id}_{data_collection_id}_
        for i in range(1, n_orgs + 1):
            for j in range(1, n_users + 1):
                env.create_user_share_case_policy(
                    f"org_admin{i}_1",
                    f"org_user{i}_{j}",
                    f"data_collection{i}",
                )
            ###
            env.create_user_share_case_policy(
                f"org_admin{i}_1",
                f"org_user{i}_1",
                f"data_collection{i + 5}",
                add_case=True,
                remove_case=True,
            )
            env.create_user_share_case_policy(
                f"org_admin{i}_1",
                f"org_user{i}_2",
                f"data_collection{i + 5}",
                add_case=True,
                remove_case=False,
            )
            env.create_user_share_case_policy(
                f"org_admin{i}_1",
                f"org_user{i}_3",
                f"data_collection{i + 5}",
                add_case=False,
                remove_case=True,
            )
            env.create_user_share_case_policy(
                f"org_admin{i}_1",
                f"org_user{i}_4",
                f"data_collection{i + 5}",
                add_case=False,
                remove_case=False,
            )
        env.create_user_share_case_policy(
            f"org_admin5_1",
            f"org_user5_1",
            f"data_collection11",
            add_case=True,
            remove_case=True,
        )

        # Create user_case_policies
        # org_user{i}_{1} has full access to (data_collection{i}, case_type{j}_dim{1}_{1}_text, case_type{j})
        for i, j in product(range(1, n_orgs + 1), range(1, n_cts + 1)):
            env.create_user_access_case_policy(
                f"org_admin{i}_1",
                f"org_user{i}_1",
                f"data_collection{i}",
                f"case_type_set{j}",
                f"case_type_col_set{j}_1_1",
                add_case=True,
                remove_case=True,
            )
        # org_user{i}_{1} has read/update access to (data_collection{n_orgs+i}, case_type{j}_dim{1}_{1}_text, case_type{j})
        for i, j in product(range(1, n_orgs + 1), range(1, n_cts + 1)):
            env.create_user_access_case_policy(
                f"org_admin{i}_1",
                f"org_user{i}_1",
                f"data_collection{n_orgs+i}",
                f"case_type_set{j}",
                f"case_type_col_set{j}_1_1",
                add_case=True,
                remove_case=True,
            )

    def save_db(self, env: Env) -> None:
        self._fill_db(env)
        dfs = {}
        for service_type in [
            enum.ServiceType.ABAC,
            enum.ServiceType.CASE,
            enum.ServiceType.ORGANIZATION,
        ]:
            repository = env.repositories[service_type]
            db = repository._db
            for model_class in env.app.domain.get_models_for_service_type(service_type):
                if not model_class.ENTITY.persistable:
                    continue
                if not db[model_class]:
                    continue
                df = pd.DataFrame.from_records(
                    x.model_dump() for x in db[model_class].values()
                )
                dfs[model_class.__name__] = df
        with pd.ExcelWriter(self.excel_file) as writer:
            for model_name, df in dfs.items():
                df.to_excel(writer, sheet_name=model_name, index=False)


class TestCaseAccess(CaseAccessSetup):

    def _encode_pairing_function(self, x: int, y: int) -> int:
        """Only for y values < 100, otherwise switch to Cantor's pairing function"""
        return x * 100 + y

    def _decode_pairing_function(self, z: int) -> tuple[int, int]:
        return z // 100, z % 100

    def test_case_access(self, env: Env) -> None:
        """
        This test is created to test the case access policies.
        The following rules should aplied using de policies.
        There are 11 data collections, 5 organizations and 4 users per organization.
        Each organization has its own data collection (DC 1-5)

        DataCollections:
        1. DCs 1-5 in which new cases can be created (DCRelation.from_data_collection=to_data_collection)
        2. DCs 6-10 to which cases can only be shared from 1-5 (one each)
        3. DC 11 to which cases can only be shared indirectly from 1-5 through 6-10

        OrganisationDataCollectionPolicies:
        1. Org 1-5: add/remove cases to/from respectively DC 1-5
        2. Org 1: add_case=True, remove_case=True for DC 6
        3. Org 1: add_case=True, remove_case=True for DC 8
        3. Org 2: add_case=True, remove_case=False for DC 7
        4. Org 3: add_case=False, remove_case=True for DC 8
        5. Org 4: add_case=False, remove_case=False for DC 9
        6. Org 5: add_case=True, remove_case=True for DC 11 (not DC 10)

        UserDataCollectionPolicies:
        1. User(1-5)_1: add_case=True, remove_case=True for DC 6
        2. User(1-5)_2: add_case=True, remove_case=False for DC 7
        3. User(1-5)_3: add_case=False, remove_case=True for DC 8
        4. User(1-5)_4: add_case=False, remove_case=False for DC 9

        """

        # DC, org, user
        # all organisations have read/write access to their own data collection
        # all users from each organization have read/write access to their own data collection
        succes_situations = [
            (1, 1, 1),
            (1, 1, 2),
            (1, 1, 3),
            (1, 1, 4),
            (2, 2, 1),
            (2, 2, 2),
            (2, 2, 3),
            (2, 2, 4),
            (3, 3, 1),
            (3, 3, 2),
            (3, 3, 3),
            (3, 3, 4),
            (4, 4, 1),
            (4, 4, 2),
            (4, 4, 3),
            (4, 4, 4),
            (5, 5, 1),
            (5, 5, 2),
            (5, 5, 3),
            (5, 5, 4),
        ]
        self._test_create_cases(env, succes_situations)

        # The first 5 data_collections are related to themselves, so they dont need to be shared
        succes_situations = [
            (6, 1, 1),
            (6, 1, 2),
            (7, 2, 1),
            (7, 2, 2),
            (10, 5, 1),  # TODO: Shouldn't this fail?
            (10, 5, 2),  # TODO: same
        ]
        self._test_create_case_dc_link(env, succes_situations)

        ## Remove cases dc6+
        # The case names are still the case names from the original data_collection,
        # so the encoded dc is the original, not the shared one.
        # only 6 CaseDataCollectionLinks are created:
        # 1,2. dc1 -> dc6 (once for user 1 and once for user 2)
        # 3,4. dc2 -> dc7 (once for user 1 and once for user 2)
        # 5,6. dc3 -> dc8 (once for user 1 and once for user 2)
        # user 2 has only create rights, no remove. So we use user3 for removal
        # org 2 has no remove rights for dc7 so they cant be removed (no 3,4)
        # org 3 has remove rights for dc8, but they have been created by org 1. Should still be removable.
        succes_situations = [
            (6, 1, 1),
            (6, 1, 3),
        ]
        for dc, user in product(range(6, 11), range(1, 5)):
            org = dc - 5
            case_id_1 = cast(  # created by user 1
                model.Case,
                env._get_obj(
                    model.Case,
                    f"case{org}_{self._encode_pairing_function(1, dc - 5)}",
                ),
            ).id
            case_id_2 = cast(  # created by user 2
                model.Case,
                env._get_obj(
                    model.Case,
                    f"case{org}_{self._encode_pairing_function(2, dc - 5)}",
                ),
            ).id
            assert case_id_1 and case_id_2
            case_ids = (case_id_1, case_id_2)

            data_collection_id = cast(
                model.DataCollection,
                env._get_obj(model.DataCollection, f"data_collection{dc}"),
            ).id
            assert data_collection_id

            # the first one should always exist
            if dc == 6 and org == 1 and user == 1:
                existing_key = (data_collection_id, case_ids[0])

            # actual deleting should be done last
            if (dc, org, user) in succes_situations:
                continue

            # I added a retry because dc 6 and org 2 have no relation,
            # so it does not throw an unauth error because there is no id to find.
            # it should still test that the user has no rights to remove a case
            # so I add a key on retry that should always exist.
            print(dc, org, user)
            with pytest.raises((exc.UnauthorizedAuthError, ValueError)):
                env.delete_object(
                    f"org_user{org}_{user}",
                    model.CaseDataCollectionLink,
                    (data_collection_id, case_ids[0]),
                    existing_key,
                )
            with pytest.raises((exc.UnauthorizedAuthError, ValueError)):
                env.delete_object(
                    f"org_user{org}_{user}",
                    model.CaseDataCollectionLink,
                    (data_collection_id, case_ids[1]),
                    existing_key,
                )

        existing_cases = env.read_all("root1_1", model.Case)
        existing_case_names = sorted(
            [env._convert_case_date_to_code(x.case_date) for x in existing_cases]
        )
        for dc, org, user in product(range(1, 6), range(1, 6), range(1, 5)):
            case_name = f"case{org}_{self._encode_pairing_function(user, dc)}"
            if not case_name in existing_case_names:
                # Cannot remember which cases have already been deleted. Change later.
                continue

            if dc == org:
                # TODO: fix LinkConstraintViolationError
                # env.delete_one_case(
                #     f"org_user{org}_{user}",
                #     f"case{org}_{self._encode_pairing_function(user, dc)}",
                # )
                continue

    def _test_create_case_dc_link(
        self, env: Env, succes_situations: list[tuple[int, int, int]]
    ) -> None:
        for dc, org, user in product(range(6, 12), range(1, 6), range(1, 5)):
            if (dc, org, user) in succes_situations:
                continue
            # A lot of cases dont exist, then we need the ValueError
            with pytest.raises((exc.UnauthorizedAuthError, ValueError)):
                env.create_case_data_collection_link(
                    f"org_user{org}_{user}",
                    f"case{org}_{self._encode_pairing_function(user, dc - 5)}",
                    f"data_collection{dc}",
                )
        for dc, org, user in succes_situations:
            env.create_case_data_collection_link(
                f"org_user{org}_{user}",
                f"case{org}_{self._encode_pairing_function(user, dc - 5)}",
                f"data_collection{dc}",
            )

    def _test_create_cases(
        self, env: Env, succes_situations: list[tuple[int, int, int]]
    ) -> None:
        for dc, org, user in product(range(1, 12), range(1, 6), range(1, 5)):
            # Fail first
            if (dc, org, user) in succes_situations:
                continue
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_case(
                    f"org_user{org}_{user}",
                    f"case{org}_{self._encode_pairing_function(user, dc)}",
                    [f"data_collection{dc}"],
                    col_index_pattern=r"dim(\d+)_(\d+)_text",
                )

        for dc, org, user in succes_situations:
            env.create_case(
                f"org_user{org}_{user}",
                f"case{org}_{self._encode_pairing_function(user, dc)}",
                [f"data_collection{dc}"],
                col_index_pattern=r"dim(\d+)_(\d+)_text",
            )

    def _delete_case_collection_links_for_4_users(
        self, env: Env, org: int, case_ids: list[UUID], data_collection_id: UUID
    ) -> None:

        users_with_rights = [1, 3]
        users_without_rights = [2, 4]

        # without rights first because otherwise the case is deleted
        for i, user in enumerate(users_without_rights):
            with pytest.raises(exc.UnauthorizedAuthError):
                env.delete_object(
                    f"org_user{org}_{user}",
                    model.CaseDataCollectionLink,
                    (data_collection_id, case_ids[i]),
                )

        for i, user in enumerate(users_with_rights):
            env.delete_object(
                f"org_user{org}_{user}",
                model.CaseDataCollectionLink,
                (data_collection_id, case_ids[i]),
            )

        # TODO: fix LinkConstraintViolationError
        # else:
        #     with pytest.raises(exc.UnauthorizedAuthError):
        #         env.delete_one_case(
        #             f"org_user{org}_{user}",
        #             f"case{org}_{self._encode_pairing_function(user, dc)}",
        #         )

        # Create cases
        # for i, j in product(range(1, n_cts), range(1, 4)):
        #     env.create_case(
        #         f"org_user{i}_1",
        #         f"case{i}_{j}",
        #         [f"data_collection{i}"],
        #         col_index_pattern=r"dim(\d+)_(\d+)_text",
        #     )

    @staticmethod
    def _create_case_type_col_set(env: Env, name: str) -> None:
        ranges = [[int(y) for y in x.split(",")] for x in name.split("_")]
        case_type_cols = set()
        for i, j, k in product(*ranges):
            case_type_cols.add(f"case_type{i}_dim{j}_{k}_text")
        env.create_case_type_col_set(
            "metadata_admin1_1", f"case_type_col_set{name}", case_type_cols
        )

    @staticmethod
    def _create_case_type_set(env: Env, name: str) -> None:
        case_types = {f"case_type{x}" for x in name.split(",")}
        env.create_case_type_set(
            "metadata_admin1_1",
            f"case_type_set{name}",
            case_types,
            "case_type_set_category1",
        )
