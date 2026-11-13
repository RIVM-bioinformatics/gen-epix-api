from types import SimpleNamespace

import sqlalchemy as sa

import gen_epix.commondb.repositories.sa_alembic.metadata as metadata_module


def test_get_target_metadata_deduplicates_shared_metadata(monkeypatch):
    shared_metadata = sa.MetaData()
    other_metadata = sa.MetaData()

    class FirstModel:
        metadata = shared_metadata

    class AnotherSharedModel:
        metadata = shared_metadata

    class OtherModel:
        metadata = other_metadata

    class ModelWithoutMetadata:
        metadata = None

    class ModelWithInvalidMetadata:
        metadata = object()

    monkeypatch.setattr(
        metadata_module,
        "sa_model",
        SimpleNamespace(
            alias=FirstModel,
            first=FirstModel,
            another_shared=AnotherSharedModel,
            other=OtherModel,
            without_metadata=ModelWithoutMetadata,
            invalid_metadata=ModelWithInvalidMetadata,
            non_model=object(),
        ),
    )

    result = metadata_module._get_target_metadata()

    assert len(result) == 2
    assert result[0] is shared_metadata
    assert result[1] is other_metadata


def test_get_target_metadata_returns_empty_tuple_without_metadata_classes(monkeypatch):
    class ModelWithoutMetadata:
        metadata = None

    monkeypatch.setattr(
        metadata_module,
        "sa_model",
        SimpleNamespace(
            without_metadata=ModelWithoutMetadata,
            non_model=object(),
        ),
    )

    assert metadata_module._get_target_metadata() == ()
