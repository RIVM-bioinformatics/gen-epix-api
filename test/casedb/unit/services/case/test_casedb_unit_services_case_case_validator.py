from __future__ import annotations

from test.util.mock_compat import MagicMock
from typing import Any, NoReturn, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.model.case.upload import CaseBatchUploadResult
from gen_epix.casedb.services.case import case_validator as case_validator_module
from gen_epix.casedb.services.case.case_validator import CaseValidator
from gen_epix.commondb.domain.enum import DataIssueType
from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import TimeUnit, TimeUnitTransformStrategy
from gen_epix.transform.transformers.iso_time import IsoTimeTransformer


def _make_case_type(
    col_types: list[enum.ColType],
    dim_type: enum.DimType = enum.DimType.TEXT,
    *,
    case_date: bool = False,
) -> tuple[model.CompleteCaseType, list[UUID], list[model.RefCol]]:
    case_type_id = uuid4()
    ref_dim_id = uuid4()
    dim_id = uuid4()
    ref_dim = model.RefDim(id=ref_dim_id, code="test", label="test", dim_type=dim_type)
    dim = model.Dim(
        id=dim_id,
        case_type_id=case_type_id,
        ref_dim_id=ref_dim_id,
        code="test",
        rank=1,
    )
    cols: dict[UUID, model.Col] = {}
    ref_cols: dict[UUID, model.RefCol] = {}
    col_ids: list[UUID] = []
    ref_col_values: list[model.RefCol] = []
    for index, col_type in enumerate(col_types):
        ref_col_id = uuid4()
        col_id = uuid4()
        ref_col_kwargs: dict[str, Any] = {
            "id": ref_col_id,
            "ref_dim_id": ref_dim_id,
            "code": f"col_{index}",
            "col_type": col_type,
        }
        if col_type in enum.ColTypeSet.NUMBER.value | {enum.ColType.INTERVAL}:
            ref_col_kwargs["unit"] = enum.Unit.YEAR
        if col_type in enum.ColTypeSet.STRING_SET.value:
            ref_col_kwargs["concept_set_id"] = uuid4()
        if col_type in enum.ColTypeSet.HAS_REGION_SET.value:
            ref_col_kwargs["region_set_id"] = uuid4()
        if col_type == enum.ColType.REGULAR_LANGUAGE:
            ref_col_kwargs["regex"] = r"^[A-Z]+$"
        ref_col = model.RefCol(**ref_col_kwargs)
        col = model.Col(
            id=col_id,
            case_type_id=case_type_id,
            dim_id=dim_id,
            ref_col_id=ref_col_id,
            code=f"test.col_{index}",
            rank=index,
        )
        cols[col_id] = col
        ref_cols[ref_col_id] = ref_col
        col_ids.append(col_id)
        ref_col_values.append(ref_col)

    complete_case_type = model.CompleteCaseType(
        id=case_type_id,
        user_id=uuid4(),
        name="test",
        etiologies={},
        etiological_agents={},
        ref_dims={ref_dim_id: ref_dim},
        ref_cols=ref_cols,
        dims={dim_id: dim},
        cols=cols,
        genetic_distance_protocols={},
        tree_algorithms={},
        case_type_access_abacs={},
        case_type_share_abacs={},
        case_date_dim_id=dim_id if case_date else None,
    )
    return complete_case_type, col_ids, ref_col_values


def _make_validator(
    complete_case_type: model.CompleteCaseType,
    *,
    concepts: list[Any] | None = None,
    concept_relations: list[Any] | None = None,
    regions: list[Any] | None = None,
    region_relations: list[Any] | None = None,
    organizations: list[Any] | None = None,
) -> CaseValidator:
    service = MagicMock()
    concepts = list(concepts or [])
    concept_relations = concept_relations or []
    regions = list(regions or [])
    region_relations = region_relations or []
    organizations = organizations or []
    supplied_concept_sets = {x.concept_set_id for x in concepts}
    for concept_set_id in {
        x.concept_set_id
        for x in complete_case_type.ref_cols.values()
        if x.concept_set_id is not None
    } - supplied_concept_sets:
        concepts.append(
            _make_concept(
                concept_set_id,
                "default",
                "Default",
                lb="0",
                ub="10",
                lb_in=True,
                ub_in=False,
            )
        )
    supplied_region_sets = {x.region_set_id for x in regions}
    for region_set_id in {
        x.region_set_id
        for x in complete_case_type.ref_cols.values()
        if x.region_set_id is not None
    } - supplied_region_sets:
        region = MagicMock()
        region.id = uuid4()
        region.region_set_id = region_set_id
        region.code = "default"
        region.name = "Default"
        regions.append(region)

    def handle(cmd: Any) -> list[Any]:
        if isinstance(cmd, command.ConceptCrudCommand):
            return concepts
        if isinstance(cmd, command.ConceptRelationCrudCommand):
            return concept_relations
        if isinstance(cmd, command.RegionCrudCommand):
            return regions
        if isinstance(cmd, command.RegionRelationCrudCommand):
            return region_relations
        if isinstance(cmd, command.OrganizationCrudCommand):
            return organizations
        raise AssertionError(f"Unexpected command: {type(cmd).__name__}")

    service.app.handle.side_effect = handle
    return CaseValidator(service, complete_case_type, uuid4())


def _make_concept(concept_set_id: UUID, code: str, name: str, **props: Any) -> Any:
    concept = MagicMock()
    concept.id = uuid4()
    concept.concept_set_id = concept_set_id
    concept.code = code
    concept.name = name
    concept.props = props
    return concept


def _make_upload(
    complete_case_type: model.CompleteCaseType,
    content: dict[UUID, str | None] | None,
) -> tuple[command.UploadCasesCommand, CaseBatchUploadResult]:
    case_type_id = complete_case_type.id
    assert case_type_id is not None
    case = None
    if content is not None:
        case = model.Case(
            case_type_id=case_type_id,
            created_in_data_collection_id=uuid4(),
            content=content,
        )
    cmd = command.UploadCasesCommand(
        case_type_id=case_type_id,
        case_batch=model.CaseBatchForUpload(cases=[model.CaseForUpload(case=case)]),
    )
    batch_result = CaseBatchUploadResult(
        cases=[model.CaseUploadResult(validated_content={}, data_issues=[])]
    )
    return cmd, batch_result


@pytest.mark.parametrize(
    ("value", "n_decimals", "expected"),
    [
        pytest.param(None, 2, None, id="none-passthrough"),
        pytest.param("12.345", 2, "12.34", id="round-half-even-down"),
        pytest.param("12.355", 2, "12.36", id="round-half-even-up"),
        pytest.param("-0.25", 1, "-0.2", id="negative-half-even"),
    ],
)
def test_transform_decimal_normalizes_supported_values(
    value: str | None, n_decimals: int, expected: str | None
) -> None:
    assert CaseValidator._transform_decimal(value, n_decimals) == expected


@pytest.mark.parametrize("value", ["", " 1.2", "NaN", "1e3", "abc"])
def test_transform_decimal_returns_invalid_sentinel(value: str) -> None:
    assert cast(Any, CaseValidator._transform_decimal(value, 2)) is NoReturn


def test_transform_decimal_handles_comma_decimal_separator() -> None:
    assert cast(Any, CaseValidator._transform_decimal("1,2", 2)) is NoReturn


def test_constructor_builds_concept_region_and_organization_maps() -> None:
    complete, _, refs = _make_case_type(
        [enum.ColType.NOMINAL, enum.ColType.GEO_REGION, enum.ColType.ORGANIZATION]
    )
    concept_set_id = refs[0].concept_set_id
    region_set_id = refs[1].region_set_id
    assert concept_set_id is not None
    assert region_set_id is not None
    concept = _make_concept(concept_set_id, "A", "Alpha")
    region = MagicMock()
    region.id = uuid4()
    region.region_set_id = region_set_id
    region.code = "R1"
    region.name = "Region One"
    organization = MagicMock()
    organization.id = uuid4()
    organization.code = "ORG"
    organization.name = "Organization"

    validator = _make_validator(
        complete,
        concepts=[concept],
        regions=[region],
        organizations=[organization],
    )

    assert validator.concept_value_maps[concept_set_id] == {
        str(concept.id).lower(): str(concept.id),
        "a": str(concept.id),
        "alpha": str(concept.id),
    }
    assert validator.region_value_maps[region_set_id]["r1"] == str(region.id)
    assert validator.region_value_maps[region_set_id]["region one"] == str(region.id)
    assert validator.organization_value_map["org"] == str(organization.id)
    assert validator.concept_set_ids == {concept_set_id}
    assert validator.region_set_ids == {region_set_id}


def test_constructor_creates_interval_transformer_and_rejects_missing_bounds() -> None:
    complete, _, refs = _make_case_type([enum.ColType.INTERVAL])
    interval_ref = refs[0]
    concept_set_id = interval_ref.concept_set_id
    assert concept_set_id is not None
    concept = _make_concept(
        concept_set_id, "under-5", "Under 5", lb="0", ub="5", lb_in=True, ub_in=False
    )
    validator = _make_validator(complete, concepts=[concept])
    assert concept_set_id in validator.interval_transformers

    concept.props = {"lb": "0", "ub": "5", "lb_in": None, "ub_in": False}
    with pytest.raises(ValueError, match="missing lb_in or ub_in"):
        _make_validator(complete, concepts=[concept])


def test_get_content_references_rejects_mismatched_case_type() -> None:
    complete, _, _ = _make_case_type([])
    validator = _make_validator(complete)
    cmd, result = _make_upload(complete, {})
    cmd.case_type_id = uuid4()

    with pytest.raises(ValueError, match="correct CaseType"):
        validator._get_content_references(cmd, result)


def test_validate_unknown_columns_keeps_content_and_appends_issue() -> None:
    complete, col_ids, _ = _make_case_type([enum.ColType.TEXT])
    validator = _make_validator(complete)
    unknown_col_id = uuid4()
    issues: list[model.CaseDataIssue] = []

    validator.validate_unknown_columns(
        [{col_ids[0]: "known", unknown_col_id: "extra"}, None], [issues, None]
    )

    assert len(issues) == 1
    assert issues[0].col_id == unknown_col_id
    assert issues[0].original_value == "extra"
    assert issues[0].data_issue_type == DataIssueType.INVALID


def test_individual_transformations_report_and_normalize_each_value_kind() -> None:
    complete, col_ids, refs = _make_case_type(
        [
            enum.ColType.REGULAR_LANGUAGE,
            enum.ColType.NOMINAL,
            enum.ColType.DECIMAL_2,
            enum.ColType.TIME_YEAR,
            enum.ColType.TEXT,
        ]
    )
    concept_set_id = refs[1].concept_set_id
    assert concept_set_id is not None
    concept = _make_concept(concept_set_id, "KNOWN", "Known")
    validator = _make_validator(complete, concepts=[concept])
    contents: list[dict[UUID, str | None] | None] = [
        {
            col_ids[0]: "ABC",
            col_ids[1]: "known",
            col_ids[2]: "1.239",
            col_ids[3]: "2024",
            col_ids[4]: "plain",
        }
    ]
    updated: list[dict[UUID, str | None] | None] = [{}]
    issues: list[model.CaseDataIssue] = []

    validator.transform_individual_values(contents, updated, [issues])

    assert updated[0] == {
        col_ids[0]: "ABC",
        col_ids[1]: str(concept.id),
        col_ids[2]: "1.24",
        col_ids[3]: "2024",
        col_ids[4]: "plain",
    }
    assert [issue.data_issue_type for issue in issues] == [
        DataIssueType.TRANSFORMED,
        DataIssueType.TRANSFORMED,
    ]


def test_region_organization_and_invalid_time_transformations() -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.GEO_REGION, enum.ColType.ORGANIZATION, enum.ColType.TIME_DAY]
    )
    region_set_id = refs[0].region_set_id
    assert region_set_id is not None
    region = MagicMock()
    region.id = uuid4()
    region.region_set_id = region_set_id
    region.code = "R1"
    region.name = "Region"
    organization = MagicMock()
    organization.id = uuid4()
    organization.code = "ORG"
    organization.name = "Organization"
    validator = _make_validator(
        complete, regions=[region], organizations=[organization]
    )
    contents: list[dict[UUID, str | None] | None] = [
        {col_ids[0]: "r1", col_ids[1]: "org", col_ids[2]: "2024-02-31"}
    ]
    updated: list[dict[UUID, str | None]] = [{}]
    issues: list[model.CaseDataIssue] = []

    validator.transform_individual_values(contents, updated, [issues])

    assert updated[0] == {
        col_ids[0]: str(region.id),
        col_ids[1]: str(organization.id),
        col_ids[2]: "2024-02-31",
    }
    assert [issue.data_issue_type for issue in issues] == [
        DataIssueType.TRANSFORMED,
        DataIssueType.TRANSFORMED,
    ]


def test_decimal_issue_message_does_not_reuse_previous_column_message() -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.NOMINAL, enum.ColType.DECIMAL_2]
    )
    concept_set_id = refs[0].concept_set_id
    assert concept_set_id is not None
    validator = _make_validator(
        complete, concepts=[_make_concept(concept_set_id, "known", "Known")]
    )
    issues: list[model.CaseDataIssue] = []

    validator.transform_individual_values(
        [{col_ids[0]: "missing", col_ids[1]: "invalid"}],
        [{}],
        [issues],
    )

    assert [issue.message for issue in issues] == [
        "missing cannot be mapped to concept",
        "invalid is not a valid DECIMAL_2 value",
    ]


def test_transform_individual_value_handles_invalid_and_none_results() -> None:
    col_id = uuid4()
    updated: dict[UUID, str | None] = {}
    issues: list[model.CaseDataIssue] = []

    CaseValidator._transform_individual_value(
        {col_id: "bad"},
        updated,
        issues,
        col_id,
        lambda _: case_validator_module.NoReturn,
        "code",
        "{orig_value} invalid",
    )
    assert col_id not in updated
    assert issues[0].message == "bad invalid"

    CaseValidator._transform_individual_value(
        {col_id: "value"}, updated, issues, col_id, lambda _: None, "code", "message"
    )
    assert col_id in updated
    assert updated[col_id] is None
    assert issues[-1].data_issue_type == DataIssueType.TRANSFORMED
    assert issues[-1].original_value == "value"
    assert issues[-1].updated_value is None

    CaseValidator._transform_individual_value(
        {col_id: None}, updated, issues, col_id, lambda value: value, "code", "message"
    )
    assert len(issues) == 2


def test_get_col_pairs_returns_both_directions_and_handles_small_inputs() -> None:
    first, second, third = uuid4(), uuid4(), uuid4()
    assert CaseValidator._get_col_pairs([]) == []
    assert CaseValidator._get_col_pairs([first]) == []
    assert CaseValidator._get_col_pairs([first, second]) == [
        (first, second),
        (second, first),
    ]
    assert len(CaseValidator._get_col_pairs([first, second, third])) == 6


def test_column_transform_skips_null_cases_empty_content_and_absent_values() -> None:
    complete, col_ids, _ = _make_case_type([enum.ColType.TEXT])
    validator = _make_validator(complete)
    issues: list[model.CaseDataIssue] = []

    validator._transform_column_values(
        col_ids[0],
        lambda value: value,
        "code",
        "message",
        [None, {}],
        [None, {}],
        [None, issues],
    )

    assert issues == []


def test_set_derived_value_classifies_new_values_and_conflicts() -> None:
    source_id, target_id = uuid4(), uuid4()
    issues: list[model.CaseDataIssue] = []
    content: dict[UUID, str | None] = {source_id: "source"}
    updated: dict[UUID, str | None] = {source_id: "source"}
    validator = object.__new__(CaseValidator)

    validator._set_derived_value(
        content, updated, issues, "code", (source_id, target_id), "first"
    )
    validator._set_derived_value(
        content, updated, issues, "code", (source_id, target_id), "second"
    )
    validator._set_derived_value(
        content, updated, issues, "code", (source_id, target_id), "second"
    )

    assert updated[target_id] == "second"
    assert [issue.data_issue_type for issue in issues] == [
        DataIssueType.DERIVED,
        DataIssueType.CONFLICT,
    ]
    assert issues[1].original_value is None


def test_time_pair_derives_more_precise_value() -> None:
    complete, col_ids, _ = _make_case_type(
        [enum.ColType.TIME_YEAR, enum.ColType.TIME_MONTH], enum.DimType.TIME
    )
    validator = _make_validator(complete)
    contents: list[dict[UUID, str | None] | None] = [{col_ids[1]: "2024-02"}]
    updated: list[dict[UUID, str | None] | None] = [{col_ids[1]: "2024-02"}]
    issues: list[model.CaseDataIssue] = []

    validator.transform_value_pairs(contents, updated, [issues])

    assert updated[0][col_ids[0]] == "2024"
    assert issues[0].data_issue_type == DataIssueType.DERIVED


def test_time_value_skips_invalid_values_and_transformer_errors() -> None:
    complete, col_ids, _ = _make_case_type(
        [enum.ColType.TIME_YEAR, enum.ColType.TIME_MONTH], enum.DimType.TIME
    )
    validator = _make_validator(complete)
    pair = (col_ids[0], col_ids[1])
    ref_col = complete.ref_cols[complete.cols[col_ids[0]].ref_col_id]
    issues: list[model.CaseDataIssue] = []
    transformer = IsoTimeTransformer(
        field_name="time_value",
        src_unit=TimeUnit.YEAR,
        tgt_unit=TimeUnit.MONTH,
        strategy=TimeUnitTransformStrategy.EXACT_ONLY,
    )

    validator._transform_time_value(
        {col_ids[0]: "bad"}, {col_ids[0]: "bad"}, issues, pair, ref_col, transformer
    )
    assert issues == []

    validator._transform_time_value(None, None, None, pair, ref_col, transformer)
    validator._transform_time_value(
        {col_ids[0]: "2024"},
        {col_ids[0]: None},
        issues,
        pair,
        ref_col,
        transformer,
    )

    class BrokenTransformer:
        def transform(self, _: ObjectAdapter) -> ObjectAdapter:
            raise RuntimeError("failed")

    validator._transform_time_value(
        {col_ids[0]: "2024"},
        {col_ids[0]: "2024"},
        issues,
        pair,
        ref_col,
        cast(Any, BrokenTransformer()),
    )
    assert issues == []


def test_case_date_uses_first_available_value_and_skips_missing_cases() -> None:
    complete, col_ids, _ = _make_case_type(
        [enum.ColType.TIME_DAY, enum.ColType.TIME_YEAR],
        enum.DimType.TIME,
        case_date=True,
    )
    validator = _make_validator(complete)
    cmd, result = _make_upload(complete, {col_ids[1]: "2020"})
    case = cmd.case_batch.cases[0].case
    assert case is not None
    original_date = case.timed_at

    validator.calculate_case_date(cmd, result, [{col_ids[1]: "2020"}])

    assert case.timed_at.year == 2020
    assert case.timed_at != original_date
    assert result.cases[0].logs


def test_validate_and_transform_returns_mutated_result_and_checks_case_type() -> None:
    complete, col_ids, _ = _make_case_type([enum.ColType.TEXT])
    validator = _make_validator(complete)
    cmd, result = _make_upload(complete, {col_ids[0]: "value"})

    assert validator.validate_and_transform(cmd, result) is result
    assert result.cases[0].validated_content == {col_ids[0]: "value"}


def test_geo_pair_derives_related_region() -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.GEO_REGION, enum.ColType.GEO_REGION], enum.DimType.GEO
    )
    source_set_id, target_set_id = refs[0].region_set_id, refs[1].region_set_id
    assert source_set_id is not None
    assert target_set_id is not None
    source_region_id, target_region_id = str(uuid4()), str(uuid4())
    validator = _make_validator(complete)
    validator.region_relation_maps = {
        (source_set_id, target_set_id): {source_region_id: target_region_id}
    }
    issues: list[model.CaseDataIssue] = []
    updated: list[dict[UUID, str | None] | None] = [{col_ids[0]: source_region_id}]

    validator.transform_value_pairs([{col_ids[0]: source_region_id}], updated, [issues])

    assert updated[0][col_ids[1]] == target_region_id
    assert issues[0].data_issue_type == DataIssueType.DERIVED


def test_decimal_to_interval_derivation_uses_interval_transformer() -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.DECIMAL_2, enum.ColType.INTERVAL], enum.DimType.NUMBER
    )
    concept_set_id = refs[1].concept_set_id
    assert concept_set_id is not None
    validator = _make_validator(complete)
    interval_transformer = MagicMock()
    interval_transformer.is_transformable.return_value = True
    interval_transformer.transform.side_effect = lambda _: ObjectAdapter(
        {"value": "interval-id"}
    )
    validator.interval_transformers[concept_set_id] = interval_transformer
    issues: list[model.CaseDataIssue] = []
    updated: list[dict[UUID, str | None] | None] = [{col_ids[0]: "2.00"}]

    validator.transform_value_pairs([{col_ids[0]: "2.00"}], updated, [issues])

    assert updated[0][col_ids[1]] == "interval-id"
    assert issues[0].data_issue_type == DataIssueType.DERIVED


def test_calculate_case_date_rejects_non_iso_value() -> None:
    complete, col_ids, _ = _make_case_type(
        [enum.ColType.TIME_DAY], enum.DimType.TIME, case_date=True
    )
    validator = _make_validator(complete)
    cmd, result = _make_upload(complete, {col_ids[0]: "2024-01-01"})

    with pytest.raises(AssertionError, match="non-ISO"):
        validator.calculate_case_date(cmd, result, [{col_ids[0]: "20240101"}])


def test_constructor_rejects_interval_metadata_without_bounds() -> None:
    complete, _, refs = _make_case_type([enum.ColType.INTERVAL])
    concept_set_id = refs[0].concept_set_id
    assert concept_set_id is not None
    concept = _make_concept(concept_set_id, "under-5", "Under 5", lb="0", ub=None)

    with pytest.raises(ValueError, match="missing lb or ub"):
        _make_validator(complete, concepts=[concept])


def test_transform_time_pair_skips_untransformable_units() -> None:
    complete, col_ids, _ = _make_case_type(
        [enum.ColType.TIME_MONTH, enum.ColType.TIME_DAY], enum.DimType.TIME
    )
    validator = _make_validator(complete)
    ref_cols = [
        complete.ref_cols[complete.cols[col_id].ref_col_id] for col_id in col_ids
    ]
    issues: list[model.CaseDataIssue] = []

    validator._transform_time_value_pair(
        [{}], [{}], [issues], (col_ids[0], col_ids[1]), ref_cols[0], ref_cols[1]
    )
    assert issues == []

    text_complete, text_col_ids, text_refs = _make_case_type(
        [enum.ColType.TEXT, enum.ColType.TIME_DAY], enum.DimType.TIME
    )
    text_validator = _make_validator(text_complete)
    text_validator._transform_time_value_pair(
        [{}], [{}], [[]], (text_col_ids[0], text_col_ids[1]), text_refs[0], text_refs[1]
    )

    reverse_complete, reverse_col_ids, reverse_refs = _make_case_type(
        [enum.ColType.TIME_YEAR, enum.ColType.TIME_DAY], enum.DimType.TIME
    )
    reverse_validator = _make_validator(reverse_complete)
    reverse_validator._transform_time_value_pair(
        [{}],
        [{}],
        [[]],
        (reverse_col_ids[0], reverse_col_ids[1]),
        reverse_refs[0],
        reverse_refs[1],
    )


def test_time_pair_skips_when_transformer_reports_unsupported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.TIME_YEAR, enum.ColType.TIME_DAY], enum.DimType.TIME
    )
    validator = _make_validator(complete)
    monkeypatch.setattr(
        IsoTimeTransformer, "can_transform_time", staticmethod(lambda *_: False)
    )

    validator._transform_time_value_pair(
        [{}], [{}], [[]], (col_ids[0], col_ids[1]), refs[0], refs[1]
    )


def test_relation_metadata_maps_containment_from_contained_to_container() -> None:
    complete, _, refs = _make_case_type([enum.ColType.NOMINAL, enum.ColType.NOMINAL])
    source_set_id = refs[0].concept_set_id
    target_set_id = refs[1].concept_set_id
    assert source_set_id is not None
    assert target_set_id is not None
    source = _make_concept(source_set_id, "source", "Source")
    target = _make_concept(target_set_id, "target", "Target")
    concept_relation = MagicMock()
    concept_relation.from_concept_id = source.id
    concept_relation.to_concept_id = target.id
    concept_relation.relation = enum.ConceptRelationType.CONTAINS
    ignored_concept_relation = MagicMock()
    ignored_concept_relation.from_concept_id = source.id
    ignored_concept_relation.to_concept_id = target.id
    ignored_concept_relation.relation = "UNSUPPORTED"
    validator = _make_validator(
        complete,
        concepts=[source, target],
        concept_relations=[concept_relation, ignored_concept_relation],
    )

    assert validator.concept_relation_maps[(target_set_id, source_set_id)] == {
        str(target.id): str(source.id)
    }

    geo_complete, _, geo_refs = _make_case_type(
        [enum.ColType.GEO_REGION, enum.ColType.GEO_REGION], enum.DimType.GEO
    )
    from_set_id = geo_refs[0].region_set_id
    to_set_id = geo_refs[1].region_set_id
    assert from_set_id is not None
    assert to_set_id is not None
    from_region = MagicMock()
    from_region.id = uuid4()
    from_region.region_set_id = from_set_id
    from_region.code = "from"
    from_region.name = "From"
    to_region = MagicMock()
    to_region.id = uuid4()
    to_region.region_set_id = to_set_id
    to_region.code = "to"
    to_region.name = "To"
    region_relation = MagicMock()
    region_relation.from_region_id = from_region.id
    region_relation.to_region_id = to_region.id
    region_relation.relation = enum.RegionRelationType.CONTAINS
    ignored_region_relation = MagicMock()
    ignored_region_relation.from_region_id = from_region.id
    ignored_region_relation.to_region_id = to_region.id
    ignored_region_relation.relation = enum.RegionRelationType.IS_SEPARATE_FROM
    geo_validator = _make_validator(
        geo_complete,
        regions=[from_region, to_region],
        region_relations=[region_relation, ignored_region_relation],
    )

    assert geo_validator.region_relation_maps[(to_set_id, from_set_id)] == {
        str(to_region.id): str(from_region.id)
    }


def test_interval_to_interval_transformer_creation_and_id_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.INTERVAL, enum.ColType.INTERVAL], enum.DimType.NUMBER
    )
    source_concept_set_id = refs[0].concept_set_id
    target_concept_set_id = refs[1].concept_set_id
    assert source_concept_set_id is not None
    assert target_concept_set_id is not None
    concept_set_ids = [source_concept_set_id, target_concept_set_id]
    concepts = [
        _make_concept(
            concept_set_id,
            f"interval_{index}",
            f"Interval {index}",
            lb="0",
            ub="10",
            lb_in=True,
            ub_in=False,
        )
        for index, concept_set_id in enumerate(concept_set_ids)
    ]
    validator = _make_validator(complete, concepts=concepts)
    ref_cols = refs

    assert (
        validator._create_interval_to_interval_transformer(
            ref_cols[0], ref_cols[1], 1.0
        )
        is not None
    )
    validator.transform_value_pairs([{}], [{}], [[]])
    validator._transform_interval_to_interval(
        [{}], [{}], [[]], (col_ids[0], col_ids[1]), ref_cols[0], ref_cols[0], 1.0
    )
    assert (
        validator._create_interval_to_interval_transformer(
            ref_cols[0], ref_cols[0], 1.0
        )
        is None
    )
    source_concept_set_id = ref_cols[0].concept_set_id
    ref_cols[0].concept_set_id = None
    assert (
        validator._create_interval_to_interval_transformer(
            ref_cols[0], ref_cols[1], 1.0
        )
        is None
    )
    ref_cols[0].concept_set_id = source_concept_set_id
    target_transformer = validator.interval_transformers[concept_set_ids[1]]
    validator.interval_transformers.pop(concept_set_ids[1])
    assert (
        validator._create_interval_to_interval_transformer(
            ref_cols[0], ref_cols[1], 1.0
        )
        is None
    )
    validator.interval_transformers[concept_set_ids[1]] = target_transformer

    class NoMatchTransformer:
        def is_transformable(self, _: str) -> bool:
            return False

    class BrokenTransformTransformer:
        def is_transformable(self, _: str) -> bool:
            return True

        def transform(self, _: ObjectAdapter) -> ObjectAdapter:
            raise RuntimeError("failed")

    class MatchingTransformer:
        def is_transformable(self, _: str) -> bool:
            return True

        def transform(self, adapter: ObjectAdapter) -> ObjectAdapter:
            adapter.set("interval_value", "mapped")
            return adapter

    assert (
        CaseValidator._transform_interval_id(cast(Any, NoMatchTransformer()), "source")
        is None
    )
    assert (
        CaseValidator._transform_interval_id(
            cast(Any, BrokenTransformTransformer()), "source"
        )
        is None
    )
    assert (
        CaseValidator._transform_interval_id(cast(Any, MatchingTransformer()), "source")
        == "mapped"
    )

    monkeypatch.setattr(
        case_validator_module,
        "IntervalToIntervalTransformer",
        lambda **_: (_ for _ in ()).throw(ValueError("bad metadata")),
    )
    assert (
        validator._create_interval_to_interval_transformer(
            ref_cols[0], ref_cols[1], 1.0
        )
        is None
    )


def test_number_pairs_skip_untransformable_and_raise_for_missing_unit_multiplier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.DECIMAL_2, enum.ColType.INTERVAL], enum.DimType.NUMBER
    )
    validator = _make_validator(complete)
    concept_set_id = refs[1].concept_set_id
    assert concept_set_id is not None
    monkeypatch.setattr(
        validator.interval_transformers[concept_set_id],
        "is_transformable",
        lambda _: False,
    )
    validator.transform_value_pairs(
        [{col_ids[0]: "2.00"}], [{col_ids[0]: "2.00"}], [[]]
    )

    refs[1].unit = enum.Unit.OTHER
    with pytest.raises(NotImplementedError, match="No multiplier found"):
        validator.transform_value_pairs([{}], [{}], [[]])


def test_case_date_no_configured_dimension_and_null_case_are_skipped() -> None:
    complete, col_ids, _ = _make_case_type([enum.ColType.TIME_DAY])
    validator = _make_validator(complete)
    cmd, result = _make_upload(complete, None)
    validator.calculate_case_date(cmd, result, [None])

    dated_complete, dated_col_ids, _ = _make_case_type(
        [enum.ColType.TIME_DAY], enum.DimType.TIME, case_date=True
    )
    dated_validator = _make_validator(dated_complete)
    null_case_cmd, null_case_result = _make_upload(dated_complete, None)
    dated_validator.calculate_case_date(null_case_cmd, null_case_result, [None])


def test_geo_pair_skips_non_geo_null_and_unmapped_values() -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.GEO_REGION, enum.ColType.GEO_REGION], enum.DimType.GEO
    )
    validator = _make_validator(complete)
    issues: list[model.CaseDataIssue] = []
    validator._transform_geo_value_pairs(
        [None, {}, {col_ids[0]: "unmapped"}],
        [None, {}, {col_ids[0]: "unmapped"}],
        [None, [], issues],
        [(col_ids[0], col_ids[1])],
    )

    text_complete, text_col_ids, text_refs = _make_case_type(
        [enum.ColType.TEXT, enum.ColType.GEO_REGION], enum.DimType.GEO
    )
    text_validator = _make_validator(text_complete)
    text_validator._transform_geo_value_pairs(
        [{}],
        [{}],
        [[]],
        [(text_col_ids[0], text_col_ids[1])],
    )
    assert refs[0].region_set_id is not None
    assert text_refs[1].region_set_id is not None
    assert issues == []


def test_decimal_to_interval_skips_missing_transformers_and_values() -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.DECIMAL_2, enum.ColType.INTERVAL], enum.DimType.NUMBER
    )
    validator = _make_validator(complete)
    pair = (col_ids[0], col_ids[1])
    issues: list[model.CaseDataIssue] = []
    interval_ref = refs[1]
    concept_set_id = interval_ref.concept_set_id
    assert concept_set_id is not None

    interval_ref.concept_set_id = None
    validator._transform_decimal_to_interval([{}], [{}], [[]], pair, interval_ref, 1.0)
    interval_ref.concept_set_id = concept_set_id
    validator.interval_transformers.pop(concept_set_id)
    validator._transform_decimal_to_interval([{}], [{}], [[]], pair, interval_ref, 1.0)

    transformer = MagicMock()
    validator._transform_decimal_content_to_interval(
        None, None, None, pair, transformer, 1.0
    )
    validator._transform_decimal_content_to_interval(
        {col_ids[0]: None}, {col_ids[0]: None}, issues, pair, transformer, 1.0
    )
    transformer.is_transformable.return_value = False
    validator._transform_decimal_content_to_interval(
        {col_ids[0]: "2"}, {col_ids[0]: "2"}, issues, pair, transformer, 1.0
    )
    transformer.is_transformable.return_value = True
    transformer.transform.return_value = ObjectAdapter({})
    validator._transform_decimal_content_to_interval(
        {col_ids[0]: "2"}, {col_ids[0]: "2"}, issues, pair, transformer, 1.0
    )
    transformer.transform.return_value = ObjectAdapter({"value": "interval-id"})
    validator._transform_decimal_content_to_interval(
        {col_ids[0]: "2"},
        {col_ids[0]: "2", col_ids[1]: "existing"},
        issues,
        pair,
        transformer,
        1.0,
    )
    assert issues == []


def test_interval_to_interval_pair_handles_missing_and_existing_values() -> None:
    complete, col_ids, refs = _make_case_type(
        [enum.ColType.INTERVAL, enum.ColType.INTERVAL], enum.DimType.NUMBER
    )
    validator = _make_validator(complete)

    class MappingTransformer:
        def is_transformable(self, value: str) -> bool:
            return value == "source"

        def transform(self, adapter: ObjectAdapter) -> ObjectAdapter:
            adapter.set("interval_value", "target")
            return adapter

    transformer = MappingTransformer()
    validator._create_interval_to_interval_transformer = lambda *_: cast(
        Any, transformer
    )
    pair = (col_ids[0], col_ids[1])
    ref_col1, ref_col2 = refs
    issues: list[model.CaseDataIssue] = []
    contents: list[dict[UUID, str | None] | None] = [
        None,
        {},
        {col_ids[0]: "unmapped"},
        {col_ids[0]: "source", col_ids[1]: "existing"},
        {col_ids[0]: "source"},
    ]
    updated: list[dict[UUID, str | None] | None] = [
        None,
        {},
        {col_ids[0]: "unmapped"},
        {col_ids[0]: "source", col_ids[1]: "existing"},
        {col_ids[0]: "source"},
    ]
    validator._transform_interval_to_interval(
        contents,
        updated,
        [None, [], [], [], issues],
        pair,
        ref_col1,
        ref_col2,
        1.0,
    )

    assert updated[-1] is not None
    assert updated[-1][col_ids[1]] == "target"
    assert len(issues) == 1
