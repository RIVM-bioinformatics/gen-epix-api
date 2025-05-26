import logging
import test.test_client.util as test_util
from test.casedb.casedb_service_test_client import CasedbServiceTestClient as Env
from test.test_client.enum import TestType as EnumTestType  # to avoid PyTest warning

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import CrudOperation, PermissionType
from gen_epix.filter import BooleanOperator, TypedCompositeFilter, TypedStringSetFilter


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(
        test_type=EnumTestType.CASEDB_INTEGRATION_CONTENT,
        repository_type=enum.RepositoryType.DICT,
        # repository_type=enum.RepositoryType.SA_SQLITE,
        load_target="full",
        verbose=False,
        log_level=logging.ERROR,
    )
    # return Env.get_env(test_type=EnumTestType.INTEGRATION_CONTENT, repository_type=enum.RepositoryType.SA_SQLITE, verbose=False, log_level=logging.ERROR)


class TestContent:
    def test_content(self, env: Env) -> None:
        app = env.app
        # Get root user
        root_user = test_util.create_root_user_from_claims(env.cfg, env.app)
        complete_root_user: model.CompleteUser = app.handle(
            command.RetrieveCompleteUserCommand(
                user=root_user,
            )
        )
        # Get all users and permissions
        users = app.handle(
            command.UserCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        permissions = app.domain.permissions
        # Get organization level policies
        org_access_case_policies = app.handle(
            command.OrganizationAccessCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        org_share_case_policies = app.handle(
            command.OrganizationShareCasePolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        # Get org admin user
        org_admin_policies = app.handle(
            command.OrganizationAdminPolicyCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        org_admin_user = [x for x in users if x.id == org_admin_policies[0].user_id][0]
        complete_org_admin_user: model.CompleteUser = app.handle(
            command.RetrieveCompleteUserCommand(
                user=org_admin_user,
            )
        )
        # Get org user
        user_access_case_policies = app.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=org_admin_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        org_user = [
            x
            for x in users
            if x.id in {y.user_id for y in user_access_case_policies}
            and enum.Role.ORG_USER in x.roles
            and len(x.roles) == 1
        ][0]
        complete_org_user: model.CompleteUser = app.handle(
            command.RetrieveCompleteUserCommand(
                user=org_user,
            )
        )
        # Get some metadata as org user
        case_types = app.handle(
            command.CaseTypeCrudCommand(
                user=org_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        case_sets = app.handle(
            command.CaseSetCrudCommand(
                user=org_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        concept_sets = app.handle(
            command.ConceptSetCrudCommand(
                user=org_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        concept_set_members = app.handle(
            command.ConceptSetMemberCrudCommand(
                user=org_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        concept_ids_by_set = {
            concept_set.id: [
                concept_set_member.concept_id
                for concept_set_member in concept_set_members
                if concept_set_member.concept_set_id == concept_set.id
            ]
            for concept_set in concept_sets
        }
        case_type_stats = app.handle(
            command.RetrieveCaseTypeStatsCommand(user=org_user)
        )
        # Get case and case set stats
        case_set_stats = app.handle(command.RetrieveCaseSetStatsCommand(user=org_user))
        # Go over all case types with data
        has_cases_case_type_ids = {
            x.case_type_id for x in case_type_stats if x.n_cases > 0
        }
        for case_type in case_types:
            if case_type.id not in has_cases_case_type_ids:
                continue
            # print(f"START: {datetime.datetime.now()}")
            complete_case_type: model.CompleteCaseType = app.handle(  # type: ignore
                command.RetrieveCompleteCaseTypeCommand(
                    user=org_user,
                    case_type_id=case_type.id,
                )
            )
            # print(f"END: {datetime.datetime.now()}")
            if len(complete_case_type.case_type_cols) <= 1:
                continue
            # Retrieve cases based on a filter
            # print(f"Retrieving cases for case type {complete_case_type.name}")
            filters = []
            for case_type_col in complete_case_type.case_type_cols.values():
                col = complete_case_type.cols[case_type_col.col_id]
                if col.concept_set_id:
                    # Create a filter for a portion of the terms in the concept set
                    filters.append(
                        TypedStringSetFilter(
                            type="STRING_SET",
                            key=str(case_type_col.id),
                            members={  # type: ignore[arg-type]
                                str(x)
                                for i, x in enumerate(
                                    concept_ids_by_set[col.concept_set_id]
                                )
                                if i // 4 == 0  # Keep only a portion of the terms
                            },
                        )
                    )
            case_ids = app.handle(
                command.RetrieveCasesByQueryCommand(
                    user=org_user,
                    case_query=model.CaseQuery(
                        case_type_ids={complete_case_type.id},
                        filter=(
                            TypedCompositeFilter(
                                type="COMPOSITE",
                                filters=filters,
                                operator=BooleanOperator.OR,
                            )
                            if filters
                            else None
                        ),
                    ),
                )
            )
            cases = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=org_user,
                    case_ids=case_ids,
                )
            )
            # Retrieve phylogenetic tree
            dist_case_type_cols = [
                case_type_col
                for case_type_col in complete_case_type.case_type_cols.values()
                if complete_case_type.cols[case_type_col.col_id].col_type
                == enum.ColType.GENETIC_DISTANCE
            ]
            for dist_case_type_col in dist_case_type_cols:
                for tree_algorithm_code in dist_case_type_col.tree_algorithm_codes:
                    if len(case_ids) > 100:
                        # Too high load for this test
                        continue
                    phylogenetic_tree = app.handle(
                        command.RetrievePhylogeneticTreeByCasesCommand(
                            user=org_user,
                            genetic_distance_case_type_col_id=dist_case_type_col.id,
                            tree_algorithm=tree_algorithm_code,
                            case_ids=case_ids,
                        )
                    )
                    if phylogenetic_tree.sequence_ids:
                        raise ValueError("Sequence IDs should not be returned")
                    if not set(phylogenetic_tree.leaf_ids).issubset(set(case_ids)):
                        raise ValueError("Leaf IDs should be a subset of the case IDs")
        for case_set in case_sets:
            case_ids = app.handle(
                command.RetrieveCasesByQueryCommand(
                    user=org_user,
                    case_query=model.CaseQuery(
                        case_set_ids={case_set.id},
                    ),
                )
            )
            cases = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=org_user,
                    case_ids=case_ids,
                )
            )

        for model_class, command_class in app._model_crud_command_map.items():
            permissions: frozenset[model.Permission] = (
                app.domain.get_permissions_for_command(command_class)
            )
            if PermissionType.READ not in {x.permission_type for x in permissions}:
                continue
            app.handle(
                command_class(
                    user=org_user,
                    operation=CrudOperation.READ_ALL,
                )
            )
