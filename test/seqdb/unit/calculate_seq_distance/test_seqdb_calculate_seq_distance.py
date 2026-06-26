import json
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import numpy as np
import pytest

from gen_epix.commondb.domain.enum import EtlStatus, Role
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.exc import ConcurrentModificationError, InvalidArgumentsError
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.services.seq.calculate_seq_distance import (
    _INT32_VOCAB_GATE,
    _NULL_ALLELE,
    _calculate_and_store_distances,
    _calculate_distance_for_decoded_profile_pair,
    _calculate_pairwise_profile_distances,
    _decode_profile,
    _encode_to_int32,
    _hamming_allele_int32_batch,
    _hamming_allele_numpy,
    _hamming_allele_numpy_batch,
    seq_service_calculate_seq_distances_for_new_profiles,
    seq_service_update_seq_distances,
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


def _make_nextclade_content(
    *,
    substitutions: str = "",
    deletions: str = "",
    insertions: str = "",
    missing: str = "",
    non_acgtns: str = "",
    alignment_start: int = 1,
    alignment_end: int = 1,
) -> str:
    return json.dumps(
        {
            "substitutions": substitutions,
            "deletions": deletions,
            "insertions": insertions,
            "missings": missing,
            "non_acgtns": non_acgtns,
            "alignment_start": alignment_start,
            "alignment_end": alignment_end,
        }
    )


def _make_snp_profile_for_upload(
    *,
    profile_id: UUID,
    sample_id: UUID,
    ref_seq_id: UUID,
    protocol_id: UUID,
    nextclade_content: str | None = None,
) -> model.SeqProfile:
    return model.SeqProfile.model_construct(
        id=profile_id,
        sample_id=sample_id,
        seq_id=None,
        ref_seq_id=ref_seq_id,
        protocol_id=protocol_id,
        content=nextclade_content or _make_nextclade_content(),
        format=enum.SeqProfileFormat.NEXTCLADE,
        content_hash=model.SeqProfile.get_snp_profile_hash(
            model.SeqProfile.model_construct(
                content=nextclade_content or _make_nextclade_content(),
                format=enum.SeqProfileFormat.NEXTCLADE,
            ).get_snps()
        ),
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


def _setup_distance_mocks(
    service_mock: Mock,
    existing_distances: list[model.SeqDistance],
    recorder: "_CrudRecorder | None" = None,
) -> None:
    """
    Set up mocks for iter_seq_distances,
    iter_seq_distance_profile_ids and
    get_max_seq_distance_modified_at consistently.

    iter_seq_distances is mocked with a side_effect so that
    each call gets a fresh iterator and filters by the
    ``profile_ids`` kwarg when provided.

    Pass recorder to also mock update_some_seq_distance_content
    so that bulk-updated objects are captured in recorder.updated.
    """

    def _iter_distances(
        uow: Any,
        protocol_id: UUID,
        profile_ids: list[UUID] | None = None,
    ) -> Iterator[model.SeqDistance]:
        pid_set = set(profile_ids) if profile_ids is not None else None
        for d in existing_distances:
            if pid_set is None or d.seq_profile_id in pid_set:
                yield d

    service_mock.repository.iter_seq_distances = Mock(
        side_effect=_iter_distances,
    )
    profile_ids = list(
        dict.fromkeys(
            seq_distance.seq_profile_id for seq_distance in existing_distances
        )
    )
    service_mock.repository.iter_seq_distance_profile_ids = Mock(
        return_value=iter(profile_ids),
    )
    service_mock.repository.get_max_seq_distance_modified_at = Mock(
        return_value=None,
    )
    if recorder is not None:

        def _update_some(uow: Any, user_id: Any, objs: list[model.SeqDistance]) -> None:
            recorder.updated.extend(objs)

        service_mock.repository.update_some_seq_distance_content = Mock(
            side_effect=_update_some,
        )


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
        operation: CrudOperation,
        filter: Any = None,
        objs: Any = None,
        obj_ids: Any = None,
        **kwargs: Any,
    ) -> Any:
        if model_class is model.Protocol and operation == CrudOperation.READ_ALL:
            return protocols
        if operation == CrudOperation.READ_SOME:
            assert isinstance(obj_ids, list)
            recorder.read_some_calls.append(obj_ids)
            return existing_profiles_by_model.get(model_class, [])
        if model_class is model.SeqDistance and operation == CrudOperation.UPDATE_ONE:
            assert isinstance(objs, model.SeqDistance)
            recorder.updated.append(objs)
            return objs
        if model_class is model.SeqDistance and operation == CrudOperation.UPDATE_SOME:
            assert isinstance(objs, list)
            for item in objs:
                assert isinstance(item, model.SeqDistance)
            recorder.updated.extend(objs)
            return objs
        if model_class is model.SeqDistance and operation == CrudOperation.CREATE_ONE:
            assert isinstance(objs, model.SeqDistance)
            recorder.created.append(objs)
            return objs
        if model_class is model.SeqDistance and operation == CrudOperation.CREATE_SOME:
            assert isinstance(objs, list)
            for item in objs:
                assert isinstance(item, model.SeqDistance)
            recorder.created.extend(objs)
            return objs
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
                user=self.user, seq_profiles=[]
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
        _setup_distance_mocks(self.service, [])

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(results, [])
        self.service.repository.iter_seq_distances.assert_not_called()
        self.assertEqual(len(recorder.created), 0)
        self.assertEqual(len(recorder.updated), 0)

    def test_kmer_profiles_raises_not_implemented(self) -> None:
        kmer_profile = model.SeqProfile.model_construct(
            id=uuid4(),
            sample_id=self.sample_id,
            seq_id=None,
            protocol_id=uuid4(),
            content="{}",
            format=enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
            content_hash=uuid4(),
            seq_profile_type=enum.SeqProfileType.KMER,
            qc_score=1.0,
            qc_result=enum.QualityControlResult.PASS,
        )
        cmd = command.CalculateSeqDistancesForNewProfilesCommand.model_construct(
            user=self.user,
            seq_profiles=[kmer_profile],
        )

        recorder: _CrudRecorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[],
        )

        with self.assertRaises(NotImplementedError):
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

    def test_protocol_not_applicable_skips_distance_calculation(self) -> None:
        # Profile's profiling protocol uses
        # other_ref_seq_id; distance protocol uses
        # ref_seq_id -> no match -> empty results
        snp_profiling_protocol: model.Protocol = (
            model.Protocol(  # type: ignore[call-arg]
                id=self.snp_detection_protocol_id,
                code="SNP_PROFILING_OTHER_REF",
                protocol_type=enum.ProtocolType.SEQ_PROFILE,
                seq_profile_type=enum.SeqProfileType.SNP,
                ref_seq_id=self.other_ref_seq_id,
            )
        )
        snp_distance_protocol: model.Protocol = _make_seq_distance_protocol_for_snp(
            protocol_id=self.protocol_id,
            ref_seq_id=self.ref_seq_id,
            max_stored_distance=10.0,
        )
        snp_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id,
            ref_seq_id=self.other_ref_seq_id,
            protocol_id=self.snp_detection_protocol_id,
            nextclade_content=_make_nextclade_content(alignment_end=4),
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                seq_profiles=[snp_profile],
            )
        )

        read_all_results: Iterator[list[model.Protocol]] = iter(
            [
                [snp_profiling_protocol],
                [snp_distance_protocol],
            ]
        )

        def _crud(
            uow: BaseUnitOfWork,
            user_id: UUID | None,
            model_class: type,
            operation: CrudOperation,
            filter: Any = None,
            objs: Any = None,
            obj_ids: Any = None,
            **kwargs: Any,
        ) -> Any:
            if model_class is model.Protocol and operation == CrudOperation.READ_ALL:
                return next(read_all_results)
            return []

        self.service.repository.crud.side_effect = _crud
        _setup_distance_mocks(self.service, [])

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(results, [])

    def test_snp_profiles_updates_existing_and_creates_new_seq_distances(self) -> None:
        existing_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.protocol_id,
            nextclade_content=_make_nextclade_content(
                substitutions="A3C,A4C,A5T",
                alignment_end=5,
            ),
        )
        new_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.protocol_id,
            nextclade_content=_make_nextclade_content(
                substitutions="A3T,A4T,A5T",
                alignment_end=5,
            ),
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=self.user,
                seq_profiles=[new_profile],
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
        _setup_distance_mocks(self.service, [existing_seq_distance], recorder=recorder)

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

        expected_distance = 2.0

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
        _setup_distance_mocks(self.service, [existing_seq_distance])

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
        _setup_distance_mocks(self.service, [existing_seq_distance], recorder=recorder)

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
            content=json.dumps([1, 2]),
            format="UNSUPPORTED",
            content_hash=uuid4(),
            seq_profile_type=enum.SeqProfileType.MLVA,
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
        _setup_distance_mocks(self.service, [existing_seq_distance])

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
            content=json.dumps([1, 2]),
            format="UNSUPPORTED",
            content_hash=uuid4(),
            seq_profile_type=enum.SeqProfileType.MLVA,
            qc_score=1.0,
            qc_result=enum.QualityControlResult.PASS,
        )
        cmd = command.CalculateSeqDistancesForNewProfilesCommand.model_construct(
            user=self.user,
            seq_profiles=[new_profile],
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
        _setup_distance_mocks(self.service, [existing_seq_distance])

        with self.assertRaises(NotImplementedError):
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

    def test_existing_seq_distances_empty_skips_read_some_and_creates_new(self) -> None:
        new_profile: model.SeqProfile = _make_snp_profile_for_upload(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.protocol_id,
            nextclade_content=_make_nextclade_content(alignment_end=4),
        )
        cmd: command.CalculateSeqDistancesForNewProfilesCommand = (
            command.CalculateSeqDistancesForNewProfilesCommand(
                user=None,
                seq_profiles=[new_profile],
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
        _setup_distance_mocks(self.service, [])

        results: list[model.CalculateSeqDistancesResult] = (
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(len(recorder.read_some_calls), 0)
        self.assertEqual(len(recorder.updated), 0)
        self.assertEqual(len(recorder.created), 1)
        self.assertEqual(json.loads(recorder.created[0].content), {})

    def _run_snp_distance(
        self,
        existing_content: str,
        new_content: str,
        max_stored_distance: float = 100.0,
    ) -> tuple[
        _CrudRecorder,
        list[model.CalculateSeqDistancesResult],
    ]:
        """Helper: compute SNP distance between two
        profiles via the service."""
        existing_profile = _make_snp_profile_for_upload(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.protocol_id,
            nextclade_content=existing_content,
        )
        new_profile = _make_snp_profile_for_upload(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            ref_seq_id=self.ref_seq_id,
            protocol_id=self.protocol_id,
            nextclade_content=new_content,
        )
        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=[new_profile],
        )
        protocol = _make_seq_distance_protocol_for_snp(
            protocol_id=self.protocol_id,
            ref_seq_id=self.ref_seq_id,
            max_stored_distance=max_stored_distance,
        )
        existing_seq_distance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )
        recorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
            existing_profiles_by_model={model.SeqProfile: [existing_profile]},
        )
        _setup_distance_mocks(self.service, [existing_seq_distance])
        results = seq_service_calculate_seq_distances_for_new_profiles(
            self.service, cmd
        )
        return recorder, results

    def test_snp_distance_identical_mismatch_n_and_gap(
        self,
    ) -> None:
        """Identical profiles are zero-distance and Nextclade states mismatch."""
        recorder, results = self._run_snp_distance(
            _make_nextclade_content(alignment_end=4),
            _make_nextclade_content(alignment_end=4),
        )
        self.assertEqual(len(results), 2)
        self.assertEqual(
            json.loads(recorder.created[0].content)[str(self.existing_profile_id)],
            0.0,
        )

        recorder, results = self._run_snp_distance(
            _make_nextclade_content(alignment_end=4),
            _make_nextclade_content(substitutions="A2T", alignment_end=4),
        )
        self.assertEqual(
            json.loads(recorder.created[0].content)[str(self.existing_profile_id)],
            1.0,
        )

        recorder, results = self._run_snp_distance(
            _make_nextclade_content(
                deletions="4",
                missing="2",
                non_acgtns="R:3",
                alignment_end=4,
            ),
            _make_nextclade_content(
                substitutions="A2T",
                alignment_end=5,
            ),
        )
        self.assertEqual(
            json.loads(recorder.created[0].content)[str(self.existing_profile_id)],
            4.0,
        )

    def test_snp_mismatched_length_raises(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            self._run_snp_distance(
                _make_nextclade_content(substitutions="bad", alignment_end=4),
                _make_nextclade_content(alignment_end=4),
            )

    def test_new_profile_without_id_raises(self) -> None:
        # Profiles without IDs are invalid input for distance calculation.
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
        _setup_distance_mocks(self.service, [existing_seq_distance])

        with self.assertRaises(InvalidArgumentsError) as ctx:
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

        self.assertEqual(ctx.exception.args[0], "fbb3c9e7")
        self.assertIn("All new profiles must have an ID", str(ctx.exception))


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
        _setup_distance_mocks(self.service, existing_seq_distances, recorder=recorder)

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
        _setup_distance_mocks(self.service, existing_seq_distances)

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
        _setup_distance_mocks(self.service, [])

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


@pytest.mark.scenario_ids("TC-11-13-01")
class TestConcurrentModificationCheck(
    BaseCalculateSeqDistanceTestCase,
):
    def test_stale_timestamp_raises_concurrent_error(
        self,
    ) -> None:
        """Fail when SeqDistances were modified after the
        provided timestamp."""
        new_profile = _make_allele_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[uuid4()],
        )
        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=[new_profile],
            seq_distance_last_modified_at=datetime(
                2025,
                1,
                1,
                tzinfo=timezone.utc,
            ),
        )
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=(enum.SeqDistanceType.ALLELE_HAMMING),
            max_stored_distance=100.0,
        )
        recorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
        )
        # Distances were modified AFTER the provided ts
        _setup_distance_mocks(self.service, [])
        self.service.repository.get_max_seq_distance_modified_at = Mock(
            return_value=datetime(
                2025,
                6,
                1,
                tzinfo=timezone.utc,
            ),
        )

        with self.assertRaises(ConcurrentModificationError):
            seq_service_calculate_seq_distances_for_new_profiles(
                self.service,
                cmd,
            )

    def test_fresh_timestamp_proceeds_normally(
        self,
    ) -> None:
        """Succeed when no modifications occurred after
        the provided timestamp."""
        new_profile = _make_allele_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[uuid4()],
        )
        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=[new_profile],
            seq_distance_last_modified_at=datetime(
                2025,
                6,
                1,
                tzinfo=timezone.utc,
            ),
        )
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=(enum.SeqDistanceType.ALLELE_HAMMING),
            max_stored_distance=100.0,
        )
        recorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
        )
        _setup_distance_mocks(self.service, [])
        self.service.repository.get_max_seq_distance_modified_at = Mock(
            return_value=datetime(
                2025,
                1,
                1,
                tzinfo=timezone.utc,
            ),
        )

        results = seq_service_calculate_seq_distances_for_new_profiles(
            self.service,
            cmd,
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].status,
            EtlStatus.CREATED,
        )

    def test_none_timestamp_skips_check(self) -> None:
        """When no timestamp is provided, proceed without
        checking."""
        new_profile = _make_allele_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[uuid4()],
        )
        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=[new_profile],
        )
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=(enum.SeqDistanceType.ALLELE_HAMMING),
            max_stored_distance=100.0,
        )
        recorder = _CrudRecorder()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=recorder,
            protocols=[protocol],
        )
        _setup_distance_mocks(self.service, [])

        results = seq_service_calculate_seq_distances_for_new_profiles(
            self.service,
            cmd,
        )
        self.assertEqual(len(results), 1)
        (self.service.repository.get_max_seq_distance_modified_at.assert_not_called())


@pytest.mark.scenario_ids("TC-11-13-03")
class TestUpdateSeqDistances(
    BaseCalculateSeqDistanceTestCase,
):
    def test_no_missing_profiles_returns_empty(
        self,
    ) -> None:
        """When all profiles already have distances,
        returns empty."""
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=(enum.SeqDistanceType.ALLELE_HAMMING),
            max_stored_distance=100.0,
        )
        profiling_protocol = model.Protocol(  # type: ignore[call-arg]
            id=self.locus_detection_protocol_id,
            code="ALLELE_PROFILING",
            name="Allele Profiling",
            protocol_type=enum.ProtocolType.SEQ_PROFILE,
            seq_profile_type=enum.SeqProfileType.ALLELE,
            locus_set_id=self.locus_set_id,
        )
        existing_profile = _make_allele_profile(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.locus_detection_protocol_id,
            allele_ids=[uuid4()],
        )

        # Profile already has a SeqDistance
        _setup_distance_mocks(
            self.service,
            [
                _make_seq_distance(
                    seq_distance_id=uuid4(),
                    protocol_id=self.protocol_id,
                    profile_id=self.existing_profile_id,
                    sample_id=self.sample_id,
                )
            ],
        )

        def _crud(
            uow: Any,
            user_id: Any,
            model_class: Any,
            operation: CrudOperation,
            filter: Any = None,
            objs: Any = None,
            obj_ids: Any = None,
            **kwargs: Any,
        ) -> Any:
            if model_class is model.Protocol and operation == CrudOperation.READ_ONE:
                return protocol
            if model_class is model.Protocol and operation == CrudOperation.READ_ALL:
                return [profiling_protocol]
            return []

        self.service.repository.crud.side_effect = _crud
        # All profiles already have distances — SQL NOT EXISTS returns nothing.
        self.service.repository.get_profiles_without_seq_distance = Mock(
            return_value=[],
        )

        cmd = command.UpdateSeqDistancesCommand(
            user=self.user,
            protocol_id=self.protocol_id,
        )
        results = seq_service_update_seq_distances(
            self.service,
            cmd,
        )
        self.assertEqual(results, [])

    def test_missing_profile_creates_distance(
        self,
    ) -> None:
        """When a profile is missing a distance, create
        it and maintain symmetry."""
        a1 = uuid4()
        a2 = uuid4()
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=(enum.SeqDistanceType.ALLELE_HAMMING),
            max_stored_distance=100.0,
        )
        profiling_protocol = model.Protocol(  # type: ignore[call-arg]
            id=self.locus_detection_protocol_id,
            code="ALLELE_PROFILING",
            name="Allele Profiling",
            protocol_type=enum.ProtocolType.SEQ_PROFILE,
            seq_profile_type=enum.SeqProfileType.ALLELE,
            locus_set_id=self.locus_set_id,
        )
        existing_profile = _make_allele_profile(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.locus_detection_protocol_id,
            allele_ids=[a1],
        )
        missing_profile = _make_allele_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.locus_detection_protocol_id,
            allele_ids=[a2],
        )

        existing_distance = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )
        # Only existing profile has a distance record
        recorder = _CrudRecorder()
        _setup_distance_mocks(self.service, [existing_distance], recorder=recorder)

        def _crud(
            uow: Any,
            user_id: Any,
            model_class: Any,
            operation: CrudOperation,
            filter: Any = None,
            objs: Any = None,
            obj_ids: Any = None,
            **kwargs: Any,
        ) -> Any:
            if model_class is model.Protocol and operation == CrudOperation.READ_ONE:
                return protocol
            if model_class is model.Protocol and operation == CrudOperation.READ_ALL:
                return [profiling_protocol]
            if model_class is model.SeqProfile and operation == CrudOperation.READ_SOME:
                recorder.read_some_calls.append(obj_ids)
                return [existing_profile]
            if (
                model_class is model.SeqDistance
                and operation == CrudOperation.CREATE_SOME
            ):
                recorder.created.extend(objs)
                return objs
            return []

        self.service.repository.crud.side_effect = _crud
        # SQL NOT EXISTS returns only the profile without a distance record.
        self.service.repository.get_profiles_without_seq_distance = Mock(
            return_value=[missing_profile],
        )

        cmd = command.UpdateSeqDistancesCommand(
            user=self.user,
            protocol_id=self.protocol_id,
        )
        results = seq_service_update_seq_distances(
            self.service,
            cmd,
        )

        # One update (existing) + one create (missing)
        self.assertEqual(len(results), 2)
        created_ids = {
            r.seq_distance_profile_id for r in results if r.status == EtlStatus.CREATED
        }
        self.assertIn(self.new_profile_id, created_ids)

        # Symmetry: existing distance updated with
        # new profile's distance AND new distance
        # contains existing profile's distance
        self.assertEqual(len(recorder.created), 1)
        created_map = json.loads(
            recorder.created[0].content,
        )
        self.assertIn(
            str(self.existing_profile_id),
            created_map,
        )
        self.assertEqual(len(recorder.updated), 1)
        updated_map = json.loads(
            recorder.updated[0].content,
        )
        self.assertIn(
            str(self.new_profile_id),
            updated_map,
        )

    def test_chunked_existing_profiles_updates_both_and_maintains_symmetry(
        self,
    ) -> None:
        """With existing_chunk_size=1 and 2 existing profiles,
        iter_seq_distances is called once per chunk, both
        existing records are updated, and the new profile's
        distance map contains both existing profile IDs.
        """
        a1, a2, a3 = uuid4(), uuid4(), uuid4()
        existing_profile_id_2 = UUID("550e8400-e29b-41d4-a716-446655440012")
        sample_id_3 = UUID("550e8400-e29b-41d4-a716-446655440007")
        protocol = _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.ALLELE_HAMMING,
            max_stored_distance=100.0,
        )
        existing_profile_1 = _make_allele_profile(
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.locus_detection_protocol_id,
            allele_ids=[a1],
        )
        existing_profile_2 = _make_allele_profile(
            profile_id=existing_profile_id_2,
            sample_id=sample_id_3,
            locus_set_id=self.locus_set_id,
            protocol_id=self.locus_detection_protocol_id,
            allele_ids=[a2],
        )
        new_profile = _make_allele_profile(
            profile_id=self.new_profile_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.locus_detection_protocol_id,
            allele_ids=[a3],
        )
        existing_distance_1 = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=self.existing_profile_id,
            sample_id=self.sample_id,
            distances={},
        )
        existing_distance_2 = _make_seq_distance(
            seq_distance_id=uuid4(),
            protocol_id=self.protocol_id,
            profile_id=existing_profile_id_2,
            sample_id=sample_id_3,
            distances={},
        )

        recorder = _CrudRecorder()
        _setup_distance_mocks(
            self.service,
            [existing_distance_1, existing_distance_2],
            recorder=recorder,
        )

        profiles_by_id = {
            self.existing_profile_id: existing_profile_1,
            existing_profile_id_2: existing_profile_2,
        }

        def _crud(
            uow: Any,
            user_id: Any,
            model_class: Any,
            operation: CrudOperation,
            filter: Any = None,
            objs: Any = None,
            obj_ids: Any = None,
            **kwargs: Any,
        ) -> Any:
            if model_class is model.SeqProfile and operation == CrudOperation.READ_SOME:
                recorder.read_some_calls.append(list(obj_ids))
                return [profiles_by_id[i] for i in obj_ids if i in profiles_by_id]
            if (
                model_class is model.SeqDistance
                and operation == CrudOperation.CREATE_SOME
            ):
                recorder.created.extend(objs)
                return objs
            return []

        self.service.repository.crud.side_effect = _crud

        results: list[model.CalculateSeqDistancesResult] = []
        _calculate_and_store_distances(
            self.service,
            Mock(),
            None,
            protocol,
            enum.SeqProfileType.ALLELE,
            [new_profile],
            results,
            known_existing_profile_ids=[
                self.existing_profile_id,
                existing_profile_id_2,
            ],
            existing_chunk_size=1,
        )

        # iter_seq_distances called once per chunk (2 chunks for 2 profiles)
        self.assertEqual(self.service.repository.iter_seq_distances.call_count, 2)
        # Both existing records updated, one new record created
        self.assertEqual(len(recorder.updated), 2)
        self.assertEqual(len(recorder.created), 1)
        # New profile's map accumulates distances from both chunks
        created_map = json.loads(recorder.created[0].content)
        self.assertIn(str(self.existing_profile_id), created_map)
        self.assertIn(str(existing_profile_id_2), created_map)


# ── Numpy allele compute helpers ─────────────────────────────────────────────


def _s16(byte_val: int, n_loci: int = 5) -> np.ndarray:
    """Return an (n_loci,) S16 array where every locus has the same UUID byte."""
    return np.array([bytes([byte_val] * 16)] * n_loci, dtype="S16")


class TestNumpyAlleleKernels(TestCase):
    def test_hamming_allele_numpy_identity_mismatch_null(self) -> None:
        a = np.array([b"\x01" * 16, b"\x02" * 16, b"\x03" * 16], dtype="S16")
        b = np.array([b"\x01" * 16, b"\x99" * 16, b"\x03" * 16], dtype="S16")
        c = np.array([_NULL_ALLELE, b"\x02" * 16, b"\x03" * 16], dtype="S16")
        self.assertEqual(_hamming_allele_numpy(a, a), 0.0)   # identity
        self.assertEqual(_hamming_allele_numpy(a, b), 1.0)   # one mismatch
        self.assertEqual(_hamming_allele_numpy(a, c), 0.0)   # null excluded

    def test_hamming_allele_numpy_batch_matches_per_pair(self) -> None:
        n_loci = 4
        existing = np.array([b"\x01" * 16, b"\x02" * 16, b"\x03" * 16, b"\x04" * 16], dtype="S16")
        new_matrix = np.array([
            [b"\x01" * 16, b"\x02" * 16, b"\x03" * 16, b"\x04" * 16],  # identical
            [b"\x01" * 16, b"\x99" * 16, b"\x03" * 16, b"\x04" * 16],  # 1 diff
            [_NULL_ALLELE, b"\x02" * 16, b"\xAA" * 16, b"\x04" * 16],  # null + 1 diff
        ], dtype="S16")
        null_new = new_matrix == _NULL_ALLELE
        result = _hamming_allele_numpy_batch(existing, new_matrix, null_new)
        for i in range(3):
            self.assertEqual(result[i], _hamming_allele_numpy(existing, new_matrix[i]))

    def test_encode_to_int32_shared_token_gets_same_code(self) -> None:
        # Token \x01 appears in both new and chunk at column 0; must get same int32 code.
        new_s16 = np.array([[b"\x01" * 16, b"\x02" * 16]], dtype="S16")
        chunk_s16 = np.array([[b"\x01" * 16, b"\x03" * 16]], dtype="S16")
        new_int32, chunk_int32 = _encode_to_int32(new_s16, chunk_s16)
        self.assertEqual(new_int32[0, 0], chunk_int32[0, 0])   # shared \x01 token
        self.assertNotEqual(new_int32[0, 1], chunk_int32[0, 1])  # \x02 vs \x03

    def test_hamming_allele_int32_batch_matches_numpy_batch(self) -> None:
        rng = np.random.default_rng(0)
        n_loci, m = 10, 3
        allele_pool = [bytes([v] * 16) for v in range(1, 6)]
        new_s16 = np.array(
            [[allele_pool[rng.integers(0, 5)] for _ in range(n_loci)] for _ in range(m)],
            dtype="S16",
        )
        existing_s16 = np.array(
            [allele_pool[rng.integers(0, 5)] for _ in range(n_loci)], dtype="S16"
        )
        null_new = new_s16 == _NULL_ALLELE
        ref = _hamming_allele_numpy_batch(existing_s16, new_s16, null_new)

        new_int32, chunk_int32 = _encode_to_int32(new_s16, existing_s16[None, :])
        null_existing = existing_s16 == _NULL_ALLELE
        result = _hamming_allele_int32_batch(
            chunk_int32[0], new_int32, null_existing, null_new
        )
        for i in range(m):
            self.assertEqual(float(result[i]), ref[i])

    def test_int32_and_numpy_batch_produce_same_distances_as_python_loop(self) -> None:
        # Parity test: all three paths must agree on the same 5-locus, 4-profile case.
        alleles = [b"\x01" * 16, b"\x02" * 16, b"\x03" * 16, _NULL_ALLELE]
        existing_s16 = np.array([alleles[0], alleles[1], alleles[2], alleles[3], alleles[0]], dtype="S16")
        new_s16 = np.array([
            [alleles[0], alleles[1], alleles[2], alleles[3], alleles[1]],  # 1 diff (pos 4), null excl
            [alleles[2], alleles[1], alleles[0], alleles[3], alleles[0]],  # 2 diffs, null excl
        ], dtype="S16")
        null_new = new_s16 == _NULL_ALLELE
        null_existing = existing_s16 == _NULL_ALLELE

        # Python reference
        def _py(ex: np.ndarray, nw: np.ndarray) -> float:
            return float(sum(
                1 for e, n in zip(ex, nw)
                if e != n and e != _NULL_ALLELE and n != _NULL_ALLELE
            ))
        ref = [_py(existing_s16, new_s16[i]) for i in range(2)]

        # numpy_batch
        batch = _hamming_allele_numpy_batch(existing_s16, new_s16, null_new)
        # int32_vocab
        new_int32, chunk_int32 = _encode_to_int32(new_s16, existing_s16[None, :])
        int32_res = _hamming_allele_int32_batch(
            chunk_int32[0], new_int32, null_existing, null_new
        )
        for i in range(2):
            self.assertEqual(batch[i], ref[i])
            self.assertEqual(float(int32_res[i]), ref[i])


# ── Numpy allele integration tests ────────────────────────────────────────────


@pytest.mark.scenario_ids("TC-11-13-01")
class TestNumpyAlleleIntegration:
    """Unit tests for all new numpy ALLELE distance code paths (LSP-3529)."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.user = _make_user()
        self.protocol_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.locus_set_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.sample_id = UUID("550e8400-e29b-41d4-a716-446655440005")
        self.sample_id2 = UUID("550e8400-e29b-41d4-a716-446655440006")
        svc: Mock = Mock()
        svc.generate_id = Mock(side_effect=uuid4)
        svc.repository = Mock()
        svc.repository.uow.return_value = _mock_uow()
        self.service = svc

    def _allele_protocol(self, max_stored_distance: float = 100.0) -> model.Protocol:
        return _make_seq_distance_protocol_for_locus_set(
            protocol_id=self.protocol_id,
            locus_set_id=self.locus_set_id,
            seq_distance_protocol_type=enum.SeqDistanceType.ALLELE_HAMMING,
            max_stored_distance=max_stored_distance,
        )

    def _run_allele_numpy_calc(
        self,
        *,
        existing_allele_ids_list: list[list[UUID | None]],
        new_allele_ids_list: list[list[UUID | None]],
        max_stored_distance: float = 100.0,
        use_batch_new_profiles: bool = False,
        use_int32_vocab: bool = False,
    ) -> tuple[_CrudRecorder, list[UUID], list[UUID]]:
        """Run _calculate_and_store_distances directly for ALLELE profiles.
        Returns (recorder, existing_ids, new_ids)."""
        e_ids = [uuid4() for _ in existing_allele_ids_list]
        n_ids = [uuid4() for _ in new_allele_ids_list]
        existing_profiles = [
            _make_allele_profile(
                profile_id=e_ids[i],
                sample_id=self.sample_id,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=existing_allele_ids_list[i],
            )
            for i in range(len(e_ids))
        ]
        new_profiles = [
            _make_allele_profile(
                profile_id=n_ids[i],
                sample_id=self.sample_id2,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=new_allele_ids_list[i],
            )
            for i in range(len(n_ids))
        ]
        protocol = self._allele_protocol(max_stored_distance)
        existing_distances = [
            _make_seq_distance(
                seq_distance_id=uuid4(),
                protocol_id=self.protocol_id,
                profile_id=e_ids[i],
                sample_id=self.sample_id,
                distances={},
            )
            for i in range(len(e_ids))
        ]
        recorder = _CrudRecorder()
        _setup_distance_mocks(self.service, existing_distances, recorder=recorder)
        profiles_by_id = {e_ids[i]: existing_profiles[i] for i in range(len(e_ids))}

        def _crud(
            uow: Any,
            user_id: Any,
            model_class: type,
            operation: CrudOperation,
            filter: Any = None,
            objs: Any = None,
            obj_ids: Any = None,
            **kwargs: Any,
        ) -> Any:
            if model_class is model.SeqProfile and operation == CrudOperation.READ_SOME:
                return [profiles_by_id[i] for i in obj_ids if i in profiles_by_id]
            if model_class is model.SeqDistance and operation == CrudOperation.CREATE_SOME:
                recorder.created.extend(objs)
                return objs
            return []

        self.service.repository.crud.side_effect = _crud
        results: list[model.CalculateSeqDistancesResult] = []
        _calculate_and_store_distances(
            self.service,
            Mock(),
            None,
            protocol,
            enum.SeqProfileType.ALLELE,
            new_profiles,
            results,
            known_existing_profile_ids=e_ids,
            use_numpy_allele=True,
            use_batch_new_profiles=use_batch_new_profiles,
            use_int32_vocab=use_int32_vocab,
        )
        return recorder, e_ids, n_ids

    def test_decode_profile_numpy_returns_s16_array(self) -> None:
        """_decode_profile with use_numpy_allele=True returns (n_loci,) S16 array;
        null loci are encoded as _NULL_ALLELE."""
        a1, a2 = uuid4(), uuid4()
        profile = _make_allele_profile(
            profile_id=uuid4(),
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[a1, None, a2],
        )
        result = _decode_profile(enum.SeqProfileType.ALLELE, profile, use_numpy_allele=True)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.dtype("S16")
        assert result.shape == (3,)
        # numpy strips trailing null bytes on scalar access, so compare via array equality
        null_mask = result == _NULL_ALLELE
        assert not null_mask[0]   # a1 is non-null
        assert null_mask[1]       # None → encoded as _NULL_ALLELE
        assert not null_mask[2]   # a2 is non-null

    def test_calculate_distance_pair_numpy_branch(self) -> None:
        """The isinstance(np.ndarray) branch in _calculate_distance_for_decoded_profile_pair
        delegates to _hamming_allele_numpy and returns the correct float distance."""
        a = np.array([b"\x01" * 16, b"\x02" * 16, b"\x03" * 16], dtype="S16")
        b = np.array([b"\x01" * 16, b"\x99" * 16, b"\x03" * 16], dtype="S16")
        result = _calculate_distance_for_decoded_profile_pair(
            enum.SeqProfileType.ALLELE, a, b
        )
        assert isinstance(result, float)
        assert result == 1.0

    @pytest.mark.parametrize(
        "flags",
        [
            {"use_numpy_allele": False, "use_batch_new_profiles": True},
            {"use_numpy_allele": False, "use_int32_vocab": True},
            {
                "use_numpy_allele": True,
                "use_batch_new_profiles": True,
                "use_int32_vocab": True,
            },
        ],
    )
    def test_flag_validation_error(self, flags: dict) -> None:
        """Each invalid variant-flag combination raises ValueError."""
        protocol = self._allele_protocol()
        with pytest.raises(ValueError):
            _calculate_and_store_distances(
                self.service,
                Mock(),
                None,
                protocol,
                enum.SeqProfileType.ALLELE,
                [],
                [],
                **flags,
            )

    def test_calculate_and_store_distances_numpy_batch(self) -> None:
        """numpy_batch path stores correct cross and intra-batch distances."""
        a1 = UUID("aaaaaaaa-0000-0000-0000-000000000001")
        a2 = UUID("aaaaaaaa-0000-0000-0000-000000000002")
        # existing [a1,a2]; n1 [a1,a1] → 1 diff; n2 [a2,a2] → 1 diff; n1 vs n2 → 2
        recorder, e_ids, n_ids = self._run_allele_numpy_calc(
            existing_allele_ids_list=[[a1, a2]],
            new_allele_ids_list=[[a1, a1], [a2, a2]],
            use_batch_new_profiles=True,
        )
        e1_id, n1_id, n2_id = e_ids[0], n_ids[0], n_ids[1]
        n1_map = json.loads(
            next(c for c in recorder.created if c.seq_profile_id == n1_id).content
        )
        n2_map = json.loads(
            next(c for c in recorder.created if c.seq_profile_id == n2_id).content
        )
        updated_map = json.loads(recorder.updated[0].content)

        assert len(recorder.created) == 2
        assert len(recorder.updated) == 1
        assert n1_map[str(e1_id)] == 1.0
        assert n2_map[str(e1_id)] == 1.0
        assert updated_map[str(n1_id)] == 1.0
        assert updated_map[str(n2_id)] == 1.0
        assert n1_map[str(n2_id)] == 2.0
        assert n2_map[str(n1_id)] == 2.0

    def test_calculate_and_store_distances_int32_vocab(self) -> None:
        """int32_vocab path produces identical distances to numpy_batch."""
        a1 = UUID("aaaaaaaa-0000-0000-0000-000000000001")
        a2 = UUID("aaaaaaaa-0000-0000-0000-000000000002")
        recorder, e_ids, n_ids = self._run_allele_numpy_calc(
            existing_allele_ids_list=[[a1, a2]],
            new_allele_ids_list=[[a1, a1], [a2, a2]],
            use_int32_vocab=True,
        )
        e1_id, n1_id, n2_id = e_ids[0], n_ids[0], n_ids[1]
        n1_map = json.loads(
            next(c for c in recorder.created if c.seq_profile_id == n1_id).content
        )
        n2_map = json.loads(
            next(c for c in recorder.created if c.seq_profile_id == n2_id).content
        )
        updated_map = json.loads(recorder.updated[0].content)

        assert len(recorder.created) == 2
        assert len(recorder.updated) == 1
        assert n1_map[str(e1_id)] == 1.0
        assert n2_map[str(e1_id)] == 1.0
        assert updated_map[str(n1_id)] == 1.0
        assert updated_map[str(n2_id)] == 1.0
        assert n1_map[str(n2_id)] == 2.0
        assert n2_map[str(n1_id)] == 2.0

    def test_pairwise_reuses_decoded_profiles_no_redecode(self) -> None:
        """When decoded_profiles is supplied, _calculate_pairwise_profile_distances
        uses them directly and does not call _decode_profile."""
        a1 = UUID("aaaaaaaa-0000-0000-0000-000000000001")
        a2 = UUID("aaaaaaaa-0000-0000-0000-000000000002")
        p1_id, p2_id = uuid4(), uuid4()
        p1 = _make_allele_profile(
            profile_id=p1_id,
            sample_id=self.sample_id,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[a1, a2],
        )
        p2 = _make_allele_profile(
            profile_id=p2_id,
            sample_id=self.sample_id2,
            locus_set_id=self.locus_set_id,
            protocol_id=self.protocol_id,
            allele_ids=[a2, a2],  # 1 diff at locus 0
        )
        decoded_p1 = _decode_profile(enum.SeqProfileType.ALLELE, p1, use_numpy_allele=True)
        decoded_p2 = _decode_profile(enum.SeqProfileType.ALLELE, p2, use_numpy_allele=True)
        distance_maps: dict[UUID, dict[str, float]] = {p1_id: {}, p2_id: {}}

        with patch(
            "gen_epix.seqdb.services.seq.calculate_seq_distance._decode_profile"
        ) as mock_decode:
            _calculate_pairwise_profile_distances(
                enum.SeqProfileType.ALLELE,
                [p1, p2],
                distance_maps,
                max_stored_distance=100.0,
                decoded_profiles=[decoded_p1, decoded_p2],
            )
        mock_decode.assert_not_called()
        assert distance_maps[p1_id][str(p2_id)] == 1.0
        assert distance_maps[p2_id][str(p1_id)] == 1.0

    @pytest.mark.parametrize(
        "n_new,exp_batch,exp_int32",
        [
            (2, True, False),   # below gate → numpy_batch
            (3, False, True),   # at gate → int32_vocab
        ],
    )
    def test_gate_selects_variant_by_n_new(
        self, n_new: int, exp_batch: bool, exp_int32: bool
    ) -> None:
        """Gate chooses use_batch_new_profiles below _INT32_VOCAB_GATE and
        use_int32_vocab at or above it."""
        protocol = self._allele_protocol()
        self.service.repository.crud.side_effect = _make_crud_side_effect(
            recorder=_CrudRecorder(), protocols=[protocol]
        )
        a1 = uuid4()
        profiles = [
            _make_allele_profile(
                profile_id=uuid4(),
                sample_id=self.sample_id2,
                locus_set_id=self.locus_set_id,
                protocol_id=self.protocol_id,
                allele_ids=[a1],
            )
            for _ in range(n_new)
        ]
        cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=self.user,
            seq_profiles=profiles,
            use_numpy_allele_distance=True,
        )
        with (
            patch(
                "gen_epix.seqdb.services.seq.calculate_seq_distance._INT32_VOCAB_GATE",
                3,
            ),
            patch(
                "gen_epix.seqdb.services.seq.calculate_seq_distance._calculate_and_store_distances"
            ) as mock_calc,
        ):
            seq_service_calculate_seq_distances_for_new_profiles(self.service, cmd)

        mock_calc.assert_called_once()
        kw = mock_calc.call_args.kwargs
        assert kw["use_batch_new_profiles"] == exp_batch
        assert kw["use_int32_vocab"] == exp_int32
        assert kw["use_numpy_allele"]
