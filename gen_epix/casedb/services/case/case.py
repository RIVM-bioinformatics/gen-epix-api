import datetime
from decimal import Decimal
from typing import Any, Callable, Iterable, Type
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService
from gen_epix.casedb.services.case.read_association_with_valid_ids import (
    case_service_read_association_with_valid_ids,
)
from gen_epix.casedb.services.case.retrieve_complete_case_type import (
    case_service_retrieve_complete_case_type,
)
from gen_epix.casedb.services.case.retrieve_phylogenetic_tree import (
    case_service_retrieve_phylogenetic_tree,
)
from gen_epix.casedb.services.case.retrieve_stats import (
    case_service_retrieve_case_set_stats,
    case_service_retrieve_case_type_stats,
)
from gen_epix.casedb.services.case.validate_cases import CaseTransformer
from gen_epix.common.util import map_paired_elements
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.fastapp.enum import CrudOperationSet
from gen_epix.filter import Filter, UuidSetFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.string_set import StringSetFilter


class CaseService(BaseCaseService):
    _VALUE_TO_STR = {
        enum.ColType.TIME_DAY: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_WEEK: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_MONTH: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_QUARTER: lambda x: None if not x else f"{x}",
        enum.ColType.TIME_YEAR: lambda x: None if not x else f"{x}",
        enum.ColType.GEO_LATLON: lambda x: None if not x else f"{x}",
        enum.ColType.TEXT: lambda x: None if not x else f"{x}",
        enum.ColType.ID_DIRECT: lambda x: None if not x else f"{x}",
        enum.ColType.ID_PSEUDONYMISED: lambda x: None if not x else f"{x}",
        enum.ColType.OTHER: lambda x: None if not x else f"{x}",
        enum.ColType.DECIMAL_0: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.0f}")
        ),
        enum.ColType.DECIMAL_1: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.1f}")
        ),
        enum.ColType.DECIMAL_2: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.2f}")
        ),
        enum.ColType.DECIMAL_3: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.3f}")
        ),
        enum.ColType.DECIMAL_4: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.4f}")
        ),
        enum.ColType.DECIMAL_5: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.5f}")
        ),
        enum.ColType.DECIMAL_6: lambda x: (
            None if not x else (x if isinstance(x, str) else f"{x:.6f}")
        ),
    }

    def crud(  # type:ignore[override]
        self, cmd: command.CrudCommand
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        """
        Override the base crud method to apply ABAC restrictions and cascade delete
        where necessary
        """
        # Handle no ABAC restrictions
        if any(isinstance(cmd, x) for x in BaseCaseService.NO_ABAC_COMMAND_CLASSES):
            # No ABAC restrictions
            return super().crud(cmd)  # type: ignore[return-value]

        # Start unit of work and execute all within this scope
        with self.repository.uow() as uow:
            # Metadata commands
            if any(
                isinstance(cmd, x)
                for x in BaseCaseService.ABAC_METADATA_COMMAND_CLASSES
            ):
                return self._crud_metadata(uow, cmd)  # type: ignore[no-any-return]
            # Data commands
            elif any(
                isinstance(cmd, x) for x in BaseCaseService.ABAC_DATA_COMMAND_CLASSES
            ):
                return self._crud_data(uow, cmd)
            else:
                raise AssertionError(
                    f"Unexpected command {cmd.__class__.__name__} with operation {cmd.operation.value}"
                )

    def validate_cases(
        self, cmd: command.ValidateCasesCommand
    ) -> model.CaseValidationReport:
        case_type_id = cmd.case_type_id
        created_in_data_collection_id = cmd.created_in_data_collection_id

        # @ABAC: verify if case set or cases may be created in the given data collection(s)
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        is_allowed = case_abac.is_allowed(
            case_type_id,
            enum.CaseRight.ADD_CASE,
            True,
            created_in_data_collection_id=created_in_data_collection_id,
            tgt_data_collection_ids=cmd.data_collection_ids,
        )
        if not is_allowed:
            assert cmd.user is not None
            raise exc.UnauthorizedAuthError(
                f"User {cmd.user.id} is not allowed to create a case set/cases in the given data collection(s)"
            )

        # TODO: merge data with existing cases when updating
        curr_cmd = command.RetrieveCompleteCaseTypeCommand(
            user=cmd.user, case_type_id=case_type_id
        )
        curr_cmd._policies.extend(cmd._policies)
        complete_case_type = case_service_retrieve_complete_case_type(self, curr_cmd)
        transformer = CaseTransformer(self, complete_case_type)
        transform_result = transformer(cmd)
        if not transform_result.success:
            raise exc.DataException(f"Failed to transform case data")
        case_validation_report: model.CaseValidationReport = (
            transform_result.transformed_object
        )  # type:ignore[assignment]

        return case_validation_report

    def create_cases(self, cmd: command.CreateCasesCommand) -> list[model.Case] | None:
        # Special case: zero cases to be created
        if not cmd.cases:
            return []

        # Get case type and created_in data collection IDs
        case_type_id = cmd.case_type_id
        created_in_data_collection_id = cmd.created_in_data_collection_id

        # @ABAC: verify if case set or cases may be created in the given data collection(s)
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        is_allowed = case_abac.is_allowed(
            case_type_id,
            enum.CaseRight.ADD_CASE,
            True,
            created_in_data_collection_id=created_in_data_collection_id,
            tgt_data_collection_ids=cmd.data_collection_ids,
        )
        if not is_allowed:
            assert cmd.user is not None
            raise exc.UnauthorizedAuthError(
                f"User {cmd.user.id} is not allowed to create cases in the given data collection(s)"
            )

        # Convert cases for create update to cases
        # TODO: validate content and add derived values
        cases: list[model.Case] = [
            model.Case(
                id=x.id,
                case_type_id=cmd.case_type_id,
                subject_id=x.subject_id,
                created_in_data_collection_id=cmd.created_in_data_collection_id,
                case_date=x.case_date,
                content={y: z for y, z in x.content.items() if z is not None},
            )
            for x in cmd.cases
        ]

        # Create cases and case data collection links
        with self.repository.uow() as uow:
            # Create cases, using the parent class method to avoid ABAC
            # restrictions
            cases = super().crud(  # type: ignore[assignment]
                command.CaseCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.CREATE_SOME,
                    objs=cases,  # type: ignore[arg-type]
                    props=cmd.props,
                )
            )
            # Associate cases with data collections
            curr_cmd = command.CaseDataCollectionLinkCrudCommand(
                user=cmd.user,
                operation=CrudOperation.CREATE_SOME,
                objs=[
                    model.CaseDataCollectionLink(
                        case_id=x.id, data_collection_id=y  # type: ignore[arg-type]
                    )
                    for x in cases
                    for y in cmd.data_collection_ids
                ],
            )
            curr_cmd._policies.extend(cmd._policies)
            case_data_collection_links = self.crud(curr_cmd)
        return cases

    def create_case_set(
        self, cmd: command.CreateCaseSetCommand
    ) -> model.CaseSet | None:
        # Get case type and created_in data collection IDs
        case_type_id = cmd.case_set.case_type_id
        created_in_data_collection_id = cmd.case_set.created_in_data_collection_id

        # @ABAC: verify if case set or cases may be created in the given data collection(s)
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        is_allowed = case_abac.is_allowed(
            case_type_id,
            enum.CaseRight.ADD_CASE_SET,
            True,
            created_in_data_collection_id=created_in_data_collection_id,
            tgt_data_collection_ids=cmd.data_collection_ids,
        )
        if not is_allowed:
            assert cmd.user is not None
            raise exc.UnauthorizedAuthError(
                f"User {cmd.user.id} is not allowed to create a case set in the given data collection(s)"
            )

        # Create case set, case set data collection links, and optionally
        # case set members
        with self.repository.uow() as uow:
            # Create case set, using the parent class method to avoid ABAC
            # restrictions
            case_set: model.CaseSet = super().crud(  # type: ignore[assignment]
                command.CaseSetCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.CREATE_ONE,
                    objs=cmd.case_set,  # type: ignore[assignment]
                    props=cmd.props,
                )
            )
            # Associate case set/cases with data collections
            assert case_set.id is not None
            curr_cmd = command.CaseSetDataCollectionLinkCrudCommand(
                user=cmd.user,
                operation=CrudOperation.CREATE_SOME,
                objs=[
                    model.CaseSetDataCollectionLink(
                        case_set_id=case_set.id, data_collection_id=x
                    )
                    for x in cmd.data_collection_ids
                ],
            )
            curr_cmd._policies.extend(cmd._policies)
            case_set_data_collection_links = self.crud(curr_cmd)
            # Associate case set with cases if necessary
            if cmd.case_ids:
                curr_cmd2: command.CaseSetMemberCrudCommand = (
                    command.CaseSetMemberCrudCommand(
                        user=cmd.user,
                        operation=CrudOperation.CREATE_SOME,
                        objs=[
                            model.CaseSetMember(case_set_id=case_set.id, case_id=x)
                            for x in cmd.case_ids
                        ],
                    )
                )
                curr_cmd2._policies.extend(cmd._policies)
                case_set_members = self.crud(curr_cmd2)
        return case_set

    def retrieve_complete_case_type(
        self: BaseCaseService,
        cmd: command.RetrieveCompleteCaseTypeCommand,
    ) -> model.CompleteCaseType:
        return case_service_retrieve_complete_case_type(self, cmd)

    def retrieve_case_type_stats(
        self,
        cmd: command.RetrieveCaseTypeStatsCommand,
    ) -> list[model.CaseTypeStat]:
        return case_service_retrieve_case_type_stats(self, cmd)

    def retrieve_case_set_stats(
        self,
        cmd: command.RetrieveCaseSetStatsCommand,
    ) -> list[model.CaseSetStat]:
        return case_service_retrieve_case_set_stats(self, cmd)

    def retrieve_cases_by_query(
        self, cmd: command.RetrieveCasesByQueryCommand
    ) -> list[UUID]:
        # TODO: This is an inefficient call first loading all cases, then filtering them and then keeping only the ids. To be replaced by optimized query.
        user, repository = self._get_user_and_repository(cmd)
        assert isinstance(user, model.User) and user.id is not None
        case_query = cmd.case_query
        case_set_ids = case_query.case_set_ids
        case_type_ids = case_query.case_type_ids
        datetime_range_filter = case_query.datetime_range_filter

        # Special case: zero case_set_ids or zero case_type_ids (None equals all)
        if case_set_ids is not None and len(case_set_ids) == 0:
            return []
        if case_type_ids is not None and len(case_type_ids) == 0:
            return []

        # @ABAC: get case abac
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None
        is_full_access = case_abac.is_full_access
        has_case_read = case_abac.get_combinations_with_access_right(
            enum.CaseRight.READ_CASE
        )

        # @ABAC: Verify read access to all given case types if applicable
        if case_type_ids and not is_full_access:
            if not case_type_ids.issubset(set(has_case_read.keys())):
                raise exc.UnauthorizedAuthError(
                    f"Unauthorized case types: {case_type_ids}"
                )

        with repository.uow() as uow:

            # @ABAC: Verify any access to all given case sets if applicable
            if case_set_ids:
                case_sets = self._retrieve_case_sets_with_content_right(
                    uow,
                    user.id,
                    case_abac,
                    # user_case_access
                    enum.CaseRight.READ_CASE_SET,
                ) + self._retrieve_case_sets_with_content_right(
                    uow,
                    user.id,
                    case_abac,
                    # user_case_access
                    enum.CaseRight.WRITE_CASE_SET,
                )
                invalid_case_set_ids = case_set_ids - {x.id for x in case_sets}
                if invalid_case_set_ids:
                    invalid_case_set_ids_str = ", ".join(
                        [str(x) for x in invalid_case_set_ids]
                    )
                    raise exc.UnauthorizedAuthError(
                        f"Unauthorized case sets: {invalid_case_set_ids_str}"
                    )

            # @ABAC: Verify validity of filter
            if case_query.filter:
                # Make sure filter keys are UUIDs
                case_query.filter.set_keys(
                    lambda x: UUID(x) if isinstance(x, str) else x
                )
                cols = self._verify_case_filter(uow, user, case_query.filter)

            # @ABAC: Retrieve all cases with read access, and content filtered on case type
            # col read access
            cases = self._retrieve_cases_with_content_right(
                uow,
                user.id,
                case_abac,
                # user_case_access,
                enum.CaseRight.READ_CASE,
                case_ids=None,
                datetime_range_filter=datetime_range_filter,
                filter_content=True,
            )

            # Filter cases by case types
            if case_type_ids:
                cases = [x for x in cases if x.case_type_id in case_type_ids]

            # Filter cases by case sets
            if case_set_ids:
                case_case_sets, _ = self._retrieve_case_case_sets_map(uow, user.id)
                cases = [
                    x
                    for x in cases
                    if x.id in case_case_sets
                    and case_case_sets[x.id].intersection(case_set_ids)  # type: ignore[arg-type]
                ]

            # Filter cases by filters
            if case_query.filter:
                map_fns = CaseService._get_map_functions_for_filters(cols)  # type: ignore[assignment]
                cases = [
                    x
                    for x, y in zip(
                        cases,
                        case_query.filter.match_rows(
                            (x.content for x in cases), map_fn=map_fns  # type: ignore[misc]
                        ),
                    )
                    if y
                ]

        # TODO: consider putting these cases, with their data already filtered, in a
        # cache, so that the expected subsequent call to retrieve them can be sped up

        # Return case ids
        case_ids = [x.id for x in cases]
        return case_ids  # type: ignore[return-value]

    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        case_ids = cmd.case_ids
        user, repository = self._get_user_and_repository(cmd)
        assert isinstance(user, model.User) and user.id is not None
        if not case_ids:
            return []
        # @ABAC: get case abac
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None

        with repository.uow() as uow:
            cases = self._retrieve_cases_with_content_right(
                uow,
                user.id,
                case_abac,
                enum.CaseRight.READ_CASE,
                case_ids=case_ids,
                filter_content=True,
            )
        return cases

    def retrieve_case_or_set_rights(
        self,
        cmd: command.RetrieveCaseRightsCommand | command.RetrieveCaseSetRightsCommand,
    ) -> list[model.CaseRights] | list[model.CaseSetRights]:
        is_case_set = isinstance(cmd, command.RetrieveCaseSetRightsCommand)
        case_or_set_ids = cmd.case_set_ids if is_case_set else cmd.case_ids  # type: ignore[union-attr]
        user, repository = self._get_user_and_repository(cmd)

        # Special case: zero case_ids
        if not case_or_set_ids:
            return []

        # @ABAC: get case abac
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None

        # Retrieve all cases and case data collection links
        with repository.uow() as uow:
            # Retrieve cases/sets
            cases_or_sets: list[model.CaseSet] | list[model.Case] = self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                model.CaseSet if is_case_set else model.Case,
                None,
                case_or_set_ids,
                CrudOperation.READ_SOME,
            )
            # Retrieve case/set data collection links
            key = "case_set_id" if is_case_set else "case_id"
            case_or_set_data_collection_links: list[model.CaseDataCollectionLink] | list[model.CaseSetDataCollectionLink] = self.repository.crud(  # type: ignore[assignment]
                uow,
                user.id,
                (
                    model.CaseSetDataCollectionLink
                    if is_case_set
                    else model.CaseDataCollectionLink
                ),
                None,
                None,
                CrudOperation.READ_ALL,
                filter=UuidSetFilter(
                    key=key,
                    members=frozenset(case_or_set_ids),
                ),
            )

        # Determine case/set rights
        case_or_set_data_collections: dict[UUID, set[UUID]] = map_paired_elements(  # type: ignore[assignment]
            (
                (x.case_set_id if is_case_set else x.case_id, x.data_collection_id)  # type: ignore[union-attr]
                for x in case_or_set_data_collection_links
            ),
            as_set=True,
        )

        # Generate return value
        retval: list[model.CaseSetRights] | list[model.CaseRights] = []
        for case_or_set in cases_or_sets:
            assert case_or_set.id is not None
            data_collection_ids = case_or_set_data_collections.get(
                case_or_set.id, set()
            )
            data_collection_ids.add(case_or_set.created_in_data_collection_id)
            args: tuple = (
                case_or_set.id,
                case_or_set.case_type_id,
                case_or_set.created_in_data_collection_id,
                case_or_set_data_collections.get(case_or_set.id, set()),
            )
            retval.append(case_abac.get_case_set_rights(*args) if is_case_set else case_abac.get_case_rights(*args))  # type: ignore[arg-type]

        return retval

    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeByCasesCommand
    ) -> model.PhylogeneticTree:
        return case_service_retrieve_phylogenetic_tree(self, cmd)

    def retrieve_genetic_sequence(
        self,
        cmd: command.RetrieveGeneticSequenceByCaseCommand,
    ) -> list[model.GeneticSequence]:
        seq_case_type_col_id = cmd.genetic_sequence_case_type_col_id
        case_ids = cmd.case_ids
        user, repository = self._get_user_and_repository(cmd)
        assert isinstance(user, model.User) and user.id is not None

        # Special case: zero case_ids
        if not case_ids:
            return []

        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
        assert case_abac is not None

        with repository.uow() as uow:

            # @ABAC: Get cases and sequence_ids
            cases = self._retrieve_cases_with_content_right(
                uow,
                user.id,
                case_abac,
                enum.CaseRight.READ_CASE,
                case_ids=case_ids,
                filter_content=True,
            )
            seq_ids = [UUID(x.content.get(seq_case_type_col_id)) for x in cases]

            # Retrieve sequences
            genetic_sequences: list[model.GeneticSequence] = self.app.handle(
                command.RetrieveGeneticSequenceByIdCommand(
                    user=user,
                    seq_ids=seq_ids,
                )
            )

        return genetic_sequences

    def _crud_metadata(
        self,
        uow: BaseUnitOfWork,
        cmd: command.CrudCommand,
    ) -> Any:
        """Logic for handling metadata commands"""
        # Metadata admin or above: no @ABAC applied
        assert cmd.user
        if cmd.user.roles.intersection(enum.RoleSet.GE_REFDATA_ADMIN.value):
            # Metadata admin and above have access to all metadata: no ABAC
            # applied, only RBAC
            return self._crud_metadata_by_admin(uow, cmd)
        return self._crud_metadata_by_non_admin(uow, cmd)

    def _crud_metadata_by_admin(
        self, uow: BaseUnitOfWork, cmd: command.CrudCommand
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        """Metadata admin command handling, no ABAC applied"""
        self._crud_cascade_delete(uow, cmd)
        return super().crud(cmd)  # type:ignore[return-value]

    def _crud_metadata_by_non_admin(
        self,
        uow: BaseUnitOfWork,
        cmd: command.CrudCommand,
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        """Metadata user command handling, ABAC applied"""
        # @ABAC: get case abac
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)

        # Special case: no policy, allows for internal commands to retrieve all
        if not case_abac:
            # No policy: allows for internal commands to retrieve all
            return super().crud(cmd)  # type:ignore[return-value]

        # Initialise some
        is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
        is_delete = cmd.operation in CrudOperationSet.DELETE.value
        access_filter: Filter | None = None

        if not is_read:
            # Only read operations are allowed for metadata commands for these
            # users
            raise AssertionError("Unexpected operation")

        if isinstance(cmd, command.CaseTypeCrudCommand):
            valid_case_type_ids = case_abac.get_case_types_with_any_rights()
            access_filter = CaseService._compose_id_filter(("id", valid_case_type_ids))
            # No cascade delete to force conscious decision to delete from other models
            return self._crud_with_access_filter(uow, cmd, access_filter)

        elif isinstance(cmd, command.CaseTypeSetMemberCrudCommand):
            valid_case_type_ids = case_abac.get_case_types_with_any_rights()
            access_filter = CaseService._compose_id_filter(
                ("case_type_id", valid_case_type_ids)
            )
            return self._crud_with_access_filter(uow, cmd, access_filter)

        elif isinstance(cmd, command.CaseTypeSetCrudCommand):
            valid_case_type_ids = case_abac.get_case_types_with_any_rights()
            valid_case_type_set_ids: set[UUID] = (
                self._read_association_with_valid_ids(  # type:ignore[assignment]
                    command.CaseTypeSetMemberCrudCommand,
                    "case_type_set_id",
                    "case_type_id",
                    valid_ids2=valid_case_type_ids,
                    match_all2=is_delete,  # delete requires all case types
                    return_type="ids1",
                    uow=uow,
                    user=cmd.user,  # type: ignore[arg-type]
                )
            )
            access_filter = CaseService._compose_id_filter(
                ("id", valid_case_type_set_ids)
            )
            # No cascade delete to force conscious decision to delete from other models
            return self._crud_with_access_filter(uow, cmd, access_filter)

        elif isinstance(cmd, command.CaseTypeColCrudCommand):
            valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
            access_filter = CaseService._compose_id_filter(
                ("id", valid_case_type_col_ids)
            )
            # No cascade delete to force conscious decision to delete from other models
            return self._crud_with_access_filter(uow, cmd, access_filter)

        elif isinstance(cmd, command.CaseTypeColSetMemberCrudCommand):
            valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
            access_filter = CaseService._compose_id_filter(
                ("case_type_col_id", valid_case_type_col_ids)
            )
            return self._crud_with_access_filter(uow, cmd, access_filter)

        elif isinstance(cmd, command.CaseTypeColSetCrudCommand):
            # Determine valid case type cols as those with any rights
            valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
            valid_case_type_col_set_ids: set[UUID] = (
                self._read_association_with_valid_ids(  # type:ignore[assignment]
                    command.CaseTypeColSetMemberCrudCommand,
                    "case_type_col_set_id",
                    "case_type_col_id",
                    valid_ids2=valid_case_type_col_ids,
                    match_all2=is_delete,  # delete requires all case type cols
                    return_type="ids1",
                    uow=uow,
                    user=cmd.user,  # type: ignore[arg-type]
                )
            )
            access_filter = CaseService._compose_id_filter(
                ("id", valid_case_type_col_set_ids)
            )
            # No cascade delete to force conscious decision to delete from other models
            return self._crud_with_access_filter(uow, cmd, access_filter)

        raise AssertionError("Unexpected operation")

    def _crud_data(
        self,
        uow: BaseUnitOfWork,
        cmd: command.CrudCommand,
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        """Logic for handling data commands"""
        assert cmd.user
        # App admin or above: no @ABAC applied
        if cmd.user.roles.intersection(enum.RoleSet.GE_APP_ADMIN.value):
            return self._crud_data_by_admin(uow, cmd)
        return self._crud_data_by_non_admin(uow, cmd)

    def _crud_data_by_admin(
        self,
        uow: BaseUnitOfWork,
        cmd: command.CrudCommand,
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        """Data admin command handling, no ABAC applied"""
        # Non-ABAC restrictions not enforced anywhere else
        is_create = cmd.operation in CrudOperationSet.CREATE.value
        is_update = cmd.operation in CrudOperationSet.UPDATE.value
        if (is_create or is_update) and isinstance(
            cmd, command.CaseSetMemberCrudCommand
        ):
            # Verify that the case set and case have the same case type
            self._verify_case_set_member_case_type(
                cmd.user, cmd.get_objs()  # type:ignore[arg-type]
            )

        # Any other operation
        self._crud_cascade_delete(uow, cmd)
        return super().crud(cmd)  # type:ignore[return-value]

    def _crud_data_by_non_admin(
        self,
        uow: BaseUnitOfWork,
        cmd: command.CrudCommand,
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        """Data user command handling, ABAC applied"""
        # @ABAC: get case abac
        case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)

        # Special case: no policy, allows for internal commands to retrieve all
        if case_abac is None:
            # No policy: allows for internal commands to retrieve all
            return super().crud(cmd)  # type:ignore[return-value]

        # Initialise some
        is_create = cmd.operation in CrudOperationSet.CREATE.value
        is_read = cmd.operation in CrudOperationSet.READ_OR_EXISTS.value
        is_read_all = cmd.operation == CrudOperation.READ_ALL
        is_update = cmd.operation in CrudOperationSet.UPDATE.value
        is_delete = cmd.operation in CrudOperationSet.DELETE.value
        is_delete_all = cmd.operation == CrudOperation.DELETE_ALL
        access_filter: Filter | None = None
        case_sets: list[model.CaseSet]
        cases: list[model.Case]
        assert cmd.user is not None and cmd.user.id is not None

        # Handle each type of command
        if isinstance(cmd, command.CaseSetCrudCommand):
            # Determine valid case types and data collections
            case_set_ids = cmd.get_obj_ids()
            if is_create:
                # Implemented through separate create case set command
                raise AssertionError("Unexpected operation")
            elif is_read:
                # At least one data collection with read access is required
                retval = self._retrieve_case_sets_with_content_right(
                    uow,
                    cmd.user.id,
                    case_abac,
                    enum.CaseRight.READ_CASE_SET,
                    case_set_ids=case_set_ids,  # type:ignore[arg-type]
                    filter=cmd.query_filter,
                )
                return (
                    retval[0] if cmd.operation == CrudOperation.READ_ONE else retval  # type: ignore[return-value]
                )
            elif is_update:
                # At least one data collection with write access is required
                case_sets = self._retrieve_case_sets_with_content_right(
                    uow,
                    cmd.user.id,
                    case_abac,
                    enum.CaseRight.WRITE_CASE_SET,
                    case_set_ids=case_set_ids,  # type:ignore[arg-type]
                )
                return super().crud(cmd)  # type: ignore[return-value]
            elif is_delete:
                # All linked data collections have remove right
                if is_delete_all:
                    # Delete all not allowed due to potential large number of case sets
                    raise exc.UnauthorizedAuthError(
                        f"Operation {cmd.operation.value} not allowed for case sets for this user"
                    )
                # Get all case sets and data collection links
                assert case_set_ids is not None
                case_sets = self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.CaseSet,
                    None,
                    case_set_ids,
                    CrudOperation.READ_SOME,
                )
                case_set_data_collection_map, _ = (
                    self._retrieve_case_set_data_collections_map(
                        uow,
                        cmd.user.id,
                        obj_ids1=case_set_ids,
                    )
                )
                # Check if the user has access to all data collections of all requested
                # case sets
                for case_set in case_sets:
                    data_collection_ids = case_set_data_collection_map.get(
                        case_set.id, set()  # type:ignore[arg-type]
                    )
                    is_allowed = case_abac.is_allowed(
                        case_set.case_type_id,
                        enum.CaseRight.REMOVE_CASE_SET,
                        True,
                        created_in_data_collection_id=case_set.created_in_data_collection_id,
                        current_data_collection_ids=data_collection_ids,
                    )
                    if not is_allowed:
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} is not allowed to delete case set {case_set.id}"
                        )
                # Delete with cascade
                self._crud_cascade_delete(uow, cmd)
                return super().crud(cmd)  # type:ignore[return-value]
            else:
                raise AssertionError("Unexpected operation")

        elif isinstance(cmd, command.CaseCrudCommand):
            # Determine valid case types and data collections
            case_ids = cmd.get_obj_ids()
            if is_create | is_read | is_update:
                # Implemented through separate create case set command
                raise AssertionError("Unexpected operation")
            elif is_delete:
                # All linked data collections have remove right
                if is_delete_all:
                    # Delete all not allowed due to potential large number of case
                    raise exc.UnauthorizedAuthError(
                        f"Operation {cmd.operation.value} not allowed for cases for this user"
                    )
                # Get all cases and data collection links
                assert case_ids is not None
                cases = self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.Case,
                    None,
                    case_ids,
                    CrudOperation.READ_SOME,
                )
                case_data_collection_map, _ = self._retrieve_case_data_collections_map(
                    uow,
                    cmd.user.id,
                    obj_ids1=case_ids,
                )
                # Check if the user has access to all data collections of all requested
                # cases
                for case in cases:
                    data_collection_ids = case_data_collection_map.get(
                        case.id, set()  # type:ignore[arg-type]
                    )
                    is_allowed = case_abac.is_allowed(
                        case.case_type_id,
                        enum.CaseRight.REMOVE_CASE,
                        True,
                        created_in_data_collection_id=case.created_in_data_collection_id,
                        current_data_collection_ids=data_collection_ids,
                    )
                    if not is_allowed:
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} is not allowed to delete case {case.id}"
                        )
                # Delete with cascade
                self._crud_cascade_delete(uow, cmd)
                return super().crud(cmd)  # type:ignore[return-value]
            else:
                raise AssertionError("Unexpected operation")

        elif isinstance(cmd, command.CaseSetMemberCrudCommand):
            # Delete all not allowed due to potential large number of case set members
            if is_delete_all or is_update:
                raise exc.UnauthorizedAuthError(
                    f"Operation {cmd.operation.value} not allowed for case set members for this user"
                )

            # Get case set members
            case_set_members: list[model.CaseSetMember]
            if is_create:
                # Must be able to write the case set and read the case
                case_set_members = cmd.get_objs()  # type:ignore[assignment]
            elif is_read_all:
                # Must be able to read or write the case set and read the case
                case_set_members = self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.CaseSetMember,
                    None,
                    None,
                    CrudOperation.READ_ALL,
                    filter=cmd.query_filter,
                )
            elif is_read or is_delete:
                # Must be able to read or write the case set and read the case
                case_set_members = self.repository.crud(  # type:ignore[assignment]
                    uow,
                    cmd.user.id,
                    model.CaseSetMember,
                    None,
                    cmd.get_obj_ids(),
                    CrudOperation.READ_SOME,
                )
            elif is_update:
                # Should not be allowed
                raise AssertionError("Update not allowed for case set members")
            else:
                raise AssertionError("Unexpected operation")

            # All operations require read access to the case: retrieve the cases while
            # checking for this read right to determine this
            cases = self._retrieve_cases_with_content_right(
                uow,
                cmd.user.id,
                case_abac,
                enum.CaseRight.READ_CASE,
                case_ids=list({x.case_id for x in case_set_members}),
                filter_content=False,
                on_invalid_case_id=(
                    "ignore" if is_read_all or is_delete_all else "raise"
                ),
            )

            # Retrieve the case sets while checking for the correct right(s)
            case_set_ids = {x.case_set_id for x in case_set_members}
            case_sets = self._retrieve_case_sets_with_content_right(
                uow,
                cmd.user.id,
                case_abac,
                enum.CaseRight.READ_CASE_SET,
                case_set_ids=list(case_set_ids),  # type: ignore[arg-type]
                on_invalid_case_set_id="ignore",
            )
            if is_delete and not case_set_ids.issubset({x.id for x in case_sets}):
                # Also check the write case set right since not all case sets have the
                # read right
                case_sets += self._retrieve_case_sets_with_content_right(
                    uow,
                    cmd.user.id,
                    case_abac,
                    enum.CaseRight.WRITE_CASE_SET,
                    case_set_ids=list(case_set_ids),  # type: ignore[arg-type]
                    on_invalid_case_set_id="ignore",
                )

            # Check if the user has access to all requested case sets
            unauthorized_case_set_ids = case_set_ids - {x.id for x in case_sets}
            if unauthorized_case_set_ids:
                if is_read_all:
                    # unauthorized case set ids not applicable, filter out the case set
                    # members instead
                    case_set_members = [
                        x
                        for x in case_set_members
                        if x.case_set_id not in unauthorized_case_set_ids
                    ]
                else:
                    unauthorized_case_set_ids_str = ", ".join(
                        [str(x) for x in unauthorized_case_set_ids]
                    )
                    raise exc.UnauthorizedAuthError(
                        f"User {cmd.user.id} does not have access to case set(s): {unauthorized_case_set_ids_str}"
                    )

            # Execute command in case of create or delete, return case set
            # members in case of read
            if is_create or is_delete:
                return super().crud(cmd)  # type:ignore[return-value]
            elif is_read:
                return (
                    case_set_members[0]  # type:ignore[return-value]
                    if cmd.operation == CrudOperation.READ_ONE
                    else case_set_members
                )
            else:
                raise AssertionError("Unexpected operation")

        elif isinstance(cmd, command.CaseDataCollectionLinkCrudCommand):
            # Read all without filter and delete all not allowed due to potential large
            # number of case data collection links
            if (is_read_all and not cmd.query_filter) or is_delete_all or is_update:
                raise exc.UnauthorizedAuthError(
                    f"Operation {cmd.operation.value} not allowed for case data collection links for this user"
                )

            # Get case data collection links
            case_data_collection_links: list[model.CaseDataCollectionLink]
            if is_create:
                # Must be able to add the case to all the data collections
                case_data_collection_links = cmd.get_objs()  # type:ignore[assignment]
            elif is_read_all:
                # Must be able to read or write the case in all the data collections
                case_data_collection_links = (
                    self.repository.crud(  # type:ignore[assignment]
                        uow,
                        cmd.user.id,
                        model.CaseDataCollectionLink,
                        None,
                        None,
                        CrudOperation.READ_ALL,
                        filter=cmd.query_filter,
                    )
                )
            elif is_read or is_delete:
                # Must be able to read or write the case in (for is_read), or remove from
                # (for is_delete), all the data collections
                case_data_collection_links = (
                    self.repository.crud(  # type:ignore[assignment]
                        uow,
                        cmd.user.id,
                        model.CaseDataCollectionLink,
                        None,
                        cmd.get_obj_ids(),
                        CrudOperation.READ_SOME,
                    )
                )
            elif is_update:
                # Should not be allowed
                raise AssertionError(
                    "Update not allowed for case data collection links"
                )
            else:
                raise AssertionError("Unexpected operation")

            # Go over each case and check if the user has the required rights to it
            case_data_collection_map = map_paired_elements(  # type: ignore[assignment]
                ((x.case_id, x.data_collection_id) for x in case_data_collection_links),
                as_set=True,
            )
            case_ids = set(case_data_collection_map.keys())
            cases = self.repository.crud(  # type:ignore[assignment]
                uow,
                cmd.user.id,
                model.Case,
                None,
                list(case_ids),
                CrudOperation.READ_SOME,
            )
            if is_read:
                # Get read or write access per case type
                has_read_access = case_abac.get_combinations_with_access_right(
                    enum.CaseRight.READ_CASE
                )
                has_write_access = case_abac.get_combinations_with_access_right(
                    enum.CaseRight.WRITE_CASE
                )
                has_access = {x: set(y) for x, y in has_read_access.items()}
                for x, y in has_write_access.items():
                    if x in has_access:
                        has_access[x].update(y)
                    else:
                        has_access[x] = y
            for case in cases:
                case_type_id = case.case_type_id
                created_in_data_collection_id = case.created_in_data_collection_id
                data_collection_ids = case_data_collection_map[
                    case.id  # type:ignore[index]
                ]
                if is_read:
                    if not data_collection_ids.intersection(
                        has_access.get(case_type_id, set())
                    ):
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} does not have read or write access to case {case.id} in all data collections"
                        )
                elif is_create:
                    is_allowed = case_abac.is_allowed(
                        case_type_id,
                        enum.CaseRight.ADD_CASE,
                        False,
                        created_in_data_collection_id=created_in_data_collection_id,
                        current_data_collection_ids=data_collection_ids,
                        tgt_data_collection_ids=data_collection_ids,
                    )
                    if not is_allowed:
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} does not have add access to case {case.id} to all data collections"
                        )
                elif is_delete:
                    is_allowed = case_abac.is_allowed(
                        case_type_id,
                        enum.CaseRight.REMOVE_CASE,
                        False,
                        created_in_data_collection_id=created_in_data_collection_id,
                        current_data_collection_ids=data_collection_ids,
                        tgt_data_collection_ids=data_collection_ids,
                    )
                    if not is_allowed:
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} does not have remove access to case {case.id} to all data collections"
                        )

            # Execute command in case of create or delete, return case data collection
            # links in case of read
            if is_create or is_delete:
                return super().crud(cmd)  # type:ignore[return-value]
            elif is_read:
                return (
                    case_data_collection_links[0]  # type:ignore[return-value]
                    if cmd.operation == CrudOperation.READ_ONE
                    else case_data_collection_links
                )
            else:
                raise AssertionError("Unexpected operation")

        elif isinstance(cmd, command.CaseSetDataCollectionLinkCrudCommand):
            # Read all without filter and delete all not allowed due to potential large
            # number of case set data collection links
            has_access: dict[UUID, set[UUID]] = {}
            if (is_read_all and not cmd.query_filter) or is_delete_all or is_update:
                raise exc.UnauthorizedAuthError(
                    f"Operation {cmd.operation.value} not allowed for case set data collection links for this user"
                )

            # Get case set data collection links
            case_set_data_collection_links: list[model.CaseSetDataCollectionLink]
            if is_create:
                # Must be able to add the case set to all the data collections
                case_set_data_collection_links = (
                    cmd.get_objs()  # type:ignore[assignment]
                )
            elif is_read_all:
                # Must be able to read or write the case set in all the data collections
                case_set_data_collection_links = (
                    self.repository.crud(  # type:ignore[assignment]
                        uow,
                        cmd.user.id,
                        model.CaseSetDataCollectionLink,
                        None,
                        None,
                        CrudOperation.READ_ALL,
                        filter=cmd.query_filter,
                    )
                )
            elif is_read or is_delete:
                # Must be able to read or write the case set in (for is_read), or remove from
                # (for is_delete), all the data collections
                case_set_data_collection_links = (
                    self.repository.crud(  # type:ignore[assignment]
                        uow,
                        cmd.user.id,
                        model.CaseSetDataCollectionLink,
                        None,
                        cmd.get_obj_ids(),
                        CrudOperation.READ_SOME,
                    )
                )
            elif is_update:
                # Should not be allowed
                raise AssertionError(
                    "Update not allowed for case set data collection links"
                )
            else:
                raise AssertionError("Unexpected operation")

            # Go over each case set and check if the user has the required rights to it
            case_set_data_collection_map: dict[UUID, set[UUID]] = (
                map_paired_elements(  # type:ignore[assignment]
                    (
                        (x.case_set_id, x.data_collection_id)
                        for x in case_set_data_collection_links
                    ),
                    as_set=True,
                )
            )
            case_set_ids = set(case_set_data_collection_map.keys())
            case_sets = self.repository.crud(  # type:ignore[assignment]
                uow,
                cmd.user.id,
                model.CaseSet,
                None,
                list(case_set_ids),
                CrudOperation.READ_SOME,
            )
            if is_read:
                # Get read or write access per case type
                has_read_access = case_abac.get_combinations_with_access_right(
                    enum.CaseRight.READ_CASE_SET
                )
                has_write_access = case_abac.get_combinations_with_access_right(
                    enum.CaseRight.WRITE_CASE_SET
                )
                has_access = {x: set(y) for x, y in has_read_access.items()}
                for x, y in has_write_access.items():
                    if x in has_access:
                        has_access[x].update(y)
                    else:
                        has_access[x] = y
            for case_set in case_sets:
                case_type_id = case_set.case_type_id
                created_in_data_collection_id = case_set.created_in_data_collection_id
                data_collection_ids = case_set_data_collection_map[
                    case_set.id  # type:ignore[index]
                ]
                if is_read:
                    if not data_collection_ids.intersection(
                        has_access.get(case_type_id, set())
                    ):
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} does not have read or write access to case set {case_set.id} in all data collections"
                        )
                elif is_create:
                    is_allowed = case_abac.is_allowed(
                        case_type_id,
                        enum.CaseRight.ADD_CASE_SET,
                        False,
                        created_in_data_collection_id=created_in_data_collection_id,
                        current_data_collection_ids=data_collection_ids,
                        tgt_data_collection_ids=data_collection_ids,
                    )
                    if not is_allowed:
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} does not have add access to case set {case_set.id} to all data collections"
                        )
                elif is_delete:
                    is_allowed = case_abac.is_allowed(
                        case_type_id,
                        enum.CaseRight.REMOVE_CASE_SET,
                        False,
                        created_in_data_collection_id=created_in_data_collection_id,
                        current_data_collection_ids=data_collection_ids,
                        tgt_data_collection_ids=data_collection_ids,
                    )
                    if not is_allowed:
                        raise exc.UnauthorizedAuthError(
                            f"User {cmd.user.id} does not have remove access to case set {case_set.id} to all data collections"
                        )

            # Execute command in case of create or delete, return case set data
            # collection links in case of read
            if is_create or is_delete:
                return super().crud(cmd)  # type:ignore[return-value]
            elif is_read:
                return (
                    case_set_data_collection_links[0]  # type:ignore[return-value]
                    if cmd.operation == CrudOperation.READ_ONE
                    else case_set_data_collection_links
                )
            else:
                raise AssertionError("Unexpected operation")

        raise AssertionError("Unexpected operation")

    def _crud_cascade_delete(
        self, uow: BaseUnitOfWork, cmd: command.CrudCommand
    ) -> None:
        """
        In case of a delete operation, cascade delete all instances of any
        linked_model_classes that are linked to the instances in cmd.
        """
        is_delete = cmd.operation in CrudOperationSet.DELETE.value
        if not is_delete:
            # Not a delete opertion: nothing to do
            return
        model_class = cmd.MODEL_CLASS
        link_model_classes: list[Type[model.Model]] | None = None
        for (
            model_base_class,
            link_model_classes_tuple,
        ) in BaseCaseService.CASCADE_DELETE_MODEL_CLASSES.items():
            if issubclass(model_class, model_base_class):
                link_model_classes = list(link_model_classes_tuple)
                break
        if link_model_classes is None:
            # No cascade delete: nothing to do
            return
        assert cmd.user is not None and cmd.user.id is not None
        obj_ids: set[UUID] | None = cmd.get_obj_ids(
            as_set=True
        )  # type:ignore[assignment]
        # Go over each link_model_class and delete all instances that are linked to
        # the instances in cmd
        for link_model_class in link_model_classes:
            assert link_model_class.ENTITY is not None
            get_obj_id = link_model_class.ENTITY.get_obj_id
            if cmd.operation == CrudOperation.DELETE_ALL:
                # Special case: delete all instances
                self.repository.crud(
                    uow,
                    cmd.user.id,
                    link_model_class,
                    None,
                    None,
                    CrudOperation.DELETE_ALL,
                )
                continue
            assert obj_ids is not None
            # Get the instances that are linked to the instances in cmd
            get_link_id = link_model_class.ENTITY.get_link_id(model_class)
            link_objs: list = self.repository.crud(  # type:ignore[assignment]
                uow,
                cmd.user.id,
                link_model_class,
                None,
                None,
                CrudOperation.READ_ALL,
            )
            link_obj_ids = [
                get_obj_id(x) for x in link_objs if get_link_id(x) in obj_ids
            ]
            # Delete these instances
            self.repository.crud(
                uow,
                cmd.user.id,
                link_model_class,
                None,
                link_obj_ids,
                CrudOperation.DELETE_SOME,
            )

    def _crud_with_access_filter(
        self,
        uow: BaseUnitOfWork,
        cmd: command.CrudCommand,
        access_filter: Filter | None = None,
        cascade_if_delete: bool = False,
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        # Set access filter if any and call generic crud
        orig_access_filter = cmd.access_filter
        if access_filter:
            if cmd.access_filter:
                cmd.access_filter = CompositeFilter(
                    filters=[access_filter, cmd.access_filter],  # type: ignore[list-item]
                    operator=LogicalOperator.AND,
                )
            else:
                cmd.access_filter = access_filter
        if cascade_if_delete:
            self._crud_cascade_delete(uow, cmd)
        retval = super().crud(cmd)
        cmd.access_filter = orig_access_filter
        return retval  # type:ignore[return-value]

    def _read_association_with_valid_ids(
        self,
        command_class: Type[command.CrudCommand],
        field_name1: str,
        field_name2: str,
        valid_ids1: set[UUID] | frozenset[UUID] | None = None,
        valid_ids2: set[UUID] | frozenset[UUID] | None = None,
        match_all1: bool = False,
        match_all2: bool = False,
        return_type: str = "objects",
        uow: BaseUnitOfWork | None = None,
        user: model.User | None = None,
    ) -> list[model.Model] | list[UUID] | dict[UUID, set[UUID]]:
        return case_service_read_association_with_valid_ids(
            self,
            command_class,
            field_name1,
            field_name2,
            valid_ids1=valid_ids1,
            valid_ids2=valid_ids2,
            match_all1=match_all1,
            match_all2=match_all2,
            return_type=return_type,
            uow=uow,
            user=user,
        )

    def _retrieve_case_sets_with_content_right(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_set_ids: list[UUID] | None = None,
        case_type_ids: set[UUID] | None = None,
        filter: Filter | None = None,
        on_invalid_case_set_id: str = "raise",
    ) -> list[model.CaseSet]:
        # TODO: This is a temporary implementation, to be replaced by optimized query
        if right not in enum.CaseRightSet.CASE_SET_CONTENT.value:
            raise exc.InvalidArgumentsError(f"Invalid case abac right: {right.value}")
        if on_invalid_case_set_id not in {"raise", "ignore"}:
            raise exc.InvalidArgumentsError(
                f"Invalid on_invalid_case_set_id: {on_invalid_case_set_id}"
            )

        # Retrieve all case sets, potentially filtered
        case_sets: list[model.CaseSet]
        if case_set_ids:
            if filter:
                raise exc.InvalidArgumentsError(
                    "Cannot use datetime range filter with case set ids"
                )
            case_sets = self.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model.CaseSet,
                None,
                case_set_ids,
                CrudOperation.READ_SOME,
            )
        else:
            case_sets = self.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model.CaseSet,
                None,
                None,
                CrudOperation.READ_ALL,
                filter=filter,
            )

        # Filter on case_type_ids if any or verify that all case sets have a valid
        # case_type_id if case_set_ids is given
        # TODO: add more efficient implementation by adding this as a filter in the
        # call to the repository
        if case_type_ids is not None:
            if case_set_ids:
                if on_invalid_case_set_id == "raise":
                    if not all(x.case_type_id in case_type_ids for x in case_sets):
                        raise exc.InvalidArgumentsError(
                            f"Some case sets have invalid case type ids: {case_set_ids}"
                        )
                elif on_invalid_case_set_id == "ignore":
                    pass
                else:
                    raise AssertionError(
                        f"Invalid on_invalid_case_set_id: {on_invalid_case_set_id}"
                    )
            case_sets = [x for x in case_sets if x.case_type_id in case_type_ids]

        # Special case: full_access
        if case_abac.is_full_access:
            return case_sets

        # @ABAC: filter case sets to which the user has read access
        case_set_data_collections, _ = self._retrieve_case_set_data_collections_map(
            uow, user_id
        )
        has_access = case_abac.get_combinations_with_access_right(right)
        filtered_case_sets = []
        for case_set in case_sets:
            # Check if user has any access to case
            case_type_id = case_set.case_type_id
            if case_type_id not in has_access:
                if case_set_ids:
                    if on_invalid_case_set_id == "raise":
                        raise exc.UnauthorizedAuthError(
                            f"User {user_id} has no access to some requested cases"
                        )
                    elif on_invalid_case_set_id == "ignore":
                        pass
                    else:
                        raise AssertionError(
                            f"Invalid on_invalid_case_id: {on_invalid_case_set_id}"
                        )
                continue
            # Check if user has access to any of the data collections of the case set
            data_collection_ids = case_set_data_collections.get(
                case_set.id, set()  # type:ignore[arg-type]
            )
            data_collection_ids.add(case_set.created_in_data_collection_id)
            if not data_collection_ids.intersection(has_access[case_type_id]):
                if case_set_ids:
                    if on_invalid_case_set_id == "raise":
                        raise exc.UnauthorizedAuthError(
                            f"User {user_id} has no access to some requested case sets"
                        )
                    elif on_invalid_case_set_id == "ignore":
                        pass
                    else:
                        raise AssertionError(
                            f"Invalid on_invalid_case_set_id: {on_invalid_case_set_id}"
                        )
                continue
            # Keep case
            filtered_case_sets.append(case_set)
        return filtered_case_sets

    def _retrieve_cases_with_content_right(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_ids: list[UUID] | None = None,
        case_type_ids: set[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
        on_invalid_case_id: str = "raise",
        filter_content: bool = True,
        extra_access_case_type_col_ids: set[UUID] | None = None,
    ) -> list[model.Case]:
        # TODO: This is a temporary implementation, to be replaced by optimized query
        if right not in enum.CaseRightSet.CASE_CONTENT.value:
            raise exc.InvalidArgumentsError(f"Invalid case abac right: {right.value}")
        if on_invalid_case_id not in {"raise", "ignore"}:
            raise exc.InvalidArgumentsError(
                f"Invalid on_invalid_case_id: {on_invalid_case_id}"
            )

        # Retrieve all cases, potentially filtered by datetime range
        if datetime_range_filter:
            if datetime_range_filter.key and datetime_range_filter.key != "case_date":
                raise exc.InvalidArgumentsError(
                    f"Invalid datetime range filter key: {datetime_range_filter.key}"
                )
            datetime_range_filter.key = "case_date"
        cases: list[model.Case]
        if case_ids:
            if datetime_range_filter:
                raise exc.InvalidArgumentsError(
                    "Cannot use datetime range filter with case ids"
                )
            cases = self.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model.Case,
                None,
                case_ids,
                CrudOperation.READ_SOME,
            )
        else:
            cases = self.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model.Case,
                None,
                None,
                CrudOperation.READ_ALL,
                filter=datetime_range_filter,
            )

        # Filter on case_type_ids if any or verify that all cases have a valid
        # case_type_id if case_ids is given
        # TODO: add more efficient implementation by adding this as a filter in the
        # call to the repository
        if case_type_ids is not None:
            if case_ids:
                if not all(x.case_type_id in case_type_ids for x in cases):
                    raise exc.InvalidArgumentsError(
                        f"Some cases have invalid case type ids: {case_ids}"
                    )
                if on_invalid_case_id == "raise":
                    if not all(x.case_type_id in case_type_ids for x in cases):
                        raise exc.InvalidArgumentsError(
                            f"Some cases have invalid case type ids: {case_ids}"
                        )
                elif on_invalid_case_id == "ignore":
                    pass
                else:
                    raise AssertionError(
                        f"Invalid on_invalid_case_id: {on_invalid_case_id}"
                    )
            cases = [x for x in cases if x.case_type_id in case_type_ids]

        # Special case: full_access
        if case_abac.is_full_access:
            return cases

        # @ABAC: filter cases to which the user has read access, and optionally also
        # the content (case type cols)
        case_data_collections, _ = self._retrieve_case_data_collections_map(
            uow, user_id
        )
        has_access = case_abac.get_combinations_with_access_right(right)
        filtered_cases = []
        for case in cases:
            # Check if user has any access to case
            case_type_id = case.case_type_id
            if case_type_id not in has_access:
                if case_ids:
                    if on_invalid_case_id == "raise":
                        raise exc.UnauthorizedAuthError(
                            f"User {user_id} has no access to some requested cases"
                        )
                    elif on_invalid_case_id == "ignore":
                        pass
                    else:
                        raise AssertionError(
                            f"Invalid on_invalid_case_id: {on_invalid_case_id}"
                        )
                continue
            # Check if user has access to any data collection of the case
            data_collection_ids = case_data_collections.get(
                case.id, set()  # type:ignore[arg-type]
            )
            data_collection_ids.add(case.created_in_data_collection_id)
            if not data_collection_ids.intersection(has_access[case_type_id]):
                if case_ids:
                    if on_invalid_case_id == "raise":
                        raise exc.UnauthorizedAuthError(
                            f"User {user_id} has no access to some requested cases"
                        )
                    elif on_invalid_case_id == "ignore":
                        pass
                    else:
                        raise AssertionError(
                            f"Invalid on_invalid_case_id: {on_invalid_case_id}"
                        )
                continue
            # Keep case
            filtered_cases.append(case)
            # Continue to next case if case content need not be filtered
            if not filter_content:
                continue
            # Determine which case type cols the user has access to
            data_collection_col_access = case_abac.case_type_access_abacs[case_type_id]
            case_type_col_ids = set()
            for data_collection_id in data_collection_ids:
                # Add case type cols with access to the case for this data
                # collection
                case_type_access_abac = data_collection_col_access.get(
                    data_collection_id
                )
                if case_type_access_abac is not None:
                    case_type_col_ids.update(
                        case_type_access_abac.read_case_type_col_ids
                    )
            if extra_access_case_type_col_ids is not None:
                case_type_col_ids.update(extra_access_case_type_col_ids)
            if not case_type_col_ids:
                data_collection_ids_str = ", ".join(
                    [str(x) for x in data_collection_ids]
                )
                raise AssertionError(
                    f"User {user_id} has zero columns with {right.value} access to case {case.id}, data collections ({data_collection_ids_str}) even though the case has some {right.value} access"
                )
            # Filter case content
            case.content = {
                x: y for x, y in case.content.items() if x in case_type_col_ids
            }
        return filtered_cases

    def _retrieve_case_data_collections_map(
        self, uow: BaseUnitOfWork, user_id: UUID, **kwargs: Any
    ) -> tuple[dict[UUID, set[UUID]], list[model.CaseDataCollectionLink]]:
        return self._retrieve_association_map(  # type:ignore[return-value]
            uow,
            user_id,
            model.CaseDataCollectionLink,
            "case_id",
            "data_collection_id",
            **kwargs,
        )

    def _retrieve_case_set_data_collections_map(
        self, uow: BaseUnitOfWork, user_id: UUID, **kwargs: Any
    ) -> tuple[dict[UUID, set[UUID]], list[model.CaseSetDataCollectionLink]]:
        return self._retrieve_association_map(  # type:ignore[return-value]
            uow,
            user_id,
            model.CaseSetDataCollectionLink,
            "case_set_id",
            "data_collection_id",
            **kwargs,
        )

    def _retrieve_case_case_sets_map(
        self, uow: BaseUnitOfWork, user_id: UUID, **kwargs: Any
    ) -> tuple[dict[UUID, set[UUID]], list[model.CaseSetMember]]:
        return self._retrieve_association_map(  # type:ignore[return-value]
            uow,
            user_id,
            model.CaseSetMember,
            "case_id",
            "case_set_id",
            **kwargs,
        )

    def _retrieve_association_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        association_class: Type[model.Model],
        link_field_name1: str,
        link_field_name2: str,
        **kwargs: Any,
    ) -> tuple[dict[UUID, set[UUID]], list[model.Model]]:
        """
        Get a dict[obj_id1, set[obj_ids]] based on the association stored in the association_class objs.
        """
        obj_ids1: frozenset[UUID] | None = kwargs.pop("obj_ids1", None)
        obj_ids2: frozenset[UUID] | None = kwargs.pop("obj_ids2", None)
        # Create a filter to restrict the association objs if necessary
        filter: Filter | None
        if obj_ids1:
            filter1 = UuidSetFilter(key=link_field_name1, members=obj_ids1)
        else:
            filter1 = None
        if obj_ids2:
            filter2 = UuidSetFilter(key=link_field_name2, members=obj_ids2)
        else:
            filter2 = None
        if filter1 and filter2:
            filter = CompositeFilter(
                filters=[filter1, filter2], operator=LogicalOperator.AND
            )
        elif filter1:
            filter = filter1
        elif filter2:
            filter = filter2
        else:
            filter = None
        # Retrieve association objs and convert to map
        association_objs: list = self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            association_class,
            None,
            None,
            CrudOperation.READ_ALL,
            filter=filter,
        )
        association_map: dict[UUID, set[UUID]] = (
            map_paired_elements(  # type:ignore[assignment]
                (
                    (getattr(x, link_field_name1), getattr(x, link_field_name2))
                    for x in association_objs
                ),
                as_set=True,
            )
        )

        return association_map, association_objs

    def _retrieve_sequence_column_data(
        self, uow: BaseUnitOfWork, user: model.User, seq_case_type_col_id: UUID
    ) -> tuple[model.CaseTypeCol, model.Col]:
        repository = self.repository
        seq_case_type_col: model.CaseTypeCol = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.CaseTypeCol,
            None,
            seq_case_type_col_id,
            CrudOperation.READ_ONE,
        )
        seq_col: model.Col = repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            seq_case_type_col.col_id,
            CrudOperation.READ_ONE,
        )
        if seq_col.col_type != enum.ColType.GENETIC_SEQUENCE:
            raise exc.InvalidArgumentsError(
                f"Case type column {seq_col.id} is not of type {enum.ColType.GENETIC_SEQUENCE.value}"
            )
        return seq_case_type_col, seq_col

    def _verify_case_filter(
        self, uow: BaseUnitOfWork, user: model.User, filter: CompositeFilter
    ) -> list[model.Col]:
        # Retrieve case type cols corresponding to filter keys
        filter_case_type_col_ids = filter.get_keys()
        filter_case_type_cols: list[model.CaseTypeCol] = (
            self.repository.crud(  # type:ignore[assignment]
                uow,
                user.id,
                model.CaseTypeCol,
                None,
                filter_case_type_col_ids,
                CrudOperation.READ_SOME,
            )
        )
        # Retrieve cols for case type cols
        cols: list[model.Col] = self.repository.crud(  # type:ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            list(
                set(x.col_id for x in filter_case_type_cols)
            ),  # TODO: consider READ_SOME allowing duplicate ids
            CrudOperation.READ_SOME,
        )
        cols_ = {x.id: x for x in cols}
        cols = [cols_[x.col_id] for x in filter_case_type_cols]
        # Verify filter validity
        concept_valid_values: dict[UUID, set[str]] = {}
        region_valid_values: dict[UUID, set[str]] = {}
        for case_type_col, col, filter in zip(  # type:ignore[assignment]
            filter_case_type_cols, cols, filter.filters
        ):
            if col.concept_set_id or col.region_set_id:
                if isinstance(filter, StringSetFilter):
                    valid_values = None
                    if col.concept_set_id is not None:
                        # Get valid region set values
                        if col.concept_set_id not in concept_valid_values:
                            concept_set_members: list[model.ConceptSetMember] = (
                                self.app.handle(
                                    command.ConceptSetMemberCrudCommand(
                                        user=user,
                                        operation=CrudOperation.READ_ALL,
                                        query_filter=UuidSetFilter(
                                            key="concept_set_id",
                                            members=frozenset({col.concept_set_id}),
                                        ),
                                    )
                                )
                            )
                            concepts = self.app.handle(
                                command.ConceptCrudCommand(
                                    user=user,
                                    operation=CrudOperation.READ_SOME,
                                    obj_ids=[x.concept_id for x in concept_set_members],
                                )
                            )
                            concept_valid_values[col.concept_set_id] = set(
                                [str(x.id).lower() for x in concepts]
                            )
                        valid_values = concept_valid_values[col.concept_set_id]
                    elif col.region_set_id is not None:
                        # Get valid region set values
                        if col.region_set_id not in region_valid_values:
                            regions: list[model.Region] = self.app.handle(
                                command.RegionCrudCommand(
                                    user=user,
                                    operation=CrudOperation.READ_ALL,
                                    query_filter=UuidSetFilter(
                                        key="region_set_id",
                                        members=frozenset({col.region_set_id}),
                                    ),
                                )
                            )
                            region_valid_values[col.region_set_id] = set(
                                [str(x.id).lower() for x in regions]
                            )
                        valid_values = region_valid_values[col.region_set_id]
                    # Handle invalid values
                    if valid_values is not None:
                        invalid_values = [
                            str(x)
                            for x in filter.members
                            if str(x).lower() not in valid_values
                        ]
                        if len(invalid_values):
                            invalid_values_str = ", ".join(invalid_values)
                            raise exc.InvalidArgumentsError(
                                f"Column {case_type_col.id}: invalid {filter.__class__.__name__} filter members: {invalid_values_str}"
                            )
                else:
                    raise exc.InvalidArgumentsError(
                        f"Column {case_type_col.id}: invalid filter type: {filter.__class__.__name__}"
                    )

        return cols

    def _verify_case_set_member_case_type(
        self, user: model.User, case_set_members: list[model.CaseSetMember]
    ) -> None:
        with self.repository.uow() as uow:
            case_set_ids = {x.case_set_id for x in case_set_members}
            case_ids = {x.case_id for x in case_set_members}
            case_sets_: list[model.CaseSet] = (
                self.repository.crud(  # type:ignore[assignment]
                    uow,
                    user.id if user else None,
                    model.CaseSet,
                    None,
                    list(case_set_ids),
                    CrudOperation.READ_SOME,
                )
            )
            case_sets = {x.id: x for x in case_sets_}
            cases_: list[model.Case] = self.repository.crud(  # type:ignore[assignment]
                uow,
                user.id if user else None,
                model.Case,
                None,
                list(case_ids),
                CrudOperation.READ_SOME,
            )
            cases = {x.id: x for x in cases_}
        invalid_case_set_member_ids = [
            x.id
            for x in case_set_members
            if case_sets[x.case_set_id].case_type_id != cases[x.case_id].case_type_id
        ]
        if invalid_case_set_member_ids:
            invalid_case_set_member_ids_str = ", ".join(
                [str(x) for x in invalid_case_set_member_ids]
            )
            raise exc.InvalidArgumentsError(
                f"Case set members invalid, case set and case must have the same case type: {invalid_case_set_member_ids_str}"
            )

    @staticmethod
    def _get_map_functions_for_filters(
        cols: Iterable[model.Col],
    ) -> list[Callable[[Any], Any]]:

        # Check validity of filter and generate map_fns
        map_fns = []
        for col in cols:
            if col.col_type == enum.ColType.TIME_DAY:
                map_fns.append(
                    lambda x: (
                        datetime.date.fromisoformat(x) if isinstance(x, str) else x
                    )
                )
            elif col.col_type in {
                enum.ColType.TIME_WEEK,
                enum.ColType.TIME_MONTH,
                enum.ColType.TIME_QUARTER,
                enum.ColType.TIME_YEAR,
                enum.ColType.GEO_REGION,
                enum.ColType.NOMINAL,
                enum.ColType.ORDINAL,
                enum.ColType.INTERVAL,
                enum.ColType.TEXT,
                enum.ColType.ID_DIRECT,
                enum.ColType.ID_PSEUDONYMISED,
                enum.ColType.ORGANIZATION,
                enum.ColType.OTHER,
            }:
                map_fns.append(lambda x: x if isinstance(x, str) else str(x))
            elif col.col_type == enum.ColType.DECIMAL_0:
                map_fns.append(lambda x: int(x) if isinstance(x, str) else x)
            elif col.col_type in {
                enum.ColType.DECIMAL_1,
                enum.ColType.DECIMAL_2,
                enum.ColType.DECIMAL_3,
                enum.ColType.DECIMAL_4,
                enum.ColType.DECIMAL_5,
                enum.ColType.DECIMAL_6,
            }:
                map_fns.append(lambda x: Decimal(x) if isinstance(x, str) else x)
            elif col.col_type == enum.ColType.GEO_LATLON:
                map_fns.append(
                    lambda x: (
                        (float(x.split(",")[0]), float(x.split(",")[1]))
                        if isinstance(x, str)
                        else x
                    )
                )
            else:
                raise exc.InvalidArgumentsError(
                    f"Unsupported column type: {col.col_type}"
                )
        return map_fns

    @staticmethod
    def _compose_id_filter(*key_and_ids: tuple[str, set[UUID]]) -> Filter:
        if len(key_and_ids) == 1:
            key, ids = key_and_ids[0]
            return UuidSetFilter(key=key, members=ids)  # type: ignore[arg-type]
        return CompositeFilter(
            filters=[
                UuidSetFilter(key=key, members=ids)  # type: ignore[arg-type]
                for key, ids in key_and_ids
            ],
            operator=LogicalOperator.AND,
        )
