import json
from collections.abc import Callable, Iterator
from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import EtlStatus, Role
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.services.seq.calculate_seq_distance import (
    seq_service_calculate_seq_distances_for_new_profiles,
)


def _mock_uow() -> Mock:
    uow: Mock = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


def _make_user() -> User:
    return User(
        id=uuid4(),
        key="test@example.com",
        email="test@example.com",
        roles={Role.APP_ADMIN.value},
        organization_id=uuid4(),
        is_active=True,
    )


def _make_seq_distance_protocol_for_snp(
    *,
    protocol_id: UUID,
    ref_seq_id: UUID,
    max_stored_distance: float = 100.0,
) -> model.Protocol:
    return model.Protocol(  # type: ignore[call-arg]
        id=protocol_id,
        code="SNP_HAMMING_TEST",
        name="SNP Hamming Test",
        is_integer_distance=True,
        protocol_type=enum.ProtocolType.SEQ_DISTANCE,
        seq_distance_type=enum.SeqDistanceType.SNP_HAMMING,
        ref_seq_id=ref_seq_id,
        locus_set_id=None,
        max_stored_distance=max_stored_distance,
        props={"version": "1.0"},
    )


def _make_seq_distance_protocol_for_locus_set(
    *,
    protocol_id: UUID,
    locus_set_id: UUID,
    seq_distance_protocol_type: enum.SeqDistanceType,
    max_stored_distance: float = 100.0,
) -> model.Protocol:
    return model.Protocol(  # type: ignore[call-arg]
        id=protocol_id,
        code="LOCUS_HAMMING_TEST",
        name="Locus Hamming Test",
        is_integer_distance=True,
        protocol_type=enum.ProtocolType.SEQ_DISTANCE,
        seq_distance_type=seq_distance_protocol_type,
        locus_set_id=locus_set_id,
        ref_seq_id=None,
        max_stored_distance=max_stored_distance,
        props={"version": "1.0"},
    )


def _make_seq_distance(
    *,
    seq_distance_id: UUID,
    protocol_id: UUID,
    profile_id: UUID,
    sample_id: UUID,
    distances: dict[str, float] | None = None,
) -> model.SeqDistance:
    return model.SeqDistance(  # type: ignore[call-arg]
        id=seq_distance_id,
        sample_id=sample_id,
        protocol_id=protocol_id,
        seq_profile_id=profile_id,
        format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content=json.dumps(distances or {}),
    )


def _make_snp_profile_for_upload(
    *,
    profile_id: UUID,
    sample_id: UUID,
    ref_seq_id: UUID,
    protocol_id: UUID,
    snp_profile: str = "AAA",
    aligned_nucleotide_seq: str | None = None,
) -> model.SeqProfile:
    # New unified SeqProfile uses `content`, `format` and `seq_profile_type`.
    # Use model_construct to avoid invoking full validators (minimal test change).
    content_value = (
        aligned_nucleotide_seq if aligned_nucleotide_seq is not None else snp_profile
    )
    return model.SeqProfile.model_construct(
        id=profile_id,
        sample_id=sample_id,
        seq_id=None,
        ref_seq_id=ref_seq_id,
        protocol_id=protocol_id,
        content=content_value,
        format=enum.SeqProfileFormat.REF_ALN_SEQ,
        content_hash=uuid4(),
        seq_profile_type=enum.SeqProfileType.SNP,
        qc_score=1.0,
        qc_result=enum.QualityControlResult.PASS,
    )


def _make_allele_profile(
    *,
    profile_id: UUID | None,
    sample_id: UUID,
    locus_set_id: UUID,
    protocol_id: UUID,
    allele_ids: list[UUID | None],
) -> model.SeqProfile:
    allele_profile: str = model.SeqProfile.get_ordered_allele_ids_representation(
        allele_ids
    )
    allele_profile_hash: UUID = model.SeqProfile.get_allele_profile_hash(allele_ids)
    n_loci: int = len(allele_ids)
    # Unified fields: use `content`, `format`, `content_hash`, and `seq_profile_type`.
    return model.SeqProfile.model_construct(
        id=profile_id,
        sample_id=sample_id,
        seq_id=None,
        locus_set_id=locus_set_id,
        protocol_id=protocol_id,
        content=allele_profile,
        format=enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
        content_hash=allele_profile_hash,
        n_loci=n_loci,
        seq_profile_type=enum.SeqProfileType.ALLELE,
        qc_score=1.0,
        qc_result=enum.QualityControlResult.PASS,
    )


def _make_mlva_profile(
    *,
    profile_id: UUID,
    sample_id: UUID,
    locus_set_id: UUID,
    protocol_id: UUID,
    repeat_numbers: list[int | None],
    profile_format: enum.SeqProfileFormat = enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
) -> model.SeqProfile:
    mlva_profile: str = model.SeqProfile.get_ordered_repeat_numbers_representation(
        repeat_numbers
    )
    repeat_numbers_int: list[int | None] = repeat_numbers
    mlva_profile_hash: UUID = model.SeqProfile.get_mlva_profile_hash(repeat_numbers_int)
    # Use unified `content`, `format`, and `seq_profile_type` fields.
    return model.SeqProfile.model_construct(
        id=profile_id,
        sample_id=sample_id,
        seq_id=None,
        protocol_id=protocol_id,
        locus_set_id=locus_set_id,
        content=mlva_profile,
        format=profile_format,
        content_hash=mlva_profile_hash,
        seq_profile_type=enum.SeqProfileType.MLVA,
        qc_score=1.0,
        qc_result=enum.QualityControlResult.PASS,
    )


def _iterable(items: list[model.SeqDistance]) -> Iterator[model.SeqDistance]:
    for item in items:
        yield item


class _CrudRecorder:
    def __init__(self) -> None:
        self.created: list[model.SeqDistance] = []
        self.updated: list[model.SeqDistance] = []
        self.read_some_calls: list[list[UUID]] = []


def _make_crud_side_effect(
    *,
    recorder: _CrudRecorder,
    protocols: list[model.Protocol],
    existing_profiles_by_model: dict[type, list[model.Model]] | None = None,
) -> Callable[..., Any]:
    existing_profiles_by_model = existing_profiles_by_model or {}

    def _crud(
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        model_class: type,
        obj: Any,
        obj_ids: Any,
        operation: CrudOperation,
        *_: Any,
        **__: Any,
    ) -> Any:
        if model_class is model.Protocol and operation == CrudOperation.READ_ALL:
            return protocols
        if operation == CrudOperation.READ_SOME:
            assert isinstance(obj_ids, list)
            recorder.read_some_calls.append(obj_ids)
            return existing_profiles_by_model.get(model_class, [])
        if model_class is model.SeqDistance and operation == CrudOperation.UPDATE_ONE:
            assert isinstance(obj, model.SeqDistance)
            recorder.updated.append(obj)
            return obj
        if model_class is model.SeqDistance and operation == CrudOperation.UPDATE_SOME:
            assert isinstance(obj, list)
            for item in obj:
                assert isinstance(item, model.SeqDistance)
            recorder.updated.extend(obj)
            return obj
        if model_class is model.SeqDistance and operation == CrudOperation.CREATE_ONE:
            assert isinstance(obj, model.SeqDistance)
            recorder.created.append(obj)
            return obj
        if model_class is model.SeqDistance and operation == CrudOperation.CREATE_SOME:
            assert isinstance(obj, list)
            for item in obj:
                assert isinstance(item, model.SeqDistance)
            recorder.created.extend(obj)
            return obj
        return []

    return _crud


class BaseCalculateSeqDistanceTestCase(TestCase):
    """Base test case with common fixtures and utilities."""

    def setUp(self) -> None:
        self.user: User = _make_user()

        self.protocol_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.ref_seq_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.other_ref_seq_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.locus_set_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.sample_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440005")
        self.sample_id2: UUID = UUID("550e8400-e29b-41d4-a716-446655440006")

        self.existing_profile_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440010")
        self.new_profile_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440011")

        self.snp_detection_protocol_id: UUID = UUID(
            "550e8400-e29b-41d4-a716-446655440020"
        )
        self.locus_detection_protocol_id: UUID = UUID(
            "550e8400-e29b-41d4-a716-446655440021"
        )
        self.mlva_detection_protocol_id: UUID = UUID(
            "550e8400-e29b-41d4-a716-446655440022"
        )

        self.service: Mock = Mock()
        self.service.generate_id = Mock(side_effect=uuid4)
        self.service.repository = Mock()

        self.uow: Mock = _mock_uow()
        self.service.repository.uow.return_value = self.uow


@pytest.mark.scenario_ids("TC-11-13-01")
class TestCalculateSeqDistancesForNewProfiles(BaseCalculateSeqDistanceTestCase):
    def test_no_profiles_returns_empty_and_only_reads_protocols(self) -> None:
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user, seq_profiles=None
            )
        )

        recorder: _CrudRecorder = _CrudRecorder()
        protocols: list[model.Protocol] = [
            _make_seq_distance_protocol_for_snp(
                protocol_id=self.protocol_id,
                ref_seq_id=self.ref_seq_id,
                max_stored_distance=10.0,
            )
        ]
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=protocols,
        )
        self.service.repository.iter_seq_distances = Mock(return_value=_iterable([]))

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(results, [])
        self.service.repository.uow.assert_called_once()
        self.service.repository.iter_seq_distances.assert_not_called()
        self.assertEqual(len(recorder.created), 0)
        self.assertEqual(len(recorder.updated), 0)

    def test_kmer_profiles_raises_not_implemented(self) -> None:
        kmer_profile = model.SeqProfile(
            id=uuid4(),
            sample_id=self.sample_id,
            seq_id=None,
            protocol_id=uuid4(),
            kmer_profile="{}",
            kmer_profile_format=enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
            kmer_profile_hash=uuid4(),
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                kmer_profiles=[kmer_profile],
            )
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[],
        )

        with self.assertRaises(NotImplementedError):
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

    def test_protocol_not_applicable_skips_distance_calculation(self) -> None:
        snp_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id,
            ref_seq_id=self.other_ref_seq_id,
            protocol_id=self.protocol_id,
            snp_profile="AAAA",
            aligned_nucleotide_seq=None,
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                snp_profiles=[snp_profile],
            )
        )

        recorder: _CrudRecorder = _CrudRecorder()
        protocols: list[model.Protocol] = [
            _make_seq_distance_protocol_for_snp(
                protocol_id=self.protocol_id,
                ref_seq_id=self.ref_seq_id,
                max_stored_distance=10.0,
            )
        ]
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=protocols,
        )
        self.service.repository.iter_seq_distances = Mock(return_value=_iterable([]))

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(results, [])
        self.service.repository.iter_seq_distances.assert_not_called()
        self.assertEqual(len(recorder.created), 0)
        self.assertEqual(len(recorder.updated), 0)

    def test_snp_profiles_updates_existing_and_creates_new_seq_distances(self) -> None:
        existing_aln: str | None = "AACCT"
        new_aln: str | None = "AATTT"
        existing_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.protocol_id,
            snp_profile="AACCT",
        )
        new_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.protocol_id,
            snp_profile="AATTT",
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                snp_profiles=[new_profile],
            )
        )

        protocol: model.Protocol = _make_seq_distance_protocol_for_snp(
            protocol_id=self.protocol_id,
            ref_seq_id=self.ref_seq_id,
            max_stored_distance=100.0,
        )
        existing_seq_distance: model.SeqDistance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: [existing_profile]},
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable([existing_seq_distance])
        )

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[1].seq_distance_profile_id, self.new_profile_id)
        self.assertEqual(results[0].status, EtlStatus.UPDATED)
        self.assertEqual(results[1].status, EtlStatus.CREATED)

        self.assertEqual(len(recorder.updated), 1)
        updated_distances: dict[str, float] = json.loads(recorder.updated[0].content)
        self.assertIn(str(self.new_profile_id), updated_distances)

        self.assertEqual(len(recorder.created), 1)
        created: model.SeqDistance = recorder.created[0]
        self.assertEqual(created.protocol_id, self.protocol_id)
        self.assertEqual(created.seq_profile_id, self.new_profile_id)
        self.assertEqual(created.sample_id, self.sample_id2)
        created_map: dict[str, float] = json.loads(created.content)
        self.assertIn(str(self.existing_profile_id), created_map)

        existing_seq: str = existing_aln if existing_aln is not None else "AACCT"
        new_seq: str = new_aln if new_aln is not None else "AATTT"
        min_len: int = min(len(existing_seq), len(new_seq))
        expected_distance: int = sum(
            1 for i in range(min_len) if existing_seq[i] != new_seq[i]
        ) + abs(len(existing_seq) - len(new_seq))

        self.assertEqual(updated_distances[str(self.new_profile_id)], expected_distance)
        self.assertEqual(created_map[str(self.existing_profile_id)], expected_distance)

    def test_allele_profiles_distance_over_threshold_creates_new_with_empty_map(
        self,
    ) -> None:
        allele_id1: UUID = UUID("550e8400-e29b-41d4-a716-446655440101")
        allele_id2: UUID = UUID("550e8400-e29b-41d4-a716-446655440102")
        allele_id3: UUID = UUID("550e8400-e29b-41d4-a716-446655440103")

        existing_profile: model.SeqProfile = _make_allele_profile(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[allele_id1, None, allele_id3],
        )
        new_profile: model.SeqProfile = _make_allele_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[allele_id2, allele_id2, allele_id3],
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                seq_profiles=[new_profile],
            )
        )

        protocol: model.Protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.ALLELE_HAMMING,
            max_stored_distance=0.5,
        )
        existing_seq_distance: model.SeqDistance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: [existing_profile]},
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable([existing_seq_distance])
        )

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].seq_distance_profile_id, self.new_profile_id)
        self.assertEqual(results[0].status, EtlStatus.CREATED)

        self.assertEqual(len(recorder.updated), 0)
        self.assertEqual(len(recorder.created), 1)
        created_map: dict[str, float] = json.loads(recorder.created[0].content)
        self.assertEqual(created_map, {})

    def test_mlva_profiles_distance_ignores_missing_loci_and_stores_distance(
        self,
    ) -> None:
        existing_profile: model.SeqProfile = _make_mlva_profile(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            repeat_numbers=[1, None, 3, 4],
        )
        new_profile: model.SeqProfile = _make_mlva_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            repeat_numbers=[2, None, 3, 0],
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                seq_profiles=[new_profile],
            )
        )

        protocol: model.Protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.MLVA_HAMMING,
            max_stored_distance=100.0,
        )
        existing_seq_distance: model.SeqDistance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: [existing_profile]},
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable([existing_seq_distance])
        )

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].status, EtlStatus.UPDATED)
        self.assertEqual(results[1].status, EtlStatus.CREATED)

        self.assertEqual(len(recorder.updated), 1)
        updated_map: dict[str, float] = json.loads(recorder.updated[0].content)
        self.assertIn(str(self.new_profile_id), updated_map)

        self.assertEqual(len(recorder.created), 1)
        created_map: dict[str, float] = json.loads(recorder.created[0].content)
        self.assertIn(str(self.existing_profile_id), created_map)

        expected: float = float(
            sum(
                1
                for x, y in zip(
                    [1, MLVA_NO_LOCUS_REPEAT_NUMBER, 3, 4],
                    [2, MLVA_NO_LOCUS_REPEAT_NUMBER, 3, 0],
                )
                if x != y
                and x != MLVA_NO_LOCUS_REPEAT_NUMBER
                and y != MLVA_NO_LOCUS_REPEAT_NUMBER
            )
        )
        self.assertEqual(updated_map[str(self.new_profile_id)], expected)
        self.assertEqual(created_map[str(self.existing_profile_id)], expected)

    def test_mlva_profiles_unsupported_existing_profile_format_raises(self) -> None:
        existing_profile: model.SeqProfile = model.SeqProfile.model_construct(
            id=self.existing_profile_id,
            sample_id=self.sample_id,
            seq_id=None,
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            mlva_profile=json.dumps([1, 2]),
            mlva_profile_format="UNSUPPORTED",
            mlva_profile_hash=uuid4(),
            qc_score=1.0,
            qc_result=enum.QualityControlResult.PASS,
        )
        new_profile: model.SeqProfile = _make_mlva_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            repeat_numbers=[1, 2],
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                seq_profiles=[new_profile],
            )
        )

        protocol: model.Protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.MLVA_HAMMING,
            max_stored_distance=100.0,
        )
        existing_seq_distance: model.SeqDistance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: [existing_profile]},
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable([existing_seq_distance])
        )

        with self.assertRaises(NotImplementedError):
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

    def test_mlva_profiles_unsupported_new_profile_format_raises(self) -> None:
        existing_profile: model.SeqProfile = _make_mlva_profile(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            repeat_numbers=[1, 2],
        )
        new_profile: model.SeqProfile = model.SeqProfile.model_construct(
            id=self.new_profile_id,
            sample_id=self.sample_id2,
            seq_id=None,
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            mlva_profile=json.dumps([1, 2]),
            mlva_profile_format="UNSUPPORTED",
            mlva_profile_hash=uuid4(),
            qc_score=1.0,
            qc_result=enum.QualityControlResult.PASS,
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                seq_profiles=[new_profile],
            )
        )

        protocol: model.Protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.MLVA_HAMMING,
            max_stored_distance=100.0,
        )
        existing_seq_distance: model.SeqDistance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: [existing_profile]},
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable([existing_seq_distance])
        )

        with self.assertRaises(NotImplementedError):
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

    def test_existing_seq_distances_empty_skips_read_some_and_creates_new(self) -> None:
        new_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.snp_detection_protocol_id,
            aligned_nucleotide_seq="AAAA",
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=None,
                snp_profiles=[new_profile],
            )
        )

        protocol: model.Protocol = _make_seq_distance_protocol_for_snp(
            protocol_id=self.protocol_id,
            ref_seq_id=self.ref_seq_id,
            max_stored_distance=100.0,
        )
        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: []},
        )
        self.service.repository.iter_seq_distances = Mock(return_value=_iterable([]))

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(len(recorder.read_some_calls), 0)
        self.assertEqual(len(recorder.updated), 0)
        self.assertEqual(len(recorder.created), 1)
        self.assertEqual(json.loads(recorder.created[0].content), {})

    def test_new_profile_without_id_is_processed(self) -> None:
        # A profile with id=None is silently filtered out by the service
        # (new_profiles_list excludes None-id entries).  No SeqDistance is
        # created and no result is returned.  The caller is responsible for
        # providing profiles with valid IDs before calling this function.
        existing_profile: model.SeqProfile = _make_allele_profile(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[uuid4()],
        )
        new_profile: model.SeqProfile = _make_allele_profile(
            profile_id=None,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[uuid4()],
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                seq_profiles=[new_profile],
            )
        )

        protocol: model.Protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.ALLELE_HAMMING,
            max_stored_distance=100.0,
        )
        existing_seq_distance: model.SeqDistance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: [existing_profile]},
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable([existing_seq_distance])
        )

        # Should not raise; the None-id profile is filtered out and skipped
        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(len(results), 0)
        self.assertEqual(len(recorder.created), 0)


@pytest.mark.scenario_ids("TC-11-13-01")
class TestCalculateSeqDistancesBatchInvariant(BaseCalculateSeqDistanceTestCase):

    def _make_batch_allele_profiles(
        self,
    ) -> tuple[
        list[model.SeqProfile],
        list[model.SeqProfile],
        list[UUID],
        list[UUID],
    ]:
        """Return (existing_profiles, new_profiles, existing_ids, new_ids)."""
        a1 = UUID("aaaaaaaa-0000-0000-0000-000000000001")
        a2 = UUID("aaaaaaaa-0000-0000-0000-000000000002")
        a3 = UUID("aaaaaaaa-0000-0000-0000-000000000003")
        a4 = UUID("aaaaaaaa-0000-0000-0000-000000000004")

        e1_id = UUID("eeeeeeee-0000-0000-0000-000000000001")
        e2_id = UUID("eeeeeeee-0000-0000-0000-000000000002")
        n1_id = UUID("bbbbbbbb-0000-0000-0000-000000000001")
        n2_id = UUID("bbbbbbbb-0000-0000-0000-000000000002")
        n3_id = UUID("bbbbbbbb-0000-0000-0000-000000000003")

        existing_profiles = [
            _make_allele_profile(
                profile_id=e1_id,
                sample_id=self.sample_id,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=[a1, a2],
            ),
            _make_allele_profile(
                profile_id=e2_id,
                sample_id=self.sample_id,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=[a3, a4],
            ),
        ]
        new_profiles = [
            _make_allele_profile(
                profile_id=n1_id,
                sample_id=self.sample_id2,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=[a1, a3],  # distance to N2 = 1, to N3 = 2
            ),
            _make_allele_profile(
                profile_id=n2_id,
                sample_id=self.sample_id2,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=[a2, a3],  # distance to N1 = 1, to N3 = 1
            ),
            _make_allele_profile(
                profile_id=n3_id,
                sample_id=self.sample_id2,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=[a2, a4],  # distance to N1 = 2, to N2 = 1
            ),
        ]
        return existing_profiles, new_profiles, [e1_id, e2_id], [n1_id, n2_id, n3_id]

    def test_batch_upload_all_inter_batch_pairs_stored_in_both_maps(self) -> None:
        """All combinations pairs must appear symmetrically in each new map."""
        existing_profiles, new_profiles, existing_ids, new_ids = (
            self._make_batch_allele_profiles()
        )
        n1_id, n2_id, n3_id = new_ids
        e1_id, e2_id = existing_ids

        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.ALLELE_HAMMING,
            max_stored_distance=100.0,
        )
        existing_seq_distances = [
            _make_seq_distance(
                seq_distance_id=uuid4(),
                protocol_id=self.protocol_id,
                profile_id=e_id,
                sample_id=self.sample_id,
                distances={},
            )
            for e_id in existing_ids
        ]

        recorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: existing_profiles},  # type: ignore[dict-item]
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable(existing_seq_distances)
        )

        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=new_profiles,
        )
        results = seq_service_calculate_seq_distances_for_new_profiles(
            self.service, cmd
        )

        # Correct number of results
        self.assertEqual(len(results), 5)
        result_ids = {
            x.seq_distance_profile_id for x in results if x.status == EtlStatus.CREATED
        }
        self.assertEqual(result_ids, {n1_id, n2_id, n3_id})

        # Build {profile_id: distances_dict} from created records
        self.assertEqual(
            len(recorder.created), 3, "Expected one SeqDistance per new profile"
        )
        created_maps: dict[UUID, dict[str, float]] = {
            x.seq_profile_id: json.loads(x.content) for x in recorder.created
        }

        # Every inter-batch pair must be present in BOTH directions
        intra_batch_pairs = [(n1_id, n2_id), (n1_id, n3_id), (n2_id, n3_id)]
        for id_a, id_b in intra_batch_pairs:
            self.assertIn(
                str(id_b),
                created_maps[id_a],
                f"distance({id_a},{id_b}) missing from {id_a}'s map",
            )
            self.assertIn(
                str(id_a),
                created_maps[id_b],
                f"distance({id_b},{id_a}) missing from {id_b}'s map",
            )
            # Symmetry: both values must be equal
            self.assertEqual(
                created_maps[id_a][str(id_b)],
                created_maps[id_b][str(id_a)],
                f"Asymmetric distance for pair ({id_a},{id_b})",
            )

        # Cross pairs must still be present
        for n_id in [n1_id, n2_id, n3_id]:
            for e_id in existing_ids:
                self.assertIn(
                    str(e_id),
                    created_maps[n_id],
                    f"N×E distance missing: new={n_id}, existing={e_id}",
                )

    def test_batch_upload_intra_batch_pair_over_threshold_not_stored(self) -> None:
        """Inter-batch pairs whose distance exceeds max_stored_distance are omitted."""
        existing_profiles, new_profiles, existing_ids, new_ids = (
            self._make_batch_allele_profiles()
        )
        n1_id, n2_id, n3_id = new_ids

        # max_stored_distance=0 → no pair survives
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.ALLELE_HAMMING,
            max_stored_distance=0.0,
        )
        existing_seq_distances = [
            _make_seq_distance(
                seq_distance_id=uuid4(),
                protocol_id=self.protocol_id,
                profile_id=e_id,
                sample_id=self.sample_id,
                distances={},
            )
            for e_id in existing_ids
        ]

        recorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: existing_profiles},  # type: ignore[dict-item]
        )
        self.service.repository.iter_seq_distances = Mock(
            return_value=_iterable(existing_seq_distances)
        )

        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=new_profiles,
        )
        seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

        created_maps: dict[UUID, dict[str, float]] = {
            x.seq_profile_id: json.loads(x.content) for x in recorder.created
        }
        # All maps must be empty — nothing was within threshold
        for n_id in [n1_id, n2_id, n3_id]:
            self.assertEqual(
                created_maps[n_id],
                {},
                f"Expected empty map for {n_id} but got {created_maps[n_id]}",
            )

    def test_single_new_profile_skips_intra_batch_loop(self) -> None:
        locus_set_id = self.locus_set_id
        a1 = uuid4()
        n1_id = UUID("bbbbbbbb-0000-0000-0000-000000000001")

        new_profile = _make_allele_profile(
            profile_id=n1_id,
            sample_id=self.sample_id2,
            locus_set_id=locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[a1],
        )
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.ALLELE_HAMMING,
            max_stored_distance=100.0,
        )

        recorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: []},
        )
        self.service.repository.iter_seq_distances = Mock(return_value=_iterable([]))

        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=[new_profile],
        )
        results = seq_service_calculate_seq_distances_for_new_profiles(
            self.service, cmd
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(len(recorder.created), 1)
        self.assertEqual(json.loads(recorder.created[0].content), {})
