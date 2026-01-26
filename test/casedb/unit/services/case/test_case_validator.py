"""
Unit tests for CaseValidator in casedb case transformer.

The tests follow the structure and style of commondb upload tests and verify
public methods, with strict isolation via mocking.
"""

from __future__ import annotations

from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.model.case.complete_case_type import CompleteCaseType
from gen_epix.casedb.domain.model.case.operational_data import Case
from gen_epix.casedb.domain.model.case.reference_data import (
    CaseTypeCol,
    CaseTypeDim,
    Col,
    Dim,
)
from gen_epix.casedb.services.case.case_validator import CaseValidator
from gen_epix.commondb.domain.model.organization import Organization


class BaseCaseValidatorTestCase(TestCase):
    """Base test case with common fixtures and helpers for CaseValidator tests."""

    def setUp(self) -> None:
        # Common IDs
        self.user_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440000")
        self.case_type_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400aa")
        self.time_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ab")
        self.geo_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ac")
        self.num_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ad")
        self.text_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ae")
        self.regex_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400af")
        self.org_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400b0")

        # Column IDs (case type col ids)
        self.col_time_day_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440101")
        self.col_time_week_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440102")
        self.col_geo_from_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440103")
        self.col_geo_to_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440104")
        self.col_num_decimal_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440105")
        self.col_num_interval1_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440106")
        self.col_num_interval2_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440107")
        self.col_string_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440108")
        self.col_regex_ctc: UUID = UUID("550e8400-e29b-41d4-a716-446655440109")
        self.col_org_ctc: UUID = UUID("550e8400-e29b-41d4-a716-44665544010a")
        self.col_other_ctc: UUID = UUID("550e8400-e29b-41d4-a716-44665544010b")

        # Underlying column IDs
        self.col_time_day_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440201")
        self.col_time_week_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440202")
        self.col_geo_from_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440203")
        self.col_geo_to_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440204")
        self.col_num_decimal_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440205")
        self.col_num_interval1_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440206")
        self.col_num_interval2_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440207")
        self.col_string_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440208")
        self.col_regex_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440209")
        self.col_org_id: UUID = UUID("550e8400-e29b-41d4-a716-44665544020a")
        self.col_other_id: UUID = UUID("550e8400-e29b-41d4-a716-44665544020b")

        # Sets
        self.concept_set_string: UUID = UUID("550e8400-e29b-41d4-a716-446655440301")
        self.concept_set_interval1: UUID = UUID("550e8400-e29b-41d4-a716-446655440302")
        self.concept_set_interval2: UUID = UUID("550e8400-e29b-41d4-a716-446655440303")
        self.concept_set_regex: UUID = UUID("550e8400-e29b-41d4-a716-446655440304")
        self.region_set_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440305")

        # Concepts
        self.string_concept1_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440401")
        self.interval1_a_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440402")
        self.interval1_b_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440403")
        self.interval2_x_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440404")
        self.interval2_y_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440405")

        # Regions
        self.region_a_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440501")
        self.region_b_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440502")

        # Organization
        self.org_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440601")
        self.org_name: str = "Acme Labs"
        self.org_code: str = "ACME"

        # Service mock
        self.case_service = Mock()

    def _build_complete_case_type(self) -> CompleteCaseType:
        # Dims
        dim_time = Dim(
            id=self.time_dim_id,
            dim_type=enum.DimType.TIME,
            code="Time",
            label="Time",
            rank=1,
        )
        dim_geo = Dim(
            id=self.geo_dim_id,
            dim_type=enum.DimType.GEO,
            code="Geo",
            label="Geo",
            rank=1,
        )
        dim_num = Dim(
            id=self.num_dim_id,
            dim_type=enum.DimType.NUMBER,
            code="Number",
            label="Number",
            rank=1,
        )
        dim_text = Dim(
            id=self.text_dim_id,
            dim_type=enum.DimType.TEXT,
            code="Text",
            label="Text",
            rank=1,
        )
        dim_regex = Dim(
            id=self.regex_dim_id,
            dim_type=enum.DimType.TEXT,
            code="Regex",
            label="Regex",
            rank=1,
        )
        dim_org = Dim(
            id=self.org_dim_id,
            dim_type=enum.DimType.ORGANIZATION,
            code="Org",
            label="Org",
            rank=1,
        )

        # Cols
        col_time_day = Col(
            id=self.col_time_day_id,
            dim_id=self.time_dim_id,
            code="Time.Day",
            rank=1,
            col_type=enum.ColType.TIME_DAY,
        )
        col_time_week = Col(
            id=self.col_time_week_id,
            dim_id=self.time_dim_id,
            code="Time.Week",
            rank=2,
            col_type=enum.ColType.TIME_WEEK,
        )
        col_geo_from = Col(
            id=self.col_geo_from_id,
            dim_id=self.geo_dim_id,
            code="Geo.From",
            rank=1,
            col_type=enum.ColType.GEO_REGION,
            region_set_id=self.region_set_id,
        )
        col_geo_to = Col(
            id=self.col_geo_to_id,
            dim_id=self.geo_dim_id,
            code="Geo.To",
            rank=2,
            col_type=enum.ColType.GEO_REGION,
            region_set_id=self.region_set_id,
        )
        col_num_decimal = Col(
            id=self.col_num_decimal_id,
            dim_id=self.num_dim_id,
            code="Number.Decimal",
            rank=1,
            col_type=enum.ColType.DECIMAL_2,
        )
        col_num_interval1 = Col(
            id=self.col_num_interval1_id,
            dim_id=self.num_dim_id,
            code="Number.Interval1",
            rank=2,
            col_type=enum.ColType.INTERVAL,
            concept_set_id=self.concept_set_interval1,
        )
        col_num_interval2 = Col(
            id=self.col_num_interval2_id,
            dim_id=self.num_dim_id,
            code="Number.Interval2",
            rank=3,
            col_type=enum.ColType.INTERVAL,
            concept_set_id=self.concept_set_interval2,
        )
        col_string = Col(
            id=self.col_string_id,
            dim_id=self.text_dim_id,
            code="Text.String",
            rank=1,
            col_type=enum.ColType.NOMINAL,
            concept_set_id=self.concept_set_string,
        )
        col_regex = Col(
            id=self.col_regex_id,
            dim_id=self.regex_dim_id,
            code="Regex.Pattern",
            rank=2,
            col_type=enum.ColType.REGULAR_LANGUAGE,
            concept_set_id=self.concept_set_regex,
        )
        col_org = Col(
            id=self.col_org_id,
            dim_id=self.org_dim_id,
            code="Org.Org",
            rank=1,
            col_type=enum.ColType.ORGANIZATION,
        )
        col_other = Col(
            id=self.col_other_id,
            dim_id=self.text_dim_id,
            code="Text.Other",
            rank=99,
            col_type=enum.ColType.OTHER,
        )

        ctd_time = CaseTypeDim(
            id=self.time_dim_id,
            case_type_id=self.case_type_id,
            dim_id=self.time_dim_id,
            occurrence=0,
            code="Time",
            rank=1,
            is_case_date_dim=True,
        )
        ctd_geo = CaseTypeDim(
            id=self.geo_dim_id,
            case_type_id=self.case_type_id,
            dim_id=self.geo_dim_id,
            occurrence=0,
            code="Geo",
            rank=2,
        )
        ctd_num = CaseTypeDim(
            id=self.num_dim_id,
            case_type_id=self.case_type_id,
            dim_id=self.num_dim_id,
            occurrence=0,
            code="Number",
            rank=3,
        )
        ctd_text = CaseTypeDim(
            id=self.text_dim_id,
            case_type_id=self.case_type_id,
            dim_id=self.text_dim_id,
            occurrence=0,
            code="Text",
            rank=4,
        )
        ctd_regex = CaseTypeDim(
            id=self.regex_dim_id,
            case_type_id=self.case_type_id,
            dim_id=self.regex_dim_id,
            occurrence=0,
            code="Regex",
            rank=5,
        )
        ctd_org = CaseTypeDim(
            id=self.org_dim_id,
            case_type_id=self.case_type_id,
            dim_id=self.org_dim_id,
            occurrence=0,
            code="Org",
            rank=6,
        )

        # CaseTypeCols
        ctc_time_day = CaseTypeCol(
            id=self.col_time_day_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.time_dim_id,
            col_id=self.col_time_day_id,
            code="Time.Day",
            rank=1,
        )
        ctc_time_week = CaseTypeCol(
            id=self.col_time_week_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.time_dim_id,
            col_id=self.col_time_week_id,
            code="Time.Week",
            rank=2,
        )
        ctc_geo_from = CaseTypeCol(
            id=self.col_geo_from_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.geo_dim_id,
            col_id=self.col_geo_from_id,
            code="Geo.From",
            rank=1,
        )
        ctc_geo_to = CaseTypeCol(
            id=self.col_geo_to_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.geo_dim_id,
            col_id=self.col_geo_to_id,
            code="Geo.To",
            rank=2,
        )
        ctc_num_decimal = CaseTypeCol(
            id=self.col_num_decimal_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.num_dim_id,
            col_id=self.col_num_decimal_id,
            code="Number.Decimal",
            rank=1,
        )
        ctc_num_interval1 = CaseTypeCol(
            id=self.col_num_interval1_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.num_dim_id,
            col_id=self.col_num_interval1_id,
            code="Number.Interval1",
            rank=2,
        )
        ctc_num_interval2 = CaseTypeCol(
            id=self.col_num_interval2_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.num_dim_id,
            col_id=self.col_num_interval2_id,
            code="Number.Interval2",
            rank=3,
        )
        ctc_string = CaseTypeCol(
            id=self.col_string_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.text_dim_id,
            col_id=self.col_string_id,
            code="Text.String",
            rank=1,
        )
        ctc_regex = CaseTypeCol(
            id=self.col_regex_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.regex_dim_id,
            col_id=self.col_regex_id,
            code="Regex.Pattern",
            rank=2,
        )
        ctc_org = CaseTypeCol(
            id=self.col_org_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.org_dim_id,
            col_id=self.col_org_id,
            code="Org.Org",
            rank=1,
        )
        ctc_other = CaseTypeCol(
            id=self.col_other_ctc,
            case_type_id=self.case_type_id,
            case_type_dim_id=self.text_dim_id,
            col_id=self.col_other_id,
            code="Text.Other",
            rank=99,
        )

        complete = CompleteCaseType(
            id=self.case_type_id,
            user_id=self.user_id,
            name="Test CT",
            etiologies={},
            etiological_agents={},
            dims={
                self.time_dim_id: dim_time,
                self.geo_dim_id: dim_geo,
                self.num_dim_id: dim_num,
                self.text_dim_id: dim_text,
                self.regex_dim_id: dim_regex,
                self.org_dim_id: dim_org,
            },
            cols={
                self.col_time_day_id: col_time_day,
                self.col_time_week_id: col_time_week,
                self.col_geo_from_id: col_geo_from,
                self.col_geo_to_id: col_geo_to,
                self.col_num_decimal_id: col_num_decimal,
                self.col_num_interval1_id: col_num_interval1,
                self.col_num_interval2_id: col_num_interval2,
                self.col_string_id: col_string,
                self.col_regex_id: col_regex,
                self.col_org_id: col_org,
                self.col_other_id: col_other,
            },
            case_type_dims={
                self.time_dim_id: ctd_time,
                self.geo_dim_id: ctd_geo,
                self.num_dim_id: ctd_num,
                self.text_dim_id: ctd_text,
                self.regex_dim_id: ctd_regex,
                self.org_dim_id: ctd_org,
            },
            case_type_cols={
                self.col_time_day_ctc: ctc_time_day,
                self.col_time_week_ctc: ctc_time_week,
                self.col_geo_from_ctc: ctc_geo_from,
                self.col_geo_to_ctc: ctc_geo_to,
                self.col_num_decimal_ctc: ctc_num_decimal,
                self.col_num_interval1_ctc: ctc_num_interval1,
                self.col_num_interval2_ctc: ctc_num_interval2,
                self.col_string_ctc: ctc_string,
                self.col_regex_ctc: ctc_regex,
                self.col_org_ctc: ctc_org,
                self.col_other_ctc: ctc_other,
            },
            genetic_distance_protocols={},
            tree_algorithms={},
            case_type_access_abacs={},
            case_type_share_abacs={},
            case_date_case_type_dim_id=self.time_dim_id,
        )
        return complete

    def _concept_data(self) -> tuple[
        dict[UUID, model.ConceptSet],
        dict[UUID, set[UUID]],
        dict[UUID, model.Concept],
        dict[tuple[UUID, UUID], dict[str, str]],
    ]:
        # Concept sets
        cs_string = model.ConceptSet(
            id=self.concept_set_string,
            code="STR",
            name="Strings",
            type=enum.ConceptSetType.NOMINAL,
        )
        cs_interval1 = model.ConceptSet(
            id=self.concept_set_interval1,
            code="INT1",
            name="Intervals1",
            type=enum.ConceptSetType.INTERVAL,
        )
        cs_interval2 = model.ConceptSet(
            id=self.concept_set_interval2,
            code="INT2",
            name="Intervals2",
            type=enum.ConceptSetType.INTERVAL,
        )
        cs_regex = model.ConceptSet(
            id=self.concept_set_regex,
            code="REGX",
            name="Regex",
            type=enum.ConceptSetType.REGULAR_LANGUAGE,
            regex=r"^[A-Z]{2}\d{3}$",
        )

        # Concepts
        c_string1 = model.Concept(
            id=self.string_concept1_id,
            concept_set_id=self.concept_set_string,
            code="CODE1",
            name="Name1",
        )
        c_int1_a = model.Concept(
            id=self.interval1_a_id,
            concept_set_id=self.concept_set_interval1,
            code="INT1_A",
            name="[0,10)",
            props={"lb": 0.0, "ub": 10.0, "lb_in": True, "ub_in": False},
        )
        c_int1_b = model.Concept(
            id=self.interval1_b_id,
            concept_set_id=self.concept_set_interval1,
            code="INT1_B",
            name="[10,20]",
            props={"lb": 10.0, "ub": 20.0, "lb_in": True, "ub_in": True},
        )
        c_int2_x = model.Concept(
            id=self.interval2_x_id,
            concept_set_id=self.concept_set_interval2,
            code="INT2_X",
            name="[0,15)",
            props={"lb": 0.0, "ub": 15.0, "lb_in": True, "ub_in": False},
        )
        c_int2_y = model.Concept(
            id=self.interval2_y_id,
            concept_set_id=self.concept_set_interval2,
            code="INT2_Y",
            name="[15,25]",
            props={"lb": 15.0, "ub": 25.0, "lb_in": True, "ub_in": True},
        )

        concept_sets = {
            cs_string.id: cs_string,
            cs_interval1.id: cs_interval1,
            cs_interval2.id: cs_interval2,
            cs_regex.id: cs_regex,
        }
        concepts = {
            c_string1.id: c_string1,
            c_int1_a.id: c_int1_a,
            c_int1_b.id: c_int1_b,
            c_int2_x.id: c_int2_x,
            c_int2_y.id: c_int2_y,
        }
        concept_set_concepts_map: dict[UUID, set[UUID]] = {
            self.concept_set_string: {self.string_concept1_id},
            self.concept_set_interval1: {self.interval1_a_id, self.interval1_b_id},
            self.concept_set_interval2: {self.interval2_x_id, self.interval2_y_id},
            self.concept_set_regex: set(),
        }
        concept_contained_in: dict[tuple[UUID, UUID], dict[str, str]] = {}
        return concept_sets, concept_set_concepts_map, concepts, concept_contained_in  # type: ignore[return-value]

    def _region_data(self) -> tuple[
        dict[UUID, model.Region],
        dict[UUID, set[UUID]],
        dict[tuple[UUID, UUID], dict[str, str]],
    ]:
        region_a = model.Region(
            id=self.region_a_id,
            region_set_id=self.region_set_id,
            code="A",
            name="Region A",
            centroid_lat=0.0,
            centroid_lon=0.0,
            center_lat=0.0,
            center_lon=0.0,
        )
        region_b = model.Region(
            id=self.region_b_id,
            region_set_id=self.region_set_id,
            code="B",
            name="Region B",
            centroid_lat=1.0,
            centroid_lon=1.0,
            center_lat=1.0,
            center_lon=1.0,
        )
        regions = {region_a.id: region_a, region_b.id: region_b}
        region_set_regions_map: dict[UUID, set[UUID]] = {
            self.region_set_id: {self.region_a_id, self.region_b_id}
        }
        # Provide a CONTAINS relation A contains B -> mapping B -> A
        region_contained_in: dict[tuple[UUID, UUID], dict[str, str]] = {
            (self.region_set_id, self.region_set_id): {
                str(self.region_b_id): str(self.region_a_id)
            }
        }
        return regions, region_set_regions_map, region_contained_in  # type: ignore[return-value]

    def _organizations(self) -> list[Organization]:
        return [
            Organization(
                id=self.org_id, name=self.org_name, legal_entity_code=self.org_code
            )
        ]

    def _create_validator(self) -> CaseValidator:
        complete = self._build_complete_case_type()
        with (
            patch.object(
                CaseValidator,
                "_retrieve_concept_data",
                return_value=self._concept_data(),
            ),
            patch.object(
                CaseValidator, "_retrieve_region_data", return_value=self._region_data()
            ),
            patch.object(
                CaseValidator,
                "_retrieve_organization_data",
                return_value=self._organizations(),
            ),
        ):
            validator = CaseValidator(self.case_service, complete, uuid4())
        return validator

    def _make_cmd_and_result(
        self,
        case_contents: list[dict[UUID, str | None]],
    ) -> tuple[command.UploadCasesCommand, model.CaseBatchUploadResult]:
        # Use a single created_in_data_collection_id across all cases and the command
        created_in_dc_id: UUID = uuid4()
        cases_for_upload: list[model.CaseForUpload] = []
        case_results: list[model.CaseUploadResult] = []
        for content in case_contents:
            c = Case(
                id=uuid4(),
                code=None,
                case_type_id=self.case_type_id,
                created_in_data_collection_id=created_in_dc_id,
                content=content,
            )
            cases_for_upload.append(model.CaseForUpload(case=c))
            # Initialize validated_content with the original content so case_date
            # calculation can operate on the expected updated values without
            # needing the full validation pipeline.
            case_results.append(
                model.CaseUploadResult(id=c.id, validated_content=c.content.copy())
            )

        batch = model.CaseBatchForUpload(cases=cases_for_upload)
        cmd = command.UploadCasesCommand(
            case_type_id=self.case_type_id,
            created_in_data_collection_id=created_in_dc_id,
            case_batch=batch,
        )
        retval = model.CaseBatchUploadResult(cases=case_results)
        return cmd, retval


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestGetContentReferences(BaseCaseValidatorTestCase):
    def test_wrong_case_type_raises(self) -> None:
        validator = self._create_validator()
        # Build a command with a different case_type_id
        cmd, retval = self._make_cmd_and_result([{}])
        cmd.case_type_id = uuid4()
        with pytest.raises(ValueError):
            validator.validate_and_transform(cmd, retval)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestValidateUnknownColumns(BaseCaseValidatorTestCase):
    def test_unknown_column_logged(self) -> None:
        validator = self._create_validator()
        unknown_col_id: UUID = uuid4()
        contents: list[dict[UUID, str | None] | None] = [{unknown_col_id: "x"}]
        data_issues_list: list[list[model.CaseDataIssue] | None] = [[]]
        validator.validate_unknown_columns(contents, data_issues_list)
        assert data_issues_list[0] is not None
        assert len(data_issues_list[0]) == 1
        issue = data_issues_list[0][0]
        assert issue.case_type_col_id == unknown_col_id
        assert issue.data_issue_type == enum.DataIssueType.UNAUTHORIZED
        assert issue.code == "a7b3f9d2"


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestTransformIndividualValues(BaseCaseValidatorTestCase):
    def test_all_branches(self) -> None:
        validator = self._create_validator()
        # Prepare contents with values for each type
        contents: list[dict[UUID, str | None] | None] = [
            {
                self.col_string_ctc: "code1",  # maps to concept id (case-insensitive)
                self.col_regex_ctc: "AB123",  # matches pattern
                self.col_geo_from_ctc: "a",  # maps to region id
                self.col_time_day_ctc: "2023-02-05",  # valid day
                self.col_num_decimal_ctc: "3.1415",  # rounded
                self.col_org_ctc: self.org_name,
                self.col_other_ctc: "keep",
            },
            {
                self.col_string_ctc: "unknown",  # cannot map
                self.col_regex_ctc: "xx",  # invalid
                self.col_geo_from_ctc: "unknown",  # cannot map
                self.col_time_day_ctc: "invalid-date",  # invalid
                self.col_num_decimal_ctc: "oops",  # invalid
                self.col_org_ctc: "unknown-org",
            },
        ]
        updated_contents: list[dict[UUID, str | None] | None] = [{}, {}]
        data_issues_list: list[list[model.CaseDataIssue] | None] = [
            [],
            [],
        ]

        validator.transform_individual_values(
            contents, updated_contents, data_issues_list
        )

        # Success case assertions
        uc0 = updated_contents[0]
        assert uc0 is not None
        assert uc0[self.col_string_ctc] == str(self.string_concept1_id)
        assert uc0[self.col_regex_ctc] == "AB123"
        # region mapping
        assert uc0[self.col_geo_from_ctc] == str(self.region_a_id)
        # time day copied
        assert uc0[self.col_time_day_ctc] == "2023-02-05"
        # number rounded
        assert uc0[self.col_num_decimal_ctc] == "3.14"
        # organization
        assert uc0[self.col_org_ctc] == str(self.org_id)
        # other passthrough
        assert uc0[self.col_other_ctc] == "keep"

        issues0 = data_issues_list[0]
        assert issues0 is not None
        # At least derived for string and decimal
        codes0 = {x.code for x in issues0}
        assert "c2d5f6a7" in codes0  # concept mapping
        assert "f5a2b3c0" in codes0  # decimal rounding
        assert "a6b1c2d3" in codes0  # organization mapping

        # Failure case assertions
        uc1 = updated_contents[1]
        assert uc1 is not None
        assert self.col_string_ctc not in uc1
        assert self.col_regex_ctc not in uc1
        assert self.col_geo_from_ctc not in uc1
        assert self.col_time_day_ctc not in uc1
        assert self.col_num_decimal_ctc not in uc1
        assert self.col_org_ctc not in uc1

        issues1 = data_issues_list[1]
        assert issues1 is not None
        codes1 = {x.code for x in issues1}
        assert "c2d5f6a7" in codes1  # string map fail
        assert "e4f1a2b9" in codes1  # time invalid
        assert "d3e9f1a8" in codes1  # region invalid
        assert "f5a2b3c0" in codes1  # decimal invalid
        assert "a6b1c2d3" in codes1  # organization invalid


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestTransformIndividualValuesEdgeCases(BaseCaseValidatorTestCase):
    def test_empty_string_in_string_set_raises(self) -> None:
        validator = self._create_validator()
        # Prepare one content with empty string for a STRING_SET column
        contents: list[dict[UUID, str | None] | None] = [{self.col_string_ctc: ""}]
        updated_contents: list[dict[UUID, str | None] | None] = [{}]
        data_issues_list: list[list[model.CaseDataIssue] | None] = [[]]
        with pytest.raises(AssertionError):
            validator.transform_individual_values(
                contents, updated_contents, data_issues_list
            )


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestTransformValuePairs(BaseCaseValidatorTestCase):
    def test_geo_time_number_pairs_and_conflicts(self) -> None:
        validator = self._create_validator()

        # Prepare content: set from GEO region id via string to map to parent region
        # Also set TIME day to derive WEEK and set conflicting existing target value
        from_region_value: str = str(self.region_b_id)  # contained in A -> derive A
        day_value: str = "2024-01-05"  # week 01
        decimal_value: str = (
            "12.5"  # maps to interval1_b, then to interval2_y via overlap
        )

        contents: list[dict[UUID, str | None] | None] = [
            {
                self.col_geo_from_ctc: from_region_value,
                self.col_time_day_ctc: day_value,
                self.col_num_decimal_ctc: decimal_value,
                self.col_num_interval1_ctc: str(
                    self.interval1_a_id
                ),  # for interval->interval
            }
        ]
        updated_contents: list[dict[UUID, str | None] | None] = [
            {
                # Pre-populate conflicting target GEO value
                self.col_geo_to_ctc: str(uuid4()),
                # Pre-populate different WEEK to cause conflict
                self.col_time_week_ctc: "2099-W01",
                # No pre for number targets
            }
        ]
        data_issues_list: list[list[model.CaseDataIssue] | None] = [[]]

        # First, individual value transform to normalize values
        validator.transform_individual_values(
            contents, updated_contents, data_issues_list
        )
        # Then, pair transforms
        validator.transform_value_pairs(contents, updated_contents, data_issues_list)

        uc = updated_contents[0]
        assert uc is not None
        # GEO derived to container region -> conflict overwrite
        assert uc[self.col_geo_to_ctc] == str(self.region_a_id)
        # TIME derived week
        assert uc[self.col_time_week_ctc] == "2024-W01"

        # NUMBER decimal -> interval1
        assert uc[self.col_num_interval1_ctc] in {
            str(self.interval1_a_id),
            str(self.interval1_b_id),
        }

        # NUMBER interval1 -> interval2
        assert uc[self.col_num_interval2_ctc] in {
            str(self.interval2_x_id),
            str(self.interval2_y_id),
        }

        issues = data_issues_list[0]
        assert issues is not None
        codes = [x.code for x in issues]
        # Has conflict logs for GEO and TIME because we pre-populated different targets
        assert "f8d3e9a2" in codes  # GEO derived/conflict
        assert "d4e2f3a4" in codes  # TIME derived/conflict
        assert "c9d4e1f2" in codes or "a8f2d5e7" in codes  # NUMBER derived


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCalculateCaseDate(BaseCaseValidatorTestCase):
    def test_no_case_date_dim_returns(self) -> None:
        validator = self._create_validator()
        # Override complete case type to not have a case_date dim
        validator.complete_case_type.case_date_case_type_dim_id = None
        cmd, retval = self._make_cmd_and_result([{self.col_time_day_ctc: "2024-01-05"}])
        # Should not raise and not add issues
        validator.calculate_case_date(
            cmd, [retval.cases[0].validated_content], [retval.cases[0].data_issues]
        )
        assert len(retval.cases[0].data_issues) == 0

    def test_case_date_updated_and_invalid_iso_raises(self) -> None:
        validator = self._create_validator()
        # Valid ISO date -> updates case_date and logs derived
        cmd1, retval1 = self._make_cmd_and_result(
            [{self.col_time_day_ctc: "2024-02-02"}]
        )

        updated_contents = [
            None if x is None else x.validated_content for x in retval1.cases
        ]

        validator.calculate_case_date(cmd1, retval1, updated_contents)
        logs = retval1.cases[0].logs

        assert any(x.code == "b2c3d4e5" for x in logs)
        # Non ISO value -> assertion
        cmd2, retval2 = self._make_cmd_and_result([{self.col_time_day_ctc: "NOT_ISO"}])
        with pytest.raises(AssertionError):
            updated_contents = [
                None if x is None else x.validated_content for x in retval2.cases
            ]
            validator.calculate_case_date(
                cmd2,
                retval2,
                updated_contents,
            )


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestValidateAndTransformEndToEnd(BaseCaseValidatorTestCase):
    def test_pipeline_updates_and_logs(self) -> None:
        validator = self._create_validator()
        # Build one case with values that exercise multiple paths
        contents = [
            {
                self.col_string_ctc: "name1",
                self.col_num_decimal_ctc: "1.234",
                self.col_geo_from_ctc: "b",
                self.col_time_day_ctc: "2024-03-03",
                self.col_org_ctc: self.org_code,
            }
        ]
        cmd, retval = self._make_cmd_and_result(contents)  # type: ignore[arg-type]
        out = validator.validate_and_transform(cmd, retval)
        assert out is retval
        case_res = out.cases[0]
        # Updated content present
        vc = case_res.validated_content
        assert vc[self.col_string_ctc] == str(self.string_concept1_id)
        assert vc[self.col_num_decimal_ctc] == "1.23"
        # Derived week present
        assert vc[self.col_time_week_ctc] == "2024-W09"
        # Case date set and logged
        assert any(x.code == "b2c3d4e5" for x in case_res.logs)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveConceptData(BaseCaseValidatorTestCase):
    def test_retrieve_concept_data_builds_maps(self) -> None:
        complete = self._build_complete_case_type()
        # Patch init to avoid fetching metadata on construction; we want to test retrieval explicitly
        with (
            patch.object(CaseValidator, "_init_concept_metadata", return_value=None),
            patch.object(CaseValidator, "_init_region_metadata", return_value=None),
            patch.object(
                CaseValidator, "_init_organization_metadata", return_value=None
            ),
        ):
            validator = CaseValidator(self.case_service, complete, uuid4())

        # Ensure set metadata is present
        validator._init_set_metadata()

        # Build fake app.handle to return concept sets, concepts and relations
        def fake_handle(
            cmd_obj: (
                command.ConceptSetCrudCommand
                | command.ConceptCrudCommand
                | command.ConceptRelationCrudCommand
            ),
        ) -> list[model.ConceptSet | model.Concept | model.ConceptRelation]:
            if isinstance(cmd_obj, command.ConceptSetCrudCommand):
                return [
                    model.ConceptSet(
                        id=self.concept_set_string,
                        code="STR",
                        name="Strings",
                        type=enum.ConceptSetType.NOMINAL,
                    ),
                    model.ConceptSet(
                        id=self.concept_set_interval1,
                        code="INT1",
                        name="Intervals1",
                        type=enum.ConceptSetType.INTERVAL,
                    ),
                    model.ConceptSet(
                        id=self.concept_set_interval2,
                        code="INT2",
                        name="Intervals2",
                        type=enum.ConceptSetType.INTERVAL,
                    ),
                    model.ConceptSet(
                        id=self.concept_set_regex,
                        code="REGX",
                        name="Regex",
                        type=enum.ConceptSetType.REGULAR_LANGUAGE,
                        regex=r"^[A-Z]{2}\d{3}$",
                    ),
                ]
            if isinstance(cmd_obj, command.ConceptCrudCommand):
                return [
                    model.Concept(
                        id=self.string_concept1_id,
                        concept_set_id=self.concept_set_string,
                        code="CODE1",
                        name="Name1",
                    ),
                    model.Concept(
                        id=self.interval1_a_id,
                        concept_set_id=self.concept_set_interval1,
                        code="INT1_A",
                        name="[0,10)",
                        props={"lb": 0.0, "ub": 10.0, "lb_in": True, "ub_in": False},
                    ),
                    model.Concept(
                        id=self.interval1_b_id,
                        concept_set_id=self.concept_set_interval1,
                        code="INT1_B",
                        name="[10,20]",
                        props={"lb": 10.0, "ub": 20.0, "lb_in": True, "ub_in": True},
                    ),
                    model.Concept(
                        id=self.interval2_x_id,
                        concept_set_id=self.concept_set_interval2,
                        code="INT2_X",
                        name="[0,15)",
                        props={"lb": 0.0, "ub": 15.0, "lb_in": True, "ub_in": False},
                    ),
                    model.Concept(
                        id=self.interval2_y_id,
                        concept_set_id=self.concept_set_interval2,
                        code="INT2_Y",
                        name="[15,25]",
                        props={"lb": 15.0, "ub": 25.0, "lb_in": True, "ub_in": True},
                    ),
                ]
            if isinstance(cmd_obj, command.ConceptRelationCrudCommand):
                return [
                    model.ConceptRelation(
                        from_concept_id=self.interval2_y_id,
                        to_concept_id=self.interval1_b_id,
                        relation=enum.ConceptRelationType.CONTAINS,
                    )
                ]
            return []

        self.case_service.app = Mock()
        self.case_service.app.handle = Mock(side_effect=fake_handle)

        concept_sets, cset_concepts_map, concepts, concept_contained_in = (
            validator._retrieve_concept_data()
        )

        assert self.concept_set_string in concept_sets
        assert self.string_concept1_id in cset_concepts_map[self.concept_set_string]
        assert (
            concepts[self.interval1_b_id].concept_set_id == self.concept_set_interval1
        )
        # Contains relation is flipped to is-contained-in mapping (interval1 -> interval2)
        key = (self.concept_set_interval1, self.concept_set_interval2)
        assert key in concept_contained_in
        assert concept_contained_in[key][str(self.interval1_b_id)] == str(
            self.interval2_y_id
        )


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveRegionData(BaseCaseValidatorTestCase):
    def test_retrieve_region_data_builds_maps(self) -> None:
        complete = self._build_complete_case_type()
        with (
            patch.object(CaseValidator, "_init_concept_metadata", return_value=None),
            patch.object(CaseValidator, "_init_region_metadata", return_value=None),
            patch.object(
                CaseValidator, "_init_organization_metadata", return_value=None
            ),
        ):
            validator = CaseValidator(self.case_service, complete, uuid4())

        validator._init_set_metadata()

        def fake_handle(
            cmd_obj: command.RegionCrudCommand | command.RegionRelationCrudCommand,
        ) -> list[model.Region | model.RegionRelation]:
            if isinstance(cmd_obj, command.RegionCrudCommand):
                return [
                    model.Region(
                        id=self.region_a_id,
                        region_set_id=self.region_set_id,
                        code="A",
                        name="Region A",
                        centroid_lat=0.0,
                        centroid_lon=0.0,
                        center_lat=0.0,
                        center_lon=0.0,
                    ),
                    model.Region(
                        id=self.region_b_id,
                        region_set_id=self.region_set_id,
                        code="B",
                        name="Region B",
                        centroid_lat=1.0,
                        centroid_lon=1.0,
                        center_lat=1.0,
                        center_lon=1.0,
                    ),
                ]
            if isinstance(cmd_obj, command.RegionRelationCrudCommand):
                return [
                    model.RegionRelation(
                        from_region_id=self.region_a_id,
                        to_region_id=self.region_b_id,
                        relation=enum.RegionRelationType.CONTAINS,
                    ),
                    model.RegionRelation(
                        from_region_id=self.region_a_id,
                        to_region_id=self.region_b_id,
                        relation=enum.RegionRelationType.OVERLAPS_WITH,
                    ),
                ]
            return []

        self.case_service.app = Mock()
        self.case_service.app.handle = Mock(side_effect=fake_handle)

        regions, region_set_regions_map, region_contained_in = (
            validator._retrieve_region_data()
        )

        assert self.region_a_id in regions and self.region_b_id in regions
        assert self.region_set_id in region_set_regions_map
        assert self.region_a_id in region_set_regions_map[self.region_set_id]
        assert self.region_b_id in region_set_regions_map[self.region_set_id]
        # Contains relation flipped to is-contained-in mapping (B -> A)
        key = (self.region_set_id, self.region_set_id)
        assert key in region_contained_in
        assert region_contained_in[key][str(self.region_b_id)] == str(self.region_a_id)
