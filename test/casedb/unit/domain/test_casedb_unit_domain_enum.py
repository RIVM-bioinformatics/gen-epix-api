"""Unit tests for the casedb domain enumerations."""

from enum import Enum, StrEnum

import pytest

from gen_epix.casedb.domain import enum
from gen_epix.commondb.domain.enum import RoleSet as CommondbRoleSet


class TestSimpleEnums:
    @pytest.mark.parametrize(
        "enum_cls",
        [
            enum.ServiceType,
            enum.RepositoryType,
            enum.RegionRelationType,
            enum.TreeAlgorithmType,
            enum.Role,
            enum.CaseRight,
            enum.CaseClassification,
            enum.CaseTypeSetCategoryPurpose,
            enum.ConceptSetType,
            enum.ConceptRelationType,
            enum.DimType,
            enum.ColType,
            enum.FeatureFlag,
        ],
    )
    def test_string_values_are_unique_and_non_empty(self, enum_cls: type[Enum]):
        values = [member.value for member in enum_cls]
        assert all(isinstance(value, str) and value for value in values)
        assert len(values) == len(set(values))
        assert len(values) == len(enum_cls.__members__)

    @pytest.mark.parametrize(
        "enum_cls",
        [
            enum.ServiceType,
            enum.RepositoryType,
            enum.RegionRelationType,
            enum.TreeAlgorithmType,
            enum.CaseRight,
            enum.CaseClassification,
            enum.CaseTypeSetCategoryPurpose,
            enum.ConceptSetType,
            enum.ConceptRelationType,
            enum.DimType,
            enum.ColType,
        ],
    )
    def test_value_equals_name(self, enum_cls: type[Enum]):
        assert all(member.value == member.name for member in enum_cls)

    def test_role_values_are_prefixed(self):
        assert all(role.value == f"CASEDB_{role.name}" for role in enum.Role)

    def test_repository_type_members(self):
        assert {m.name for m in enum.RepositoryType} == {"DICT", "SA_SQLITE", "SA_SQL"}

    def test_col_relation_values(self):
        assert [m.value for m in enum.ColRelation] == [0, 1, 2]
        assert enum.ColRelation(0) is enum.ColRelation.IS_UNRELATED_TO

    def test_feature_flag_value(self):
        assert enum.FeatureFlag.DISABLE_UPLOAD.value == "disable_upload"

    def test_lookup_by_value_and_invalid_value(self):
        assert enum.CaseClassification("CONFIRMED") is enum.CaseClassification.CONFIRMED
        with pytest.raises(ValueError):
            enum.CaseClassification("confirmed")
        with pytest.raises(ValueError):
            enum.CaseClassification("")

    def test_role_set_is_reexported_from_commondb(self):
        assert enum.RoleSet is CommondbRoleSet


class TestUnit:
    def test_is_str_enum(self):
        assert issubclass(enum.Unit, StrEnum)

    def test_members_equal_their_names_as_strings(self):
        assert all(unit == unit.name and str(unit) == unit.name for unit in enum.Unit)
        assert enum.Unit("DAY") is enum.Unit.DAY
        with pytest.raises(ValueError):
            enum.Unit("day")


class TestCaseRightSet:
    def test_members_are_frozensets_of_case_rights(self):
        for member in enum.CaseRightSet:
            assert isinstance(member.value, frozenset)
            assert member.value
            assert all(isinstance(right, enum.CaseRight) for right in member.value)

    def test_all_members_are_distinct(self):
        assert len(enum.CaseRightSet.__members__) == len(list(enum.CaseRightSet))

    def test_share_and_content_partition_all_rights(self):
        share = enum.CaseRightSet.SHARE.value
        content = enum.CaseRightSet.CONTENT.value
        assert share.isdisjoint(content)
        assert share | content == set(enum.CaseRight)

    def test_add_and_remove_are_subsets_of_share(self):
        share = enum.CaseRightSet.SHARE.value
        assert enum.CaseRightSet.ADD.value | enum.CaseRightSet.REMOVE.value == share
        assert enum.CaseRightSet.ADD.value.isdisjoint(enum.CaseRightSet.REMOVE.value)

    def test_case_and_case_set_partition_all_rights(self):
        case = enum.CaseRightSet.CASE.value
        case_set = enum.CaseRightSet.CASE_SET.value
        assert case.isdisjoint(case_set)
        assert case | case_set == set(enum.CaseRight)
        assert all(right.value.endswith("_CASE") for right in case)
        assert all(right.value.endswith("_CASE_SET") for right in case_set)

    def test_content_subsets(self):
        content = enum.CaseRightSet.CONTENT.value
        assert enum.CaseRightSet.CASE_CONTENT.value < content
        assert enum.CaseRightSet.CASE_SET_CONTENT.value < content
        assert (
            enum.CaseRightSet.CASE_CONTENT.value
            | enum.CaseRightSet.CASE_SET_CONTENT.value
            == content
        )


class TestConceptSetTypeSet:
    def test_language_members(self):
        assert enum.ConceptSetTypeSet.LANGUAGE.value == {
            enum.ConceptSetType.CONTEXT_FREE_GRAMMAR_JSON,
            enum.ConceptSetType.CONTEXT_FREE_GRAMMAR_XML,
            enum.ConceptSetType.REGULAR_LANGUAGE,
        }

    def test_language_and_string_set_cover_all_types_disjointly(self):
        language = enum.ConceptSetTypeSet.LANGUAGE.value
        string_set = enum.ConceptSetTypeSet.STRING_SET.value
        assert language.isdisjoint(string_set)
        assert language | string_set == set(enum.ConceptSetType)

    def test_has_unit_is_interval_only(self):
        assert enum.ConceptSetTypeSet.HAS_UNIT.value == {enum.ConceptSetType.INTERVAL}


class TestColTypeSet:
    def test_all_values_are_frozensets_of_col_types(self):
        for value in (member.value for member in enum.ColTypeSet):
            assert isinstance(value, frozenset)
            assert value
            assert all(isinstance(col_type, enum.ColType) for col_type in value)
        # Members with identical values become aliases and are accessible by name.
        for name in ("HAS_CONCEPT_SET", "HAS_SCHEMA"):
            assert isinstance(enum.ColTypeSet[name].value, frozenset)

    @pytest.mark.parametrize(
        "set_name, expected_names",
        [
            (
                "ID",
                {
                    "ID_PERSON",
                    "ID_SAMPLE",
                    "ID_CASE",
                    "ID_EVENT",
                    "ID_GENETIC_SEQUENCE",
                },
            ),
            (
                "LANGUAGE",
                {
                    "CONTEXT_FREE_GRAMMAR_JSON",
                    "CONTEXT_FREE_GRAMMAR_XML",
                    "REGULAR_LANGUAGE",
                },
            ),
            (
                "CONTEXT_FREE_GRAMMAR",
                {"CONTEXT_FREE_GRAMMAR_JSON", "CONTEXT_FREE_GRAMMAR_XML"},
            ),
            ("ENTITY", {"GENETIC_SEQUENCE", "GENETIC_DISTANCE", "ORGANIZATION"}),
            ("STRING_SET", {"NOMINAL", "ORDINAL", "INTERVAL"}),
            (
                "TIME",
                {"TIME_DAY", "TIME_WEEK", "TIME_MONTH", "TIME_QUARTER", "TIME_YEAR"},
            ),
            ("GEO", {"GEO_LATLON", "GEO_REGION"}),
            ("NUMBER", {f"DECIMAL_{i}" for i in range(7)}),
            (
                "GENETIC",
                {
                    "GENETIC_READS",
                    "GENETIC_SEQUENCE",
                    "GENETIC_PROFILE",
                    "GENETIC_DISTANCE",
                },
            ),
            ("ORGANIZATION", {"ORGANIZATION"}),
            ("OTHER", {"OTHER"}),
            ("HAS_UNIT", {f"DECIMAL_{i}" for i in range(7)} | {"INTERVAL"}),
            ("HAS_CONCEPT_SET", {"NOMINAL", "ORDINAL", "INTERVAL"}),
            ("HAS_REGION_SET", {"GEO_REGION"}),
            ("HAS_GENETIC_DISTANCE_PROTOCOL", {"GENETIC_DISTANCE"}),
            ("HAS_REGEX", {"REGULAR_LANGUAGE"}),
            ("HAS_SCHEMA", {"CONTEXT_FREE_GRAMMAR_JSON", "CONTEXT_FREE_GRAMMAR_XML"}),
        ],
    )
    def test_set_contents(self, set_name: str, expected_names: set[str]):
        assert {c.name for c in enum.ColTypeSet[set_name].value} == expected_names

    def test_regular_language_contents(self):
        value = enum.ColTypeSet.REGULAR_LANGUAGE.value
        expected = (
            enum.ColTypeSet.STRING_SET.value
            | enum.ColTypeSet.TIME.value
            | enum.ColTypeSet.GEO.value
            | enum.ColTypeSet.NUMBER.value
            | {enum.ColType.REGULAR_LANGUAGE}
        )
        assert value == expected

    def test_has_unit_is_number_plus_interval(self):
        assert enum.ColTypeSet.HAS_UNIT.value == (
            enum.ColTypeSet.NUMBER.value | {enum.ColType.INTERVAL}
        )

    def test_col_types_str_like(self):
        value = enum.ColTypeSet.COL_TYPES_STR_LIKE.value
        assert enum.ColType.TIME_DAY not in value
        assert enum.ColType.TEXT in value
        assert enum.ColTypeSet.ID.value <= value
        assert {
            enum.ColType.TIME_WEEK,
            enum.ColType.TIME_MONTH,
            enum.ColType.TIME_QUARTER,
            enum.ColType.TIME_YEAR,
            enum.ColType.GEO_REGION,
            enum.ColType.ORGANIZATION,
            enum.ColType.OTHER,
        } <= value
        assert value.isdisjoint(enum.ColTypeSet.NUMBER.value)

    def test_every_col_type_belongs_to_some_set(self):
        covered = set().union(*(member.value for member in enum.ColTypeSet))
        assert covered == set(enum.ColType)


class TestColConceptSetType:
    def test_pairs_are_col_type_and_concept_set_type(self):
        for member in enum.ColConceptSetType:
            col_type, concept_set_type = member.value
            assert isinstance(col_type, enum.ColType)
            assert isinstance(concept_set_type, enum.ConceptSetType)
            assert col_type.name == concept_set_type.name == member.name

    def test_col_types_have_concept_set_or_language(self):
        col_types = {member.value[0] for member in enum.ColConceptSetType}
        assert col_types == (
            enum.ColTypeSet.HAS_CONCEPT_SET.value | enum.ColTypeSet.LANGUAGE.value
        )


class TestDimColTypeSet:
    def test_members_match_dim_types(self):
        assert {m.name for m in enum.DimColTypeSet} == {d.name for d in enum.DimType}

    def test_all_values_are_frozensets_of_col_types(self):
        for member in enum.DimColTypeSet:
            assert isinstance(member.value, frozenset)
            assert all(isinstance(c, enum.ColType) for c in member.value)

    def test_simple_dimension_mappings(self):
        assert enum.DimColTypeSet.IDENTIFIER.value == enum.ColTypeSet.ID.value
        assert enum.DimColTypeSet.TIME.value == enum.ColTypeSet.TIME.value
        assert enum.DimColTypeSet.GEO.value == enum.ColTypeSet.GEO.value
        assert (
            enum.DimColTypeSet.ORGANIZATION.value == enum.ColTypeSet.ORGANIZATION.value
        )

    def test_number_dimension(self):
        assert enum.DimColTypeSet.NUMBER.value == (
            enum.ColTypeSet.NUMBER.value
            | {enum.ColType.INTERVAL, enum.ColType.NOMINAL, enum.ColType.ORDINAL}
        )

    def test_text_dimension(self):
        assert enum.DimColTypeSet.TEXT.value == (
            enum.ColTypeSet.LANGUAGE.value
            | enum.ColTypeSet.STRING_SET.value
            | enum.ColTypeSet.GENETIC.value
            | {enum.ColType.TEXT}
        )

    def test_other_dimension_extends_text_with_other(self):
        assert enum.DimColTypeSet.OTHER.value == (
            enum.DimColTypeSet.TEXT.value | {enum.ColType.OTHER}
        )


def test_col_type_order_time_resolution():
    order = enum.ColTypeOrder.TIME_RESOLUTION_DESC.value
    assert list(order) == [
        enum.ColType.TIME_DAY,
        enum.ColType.TIME_WEEK,
        enum.ColType.TIME_MONTH,
        enum.ColType.TIME_QUARTER,
        enum.ColType.TIME_YEAR,
    ]
    assert list(order.values()) == [1, 2, 3, 4, 5]
    assert set(order) == enum.ColTypeSet.TIME.value
