import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import TestType as EnumTestType  # to avoid PyTest warning
from typing import Iterable

import pytest

from gen_epix import fastapp
from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.enum import Role as CommonRole
from gen_epix.commondb.domain.util import get_app_cfgs
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
        env._set_obj(root_user)
        root_permissions: set[Permission] = app.handle(
            command.RetrieveOwnPermissionsCommand(user=root_user)
        )

        # # --------------------------------------------------------------------------------------

        # # Code for performance profiling of a code chunk
        # import pyinstrument

        # users = app.handle(
        #     command.UserCrudCommand(
        #         user=root_user,
        #         operation=CrudOperation.READ_ALL,
        #     )
        # )
        # org_admin_policies = app.handle(
        #     command.OrganizationAdminPolicyCrudCommand(
        #         user=root_user,
        #         operation=CrudOperation.READ_ALL,
        #     )
        # )
        # org_admin_user: model.User = [
        #     x for x in users if x.id == org_admin_policies[0].user_id
        # ][0]
        # user_access_case_policies: list[model.UserAccessCasePolicy] = app.handle(
        #     command.UserAccessCasePolicyCrudCommand(
        #         user=org_admin_user,
        #         operation=CrudOperation.READ_ALL,
        #     )
        # )
        # org_user: model.User = [
        #     x
        #     for x in users
        #     if x.id in {y.user_id for y in user_access_case_policies}
        #     and app_impl.role_map[CommonRole.ORG_USER] in x.roles
        #     and len(x.roles) == 1
        # ][0]

        # profiler = pyinstrument.Profiler(async_mode="enabled")
        # profiler.start()

        # t0 = datetime.datetime.now()

        # case_stats = app.handle(command.RetrieveCaseStatsCommand(user=org_user))
        # case_sets: list[model.CaseSet] = app.handle(
        #     command.CaseSetCrudCommand(
        #         user=org_user,
        #         operation=CrudOperation.READ_ALL,
        #     )
        # )
        # case_set_ids: list[UUID] = [x.id for x in case_sets]  # type:ignore[assignment]
        # case_set_stats = app.handle(
        #     command.RetrieveCaseStatsCommand(user=org_user, case_set_ids=case_set_ids)
        # )

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
            and app_impl.role_map[CommonRole.ORG_USER] in x.roles
            and len(x.roles) == 1
        ][0]
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

        # Get case type and and case set stats
        case_stats = app.handle(command.RetrieveCaseStatsCommand(user=org_user))
        case_set_stats = app.handle(command.RetrieveCaseStatsCommand(user=org_user))

        # Go over all case types with data
        has_cases_case_type_ids = {x.case_type_id for x in case_stats if x.n_cases > 0}
        for case_type in case_types:
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
            if len(complete_case_type.case_type_cols) <= 1:
                continue

            # Retrieve cases based on a filter
            # print(f"Retrieving cases for case type {complete_case_type.name}")
            filters: list = []
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
            dist_case_type_cols = [
                case_type_col
                for case_type_col in complete_case_type.case_type_cols.values()
                if complete_case_type.cols[case_type_col.col_id].col_type
                == enum.ColType.GENETIC_DISTANCE
            ]
            for dist_case_type_col in dist_case_type_cols:
                assert dist_case_type_col is not None
                assert dist_case_type_col.id is not None
                for tree_algorithm_code in (
                    dist_case_type_col.tree_algorithm_codes or []
                ):
                    phylogenetic_tree: model.PhylogeneticTree = app.handle(
                        command.RetrievePhylogeneticTreeByCasesCommand(
                            user=org_user,
                            case_type_id=complete_case_type.id,
                            genetic_distance_case_type_col_id=dist_case_type_col.id,
                            tree_algorithm=tree_algorithm_code,
                            case_ids=case_ids,
                        )
                    )
                    if phylogenetic_tree.sequence_ids:
                        raise ValueError("Sequence IDs should not be returned")
                    assert phylogenetic_tree.leaf_ids is not None
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
                has_seq_case_ids = [
                    x.id
                    for x in cases
                    if x.content.get(genetic_sequence_case_type_col.id)
                ]
                if not has_seq_case_ids:
                    continue
                # TODO: retrieval of genetic sequences method likely not needed anymore, delete when this is confirmed or otherwise enable again
                # # Retrieve genetic sequence
                # genetic_sequences: list[model.GeneticSequence] = app.handle(
                #     command.RetrieveGeneticSequenceByCaseCommand(
                #         user=org_user,
                #         case_ids=has_seq_case_ids[0:1],
                #         genetic_sequence_case_type_col_id=genetic_sequence_case_type_col.id,
                #     )
                # )
                # if not genetic_sequences:
                #     raise ValueError("Genetic sequence should not be empty")
                # for seq in genetic_sequences:
                #     if not seq.id:
                #         raise ValueError("Genetic sequence ID should not be empty")
                #     if not hasattr(seq, "nucleotide_sequence"):
                #         raise ValueError(
                #             "Genetic sequence should have nucleotide_sequence attribute"
                #         )

                # Retrieve genetic sequences in FASTA format
                fasta_iterator: Iterable[str] = app.handle(
                    command.RetrieveGeneticSequenceFastaByCaseCommand(
                        user=org_user,
                        case_type_id=complete_case_type.id,
                        case_ids=has_seq_case_ids[0:1],
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
                # Retrieve SequencingProtocols
                sequencing_protocols: list[seqdb_model.SequencingProtocol] = app.handle(
                    command.RetrieveSequencingProtocolsCommand(
                        user=org_user,
                    )
                )
                if not sequencing_protocols:
                    raise ValueError("Library prep protocols should not be None")
                for sequencing_protocol in sequencing_protocols:
                    if not sequencing_protocol.id:
                        raise ValueError("Library prep protocol ID should not be empty")
                # Retrieve AssemblyProtocols
                assembly_protocols: list[seqdb_model.AssemblyProtocol] = app.handle(
                    command.RetrieveAssemblyProtocolsCommand(
                        user=org_user,
                    )
                )
                if not assembly_protocols:
                    raise ValueError("Assembly protocols should not be None")
                for assembly_protocol in assembly_protocols:
                    if not assembly_protocol.id:
                        raise ValueError("Assembly protocol ID should not be empty")

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
