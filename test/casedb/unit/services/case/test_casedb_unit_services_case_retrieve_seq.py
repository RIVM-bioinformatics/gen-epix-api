from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock, patch
from types import SimpleNamespace
from uuid import uuid4

import pytest

import gen_epix.casedb.services.case.retrieve_seq as retrieve_seq
from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum


class TestRetrieveGeneticSequenceFasta(BaseCrudTestCase):
    """Test sequence identifier extraction and missing-value handling."""

    def test_get_seq_ids_preserves_missing_values_and_parses_uuids(self) -> None:
        case_type_id = uuid4()
        case_ids = [uuid4(), uuid4()]
        seq_col_id = uuid4()
        seq_id = uuid4()
        missing_case = Mock()
        missing_case.content = {seq_col_id: None}
        populated_case = Mock()
        populated_case.content = {seq_col_id: str(seq_id)}
        cases = [missing_case, populated_case]
        self.service._retrieve_cases_with_content_right.return_value = (cases, False)

        result = retrieve_seq._get_seq_ids_from_cases(
            self.service,
            self.uow,
            self.user,
            Mock(),
            case_type_id,
            case_ids,
            seq_col_id,
        )

        assert result == [None, seq_id]

    def test_missing_sequence_id_raises_no_results_error(self) -> None:
        cmd = Mock()
        cmd.case_type_id = uuid4()
        cmd.genetic_sequence_col_id = uuid4()
        cmd.case_ids = [uuid4()]
        cmd.user = self.user
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )

        with (
            patch(
                f"{retrieve_seq.__name__}.BaseCaseAbacPolicy.get_case_abac_from_command",
                return_value=Mock(),
            ),
            patch(
                f"{retrieve_seq.__name__}._get_seq_ids_from_cases",
                return_value=[None],
            ),
            pytest.raises(exc.NoResultsError, match="Not all cases have a sequence"),
        ):
            retrieve_seq.case_service_retrieve_genetic_sequence_fasta_by_case(
                self.service, cmd
            )

        self.service.app.handle.assert_not_called()

    def test_get_seq_ids_returns_empty_list_for_no_cases(self) -> None:
        self.service._retrieve_cases_with_content_right.return_value = ([], False)

        result = retrieve_seq._get_seq_ids_from_cases(
            self.service,
            self.uow,
            self.user,
            Mock(),
            uuid4(),
            [],
            uuid4(),
        )

        assert result == []

    def test_fasta_retrieval_rejects_empty_case_ids(self) -> None:
        cmd = Mock()
        cmd.case_type_id = uuid4()
        cmd.genetic_sequence_col_id = uuid4()
        cmd.case_ids = []
        cmd.user = self.user
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )

        with pytest.raises(exc.InvalidArgumentsError, match="No case IDs given"):
            retrieve_seq.case_service_retrieve_genetic_sequence_fasta_by_case(
                self.service, cmd
            )

        self.service._retrieve_cases_with_content_right.assert_not_called()
        self.service.app.handle.assert_not_called()

    def test_fasta_retrieval_dispatches_sequence_ids_and_returns_iterator(self) -> None:
        case_ids = [uuid4(), uuid4()]
        seq_ids = [uuid4(), uuid4()]
        case_abac = Mock()
        fasta_lines = iter([">sequence", "ACGT"])
        cmd = Mock()
        cmd.case_type_id = uuid4()
        cmd.genetic_sequence_col_id = uuid4()
        cmd.case_ids = case_ids
        cmd.user = self.user
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.app.handle.return_value = fasta_lines

        with (
            patch.object(
                retrieve_seq.BaseCaseAbacPolicy,
                "get_case_abac_from_command",
                return_value=case_abac,
            ),
            patch.object(
                retrieve_seq, "_get_seq_ids_from_cases", return_value=seq_ids
            ) as get_seq_ids,
        ):
            result = retrieve_seq.case_service_retrieve_genetic_sequence_fasta_by_case(
                self.service, cmd
            )

        assert result is fasta_lines
        get_seq_ids.assert_called_once_with(
            self.service,
            self.uow,
            self.user,
            case_abac,
            cmd.case_type_id,
            case_ids,
            cmd.genetic_sequence_col_id,
        )
        sent_command = self.service.app.handle.call_args.args[0]
        assert isinstance(sent_command, command.RetrieveGeneticSequenceFastaByIdCommand)
        assert sent_command.seq_ids == seq_ids

    def test_retrieve_protocols_filters_by_requested_type(self) -> None:
        assembly_protocol = SimpleNamespace(
            protocol_type=seqdb_enum.ProtocolType.ASSEMBLY
        )
        distance_protocol = SimpleNamespace(
            protocol_type=seqdb_enum.ProtocolType.SEQ_DISTANCE
        )
        cmd = Mock()
        cmd.user = self.user
        cmd.protocol_type = seqdb_enum.ProtocolType.ASSEMBLY
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.app.handle.return_value = [assembly_protocol, distance_protocol]

        result = retrieve_seq.case_service_retrieve_protocols(self.service, cmd)

        assert result == [assembly_protocol]
        sent_command = self.service.app.handle.call_args.args[0]
        assert isinstance(sent_command, seqdb_command.ProtocolCrudCommand)
        assert sent_command.operation == CrudOperation.READ_ALL

    def test_phylogenetic_tree_handles_empty_case_ids(self) -> None:
        protocol_id = uuid4()
        seqdb_protocol_id = uuid4()
        algorithm = enum.TreeAlgorithmType.UPGMA
        protocol = SimpleNamespace(
            id=protocol_id, seqdb_seq_distance_protocol_id=seqdb_protocol_id
        )
        dist_col = SimpleNamespace(tree_algorithm_codes={algorithm})
        tree = model.PhylogeneticTree(
            tree_algorithm_code=algorithm,
            newick_repr=";",
        )
        cmd = Mock()
        cmd.tree_algorithm = algorithm
        cmd.case_ids = []
        cmd.user = self.user
        cmd.allowed_qc_results = set()
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.app.handle.return_value = tree

        with patch.object(
            retrieve_seq,
            "_retrieve_case_profile_map",
            return_value=(protocol, {}, dist_col),
        ):
            result = retrieve_seq.case_service_retrieve_phylogenetic_tree(
                self.service, cmd
            )

        assert result is tree
        assert result.protocol_id == protocol_id
        sent_command = self.service.app.handle.call_args.args[0]
        assert isinstance(
            sent_command, command.RetrievePhylogeneticTreeByProfilesCommand
        )
        assert sent_command.profile_ids == []
        assert sent_command.seqdb_protocol_id == seqdb_protocol_id

    def test_phylogenetic_tree_maps_profile_leaves_to_case_ids(self) -> None:
        case_id = uuid4()
        profile_id = uuid4()
        protocol_id = uuid4()
        seqdb_protocol_id = uuid4()
        algorithm = enum.TreeAlgorithmType.UPGMA
        protocol = SimpleNamespace(
            id=protocol_id, seqdb_seq_distance_protocol_id=seqdb_protocol_id
        )
        dist_col = SimpleNamespace(tree_algorithm_codes={algorithm})
        tree = model.PhylogeneticTree(
            tree_algorithm_code=algorithm,
            newick_repr="(profile);",
        )
        cmd = Mock()
        cmd.tree_algorithm = algorithm
        cmd.case_ids = [case_id]
        cmd.user = self.user
        cmd.allowed_qc_results = set()
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.app.handle.return_value = tree

        with patch.object(
            retrieve_seq,
            "_retrieve_case_profile_map",
            return_value=(protocol, {case_id: profile_id}, dist_col),
        ):
            result = retrieve_seq.case_service_retrieve_phylogenetic_tree(
                self.service, cmd
            )

        assert result.protocol_id == protocol_id
        sent_command = self.service.app.handle.call_args.args[0]
        assert sent_command.profile_ids == [profile_id]
        assert sent_command.seqdb_protocol_id == seqdb_protocol_id
        assert sent_command.props["leaf_id_mapper"](profile_id) == case_id

    def test_phylogenetic_tree_rejects_disallowed_algorithm(self) -> None:
        algorithm = enum.TreeAlgorithmType.UPGMA
        protocol = SimpleNamespace(id=uuid4(), seqdb_seq_distance_protocol_id=uuid4())
        dist_col = SimpleNamespace(tree_algorithm_codes=set())
        cmd = Mock()
        cmd.tree_algorithm = algorithm
        cmd.case_ids = []
        cmd.user = self.user
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )

        with (
            patch.object(
                retrieve_seq,
                "_retrieve_case_profile_map",
                return_value=(protocol, {}, dist_col),
            ),
            pytest.raises(
                exc.UnauthorizedAuthError, match="no read access to tree algorithm"
            ),
        ):
            retrieve_seq.case_service_retrieve_phylogenetic_tree(self.service, cmd)

        self.service.app.handle.assert_not_called()

    def test_retrieve_case_profile_map_extracts_populated_profiles(self) -> None:
        case_type_id = uuid4()
        col_id = uuid4()
        ref_col_id = uuid4()
        protocol_id = uuid4()
        profile_id = uuid4()
        case_id = uuid4()
        protocol = SimpleNamespace(id=protocol_id)
        dist_col = SimpleNamespace(case_type_id=case_type_id, ref_col_id=ref_col_id)
        ref_col = SimpleNamespace(
            col_type=enum.ColType.GENETIC_DISTANCE,
            genetic_distance_protocol_id=protocol_id,
        )
        cases = [
            SimpleNamespace(id=case_id, content={col_id: str(profile_id)}),
            SimpleNamespace(id=uuid4(), content={col_id: None}),
        ]
        case_abac = Mock()
        cmd = Mock()
        cmd.case_type_id = case_type_id
        cmd.genetic_distance_col_id = col_id
        cmd.case_ids = [case_id]
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.repository.crud.side_effect = [dist_col, ref_col, protocol]
        self.service._retrieve_cases_with_content_right.return_value = (cases, False)

        with patch.object(
            retrieve_seq.BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=case_abac,
        ):
            result = retrieve_seq._retrieve_case_profile_map(
                self.service, self.uow, cmd
            )

        assert result[0] is protocol
        assert result[1] == {case_id: profile_id}
        assert result[2] is dist_col
        self.service._retrieve_cases_with_content_right.assert_called_once_with(
            self.uow,
            self.user.id,
            case_abac,
            enum.CaseRight.READ_CASE,
            case_type_id,
            case_ids=[case_id],
            filter_content=True,
        )

    def test_retrieve_case_profile_map_returns_empty_for_empty_case_ids(self) -> None:
        case_type_id = uuid4()
        col_id = uuid4()
        protocol_id = uuid4()
        protocol = SimpleNamespace(id=protocol_id)
        dist_col = SimpleNamespace(case_type_id=case_type_id, ref_col_id=uuid4())
        ref_col = SimpleNamespace(
            col_type=enum.ColType.GENETIC_DISTANCE,
            genetic_distance_protocol_id=protocol_id,
        )
        cmd = Mock()
        cmd.case_type_id = case_type_id
        cmd.genetic_distance_col_id = col_id
        cmd.case_ids = []
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.repository.crud.side_effect = [dist_col, ref_col, protocol]

        result = retrieve_seq._retrieve_case_profile_map(self.service, self.uow, cmd)

        assert result[0] is protocol
        assert result[1] == {}
        assert result[2] is dist_col
        self.service._retrieve_cases_with_content_right.assert_not_called()

    def test_retrieve_case_profile_map_rejects_wrong_case_type(self) -> None:
        cmd = Mock()
        cmd.case_type_id = uuid4()
        cmd.genetic_distance_col_id = uuid4()
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.repository.crud.return_value = SimpleNamespace(
            case_type_id=uuid4()
        )

        with pytest.raises(exc.InvalidArgumentsError, match="does not belong"):
            retrieve_seq._retrieve_case_profile_map(self.service, self.uow, cmd)

        self.service.repository.crud.assert_called_once()

    def test_retrieve_case_profile_map_rejects_non_distance_column(self) -> None:
        cmd = Mock()
        cmd.case_type_id = uuid4()
        cmd.genetic_distance_col_id = uuid4()
        dist_col = SimpleNamespace(
            case_type_id=cmd.case_type_id,
            ref_col_id=uuid4(),
        )
        ref_col = SimpleNamespace(col_type=enum.ColType.TEXT)
        self.service._get_user_and_repository.return_value = (
            self.user,
            self.service.repository,
        )
        self.service.repository.crud.side_effect = [dist_col, ref_col]

        with pytest.raises(exc.InvalidArgumentsError, match="is not of type"):
            retrieve_seq._retrieve_case_profile_map(self.service, self.uow, cmd)

        assert self.service.repository.crud.call_count == 2
