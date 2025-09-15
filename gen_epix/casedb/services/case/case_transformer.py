import re
from decimal import Decimal, InvalidOperation
from typing import Any, NoReturn
from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import (
    CaseColDataRule,
    ColType,
    ColTypeSet,
    RegionRelationType,
)
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.util import map_paired_elements
from gen_epix.fastapp import CrudOperation
from gen_epix.filter import UuidSetFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.transform import Transformer
from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.transform_result import TransformResult
from gen_epix.transform.transformers import IntervalTransformer


class CaseTransformer(Transformer):
    N_DECIMALS = {
        ColType.DECIMAL_0: 0,
        ColType.DECIMAL_1: 1,
        ColType.DECIMAL_2: 2,
        ColType.DECIMAL_3: 3,
        ColType.DECIMAL_4: 4,
        ColType.DECIMAL_5: 5,
        ColType.DECIMAL_6: 6,
    }

    TIME_YEAR_PATTERN = re.compile(r"^\d{4}$")
    TIME_QUARTER_PATTERN = re.compile(r"^\d{4}-Q[1-4]$")
    TIME_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
    TIME_WEEK_PATTERN = re.compile(r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")
    TIME_DAY_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")

    TIME_MATCHERS = {
        ColType.TIME_YEAR: lambda x: (
            x if x is None or CaseTransformer.TIME_YEAR_PATTERN.match(x) else NoReturn
        ),
        ColType.TIME_QUARTER: lambda x: (
            x
            if x is None or CaseTransformer.TIME_QUARTER_PATTERN.match(x)
            else NoReturn
        ),
        ColType.TIME_MONTH: lambda x: (
            x if x is None or CaseTransformer.TIME_MONTH_PATTERN.match(x) else NoReturn
        ),
        ColType.TIME_WEEK: lambda x: (
            x if x is None or CaseTransformer.TIME_WEEK_PATTERN.match(x) else NoReturn
        ),
        ColType.TIME_DAY: lambda x: (
            x if x is None or CaseTransformer.TIME_DAY_PATTERN.match(x) else NoReturn
        ),
    }

    @staticmethod
    def _transform_decimal(value: str | None, n_decimals: int) -> str | None | NoReturn:
        if value is None:
            return None
        try:
            num_value = round(Decimal(value), n_decimals)
            return str(num_value)
        except (ValueError, InvalidOperation):
            return NoReturn

    def __init__(
        self, case_service: BaseCaseService, complete_case_type: model.CompleteCaseType
    ):
        self.case_service = case_service
        self.complete_case_type = complete_case_type
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

        self._init_metadata()

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        raise NotImplementedError()

    def __call__(self, obj: Any) -> TransformResult:
        if not isinstance(obj, command.ValidateCasesCommand):
            raise ValueError("Invalid input")
        if obj.case_type_id != self.complete_case_type.id:
            raise ValueError("Invalid case type")
        is_update = obj.is_update
        contents = [case.content for case in obj.cases]

        # Create case validation report with empty content for cases
        case_validation_report = model.CaseValidationReport(
            case_type_id=obj.case_type_id,
            created_in_data_collection_id=obj.created_in_data_collection_id,
            is_update=obj.is_update,
            data_collection_ids=obj.data_collection_ids,
            validated_cases=[
                model.ValidatedCase(
                    case=model.CaseForCreateUpdate(
                        **x.model_dump(exclude={"content"}), content={}
                    ),
                    data_issues=[],
                )
                for x in obj.cases
            ],
        )
        updated_contents = [
            x.case.content for x in case_validation_report.validated_cases
        ]

        # Validate and transform individual values
        msg_template = "{orig_value}"
        for case_type_col in self.complete_case_type.case_type_cols.values():
            case_type_col_id = case_type_col.id
            assert case_type_col_id is not None
            col = self.complete_case_type.cols[case_type_col.col_id]
            if col.col_type == ColType.REGULAR_LANGUAGE:
                assert col.concept_set_id
                transform_fn = lambda x: (
                    x
                    if x is None or self.regex_patterns[col.concept_set_id].match(x)
                    else NoReturn
                )
                msg_template = "{orig_value} does not match regex"
            elif col.col_type in ColTypeSet.STRING_SET.value:
                assert col.concept_set_id
                concept_value_map = self.concept_value_maps[col.concept_set_id]
                transform_fn = lambda x: (
                    concept_value_map.get(x.lower(), NoReturn) if x else None
                )
                msg_template = "{orig_value} cannot be mapped to concept"
            elif col.col_type in ColTypeSet.HAS_REGION_SET.value:
                assert col.region_set_id
                region_value_map = self.region_value_maps[col.region_set_id]
                transform_fn = lambda x: (
                    region_value_map.get(x.lower(), NoReturn) if x else None
                )
                msg_template = "{orig_value} cannot be mapped to region"
            elif col.col_type in ColTypeSet.TIME.value:
                transform_fn = self.TIME_MATCHERS[col.col_type]
                msg_template = (
                    "{orig_value} is not a valid " + col.col_type.value + " value"
                )
            elif col.col_type in ColTypeSet.NUMBER.value:
                n_decimals = self.N_DECIMALS[col.col_type]
                transform_fn = lambda x: CaseTransformer._transform_decimal(
                    x, n_decimals
                )
            else:
                # TODO: transform other col_types
                transform_fn = lambda x: x
            # Update value
            for i, (content, updated_content) in enumerate(
                zip(contents, updated_contents)
            ):
                if case_type_col_id not in content:
                    continue
                orig_value = content[case_type_col_id]
                if orig_value is None:
                    if is_update:
                        # Deletion of value by providing None -> keep in content
                        updated_content[case_type_col_id] = None
                    # Unnecessary None -> do not add
                    continue
                new_value = transform_fn(orig_value)
                if new_value == NoReturn:
                    new_value = None
                    # No mapping found
                    case_validation_report.validated_cases[i].data_issues.append(
                        model.CaseDataIssue(
                            case_type_col_id=case_type_col_id,
                            original_value=orig_value,
                            updated_value=new_value,
                            data_rule=CaseColDataRule.INVALID,
                            details=msg_template.format(orig_value=orig_value),
                        )
                    )
                    continue
                updated_content[case_type_col_id] = new_value

        # Add any other case type cols present as data issue
        for i, content in enumerate(contents):
            for case_type_col_id in content.keys():
                if case_type_col_id in self.complete_case_type.case_type_cols:
                    continue
                # Unknown case type col
                case_validation_report.validated_cases[i].data_issues.append(
                    model.CaseDataIssue(
                        case_type_col_id=case_type_col_id,
                        original_value=content[case_type_col_id],
                        updated_value=None,
                        data_rule=CaseColDataRule.UNAUTHORIZED,
                        details="Unknown case type column",
                    )
                )

        # TODO: merge with existing content in case of update

        # TODO: Add derived values: per case type dim, go over all pairs of case type cols and derive values
        # for case_type_dim in self.complete_case_type.case_type_dims:
        #     case_type_col_ids = case_type_dim.case_type_col_order
        #     case_type_cols = [self.complete_case_type.case_type_cols[x] for x in case_type_col_ids]
        #     cols = [self.complete_case_type.cols[x.col_id] for x in case_type_cols]
        #     for case_type_col_id, col in zip(case_type_col_ids, cols):

        return TransformResult(
            success=True, original_object=obj, transformed_object=case_validation_report
        )

    def _init_metadata(self) -> None:
        self._init_set_metadata()
        self._init_concept_metadata()
        self._init_region_metadata()

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
        concept_sets, concept_set_concepts_map, concepts, concept_relations = (
            self._retrieve_concept_data()
        )

        # Fill concept_value_maps
        for concept_set_id, concept_ids in concept_set_concepts_map.items():
            self.concept_value_maps[concept_set_id] = (
                {str(x).lower(): str(x) for x in concept_ids}
                | {
                    concepts[x].abbreviation.lower(): str(x)
                    for x in concept_ids
                    if concepts[x].abbreviation is not None
                }
                | {
                    concepts[x].name.lower(): str(x)
                    for x in concept_ids
                    if concepts[x].name is not None
                }
            )

        # Fill in concept relation maps
        for concept_relations in concept_relations:
            from_concept = concepts[concept_relations.from_concept_set_id]
            to_concept = concepts[concept_relations.to_concept_set_id]
            key = (from_concept.concept_set_id, to_concept.concept_set_id)
            self.concept_relation_maps.setdefault(key, {})
            self.concept_relation_maps[key][str(from_concept.id)] = str(to_concept.id)

        # Fill in interval mappers
        for concept_set_id in self.interval_concept_set_ids:
            interval_concepts = [
                concepts[x] for x in concept_set_concepts_map[concept_set_id]
            ]
            self.interval_transformers[concept_set_id] = IntervalTransformer(
                None,
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

        # Retrieve relevant regions and relations
        regions, region_set_regions_map, region_relations = self._retrieve_region_data()

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
        for region_relation in region_relations:
            from_region = regions[region_relation.from_region_id]
            to_region = regions[region_relation.to_region_id]
            if region_relation.relation == RegionRelationType.CONTAINS:
                # Swap regions to convert from contains to is-contained-in
                from_region, to_region = to_region, from_region
            elif region_relation.relation != RegionRelationType.IS_CONTAINED_IN:
                # Only contains and is-contained-in relationships considered
                continue
            key = (from_region.region_set_id, to_region.region_set_id)
            self.region_relation_maps.setdefault(key, {})
            assert from_region.id is not None
            assert to_region.id is not None
            self.region_relation_maps[key][str(from_region.id)] = str(to_region.id)

    def _retrieve_concept_data(
        self,
    ) -> tuple[
        dict[UUID, model.ConceptSet],
        dict[UUID, set[UUID]],
        dict[UUID, model.Concept],
        list,  # TODO: change to list[model.ConceptRelation] once implemented
    ]:
        app = self.case_service.app
        # Retrieve relevant concept sets
        concept_sets: dict[UUID, model.ConceptSet] = {
            x.id: x
            for x in app.handle(
                command.ConceptSetCrudCommand(
                    obj_ids=list(self.concept_set_ids),
                    operation=CrudOperation.READ_SOME,
                )
            )
        }
        # TODO: remove once ConceptSet-Concept is one-to-many
        concept_set_members: list[model.ConceptSetMember] = app.handle(
            command.ConceptSetMemberCrudCommand(
                operation=CrudOperation.READ_ALL,
                query_filter=UuidSetFilter(
                    key="concept_set_id", members=frozenset(self.concept_set_ids)
                ),
            )
        )
        concept_set_concepts_map: dict[UUID, set[UUID]] = (
            map_paired_elements(  # type:ignore[assignment]
                [(x.concept_set_id, x.concept_id) for x in concept_set_members],
                as_set=True,
            )
        )
        # Retrieve relevant concepts
        concept_ids = {x.concept_id for x in concept_set_members}
        concepts: dict[UUID, model.Concept] = {
            x.id: x
            for x in app.handle(
                command.ConceptCrudCommand(
                    obj_ids=list(concept_ids), operation=CrudOperation.READ_SOME
                )
            )
        }
        # TODO: Retrieve relevant concept contains/is-contained-in relations once ConceptSet-Concept is one-to-many (for now no relations)
        concept_relations: list = []
        return concept_sets, concept_set_concepts_map, concepts, concept_relations

    def _retrieve_region_data(self) -> tuple[
        dict[UUID, model.Region],
        dict[UUID, set[UUID]],
        list[model.RegionRelation],
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
        region_relations: list[model.RegionRelation] = app.handle(
            command.RegionRelationCrudCommand(
                operation=CrudOperation.READ_ALL,
                query_filter=CompositeFilter(
                    filters=[
                        UuidSetFilter(
                            key="from_region_id",
                            members=frozenset(regions.keys()),
                        ),
                        UuidSetFilter(
                            key="to_region_id",
                            members=frozenset(regions.keys()),
                        ),
                    ],
                    operator=LogicalOperator.AND,
                ),
            )
        )

        return regions, region_set_regions_map, region_relations


# TODO: for reference, remove when no longer needed
# def tfm_geo_resolution(
#     region_id_contained_in: dict[tuple[str, str], str],
#     values1: Iterable[str | None],
#     region_set_id2: str,
#     orig_values2: Iterable[str | None] | None,
# ) -> tuple[list[str | None], list[tuple[str | None, str | None]]]:
#     new_values2 = [
#         None if x is None else region_id_contained_in.get((x, region_set_id2))
#         for x in values1
#     ]
#     if orig_values2 is None:
#         diff_values = []
#     else:
#         # Only replace original values with a non-null value
#         new_values2 = [y if x is None else x for x, y in zip(new_values2, orig_values2)]
#         diff_values = [
#             (x, y)
#             for x, y in zip(orig_values2, new_values2)
#             if x is not None and y is not None and y != x
#         ]
#     return new_values2, diff_values


# def tfm_age_category(
#     age_categories1: dict[str : tuple[float, float]] | None,
#     values1: Iterable[str | None],
#     age_categories2: dict[str : tuple[float, float]] | None,
#     orig_values2: Iterable[str | None] | None,
# ) -> tuple[list[str | None], list[tuple[str | None, str | None]]]:
#     n = len(values1)
#     if not age_categories1:
#         # Variable 1 numeric
#         if not age_categories2:
#             # Variable 2 numeric -> no action, keep 2
#             new_values2 = list(orig_values2)
#         else:
#             # Variable 2 ordinal -> map to number to age category
#             new_values2 = [None] * n
#             for i, value1 in enumerate(values1):
#                 if value1 is None:
#                     continue
#                 for age_category_id2, bounds2 in age_categories2.items():
#                     if bounds2[0] <= value1 < bounds2[1]:
#                         new_values2[i] = age_category_id2
#                         break
#     else:
#         # Variable 1 ordinal
#         if not age_categories2:
#             # Variable 2 numeric -> no action, keep 2
#             new_values2 = list(orig_values2)
#         else:
#             # Variable 2 ordinal -> map to age category 1 to age category 2
#             # but only if all age categories 1 fit within an age category 2
#             # to avoid consistently removing some values and thereby introducing bias
#             age_category_map = {}
#             is_complete_mapping = True
#             for age_category1, bounds1 in age_categories1.items():
#                 for age_category2, bounds2 in age_categories2.items():
#                     if bounds1[0] >= bounds2[0] and bounds1[1] <= bounds2[1]:
#                         # Age category 1 maps to age category 2
#                         age_category_map[age_category1] = age_category2
#                         break
#                 if age_category1 not in age_category_map:
#                     is_complete_mapping = False
#             if not is_complete_mapping:
#                 new_values2 = list(orig_values2)
#             else:
#                 new_values2 = [None] * n
#                 for i, value1 in enumerate(values1):
#                     if value1 is None:
#                         continue
#                     new_values2[i] = age_category_map[value1]
#     if orig_values2 is None:
#         diff_values = []
#     else:
#         # Only replace original values with a non-null value
#         new_values2 = [y if x is None else x for x, y in zip(new_values2, orig_values2)]
#         diff_values = [
#             (x, y)
#             for x, y in zip(orig_values2, new_values2)
#             if x is not None and y is not None and y != x
#         ]
#     return new_values2, diff_values
