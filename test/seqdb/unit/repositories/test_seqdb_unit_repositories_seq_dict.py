"""Tests for sequence retrieval in the Dict-backed repository."""

import json
from datetime import datetime
from test.seqdb.unit.repositories.seq_fasta_test_support import (
    create_seq,
    expected_fasta,
)
from uuid import uuid4

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.repositories.seq_dict import SeqDictRepository


def create_repository(
    db: dict | None = None,
    entity_classes: list[type[model.Model]] | None = None,
) -> SeqDictRepository:
    return SeqDictRepository(
        entities=[model_class.ENTITY for model_class in entity_classes or []],
        db=db or {},
        missing_data="ignore",
    )


def create_full_sample_db() -> dict:
    model_classes = [
        model.Sample,
        *model.FullSample.DATA_CLASSES,
        *model.FullSample.IDENTIFIER_CLASSES,
        model.SampleIdentifier,
    ]
    return {model_class: {} for model_class in model_classes}


def create_distance(
    protocol_id: object,
    profile_id: object,
    distances: dict[str, float] | None = None,
    modified_at: datetime | None = None,
) -> model.SeqDistance:
    return model.SeqDistance.model_construct(
        id=uuid4(),
        protocol_id=protocol_id,
        seq_profile_id=profile_id,
        format=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        content=json.dumps(distances or {}),
        content2=None,
        modified_at=modified_at,
    )


def test_retrieve_seq_fasta_decodes_compressed_contig() -> None:
    sequence = "AT-CGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA_INCL_GAP_GZB64)
    repository = SeqDictRepository(
        entities=[model.Seq.ENTITY],
        db={model.Seq: {seq.id: seq}},
        missing_data="ignore",
    )

    with repository.uow() as uow:
        result = list(repository.retrieve_seq_fasta(uow, [seq.id]))  # type: ignore[list-item]

    assert result == expected_fasta(seq, sequence)


def test_get_full_samples_by_sample_ids_raises_for_missing_ids() -> None:
    sample_id = uuid4()
    missing_id = uuid4()
    sample = model.Sample(
        id=sample_id,
        created_in_data_collection_id=uuid4(),
    )
    repository = SeqDictRepository(
        entities=[model.Sample.ENTITY],
        db={model.Sample: {sample_id: sample}},
        missing_data="ignore",
    )

    with pytest.raises(exc.InvalidIdsError, match="e6de62b3") as error:
        repository.get_full_samples_by_sample_ids([sample_id, missing_id])

    assert error.value.ids == [missing_id]


def test_retrieve_seq_fasta_rejects_duplicate_ids() -> None:
    seq_id = uuid4()
    repository = create_repository({model.Seq: {}}, [model.Seq])

    with repository.uow() as uow, pytest.raises(exc.DuplicateIdsError) as error:
        list(repository.retrieve_seq_fasta(uow, [seq_id, seq_id]))

    assert error.value.ids == [seq_id]


def test_retrieve_seq_fasta_rejects_non_dna_contig() -> None:
    seq_id = uuid4()
    seq = model.Seq.model_construct(
        id=seq_id,
        contigs=[
            model.Contig.model_construct(
                id=uuid4(), seq_format=enum.SeqFormat.HASH_ONLY, seq=""
            )
        ],
    )
    repository = create_repository({model.Seq: {seq_id: seq}}, [model.Seq])

    with repository.uow() as uow, pytest.raises(exc.InitializationServiceError):
        list(repository.retrieve_seq_fasta(uow, [seq_id]))


def test_get_sample_ids_modified_in_range_deduplicates_and_applies_bounds() -> None:
    before_range_id, in_range_id, upper_bound_id = uuid4(), uuid4(), uuid4()
    lower_bound = datetime(2024, 1, 1)
    upper_bound = datetime(2024, 2, 1)
    db = create_full_sample_db()
    db[model.Sample] = {
        before_range_id: model.Sample.model_construct(
            id=before_range_id, modified_at=datetime(2023, 12, 31)
        ),
        in_range_id: model.Sample.model_construct(
            id=in_range_id, modified_at=lower_bound
        ),
        upper_bound_id: model.Sample.model_construct(
            id=upper_bound_id, modified_at=upper_bound
        ),
    }
    linked_profile = model.SeqProfile.model_construct(
        id=uuid4(), sample_id=in_range_id, modified_at=datetime(2024, 1, 15)
    )
    db[model.SeqProfile] = {linked_profile.id: linked_profile}
    repository = create_repository(db)

    with repository.uow() as uow:
        result = repository.get_sample_ids_modified_in_range(
            uow, lower_bound, upper_bound
        )

    assert result == [in_range_id]


def test_get_full_samples_by_sample_ids_assembles_linked_records() -> None:
    sample_id = uuid4()
    sample = model.Sample(id=sample_id, created_in_data_collection_id=uuid4())
    seq = create_seq("ATCG", enum.SeqFormat.STR_DNA)
    seq.sample_id = sample_id
    sample_identifier = model.SampleIdentifier(
        identifier_issuer_id=uuid4(), external_id="sample-ext", internal_id=sample_id
    )
    db = create_full_sample_db()
    db[model.Sample] = {sample_id: sample}
    db[model.Seq] = {seq.id: seq}
    db[model.SampleIdentifier] = {sample_identifier.id: sample_identifier}
    repository = create_repository(db)

    result = repository.get_full_samples_by_sample_ids([sample_id])

    assert len(result) == 1
    assert result[0].sample is sample
    assert result[0].seqs == [seq]
    assert result[0].sample_identifiers == [sample_identifier]


def test_get_full_samples_by_sample_ids_returns_empty_for_empty_input() -> None:
    assert (
        create_repository(create_full_sample_db()).get_full_samples_by_sample_ids([])
        == []
    )


def test_retrieve_similar_profiles_filters_protocol_and_distance_threshold() -> None:
    protocol_id = uuid4()
    source_id, included_id, excluded_id, unrelated_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    distances = create_distance(
        protocol_id,
        source_id,
        {str(source_id): 0, str(included_id): 2, str(excluded_id): 3},
    )
    unrelated_profile = create_distance(protocol_id, uuid4(), {str(uuid4()): 0})
    unrelated = create_distance(uuid4(), source_id, {str(unrelated_id): 0})
    repository = create_repository(
        {
            model.SeqDistance: {
                distances.id: distances,
                unrelated_profile.id: unrelated_profile,
                unrelated.id: unrelated,
            }
        }
    )

    with repository.uow() as uow:
        result = repository.retrieve_similar_profiles(
            uow, protocol_id, [source_id], max_distance=2
        )

    assert result == [included_id]


def test_retrieve_similar_profiles_returns_empty_without_source_ids() -> None:
    repository = create_repository({model.SeqDistance: {}})

    with repository.uow() as uow:
        assert repository.retrieve_similar_profiles(uow, uuid4(), [], 1) == []


def test_iter_seq_distances_filters_protocol_and_optional_profile_ids() -> None:
    protocol_id = uuid4()
    selected_id, other_id = uuid4(), uuid4()
    selected = create_distance(protocol_id, selected_id)
    other = create_distance(protocol_id, other_id)
    unrelated = create_distance(uuid4(), selected_id)
    repository = create_repository(
        {
            model.SeqDistance: {
                selected.id: selected,
                other.id: other,
                unrelated.id: unrelated,
            }
        }
    )

    with repository.uow() as uow:
        all_protocol_distances = list(repository.iter_seq_distances(uow, protocol_id))
        selected_distances = list(
            repository.iter_seq_distances(uow, protocol_id, [selected_id])
        )
        no_distances = list(repository.iter_seq_distances(uow, protocol_id, []))

    assert all_protocol_distances == [selected, other]
    assert selected_distances == [selected]
    assert no_distances == []


def test_iter_seq_distance_profile_ids_yields_unique_profile_ids() -> None:
    protocol_id = uuid4()
    first_profile_id, second_profile_id = uuid4(), uuid4()
    distances = [
        create_distance(protocol_id, first_profile_id),
        create_distance(protocol_id, second_profile_id),
        create_distance(protocol_id, first_profile_id),
        create_distance(uuid4(), uuid4()),
    ]
    repository = create_repository(
        {model.SeqDistance: {distance.id: distance for distance in distances}}
    )

    with repository.uow() as uow:
        result = list(repository.iter_seq_distance_profile_ids(uow, protocol_id))

    assert result == [first_profile_id, second_profile_id]


def test_get_max_seq_distance_modified_at_ignores_other_protocol_and_none() -> None:
    protocol_id = uuid4()
    first_modified = datetime(2024, 1, 1)
    latest_modified = datetime(2024, 2, 1)
    distances = [
        create_distance(protocol_id, uuid4(), modified_at=first_modified),
        create_distance(protocol_id, uuid4(), modified_at=latest_modified),
        create_distance(protocol_id, uuid4()),
        create_distance(uuid4(), uuid4(), modified_at=datetime(2025, 1, 1)),
    ]
    repository = create_repository(
        {model.SeqDistance: {distance.id: distance for distance in distances}}
    )

    with repository.uow() as uow:
        result = repository.get_max_seq_distance_modified_at(uow, protocol_id)

    assert result == latest_modified


def test_get_max_seq_distance_modified_at_returns_none_without_timestamps() -> None:
    protocol_id = uuid4()
    distance = create_distance(protocol_id, uuid4())
    repository = create_repository({model.SeqDistance: {distance.id: distance}})

    with repository.uow() as uow:
        result = repository.get_max_seq_distance_modified_at(uow, protocol_id)

    assert result is None


def test_update_some_seq_distance_content_skips_empty_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = create_repository()
    calls: list[tuple[tuple, dict]] = []
    monkeypatch.setattr(
        repository, "crud", lambda *args, **kwargs: calls.append((args, kwargs))
    )

    with repository.uow() as uow:
        repository.update_some_seq_distance_content(uow, None, [])

    assert calls == []


def test_update_some_seq_distance_content_delegates_non_empty_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = create_repository()
    user_id = uuid4()
    distance = create_distance(uuid4(), uuid4())
    calls: list[tuple[tuple, dict]] = []
    monkeypatch.setattr(
        repository, "crud", lambda *args, **kwargs: calls.append((args, kwargs))
    )

    with repository.uow() as uow:
        repository.update_some_seq_distance_content(uow, user_id, [distance])

    assert calls == [
        (
            (uow, user_id, model.SeqDistance, CrudOperation.UPDATE_SOME),
            {"objs": [distance]},
        )
    ]


def test_get_profiles_without_seq_distance_filters_and_applies_limit() -> None:
    profile_protocol_id, distance_protocol_id, other_protocol_id = (
        uuid4(),
        uuid4(),
        uuid4(),
    )
    existing_distance_profile_id = uuid4()
    profiles = [
        model.SeqProfile.model_construct(
            id=existing_distance_profile_id, protocol_id=profile_protocol_id
        ),
        model.SeqProfile.model_construct(id=uuid4(), protocol_id=profile_protocol_id),
        model.SeqProfile.model_construct(id=uuid4(), protocol_id=other_protocol_id),
    ]
    distance = create_distance(distance_protocol_id, existing_distance_profile_id)
    repository = create_repository(
        {
            model.SeqProfile: {profile.id: profile for profile in profiles},
            model.SeqDistance: {distance.id: distance},
        }
    )

    with repository.uow() as uow:
        result = repository.get_profiles_without_seq_distance(
            uow, distance_protocol_id, [profile_protocol_id], limit=1
        )

    assert result == [profiles[1]]


def test_get_profiles_by_protocol_ids_filters_profiles() -> None:
    selected_protocol_id, other_protocol_id = uuid4(), uuid4()
    profiles = [
        model.SeqProfile.model_construct(id=uuid4(), protocol_id=selected_protocol_id),
        model.SeqProfile.model_construct(id=uuid4(), protocol_id=other_protocol_id),
    ]
    repository = create_repository(
        {model.SeqProfile: {profile.id: profile for profile in profiles}}
    )

    with repository.uow() as uow:
        result = repository.get_profiles_by_protocol_ids(uow, [selected_protocol_id])

    assert result == [profiles[0]]


def test_filter_seq_profiles_by_quality_returns_only_allowed_requested_ids() -> None:
    passing_id, warning_id, failing_id, unrequested_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    profiles = [
        model.SeqProfile.model_construct(
            id=passing_id,
            qc_result_machine=enum.QualityControlResult.PASS,
            qc_result_human=enum.QualityControlResult.PENDING,
        ),
        model.SeqProfile.model_construct(
            id=warning_id,
            qc_result_machine=enum.QualityControlResult.FAIL,
            qc_result_human=enum.QualityControlResult.WARN,
        ),
        model.SeqProfile.model_construct(
            id=failing_id,
            qc_result_machine=enum.QualityControlResult.FAIL,
            qc_result_human=enum.QualityControlResult.PENDING,
        ),
        model.SeqProfile.model_construct(
            id=unrequested_id,
            qc_result_machine=enum.QualityControlResult.PASS,
            qc_result_human=enum.QualityControlResult.PENDING,
        ),
        model.SeqProfile.model_construct(
            id=None,
            qc_result_machine=enum.QualityControlResult.PASS,
            qc_result_human=enum.QualityControlResult.PENDING,
        ),
    ]
    repository = create_repository(
        {model.SeqProfile: {uuid4(): profile for profile in profiles}}
    )

    with repository.uow() as uow:
        result = repository.filter_seq_profiles_by_quality(
            uow, [passing_id, warning_id, failing_id]
        )

    assert set(result) == {passing_id, warning_id}
