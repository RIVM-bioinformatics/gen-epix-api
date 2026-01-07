import re
from decimal import Decimal, InvalidOperation
from itertools import combinations
from typing import NoReturn
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.enum import (
    ColType,
    ColTypeSet,
    ConceptRelationType,
    DataIssueType,
    RegionRelationType,
)
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_date import (
    case_service_get_case_date_case_type_col_mappers_from_cols,
)
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import UuidSetFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.enum import NoMatchStrategy, TimeUnit, TimeUnitTransformStrategy
from gen_epix.transform.transformers import IntervalTransformer
from gen_epix.transform.transformers.interval import IntervalToIntervalTransformer
from gen_epix.transform.transformers.iso_time import IsoTimeTransformer
from gen_epix.util import map_paired_elements


class CaseValidator:
    N_DECIMALS = {
        ColType.DECIMAL_0: 0,
        ColType.DECIMAL_1: 1,
        ColType.DECIMAL_2: 2,
        ColType.DECIMAL_3: 3,
        ColType.DECIMAL_4: 4,
        ColType.DECIMAL_5: 5,
        ColType.DECIMAL_6: 6,
    }

    FLOAT_PATTERN = re.compile(
        r"^[+-]?("
        r"(?:\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"  # normal floats + scientific notation
        r"|inf(?:inity)?"  # inf / infinity
        r"|nan"  # nan
        r")$",
        re.IGNORECASE,
    )

    DECIMAL_PATTERN = re.compile(r"^[+-]?([0-9]*[.,])?[0-9]+$")

    TIME_YEAR_PATTERN = re.compile(r"^\d{4}$")
    TIME_QUARTER_PATTERN = re.compile(r"^\d{4}-Q[1-4]$")
    TIME_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
    TIME_WEEK_PATTERN = re.compile(r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")
    TIME_DAY_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")

    TIME_MATCHERS = {
        ColType.TIME_YEAR: lambda x: (
            x if x is None or CaseValidator.TIME_YEAR_PATTERN.match(x) else NoReturn
        ),
        ColType.TIME_QUARTER: lambda x: (
            x if x is None or CaseValidator.TIME_QUARTER_PATTERN.match(x) else NoReturn
        ),
        ColType.TIME_MONTH: lambda x: (
            x if x is None or CaseValidator.TIME_MONTH_PATTERN.match(x) else NoReturn
        ),
        ColType.TIME_WEEK: lambda x: (
            x if x is None or CaseValidator.TIME_WEEK_PATTERN.match(x) else NoReturn
        ),
        ColType.TIME_DAY: lambda x: (
            x if x is None or CaseValidator.TIME_DAY_PATTERN.match(x) else NoReturn
        ),
    }

    COL_TYPE_TO_TIME_UNIT = {
        ColType.TIME_YEAR: TimeUnit.YEAR,
        ColType.TIME_QUARTER: TimeUnit.QUARTER,
        ColType.TIME_MONTH: TimeUnit.MONTH,
        ColType.TIME_WEEK: TimeUnit.WEEK,
        ColType.TIME_DAY: TimeUnit.DAY,
    }

    @staticmethod
    def _transform_decimal(value: str | None, n_decimals: int) -> str | None | NoReturn:
        if value is None:
            return None
        if CaseValidator.DECIMAL_PATTERN.match(value) is None:
            return NoReturn
        try:
            num_value = round(Decimal(value), n_decimals)
            return str(num_value)
        except (ValueError, InvalidOperation):
            return NoReturn

    def __init__(
        self,
        case_service: BaseCaseService,
        complete_case_type: model.CompleteCaseType,
        user_id: UUID,
    ):
        self.case_service = case_service
        self.complete_case_type = complete_case_type
        self.user_id = user_id
        # Unique concept and region sets across the complete case type
        self.concept_set_ids: set[UUID] = set()
        self.interval_concept_set_ids: set[UUID] = set()
        self.regex_concept_set_ids: set[UUID] = set()
        self.region_set_ids: set[UUID] = set()
        # dict[concept_set_id, dict[lower(str(concept_id)|abbrevation|name), concept_id]]
        self.concept_value_maps: dict[UUID, dict[str, str]] = {}
        # dict[(from_concept_set_id, to_concept_set_id), dict[from_concept_id, to_concept_id]]
        self.concept_relation_maps: dict[tuple[UUID, UUID], dict[str, str]] = {}
        # dict[to_concept_set_id, IntervalTransformer]
        self.interval_transformers: dict[UUID, IntervalTransformer] = {}
        # dict[concept_set_id, pattern_matcher]
        self.regex_patterns: dict[UUID, re.Pattern] = {}
        # dict[region_set_id, dict[lower(str(region_id)|code|name), region_id]]
        self.region_value_maps: dict[UUID, dict[str, str]] = {}
        # dict[(from_region_set_id, to_region_set_id), dict[from_region_id, to_region_id]]
        self.region_relation_maps: dict[tuple[UUID, UUID], dict[str, str]] = {}
        # dict[from_region_id, to_region_id] - flattened mapping across all region sets
        self.region_contained_in: dict[UUID, UUID] = {}
        # dict[region_id, region_object] - for looking up region details
        self.regions: dict[UUID, model.Region] = {}
        # dict[lower(str(organization_id)|name|legal_entity_code), concept_id]
        self.organization_value_map: dict[str, str] = {}

        self._init_metadata()

    def validate_and_transform(
        self, cmd: command.UploadCasesCommand, retval: model.CaseBatchUploadResult
    ) -> model.CaseBatchUploadResult:
        """
        Validate and transform the content of the cases in batch upload command.
        Where applicable, individual values are transformed from synonymous values to
        standard values, and combinations of values are transformed based on defined
        relations.

        The method adds resulting ValidatedCaseForUpload to the upload result,
        including any data issues found during validation and transformation.
        """
        contents, updated_contents, data_issues_list = self._get_content_references(
            cmd, retval
        )
        self.validate_unknown_columns(contents, data_issues_list)
        self.transform_individual_values(contents, updated_contents, data_issues_list)
        self.transform_value_pairs(contents, updated_contents, data_issues_list)
        self.calculate_case_date(cmd, updated_contents, data_issues_list)

        return retval

    def _get_content_references(
        self,
        cmd: command.UploadCasesCommand,
        retval: model.CaseBatchUploadResult,
    ) -> tuple[
        list[dict[UUID, str | None] | None],
        list[dict[UUID, str | None] | None],
        list[list[model.CaseDataIssue] | None],
    ]:
        """
        Get references to contents, updated_contents and data_issues_list for all
        cases, as a convenience for easily updating these in-place.
        """
        if cmd.case_type_id != self.complete_case_type.id:
            raise ValueError("Cases are not for the correct case type")

        # Get contents, updated_contents and data_issues_list references
        contents = [
            None if x.case is None else x.case.content for x in cmd.case_batch.cases
        ]
        updated_contents = [
            None if x is None else x.validated_content for x in retval.cases
        ]
        data_issues_list = [None if x is None else x.data_issues for x in retval.cases]

        return contents, updated_contents, data_issues_list

    def validate_unknown_columns(
        self,
        contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
    ) -> None:
        """Handle any unknown case type columns and add appropriate data issues."""
        for content, data_issues in zip(contents, data_issues_list):
            if content is None:
                continue
            assert data_issues is not None
            for case_type_col_id in content.keys():
                if case_type_col_id in self.complete_case_type.case_type_cols:
                    continue
                # Unknown case type col
                data_issues.append(
                    model.CaseDataIssue(
                        case_type_col_id=case_type_col_id,
                        original_value=content[case_type_col_id],
                        updated_value=None,
                        data_issue_type=DataIssueType.UNAUTHORIZED,
                        code="a7b3f9d2",
                        message="Unknown case type column",
                    )
                )

    def transform_individual_values(
        self,
        contents: list[dict[UUID, str | None] | None],
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
    ) -> None:
        """Validate and transform individual values."""
        msg_template = "{orig_value}"
        for case_type_col in self.complete_case_type.case_type_cols.values():
            case_type_col_id = case_type_col.id
            assert case_type_col_id is not None
            col = self.complete_case_type.cols[case_type_col.col_id]
            if col.col_type == ColType.REGULAR_LANGUAGE:
                pattern = self.regex_patterns[
                    col.concept_set_id
                ]  # type:ignore[arg-type]
                transform_fn = lambda x: (
                    x if x is None or pattern.match(x) else NoReturn
                )
                code = "b1c4e5f6"
                msg_template = "{orig_value} does not match regex"
            elif col.col_type in ColTypeSet.STRING_SET.value:
                concept_set_id = col.concept_set_id
                assert concept_set_id is not None
                concept_value_map = self.concept_value_maps[concept_set_id]
                transform_fn = lambda x: (
                    concept_value_map.get(x.lower(), NoReturn) if x else None
                )
                code = "c2d5f6a7"
                msg_template = "{orig_value} cannot be mapped to concept"
            elif col.col_type in ColTypeSet.HAS_REGION_SET.value:
                assert col.region_set_id
                region_value_map = self.region_value_maps[col.region_set_id]
                transform_fn = lambda x: (
                    region_value_map.get(x.lower(), NoReturn) if x else None
                )
                code = "d3e9f1a8"
                msg_template = "{orig_value} cannot be mapped to region"
            elif col.col_type in ColTypeSet.TIME.value:
                transform_fn = self.TIME_MATCHERS[col.col_type]
                code = "e4f1a2b9"
                msg_template = (
                    "{orig_value} is not a valid " + col.col_type.value + " value"
                )
            elif col.col_type in ColTypeSet.NUMBER.value:
                n_decimals = self.N_DECIMALS[col.col_type]
                code = "f5a2b3c0"
                transform_fn = lambda x: CaseValidator._transform_decimal(x, n_decimals)
            elif col.col_type == ColType.ORGANIZATION:
                organization_value_map = self.organization_value_map
                transform_fn = lambda x: (
                    organization_value_map.get(x.lower(), NoReturn) if x else None
                )
                code = "a6b1c2d3"
                msg_template = "{orig_value} cannot be mapped to organization"
            else:
                # TODO: transform any other col_types
                code = "8f7a2d1b"
                transform_fn = lambda x: x
            # Update value
            for content, updated_content, data_issues in zip(
                contents, updated_contents, data_issues_list
            ):
                if content is None:
                    continue
                assert updated_content is not None
                assert data_issues is not None
                if case_type_col_id not in content:
                    continue
                orig_value = content[case_type_col_id]
                new_value: str | None | NoReturn = transform_fn(orig_value)  # type: ignore[assignment]
                if new_value == NoReturn:
                    new_value = None
                    # No mapping found
                    data_issues.append(
                        model.CaseDataIssue(
                            case_type_col_id=case_type_col_id,
                            original_value=orig_value,
                            updated_value=new_value,
                            data_issue_type=DataIssueType.INVALID,
                            code=code,
                            message=msg_template.format(orig_value=orig_value),
                        )
                    )
                    # None is not added to updated_content, since an explicit None value is interpreted as deletion of a value during update
                    continue
                if new_value != orig_value:
                    # Value transformed
                    data_issues.append(
                        model.CaseDataIssue(
                            case_type_col_id=case_type_col_id,
                            original_value=orig_value,
                            updated_value=new_value,
                            data_issue_type=DataIssueType.DERIVED,
                            code=code,
                            message="Value transformed",
                        )
                    )
                    if new_value is None:
                        raise AssertionError(
                            f"Unexpected None value after transformation of value {orig_value} for case type column {case_type_col_id}"
                        )
                # Add to updated_content
                updated_content[case_type_col_id] = new_value

    def transform_value_pairs(
        self,
        contents: list[dict[UUID, str | None] | None],
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
    ) -> None:
        """
        Validate and transform pairs of values.
        This method assumes that only standard values are present in updated_contents.
        """

        # Go over each case type dimension
        for case_type_dim in self.complete_case_type.case_type_dims.values():
            assert case_type_dim.id is not None
            dim_type = self.complete_case_type.dims[case_type_dim.dim_id]
            case_type_col_ids = (
                self.complete_case_type.ordered_case_type_col_ids_by_dim[
                    case_type_dim.id
                ]
            )
            # Handle each type of dimension
            if dim_type.dim_type == enum.DimType.GEO:
                col_pairs = CaseValidator._get_col_pairs(case_type_col_ids)
                self._transform_geo_value_pairs(
                    contents, updated_contents, data_issues_list, col_pairs
                )
            elif dim_type.dim_type == enum.DimType.TIME:
                # Sort col_pairs by time resolution descending (DAY, WEEK, MONTH, QUARTER, YEAR)
                case_type_col_ids.sort(
                    key=lambda x: enum.ColTypeOrder.TIME_RESOLUTION_DESC.value.get(
                        self.complete_case_type.cols[
                            self.complete_case_type.case_type_cols[x].col_id
                        ].col_type,
                        len(case_type_col_ids),
                    )
                )
                col_pairs = CaseValidator._get_col_pairs(case_type_col_ids)
                self._transform_time_value_pairs(
                    contents, updated_contents, data_issues_list, col_pairs
                )
            elif dim_type.dim_type == enum.DimType.NUMBER:
                col_pairs = CaseValidator._get_col_pairs(case_type_col_ids)
                self._transform_number_value_pairs(
                    contents, updated_contents, data_issues_list, col_pairs
                )
            elif dim_type.dim_type == enum.DimType.TEXT:
                pass
            else:
                continue

    def calculate_case_date(
        self,
        cmd: command.UploadCasesCommand,
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
    ) -> None:
        """Calculate case date based on TIME dimension columns."""
        # Determine case type columns from which the case date needs to be derived
        # Calculate case date where possible
        case_date_case_type_dim_id = self.complete_case_type.case_date_case_type_dim_id
        if case_date_case_type_dim_id is None:
            case_date_case_type_col_mappers = {}
        else:
            case_type_cols = [
                self.complete_case_type.case_type_cols[x]
                for x in self.complete_case_type.ordered_case_type_col_ids_by_dim[
                    case_date_case_type_dim_id
                ]
            ]
            case_date_case_type_col_mappers = (
                case_service_get_case_date_case_type_col_mappers_from_cols(
                    case_type_cols,
                    self.complete_case_type.cols,
                )
            )
        if not case_date_case_type_col_mappers:
            # No case date columns defined, skip calculation
            return

        # Calculate case dates
        for case_for_upload, updated_content, data_issues in zip(
            cmd.case_batch.cases, updated_contents, data_issues_list
        ):
            case = case_for_upload.case
            if case is None:
                continue
            assert updated_content is not None
            assert data_issues is not None
            for case_type_col_id, mapper in case_date_case_type_col_mappers.items():
                iso_datetime_value: str | None = case.content.get(case_type_col_id)
                if iso_datetime_value is None:
                    continue
                orig_case_date = case.case_date
                case.case_date = mapper(iso_datetime_value)
                if case.case_date != orig_case_date:
                    data_issues.append(
                        model.CaseDataIssue(
                            case_type_col_id=case_type_col_id,
                            original_value=iso_datetime_value,
                            updated_value=str(case.case_date),
                            data_issue_type=DataIssueType.DERIVED,
                            code="b2c3d4e5",
                            message="Case date updated",
                        )
                    )

    def _transform_geo_value_pairs(
        self,
        contents: list[dict[UUID, str | None] | None],
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
        col_pairs: list[tuple[UUID, UUID]],
    ) -> None:
        """
        Validate and transform GEO pairs of values.
        Applies only to GEO_REGION-GEO_REGION column pairs.
        """
        for col_pair in col_pairs:
            col1 = self.complete_case_type.cols[
                self.complete_case_type.case_type_cols[col_pair[0]].col_id
            ]
            col2 = self.complete_case_type.cols[
                self.complete_case_type.case_type_cols[col_pair[1]].col_id
            ]
            if (
                col1.col_type != ColType.GEO_REGION
                or col2.col_type != ColType.GEO_REGION
            ):
                continue
            assert col1.region_set_id is not None
            assert col2.region_set_id is not None
            region_relation_map = self.region_relation_maps.get(
                (col1.region_set_id, col2.region_set_id), {}
            )
            for content, updated_content, data_issues in zip(
                contents, updated_contents, data_issues_list
            ):
                if content is None:
                    continue
                assert updated_content is not None
                assert data_issues is not None
                from_region_id = updated_content.get(col_pair[0])
                if from_region_id is None:
                    continue
                to_region_id = region_relation_map.get(from_region_id)
                if to_region_id is None:
                    continue

                self._set_derived_value(
                    content,
                    updated_content,
                    data_issues,
                    "f8d3e9a2",
                    col_pair,
                    to_region_id,
                )

    def _transform_time_value_pairs(
        self,
        contents: list[dict[UUID, str | None] | None],
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
        col_pairs: list[tuple[UUID, UUID]],
    ) -> None:
        """Validate and transform TIME pairs of values."""
        # For TIME dim: use IsoTimeTransformer with TimeUnitTransformStrategy.EXACT_ONLY to transform from-values to to-values. When no transformation is possible (e.g. from MONTH to DAY), skip that pair of cols to avoid a call to the IsoTimeTransformer.
        for col_pair in col_pairs:
            col1 = self.complete_case_type.cols[
                self.complete_case_type.case_type_cols[col_pair[0]].col_id
            ]
            col2 = self.complete_case_type.cols[
                self.complete_case_type.case_type_cols[col_pair[1]].col_id
            ]
            # Skip if columns are not TIME types
            if (
                col1.col_type not in ColTypeSet.TIME.value
                or col2.col_type not in ColTypeSet.TIME.value
            ):
                continue

            from_time_unit = self.COL_TYPE_TO_TIME_UNIT[col1.col_type]
            to_time_unit = self.COL_TYPE_TO_TIME_UNIT[col2.col_type]

            # Skip if transformation is not possible
            if not IsoTimeTransformer.can_transform_time(from_time_unit, to_time_unit):
                continue

            # Create IsoTimeTransformer for this transformation
            time_transformer = IsoTimeTransformer(
                field_name="time_value",
                src_unit=from_time_unit,
                tgt_unit=to_time_unit,
                strategy=TimeUnitTransformStrategy.EXACT_ONLY,
            )

            for content, updated_content, data_issues in zip(
                contents, updated_contents, data_issues_list
            ):
                if content is None:
                    continue
                assert updated_content is not None
                assert data_issues is not None
                from_time = updated_content.get(col_pair[0])
                if from_time is None:
                    continue
                col1 = self.complete_case_type.cols[
                    self.complete_case_type.case_type_cols[col_pair[0]].col_id
                ]

                # Check if from_time is a valid time value for col1's type
                if self.TIME_MATCHERS[col1.col_type](from_time) is NoReturn:
                    continue

                # Transform the time value using ObjectAdapter
                try:
                    adapter = ObjectAdapter({"time_value": from_time})
                    transformed_adapter = time_transformer.transform(adapter)
                    to_time = transformed_adapter.get("time_value")
                except Exception:
                    # Skip if transformation fails
                    continue
                if to_time is None:
                    continue

                self._set_derived_value(
                    content,
                    updated_content,
                    data_issues,
                    "d4e2f3a4",
                    col_pair,
                    to_time,
                )

    def _transform_number_value_pairs(
        self,
        contents: list[dict[UUID, str | None] | None],
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
        col_pairs: list[tuple[UUID, UUID]],
    ) -> None:
        """
        Validate and transform NUMBER pairs of values.
        Applies only to DECIMAL_XXX-INTERVAL and INTERVAL-INTERVAL column pairs.
        """
        for col_pair in col_pairs:
            col1 = self.complete_case_type.cols[
                self.complete_case_type.case_type_cols[col_pair[0]].col_id
            ]
            col2 = self.complete_case_type.cols[
                self.complete_case_type.case_type_cols[col_pair[1]].col_id
            ]

            # Only handle DECIMAL_XXX-INTERVAL and INTERVAL-INTERVAL pairs
            is_col1_decimal = col1.col_type in ColTypeSet.NUMBER.value
            is_col2_interval = col2.col_type == ColType.INTERVAL
            is_col1_interval = col1.col_type == ColType.INTERVAL

            # DECIMAL_XXX -> INTERVAL transformation
            if is_col1_decimal and is_col2_interval:
                self._transform_decimal_to_interval(
                    contents,
                    updated_contents,
                    data_issues_list,
                    col_pair,
                    col2,
                )

            # INTERVAL -> INTERVAL transformation using IntervalToIntervalTransformer
            elif is_col1_interval and is_col2_interval:
                self._transform_interval_to_interval(
                    contents,
                    updated_contents,
                    data_issues_list,
                    col_pair,
                    col1,
                    col2,
                )

    def _transform_decimal_to_interval(
        self,
        contents: list[dict[UUID, str | None] | None],
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
        col_pair: tuple[UUID, UUID],
        col2: model.Col,
    ) -> None:
        """Process DECIMAL_XXX -> INTERVAL transformation."""
        # Check if we have an interval transformer for col2's concept set
        if col2.concept_set_id is None:
            return
        interval_transformer = self.interval_transformers.get(col2.concept_set_id)
        if interval_transformer is None:
            return

        for content, updated_content, data_issues in zip(
            contents, updated_contents, data_issues_list
        ):
            if content is None:
                continue
            assert updated_content is not None
            assert data_issues is not None
            from_number_str = updated_content.get(col_pair[0])
            if from_number_str is None:
                continue
            from_number = float(from_number_str)

            if not interval_transformer.is_transformable(from_number):
                continue

            # Use the interval transformer with "value" field name
            adapter = ObjectAdapter({"value": from_number})
            transformed_adapter = interval_transformer.transform(adapter)
            to_interval_id = transformed_adapter.get("value")
            if to_interval_id is None:
                continue

            self._set_derived_value(
                content,
                updated_content,
                data_issues,
                "c9d4e1f2",
                col_pair,
                to_interval_id,
            )

    def _transform_interval_to_interval(
        self,
        contents: list[dict[UUID, str | None] | None],
        updated_contents: list[dict[UUID, str | None] | None],
        data_issues_list: list[list[model.CaseDataIssue] | None],
        col_pair: tuple[UUID, UUID],
        col1: model.Col,
        col2: model.Col,
    ) -> None:
        """Process INTERVAL -> INTERVAL transformation using IntervalToIntervalTransformer."""
        # Check if both columns have concept sets
        if col1.concept_set_id is None or col2.concept_set_id is None:
            return

        # Skip if trying to map to the same concept set
        if col1.concept_set_id == col2.concept_set_id:
            return

        # Get interval transformers for both concept sets
        src_transformer = self.interval_transformers.get(col1.concept_set_id)
        tgt_transformer = self.interval_transformers.get(col2.concept_set_id)

        if src_transformer is None or tgt_transformer is None:
            return

        # Create IntervalToIntervalTransformer
        try:
            interval_to_interval_transformer = IntervalToIntervalTransformer(
                src_field="interval_value",
                src_interval_names=src_transformer._interval_names,
                src_lower_bounds=src_transformer._lower_bounds,  # type:ignore[arg-type]
                src_upper_bounds=src_transformer._upper_bounds,  # type:ignore[arg-type]
                tgt_interval_names=tgt_transformer._interval_names,
                tgt_lower_bounds=tgt_transformer._lower_bounds,  # type:ignore[arg-type]
                tgt_upper_bounds=tgt_transformer._upper_bounds,  # type:ignore[arg-type]
                src_lower_bound_is_inclusive=src_transformer._lower_bound_is_inclusive,
                src_upper_bound_is_inclusive=src_transformer._upper_bound_is_inclusive,
                tgt_lower_bound_is_inclusive=tgt_transformer._lower_bound_is_inclusive,
                tgt_upper_bound_is_inclusive=tgt_transformer._upper_bound_is_inclusive,
                overlap_strategy="largest_overlap",
                no_match_strategy=NoMatchStrategy.SET_NONE,
            )
        except Exception:
            # Skip if transformer creation fails
            return

        for content, updated_content, data_issues in zip(
            contents, updated_contents, data_issues_list
        ):
            if content is None:
                continue
            assert updated_content is not None
            assert data_issues is not None
            from_interval_id = updated_content.get(col_pair[0])
            if from_interval_id is None:
                continue

            # TODO: replace by pre-calculated interval_relation_map for efficiency
            # Check if transformation is possible
            if not interval_to_interval_transformer.is_transformable(from_interval_id):
                continue
            # Transform the interval value using ObjectAdapter
            try:
                adapter = ObjectAdapter({"interval_value": from_interval_id})
                transformed_adapter = interval_to_interval_transformer.transform(
                    adapter
                )
                to_interval_id = transformed_adapter.get("interval_value")
            except Exception:
                # Skip if transformation fails
                continue
            if to_interval_id is None:
                continue

            self._set_derived_value(
                content,
                updated_content,
                data_issues,
                "a8f2d5e7",
                col_pair,
                to_interval_id,
            )

    def _set_derived_value(
        self,
        content: dict[UUID, str | None],
        updated_content: dict[UUID, str | None],
        data_issues: list[model.CaseDataIssue],
        code: str,
        col_pair: tuple,
        new_value: str,
    ) -> None:
        # Add derived value to updated_content
        updated_content[col_pair[1]] = new_value

        # Log data issue in validation report
        if (
            col_pair[1] in updated_content
            and updated_content[col_pair[1]] is not None
            and updated_content[col_pair[1]] != new_value
        ):
            # Overwrite existing different value
            data_issues.append(
                model.CaseDataIssue(
                    case_type_col_id=col_pair[1],
                    original_value=content[col_pair[1]],
                    updated_value=new_value,
                    data_issue_type=DataIssueType.CONFLICT,
                    code=code,
                    message=f"Value overwritten based on derived value from '{content[col_pair[0]]}'",
                )
            )
        else:
            # Set derived value
            data_issues.append(
                model.CaseDataIssue(
                    case_type_col_id=col_pair[1],
                    original_value=content.get(col_pair[1]),
                    updated_value=new_value,
                    data_issue_type=DataIssueType.DERIVED,
                    code=code,
                    message=f"Value derived from '{content.get(col_pair[0])}'",
                )
            )

    def _init_metadata(self) -> None:
        self._init_set_metadata()
        self._init_concept_metadata()
        self._init_region_metadata()
        self._init_organization_metadata()

    def _init_set_metadata(self) -> None:
        self.concept_set_ids = set()
        self.interval_concept_set_ids = set()
        self.regex_concept_set_ids = set()
        self.region_set_ids = set()
        # Get unique concept and region sets across the complete case type
        for col in self.complete_case_type.cols.values():
            if col.col_type in ColTypeSet.HAS_CONCEPT_SET.value:
                assert col.concept_set_id
                self.concept_set_ids.add(col.concept_set_id)
                if col.col_type == ColType.INTERVAL:
                    self.interval_concept_set_ids.add(col.concept_set_id)
                elif col.col_type == ColType.REGULAR_LANGUAGE:
                    self.regex_concept_set_ids.add(col.concept_set_id)
            elif col.col_type in ColTypeSet.HAS_REGION_SET.value:
                assert col.region_set_id
                self.region_set_ids.add(col.region_set_id)

    def _init_concept_metadata(self) -> None:
        self.concept_value_maps = {}
        self.concept_relation_maps = {}
        self.interval_transformers = {}
        self.regex_patterns = {}

        # Retrieve relevant concept sets, concepts, and relations
        concept_sets, concept_set_concepts_map, concepts, concept_contained_in = (
            self._retrieve_concept_data()
        )

        # Fill concept_value_maps
        for concept_set_id, concept_ids in concept_set_concepts_map.items():
            self.concept_value_maps[concept_set_id] = (
                {str(x).lower(): str(x) for x in concept_ids}
                | {
                    concepts[x].code.lower(): str(x)
                    for x in concept_ids
                    if concepts[x].code is not None
                }
                | {
                    concepts[x].name.lower(): str(x)  # type: ignore[index]
                    for x in concept_ids
                    if concepts[x].name is not None
                }
            )

        # Fill in concept relation maps
        for (
            from_concept_set_id,
            to_concept_set_id,
        ), mapping in concept_contained_in.items():
            self.concept_relation_maps.setdefault(
                (from_concept_set_id, to_concept_set_id), {}
            )
            self.concept_relation_maps[(from_concept_set_id, to_concept_set_id)].update(
                mapping
            )

        # Fill in interval mappers
        for concept_set_id in self.interval_concept_set_ids:
            interval_concepts = [
                concepts[x] for x in concept_set_concepts_map[concept_set_id]
            ]
            self.interval_transformers[concept_set_id] = IntervalTransformer(
                "value",  # src_field should match the field name used in ObjectAdapter
                [str(x.id) for x in interval_concepts],
                [x.props["lb"] for x in interval_concepts],
                [x.props["ub"] for x in interval_concepts],
                lower_bound_is_inclusive=[x.props["lb_in"] for x in interval_concepts],
                upper_bound_is_inclusive=[x.props["ub_in"] for x in interval_concepts],
            )

        # Fill in regex matchers
        for concept_set_id in self.regex_concept_set_ids:
            concept_set = concept_sets[concept_set_id]
            assert concept_set.regex is not None
            self.regex_patterns[concept_set_id] = re.compile(concept_set.regex)

    def _init_region_metadata(self) -> None:
        self.region_value_maps = {}
        self.region_relation_maps = {}
        self.region_contained_in = {}
        self.regions = {}

        # Retrieve relevant regions and relations
        regions, region_set_regions_map, region_contained_in = (
            self._retrieve_region_data()
        )

        # Store regions for lookup
        self.regions = regions

        # Fill in region value maps
        for region_set_id in self.region_set_ids:
            curr_regions = [regions[x] for x in region_set_regions_map[region_set_id]]
            self.region_value_maps[region_set_id] = (  # type:ignore[arg-type]
                {
                    str(x.id).lower(): str(x.id) for x in curr_regions
                }  # type:ignore[assignment]
                | {x.code.lower(): str(x.id) for x in curr_regions if x.code}
                | {x.name.lower(): str(x.id) for x in curr_regions if x.name}
            )

        # Fill in region relation maps
        for (
            from_region_set_id,
            to_region_set_id,
        ), mapping in region_contained_in.items():
            self.region_relation_maps.setdefault(
                (from_region_set_id, to_region_set_id), {}
            )
            self.region_relation_maps[(from_region_set_id, to_region_set_id)].update(
                mapping
            )

    def _init_organization_metadata(self) -> None:
        self.organization_value_map = {}

        # Retrieve organizations
        organizations = self._retrieve_organization_data()

        # Fill in organization value map
        self.organization_value_map = (
            {str(x.id).lower(): str(x.id) for x in organizations}
            | {
                x.legal_entity_code.lower(): str(x.id)
                for x in organizations
                if x.legal_entity_code
            }
            | {x.name.lower(): str(x.id) for x in organizations if x.name}
        )

    def _retrieve_concept_data(
        self,
    ) -> tuple[
        dict[UUID, model.ConceptSet],
        dict[UUID, set[UUID]],
        dict[UUID, model.Concept],
        dict[tuple[UUID, UUID], dict[str, str]],
    ]:
        app = self.case_service.app
        # Retrieve relevant concepts sets
        concept_sets: dict[UUID, model.ConceptSet] = {
            x.id: x
            for x in app.handle(
                command.ConceptSetCrudCommand(
                    operation=CrudOperation.READ_ALL,
                    query_filter=UuidSetFilter(
                        key="id", members=frozenset(self.concept_set_ids)
                    ),
                )
            )
        }
        # Retrieve relevant concepts
        concepts: dict[UUID, model.Concept] = {
            x.id: x
            for x in app.handle(
                command.ConceptCrudCommand(
                    operation=CrudOperation.READ_ALL,
                    query_filter=UuidSetFilter(
                        key="concept_set_id", members=frozenset(self.concept_set_ids)
                    ),
                )
            )
        }
        # Map concepts to sets
        concept_set_concepts_map: dict[UUID, set[UUID]] = (
            map_paired_elements(  # type:ignore[assignment]
                [(x.concept_set_id, x.id) for x in concepts.values()],
                as_set=True,
            )
        )

        # concept_contained_in maps (from_concept_set_id, to_concept_set_id) to map from_concept_id to to_concept_id
        concept_contained_in: dict[tuple[UUID, UUID], dict[str, str]] = {}
        concept_relations: list[model.ConceptRelation] = app.handle(
            command.ConceptRelationCrudCommand(
                operation=CrudOperation.READ_ALL,
                query_filter=CompositeFilter(
                    filters=[
                        UuidSetFilter(
                            key="from_concept_id",
                            members=frozenset(concepts.keys()),
                        ),
                        UuidSetFilter(
                            key="to_concept_id",
                            members=frozenset(concepts.keys()),
                        ),
                    ],
                    operator=LogicalOperator.AND,
                ),
            )
        )
        for concept_relation in concept_relations:
            from_concept = concepts[concept_relation.from_concept_id]
            to_concept = concepts[concept_relation.to_concept_id]
            if concept_relation.relation == ConceptRelationType.CONTAINS:
                # Swap concepts to convert from contains to is-contained-in
                from_concept, to_concept = to_concept, from_concept
            else:
                # Only contains and is-contained-in relationships considered
                continue
            key = (from_concept.concept_set_id, to_concept.concept_set_id)
            concept_contained_in.setdefault(key, {})
            assert from_concept.id is not None
            assert to_concept.id is not None
            concept_contained_in[key][str(from_concept.id)] = str(to_concept.id)

        return concept_sets, concept_set_concepts_map, concepts, concept_contained_in

    def _retrieve_region_data(self) -> tuple[
        dict[UUID, model.Region],
        dict[UUID, set[UUID]],
        dict[tuple[UUID, UUID], dict[str, str]],
    ]:
        app = self.case_service.app
        # Retrieve relevant regions
        regions: dict[UUID, model.Region] = {
            x.id: x
            for x in app.handle(
                command.RegionCrudCommand(
                    operation=CrudOperation.READ_ALL,
                    query_filter=UuidSetFilter(
                        key="region_set_id", members=frozenset(self.region_set_ids)
                    ),
                )
            )
        }
        # Map regions to sets
        region_set_regions_map: dict[UUID, set[UUID]] = (
            map_paired_elements(  # type:ignore[assignment]
                [(x.region_set_id, x.id) for x in regions.values()],
                as_set=True,
            )
        )

        # Retrieve region relations
        region_contained_in: dict[tuple[UUID, UUID], dict[str, str]] = {}
        region_relations: list[model.RegionRelation] = app.handle(
            command.RegionRelationCrudCommand(
                operation=CrudOperation.READ_ALL,
            )
        )
        region_relations = [
            x
            for x in region_relations
            if x.from_region_id in regions and x.to_region_id in regions
        ]
        for region_relation in region_relations:
            from_region = regions[region_relation.from_region_id]
            to_region = regions[region_relation.to_region_id]
            if region_relation.relation == RegionRelationType.CONTAINS:
                # Swap regions to convert from contains to is-contained-in
                from_region, to_region = to_region, from_region
            else:
                # Only contains and is-contained-in relationships considered
                continue
            key = (from_region.region_set_id, to_region.region_set_id)
            region_contained_in.setdefault(key, {})
            assert from_region.id is not None
            assert to_region.id is not None
            region_contained_in[key][str(from_region.id)] = str(to_region.id)

        return regions, region_set_regions_map, region_contained_in

    def _retrieve_organization_data(
        self,
    ) -> list[model.Organization]:
        app = self.case_service.app
        # Retrieve relevant organizations
        organizations: list[model.Organization] = app.handle(
            command.OrganizationCrudCommand(
                operation=CrudOperation.READ_ALL,
            )
        )
        return organizations

    @staticmethod
    def _get_col_pairs(case_type_col_ids: list[UUID]) -> list[tuple[UUID, UUID]]:
        """
        Generate all pairs of case type col IDs in both directions.
        """
        return list(combinations(case_type_col_ids, 2)) + list(
            combinations(case_type_col_ids[::-1], 2)
        )
