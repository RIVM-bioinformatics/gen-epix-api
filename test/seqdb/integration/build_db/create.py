from test.seqdb.integration.build_db.base import (
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_METADATA_USERS,
    BELOW_APP_ADMIN_USERS,
    DATA_USERS,
    REFDATA_ADMIN_OR_ABOVE_USERS,
    SKIP_RAISE,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env

import pytest

from gen_epix.seqdb.domain import exc, model

VALID_FASTA_FILE_CONTENT = b""">seq1
AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG
AGCTAGCTAGCTAGCACAC
"""
VALID_FASTQ_FILE_CONTENT = b"""@3c2bbdcb-b017-4f1e-85c7-fd0fc34d356e
AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG
+
IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"""


class TestCreate:
    # CREATE tests

    def test_create_user_first_root(self, env: Env) -> None:
        # Create a first root user and organization
        user: model.User = env.retrieve_user_by_key("root1_1@org1.org")  # type: ignore[assignment]
        user.name = "root1_1"
        env._set_obj(user)
        env._set_obj(
            env.read_one_by_property("root1_1", model.Organization, "name", "org1")
        )

    def test_create_user_additional_root(self, env: Env) -> None:
        # Create additional root user, including in a different organization
        env.invite_and_register_user("root1_1", "root1_2")
        env.create_organization("root1_2", "org2")
        env.create_organization("root1_2", "org3")
        env.invite_and_register_user("root1_2", "root2_1")
        env.invite_and_register_user("root1_2", "root2_2")

    def test_create_user_app_admin(self, env: Env) -> None:
        # Create invitations for app_admin as root
        env.invite_and_register_user("root1_1", "app_admin1_1")
        env.invite_and_register_user("root2_1", "app_admin1_2")
        env.invite_and_register_user("root1_2", "app_admin2_1")
        env.invite_and_register_user("root2_2", "app_admin2_2")
        env.invite_and_register_user("root1_2", "app_admin3_1")
        env.invite_and_register_user("root2_2", "app_admin3_2")

    def test_create_user_organization(self, env: Env) -> None:
        # Create organizations as root and app_admin
        env.create_organization("root1_2", "org4")
        env.create_organization("app_admin1_2", "org5")
        env.create_organization("app_admin2_1", "org6")
        if env.verbose:
            env.print_organizations()

    def test_create_user_refdata_admin(self, env: Env) -> None:
        # Create refdata_admin as root and app_admin
        env.invite_and_register_user("root2_1", "refdata_admin1_1")
        env.invite_and_register_user("app_admin2_1", "refdata_admin1_2")
        env.invite_and_register_user("app_admin1_1", "refdata_admin2_1")
        env.invite_and_register_user("app_admin1_2", "refdata_admin2_2")

    def test_create_user_org_admin(self, env: Env) -> None:
        # Create org_admin as root and app_admin
        env.invite_and_register_user("root2_1", "org_admin1_1")
        env.invite_and_register_user("app_admin2_1", "org_admin1_2")
        env.invite_and_register_user("app_admin1_1", "org_admin2_1")
        env.invite_and_register_user("app_admin1_2", "org_admin2_2")
        env.invite_and_register_user("app_admin1_1", "org_admin3_1")
        env.invite_and_register_user("app_admin1_2", "org_admin3_2")
        env.invite_and_register_user("app_admin2_1", "org_admin4_1")
        env.invite_and_register_user("app_admin2_2", "org_admin4_2")
        env.invite_and_register_user("app_admin3_1", "org_admin5_1")
        env.invite_and_register_user("app_admin3_2", "org_admin5_2")

    def test_create_org_admin_policy(self, env: Env) -> None:
        # Add org_admin policy
        env.create_org_admin_policy("root1_1", "app_admin1_1", "org5")
        env.create_org_admin_policy("root2_1", "org_admin1_1", "org1")
        env.create_org_admin_policy("app_admin1_1", "app_admin2_1", "org5")
        env.create_org_admin_policy("app_admin2_1", "org_admin2_1", "org2")
        env.create_org_admin_policy("app_admin3_1", "org_admin3_1", "org1")
        env.create_org_admin_policy("app_admin3_1", "org_admin3_1", "org2")
        env.create_org_admin_policy("app_admin3_1", "org_admin3_1", "org3")
        env.create_org_admin_policy("app_admin3_1", "org_admin4_1", "org3")
        env.create_org_admin_policy("app_admin3_1", "org_admin4_1", "org4")
        env.create_org_admin_policy("app_admin3_1", "org_admin4_1", "org5")
        env.create_org_admin_policy("app_admin3_1", "org_admin5_1", "org5")
        if env.verbose:
            env.print_org_admin_policies()

    def test_create_user_org_user(self, env: Env) -> None:
        # Create org_user as root, app_admin and org_admin
        env.invite_and_register_user("root1_1", "org_user1_1")
        env.invite_and_register_user("root1_1", "org_user1_2")
        env.invite_and_register_user("root2_1", "org_user1_3")
        env.invite_and_register_user("app_admin1_1", "org_user2_1")
        env.invite_and_register_user("org_admin3_1", "org_user2_2")
        env.invite_and_register_user("org_admin3_1", "org_user2_3")
        env.invite_and_register_user("org_admin3_1", "org_user3_1")
        env.invite_and_register_user("org_admin4_1", "org_user3_2")
        env.invite_and_register_user("org_admin4_1", "org_user3_3")
        env.invite_and_register_user("org_admin4_1", "org_user4_1")
        env.invite_and_register_user("org_admin4_1", "org_user4_2")
        env.invite_and_register_user("org_admin4_1", "org_user4_3")
        env.invite_and_register_user("org_admin4_1", "org_user5_1")
        env.invite_and_register_user("org_admin5_1", "org_user5_2")
        env.invite_and_register_user("org_admin5_1", "org_user5_3")

    def test_create_user_guest(self, env: Env) -> None:
        # Create guest as root, app_admin and org_admin
        env.invite_and_register_user("root1_1", "guest1_1")
        env.invite_and_register_user("root2_1", "guest1_2")
        env.invite_and_register_user("app_admin1_1", "guest2_1")
        env.invite_and_register_user("app_admin1_2", "guest2_2")
        env.invite_and_register_user("org_admin3_1", "guest3_1")
        env.invite_and_register_user("org_admin4_1", "guest3_2")
        if env.verbose:
            env.print_users()

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_user_raise(self, env: Env) -> None:
        # Invite user by admin
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "root1_11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "app_admin1_11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "refdata_admin1_11")
        for exec_user in ["org_user1_1", "guest1_1"]:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "root1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "app_admin1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "refdata_admin1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "org_admin1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "org_user1_11")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.invite_and_register_user(exec_user, "guest1_11")
        # Invite user by org admin
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("org_admin1_1", "app_admin1_1")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_organization_raise(self, env: Env) -> None:
        # Check if non-root, non-app_admin users cannot create an organization
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("org_admin1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("refdata_admin1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("org_user1_1", "org11")
        with pytest.raises(exc.UnauthorizedAuthError):
            env.create_organization("guest1_1", "org11")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_org_admin_policy_raise(self, env: Env) -> None:
        for exec_user in [
            "org_admin1_1",
            "refdata_admin1_1",
            "org_user1_1",
            "guest1_1",
        ]:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "root2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "app_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "refdata_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "org_admin2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "org_user2_1", "org1")
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_org_admin_policy(exec_user, "guest2_1", "org1")

    def test_create_data_collection(self, env: Env) -> None:
        # Create data_collection as root, app_admin
        env.create_data_collection("root1_1", "data_collection1")
        env.create_data_collection("app_admin1_1", "data_collection2")
        env.create_data_collection("app_admin1_2", "data_collection3")
        env.create_data_collection("app_admin2_1", "data_collection4")
        env.create_data_collection("app_admin2_2", "data_collection5")
        if env.verbose:
            env.print_data_collections()

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_data_collection_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_data_collection(exec_user, "data_collection11")

    def test_create_sequencing_protocol(self, env: Env) -> None:
        # Create sequencing_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.create_sequencing_protocol(exec_user, f"sequencing_protocol{i + 1}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_library_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_sequencing_protocol(exec_user, "sequencing_protocol11")

    def test_create_assembly_protocol(self, env: Env) -> None:
        # Create assembly_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS):
            env.create_assembly_protocol(exec_user, f"assembly_protocol{i + 1}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_assembly_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_assembly_protocol(exec_user, "assembly_protocol11")

    def test_create_file(self, env: Env) -> None:
        for exec_user in DATA_USERS:
            env.create_file(exec_user, content=VALID_FASTA_FILE_CONTENT)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_file_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_METADATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_file(exec_user, content=VALID_FASTA_FILE_CONTENT)

    def test_create_file_invalid_content(self, env: Env) -> None:
        with pytest.raises(exc.InvalidArgumentsError):
            env.create_file("root1_1", content=b"")
            env.create_file("root1_1", content=b"INVALID FILE CONTENT")
            env.create_file("root1_1", content=b">MY OWN HEADER ID\nAGVVAGFAEAADA")

    def test_create_read_set(self, env: Env) -> None:
        # Create ReadSet as root, app_admin, org_admin and org_user
        kwargs = env.get_default_kwargs(model.ReadSet) | {
            "sequencing_protocol_or_str": "sequencing_protocol1",
        }
        for exec_user in DATA_USERS:
            env.create_read_set(exec_user, **kwargs)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_read_set_raise(self, env: Env) -> None:
        # Check that below data users cannot create ReadSet
        kwargs = env.get_default_kwargs(model.ReadSet) | {
            "sequencing_protocol_or_str": "sequencing_protocol1",
        }
        for exec_user in BELOW_APP_ADMIN_METADATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_read_set(exec_user, **kwargs)

    def test_create_file_for_read_set(self, env: Env) -> None:
        kwargs = env.get_default_kwargs(model.ReadSet) | {
            "sequencing_protocol_or_str": "sequencing_protocol1",
        }
        for exec_user in DATA_USERS:
            fwd_file = env.create_file(
                exec_user, content=kwargs["fwd_reads_hash_or_content"]
            )
            rev_file = env.create_file(
                exec_user, content=kwargs["rev_reads_hash_or_content"]
            )
            env.create_read_set(
                exec_user, fwd_file_id=fwd_file.id, rev_file_id=rev_file.id, **kwargs
            )

    def test_create_seq(self, env: Env) -> None:
        # Create Seq as root, app_admin, org_admin and org_user
        assembly_protocol: model.AssemblyProtocol = env.create_assembly_protocol(
            "root1_1", "assembly_protocol99"
        )
        for exec_user in DATA_USERS:
            env.create_seq(
                exec_user,
                assembly_protocol_or_str=assembly_protocol,
            )

    def test_create_seq_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_METADATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_seq(
                    exec_user,
                    assembly_protocol_or_str="assembly_protocol99",
                )

    def test_create_seq_with_file(self, env: Env) -> None:
        for exec_user in DATA_USERS:
            file = env.create_file(exec_user, content=VALID_FASTA_FILE_CONTENT)
            env.create_seq(
                exec_user,
                assembly_protocol_or_str="assembly_protocol99",
                file_id=file.id,
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_object_already_exists(self, env: Env) -> None:
        # Organization already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_organization("root2_2", "org2")
        # User already exists
        with pytest.raises(exc.UserAlreadyExistsAuthError):
            env.invite_and_register_user("root1_2", "root2_1")
        with pytest.raises(exc.UserAlreadyExistsAuthError):
            env.invite_and_register_user("app_admin1_1", "org_admin2_1")
        # Organization admin policy already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_org_admin_policy("app_admin1_1", "org_admin1_1", "org1")
        # Library prep protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_sequencing_protocol("refdata_admin1_1", "sequencing_protocol1")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_object_invalid_reference(self, env: Env) -> None:
        # User.organization does not exist
        with pytest.raises(exc.InvalidIdsError):
            env.invite_and_register_user(
                "root1_1", "root11_1", set_dummy_organization=True
            )
        # UserInvitation.token is invalid
        with pytest.raises(exc.UnauthorizedAuthError):
            env.invite_and_register_user("root1_1", "root1_11", set_dummy_token=True)
        # TODO: OrganizationAdminPolicy.user does not exist
        # ReadSet.sequencing_protocol does not exist
        with pytest.raises(exc.InvalidLinkIdsError):
            env.create_read_set(
                "root1_1",
                **env.get_default_kwargs(model.ReadSet),
                set_dummy_sequencing_protocol=True,
            )
