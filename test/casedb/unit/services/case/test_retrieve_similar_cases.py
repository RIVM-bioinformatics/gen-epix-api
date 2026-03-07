from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, Mock, call
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_similar_cases import (
    case_service_retrieve_similar_cases,
)
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum


class BaseSimilarCasesTestCase(TestCase):
    """Base test case with common fixtures and utilities for similar cases."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Test user
        self.user: model.User = model.User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={"CASEDB_APP_ADMIN"},
            organization_id=uuid4(),
            is_active=True,
        )

        # IDs
        self.case_type_id: UUID = uuid4()
        self.dist_case_type_col_id: UUID = uuid4()
        self.ref_col_id: UUID = uuid4()
        self.ref_dim_id: UUID = uuid4()
        self.protocol_id: UUID = uuid4()
        self.data_collection_id: UUID = uuid4()

        # Mock service
        self.service: BaseCaseService = Mock(spec=BaseCaseService)
        self.repository = Mock()
        self.service.repository = self.repository

        # Mock UOW context manager using MagicMock to support context manager protocol
        self.uow = MagicMock()
        self.uow.__enter__.return_value = self.uow
        self.uow.__exit__.return_value = None
        self.repository.uow = MagicMock(return_value=self.uow)

        # Mock app for cross-service calls
        self.service.app = Mock(spec=App)
        self.service.app.handle.return_value = []

        # Private service methods used internally should be mocked
        self.service._get_user_and_repository = Mock(
            return_value=(self.user, self.repository)
        )
        self.service._retrieve_cases_with_content_right = Mock(return_value=[])

        # Patch ABAC policy resolution
        self._orig_get_case_abac = BaseCaseAbacPolicy.get_case_abac_from_command
        BaseCaseAbacPolicy.get_case_abac_from_command = Mock(  # type: ignore[method-assign]
            return_value=SimpleNamespace()
        )

    def tearDown(self) -> None:
        BaseCaseAbacPolicy.get_case_abac_from_command = self._orig_get_case_abac  # type: ignore[method-assign]

    # Helpers
    def create_command(
        self,
        case_ids: list[UUID],
        max_distance: float = 5.0,
    ) -> command.RetrieveSimilarCasesCommand:
        """Create a RetrieveSimilarCasesCommand for tests."""
        return command.RetrieveSimilarCasesCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            genetic_distance_case_type_col_id=self.dist_case_type_col_id,
            case_ids=case_ids,
            max_distance=max_distance,
        )

    def create_case_type_col(
        self, case_type_id: UUID | None = None
    ) -> model.CaseTypeCol:
        return model.CaseTypeCol(
            case_type_id=case_type_id or self.case_type_id,
            case_type_dim_id=uuid4(),
            ref_col_id=self.ref_col_id,
            code="Specimen.Genetic.Distance",
            rank=0,
        )

    def create_col(
        self,
        col_type: enum.ColType,
        genetic_distance_protocol_id: UUID | None = None,
    ) -> model.RefCol:
        return model.RefCol(
            ref_dim_id=self.ref_dim_id,
            code="Specimen.Genetic.Distance",
            col_type=col_type,
            genetic_distance_protocol_id=genetic_distance_protocol_id,
        )

    def create_protocol(self) -> model.GeneticDistanceProtocol:
        return model.GeneticDistanceProtocol(
            seqdb_seq_distance_protocol_id=self.protocol_id,
            seqdb_seq_distance_protocol_type=seqdb_enum.SeqDistanceProtocolType.KMER_EUCLIDEAN,
            name="KMER_EUCLIDEAN",
            seqdb_is_integer_distance=False,
            min_scale_unit=0.1,
        )

    def create_case(
        self,
        case_id: UUID,
        profile_id: UUID | None,
    ) -> model.Case:
        return model.Case(
            id=case_id,
            case_type_id=self.case_type_id,
            created_in_data_collection_id=self.data_collection_id,
            content={
                self.dist_case_type_col_id: (
                    None if profile_id is None else str(profile_id)
                )
            },
        )


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestInputValidation(BaseSimilarCasesTestCase):
    def test_empty_case_ids_raises_error(self) -> None:
        # 1. Input
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(case_ids=[])

        # 2. Mocks
        # (already configured in setUp)

        # 3. Execute
        profile_ids = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert profile_ids == []
        self.repository.crud.assert_not_called()
        self.service._retrieve_cases_with_content_right.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestBranchErrors(BaseSimilarCasesTestCase):
    def test_case_type_col_mismatch_raises(self) -> None:
        # 1. Input
        case_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[case_id]
        )

        # 2. Mocks
        dist_case_type_col: model.CaseTypeCol = self.create_case_type_col(
            case_type_id=uuid4()
        )
        self.repository.crud.side_effect = [dist_case_type_col]

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError) as err:
            case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert "does not belong to case type" in str(err.value)
        self.repository.crud.assert_called_once()
        assert self.repository.crud.call_args == call(
            self.uow,
            self.user.id,
            model.CaseTypeCol,
            None,
            self.dist_case_type_col_id,
            CrudOperation.READ_ONE,
        )
        self.service._retrieve_cases_with_content_right.assert_not_called()  # type: ignore[attr-defined]

    def test_col_type_not_genetic_distance_raises(self) -> None:
        # 1. Input
        case_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[case_id]
        )

        # 2. Mocks
        dist_case_type_col: model.CaseTypeCol = self.create_case_type_col(
            case_type_id=self.case_type_id
        )
        wrong_col: model.RefCol = self.create_col(col_type=enum.ColType.TEXT)
        self.repository.crud.side_effect = [
            dist_case_type_col,
            wrong_col,
        ]

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError) as err:
            case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert enum.ColType.GENETIC_DISTANCE.value in str(err.value)
        assert self.repository.crud.mock_calls[:2] == [
            call(
                self.uow,
                self.user.id,
                model.CaseTypeCol,
                None,
                self.dist_case_type_col_id,
                CrudOperation.READ_ONE,
            ),
            call(
                self.uow,
                self.user.id,
                model.RefCol,
                None,
                dist_case_type_col.ref_col_id,
                CrudOperation.READ_ONE,
            ),
        ]
        assert self.repository.crud.call_count == 2
        self.service._retrieve_cases_with_content_right.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestHappyPath(BaseSimilarCasesTestCase):
    def test_returns_similar_case_ids(self) -> None:
        # 1. Input
        seed_case_id1: UUID = uuid4()
        seed_case_id2: UUID = uuid4()
        other_case_id: UUID = uuid4()
        seed_profile_id1: UUID = uuid4()
        seed_profile_id2: UUID = uuid4()
        other_profile_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id1, seed_case_id2], max_distance=7.5
        )

        # 2. Mocks
        dist_case_type_col: model.CaseTypeCol = self.create_case_type_col(
            case_type_id=self.case_type_id
        )
        dist_col: model.RefCol = self.create_col(
            col_type=enum.ColType.GENETIC_DISTANCE,
            genetic_distance_protocol_id=self.protocol_id,
        )
        protocol: model.GeneticDistanceProtocol = self.create_protocol()
        self.repository.crud.side_effect = [dist_case_type_col, dist_col, protocol]

        all_cases: list[model.Case] = [
            self.create_case(seed_case_id1, seed_profile_id1),
            self.create_case(seed_case_id2, seed_profile_id2),
            self.create_case(other_case_id, other_profile_id),
            self.create_case(uuid4(), None),  # No profile for this case
        ]
        self.service._retrieve_cases_with_content_right.return_value = all_cases  # type: ignore[attr-defined]

        # Cross-service call returns a similar profile (as string) to include
        self.service.app.handle.return_value = [str(other_profile_id)]  # type: ignore[attr-defined]

        # 3. Execute
        result: list[UUID] = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        # Result must exclude the two seeds and the other case
        assert set(result) == {other_case_id}

        # Verify repository interactions
        assert self.repository.crud.mock_calls == [
            call(
                self.uow,
                self.user.id,
                model.CaseTypeCol,
                None,
                self.dist_case_type_col_id,
                CrudOperation.READ_ONE,
            ),
            call(
                self.uow,
                self.user.id,
                model.RefCol,
                None,
                dist_case_type_col.ref_col_id,
                CrudOperation.READ_ONE,
            ),
            call(
                self.uow,
                self.user.id,
                model.GeneticDistanceProtocol,
                None,
                dist_col.genetic_distance_protocol_id,
                CrudOperation.READ_ONE,
            ),
        ]

        # Verify _retrieve_cases_with_content_right called with correct args
        self.service._retrieve_cases_with_content_right.assert_called_once()  # type: ignore[attr-defined]

        # Verify cross-service command construction and call
        self.service.app.handle.assert_called_once()  # type: ignore[attr-defined]
        seq_cmd = self.service.app.handle.call_args[0][0]  # type: ignore[attr-defined]
        assert (
            seq_cmd.seq_distance_protocol_id == protocol.seqdb_seq_distance_protocol_id
        )
        assert set(seq_cmd.profile_ids) == {seed_profile_id1, seed_profile_id2}
        assert seq_cmd.max_distance == 7.5

    def test_no_profile_ids_extracted_returns_empty(self) -> None:
        # 1. Input
        seed_case_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        dist_case_type_col: model.CaseTypeCol = self.create_case_type_col(
            case_type_id=self.case_type_id
        )
        dist_col: model.RefCol = self.create_col(
            col_type=enum.ColType.GENETIC_DISTANCE,
            genetic_distance_protocol_id=self.protocol_id,
        )
        protocol: model.GeneticDistanceProtocol = self.create_protocol()
        self.repository.crud.side_effect = [dist_case_type_col, dist_col, protocol]

        # Seed case does not have a profile ID in content
        all_cases: list[model.Case] = [self.create_case(seed_case_id, None)]
        self.service._retrieve_cases_with_content_right.return_value = all_cases  # type: ignore[attr-defined]

        # 3. Execute
        result: list[UUID] = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert result == []
        self.service.app.handle.assert_called_once()  # type: ignore[attr-defined]
        seq_cmd = self.service.app.handle.call_args[0][0]  # type: ignore[attr-defined]
        assert seq_cmd.profile_ids == []
