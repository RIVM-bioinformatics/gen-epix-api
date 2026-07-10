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
from gen_epix.seqdb.domain import command as seqdb_command
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
        self.dist_col_id: UUID = uuid4()
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
        self.service._retrieve_case_data_collections_map = Mock(return_value={})

        # Patch ABAC policy resolution; default: no private data collections
        self._orig_get_case_abac = BaseCaseAbacPolicy.get_case_abac_from_command
        BaseCaseAbacPolicy.get_case_abac_from_command = Mock(  # type: ignore[method-assign]
            return_value=SimpleNamespace(case_type_access_abacs={})
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
            genetic_distance_col_id=self.dist_col_id,
            case_ids=case_ids,
            max_distance=max_distance,
        )

    def create_col(self, case_type_id: UUID | None = None) -> model.Col:
        return model.Col(
            case_type_id=case_type_id or self.case_type_id,
            dim_id=uuid4(),
            ref_col_id=self.ref_col_id,
            code="Specimen.Genetic.Distance",
            rank=0,
        )

    def create_ref_col(
        self,
        col_type: enum.ColType,
        protocol_id: UUID | None = None,
    ) -> model.RefCol:
        return model.RefCol(
            ref_dim_id=self.ref_dim_id,
            code="Specimen.Genetic.Distance",
            col_type=col_type,
            genetic_distance_protocol_id=protocol_id,
        )

    def create_protocol(self) -> model.GeneticDistanceProtocol:
        return model.GeneticDistanceProtocol(
            seqdb_seq_distance_protocol_id=self.protocol_id,
            seqdb_seq_distance_type=seqdb_enum.SeqDistanceType.ALLELE_HAMMING,
            name="KMER_EUCLIDEAN",
            seqdb_is_integer_distance=False,
            min_scale_unit=0.1,
        )

    def create_case(
        self,
        case_id: UUID,
        profile_id: UUID | None,
        data_collection_id: UUID | None = None,
    ) -> model.Case:
        return model.Case(
            id=case_id,
            case_type_id=self.case_type_id,
            created_in_data_collection_id=(
                data_collection_id
                if data_collection_id is not None
                else self.data_collection_id
            ),
            content={
                self.dist_col_id: (None if profile_id is None else str(profile_id))
            },
        )

    def create_access_abac(
        self,
        data_collection_id: UUID,
        is_private: bool,
    ) -> model.CaseTypeAccessAbac:
        """Create a minimal CaseTypeAccessAbac for use in tests."""
        return model.CaseTypeAccessAbac(
            case_type_id=self.case_type_id,
            data_collection_id=data_collection_id,
            is_private=is_private,
            add_case=False,
            remove_case=False,
            add_case_set=False,
            remove_case_set=False,
            read_col_ids=set(),
            write_col_ids=set(),
            read_case_set=False,
            write_case_set=False,
        )


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestInputValidation(BaseSimilarCasesTestCase):
    def test_empty_case_ids_raises_error(self) -> None:
        # 1. Input
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(case_ids=[])

        # 2. Mocks
        # (already configured in setUp)

        # 3. Execute
        similar_cases = case_service_retrieve_similar_cases(self.service, cmd)
        similar_case_ids = [x.id for x in similar_cases.cases]

        # 4. Verify
        assert similar_case_ids == []
        self.repository.crud.assert_not_called()
        self.service._retrieve_cases_with_content_right.assert_not_called()  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestBranchErrors(BaseSimilarCasesTestCase):
    def test_col_mismatch_raises(self) -> None:
        # 1. Input
        case_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[case_id]
        )

        # 2. Mocks
        dist_col: model.Col = self.create_col(case_type_id=uuid4())
        self.repository.crud.side_effect = [dist_col]

        # 3. Execute
        with pytest.raises(exc.InvalidArgumentsError) as err:
            case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert "does not belong to CaseType" in str(err.value)
        self.repository.crud.assert_called_once()
        assert self.repository.crud.call_args == call(
            self.uow,
            self.user.id,
            model.Col,
            CrudOperation.READ_ONE,
            obj_ids=self.dist_col_id,
        )
        self.service._retrieve_cases_with_content_right.assert_not_called()  # type: ignore[attr-defined]

    def test_col_type_not_genetic_distance_raises(self) -> None:
        # 1. Input
        case_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[case_id]
        )

        # 2. Mocks
        dist_col: model.Col = self.create_col(case_type_id=self.case_type_id)
        wrong_col: model.RefCol = self.create_ref_col(col_type=enum.ColType.TEXT)
        self.repository.crud.side_effect = [
            dist_col,
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
                model.Col,
                CrudOperation.READ_ONE,
                obj_ids=self.dist_col_id,
            ),
            call(
                self.uow,
                self.user.id,
                model.RefCol,
                CrudOperation.READ_ONE,
                obj_ids=dist_col.ref_col_id,
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
        dist_col: model.Col = self.create_col(case_type_id=self.case_type_id)
        dist_ref_col: model.RefCol = self.create_ref_col(
            col_type=enum.ColType.GENETIC_DISTANCE,
            protocol_id=self.protocol_id,
        )
        protocol: model.GeneticDistanceProtocol = self.create_protocol()
        self.repository.crud.side_effect = [dist_col, dist_ref_col, protocol]

        all_cases: list[model.Case] = [
            self.create_case(seed_case_id1, seed_profile_id1),
            self.create_case(seed_case_id2, seed_profile_id2),
            self.create_case(other_case_id, other_profile_id),
            self.create_case(uuid4(), None),  # No profile for this case
        ]
        similar_cases_with_dates: list[model.Case] = [
            self.create_case(other_case_id, other_profile_id)
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases_with_dates,
        ]

        # Cross-service call returns a similar profile (as string) to include
        self.service.app.handle.return_value = [str(other_profile_id)]  # type: ignore[attr-defined]

        # 3. Execute
        similar_cases = case_service_retrieve_similar_cases(self.service, cmd)
        similar_case_ids = [x.id for x in similar_cases.cases]

        # 4. Verify
        # Result must exclude the two seeds and the other case
        assert set(similar_case_ids) == {other_case_id}

        # Verify repository interactions
        assert self.repository.crud.mock_calls == [
            call(
                self.uow,
                self.user.id,
                model.Col,
                CrudOperation.READ_ONE,
                obj_ids=self.dist_col_id,
            ),
            call(
                self.uow,
                self.user.id,
                model.RefCol,
                CrudOperation.READ_ONE,
                obj_ids=dist_col.ref_col_id,
            ),
            call(
                self.uow,
                self.user.id,
                model.GeneticDistanceProtocol,
                CrudOperation.READ_ONE,
                obj_ids=dist_ref_col.genetic_distance_protocol_id,
            ),
        ]

        # Verify _retrieve_cases_with_content_right called twice with expected
        # filtering behavior.
        assert self.service._retrieve_cases_with_content_right.call_count == 2  # type: ignore[attr-defined]
        first_call = self.service._retrieve_cases_with_content_right.mock_calls[0]  # type: ignore[attr-defined]
        second_call = self.service._retrieve_cases_with_content_right.mock_calls[1]  # type: ignore[attr-defined]
        assert first_call.kwargs["case_ids"] is None
        assert first_call.kwargs["calculate_case_date"] is False
        assert second_call.kwargs["case_ids"] == [other_case_id]
        assert second_call.kwargs["calculate_case_date"] is True

        # Verify cross-service command construction and call
        self.service.app.handle.assert_called_once()  # type: ignore[attr-defined]
        seq_cmd: seqdb_command.RetrieveSimilarProfilesCommand = self.service.app.handle.call_args[0][0]  # type: ignore[attr-defined]
        assert seq_cmd.protocol_id == protocol.seqdb_seq_distance_protocol_id
        assert set(seq_cmd.profile_ids) == {seed_profile_id1, seed_profile_id2}
        assert seq_cmd.max_distance == 7.5

    def test_no_profile_ids_extracted_returns_empty(self) -> None:
        # 1. Input
        seed_case_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        dist_col: model.Col = self.create_col(case_type_id=self.case_type_id)
        dist_ref_col: model.RefCol = self.create_ref_col(
            col_type=enum.ColType.GENETIC_DISTANCE,
            protocol_id=self.protocol_id,
        )
        protocol: model.GeneticDistanceProtocol = self.create_protocol()
        self.repository.crud.side_effect = [dist_col, dist_ref_col, protocol]

        # Seed case does not have a profile ID in content
        all_cases: list[model.Case] = [self.create_case(seed_case_id, None)]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            [],
        ]

        # 3. Execute
        similar_cases = case_service_retrieve_similar_cases(self.service, cmd)
        similar_case_ids = [x.id for x in similar_cases.cases]

        # 4. Verify
        assert similar_case_ids == []
        self.service.app.handle.assert_called_once()  # type: ignore[attr-defined]
        seq_cmd: seqdb_command.RetrieveSimilarProfilesCommand = self.service.app.handle.call_args[0][0]  # type: ignore[attr-defined]
        assert seq_cmd.profile_ids == []


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestOwnCases(BaseSimilarCasesTestCase):
    """Tests for the is_own_case classification of similar cases."""

    def _setup_standard_path(
        self,
        seed_case_id: UUID,
        similar_case_id: UUID,
        seed_profile_id: UUID,
        similar_profile_id: UUID,
    ) -> None:
        """Set up the standard CRUD and retrieval mocks for a single seed +
        single similar-case scenario."""
        dist_col = self.create_col()
        dist_ref_col = self.create_ref_col(
            col_type=enum.ColType.GENETIC_DISTANCE,
            protocol_id=self.protocol_id,
        )
        protocol = self.create_protocol()
        self.repository.crud.side_effect = [dist_col, dist_ref_col, protocol]
        self.service.app.handle.return_value = [str(similar_profile_id)]  # type: ignore[attr-defined]
        self._dist_col = dist_col

    def test_created_in_private_collection_is_own_case(self) -> None:
        # 1. Input
        seed_case_id: UUID = uuid4()
        similar_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        similar_profile_id: UUID = uuid4()
        private_dc_id: UUID = uuid4()
        public_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        private_dc_id: self.create_access_abac(
                            private_dc_id, is_private=True
                        )
                    }
                }
            )
        )
        self._setup_standard_path(
            seed_case_id, similar_case_id, seed_profile_id, similar_profile_id
        )
        all_cases: list[model.Case] = [
            self.create_case(seed_case_id, seed_profile_id),
            # Similar case created in private DC; map has only public DC entry
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=private_dc_id
            ),
        ]
        similar_cases: list[model.Case] = [
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=private_dc_id
            )
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        self.service._retrieve_case_data_collections_map.return_value = {  # type: ignore[attr-defined]
            similar_case_id: {public_dc_id}
        }

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 1
        assert result.cases[0].id == similar_case_id
        assert result.cases[0].is_own_case is True

    def test_mapped_private_collection_is_own_case(self) -> None:
        # 1. Input
        seed_case_id: UUID = uuid4()
        similar_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        similar_profile_id: UUID = uuid4()
        private_dc_id: UUID = uuid4()
        public_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks — similar case was created in a public DC, but is shared
        # into a private DC that the user can see via the collections map.
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        private_dc_id: self.create_access_abac(
                            private_dc_id, is_private=True
                        )
                    }
                }
            )
        )
        self._setup_standard_path(
            seed_case_id, similar_case_id, seed_profile_id, similar_profile_id
        )
        all_cases = [
            self.create_case(seed_case_id, seed_profile_id),
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=public_dc_id
            ),
        ]
        similar_cases = [
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=public_dc_id
            )
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        self.service._retrieve_case_data_collections_map.return_value = {  # type: ignore[attr-defined]
            similar_case_id: {private_dc_id}
        }

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 1
        assert result.cases[0].id == similar_case_id
        assert result.cases[0].is_own_case is True

    def test_case_in_public_collection_only_is_not_own_case(self) -> None:
        # 1. Input — private DC exists but the case only lives in public DC.
        seed_case_id: UUID = uuid4()
        similar_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        similar_profile_id: UUID = uuid4()
        private_dc_id: UUID = uuid4()
        public_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        private_dc_id: self.create_access_abac(
                            private_dc_id, is_private=True
                        ),
                        public_dc_id: self.create_access_abac(
                            public_dc_id, is_private=False
                        ),
                    }
                }
            )
        )
        self._setup_standard_path(
            seed_case_id, similar_case_id, seed_profile_id, similar_profile_id
        )
        all_cases = [
            self.create_case(seed_case_id, seed_profile_id),
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=public_dc_id
            ),
        ]
        similar_cases = [
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=public_dc_id
            )
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        self.service._retrieve_case_data_collections_map.return_value = {  # type: ignore[attr-defined]
            similar_case_id: {public_dc_id}
        }

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 1
        assert result.cases[0].id == similar_case_id
        assert result.cases[0].is_own_case is False

    def test_case_with_no_matching_collection_is_not_own_case(self) -> None:
        # 1. Input — map returns no entry for the case; created_in is not private.
        seed_case_id: UUID = uuid4()
        similar_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        similar_profile_id: UUID = uuid4()
        private_dc_id: UUID = uuid4()
        unrelated_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        private_dc_id: self.create_access_abac(
                            private_dc_id, is_private=True
                        )
                    }
                }
            )
        )
        self._setup_standard_path(
            seed_case_id, similar_case_id, seed_profile_id, similar_profile_id
        )
        all_cases = [
            self.create_case(seed_case_id, seed_profile_id),
            self.create_case(
                similar_case_id,
                similar_profile_id,
                data_collection_id=unrelated_dc_id,
            ),
        ]
        similar_cases = [
            self.create_case(
                similar_case_id,
                similar_profile_id,
                data_collection_id=unrelated_dc_id,
            )
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        # Map has no entry for this case at all
        self.service._retrieve_case_data_collections_map.return_value = {}  # type: ignore[attr-defined]

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 1
        assert result.cases[0].id == similar_case_id
        assert result.cases[0].is_own_case is False

    def test_subset_of_similar_cases_are_own_cases(self) -> None:
        # 1. Input — two similar cases; only one belongs to a private DC.
        seed_case_id: UUID = uuid4()
        own_case_id: UUID = uuid4()
        not_own_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        own_profile_id: UUID = uuid4()
        not_own_profile_id: UUID = uuid4()
        private_dc_id: UUID = uuid4()
        public_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        private_dc_id: self.create_access_abac(
                            private_dc_id, is_private=True
                        )
                    }
                }
            )
        )
        dist_col = self.create_col()
        dist_ref_col = self.create_ref_col(
            col_type=enum.ColType.GENETIC_DISTANCE,
            protocol_id=self.protocol_id,
        )
        protocol = self.create_protocol()
        self.repository.crud.side_effect = [dist_col, dist_ref_col, protocol]
        self.service.app.handle.return_value = [  # type: ignore[attr-defined]
            str(own_profile_id),
            str(not_own_profile_id),
        ]
        all_cases = [
            self.create_case(seed_case_id, seed_profile_id),
            self.create_case(
                own_case_id, own_profile_id, data_collection_id=private_dc_id
            ),
            self.create_case(
                not_own_case_id, not_own_profile_id, data_collection_id=public_dc_id
            ),
        ]
        similar_cases = [
            self.create_case(
                own_case_id, own_profile_id, data_collection_id=private_dc_id
            ),
            self.create_case(
                not_own_case_id, not_own_profile_id, data_collection_id=public_dc_id
            ),
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        self.service._retrieve_case_data_collections_map.return_value = {}  # type: ignore[attr-defined]

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 2
        own_ids = {c.id for c in result.cases if c.is_own_case}
        not_own_ids = {c.id for c in result.cases if not c.is_own_case}
        assert own_ids == {own_case_id}
        assert not_own_ids == {not_own_case_id}

    def test_case_matching_both_paths_is_own_case(self) -> None:
        # 1. Input — created_in AND the collections map both point to the same
        # private DC. The set union must not crash and the case is an own case.
        seed_case_id: UUID = uuid4()
        similar_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        similar_profile_id: UUID = uuid4()
        private_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        private_dc_id: self.create_access_abac(
                            private_dc_id, is_private=True
                        )
                    }
                }
            )
        )
        self._setup_standard_path(
            seed_case_id, similar_case_id, seed_profile_id, similar_profile_id
        )
        all_cases = [
            self.create_case(seed_case_id, seed_profile_id),
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=private_dc_id
            ),
        ]
        similar_cases = [
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=private_dc_id
            )
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        # Map also returns the same private DC for the case
        self.service._retrieve_case_data_collections_map.return_value = {  # type: ignore[attr-defined]
            similar_case_id: {private_dc_id}
        }

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 1
        assert result.cases[0].id == similar_case_id
        assert result.cases[0].is_own_case is True

    def test_empty_map_uses_created_in_data_collection(self) -> None:
        # 1. Input — map returns {} entirely; is_own_case depends solely on
        # created_in_data_collection_id.
        seed_case_id: UUID = uuid4()
        similar_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        similar_profile_id: UUID = uuid4()
        private_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        private_dc_id: self.create_access_abac(
                            private_dc_id, is_private=True
                        )
                    }
                }
            )
        )
        self._setup_standard_path(
            seed_case_id, similar_case_id, seed_profile_id, similar_profile_id
        )
        all_cases = [
            self.create_case(seed_case_id, seed_profile_id),
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=private_dc_id
            ),
        ]
        similar_cases = [
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=private_dc_id
            )
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        # Empty map: get(x.id, set()) must default to set()
        self.service._retrieve_case_data_collections_map.return_value = {}  # type: ignore[attr-defined]

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 1
        assert result.cases[0].id == similar_case_id
        assert result.cases[0].is_own_case is True

    def test_no_private_collections_means_no_own_cases(self) -> None:
        # 1. Input — user has no private data collections; no case should be
        # classified as an own case regardless of its data collections.
        seed_case_id: UUID = uuid4()
        similar_case_id: UUID = uuid4()
        seed_profile_id: UUID = uuid4()
        similar_profile_id: UUID = uuid4()
        any_dc_id: UUID = uuid4()
        cmd: command.RetrieveSimilarCasesCommand = self.create_command(
            case_ids=[seed_case_id]
        )

        # 2. Mocks — all data collections are public (is_private=False)
        BaseCaseAbacPolicy.get_case_abac_from_command.return_value = (  # type: ignore[attr-defined]
            SimpleNamespace(
                case_type_access_abacs={
                    self.case_type_id: {
                        any_dc_id: self.create_access_abac(any_dc_id, is_private=False)
                    }
                }
            )
        )
        self._setup_standard_path(
            seed_case_id, similar_case_id, seed_profile_id, similar_profile_id
        )
        all_cases = [
            self.create_case(seed_case_id, seed_profile_id),
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=any_dc_id
            ),
        ]
        similar_cases = [
            self.create_case(
                similar_case_id, similar_profile_id, data_collection_id=any_dc_id
            )
        ]
        self.service._retrieve_cases_with_content_right.side_effect = [  # type: ignore[attr-defined]
            all_cases,
            similar_cases,
        ]
        self.service._retrieve_case_data_collections_map.return_value = {  # type: ignore[attr-defined]
            similar_case_id: {any_dc_id}
        }

        # 3. Execute
        result = case_service_retrieve_similar_cases(self.service, cmd)

        # 4. Verify
        assert len(result.cases) == 1
        assert result.cases[0].id == similar_case_id
        assert result.cases[0].is_own_case is False
