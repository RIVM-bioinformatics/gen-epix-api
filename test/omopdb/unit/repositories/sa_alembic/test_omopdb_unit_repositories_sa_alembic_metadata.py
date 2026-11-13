"""Unit tests for Alembic metadata collection and normalization."""

from types import SimpleNamespace

import sqlalchemy as sa

from gen_epix.omopdb.repositories.sa_alembic import metadata as metadata_module


def test_get_target_metadata_deduplicates_and_ignores_non_model_values(monkeypatch):
    """Keep one metadata object per mapped model registry."""
    first_metadata = sa.MetaData()
    second_metadata = sa.MetaData()
    first_model = type("FirstModel", (), {"metadata": first_metadata})
    duplicate_model = type("DuplicateModel", (), {"metadata": first_metadata})
    second_model = type("SecondModel", (), {"metadata": second_metadata})
    model_without_metadata = type("ModelWithoutMetadata", (), {})
    model_with_invalid_metadata = type(
        "ModelWithInvalidMetadata", (), {"metadata": object()}
    )

    monkeypatch.setattr(
        metadata_module,
        "sa_model",
        SimpleNamespace(
            first=first_model,
            duplicate=duplicate_model,
            second=second_model,
            without_metadata=model_without_metadata,
            invalid_metadata=model_with_invalid_metadata,
            non_model=first_metadata,
        ),
    )

    # pylint: disable=protected-access
    assert metadata_module._get_target_metadata() == (first_metadata, second_metadata)


def test_get_target_metadata_returns_empty_when_no_models_are_exported(monkeypatch):
    """Return an empty tuple when the model registry exports no classes."""
    monkeypatch.setattr(metadata_module, "sa_model", SimpleNamespace())

    # pylint: disable=protected-access
    assert not metadata_module._get_target_metadata()


def test_target_metadata_primary_keys_are_non_nullable():
    """Expose the SQL Server primary-key nullability invariant to Alembic."""
    primary_key_columns = [
        column
        for metadata in metadata_module.target_metadata
        for table in metadata.tables.values()
        for column in table.primary_key.columns
    ]

    assert primary_key_columns
    assert all(not column.nullable for column in primary_key_columns)
