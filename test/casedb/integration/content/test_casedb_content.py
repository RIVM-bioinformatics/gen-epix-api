import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import TestType as EnumTestType  # to avoid PyTest warning
from typing import Iterable

import pytest

import gen_epix.commondb.test.util as test_util
from gen_epix.casedb.domain import command, enum, model
from gen_epix.fastapp import CrudOperation, PermissionType
from gen_epix.fastapp.model import Permission
from gen_epix.filter import LogicalOperator, TypedCompositeFilter, TypedStringSetFilter


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=EnumTestType.CASEDB_INTEGRATION_CONTENT.value,
        repository_type=enum.RepositoryType.DICT,
        # repository_type=enum.RepositoryType.SA_SQLITE,
        verbose=False,
        log_level=logging.ERROR,
        use_endpoints=True,
        data_fixture_name="FULL",
    )


class TestContent:
    def test_content(self, env: Env) -> None:

        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()

        app = env.app
        # Get root user
        root_user: model.User = test_util.create_root_user_from_claims(env.cfg, env.app)
        env._set_obj(root_user)
        root_permissions: set[Permission] = app.handle(
            command.RetrieveOwnPermissionsCommand(user=root_user)
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
        org_admin_user: model.User = [
            x for x in users if x.id == org_admin_policies[0].user_id
        ][0]
        org_admin_permissions: set[Permission] = app.handle(
            command.RetrieveOwnPermissionsCommand(user=org_admin_user)
        )
        # Get org user
        user_access_case_policies: list[model.UserAccessCasePolicy] = app.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=org_admin_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        org_user: model.User = [
            x
            for x in users
            if x.id in {y.user_id for y in user_access_case_policies}
            and enum.Role.ORG_USER in x.roles
            and len(x.roles) == 1
        ][0]
        org_user_permissions: set[Permission] = app.handle(
            command.RetrieveOwnPermissionsCommand(user=org_user)
        )
        # Invite an org user as org admin user
        new_user = model.User(
            email="new_user@example.com",
            organization_id=org_admin_user.organization_id,
            roles={enum.Role.ORG_USER},
        )
        new_user_invitation: model.UserInvitation = app.handle(
            command.InviteUserCommand(
                user=org_admin_user,
                email=new_user.email,
                organization_id=new_user.organization_id,
                roles=new_user.roles,
            )
        )
        new_user_in_db: model.User = app.handle(
            command.RegisterInvitedUserCommand(
                user=new_user,
                token=new_user_invitation.token,
            )
        )
        # Get constraints on user invitation
        user_invitation_constraints = app.handle(
            command.RetrieveInviteUserConstraintsCommand(
                user=org_admin_user,
            )
        )
        # Get some refdata as org user
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
        concepts: list[model.Concept] = app.handle(
            command.ConceptCrudCommand(
                user=org_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        concept_ids_by_set = {
            concept_set.id: [
                x.id for x in concepts if x.concept_set_id == concept_set.id
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
            complete_case_type: model.CompleteCaseType = app.handle(  # type: ignore
                command.RetrieveCompleteCaseTypeCommand(
                    user=org_user,
                    case_type_id=case_type.id,
                )
            )
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
                                operator=LogicalOperator.OR,
                            )
                            if filters
                            else None
                        ),
                    ),
                )
            )
            case_ids = case_ids[0:10]
            cases = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=org_user,
                    case_ids=case_ids,
                )
            )
            if len(case_ids) > 100:
                # Too high load for this test
                continue
            # Retrieve phylogenetic tree
            dist_case_type_cols = [
                case_type_col
                for case_type_col in complete_case_type.case_type_cols.values()
                if complete_case_type.cols[case_type_col.col_id].col_type
                == enum.ColType.GENETIC_DISTANCE
            ]
            for dist_case_type_col in dist_case_type_cols:
                for tree_algorithm_code in dist_case_type_col.tree_algorithm_codes:
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
            # Retrieve genetic sequence
            genetic_sequence_case_type_cols = [
                case_type_col
                for case_type_col in complete_case_type.case_type_cols.values()
                if complete_case_type.cols[case_type_col.col_id].col_type
                == enum.ColType.GENETIC_SEQUENCE
            ]
            for genetic_sequence_case_type_col in genetic_sequence_case_type_cols:
                genetic_sequences: list[model.GeneticSequence] = app.handle(
                    command.RetrieveGeneticSequenceByCaseCommand(
                        user=org_user,
                        case_ids=case_ids[0:1],
                        genetic_sequence_case_type_col_id=genetic_sequence_case_type_col.id,
                    )
                )
                if not genetic_sequences:
                    raise ValueError("Genetic sequence should not be empty")
                for seq in genetic_sequences:
                    if not seq.id:
                        raise ValueError("Genetic sequence ID should not be empty")
                    if not hasattr(seq, "nucleotide_sequence"):
                        raise ValueError(
                            "Genetic sequence should have nucleotide_sequence attribute"
                        )
            # Retrieve genetic sequences in FASTA format
            for genetic_sequence_case_type_col in genetic_sequence_case_type_cols:
                fasta_iterator: Iterable[str] = app.handle(
                    command.RetrieveGeneticSequenceFastaByCaseCommand(
                        user=org_user,
                        case_ids=case_ids[0:1],
                        genetic_sequence_case_type_col_id=genetic_sequence_case_type_col.id,  # type: ignore[arg-type]
                    )
                )
                if not fasta_iterator:
                    raise ValueError("generator should not be empty")
                # convert generator to string
                fasta_str = "\n".join(fasta_iterator)
                if not fasta_str.startswith(">"):
                    raise ValueError("FASTA string should start with '>'")
                if "\n" not in fasta_str:
                    raise ValueError("FASTA string should contain new lines")
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

        # profiler.stop()
        # with open(env.test_dir / f"content.performance.html", "w") as f:
        #     f.write("".join(profiler.output_html()))
