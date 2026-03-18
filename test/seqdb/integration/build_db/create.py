from test.seqdb.integration.build_db.base import (
    BELOW_APP_ADMIN_DATA_USERS,
    BELOW_APP_ADMIN_REFDATA_USERS,
    BELOW_APP_ADMIN_USERS,
    DATA_USERS,
    REFDATA_ADMIN_OR_ABOVE_USERS,
    SKIP_RAISE,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env

import pytest

from gen_epix.seqdb.domain import enum, exc, model


@pytest.mark.scenario_ids("TC-11-09-02", "TC-11-10-01", "TC-11-11-01", "TC-11-12-01")
class TestCreate:
    # CREATE tests

    def test_create_user_first_root(self, env: Env) -> None:
        # Create a first root user and organization
        user = env.retrieve_user_by_key("root1_1@org1.org")
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
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_sequencing_protocol(exec_user, f"sequencing_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_sequencing_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_sequencing_protocol(exec_user, "sequencing_protocol11")

    def test_create_assembly_protocol(self, env: Env) -> None:
        # Create assembly_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_assembly_protocol(exec_user, f"assembly_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_assembly_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_assembly_protocol(exec_user, "assembly_protocol11")

    def test_create_locus_detection_protocol(self, env: Env) -> None:
        # Create locus_detection_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_locus_detection_protocol(
                exec_user, f"locus_detection_protocol{i}"
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_locus_detection_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_locus_detection_protocol(
                    exec_user, "locus_detection_protocol11"
                )

    def test_create_pcr_protocol(self, env: Env) -> None:
        # Create pcr_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_pcr_protocol(exec_user, f"pcr_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_pcr_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_pcr_protocol(exec_user, "pcr_protocol11")

    def test_create_ast_protocol(self, env: Env) -> None:
        # Create ast_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_ast_protocol(exec_user, f"ast_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_ast_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_ast_protocol(exec_user, "ast_protocol11")

    def test_create_alignment_protocol(self, env: Env) -> None:
        # Create alignment_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_alignment_protocol(exec_user, f"alignment_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_alignment_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_alignment_protocol(exec_user, "alignment_protocol11")

    def test_create_taxonomy_protocol(self, env: Env) -> None:
        # Create taxonomy_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_taxonomy_protocol(exec_user, f"taxonomy_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_taxonomy_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_taxonomy_protocol(exec_user, "taxonomy_protocol11")

    def test_create_seq_classification_protocol(self, env: Env) -> None:
        # Create seq_classification_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_seq_classification_protocol(
                exec_user, f"seq_classification_protocol{i}"
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_seq_classification_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_seq_classification_protocol(
                    exec_user, "seq_classification_protocol11"
                )

    def test_create_seq_distance_protocol(self, env: Env) -> None:
        # Create seq_distance_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_seq_distance_protocol(exec_user, f"seq_distance_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_seq_distance_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_seq_distance_protocol(exec_user, "seq_distance_protocol11")

    def test_create_snp_detection_protocol(self, env: Env) -> None:
        # Create snp_detection_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_snp_detection_protocol(exec_user, f"snp_detection_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_snp_detection_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_snp_detection_protocol(exec_user, "snp_detection_protocol11")

    def test_create_mlva_detection_protocol(self, env: Env) -> None:
        # Create mlva_detection_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_mlva_detection_protocol(exec_user, f"mlva_detection_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_mlva_detection_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_mlva_detection_protocol(
                    exec_user, "mlva_detection_protocol11"
                )

    def test_create_kmer_detection_protocol(self, env: Env) -> None:
        # Create kmer_detection_protocol as root, app_admin, refdata_admin
        for i, exec_user in enumerate(REFDATA_ADMIN_OR_ABOVE_USERS, start=1):
            env.create_kmer_detection_protocol(exec_user, f"kmer_detection_protocol{i}")

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_kmer_detection_protocol_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_DATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_kmer_detection_protocol(
                    exec_user, "kmer_detection_protocol11"
                )

    def test_create_sample(self, env: Env) -> None:
        # Create Sample as root, app_admin, org_admin and org_user
        for i, exec_user in enumerate(DATA_USERS, start=1):
            env.create_sample(
                exec_user,
                code=f"sample{i}",
                created_in_data_collection_or_str=f"data_collection{i}",
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_sample_raise(self, env: Env) -> None:
        # Check that below data users cannot create Sample
        for exec_user in BELOW_APP_ADMIN_REFDATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_sample(
                    exec_user,
                    code="sample11",
                    created_in_data_collection_or_str="data_collection1",
                )

    def test_create_file(self, env: Env) -> None:
        for exec_user in DATA_USERS:
            env.create_file(
                exec_user,
                env.DUMMY_VALUES["fasta_bytes1"],
                enum.FileFormat.FASTA,
                compression=enum.FileCompression.NONE,
            )
            env.create_file(
                exec_user,
                env.DUMMY_VALUES["fasta_gzip_bytes1"],
                enum.FileFormat.FASTA,
                compression=enum.FileCompression.GZIP,
            )
            env.create_file(
                exec_user,
                env.DUMMY_VALUES["fwd_fastq_bytes1"],
                enum.FileFormat.FASTQ,
                compression=enum.FileCompression.NONE,
            )
            env.create_file(
                exec_user,
                env.DUMMY_VALUES["fwd_fastq_gzip_bytes1"],
                enum.FileFormat.FASTQ,
                compression=enum.FileCompression.GZIP,
            )

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_file_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_REFDATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_file(
                    exec_user,
                    env.DUMMY_VALUES["fasta_bytes1"],
                    enum.FileFormat.FASTA,
                )
                env.create_file(
                    exec_user,
                    env.DUMMY_VALUES["fwd_fastq_bytes1"],
                    enum.FileFormat.FASTQ,
                )
        with pytest.raises(exc.InvalidArgumentsError):
            env.create_file("root1_1", b"", enum.FileFormat.FASTA)
            env.create_file(
                "root1_1",
                env.DUMMY_VALUES["invalid_fasta_bytes1"],
                enum.FileFormat.FASTA,
                compression=enum.FileCompression.NONE,
            )
            env.create_file(
                "root1_1",
                env.DUMMY_VALUES["fasta_bytes1"],
                enum.FileFormat.FASTA,
                compression=enum.FileCompression.GZIP,
            )
            env.create_file(
                "root1_1",
                env.DUMMY_VALUES["fasta_gzip_bytes1"],
                enum.FileFormat.FASTA,
                compression=enum.FileCompression.NONE,
            )
            env.create_file(
                "root1_1",
                env.DUMMY_VALUES["invalid_fastq_bytes1"],
                enum.FileFormat.FASTQ,
                compression=enum.FileCompression.NONE,
            )
            env.create_file(
                "root1_1",
                env.DUMMY_VALUES["fwd_fastq_bytes1"],
                enum.FileFormat.FASTQ,
                compression=enum.FileCompression.GZIP,
            )
            env.create_file(
                "root1_1",
                env.DUMMY_VALUES["fwd_fastq_gzip_bytes1"],
                enum.FileFormat.FASTQ,
                compression=enum.FileCompression.NONE,
            )

    def test_create_read_set(self, env: Env) -> None:
        # Create ReadSet as root, app_admin, org_admin and org_user
        kwargs = {
            "fwd_uri": env.DUMMY_VALUES["fwd_reads_uri1"],
            "rev_uri": env.DUMMY_VALUES["rev_reads_uri1"],
            "sample_or_str": "sample1",
            "sequencing_protocol_or_str": "sequencing_protocol1",
        }
        for exec_user in DATA_USERS:
            env.create_read_set(exec_user, **kwargs)

    @pytest.mark.skipif(SKIP_RAISE, reason="Skipped to facilitate debugging")
    def test_create_read_set_raise(self, env: Env) -> None:
        # Check that below data users cannot create ReadSet
        kwargs = {
            "fwd_uri": env.DUMMY_VALUES["fwd_reads_uri1"],
            "rev_uri": env.DUMMY_VALUES["rev_reads_uri1"],
            "sample_or_str": "sample1",
            "sequencing_protocol_or_str": "sequencing_protocol1",
        }
        for exec_user in BELOW_APP_ADMIN_REFDATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_read_set(exec_user, **kwargs)

    def test_create_file_for_read_set(self, env: Env) -> None:
        kwargs = {
            "sample_or_str": "sample1",
            "sequencing_protocol_or_str": "sequencing_protocol1",
            "fwd_reads_hash": env.DUMMY_VALUES["fwd_reads_hash1"],
            "rev_reads_hash": env.DUMMY_VALUES["rev_reads_hash1"],
            "file_format": enum.FileFormat.FASTQ,
            "file_compression": enum.FileCompression.GZIP,
        }
        for exec_user in DATA_USERS:
            fwd_file = env.create_file(
                exec_user,
                env.DUMMY_VALUES["fwd_fastq_gzip_bytes1"],
                kwargs["file_format"],
                compression=kwargs["file_compression"],
            )
            rev_file = env.create_file(
                exec_user,
                env.DUMMY_VALUES["rev_fastq_gzip_bytes1"],
                format=kwargs["file_format"],
                compression=kwargs["file_compression"],
            )
            env.create_read_set(
                exec_user, fwd_file_id=fwd_file.id, rev_file_id=rev_file.id, **kwargs
            )

    def test_create_seq(self, env: Env) -> None:
        # Create Seq as root, app_admin, org_admin and org_user
        for i, exec_user in enumerate(DATA_USERS, start=1):
            env.create_seq(
                exec_user,
                sample_or_str=f"sample{i}",
                protocol_or_str="assembly_protocol1",
            )

    def test_create_seq_raise(self, env: Env) -> None:
        for exec_user in BELOW_APP_ADMIN_REFDATA_USERS:
            with pytest.raises(exc.UnauthorizedAuthError):
                env.create_seq(
                    exec_user,
                    sample_or_str="sample1",
                    protocol_or_str="assembly_protocol1",
                )

    def test_create_seq_with_file(self, env: Env) -> None:
        for i, exec_user in enumerate(DATA_USERS, start=1):
            file = env.create_file(
                exec_user,
                env.DUMMY_VALUES["fasta_gzip_bytes1"],
                enum.FileFormat.FASTA,
                compression=enum.FileCompression.GZIP,
            )
            env.create_seq(
                exec_user,
                sample_or_str=f"sample{i}",
                protocol_or_str="assembly_protocol2",
                file_id=file.id,
                file_format=enum.FileFormat.FASTA,
                file_compression=enum.FileCompression.GZIP,
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
        # Sequencing protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_sequencing_protocol("refdata_admin1_1", "sequencing_protocol1")
        # Assembly protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_assembly_protocol("refdata_admin1_1", "assembly_protocol1")
        # Locus detection protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_locus_detection_protocol(
                "refdata_admin1_1", "locus_detection_protocol1"
            )
        # PCR protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_pcr_protocol("refdata_admin1_1", "pcr_protocol1")
        # AST protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_ast_protocol("refdata_admin1_1", "ast_protocol1")
        # Alignment protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_alignment_protocol("refdata_admin1_1", "alignment_protocol1")
        # Taxonomy protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_taxonomy_protocol("refdata_admin1_1", "taxonomy_protocol1")
        # Seq classification protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_seq_classification_protocol(
                "refdata_admin1_1", "seq_classification_protocol1"
            )
        # Seq distance protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_seq_distance_protocol(
                "refdata_admin1_1", "seq_distance_protocol1"
            )
        # SNP detection protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_snp_detection_protocol(
                "refdata_admin1_1", "snp_detection_protocol1"
            )
        # MLVA detection protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_mlva_detection_protocol(
                "refdata_admin1_1", "mlva_detection_protocol1"
            )
        # Kmer detection protocol already exists
        with pytest.raises(exc.UniqueConstraintViolationError):
            env.create_kmer_detection_protocol(
                "refdata_admin1_1", "kmer_detection_protocol1"
            )

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
        kwargs = {
            "fwd_uri": env.DUMMY_VALUES["fwd_reads_uri1"],
            "rev_uri": env.DUMMY_VALUES["rev_reads_uri1"],
            "sample_or_str": "sample1",
        }
        with pytest.raises(exc.InvalidLinkIdsError):
            env.create_read_set("root1_1", set_dummy_protocol=True, **kwargs)
