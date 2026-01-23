from test.general.docs.test_model_field_descriptions import is_model_class
from typing import Any

import pytest
from pydantic import BaseModel

from gen_epix.casedb import api as casedb_api
from gen_epix.casedb.domain import model as casedb_model
from gen_epix.commondb import api as commondb_api
from gen_epix.commondb.domain import model as commondb_model
from gen_epix.omopdb import api as omopdb_api
from gen_epix.omopdb.domain import model as omopdb_model
from gen_epix.seqdb import api as seqdb_api
from gen_epix.seqdb.domain import model as seqdb_model

# set to false to only print the missing max_length fields without failing the test
SHOULD_FAIL = True


def _is_iterable_type(field_type: Any) -> bool:
    """Check if the given field type is an iterable type (like List, Set, Tuple, etc.)"""
    origin = getattr(field_type, "__origin__", None)
    return origin in {list, set, tuple, frozenset}


@pytest.mark.scenario_ids("TC-SEC-28-08")
def test_model_field_properties() -> None:
    """test if domain and request body models have a max_length for all iterable properties."""

    domains = [
        commondb_model,
        casedb_model,
        seqdb_model,
        omopdb_model,
        casedb_api,
        commondb_api,
        omopdb_api,
        seqdb_api,
    ]

    for domain in domains:
        model_classes = [x for x in vars(domain).values() if is_model_class(x)]
        assert (
            model_classes
        ), f"no model classes discovered in domain module {domain.__name__}"

        for model_class in model_classes:
            if not issubclass(model_class, BaseModel):
                continue

            for field_name, field_info in model_class.model_fields.items():
                if _is_iterable_type(field_info.annotation):
                    max_length = None
                    try:
                        max_length = field_info.field_info.max_length  # type: ignore[attr-defined]
                    except AttributeError:
                        message: str = (
                            f"{domain.__name__}.{model_class.__name__}.{field_name} is an iterable type but has no max_length defined in Field(...)"
                        )
                        if SHOULD_FAIL:
                            pytest.fail(message)
                        else:
                            print(message)
                    if not max_length is None:
                        assert (
                            max_length is not None
                        ), f"{domain.__name__}.{model_class.__name__}.{field_name} is an iterable type but has no max_length defined in Field(...)"
                        assert (
                            max_length > 0
                        ), f"{domain.__name__}.{model_class.__name__}.{field_name} has invalid max_length={max_length}, must be > 0"
