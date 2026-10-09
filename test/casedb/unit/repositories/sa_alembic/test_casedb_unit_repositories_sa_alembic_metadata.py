import sqlalchemy as sa

from gen_epix.casedb.repositories.sa_alembic import metadata


def test_get_target_metadata_collects_unique_model_metadata(monkeypatch):
    existing_metadata = metadata._get_target_metadata()
    shared_metadata = sa.MetaData()
    additional_metadata = sa.MetaData()
    model_with_shared_metadata = type(
        "ModelWithSharedMetadata", (), {"metadata": shared_metadata}
    )
    another_model_with_shared_metadata = type(
        "AnotherModelWithSharedMetadata", (), {"metadata": shared_metadata}
    )
    model_with_additional_metadata = type(
        "ModelWithAdditionalMetadata", (), {"metadata": additional_metadata}
    )
    model_with_invalid_metadata = type(
        "ModelWithInvalidMetadata", (), {"metadata": object()}
    )

    monkeypatch.setattr(
        metadata.sa_model,
        "_metadata_test_model_a",
        model_with_shared_metadata,
        raising=False,
    )
    monkeypatch.setattr(
        metadata.sa_model,
        "_metadata_test_model_b",
        another_model_with_shared_metadata,
        raising=False,
    )
    monkeypatch.setattr(
        metadata.sa_model,
        "_metadata_test_model_c",
        model_with_additional_metadata,
        raising=False,
    )
    monkeypatch.setattr(
        metadata.sa_model,
        "_metadata_test_model_d",
        model_with_invalid_metadata,
        raising=False,
    )
    monkeypatch.setattr(
        metadata.sa_model, "_metadata_test_value", sa.MetaData(), raising=False
    )

    assert metadata._get_target_metadata() == (
        *existing_metadata,
        shared_metadata,
        additional_metadata,
    )


def test_target_metadata_is_initialized_from_model_exports():
    assert metadata.target_metadata == metadata._get_target_metadata()
