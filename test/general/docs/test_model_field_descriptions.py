from typing import Any

from gen_epix.casedb.domain import model as casedb_model
from gen_epix.commondb.domain import model as commondb_model
from gen_epix.omopdb.domain import model as omopdb_model
from gen_epix.seqdb.domain import model as seqdb_model


def is_model_class(obj: Any) -> bool:
    return isinstance(obj, type) and hasattr(obj, "model_fields")


def test_model_field_descriptions() -> None:
    """Ensure every model field (including computed fields) has a non-empty description."""
    domains = [
        commondb_model,
        casedb_model,
        seqdb_model,
        omopdb_model,
    ]

    for domain in domains:
        model_classes = [x for x in vars(domain).values() if is_model_class(x)]
        assert (
            model_classes
        ), f"no model classes discovered in domain module {domain.__name__}"

        for model_class in model_classes:
            fields: dict[str, Any] = {}
            fields.update(getattr(model_class, "model_fields", {}) or {})
            fields.update(getattr(model_class, "model_computed_fields", {}) or {})

            for field_name, field_info in fields.items():
                desc = getattr(field_info, "description", None)
                assert (
                    desc is not None
                ), f"{domain.__name__}.{model_class.__name__}.{field_name} has no description, add Field(description=...)"
                assert (
                    str(desc).strip() != ""
                ), f"{domain.__name__}.{model_class.__name__}.{field_name} description is empty"
