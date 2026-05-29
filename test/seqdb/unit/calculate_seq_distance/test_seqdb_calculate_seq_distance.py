import json
from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from typing import Any
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import EtlStatus, Role
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.exc import ConcurrentModificationError
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.literal import MLVA_NO_LOCUS_REPEAT_NUMBER
from gen_epix.seqdb.services.seq.calculate_seq_distance import (
    _calculate_and_store_distances,
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

    Pass recorder to also mock bulk_update_seq_distance_content
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
        def _bulk_update(
            uow: Any, user_id: Any, objs: list[model.SeqDistance]
        ) -> None:
            recorder.updated.extend(objs)
        service_mock.repository.bulk_update_seq_distance_content = Mock(
            side_effect=_bulk_update,
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
        _setup_distance_mocks(self.service, [existing_seq_distance])

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
        self.service.repository.get_profiles_by_protocol_ids = Mock(
            return_value=[existing_profile],
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
        self.service.repository.get_profiles_by_protocol_ids = Mock(
            return_value=[
                existing_profile,
                missing_profile,
            ],
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
