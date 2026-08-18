import json
from typing import Any
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain import exc as casedb_exc
from gen_epix.casedb.domain.model.case.ref_data import (
    CaseType,
    CaseTypeProps,
    CaseTypeSetCategory,
    Col,
    GeneticDistanceProtocol,
    RefCol,
    RefDim,
    TreeAlgorithm,
)
from gen_epix.seqdb.domain import enum as seqdb_enum


def _valid_ref_col_kwargs() -> dict[str, Any]:
    return {
        "ref_dim_id": uuid4(),
        "code": "col.code",
        "col_type": enum.ColType.TEXT,
    }


def _assert_invalid_arguments_error_code(
    kwargs: dict[str, Any], expected_code: str
) -> None:
    with pytest.raises(casedb_exc.InvalidArgumentsError) as excinfo:
        RefCol(**kwargs)
    assert expected_code in str(excinfo.value)


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestModelCaseRefData:
    def test_genetic_distance_protocol_validator_and_serializer(self) -> None:
        obj = GeneticDistanceProtocol.model_validate_json(
            json.dumps(
                {
                    "seqdb_seq_distance_protocol_id": str(uuid4()),
                    "seqdb_seq_distance_type": "SNP_HAMMING",
                    "name": "proto",
                    "seqdb_is_integer_distance": True,
                    "min_scale_unit": 1.0,
                }
            )
        )
        dumped = obj.model_dump()
        assert dumped["seqdb_seq_distance_type"] == 1

    def test_tree_algorithm_validator_and_serializer(self) -> None:
        tree = TreeAlgorithm(
            tree_algorithm_class_id=uuid4(),
            seqdb_tree_algorithm_id=uuid4(),
            code=enum.TreeAlgorithmType.NJ,
            name="Neighbor joining",
            is_ultrametric=False,
        )
        dumped = tree.model_dump()
        assert tree.code == enum.TreeAlgorithmType.NJ
        assert dumped["code"] == "NJ"

    def test_ref_dim_code_and_dim_type_serialization(self) -> None:
        ref_dim = RefDim.model_validate(
            {"dim_type": "TEXT", "code": 42, "label": "Label"}
        )
        dumped = ref_dim.model_dump()
        assert ref_dim.code == "42"
        assert dumped["dim_type"] == "TEXT"

    @pytest.mark.parametrize(
        ("overrides", "expected_code"),
        [
            ({"col_type": enum.ColType.DECIMAL_1}, "0b6c1a3a"),
            (
                {"col_type": enum.ColType.TEXT, "unit": enum.Unit.DAY},
                "29bdfe0d",
            ),
            ({"col_type": enum.ColType.NOMINAL}, "00437e28"),
            ({"col_type": enum.ColType.TEXT, "concept_set_id": uuid4()}, "6357f6c4"),
            ({"col_type": enum.ColType.GEO_REGION}, "3b16f972"),
            ({"col_type": enum.ColType.TEXT, "region_set_id": uuid4()}, "902946f9"),
            ({"col_type": enum.ColType.GENETIC_DISTANCE}, "b1f2639c"),
            (
                {
                    "col_type": enum.ColType.TEXT,
                    "genetic_distance_protocol_id": uuid4(),
                },
                "23db92a4",
            ),
            ({"col_type": enum.ColType.REGULAR_LANGUAGE}, "0728233a"),
            ({"col_type": enum.ColType.TEXT, "regex": ".*"}, "dee07f88"),
            ({"col_type": enum.ColType.CONTEXT_FREE_GRAMMAR_JSON}, "4f3501ad"),
            (
                {"col_type": enum.ColType.TEXT, "schema_definition": "{...}"},
                "4bab82b4",
            ),
            (
                {
                    "col_type": enum.ColType.TEXT,
                    "schema_uri": "https://example.org/schema",
                },
                "1b6ba175",
            ),
            (
                {
                    "col_type": enum.ColType.CONTEXT_FREE_GRAMMAR_XML,
                    "schema_definition": "<schema />",
                    "schema_uri": "https://example.org/schema",
                },
                "4dd65d8e",
            ),
        ],
    )
    def test_ref_col_invalid_state_branches(
        self, overrides: dict[str, Any], expected_code: str
    ) -> None:
        kwargs = _valid_ref_col_kwargs()
        kwargs.update(overrides)
        _assert_invalid_arguments_error_code(kwargs, expected_code)

    def test_ref_col_valid_state_and_serializer(self) -> None:
        ref_col = RefCol.model_validate(
            {
                "ref_dim_id": uuid4(),
                "code": 7,
                "col_type": "DECIMAL_2",
                "unit": enum.Unit.DAY,
            }
        )
        dumped = ref_col.model_dump()
        assert ref_col.code == "7"
        assert ref_col.col_type == enum.ColType.DECIMAL_2
        assert dumped["col_type"] == "DECIMAL_2"
        assert dumped["unit"] == "DAY"
        ref_col = RefCol.model_validate(
            {
                "ref_dim_id": uuid4(),
                "code": 8,
                "col_type": "INTERVAL",
                "unit": enum.Unit.YEAR,
            }
        )
        dumped = ref_col.model_dump()
        assert ref_col.code == "8"
        assert ref_col.col_type == enum.ColType.INTERVAL
        assert dumped["col_type"] == "INTERVAL"
        assert dumped["unit"] == "YEAR"

    def test_ref_col_serializer_none_unit(self) -> None:
        ref_col = RefCol(
            ref_dim_id=uuid4(),
            code="abc",
            col_type=enum.ColType.TEXT,
        )
        dumped = ref_col.model_dump()
        assert dumped["unit"] is None

    def test_case_type_props_validator_and_serializer(self) -> None:
        props_obj = CaseTypeProps(read_max_n_cases=5)

        case_type_obj = CaseType(name="ct-a", props=props_obj)
        assert case_type_obj.props.read_max_n_cases == 5

        case_type_dict = CaseType.model_validate(
            {"name": "ct-b", "props": {"read_max_n_cases": 6}}
        )
        assert case_type_dict.props.read_max_n_cases == 6

        case_type_json = CaseType.model_validate(
            {
                "name": "ct-c",
                "props": json.dumps({"read_max_n_cases": 7}),
            }
        )
        assert case_type_json.props.read_max_n_cases == 7

        dumped = case_type_json.model_dump()
        assert dumped["props"]["read_max_n_cases"] == 7

        with pytest.raises(ValueError):
            CaseType.model_validate({"name": "ct-d", "props": 123})

    def test_case_type_set_category_purpose_serializer(self) -> None:
        category = CaseTypeSetCategory(name="security", rank=1)
        dumped = category.model_dump()
        assert dumped["purpose"] == "CONTENT"

    def test_col_code_and_tree_algorithm_code_validators_and_serializers(self) -> None:
        col = Col.model_validate(
            {
                "case_type_id": uuid4(),
                "dim_id": uuid4(),
                "ref_col_id": uuid4(),
                "code": 99,
                "rank": 1,
                "tree_algorithm_codes": '["NJ", "CLINK"]',
            }
        )
        dumped = col.model_dump()
        assert col.code == "99"
        assert col.tree_algorithm_codes == {
            enum.TreeAlgorithmType.NJ,
            enum.TreeAlgorithmType.CLINK,
        }
        assert dumped["tree_algorithm_codes"] == ["CLINK", "NJ"]

    def test_col_tree_algorithm_code_validator_none_and_set(self) -> None:
        base_kwargs = {
            "case_type_id": uuid4(),
            "dim_id": uuid4(),
            "ref_col_id": uuid4(),
            "code": "col",
            "rank": 1,
        }

        col_none = Col(**base_kwargs, tree_algorithm_codes=None)  # type: ignore[arg-type]
        assert col_none.tree_algorithm_codes is None

        codes_set = {enum.TreeAlgorithmType.NJ}
        col_set = Col(**base_kwargs, tree_algorithm_codes=codes_set)  # type: ignore[arg-type]
        assert col_set.tree_algorithm_codes == codes_set

    def test_seq_distance_type_accepts_int_enum_value(self) -> None:
        obj = GeneticDistanceProtocol(
            seqdb_seq_distance_protocol_id=uuid4(),
            seqdb_seq_distance_type=seqdb_enum.SeqDistanceType.MLVA_HAMMING,
            name="proto",
            seqdb_is_integer_distance=False,
            min_scale_unit=2.0,
        )
        assert obj.seqdb_seq_distance_type == seqdb_enum.SeqDistanceType.MLVA_HAMMING

    def test_direct_validator_helper_paths(self) -> None:
        assert TreeAlgorithm._validate_code("NJ") == enum.TreeAlgorithmType.NJ
        assert RefDim._validate_dim_type("TEXT") == enum.DimType.TEXT
        assert RefDim._validate_dim_type(enum.DimType.TEXT) == enum.DimType.TEXT
        assert Col.validate_tree_algorithm_codes([enum.TreeAlgorithmType.NJ]) == {
            enum.TreeAlgorithmType.NJ
        }
