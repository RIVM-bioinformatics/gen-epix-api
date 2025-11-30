import datetime
from collections.abc import Callable, Iterable
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_date import (
    case_service_calculate_case_date,
    case_service_get_case_date_case_type_col_mappers,
)
from gen_epix.casedb.services.case.case_transformer import CaseTransformer
from gen_epix.casedb.services.case.create_case import (
    case_service_create_case_set,
    case_service_create_cases,
)
from gen_epix.casedb.services.case.create_seq import (
    case_service_create_file_for_read_set_or_seq,
    case_service_create_read_sets_or_seqs_for_cases,
)
from gen_epix.casedb.services.case.crud import crud
from gen_epix.casedb.services.case.read_association_with_valid_ids import (
    case_service_read_association_with_valid_ids,
)
from gen_epix.casedb.services.case.retrieve_case import (
    case_service_retrieve_cases_by_id,
    case_service_retrieve_cases_by_query,
)
from gen_epix.casedb.services.case.retrieve_complete_case_type import (
    case_service_retrieve_complete_case_type,
)
from gen_epix.casedb.services.case.retrieve_seq import (
    case_service_retrieve_assembly_protocols,
    case_service_retrieve_genetic_sequence_by_case,
    case_service_retrieve_genetic_sequence_fasta_by_case,
    case_service_retrieve_phylogenetic_tree,
    case_service_retrieve_sequencing_protocols,
)
from gen_epix.casedb.services.case.retrieve_stats import (
    case_service_retrieve_case_set_stats,
    case_service_retrieve_case_type_stats,
)
from gen_epix.commondb.util import map_paired_elements
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter import Filter, UuidSetFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_uuid import EqualsUuidFilter


class CaseService(BaseCaseService):

    def crud(  # type:ignore[override]
        self, cmd: command.CrudCommand
    ) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
        return crud(self, cmd)

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
            transform_result.transformed_object  # type:ignore[assignment]
        )

        return case_validation_report

    def create_cases(self, cmd: command.CreateCasesCommand) -> list[model.Case] | None:
        return case_service_create_cases(self, cmd)

    def create_case_set(
        self, cmd: command.CreateCaseSetCommand
    ) -> model.CaseSet | None:
        return case_service_create_case_set(self, cmd)

    def create_reads_sets_for_cases(
        self, cmd: command.CreateReadSetsForCasesCommand
    ) -> list[model.ReadSet]:
        retval: list[model.ReadSet] = case_service_create_read_sets_or_seqs_for_cases(
            self, cmd
        )  # type:ignore[assignment]
        return retval

    def create_seq_for_case(self, cmd: command.CreateSeqsForCasesCommand) -> model.Seq:
        retval: list[model.Seq] = case_service_create_read_sets_or_seqs_for_cases(
            self, cmd
        )  # type:ignore[assignment]
        return retval[0]

    def create_seqs_for_cases(
        self, cmd: command.CreateSeqsForCasesCommand
    ) -> list[model.Seq]:
        retval: list[model.Seq] = case_service_create_read_sets_or_seqs_for_cases(
            self, cmd
        )  # type:ignore[assignment]
        return retval

    def create_file_for_read_set(
        self, cmd: command.CreateFileForReadSetCommand
    ) -> UUID:
        return case_service_create_file_for_read_set_or_seq(self, cmd)

    def create_file_for_seq(self, cmd: command.CreateFileForSeqCommand) -> UUID:
        return case_service_create_file_for_read_set_or_seq(self, cmd)

    def retrieve_complete_case_type(
        self: DomainBaseCaseService,
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
    ) -> model.CaseQueryResult:
        return case_service_retrieve_cases_by_query(self, cmd)

    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        return case_service_retrieve_cases_by_id(self, cmd)

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

    def retrieve_genetic_sequence_by_case(
        self,
        cmd: command.RetrieveGeneticSequenceByCaseCommand,
    ) -> list[model.GeneticSequence]:
        return case_service_retrieve_genetic_sequence_by_case(self, cmd)

    def retrieve_genetic_sequence_fasta_by_case(
        self, cmd: command.RetrieveGeneticSequenceFastaByCaseCommand
    ) -> Iterable[str]:
        """
        Return a streaming iterable of FASTA formatted lines.
        Path:
        HTTP client
        -> casedb endpoint
        -> casedb service calls casedb seqdb command
        -> seqdb command (inside casedb) calls ext_app with RetrieveSeqFastaCommand
        -> seqdb service calls correct repository (dict or SA implementation) to stream Seq rows
        -> seqdb service converts rows to FASTA lines on the fly
        -> returns an iterator
        -> casedb forwards that iterator
        -> FastAPI wraps it in a StreamingResponse.
        """
        return case_service_retrieve_genetic_sequence_fasta_by_case(self, cmd)

    def retrieve_sequencing_protocols(
        self,
        cmd: command.RetrieveSequencingProtocolsCommand,
    ) -> list[model.SequencingProtocol]:
        return case_service_retrieve_sequencing_protocols(self, cmd)

    def retrieve_assembly_protocols(
        self, cmd: command.RetrieveAssemblyProtocolsCommand
    ) -> list[model.AssemblyProtocol]:
        return case_service_retrieve_assembly_protocols(self, cmd)

    def _read_association_with_valid_ids(
        self,
        command_class: type[command.CrudCommand],
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
        case_type_ids: set[UUID] | None = None,
        case_set_ids: list[UUID] | None = None,
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
        case_set_data_collections = self._retrieve_case_set_data_collections_map(
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
        case_type_id: UUID,
        case_type_settings: model.CaseTypeSettings | None = None,
        case_ids: list[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
        on_invalid_case_id: str = "raise",
        filter_content: bool = True,
        calculate_case_date: bool = False,
        extra_access_case_type_col_ids: set[UUID] | None = None,
    ) -> list[model.Case]:
        # TODO: This is a temporary implementation, to be replaced by optimized query
        if right not in enum.CaseRightSet.CASE_CONTENT.value:
            raise ValueError(f"Invalid case abac right: {right.value}")
        if on_invalid_case_id not in {"raise", "ignore"}:
            raise ValueError(f"Invalid on_invalid_case_id: {on_invalid_case_id}")
        if not filter_content and calculate_case_date:
            raise ValueError("Cannot calculate case date when filter_content is False")

        # @ABAC: verify access to case type
        access_data_collections = case_abac.get_combinations_with_access_right(
            right
        ).get(case_type_id, set())
        is_full_access = case_abac.is_full_access
        data_collection_col_access = case_abac.case_type_access_abacs.get(
            case_type_id, {}
        )
        if not access_data_collections and not is_full_access:
            raise exc.UnauthorizedAuthError(
                f"User {user_id} has no access to case type {case_type_id}"
            )

        # Verify max number of cases
        case_date_case_type_col_mappers: (
            dict[UUID, Callable[[str], datetime.datetime]] | None
        ) = {}
        max_n_cases: float = float("inf")
        if case_type_settings is not None:
            if right == enum.CaseRight.READ_CASE:
                max_n_cases = case_type_settings.read_max_n_cases
            elif right == enum.CaseRight.WRITE_CASE:
                max_n_cases = case_type_settings.update_max_n_cases
            else:
                raise NotImplementedError(f"Unsupported case right: {right}")
            case_date_case_type_col_mappers = (
                case_service_get_case_date_case_type_col_mappers(
                    self,
                    uow,
                    user_id,
                    case_type_id,
                    case_type_settings.stats_time_case_type_col_id,
                )
            )

        if case_ids and len(case_ids) > max_n_cases:
            raise exc.RequestLimitExceededAuthError(
                f"Number of requested cases {len(case_ids)} exceeds maximum allowed {max_n_cases}"
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
            if not all(x.case_type_id == case_type_id for x in cases):
                raise exc.InvalidArgumentsError(
                    f"Some cases have invalid case type ids: {case_ids}"
                )
        else:
            case_type_filter = EqualsUuidFilter(key="case_type_id", value=case_type_id)
            if datetime_range_filter:
                case_filter = CompositeFilter(
                    operator=LogicalOperator.AND,
                    filters=[case_type_filter, datetime_range_filter],
                )
            else:
                case_filter = case_type_filter
            cases = self.repository.crud(  # type:ignore[assignment]
                uow,
                user_id,
                model.Case,
                None,
                None,
                CrudOperation.READ_ALL,
                filter=case_filter,
            )

        # Special case: full_access -> nothing left to filter
        if case_abac.is_full_access:
            return cases

        # @ABAC: filter cases to which the user has access, and optionally also
        # the content (case type cols)
        case_data_collections = self._retrieve_case_data_collections_map(uow, user_id)
        filtered_cases = []
        count = 0
        for case in cases:
            # Check if user has access to any data collection of the case
            is_unauthorized_case = False
            if case.id not in case_data_collections:
                is_unauthorized_case = True
            else:
                assert case.id is not None
                data_collection_ids: set[UUID] = case_data_collections.get(
                    case.id, set()
                )
                data_collection_ids.add(case.created_in_data_collection_id)
                if not data_collection_ids.intersection(access_data_collections):
                    is_unauthorized_case = True
            if is_unauthorized_case:
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
            # Stop if maximum number of cases reached
            count += case.count if case.count is not None else 1
            if count > max_n_cases:
                break
            # Keep case
            filtered_cases.append(case)
            # Continue to next case if case content need not be filtered
            if not filter_content:
                continue
            # Determine which case type cols the user has access to
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

        # Calculate case date if necessary
        if calculate_case_date and case_date_case_type_col_mappers:
            case_service_calculate_case_date(cases, case_date_case_type_col_mappers)

        return filtered_cases

    def _retrieve_case_data_collections_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_ids: Iterable[UUID] | None = None,
        data_collection_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        return self._retrieve_association_map(
            uow,
            user_id,
            model.CaseDataCollectionLink,
            "case_id",
            "data_collection_id",
            obj_ids1=frozenset(case_ids) if case_ids else None,
            obj_ids2=frozenset(data_collection_ids) if data_collection_ids else None,
        )

    def _retrieve_case_set_data_collections_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_set_ids: Iterable[UUID] | None = None,
        data_collection_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        return self._retrieve_association_map(
            uow,
            user_id,
            model.CaseSetDataCollectionLink,
            "case_set_id",
            "data_collection_id",
            obj_ids1=frozenset(case_set_ids) if case_set_ids else None,
            obj_ids2=frozenset(data_collection_ids) if data_collection_ids else None,
        )

    def _retrieve_case_case_sets_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_ids: Iterable[UUID] | None = None,
        case_set_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        return self._retrieve_association_map(
            uow,
            user_id,
            model.CaseSetMember,
            "case_id",
            "case_set_id",
            obj_ids1=frozenset(case_ids) if case_ids else None,
            obj_ids2=frozenset(case_set_ids) if case_set_ids else None,
        )

    def _retrieve_association_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID | None,
        association_class: type[model.Model],
        link_field_name1: str,
        link_field_name2: str,
        obj_ids1: frozenset[UUID] | None = None,
        obj_ids2: frozenset[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """
        Get a dict[obj_id1, set[obj_ids]] based on the association stored in the association_class objs.
        """
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
        value_pairs_iterable: Iterable[tuple[UUID, UUID]] = self.repository.read_fields(
            uow=uow,
            user_id=user_id,
            model_class=association_class,
            field_names=[link_field_name1, link_field_name2],
            filter=filter,
        )
        association_map: dict[UUID, set[UUID]] = map_paired_elements(value_pairs_iterable, as_set=True)  # type: ignore[assignment]

        return association_map

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
