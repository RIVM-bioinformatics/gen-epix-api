import json

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain import model


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestCaseTypeProps:
    def test_default_construction(self) -> None:
        props = model.CaseTypeProps()
        assert props.create_max_n_cases == 0
        assert props.read_max_n_cases == 0
        assert props.read_max_tree_size == 0
        assert props.update_max_n_cases == 0
        assert props.delete_max_n_cases == 0

    def test_explicit_construction(self) -> None:
        props = model.CaseTypeProps(
            create_max_n_cases=10,
            read_max_n_cases=20,
            read_max_tree_size=30,
            update_max_n_cases=40,
            delete_max_n_cases=50,
        )
        assert props.create_max_n_cases == 10
        assert props.read_max_n_cases == 20
        assert props.read_max_tree_size == 30
        assert props.update_max_n_cases == 40
        assert props.delete_max_n_cases == 50

    @pytest.mark.parametrize(
        "field",
        [
            "create_max_n_cases",
            "read_max_n_cases",
            "read_max_tree_size",
            "update_max_n_cases",
            "delete_max_n_cases",
        ],
    )
    def test_negative_value_rejected(self, field: str) -> None:
        with pytest.raises(ValidationError):
            model.CaseTypeProps(**{field: -1})

    def test_zero_is_accepted(self) -> None:
        props = model.CaseTypeProps(
            create_max_n_cases=0,
            read_max_n_cases=0,
            read_max_tree_size=0,
            update_max_n_cases=0,
            delete_max_n_cases=0,
        )
        assert props.read_max_n_cases == 0

    def test_case_type_constructed_with_props(self) -> None:
        props = model.CaseTypeProps(read_max_n_cases=100)
        case_type = model.CaseType(name="TEST", props=props)
        assert case_type.props.read_max_n_cases == 100

    def test_case_type_props_defaults_when_omitted(self) -> None:
        case_type = model.CaseType(name="TEST")
        assert case_type.props.read_max_n_cases == 0

    def test_field_serializer_produces_dict(self) -> None:
        props = model.CaseTypeProps(read_max_n_cases=42)
        case_type = model.CaseType(name="TEST", props=props)
        serialized = case_type.model_dump()
        # props must be a plain dict (JSON-compatible), not a CaseTypeProps instance
        assert isinstance(serialized["props"], dict)
        assert serialized["props"]["read_max_n_cases"] == 42

    def test_round_trip_via_json(self) -> None:
        original = model.CaseTypeProps(
            create_max_n_cases=1,
            read_max_n_cases=2,
            read_max_tree_size=3,
            update_max_n_cases=4,
            delete_max_n_cases=5,
        )
        as_dict = original.model_dump()
        as_json = json.dumps(as_dict)
        restored = model.CaseTypeProps.model_validate(json.loads(as_json))
        assert restored == original
