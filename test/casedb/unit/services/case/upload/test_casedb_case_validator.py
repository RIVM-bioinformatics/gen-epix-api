"""
Unit tests for CaseValidator in casedb case transformer.

The tests follow the structure and style of commondb upload tests and verify
public methods, with strict isolation via mocking.
"""

from __future__ import annotations

import datetime
from test.util.mock_compat import Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.model.case.complete_case_type import CompleteCaseType
from gen_epix.casedb.domain.model.case.ops_data import Case
from gen_epix.casedb.domain.model.case.ref_data import Col, Dim, RefCol, RefDim
from gen_epix.casedb.services.case.case_validator import CaseValidator
from gen_epix.commondb.domain.enum import DataIssueType
from gen_epix.commondb.domain.model.organization import Organization


class BaseCaseValidatorTestCase:
    """Base test case with common fixtures and helpers for CaseValidator tests."""

    def setup_method(self) -> None:
        # Common and reference dimension IDs
        self.user_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440000")
        self.case_type_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400aa")
        self.time_ref_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ab")
        self.geo_ref_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ac")
        self.num_ref_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ad")
        self.text_ref_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400ae")
        self.regex_ref_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400af")
        self.org_ref_dim_id: UUID = UUID("550e8400-e29b-41d4-a716-4466554400b0")

        # Col IDs (Col ids)
        self.time_day_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440101")
        self.time_week_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440102")
        self.geo_from_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440103")
        self.geo_to_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440104")
        self.num_decimal_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440105")
        self.num_interval1_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440106")
        self.num_interval2_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440107")
        self.string_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440108")
        self.regex_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440109")
        self.org_col_id: UUID = UUID("550e8400-e29b-41d4-a716-44665544010a")
        self.other_col_id: UUID = UUID("550e8400-e29b-41d4-a716-44665544010b")

        # Underlying reference column IDs
        self.time_day_ref_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440201")
        self.time_week_ref_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440202")
        self.geo_ref_col_from_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440203")
        self.geo_ref_col_to_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440204")
        self.num_decimal_ref_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440205")
        self.num_interval1_ref_col_id: UUID = UUID(
            "550e8400-e29b-41d4-a716-446655440206"
        )
        self.num_interval2_ref_col_id: UUID = UUID(
            "550e8400-e29b-41d4-a716-446655440207"
        )
        self.string_ref_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440208")
        self.regex_ref_col_id: UUID = UUID("550e8400-e29b-41d4-a716-446655440209")
        self.org_ref_col_id: UUID = UUID("550e8400-e29b-41d4-a716-44665544020a")
        self.other_ref_col_id: UUID = UUID("550e8400-e29b-41d4-a716-44665544020b")

        # Sets
        self.concept_set_string: UUID = UUID("550e8400-e29b-41d4-a716-446655440301")
        self.concept_set_interval1: UUID = UUID("550e8400-e29b-41d4-a716-446655440302")
        self.concept_set_interval2: UUID = UUID("550e8400-e29b-41d4-a716-446655440303")
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
        # RefDims
        ref_dim_time = RefDim(
            id=self.time_ref_dim_id,
            dim_type=enum.DimType.TIME,
            code="Time",
            label="Time",
            rank=1,
        )
        ref_dim_geo = RefDim(
            id=self.geo_ref_dim_id,
            dim_type=enum.DimType.GEO,
            code="Geo",
            label="Geo",
            rank=1,
        )
        ref_dim_num = RefDim(
            id=self.num_ref_dim_id,
            dim_type=enum.DimType.NUMBER,
            code="Number",
            label="Number",
            rank=1,
        )
        ref_dim_text = RefDim(
            id=self.text_ref_dim_id,
            dim_type=enum.DimType.TEXT,
            code="Text",
            label="Text",
            rank=1,
        )
        ref_dim_regex = RefDim(
            id=self.regex_ref_dim_id,
            dim_type=enum.DimType.TEXT,
            code="Regex",
            label="Regex",
            rank=1,
        )
        ref_dim_org = RefDim(
            id=self.org_ref_dim_id,
            dim_type=enum.DimType.ORGANIZATION,
            code="Org",
            label="Org",
            rank=1,
        )

        # RefCols
        ref_col_time_day = RefCol(
            id=self.time_day_ref_col_id,
            ref_dim_id=self.time_ref_dim_id,
            code="Time.Day",
            rank=1,
            col_type=enum.ColType.TIME_DAY,
        )
        ref_col_time_week = RefCol(
            id=self.time_week_ref_col_id,
            ref_dim_id=self.time_ref_dim_id,
            code="Time.Week",
            rank=2,
            col_type=enum.ColType.TIME_WEEK,
        )
        ref_col_geo_from = RefCol(
            id=self.geo_ref_col_from_id,
            ref_dim_id=self.geo_ref_dim_id,
            code="Geo.From",
            rank=1,
            col_type=enum.ColType.GEO_REGION,
            region_set_id=self.region_set_id,
        )
        ref_col_geo_to = RefCol(
            id=self.geo_ref_col_to_id,
            ref_dim_id=self.geo_ref_dim_id,
            code="Geo.To",
            rank=2,
            col_type=enum.ColType.GEO_REGION,
            region_set_id=self.region_set_id,
        )
        ref_col_num_decimal = RefCol(
            id=self.num_decimal_ref_col_id,
            ref_dim_id=self.num_ref_dim_id,
            code="Number.Decimal",
            rank=1,
            col_type=enum.ColType.DECIMAL_2,
            unit=enum.Unit.MONTH,
        )
        ref_col_num_interval1 = RefCol(
            id=self.num_interval1_ref_col_id,
            ref_dim_id=self.num_ref_dim_id,
            code="Number.Interval1",
            rank=2,
            col_type=enum.ColType.INTERVAL,
            concept_set_id=self.concept_set_interval1,
            unit=enum.Unit.YEAR,
        )
        ref_col_num_interval2 = RefCol(
            id=self.num_interval2_ref_col_id,
            ref_dim_id=self.num_ref_dim_id,
            code="Number.Interval2",
            rank=3,
            col_type=enum.ColType.INTERVAL,
            concept_set_id=self.concept_set_interval2,
            unit=enum.Unit.QUARTER,
        )
        ref_col_string = RefCol(
            id=self.string_ref_col_id,
            ref_dim_id=self.text_ref_dim_id,
            code="Text.String",
            rank=1,
            col_type=enum.ColType.NOMINAL,
            concept_set_id=self.concept_set_string,
        )
        ref_col_regex = RefCol(
            id=self.regex_ref_col_id,
            ref_dim_id=self.regex_ref_dim_id,
            code="Regex.Pattern",
            rank=2,
            col_type=enum.ColType.REGULAR_LANGUAGE,
            regex=r"^[A-Z]{2}\d{3}$",
        )
        ref_col_org = RefCol(
            id=self.org_ref_col_id,
            ref_dim_id=self.org_ref_dim_id,
            code="Org.Org",
            rank=1,
            col_type=enum.ColType.ORGANIZATION,
        )
        ref_col_other = RefCol(
            id=self.other_ref_col_id,
            ref_dim_id=self.text_ref_dim_id,
            code="Text.Other",
            rank=99,
            col_type=enum.ColType.OTHER,
        )

        time_dim = Dim(
            id=self.time_ref_dim_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.time_ref_dim_id,
            occurrence=0,
            code="Time",
            rank=1,
            is_case_date_dim=True,
        )
        geo_dim = Dim(
            id=self.geo_ref_dim_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.geo_ref_dim_id,
            occurrence=0,
            code="Geo",
            rank=2,
        )
        num_dim = Dim(
            id=self.num_ref_dim_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.num_ref_dim_id,
            occurrence=0,
            code="Number",
            rank=3,
        )
        text_dim = Dim(
            id=self.text_ref_dim_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.text_ref_dim_id,
            occurrence=0,
            code="Text",
            rank=4,
        )
        regex_dim = Dim(
            id=self.regex_ref_dim_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.regex_ref_dim_id,
            occurrence=0,
            code="Regex",
            rank=5,
        )
        org_dim = Dim(
            id=self.org_ref_dim_id,
            case_type_id=self.case_type_id,
            ref_dim_id=self.org_ref_dim_id,
            occurrence=0,
            code="Org",
            rank=6,
        )

        # Cols
        time_day_col = Col(
            id=self.time_day_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.time_ref_dim_id,
            ref_col_id=self.time_day_ref_col_id,
            code="Time.Day",
            rank=1,
        )
        time_week_col = Col(
            id=self.time_week_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.time_ref_dim_id,
            ref_col_id=self.time_week_ref_col_id,
            code="Time.Week",
            rank=2,
        )
        geo_from_col = Col(
            id=self.geo_from_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.geo_ref_dim_id,
            ref_col_id=self.geo_ref_col_from_id,
            code="Geo.From",
            rank=1,
        )
        geo_to_col = Col(
            id=self.geo_to_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.geo_ref_dim_id,
            ref_col_id=self.geo_ref_col_to_id,
            code="Geo.To",
            rank=2,
        )
        num_decimal_col = Col(
            id=self.num_decimal_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.num_ref_dim_id,
            ref_col_id=self.num_decimal_ref_col_id,
            code="Number.Decimal",
            rank=1,
        )
        num_interval1_col = Col(
            id=self.num_interval1_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.num_ref_dim_id,
            ref_col_id=self.num_interval1_ref_col_id,
            code="Number.Interval1",
            rank=2,
        )
        num_interval2_col = Col(
            id=self.num_interval2_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.num_ref_dim_id,
            ref_col_id=self.num_interval2_ref_col_id,
            code="Number.Interval2",
            rank=3,
        )
        string_col = Col(
            id=self.string_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.text_ref_dim_id,
            ref_col_id=self.string_ref_col_id,
            code="Text.String",
            rank=1,
        )
        regex_col = Col(
            id=self.regex_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.regex_ref_dim_id,
            ref_col_id=self.regex_ref_col_id,
            code="Regex.Pattern",
            rank=2,
        )
        org_col = Col(
            id=self.org_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.org_ref_dim_id,
            ref_col_id=self.org_ref_col_id,
            code="Org.Org",
            rank=1,
        )
        other_col = Col(
            id=self.other_col_id,
            case_type_id=self.case_type_id,
            dim_id=self.text_ref_dim_id,
            ref_col_id=self.other_ref_col_id,
            code="Text.Other",
            rank=99,
        )

        complete_case_type = CompleteCaseType(
            id=self.case_type_id,
            user_id=self.user_id,
            name="Test CT",
            etiologies={},
            etiological_agents={},
            ref_dims={
                self.time_ref_dim_id: ref_dim_time,
                self.geo_ref_dim_id: ref_dim_geo,
                self.num_ref_dim_id: ref_dim_num,
                self.text_ref_dim_id: ref_dim_text,
                self.regex_ref_dim_id: ref_dim_regex,
                self.org_ref_dim_id: ref_dim_org,
            },
            ref_cols={
                self.time_day_ref_col_id: ref_col_time_day,
                self.time_week_ref_col_id: ref_col_time_week,
                self.geo_ref_col_from_id: ref_col_geo_from,
                self.geo_ref_col_to_id: ref_col_geo_to,
                self.num_decimal_ref_col_id: ref_col_num_decimal,
                self.num_interval1_ref_col_id: ref_col_num_interval1,
                self.num_interval2_ref_col_id: ref_col_num_interval2,
                self.string_ref_col_id: ref_col_string,
                self.regex_ref_col_id: ref_col_regex,
                self.org_ref_col_id: ref_col_org,
                self.other_ref_col_id: ref_col_other,
            },
            dims={
                self.time_ref_dim_id: time_dim,
                self.geo_ref_dim_id: geo_dim,
                self.num_ref_dim_id: num_dim,
                self.text_ref_dim_id: text_dim,
                self.regex_ref_dim_id: regex_dim,
                self.org_ref_dim_id: org_dim,
            },
            cols={
                self.time_day_col_id: time_day_col,
                self.time_week_col_id: time_week_col,
                self.geo_from_col_id: geo_from_col,
                self.geo_to_col_id: geo_to_col,
                self.num_decimal_col_id: num_decimal_col,
                self.num_interval1_col_id: num_interval1_col,
                self.num_interval2_col_id: num_interval2_col,
                self.string_col_id: string_col,
                self.regex_col_id: regex_col,
                self.org_col_id: org_col,
                self.other_col_id: other_col,
            },
            genetic_distance_protocols={},
            tree_algorithms={},
            case_type_access_abacs={},
            case_type_share_abacs={},
            case_date_dim_id=self.time_ref_dim_id,
        )
        return complete_case_type

    def _concept_data(self) -> tuple[
        dict[UUID, set[UUID]],
        dict[UUID, model.Concept],
        dict[tuple[UUID, UUID], dict[str, str]],
    ]:
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
        }
        concept_contained_in: dict[tuple[UUID, UUID], dict[str, str]] = {}
        return concept_set_concepts_map, concepts, concept_contained_in  # type: ignore[return-value]

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
        return [Organization(id=self.org_id, name=self.org_name, code=self.org_code)]

    def _create_validator(self) -> CaseValidator:
        complete_case_type = self._build_complete_case_type()
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
            validator = CaseValidator(self.case_service, complete_case_type, uuid4())
        return validator

    def _make_cmd_and_result(
        self,
        case_contents: list[dict[UUID, str | None]],
    ) -> tuple[command.UploadCasesCommand, model.CaseBatchUploadResult]:
        # Use a single created_in_data_collection_id across all cases and the command
        created_in_data_collection_id: UUID = uuid4()
        cases_for_upload: list[model.CaseForUpload] = []
        case_results: list[model.CaseUploadResult] = []
        for content in case_contents:
            c = Case(
                id=uuid4(),
                code=None,
                case_type_id=self.case_type_id,
                created_in_data_collection_id=created_in_data_collection_id,
                content=content,
            )
            cases_for_upload.append(model.CaseForUpload(case=c))
            # Initialize validated_content with the original content so timed_at
            # calculation can operate on the expected updated values without
            # needing the full validation pipeline.
            case_results.append(
                model.CaseUploadResult(id=c.id, validated_content=c.content.copy())
            )

        batch = model.CaseBatchForUpload(cases=cases_for_upload)
        cmd = command.UploadCasesCommand(
            case_type_id=self.case_type_id,
            default_created_in_data_collection_id=created_in_data_collection_id,
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
        assert issue.col_id == unknown_col_id
        assert issue.data_issue_type == DataIssueType.INVALID
        assert issue.code == "ef8e4d6d"


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestTransformIndividualValues(BaseCaseValidatorTestCase):
    def test_all_branches(self) -> None:
        validator = self._create_validator()
        # Prepare contents with values for each type
        contents: list[dict[UUID, str | None] | None] = [
            {
                self.string_col_id: "code1",  # maps to concept id (case-insensitive)
                self.regex_col_id: "AB123",  # matches pattern
                self.geo_from_col_id: "a",  # maps to region id
                self.time_day_col_id: "2023-02-05",  # valid day
                self.num_decimal_col_id: "3.1415",  # rounded
                self.org_col_id: self.org_name,
                self.other_col_id: "keep",
            },
            {
                self.string_col_id: "unknown",  # cannot map
                self.regex_col_id: "xx",  # invalid
                self.geo_from_col_id: "unknown",  # cannot map
                self.time_day_col_id: "invalid-date",  # invalid
                self.num_decimal_col_id: "oops",  # invalid
                self.org_col_id: "unknown-org",
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
        assert uc0[self.string_col_id] == str(self.string_concept1_id)
        assert uc0[self.regex_col_id] == "AB123"
        # region mapping
        assert uc0[self.geo_from_col_id] == str(self.region_a_id)
        # time day copied
        assert uc0[self.time_day_col_id] == "2023-02-05"
        # number rounded
        assert uc0[self.num_decimal_col_id] == "3.14"
        # organization
        assert uc0[self.org_col_id] == str(self.org_id)
        # other passthrough
        assert uc0[self.other_col_id] == "keep"

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
        assert self.string_col_id not in uc1
        assert self.regex_col_id not in uc1
        assert self.geo_from_col_id not in uc1
        assert self.time_day_col_id not in uc1
        assert self.num_decimal_col_id not in uc1
        assert self.org_col_id not in uc1

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
        contents: list[dict[UUID, str | None] | None] = [{self.string_col_id: ""}]
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
            "12.5"  # 12.5 months -> interval1_a in years -> interval2_x in quarters
        )

        contents: list[dict[UUID, str | None] | None] = [
            {
                self.geo_from_col_id: from_region_value,
                self.time_day_col_id: day_value,
                self.num_decimal_col_id: decimal_value,
                self.num_interval1_col_id: str(
                    self.interval1_a_id
                ),  # for interval->interval
            }
        ]
        updated_contents: list[dict[UUID, str | None] | None] = [
            {
                # Pre-populate conflicting target GEO value
                self.geo_to_col_id: str(uuid4()),
                # Pre-populate different WEEK to cause conflict
                self.time_week_col_id: "2099-W01",
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
        assert uc[self.geo_to_col_id] == str(self.region_a_id)
        # TIME derived week
        assert uc[self.time_week_col_id] == "2024-W01"

        # NUMBER decimal -> interval1 using month -> year conversion
        assert uc[self.num_interval1_col_id] == str(self.interval1_a_id)

        # NUMBER interval1 -> interval2 using year -> quarter conversion
        assert uc[self.num_interval2_col_id] == str(self.interval2_x_id)

        issues = data_issues_list[0]
        assert issues is not None
        codes = [x.code for x in issues]
        # Has conflict logs for GEO and TIME because we pre-populated different targets
        assert "f8d3e9a2" in codes  # GEO derived/conflict
        assert "d4e2f3a4" in codes  # TIME derived/conflict
        assert "c9d4e1f2" in codes or "a8f2d5e7" in codes  # NUMBER derived


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestNumberPairReverseDirectionGuard(BaseCaseValidatorTestCase):
    """Regression test for LSP-3417.

    ``_get_col_pairs`` generates both directions, so after interval2 is derived
    from a supplied interval1, the subsequent reverse pair (interval2 ->
    interval1) must NOT overwrite the originally supplied interval1 value. The
    early-continue guard in ``_transform_interval_to_interval`` enforces this.
    """

    def test_derived_interval_target_does_not_overwrite_source(self) -> None:
        concept_set_concepts_map, concepts, concept_contained_in = self._concept_data()
        concepts[self.interval2_x_id].props = {
            "lb": 0.0,
            "ub": 40.0,
            "lb_in": True,
            "ub_in": False,
        }
        concepts[self.interval2_y_id].props = {
            "lb": 40.0,
            "ub": 80.0,
            "lb_in": True,
            "ub_in": True,
        }
        with patch.object(
            self,
            "_concept_data",
            return_value=(
                concept_set_concepts_map,
                concepts,
                concept_contained_in,
            ),
        ):
            validator = self._create_validator()

        # A [0,10) years maps to X [0,40) quarters. The reverse pair must
        # leave the supplied A value untouched.
        contents: list[dict[UUID, str | None] | None] = [
            {self.num_interval1_col_id: str(self.interval1_a_id)}
        ]
        cmd, retval = self._make_cmd_and_result(contents)  # type: ignore[arg-type]
        out = validator.validate_and_transform(cmd, retval)

        uc = out.cases[0].validated_content
        # Source interval1 remains exactly as supplied.
        assert uc[self.num_interval1_col_id] == str(self.interval1_a_id)
        # Forward derivation still populated interval2.
        assert uc[self.num_interval2_col_id] == str(self.interval2_x_id)
        # No conflict/derived issue rewrote the supplied interval1 value.
        interval1_issues = [
            x
            for x in out.cases[0].data_issues
            if x.col_id == self.num_interval1_col_id
            and x.code in {"c9d4e1f2", "a8f2d5e7"}
        ]
        assert interval1_issues == []

    def test_guard_skips_prepopulated_reverse_target(self) -> None:
        # Directly exercise the guard on the reverse pair (interval2 ->
        # interval1) with interval1 already populated. Even though the reverse
        # transformer can map interval2 to a (possibly different) interval1
        # value, the guard must skip the write.
        validator = self._create_validator()
        ref_col_interval2 = validator.complete_case_type.ref_cols[
            self.num_interval2_ref_col_id
        ]
        ref_col_interval1 = validator.complete_case_type.ref_cols[
            self.num_interval1_ref_col_id
        ]
        assert ref_col_interval2.unit is not None
        assert ref_col_interval1.unit is not None
        col_pair = (self.num_interval2_col_id, self.num_interval1_col_id)

        contents: list[dict[UUID, str | None] | None] = [
            {self.num_interval1_col_id: str(self.interval1_b_id)}
        ]
        updated_contents: list[dict[UUID, str | None] | None] = [
            {
                self.num_interval2_col_id: str(self.interval2_x_id),
                self.num_interval1_col_id: str(self.interval1_b_id),
            }
        ]
        data_issues_list: list[list[model.CaseDataIssue] | None] = [[]]

        validator._transform_interval_to_interval(
            contents,
            updated_contents,
            data_issues_list,
            col_pair,
            ref_col_interval2,
            ref_col_interval1,
            CaseValidator.UNIT_PAIR_MULTIPLIER_MAP[
                (ref_col_interval2.unit, ref_col_interval1.unit)
            ],
        )

        uc = updated_contents[0]
        assert uc is not None
        # Pre-populated interval1 value preserved, no derived/conflict logged.
        assert uc[self.num_interval1_col_id] == str(self.interval1_b_id)
        assert data_issues_list[0] == []


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestCalculateCaseDate(BaseCaseValidatorTestCase):
    def test_no_case_date_dim_returns(self) -> None:
        validator = self._create_validator()
        # Override complete CaseType to not have a case_date_dim
        validator.complete_case_type.case_date_dim_id = None
        cmd, retval = self._make_cmd_and_result([{self.time_day_col_id: "2024-01-05"}])
        # Should not raise and not add issues
        validator.calculate_case_date(cmd, retval, [retval.cases[0].validated_content])
        assert len(retval.cases[0].data_issues) == 0

    def test_uses_highest_resolution_col_when_multiple_time_cols_present(self) -> None:
        validator = self._create_validator()
        cmd, retval = self._make_cmd_and_result([{}])
        # Both day and week present; day (higher resolution) must win
        updated_contents: list[dict[UUID, str | None] | None] = [
            {
                self.time_day_col_id: "2024-03-15",
                self.time_week_col_id: "2024-W01",  # would give 2024-01-01 if used
            }
        ]
        validator.calculate_case_date(cmd, retval, updated_contents)
        case = cmd.case_batch.cases[0].case
        assert case is not None
        assert case.timed_at == datetime.datetime(2024, 3, 15)

    def test_case_date_updated_and_invalid_iso_raises(self) -> None:
        validator = self._create_validator()
        # Valid ISO date -> updates timed_at and logs derived
        cmd1, retval1 = self._make_cmd_and_result(
            [{self.time_day_col_id: "2024-02-02"}]
        )

        updated_contents: list[dict[UUID, str | None] | None] = [
            None if x is None else x.validated_content for x in retval1.cases
        ]

        validator.calculate_case_date(cmd1, retval1, updated_contents)
        logs = retval1.cases[0].logs

        assert any(x.code == "b2c3d4e5" for x in logs)
        # Non ISO value -> assertion
        cmd2, retval2 = self._make_cmd_and_result([{self.time_day_col_id: "NOT_ISO"}])
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
                self.string_col_id: "name1",
                self.num_decimal_col_id: "1.234",
                self.geo_from_col_id: "b",
                self.time_day_col_id: "2024-03-03",
                self.org_col_id: self.org_code,
            }
        ]
        cmd, retval = self._make_cmd_and_result(contents)  # type: ignore[arg-type]
        out = validator.validate_and_transform(cmd, retval)
        assert out is retval
        case_res = out.cases[0]
        # Updated content present
        vc = case_res.validated_content
        assert vc[self.string_col_id] == str(self.string_concept1_id)
        assert vc[self.num_decimal_col_id] == "1.23"
        assert vc[self.num_interval1_col_id] == str(self.interval1_a_id)
        assert vc[self.num_interval2_col_id] == str(self.interval2_x_id)
        # Derived week present
        assert vc[self.time_week_col_id] == "2024-W09"
        # Case date set and logged
        assert any(x.code == "b2c3d4e5" for x in case_res.logs)


@pytest.mark.scenario_ids("TC-SEC-29-02")
class TestRetrieveConceptData(BaseCaseValidatorTestCase):
    def test_retrieve_concept_data_builds_maps(self) -> None:
        complete_case_type = self._build_complete_case_type()
        # Patch init to avoid fetching metadata on construction; we want to test retrieval explicitly
        with (
            patch.object(CaseValidator, "_init_concept_metadata", return_value=None),
            patch.object(CaseValidator, "_init_region_metadata", return_value=None),
            patch.object(
                CaseValidator, "_init_organization_metadata", return_value=None
            ),
        ):
            validator = CaseValidator(self.case_service, complete_case_type, uuid4())

        # Ensure set metadata is present
        validator._init_set_metadata()

        # Build fake app.handle to return concepts and relations
        def fake_handle(
            cmd_obj: command.ConceptCrudCommand | command.ConceptRelationCrudCommand,
        ) -> list[model.Concept | model.ConceptRelation]:
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

        cset_concepts_map, concepts, concept_contained_in = (
            validator._retrieve_concept_data()
        )

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
