"""Tests for sequence retrieval in the SQLAlchemy repository."""

import json
from datetime import datetime, timezone
from test.seqdb.unit.repositories.seq_fasta_test_support import (
    create_seq,
    expected_fasta,
)
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from gen_epix.fastapp import exc
from gen_epix.fastapp.repositories.sa import SAUnitOfWork
from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.repositories.seq_sa import SeqSARepository


class FakeSession:
    def __init__(self, results: list[list[tuple[Any, ...]]] | None = None) -> None:
        self.results = list(results or [])
        self.queries: list[Any] = []
        self.executions: list[tuple[Any, Any]] = []
        self.bind = SimpleNamespace(dialect=SimpleNamespace(name="sqlite"))
        self.scalar_output: Any = None
        self.scalar_values: list[Any] | None = None

    def execute(self, statement: Any, parameters: Any = None) -> FakeResult:
        self.queries.append(statement)
        self.executions.append((statement, parameters))
        rows = self.results.pop(0) if self.results else []
        return FakeResult(rows, self.scalar_output, self.scalar_values)

    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass

    def close(self) -> None:
        pass

    def get_bind(self) -> SimpleNamespace:
        return self.bind


class FakeMapper:
    def __init__(self, seq: model.Seq) -> None:
        self.seq = seq

    def load(self, row: object) -> model.Seq:
        del row
        return self.seq


class IdentityMapper:
    def load(self, row: object) -> object:
        return row


class FakeSeqSARepository(SeqSARepository):
    def __init__(self, session: FakeSession, mapper: Any | None = None) -> None:
        self.session = session
        self.mapper = mapper or IdentityMapper()

    def uow(self, **kwargs: Any) -> SAUnitOfWork:
        del kwargs
        return create_uow(self.session)

    def get_mapper(self, model_class: type[model.Model]) -> Any:
        del model_class
        return self.mapper


class FakeResult:
    def __init__(
        self,
        rows: list[tuple[Any, ...]],
        scalar_output: Any = None,
        scalar_values: list[Any] | None = None,
    ) -> None:
        self.rows = rows
        self.scalar_output = scalar_output
        self.scalar_values = scalar_values

    def __iter__(self) -> Any:
        return iter(self.rows)

    def scalar(self) -> Any:
        return self.scalar_output

    def scalars(self) -> FakeResult:
        return self

    def all(self) -> list[Any]:
        if self.scalar_values is not None:
            return self.scalar_values
        return [row[0] for row in self.rows]


def create_repository(session: FakeSession) -> FakeSeqSARepository:
    return FakeSeqSARepository(session)


def create_uow(session: FakeSession) -> SAUnitOfWork:
    return SAUnitOfWork(cast(Session, session))


def test_retrieve_seq_fasta_decodes_compressed_contig() -> None:
    sequence = "ATCGATCG"
    seq = create_seq(sequence, enum.SeqFormat.STR_DNA_GZB64)
    repository = FakeSeqSARepository(FakeSession([[(object(),)]]), FakeMapper(seq))
    uow = create_uow(repository.session)

    result = list(repository.retrieve_seq_fasta(uow, [seq.id]))  # type: ignore[list-item]

    assert result == expected_fasta(seq, sequence)


def test_retrieve_seq_fasta_rejects_duplicate_ids() -> None:
    session = FakeSession()
    repository = create_repository(session)
    seq_id = uuid4()

    with pytest.raises(exc.DuplicateIdsError) as error:
        list(repository.retrieve_seq_fasta(create_uow(session), [seq_id, seq_id]))

    assert error.value.ids == [seq_id]
    assert session.queries == []


def test_retrieve_seq_fasta_rejects_non_dna_contig() -> None:
    seq = SimpleNamespace(
        id=uuid4(),
        contigs=[SimpleNamespace(seq_format=enum.SeqFormat.HASH_ONLY)],
    )
    session = FakeSession([[(object(),)]])
    repository = FakeSeqSARepository(session, FakeMapper(cast(model.Seq, seq)))

    with pytest.raises(exc.InitializationServiceError, match="6672c6dd"):
        list(repository.retrieve_seq_fasta(create_uow(session), [seq.id]))


def test_get_full_samples_by_sample_ids_returns_requested_samples() -> None:
    sample_ids = [uuid4(), uuid4()]
    samples = [
        model.Sample(id=sample_id, created_in_data_collection_id=uuid4())
        for sample_id in sample_ids
    ]
    session = FakeSession([[(sample,) for sample in samples]])
    repository = create_repository(session)

    result = repository.get_full_samples_by_sample_ids(sample_ids)

    assert [full_sample.id for full_sample in result] == sample_ids
    assert [full_sample.sample for full_sample in result] == samples
    assert (
        len(session.queries)
        == len(model.FullSample.DATA_CLASSES)
        + len(model.FullSample.IDENTIFIER_CLASSES)
        + 2
    )


def test_get_full_samples_by_sample_ids_raises_for_missing_ids() -> None:
    existing_id, missing_id = uuid4(), uuid4()
    sample_ids = [existing_id, missing_id]
    sample = model.Sample(id=existing_id, created_in_data_collection_id=uuid4())
    session = FakeSession([[(sample,)]])
    repository = create_repository(session)

    with pytest.raises(exc.InvalidIdsError, match="eca0e66d") as error:
        repository.get_full_samples_by_sample_ids(sample_ids)

    assert error.value.ids == [missing_id]


def test_get_full_samples_by_sample_ids_returns_empty_for_empty_input() -> None:
    repository = create_repository(FakeSession())

    assert repository.get_full_samples_by_sample_ids([]) == []


def test_get_sample_ids_modified_in_range_deduplicates_and_sorts() -> None:
    first_id, second_id = uuid4(), uuid4()
    expected = sorted({first_id, second_id})
    result_rows = [[(first_id,), (second_id,), (first_id,)]]
    session = FakeSession(result_rows * (len(model.FullSample.DATA_CLASSES) + 1))
    repository = create_repository(session)

    result = repository.get_sample_ids_modified_in_range(
        create_uow(session),
    )

    assert result == expected


@pytest.mark.parametrize(
    ("modified_since", "modified_until", "expected_conditions"),
    [
        (None, None, 0),
        (datetime(2024, 1, 1, tzinfo=timezone.utc), None, 1),
        (None, datetime(2024, 2, 1, tzinfo=timezone.utc), 1),
        (
            datetime(2024, 1, 1, tzinfo=timezone.utc),
            datetime(2024, 2, 1, tzinfo=timezone.utc),
            2,
        ),
    ],
    ids=["unbounded", "lower-bound", "upper-bound", "bounded"],
)
def test_get_sample_ids_modified_in_range_applies_optional_bounds(
    modified_since: datetime | None,
    modified_until: datetime | None,
    expected_conditions: int,
) -> None:
    session = FakeSession([[]] * (len(model.FullSample.DATA_CLASSES) + 1))
    repository = create_repository(session)

    assert (
        repository.get_sample_ids_modified_in_range(
            create_uow(session), modified_since, modified_until
        )
        == []
    )
    assert all(
        len(statement._where_criteria) == expected_conditions
        for statement in session.queries
    )


def test_retrieve_similar_profiles_includes_threshold_and_excludes_sources() -> None:
    source_id, matching_id, distant_id = uuid4(), uuid4(), uuid4()
    distances = {str(matching_id): 2, str(distant_id): 3}
    session = FakeSession(
        [
            [
                (
                    uuid4(),
                    enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
                    json.dumps(distances),
                    None,
                )
            ]
        ]
    )
    repository = create_repository(session)

    result = repository.retrieve_similar_profiles(
        create_uow(session), uuid4(), [source_id], 2
    )

    assert result == [matching_id]


def test_retrieve_similar_profiles_returns_empty_without_sources() -> None:
    session = FakeSession()
    repository = create_repository(session)

    assert (
        repository.retrieve_similar_profiles(create_uow(session), uuid4(), [], 1) == []
    )
    assert session.queries == []


def test_retrieve_similar_profiles_uses_mssql_temp_table(monkeypatch: Any) -> None:
    source_id, matching_id = uuid4(), uuid4()
    distances = json.dumps({str(matching_id): 0})
    session = FakeSession(
        [[(uuid4(), enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP, distances, None)]]
    )
    session.bind.dialect.name = "mssql"
    repository = create_repository(session)
    temp_tables: list[str] = []

    def create_temp_table(*args: Any) -> sa.TableClause:
        temp_tables.append(args[2])
        return sa.table("requested_ids", sa.column(args[2]))

    monkeypatch.setattr(
        repository, "create_unique_values_temp_table", create_temp_table
    )

    result = repository.retrieve_similar_profiles(
        create_uow(session), uuid4(), [source_id], 0
    )

    assert result == [matching_id]
    assert temp_tables == ["seq_profile_id"]


def test_iter_seq_distances_uses_mssql_temp_table(monkeypatch: Any) -> None:
    distance = object()
    session = FakeSession([[(distance,)]])
    session.bind.dialect.name = "mssql"
    repository = create_repository(session)
    temp_tables: list[str] = []

    def create_temp_table(*args: Any) -> sa.TableClause:
        temp_tables.append(args[2])
        return sa.table("requested_ids", sa.column(args[2]))

    monkeypatch.setattr(
        repository, "create_unique_values_temp_table", create_temp_table
    )

    result = list(
        repository.iter_seq_distances(create_uow(session), uuid4(), [uuid4()])
    )

    assert result == [distance]
    assert temp_tables == ["seq_profile_id"]


def test_iter_seq_distances_empty_filter_does_not_query() -> None:
    session = FakeSession()
    repository = create_repository(session)

    assert list(repository.iter_seq_distances(create_uow(session), uuid4(), [])) == []
    assert session.queries == []


def test_iter_seq_distances_maps_rows_with_optional_filter() -> None:
    first_distance, second_distance = object(), object()
    session = FakeSession([[(first_distance,), (second_distance,)]])
    repository = create_repository(session)

    result = list(
        repository.iter_seq_distances(create_uow(session), uuid4(), [uuid4()])
    )

    assert result == [first_distance, second_distance]


def test_iter_seq_distances_without_filter_maps_rows() -> None:
    distance = object()
    session = FakeSession([[(distance,)]])
    repository = create_repository(session)

    assert list(repository.iter_seq_distances(create_uow(session), uuid4())) == [
        distance
    ]


def test_iter_seq_distance_profile_ids_yields_rows() -> None:
    profile_ids = [uuid4(), uuid4()]
    session = FakeSession([[(profile_id,) for profile_id in profile_ids]])
    repository = create_repository(session)

    assert (
        list(repository.iter_seq_distance_profile_ids(create_uow(session), uuid4()))
        == profile_ids
    )


def test_get_max_seq_distance_modified_at_returns_scalar() -> None:
    modified_at = object()
    session = FakeSession()
    session.scalar_output = modified_at
    repository = create_repository(session)

    assert (
        repository.get_max_seq_distance_modified_at(create_uow(session), uuid4())
        is modified_at
    )


def test_get_max_seq_distance_modified_at_returns_none_without_rows() -> None:
    session = FakeSession()
    repository = create_repository(session)

    assert (
        repository.get_max_seq_distance_modified_at(create_uow(session), uuid4())
        is None
    )


def test_update_some_seq_distance_content_skips_empty_batch() -> None:
    session = FakeSession()
    repository = create_repository(session)

    repository.update_some_seq_distance_content(create_uow(session), None, [])

    assert session.queries == []


@pytest.mark.parametrize("user_id", [None, uuid4()], ids=["no-user", "user"])
def test_update_some_seq_distance_content_batches_values(user_id: Any) -> None:
    seq_distance_id = uuid4()
    obj = cast(
        model.SeqDistance, SimpleNamespace(id=seq_distance_id, content="updated")
    )
    session = FakeSession()
    repository = create_repository(session)

    repository.update_some_seq_distance_content(create_uow(session), user_id, [obj])

    assert len(session.executions) == 1
    assert session.executions[0][1] == [
        {
            "b_id": seq_distance_id,
            "b_content": "updated",
            "b_modified_by": user_id.bytes if user_id is not None else None,
        }
    ]


def test_get_profiles_without_seq_distance_returns_empty_for_empty_protocols() -> None:
    session = FakeSession()
    repository = create_repository(session)

    assert (
        repository.get_profiles_without_seq_distance(create_uow(session), uuid4(), [])
        == []
    )
    assert session.queries == []


def test_get_profiles_without_seq_distance_applies_limit() -> None:
    profiles = [object(), object()]
    session = FakeSession([[(profile,) for profile in profiles]])
    repository = create_repository(session)

    result = repository.get_profiles_without_seq_distance(
        create_uow(session), uuid4(), [uuid4()], limit=1
    )

    assert result == profiles
    assert "LIMIT" in str(session.queries[0]).upper()


def test_get_profiles_without_seq_distance_uses_mssql_temp_table(
    monkeypatch: Any,
) -> None:
    profile = object()
    session = FakeSession([[(profile,)]])
    session.bind.dialect.name = "mssql"
    repository = create_repository(session)
    temp_tables: list[str] = []

    def create_temp_table(*args: Any) -> sa.TableClause:
        temp_tables.append(args[2])
        return sa.table("requested_ids", sa.column(args[2]))

    monkeypatch.setattr(
        repository, "create_unique_values_temp_table", create_temp_table
    )

    result = repository.get_profiles_without_seq_distance(
        create_uow(session), uuid4(), [uuid4()]
    )

    assert result == [profile]
    assert temp_tables == ["protocol_id"]


def test_get_profiles_by_protocol_ids_returns_empty_without_ids() -> None:
    session = FakeSession()
    repository = create_repository(session)

    assert repository.get_profiles_by_protocol_ids(create_uow(session), []) == []
    assert session.queries == []


def test_get_profiles_by_protocol_ids_uses_mssql_temp_table(monkeypatch: Any) -> None:
    profile = object()
    session = FakeSession([[(profile,)]])
    session.bind.dialect.name = "mssql"
    repository = create_repository(session)
    temp_tables: list[str] = []

    def create_temp_table(*args: Any) -> sa.TableClause:
        temp_tables.append(args[2])
        return sa.table("requested_ids", sa.column(args[2]))

    monkeypatch.setattr(
        repository, "create_unique_values_temp_table", create_temp_table
    )

    result = repository.get_profiles_by_protocol_ids(create_uow(session), [uuid4()])

    assert result == [profile]
    assert temp_tables == ["protocol_id"]


def test_get_profiles_by_protocol_ids_uses_in_filter_for_sqlite() -> None:
    profile = object()
    session = FakeSession([[(profile,)]])
    repository = create_repository(session)

    assert repository.get_profiles_by_protocol_ids(create_uow(session), [uuid4()]) == [
        profile
    ]
    assert "IN" in str(session.queries[0]).upper()


@pytest.mark.parametrize(
    ("profile_ids", "allowed_results"),
    [([], enum.QualityControlResultSet.USABLE.value), ([uuid4()], frozenset())],
    ids=["no-profiles", "no-allowed-results"],
)
def test_filter_seq_profiles_by_quality_returns_empty_for_empty_inputs(
    profile_ids: list[Any], allowed_results: Any
) -> None:
    session = FakeSession()
    repository = create_repository(session)

    assert (
        repository.filter_seq_profiles_by_quality(
            create_uow(session), profile_ids, allowed_results
        )
        == []
    )
    assert session.queries == []


def test_filter_seq_profiles_by_quality_returns_scalar_ids() -> None:
    profile_ids = [uuid4(), uuid4()]
    session = FakeSession()
    session.scalar_values = profile_ids
    repository = create_repository(session)

    assert (
        repository.filter_seq_profiles_by_quality(create_uow(session), profile_ids)
        == profile_ids
    )
