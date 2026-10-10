"""Test SQLAlchemy metadata discovery for SeqDB migrations."""

from types import SimpleNamespace

import sqlalchemy as sa

from gen_epix.seqdb.repositories.sa_alembic import metadata


def test_get_target_metadata_deduplicates_and_preserves_model_order(monkeypatch):
    """Collect each model metadata once in the order it is first encountered."""
    first_metadata = sa.MetaData()
    second_metadata = sa.MetaData()
    first_model = type("FirstModel", (), {"metadata": first_metadata})
    metadata_alias = type("MetadataAlias", (), {"metadata": first_metadata})
    second_model = type("SecondModel", (), {"metadata": second_metadata})
    invalid_metadata = type("InvalidMetadata", (), {"metadata": object()})

    monkeypatch.setattr(
        metadata,
        "sa_model",
        SimpleNamespace(
            FirstModel=first_model,
            MetadataAlias=metadata_alias,
            non_class=first_metadata,
            InvalidMetadata=invalid_metadata,
            SecondModel=second_model,
        ),
    )

    get_target_metadata = vars(metadata)["_get_target_metadata"]
    assert get_target_metadata() == (first_metadata, second_metadata)


def test_get_target_metadata_returns_empty_tuple_without_mapped_models(monkeypatch):
    """Return no metadata when the exported namespace has no mapped classes."""
    monkeypatch.setattr(metadata, "sa_model", SimpleNamespace())

    get_target_metadata = vars(metadata)["_get_target_metadata"]
    result = get_target_metadata()
    assert isinstance(result, tuple)
    assert not result
