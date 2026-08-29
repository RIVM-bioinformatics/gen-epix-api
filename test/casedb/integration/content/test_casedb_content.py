import logging
from datetime import datetime
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import (
    EnumTestType as EnumTestType,  # to avoid PyTest warning
)
from typing import Iterable
from uuid import UUID

import pytest

from gen_epix import fastapp
from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.commondb.test.util import set_log_level
from gen_epix.fastapp import CrudOperation, PermissionType
from gen_epix.fastapp.model import Permission
from gen_epix.filter import LogicalOperator, TypedCompositeFilter, TypedStringSetFilter
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model

TEST_TYPE = EnumTestType.CASEDB_INTEGRATION_CASE_ACCESS

SKIP_ENDPOINTS = False
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_DEMO
# DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQLITE_DEMO

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
    log_any=VERBOSE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
    log_any=VERBOSE,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    # explicitly set log level for seqdb
    set_log_level("seqdb", logging.ERROR)

    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


@pytest.mark.scenario_ids(
    "TC-RBAC-04-07",
    "TC-RBAC-04-20",
    "TC-RBAC-04-10",
    "TC-RBAC-04-12",
    "TC-RBAC-04-06",
    "TC-RBAC-04-06",
    "TC-RBAC-04-08",
    "TC-RBAC-04-09",
)
class TestContent:
    def test_content(self, env: Env) -> None:

        # import pyinstrument

        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()

        app = env.app
        app_impl: AppImplDetails = app.impl

        # Get root user
        root_user = env.get_root_user()
        env.set_obj(root_user)
        root_permissions: set[Permission] = app.handle(
            command.RetrieveOwnPermissionsCommand(user=root_user)
        )

        # Get all users and permissions
        users: list[model.User] = app.handle(
            command.UserCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        permissions = app.domain.permissions

        # Get org admin, org admin policies and corresponding org users
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

        # # --------------------------------------------------------------------------------------

        # # Code for performance profiling of a code chunk
        # import pyinstrument

        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()

        # t0 = datetime.datetime.now()

        # t1 = datetime.datetime.now()
        # print(f"\n\n\n\nRetrieveCaseSetStatsCommand took {t1 - t0}\n\n\n\n")
        # profiler.stop()
        # dir = Path("./test/output/performance")
        # if not dir.exists():
        #     dir.mkdir()
        # with open(
        #     dir
        #     / f"performance.{datetime.datetime.now().isoformat().replace(':', '.')}.case_set_stats.{DEV_REPOSITORY_CONFIG.value}.html",
        #     "w",
        # ) as f:
        #     f.write("".join(profiler.output_html()))
        # return

        # # --------------------------------------------------------------------------------------

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

        # Get org user
        user_access_case_policies: list[model.UserAccessCasePolicy] = app.handle(
            command.UserAccessCasePolicyCrudCommand(
                user=org_admin_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        org_users: list[model.User] = [
            x
            for x in users
            if x.id in {y.user_id for y in user_access_case_policies}
            and app_impl.role_map[CommonRole.ORG_USER] in x.roles
            and len(x.roles) == 1
        ]
        org_user = org_users[0]
        org_user_permissions: set[Permission] = app.handle(
            command.RetrieveOwnPermissionsCommand(user=org_user)
        )

        # Invite an org user as org admin user
        new_user = model.User(
            key="new_user@example.com",
            email="new_user@example.com",
            organization_id=org_admin_user.organization_id,
            roles={app_impl.role_map[CommonRole.ORG_USER]},
        )
        new_user_invitation: model.UserInvitation = app.handle(
            command.InviteUserCommand(
                user=org_admin_user,
                key=new_user.key,
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
        case_types: list[model.CaseType] = app.handle(
            command.CaseTypeCrudCommand(
                user=org_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        case_sets: list[model.CaseSet] = app.handle(
            command.CaseSetCrudCommand(
                user=org_user,
                operation=CrudOperation.READ_ALL,
            )
        )
        concept_sets: list[model.ConceptSet] = app.handle(
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

        # Get CaseType and and case set stats
        case_stats = app.handle(command.RetrieveCaseTypeStatsCommand(user=org_user))
        case_set_stats = app.handle(command.RetrieveCaseSetStatsCommand(user=org_user))

        # Go over all CaseTypes with data
        found_some_similar_cases = False
        has_cases_case_type_ids = {x.case_type_id for x in case_stats if x.n_cases > 0}
        for case_type in case_types:
            if VERBOSE:
                print(f"Checking CaseType {case_type.name}")
            assert case_type.id is not None
            if case_type.id not in has_cases_case_type_ids:
                continue
            complete_case_type: model.CompleteCaseType = app.handle(
                command.RetrieveCompleteCaseTypeCommand(
                    user=org_user,
                    case_type_id=case_type.id,
                )
            )
            assert complete_case_type.id is not None
            if len(complete_case_type.cols) <= 1:
                continue

            # Retrieve cases based on a filter
            # print(f"Retrieving cases for CaseType {complete_case_type.name}")
            filters: list = []
            for col in complete_case_type.cols.values():
                ref_col = complete_case_type.ref_cols[col.ref_col_id]
                if ref_col.concept_set_id:
                    # Create a filter for a portion of the terms in the concept set
                    filters.append(
                        TypedStringSetFilter(
                            type="STRING_SET",
                            key=str(col.id),
                            members={  # type: ignore[arg-type]
                                str(x)
                                for i, x in enumerate(
                                    concept_ids_by_set[ref_col.concept_set_id]
                                )
                                if i // 4 == 0  # Keep only a portion of the terms
                            },
                        )
                    )
            case_query_result: model.CaseQueryResult = app.handle(
                command.RetrieveCasesByQueryCommand(
                    user=org_user,
                    case_query=model.CaseQuery(
                        case_type_id=complete_case_type.id,
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
            case_ids = case_query_result.case_ids
            case_ids = case_ids[0:10]
            cases = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=org_user,
                    case_type_id=complete_case_type.id,
                    case_ids=case_ids,
                )
            )
            if len(case_ids) > 100:
                # Too high load for this test
                continue

            # Retrieve phylogenetic tree
            found_similar_cases = False
            dist_cols = [
                x
                for x in complete_case_type.cols.values()
                if complete_case_type.ref_cols[x.ref_col_id].col_type
                == enum.ColType.GENETIC_DISTANCE
            ]
            similar_cases_retval = command.RetrieveSimilarCasesReturnValue(cases=[])
            for dist_col in dist_cols:
                assert dist_col is not None
                assert dist_col.id is not None
                for tree_algorithm_code in dist_col.tree_algorithm_codes or []:
                    if VERBOSE:
                        print(
                            f"\tRetrieving phylogenetic tree for {dist_col.code} using tree algorithm {tree_algorithm_code}"
                        )
                    phylogenetic_tree: model.PhylogeneticTree = app.handle(
                        command.RetrievePhylogeneticTreeByCasesCommand(
                            user=org_user,
                            case_type_id=complete_case_type.id,
                            genetic_distance_col_id=dist_col.id,
                            tree_algorithm=tree_algorithm_code,
                            case_ids=case_ids,
                        )
                    )
                    assert phylogenetic_tree.leaf_ids is not None
                    if not set(phylogenetic_tree.leaf_ids).issubset(set(case_ids)):
                        raise ValueError("Leaf IDs should be a subset of the case IDs")

                    # retrieve similar cases
                    similar_cases_retval = app.handle(
                        command.RetrieveSimilarCasesCommand(
                            user=org_user,
                            case_type_id=complete_case_type.id,
                            genetic_distance_col_id=dist_col.id,
                            case_ids=case_ids[0:5],
                            max_distance=20,
                        )
                    )
                    if len(similar_cases_retval.cases) > 0:
                        found_similar_cases = True

            if found_similar_cases:
                found_some_similar_cases = True
                assert len(dist_cols) >= 1
                # assert that any item in similar_case_ids is a UUID
                for case_id_and_date in similar_cases_retval.cases:
                    assert isinstance(case_id_and_date.id, UUID)
                    assert isinstance(case_id_and_date.case_date, datetime)

            # Retrieve genetic sequence
            genetic_sequence_cols = [
                x
                for x in complete_case_type.cols.values()
                if complete_case_type.ref_cols[x.ref_col_id].col_type
                == enum.ColType.GENETIC_SEQUENCE
            ]
            for genetic_sequence_col in genetic_sequence_cols:
                has_seq_case_ids = [
                    x.id for x in cases if x.content.get(genetic_sequence_col.id)
                ]
                if not has_seq_case_ids:
                    continue

                # Retrieve genetic sequences in FASTA format
                if VERBOSE:
                    print(f"\tRetrieving genetic sequences")
                fasta_iterator: Iterable[str] = app.handle(
                    command.RetrieveGeneticSequenceFastaByCaseCommand(
                        user=org_user,
                        case_type_id=complete_case_type.id,
                        case_ids=has_seq_case_ids[0:1],
                        genetic_sequence_col_id=genetic_sequence_col.id,  # type: ignore[arg-type]
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
                # Retrieve SequencingProtocols
                sequencing_protocols: list[seqdb_model.Protocol] = app.handle(
                    command.RetrieveProtocolsCommand(
                        user=org_user,
                        protocol_type=seqdb_enum.ProtocolType.SEQUENCING,
                    )
                )
                if not sequencing_protocols:
                    raise ValueError("Library prep protocols should not be None")
                for sequencing_protocol in sequencing_protocols:
                    if not sequencing_protocol.id:
                        raise ValueError("Library prep protocol ID should not be empty")
                # Retrieve AssemblyProtocols
                assembly_protocols: list[seqdb_model.Protocol] = app.handle(
                    command.RetrieveProtocolsCommand(
                        user=org_user,
                        protocol_type=seqdb_enum.ProtocolType.ASSEMBLY,
                    )
                )
                if not assembly_protocols:
                    raise ValueError("Assembly protocols should not be None")
                for assembly_protocol in assembly_protocols:
                    if not assembly_protocol.id:
                        raise ValueError("Assembly protocol ID should not be empty")

        if not found_some_similar_cases:
            raise ValueError(
                "Did not find similar cases for any CaseType, cannot validate RetrieveSimilarCasesCommand"
            )

        # Go over all case sets
        for case_set in case_sets:
            case_query_result = app.handle(
                command.RetrieveCasesByQueryCommand(
                    user=org_user,
                    case_query=model.CaseQuery(
                        case_type_id=case_set.case_type_id,
                    ),
                )
            )
            case_ids = case_query_result.case_ids
            cases = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=org_user,
                    case_ids=case_ids,
                    case_type_id=case_set.case_type_id,
                )
            )

        # Read all for all models with read permission
        for model_class, command_class in app._model_crud_command_map.items():
            permissions: frozenset[fastapp.Permission] = (  # type: ignore[assignment]
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
        # with open(env.test_dir / f"content.performance.html", "w") as f:
        #     f.write("".join(profiler.output_html()))

    def test_retrieve_is_own_cases(self, env: Env) -> None:
        """
        Happy-path test for RetrieveIsOwnCasesCommand.

        Finds an org user whose organization has at least one private data
        collection, locates cases that were created in that collection, and
        verifies the command returns True for every one of those cases.
        """
        app = env.app
        app_impl: AppImplDetails = app.impl

        root_user = env.get_root_user()
        users: list[model.User] = app.handle(
            command.UserCrudCommand(user=root_user, operation=CrudOperation.READ_ALL)
        )
        org_access_case_policies: list[model.OrganizationAccessCasePolicy] = app.handle(
            command.OrganizationAccessCasePolicyCrudCommand(
                user=root_user, operation=CrudOperation.READ_ALL
            )
        )
        orgs_with_private_dc: set[UUID] = {
            x.organization_id for x in org_access_case_policies if x.is_private
        }

        all_org_users: list[model.User] = [
            x
            for x in users
            if app_impl.role_map[CommonRole.ORG_USER] in x.roles and len(x.roles) == 1
        ]

        org_user: model.User | None = None
        private_dc_ids: set[UUID] = set()

        # Select an ORG_USER from an organization with private data
        # collections AND who has cases in those collections
        for candidate_user in all_org_users:
            if candidate_user.organization_id not in orgs_with_private_dc:
                continue

            # Check if this user has any cases in their private data collections
            candidate_private_dc_ids: set[UUID] = {
                x.data_collection_id
                for x in org_access_case_policies
                if x.is_private and x.organization_id == candidate_user.organization_id
            }

            candidate_case_types: list[model.CaseType] = app.handle(
                command.CaseTypeCrudCommand(
                    user=candidate_user, operation=CrudOperation.READ_ALL
                )
            )
            candidate_case_stats = app.handle(
                command.RetrieveCaseTypeStatsCommand(user=candidate_user)
            )
            has_cases_ct_ids: set[UUID] = {
                x.case_type_id for x in candidate_case_stats if x.n_cases > 0
            }

            # Check if any case type has cases in private data collections
            found_own_cases = False
            for case_type in candidate_case_types:
                if case_type.id not in has_cases_ct_ids:
                    continue
                q_result: model.CaseQueryResult = app.handle(
                    command.RetrieveCasesByQueryCommand(
                        user=candidate_user,
                        case_query=model.CaseQuery(case_type_id=case_type.id),
                    )
                )
                if not q_result.case_ids:
                    continue
                candidate_cases: list[model.Case] = app.handle(
                    command.RetrieveCasesByIdCommand(
                        user=candidate_user,
                        case_type_id=case_type.id,
                        case_ids=q_result.case_ids[:20],
                    )
                )
                if any(
                    x.created_in_data_collection_id in candidate_private_dc_ids
                    for x in candidate_cases
                ):
                    found_own_cases = True
                    break

            if found_own_cases:
                org_user = candidate_user
                private_dc_ids = candidate_private_dc_ids
                break

        if org_user is None:
            raise ValueError("No ORG_USER found with cases in private data collections")

        # Find the first case type that has cases in a private data collection
        case_types: list[model.CaseType] = app.handle(
            command.CaseTypeCrudCommand(user=org_user, operation=CrudOperation.READ_ALL)
        )
        case_stats = app.handle(command.RetrieveCaseTypeStatsCommand(user=org_user))
        has_cases_ct_ids: set[UUID] = {
            x.case_type_id for x in case_stats if x.n_cases > 0
        }

        for own_case_type in case_types:
            assert own_case_type.id is not None
            if own_case_type.id not in has_cases_ct_ids:
                continue
            q_result: model.CaseQueryResult = app.handle(
                command.RetrieveCasesByQueryCommand(
                    user=org_user,
                    case_query=model.CaseQuery(case_type_id=own_case_type.id),
                )
            )
            candidate_ids: list[UUID] = q_result.case_ids[:20]
            if not candidate_ids:
                continue
            candidate_cases: list[model.Case] = app.handle(
                command.RetrieveCasesByIdCommand(
                    user=org_user,
                    case_type_id=own_case_type.id,
                    case_ids=candidate_ids,
                )
            )
            own_case_ids: list[UUID] = [
                c.id
                for c in candidate_cases
                if c.created_in_data_collection_id in private_dc_ids
                and c.id is not None
            ]
            if not own_case_ids:
                continue

            # Call RetrieveIsOwnCasesCommand: all own cases must be marked True
            is_own_map: dict[UUID, bool] = app.handle(
                command.RetrieveIsOwnCasesCommand(
                    user=org_user,
                    case_type_id=own_case_type.id,
                    case_ids=own_case_ids,
                )
            )

            assert set(is_own_map.keys()) == set(own_case_ids)
            assert all(is_own_map[cid] is True for cid in own_case_ids)

            # Test scenario: shared (non-own) cases should return False
            shared_case_ids: list[UUID] = [
                x.id
                for x in candidate_cases
                if x.created_in_data_collection_id not in private_dc_ids
                and x.id is not None
            ]
            if shared_case_ids:
                is_own_map_shared: dict[UUID, bool] = app.handle(
                    command.RetrieveIsOwnCasesCommand(
                        user=org_user,
                        case_type_id=own_case_type.id,
                        case_ids=shared_case_ids,
                    )
                )
                assert set(is_own_map_shared.keys()) == set(shared_case_ids)
                assert all(is_own_map_shared[cid] is False for cid in shared_case_ids)
            return

        raise ValueError(
            "No cases in a private data collection found for any case type"
        )
