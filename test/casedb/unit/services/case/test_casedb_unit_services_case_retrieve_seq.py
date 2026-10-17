from test.casedb.unit.services.case.base import BaseCrudTestCase
from test.util.mock_compat import Mock, patch
from uuid import uuid4

import pytest

import gen_epix.casedb.services.case.retrieve_seq as retrieve_seq
from gen_epix.casedb.domain import exc


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
