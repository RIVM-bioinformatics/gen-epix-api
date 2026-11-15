"""Verify SQLAlchemy mapper argument construction."""

from types import SimpleNamespace

from gen_epix.commondb.repositories.sa_model.util import (
    create_composite_primary_key_mapper_args,
)


def test_composite_key_mapper_args_preserve_other_options() -> None:
    """Retain caller mapper options alongside the derived primary key."""
    model_class = type(
        "TestModel",
        (),
        {"ENTITY": SimpleNamespace(get_field_names=lambda: ["code", "name"])},
    )

    result = create_composite_primary_key_mapper_args(
        model_class, mapper_args={"eager_defaults": True}
    )

    assert result == {"eager_defaults": True, "primary_key": ["code", "name"]}
