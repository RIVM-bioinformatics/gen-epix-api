"""Coordinate case commands, persistence, authorization, and seqdb operations.

The module exposes :class:`CaseService`, the concrete facade that delegates command
handling to focused case-service modules and implements shared repository, ABAC,
association, rights, caching, and content-filtering helpers.
"""

import datetime
from collections.abc import Callable, Iterable
from typing import cast
from uuid import UUID

from cachetools import cached

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_date import (
    case_service_calculate_case_date,
    case_service_get_case_date_col_mappers,
)
from gen_epix.casedb.services.case.create_case_set import case_service_create_case_set
from gen_epix.casedb.services.case.create_seq import (
    case_service_create_file_for_read_set_or_seq,
)
from gen_epix.casedb.services.case.crud_case import case_service_crud_case
from gen_epix.casedb.services.case.crud_case_data_collection_link import (
    case_service_crud_case_data_collection_link,
)
from gen_epix.casedb.services.case.crud_case_identifier import (
    case_service_crud_case_identifier,
)
from gen_epix.casedb.services.case.crud_case_set import case_service_crud_case_set
from gen_epix.casedb.services.case.crud_case_set_category import (
    case_service_crud_case_set_category,
)
from gen_epix.casedb.services.case.crud_case_set_data_collection_link import (
    case_service_crud_case_set_data_collection_link,
)
from gen_epix.casedb.services.case.crud_case_set_member import (
    case_service_crud_case_set_member,
)
from gen_epix.casedb.services.case.crud_case_set_status import (
    case_service_crud_case_set_status,
)
from gen_epix.casedb.services.case.crud_case_type import case_service_crud_case_type
from gen_epix.casedb.services.case.crud_case_type_set import (
    case_service_crud_case_type_set,
)
from gen_epix.casedb.services.case.crud_case_type_set_category import (
    case_service_crud_case_type_set_category,
)
from gen_epix.casedb.services.case.crud_case_type_set_member import (
    case_service_crud_case_type_set_member,
)
from gen_epix.casedb.services.case.crud_col import case_service_crud_col
from gen_epix.casedb.services.case.crud_col_set import case_service_crud_col_set
from gen_epix.casedb.services.case.crud_col_set_member import (
    case_service_crud_col_set_member,
)
from gen_epix.casedb.services.case.crud_dim import case_service_crud_dim
from gen_epix.casedb.services.case.crud_genetic_distance_protocol import (
    case_service_crud_genetic_distance_protocol,
)
from gen_epix.casedb.services.case.crud_ref_col import case_service_crud_ref_col
from gen_epix.casedb.services.case.crud_ref_dim import case_service_crud_ref_dim
from gen_epix.casedb.services.case.crud_tree_algorithm import (
    case_service_crud_tree_algorithm,
)
from gen_epix.casedb.services.case.crud_tree_algorithm_class import (
    case_service_crud_tree_algorithm_class,
)
from gen_epix.casedb.services.case.read_association_with_valid_ids import (
    case_service_read_association_with_valid_ids,
)
from gen_epix.casedb.services.case.retrieve_case import (
    case_service_retrieve_case_cohort_links_by_case_type,
    case_service_retrieve_cases_by_id,
    case_service_retrieve_cases_by_query,
)
from gen_epix.casedb.services.case.retrieve_complete_case_type import (
    case_service_retrieve_complete_case_type,
)
from gen_epix.casedb.services.case.retrieve_is_own_cases import (
    case_service_retrieve_is_own_cases,
)
from gen_epix.casedb.services.case.retrieve_seq import (
    case_service_retrieve_genetic_sequence_fasta_by_case,
    case_service_retrieve_phylogenetic_tree,
    case_service_retrieve_protocols,
)
from gen_epix.casedb.services.case.retrieve_similar_cases import (
    case_service_retrieve_similar_cases,
)
from gen_epix.casedb.services.case.retrieve_stats import (
    case_service_retrieve_case_stats,
)
from gen_epix.casedb.services.case.upload import case_service_upload_cases
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter import Filter, LogicalOperator, UuidSetFilter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.util import map_paired_elements


class CaseService(BaseCaseService):
    """Encapsulates case command handling and cross-service orchestration.

    The service delegates public commands to focused handlers while supplying the
    shared repository and authorization operations they require. Repository work is
    scoped either to a handler-owned unit of work or to a unit supplied to a private
    helper. Case access is evaluated from command-attached ABAC data; content
    filtering mutates returned case models by removing inaccessible columns.

    seqdb collaboration is performed through application commands. Those remote
    operations are not atomic with casedb repository units of work. Complete case
    types are cached by case type and user for the inherited cache lifetime.

    Attributes:
        role_map: Mapping of application roles by identifier.
        role_set_map: Mapping of application role sets by identifier.
    """

    _RETRIEVE_COMPLETE_CASE_TYPE_CACHE = (
        BaseCaseService._RETRIEVE_COMPLETE_CASE_TYPE_CACHE
    )

    def upload_cases(
        self, cmd: command.UploadCasesCommand
    ) -> model.CaseBatchUploadResult:
        """Verify and persist a case batch and its seqdb samples.

        Verification and persistence can mutate uploaded cases and the returned
        batch result with normalized content, identifiers, statuses, and logs.
        casedb and seqdb changes do not share one atomic transaction.

        Args:
            cmd: Case upload command and batch to process.

        Returns:
            Per-case upload outcomes and validation issues.

        Raises:
            FeatureDisabledServiceError: If case upload is disabled.
        """
        return case_service_upload_cases(self, cmd)

    def create_case_set(
        self, cmd: command.CreateCaseSetCommand
    ) -> model.CaseSet | None:
        """Create an authorized case set and its requested associations.

        The case set and its collection and member links are persisted in one
        casedb unit of work. Policies attached to ``cmd`` are propagated to the
        nested association commands.

        Args:
            cmd: Case set, collection IDs, and optional member case IDs.

        Returns:
            The created case set.

        Raises:
            UnauthorizedAuthError: If the user cannot create the set in every
                requested data collection.
        """
        return case_service_create_case_set(self, cmd)

    def create_file_for_read_set(
        self, cmd: command.CreateFileForReadSetCommand
    ) -> UUID:
        """Create or reuse a seqdb file for a case-linked read set.

        casedb access validation and seqdb file creation and read-set update occur
        through separate transactions. Re-uploading identical uncompressed content
        returns the existing file identifier.

        Args:
            cmd: File content and linked case, column, and read-set direction.

        Returns:
            Existing or newly created seqdb file identifier.

        Raises:
            InvalidArgumentsError: If the link, column, case type, command, or
                existing file content is invalid.
            UnauthorizedAuthError: If the user lacks column-level write access.
            ValueError: If an unsupported command branch is reached.
        """
        return case_service_create_file_for_read_set_or_seq(self, cmd)

    def create_file_for_seq(self, cmd: command.CreateFileForSeqCommand) -> UUID:
        """Create or reuse a seqdb file for a case-linked sequence.

        casedb access validation and seqdb file creation and sequence update occur
        through separate transactions. Re-uploading identical uncompressed content
        returns the existing file identifier.

        Args:
            cmd: File content and linked case and sequence column.

        Returns:
            Existing or newly created seqdb file identifier.

        Raises:
            InvalidArgumentsError: If the link, column, case type, command, or
                existing file content is invalid.
            UnauthorizedAuthError: If the user lacks column-level write access.
            ValueError: If an unsupported command branch is reached.
        """
        return case_service_create_file_for_read_set_or_seq(self, cmd)

    @cached(
        cache=_RETRIEVE_COMPLETE_CASE_TYPE_CACHE,
        key=lambda self, cmd: (cmd.case_type_id, cmd.user.id if cmd.user else None),
    )
    def retrieve_complete_case_type(
        self,
        cmd: command.RetrieveCompleteCaseTypeCommand,
    ) -> model.CompleteCaseType:
        """Retrieve accessible case-type metadata with a user-scoped cache.

        Results are cached for the inherited TTL by case type and user identifier.
        Internal commands without a user follow the full-access metadata path.
        Callers must treat returned metadata as shared cached state.

        Args:
            cmd: Case type and optional user context.

        Returns:
            Complete case-type metadata and effective access mappings.
        """
        return case_service_retrieve_complete_case_type(self, cmd)

    def retrieve_case_stats(
        self,
        cmd: command.RetrieveCaseTypeStatsCommand | command.RetrieveCaseSetStatsCommand,
    ) -> list[model.CaseStats]:
        """Calculate access-aware statistics by case type or case set.

        Args:
            cmd: Statistics scope and optional date-range restriction.

        Returns:
            Statistics for each accessible requested case type or set.

        Raises:
            UnauthorizedAuthError: If READ_CASE access is missing for a requested
                case type or the type of a requested case set.
        """
        return case_service_retrieve_case_stats(self, cmd)

    def retrieve_cases_by_query(
        self, cmd: command.RetrieveCasesByQueryCommand
    ) -> model.CaseQueryResult:
        """Retrieve case IDs after ABAC, case-set, date, and content filtering.

        String content-filter keys in ``cmd.case_query`` are converted to UUIDs in
        place. The configured limit is applied after all requested filters.

        Args:
            cmd: Case query and acting-user context.

        Returns:
            Matching case IDs and whether the result limit was exceeded.

        Raises:
            NotImplementedError: If an explicitly empty case-set selection is used.
            UnauthorizedAuthError: If the user cannot read the case type or a
                requested case set.
            InvalidArgumentsError: If filter columns, members, or types are invalid.
        """
        return case_service_retrieve_cases_by_query(self, cmd)

    def retrieve_case_cohort_links_by_case_type(
        self, cmd: command.RetrieveCaseCohortLinksByCaseTypeCommand
    ) -> list[model.CaseCohortLink]:
        """Retrieve cohort links for every case of one case type.

        Args:
            cmd: Case type and whether cases without cohort metadata are included.

        Returns:
            Case-to-cohort links, with null placeholders for missing links when
            requested.
        """
        return case_service_retrieve_case_cohort_links_by_case_type(self, cmd)

    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        """Retrieve requested cases with ABAC-filtered content.

        Returned case models are mutated by the filtering pipeline to remove columns
        the user cannot read, and the configured case-type limit is enforced.

        Args:
            cmd: Case type and requested case identifiers.

        Returns:
            Accessible cases in repository result order.

        Raises:
            InvalidArgumentsError: If the case type or requested cases are invalid.
            UnauthorizedAuthError: If a requested case is inaccessible.
        """
        return case_service_retrieve_cases_by_id(self, cmd)

    def retrieve_case_or_set_rights(
        self,
        cmd: command.RetrieveCaseRightsCommand | command.RetrieveCaseSetRightsCommand,
    ) -> list[model.CaseRights] | list[model.CaseSetRights]:
        """Resolve effective rights for requested cases or case sets.

        Entities and collection links are read in one repository unit of work. Each
        entity's creation collection is included in its effective rights. Empty
        identifier input returns immediately.

        Args:
            cmd: Rights command and requested case or case-set identifiers.

        Returns:
            Rights objects in repository result order.
        """
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
            cases_or_sets: list[model.CaseSet] | list[model.Case] = (
                self.repository.crud(
                    uow,
                    user.id,
                    model.CaseSet if is_case_set else model.Case,
                    CrudOperation.READ_SOME,
                    obj_ids=case_or_set_ids,
                )
            )
            # Retrieve case/set data collection links
            key = "case_set_id" if is_case_set else "case_id"
            case_or_set_data_collection_links: (
                list[model.CaseDataCollectionLink]
                | list[model.CaseSetDataCollectionLink]
            ) = self.repository.crud(
                uow,
                user.id,
                (
                    model.CaseSetDataCollectionLink
                    if is_case_set
                    else model.CaseDataCollectionLink
                ),
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
                data_collection_ids,
            )
            retval.append(case_abac.get_case_set_rights(*args) if is_case_set else case_abac.get_case_rights(*args))  # type: ignore[arg-type]

        return retval

    def retrieve_phylogenetic_tree(
        self, cmd: command.RetrievePhylogeneticTreeByCasesCommand
    ) -> model.PhylogeneticTree:
        """Build a seqdb phylogenetic tree from accessible case profiles.

        Case content is filtered before profile IDs cross the service boundary, and
        returned leaf profile IDs are mapped back to case IDs.

        Args:
            cmd: Cases, distance column, tree algorithm, and QC restrictions.

        Returns:
            Tree annotated with the casedb genetic-distance protocol identifier.

        Raises:
            InvalidArgumentsError: If the distance column has an incompatible case
                type or column type.
            UnauthorizedAuthError: If the selected tree algorithm is not allowed.
        """
        return case_service_retrieve_phylogenetic_tree(self, cmd)

    def retrieve_similar_cases(
        self, cmd: command.RetrieveSimilarCasesCommand
    ) -> command.RetrieveSimilarCasesReturnValue:
        """Retrieve accessible cases genetically similar to query cases.

        Only profiles from ABAC-filtered cases are sent to seqdb. Query cases are
        excluded, and candidates are filtered again before return.

        Args:
            cmd: Query cases, distance column, and maximum genetic distance.

        Returns:
            Accessible similar cases with derived dates, or an empty result.

        Raises:
            InvalidArgumentsError: If the distance column has an incompatible case
                type or column type.
        """
        return case_service_retrieve_similar_cases(self, cmd)

    def retrieve_genetic_sequence_fasta_by_case(
        self, cmd: command.RetrieveGeneticSequenceFastaByCaseCommand
    ) -> Iterable[str]:
        """Return lazy FASTA lines for accessible case-linked sequences.

        The handler resolves and filters cases in casedb, then forwards sequence IDs
        through the configured seqdb application. seqdb retains repository iteration
        and FASTA conversion laziness so transport code can stream the result.

        Args:
            cmd: Cases and the genetic-sequence content column to retrieve.

        Returns:
            Lazy FASTA-formatted text lines produced by seqdb.

        Raises:
            InvalidArgumentsError: If no case identifiers are supplied.
            NoResultsError: If an accessible requested case lacks a sequence value.
        """
        return case_service_retrieve_genetic_sequence_fasta_by_case(self, cmd)

    def retrieve_protocols(
        self, cmd: command.RetrieveProtocolsCommand
    ) -> list[seqdb_model.Protocol]:
        """Retrieve seqdb protocols of the requested protocol type.

        Args:
            cmd: User context and protocol type restriction.

        Returns:
            seqdb protocols whose type matches the command.
        """
        return case_service_retrieve_protocols(self, cmd)

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
        """Read associations constrained by valid endpoint identifiers.

        An existing ``uow`` is reused when supplied; otherwise the handler owns a
        repository unit of work. Empty valid-ID sets return without repository
        access.

        Args:
            command_class: CRUD command class for the association model.
            field_name1: First endpoint field name.
            field_name2: Second endpoint field name.
            valid_ids1: Optional accepted first-endpoint identifiers.
            valid_ids2: Optional accepted second-endpoint identifiers.
            match_all1: Require second endpoints to link to every first endpoint.
            match_all2: Require first endpoints to link to every second endpoint.
            return_type: Objects, endpoint IDs, or a directional association map.
            uow: Caller-owned unit of work to reuse, if any.
            user: Optional user attached to the generated read command.

        Returns:
            Association objects, endpoint IDs, or grouped endpoint IDs.

        Raises:
            ValueError: If the return mode or match-all combination is invalid.
            AssertionError: If a validated mode reaches an unexpected branch.
        """
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
        case_type_id: UUID | None = None,
        case_set_ids: list[UUID] | None = None,
        filter: Filter | None = None,
        on_invalid_case_set_id: str = "raise",
    ) -> list[model.CaseSet]:
        """Retrieve case sets for which a user has a content right.

        The caller owns ``uow``. Requested IDs are validated individually, while an
        unrestricted read filters inaccessible sets. The creation collection is
        included when evaluating access.

        Args:
            uow: Active repository unit of work.
            user_id: User whose access is evaluated.
            case_abac: Effective case access metadata.
            right: Required case-set content right.
            case_type_id: Optional case type restriction.
            case_set_ids: Optional requested case-set identifiers.
            filter: Repository filter used only when IDs are not supplied.
            on_invalid_case_set_id: Whether inaccessible requested IDs raise or are
                ignored.

        Returns:
            Accessible case sets satisfying the supplied restrictions.

        Raises:
            InvalidArgumentsError: If the right or invalid-ID mode is unsupported,
                or requested sets have an incompatible case type.
            UnauthorizedAuthError: If a requested set is inaccessible and raising is
                configured.
            AssertionError: If an unsupported invalid-ID mode reaches validation.
        """
        # TODO: This is a temporary implementation, to be replaced by optimized query
        self.validate_case_right(right, on_invalid_case_set_id)
        case_sets: list[model.CaseSet] = self.repository.crud(
            uow,
            user_id,
            model.CaseSet,
            CrudOperation.READ_SOME if case_set_ids else CrudOperation.READ_ALL,
            filter=None if case_set_ids else filter,
            obj_ids=case_set_ids if case_set_ids else None,
        )

        # Filter on case_type_id if any or verify that all case sets have the valid
        # case_type_id if case_set_ids is given
        # TODO: add more efficient implementation by adding this as a filter in the
        # call to the repository
        if case_type_id is not None:
            case_sets = self._filter_case_sets_by_same_case_type_id(
                case_type_id, case_set_ids, on_invalid_case_set_id, case_sets
            )
        if case_abac.is_full_access:
            return case_sets
        case_set_data_collections = self._retrieve_case_set_data_collections_map(
            uow, user_id
        )
        has_access = case_abac.get_combinations_with_access_right(right)
        filtered_case_sets: list[model.CaseSet] = []
        if case_set_ids:
            # Read some: check if access to each of the requested case sets, and filter out those without access
            for case_set in case_sets:
                self._validate_case_set_access(
                    case_set,
                    user_id,
                    case_set_ids,
                    on_invalid_case_set_id,
                    case_set_data_collections,
                    has_access,
                )
            filtered_case_sets.extend(case_sets)
        else:
            # Read all: filter out case sets without access
            for case_set in case_sets:
                if self._validate_case_set_access(
                    case_set,
                    user_id,
                    None,
                    on_invalid_case_set_id,
                    case_set_data_collections,
                    has_access,
                ):
                    filtered_case_sets.append(case_set)
        return filtered_case_sets

    def _has_case_set_access(
        self,
        case_set: model.CaseSet,
        case_set_data_collections: dict[UUID, set[UUID]],
        has_access: dict[UUID, set[UUID]],
    ) -> bool:
        """Check case-type and collection access for one case set.

        Args:
            case_set: Case set to evaluate.
            case_set_data_collections: Collection IDs grouped by case-set ID.
            has_access: Accessible collection IDs grouped by case-type ID.

        Returns:
            Whether an associated or creation collection grants access.
        """
        if case_set.case_type_id not in has_access:
            return False

        # Check if user has access to any of the data collections of the case set
        assert case_set.id is not None
        data_collection_ids = case_set_data_collections.get(case_set.id, set())
        data_collection_ids.add(case_set.created_in_data_collection_id)

        if not data_collection_ids & has_access.get(case_set.case_type_id, set()):
            return False

        return True

    def _validate_case_set_access(
        self,
        case_set: model.CaseSet,
        user_id: UUID,
        case_set_ids: list[UUID] | None,
        on_invalid_case_set_id: str,
        case_set_data_collections: dict[UUID, set[UUID]],
        has_access: dict[UUID, set[UUID]],
    ) -> bool:
        """Check one case set and enforce requested-ID failure behavior.

        Args:
            case_set: Case set to authorize.
            user_id: User identifier included in authorization errors.
            case_set_ids: Requested IDs, or ``None`` for a filter-only read.
            on_invalid_case_set_id: Whether inaccessible requested IDs raise or are
                ignored.
            case_set_data_collections: Collections grouped by case-set ID.
            has_access: Accessible collections grouped by case-type ID.

        Returns:
            Whether the user has access to the case set.

        Raises:
            UnauthorizedAuthError: If a requested set is inaccessible and raising is
                configured.
            AssertionError: If inaccessible requested IDs use an unsupported mode.
        """
        has_access_to_case_set = self._has_case_set_access(
            case_set, case_set_data_collections, has_access
        )
        if case_set_ids:
            if not has_access_to_case_set:
                if on_invalid_case_set_id == "raise":
                    raise exc.UnauthorizedAuthError(
                        "e6782185",
                        f"User {user_id} has no access to some requested cases",
                    )
                if on_invalid_case_set_id == "ignore":
                    pass
                else:
                    raise AssertionError(
                        f"Invalid on_invalid_case_id: {on_invalid_case_set_id}"
                    )
        return has_access_to_case_set

    def _filter_case_sets_by_same_case_type_id(
        self,
        case_type_id: UUID,
        case_set_ids: list[UUID] | None,
        on_invalid_case_set_id: str,
        case_sets: list[model.CaseSet],
    ) -> list[model.CaseSet]:
        """Restrict case sets to one case type and validate requested IDs.

        Args:
            case_type_id: Required case type identifier.
            case_set_ids: Explicitly requested IDs, if any.
            on_invalid_case_set_id: Failure behavior for incompatible requested sets.
            case_sets: Retrieved case sets to filter.

        Returns:
            Case sets whose case type matches ``case_type_id``.

        Raises:
            InvalidArgumentsError: If a requested set has another case type and
                raising is configured.
            AssertionError: If explicit IDs use an unsupported failure mode.
        """
        if case_set_ids:
            if on_invalid_case_set_id == "raise":
                if not all(x.case_type_id == case_type_id for x in case_sets):
                    raise exc.InvalidArgumentsError(
                        "0c4731c3",
                        f"Some case sets have invalid CaseType ids: {case_set_ids}",
                    )
            else:
                raise AssertionError(
                    f"Invalid on_invalid_case_set_id: {on_invalid_case_set_id}"
                )

        return [x for x in case_sets if x.case_type_id == case_type_id]

    def validate_case_right(
        self, right: enum.CaseRight, on_invalid_case_set_id: str
    ) -> None:
        """Validate case-set content access arguments.

        Args:
            right: Case-set content right to validate.
            on_invalid_case_set_id: Requested-ID failure mode.

        Raises:
            InvalidArgumentsError: If the right or failure mode is unsupported.
        """
        if right not in enum.CaseRightSet.CASE_SET_CONTENT.value:
            raise exc.InvalidArgumentsError(
                "28123c2c", f"Invalid case abac right: {right.value}"
            )
        if on_invalid_case_set_id not in {"raise", "ignore"}:
            raise exc.InvalidArgumentsError(
                "dbc2e500", f"Invalid on_invalid_case_set_id: {on_invalid_case_set_id}"
            )

    def _retrieve_cases_with_content_right(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_type_id: UUID,
        case_ids: list[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
        on_invalid_case_id: str = "raise",
        filter_content: bool = True,
        calculate_case_date: bool = False,
        extra_access_col_ids: set[UUID] | None = None,
        apply_max_n_cases: bool = True,
    ) -> tuple[list[model.Case], bool]:
        """Retrieve cases under case-level and column-level ABAC restrictions.

        The caller owns ``uow``. The helper may normalize
        ``datetime_range_filter.key`` to ``"timed_at"`` in place and removes
        inaccessible entries from each returned case's ``content`` mapping. Derived
        case dates are calculated only after access filtering.

        Args:
            uow: Active repository unit of work.
            user_id: User whose access is evaluated.
            case_abac: Effective case access metadata.
            right: Required READ_CASE or WRITE_CASE right.
            case_type_id: Required case type identifier.
            case_ids: Optional requested case identifiers.
            datetime_range_filter: Optional case-date range restriction.
            on_invalid_case_id: Whether inaccessible requested IDs raise or are
                ignored.
            filter_content: Whether inaccessible content columns are removed.
            calculate_case_date: Whether accessible date columns populate case date.
            extra_access_col_ids: Additional columns retained during filtering.
            apply_max_n_cases: Whether configured request and result limits apply.

        Returns:
            Accessible cases and whether the configured result limit was exceeded.

        Raises:
            ValueError: If access or filtering arguments are incompatible.
            InvalidArgumentsError: If the case type or date filter is invalid.
            UnauthorizedAuthError: If case-type or requested-case access is missing.
            RequestLimitExceededAuthError: If explicit IDs exceed the configured
                maximum.
            NotImplementedError: If limit resolution receives an unsupported right.
            AssertionError: If content filtering finds no accessible columns.
        """
        # TODO: This is a temporary implementation, to be replaced by optimized query
        self._validate_case_access_args(
            right, on_invalid_case_id, filter_content, calculate_case_date
        )
        access_data_collections, data_collection_col_access = (
            self._resolve_case_type_access(user_id, case_abac, right, case_type_id)
        )
        case_type = self._load_case_type(uow, user_id, case_type_id)

        # Verify max number of cases
        case_date_col_mappers, max_n_cases = self._resolve_case_date_mappers_and_limits(
            uow,
            user_id,
            case_type,
            right,
            apply_max_n_cases,
            case_abac.is_full_access,
        )

        if case_ids and max_n_cases > 0 and len(case_ids) > max_n_cases:
            raise exc.RequestLimitExceededAuthError(
                "f9c1adb2",
                f"Number of requested cases {len(case_ids)} exceeds maximum allowed {max_n_cases}",
            )

        # Retrieve all cases, potentially filtered by datetime range
        if datetime_range_filter:
            if datetime_range_filter.key and datetime_range_filter.key != "timed_at":
                raise exc.InvalidArgumentsError(
                    "c0adc8e0",
                    f"Invalid datetime range filter key: {datetime_range_filter.key}",
                )
            datetime_range_filter.key = "timed_at"
        cases, is_max_results_exceeded = (
            self._retrieve_cases_by_ids_or_case_type_filter(
                uow, user_id, case_type_id, case_ids, datetime_range_filter, max_n_cases
            )
        )

        if case_abac.is_full_access:
            return cases, is_max_results_exceeded

        # @ABAC: filter cases to which the user has access, and optionally also
        # the content (Cols)
        filtered_cases, is_max_results_exceeded = (
            self._filter_cases_by_access_and_content(
                uow,
                user_id,
                right,
                case_ids,
                on_invalid_case_id,
                filter_content,
                extra_access_col_ids,
                access_data_collections,
                data_collection_col_access,
                max_n_cases,
                cases,
            )
        )

        # Calculate case date if necessary
        if calculate_case_date and case_date_col_mappers:
            case_service_calculate_case_date(cases, case_date_col_mappers)

        return filtered_cases, is_max_results_exceeded

    def _filter_cases_by_access_and_content(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        right: enum.CaseRight,
        case_ids: list[UUID] | None,
        on_invalid_case_id: str,
        filter_content: bool,
        extra_access_col_ids: set[UUID] | None,
        access_data_collections: set[UUID],
        data_collection_col_access: dict[UUID, model.CaseTypeAccessAbac],
        max_n_cases: int,
        cases: list[model.Case],
    ) -> tuple[list[model.Case], bool]:
        """Apply case access, weighted limits, and in-place content filtering.

        Args:
            uow: Active repository unit of work.
            user_id: User whose access is evaluated.
            right: Required case content right.
            case_ids: Explicitly requested case IDs, if any.
            on_invalid_case_id: Failure behavior for inaccessible requested cases.
            filter_content: Whether returned content is filtered in place.
            extra_access_col_ids: Additional columns retained in content.
            access_data_collections: Collections granting case-level access.
            data_collection_col_access: Column access by collection.
            max_n_cases: Maximum weighted result count, or zero for unlimited.
            cases: Retrieved cases to filter and potentially mutate.

        Returns:
            Accessible cases and whether filtering stopped at the result limit.

        Raises:
            UnauthorizedAuthError: If a requested case is inaccessible and raising is
                configured.
            AssertionError: If an accessible case has no permitted content columns.
        """
        case_data_collections = self._retrieve_case_data_collections_map(uow, user_id)
        filtered_cases: list[model.Case] = []
        count = 0
        is_max_results_exceeded = False
        case_access_cache: dict[frozenset[UUID], set[UUID]] = {}
        for case in cases:
            data_collection_ids = (
                self._authorize_case(
                    case,
                    case_ids,
                    on_invalid_case_id,
                    user_id,
                    case_data_collections,
                    access_data_collections,
                )
                or frozenset()
            )

            if not data_collection_ids:
                # No access to case
                continue
            count += case.count if case.count is not None else 1
            if max_n_cases > 0 and count > max_n_cases:
                is_max_results_exceeded = True
                break
            # Keep case
            filtered_cases.append(case)

            # Continue to next case if case content need not be filtered
            if filter_content:
                self._filter_case_content(
                    case,
                    data_collection_ids,
                    data_collection_col_access,
                    extra_access_col_ids,
                    right,
                    user_id,
                    case_access_cache,
                )

        return filtered_cases, is_max_results_exceeded

    def _filter_case_content(
        self,
        case: model.Case,
        data_collection_ids: frozenset[UUID],
        data_collection_col_access: dict[UUID, model.CaseTypeAccessAbac],
        extra_access_col_ids: set[UUID] | None,
        right: enum.CaseRight,
        user_id: UUID,
        case_access_cache: dict[frozenset[UUID], set[UUID]],
    ) -> None:
        """Remove inaccessible columns from a case's content in place.

        Accessible column sets are cached by collection combination for reuse during
        one filtering pass.

        Args:
            case: Case whose content is replaced with an accessible subset.
            data_collection_ids: Collections associated with the case.
            data_collection_col_access: Column access by collection.
            extra_access_col_ids: Additional columns to retain.
            right: Right used to describe invalid zero-column access.
            user_id: User identifier used in validation errors.
            case_access_cache: Mutable cache of columns by collection combination.

        Raises:
            AssertionError: If no content column is accessible for the case.
        """
        if data_collection_ids in case_access_cache:
            col_ids = case_access_cache[data_collection_ids]
        else:
            col_ids: set[UUID] = set()
            for data_collection_id in data_collection_ids:
                abac = data_collection_col_access.get(data_collection_id)
                if abac:
                    col_ids.update(abac.read_col_ids)
            if extra_access_col_ids:
                col_ids.update(extra_access_col_ids)

            if not col_ids:
                raise AssertionError(
                    f"User {user_id} has zero columns with {right.value} access to case {case.id}"
                )
            case_access_cache[data_collection_ids] = col_ids
        case.content = {x: y for x, y in case.content.items() if x in col_ids}

    def _authorize_case(
        self,
        case: model.Case,
        case_ids: list[UUID] | None,
        on_invalid_case_id: str,
        user_id: UUID,
        case_data_collections: dict[UUID, set[UUID]],
        access_data_collections: set[UUID],
    ) -> frozenset[UUID] | None:
        """Resolve a case's collections when any collection grants access.

        Args:
            case: Case to authorize.
            case_ids: Explicitly requested IDs, if any.
            on_invalid_case_id: Failure behavior for inaccessible requested cases.
            user_id: User identifier included in authorization errors.
            case_data_collections: Collection IDs grouped by case ID.
            access_data_collections: Collections granting the required access.

        Returns:
            All associated and creation collection IDs, or ``None`` when inaccessible
            or when the case has no identifier.

        Raises:
            UnauthorizedAuthError: If a requested case is inaccessible and raising
                is configured.
        """
        case_id = case.id
        if case_id is None:
            return None
        data_collection_ids = case_data_collections.get(case_id, set()) | {
            case.created_in_data_collection_id
        }
        if not bool(data_collection_ids & access_data_collections):
            if case_ids and on_invalid_case_id == "raise":
                raise exc.UnauthorizedAuthError(
                    "a7f7b2a0", f"User {user_id} has no access to some requested cases"
                )
            return None

        return frozenset(data_collection_ids)

    def _retrieve_cases_by_ids_or_case_type_filter(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_type_id: UUID,
        case_ids: list[UUID] | None = None,
        datetime_range_filter: DatetimeRangeFilter | None = None,
        max_n_cases: int = 0,
    ) -> tuple[list[model.Case], bool]:
        """Retrieve cases by explicit IDs or by case type and date range.

        The caller owns ``uow``. Explicit-ID reads preserve repository result order;
        unrestricted reads are truncated after the repository query.

        Args:
            uow: Active repository unit of work.
            user_id: User identifier used for repository access.
            case_type_id: Required case type identifier.
            case_ids: Optional explicit case identifiers.
            datetime_range_filter: Optional case-date restriction for type reads.
            max_n_cases: Maximum returned cases, or zero for unlimited.

        Returns:
            Retrieved cases and whether a type read exceeded the result limit.

        Raises:
            RequestLimitExceededAuthError: If explicit IDs exceed the limit.
            InvalidArgumentsError: If IDs are combined with a date filter or resolve
                to cases of another case type.
        """
        cases: list[model.Case]
        if case_ids:
            if max_n_cases > 0 and len(case_ids) > max_n_cases:
                raise exc.RequestLimitExceededAuthError(
                    "f9c1adb2",
                    f"Number of requested cases {len(case_ids)} exceeds maximum allowed {max_n_cases}",
                )
            if datetime_range_filter:
                raise exc.InvalidArgumentsError(
                    "271e9667", "Cannot use datetime range filter with case ids"
                )
            cases = self.repository.crud(
                uow,
                user_id,
                model.Case,
                CrudOperation.READ_SOME,
                obj_ids=case_ids,
            )
            if not all(x.case_type_id == case_type_id for x in cases):
                raise exc.InvalidArgumentsError(
                    "d0120f09", f"Some cases have invalid CaseType ids: {case_ids}"
                )
            is_max_results_exceeded = False
        else:
            case_type_filter = EqualsUuidFilter(key="case_type_id", value=case_type_id)
            if datetime_range_filter:
                case_filter: Filter = CompositeFilter(
                    operator=LogicalOperator.AND,
                    filters=[case_type_filter, datetime_range_filter],
                )
            else:
                case_filter = case_type_filter
            cases = self.repository.crud(
                uow,
                user_id,
                model.Case,
                CrudOperation.READ_ALL,
                filter=case_filter,
            )
            is_max_results_exceeded = max_n_cases > 0 and len(cases) > max_n_cases
            cases = cases[:max_n_cases] if is_max_results_exceeded else cases

        return cases, is_max_results_exceeded

    def _resolve_case_date_mappers_and_limits(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_type: model.CaseType,
        right: enum.CaseRight,
        apply_max_n_cases: bool,
        is_full_access: bool,
    ) -> tuple[dict[UUID, Callable[[str], datetime.datetime]] | None, int]:
        """Resolve case-date converters and the effective case limit.

        Args:
            uow: Active repository unit of work.
            user_id: User identifier used for metadata reads.
            case_type: Case type supplying operation-specific limits.
            right: READ_CASE or WRITE_CASE operation being limited.
            apply_max_n_cases: Whether a configured limit should be resolved.
            is_full_access: Whether ABAC date-column filtering can be skipped.

        Returns:
            Accessible date-column converters and the effective maximum case count.

        Raises:
            NotImplementedError: If limit resolution receives an unsupported right.
            ValueError: If case-date metadata cannot use a temporal converter.
        """
        case_date_col_mappers: dict[UUID, Callable[[str], datetime.datetime]] | None = (
            {}
        )
        max_n_cases = 0
        if apply_max_n_cases:
            if right == enum.CaseRight.READ_CASE:
                _raw = case_type.props.read_max_n_cases
                max_n_cases = _raw if _raw > 0 else self._default_props.read_max_n_cases
            elif right == enum.CaseRight.WRITE_CASE:
                _raw = case_type.props.update_max_n_cases
                max_n_cases = (
                    _raw if _raw > 0 else self._default_props.update_max_n_cases
                )
            else:
                raise NotImplementedError(f"Unsupported case right: {right}")
        if not is_full_access:
            case_date_col_mappers = case_service_get_case_date_col_mappers(
                self, uow, user_id, cast(UUID, case_type.id)
            )

        return case_date_col_mappers, max_n_cases

    def _load_case_type(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_type_id: UUID,
    ) -> model.CaseType:
        """Load one case type in a caller-owned unit of work.

        Args:
            uow: Active repository unit of work.
            user_id: User identifier used for repository access.
            case_type_id: Case type identifier to load.

        Returns:
            The requested case type.

        Raises:
            InvalidArgumentsError: If the case type does not exist.
        """
        case_types: list[model.CaseType] = self.repository.crud(
            uow,
            user_id,
            model.CaseType,
            CrudOperation.READ_SOME,
            obj_ids=[case_type_id],
        )
        if not case_types:
            raise exc.InvalidArgumentsError(
                "ccd3ccac", f"CaseType not found: {case_type_id}"
            )
        case_type = case_types[0]
        return case_type

    def _resolve_case_type_access(
        self,
        user_id: UUID,
        case_abac: model.CaseAbac,
        right: enum.CaseRight,
        case_type_id: UUID,
    ) -> tuple[set[UUID], dict[UUID, model.CaseTypeAccessAbac]]:
        """Resolve case-level collections and column access for one case type.

        Args:
            user_id: User whose access is evaluated.
            case_abac: Effective case access metadata.
            right: Required case content right.
            case_type_id: Case type whose access is resolved.

        Returns:
            Accessible collection IDs and per-collection column access.

        Raises:
            UnauthorizedAuthError: If a non-full-access user has no matching case
                access for the case type.
        """
        access_data_collections = case_abac.get_combinations_with_access_right(
            right
        ).get(case_type_id, set())
        data_collection_col_access = case_abac.case_type_access_abacs.get(
            case_type_id, {}
        )
        if not access_data_collections and not case_abac.is_full_access:
            raise exc.UnauthorizedAuthError(
                "666af198", f"User {user_id} has no access to CaseType {case_type_id}"
            )

        return access_data_collections, data_collection_col_access

    def _validate_case_access_args(
        self,
        right: enum.CaseRight,
        on_invalid_case_id: str,
        filter_content: bool,
        calculate_case_date: bool,
    ) -> None:
        """Validate case-content access and filtering arguments.

        Args:
            right: Required READ_CASE or WRITE_CASE right.
            on_invalid_case_id: Requested-case failure behavior.
            filter_content: Whether inaccessible content is removed.
            calculate_case_date: Whether a derived case date is requested.

        Raises:
            ValueError: If the right or failure mode is unsupported, or case-date
                calculation is requested without content filtering.
        """
        if right not in enum.CaseRightSet.CASE_CONTENT.value:
            raise ValueError(f"Invalid case abac right: {right.value}")
        if on_invalid_case_id not in {"raise", "ignore"}:
            raise ValueError(f"Invalid on_invalid_case_id: {on_invalid_case_id}")
        if not filter_content and calculate_case_date:
            raise ValueError("Cannot calculate case date when filter_content is False")

    def _retrieve_case_data_collections_map(
        self,
        uow: BaseUnitOfWork,
        user_id: UUID,
        case_ids: Iterable[UUID] | None = None,
        data_collection_ids: Iterable[UUID] | None = None,
    ) -> dict[UUID, set[UUID]]:
        """Retrieve data collection IDs grouped by case ID.

        Args:
            uow: Active repository unit of work.
            user_id: User identifier used for repository access.
            case_ids: Optional case IDs restricting association rows.
            data_collection_ids: Optional collection IDs restricting rows.

        Returns:
            Data collection IDs grouped by case ID.
        """
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
        """Retrieve data collection IDs grouped by case-set ID.

        Args:
            uow: Active repository unit of work.
            user_id: User identifier used for repository access.
            case_set_ids: Optional case-set IDs restricting association rows.
            data_collection_ids: Optional collection IDs restricting rows.

        Returns:
            Data collection IDs grouped by case-set ID.
        """
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
        """Retrieve case-set IDs grouped by case ID.

        Args:
            uow: Active repository unit of work.
            user_id: User identifier used for repository access.
            case_ids: Optional case IDs restricting membership rows.
            case_set_ids: Optional case-set IDs restricting membership rows.

        Returns:
            Case-set IDs grouped by case ID.
        """
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
        """Retrieve linked identifiers grouped by the first endpoint.

        The caller owns ``uow``. When both endpoint restrictions are present, both
        must match the same association row.

        Args:
            uow: Active repository unit of work.
            user_id: Optional user identifier used for repository access.
            association_class: Association model to query.
            link_field_name1: First endpoint field name and result key.
            link_field_name2: Second endpoint field name and grouped result value.
            obj_ids1: Optional accepted first-endpoint IDs.
            obj_ids2: Optional accepted second-endpoint IDs.

        Returns:
            Second-endpoint IDs grouped by first-endpoint ID.
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

    def _retrieve_seq_column_data(
        self, uow: BaseUnitOfWork, user: model.User, seq_col_id: UUID
    ) -> tuple[model.Col, model.RefCol]:
        """Retrieve and validate genetic-sequence column metadata.

        Args:
            uow: Active repository unit of work.
            user: User performing repository reads.
            seq_col_id: Sequence column identifier.

        Returns:
            The column and its genetic-sequence reference metadata.

        Raises:
            InvalidArgumentsError: If the reference column is not a genetic-sequence
                column.
        """
        repository = self.repository
        seq_col: model.Col = repository.crud(
            uow,
            user.id,
            model.Col,
            CrudOperation.READ_ONE,
            obj_ids=seq_col_id,
        )
        ref_seq_col: model.RefCol = repository.crud(
            uow,
            user.id,
            model.RefCol,
            CrudOperation.READ_ONE,
            obj_ids=seq_col.ref_col_id,
        )
        if ref_seq_col.col_type != enum.ColType.GENETIC_SEQUENCE:
            raise exc.InvalidArgumentsError(
                "3983f776",
                f"Col {seq_col.id} is not of type {enum.ColType.GENETIC_SEQUENCE.value}",
            )
        return seq_col, ref_seq_col

    def _verify_case_set_member_case_type(
        self, user: model.User, case_set_members: list[model.CaseSetMember]
    ) -> None:
        """Verify that each case-set member links matching case types.

        This helper owns a repository unit of work. It does not persist or mutate the
        supplied membership models.

        Args:
            user: User performing repository reads.
            case_set_members: Membership records to verify.

        Raises:
            InvalidArgumentsError: If any member links a case and case set with
                different case types.
        """
        with self.repository.uow() as uow:
            case_set_ids = {x.case_set_id for x in case_set_members}
            case_ids = {x.case_id for x in case_set_members}
            case_sets_: list[model.CaseSet] = self.repository.crud(
                uow,
                user.id if user else None,
                model.CaseSet,
                CrudOperation.READ_SOME,
                obj_ids=list(case_set_ids),
            )
            case_sets = {x.id: x for x in case_sets_}
            cases_: list[model.Case] = self.repository.crud(
                uow,
                user.id if user else None,
                model.Case,
                CrudOperation.READ_SOME,
                obj_ids=list(case_ids),
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
                "3e11edd5",
                f"Case set members invalid, case set and case must have the same CaseType: {invalid_case_set_member_ids_str}",
            )

    def retrieve_is_own_cases(
        self,
        cmd: command.RetrieveIsOwnCasesCommand,
    ) -> dict[UUID, bool]:
        """Map accessible requested cases to private-collection ownership.

        Args:
            cmd: Case type and case identifiers to evaluate.

        Returns:
            Ownership flags keyed by accessible case identifier.

        Raises:
            UnauthorizedAuthError: If the user cannot read the requested case type.
        """
        return case_service_retrieve_is_own_cases(self, cmd)

    # CRUD method implementations
    def crud_case(
        self, cmd: command.CaseCrudCommand
    ) -> list[model.Case] | model.Case | list[UUID] | UUID | list[bool] | bool | None:
        """Handle case CRUD under case-data ABAC in a repository unit of work.

        Delete operations include configured dependent associations. Restricted
        users cannot delete all cases and must have REMOVE_CASE access through every
        collection associated with each requested case.

        Args:
            cmd: Case CRUD operation, inputs, and user context.

        Returns:
            Cases, identifiers, existence flags, or ``None`` for the operation.

        Raises:
            UnauthorizedAuthError: If deletion is too broad or remove access is
                missing for a requested case.
            AssertionError: If an unsupported restricted-user operation is routed to
                the deletion handler.
        """
        return case_service_crud_case(self, cmd)

    def crud_case_data_collection_link(
        self, cmd: command.CaseDataCollectionLinkCrudCommand
    ) -> (
        list[model.CaseDataCollectionLink]
        | model.CaseDataCollectionLink
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-collection link CRUD under case-data ABAC.

        The delegated handler owns a repository unit of work and applies cascade and
        restricted-user operation rules.

        Args:
            cmd: Link CRUD operation, inputs, and user context.

        Returns:
            Links, identifiers, existence flags, or ``None`` for the operation.

        Raises:
            UnauthorizedAuthError: If a restricted user requests an unsupported
                bulk or mutation operation.
        """
        return case_service_crud_case_data_collection_link(self, cmd)

    def crud_case_identifier(
        self: BaseCaseService, cmd: command.CaseIdentifierCrudCommand
    ) -> (
        list[model.CaseIdentifier]
        | model.CaseIdentifier
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-identifier CRUD under case-data ABAC.

        The delegated handler owns a repository unit of work and applies cascade and
        restricted-user operation rules.

        Args:
            cmd: Identifier CRUD operation, inputs, and user context.

        Returns:
            Identifiers, UUIDs, existence flags, or ``None`` for the operation.

        Raises:
            UnauthorizedAuthError: If a restricted user requests an unsupported
                bulk or mutation operation.
        """
        return case_service_crud_case_identifier(self, cmd)

    def crud_case_set_category(
        self, cmd: command.CaseSetCategoryCrudCommand
    ) -> (
        list[model.CaseSetCategory]
        | model.CaseSetCategory
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-set-category CRUD in a repository unit of work.

        Args:
            cmd: Category CRUD operation, inputs, and user context.

        Returns:
            Categories, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_case_set_category(self, cmd)

    def crud_case_set(
        self, cmd: command.CaseSetCrudCommand
    ) -> (
        list[model.CaseSet]
        | model.CaseSet
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-set CRUD under case-data ABAC.

        Delete operations include dependent collection links and memberships.
        Restricted users cannot delete all sets and must have REMOVE_CASE_SET access
        through every collection associated with each requested set.

        Args:
            cmd: Case-set CRUD operation, inputs, and user context.

        Returns:
            Case sets, identifiers, existence flags, or ``None`` for the operation.

        Raises:
            UnauthorizedAuthError: If deletion is too broad or remove access is
                missing for a requested case set.
            AssertionError: If an unsupported restricted-user operation is routed to
                the deletion handler.
        """
        return case_service_crud_case_set(self, cmd)

    def crud_case_set_data_collection_link(
        self, cmd: command.CaseSetDataCollectionLinkCrudCommand
    ) -> (
        list[model.CaseSetDataCollectionLink]
        | model.CaseSetDataCollectionLink
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-set-collection link CRUD under case-data ABAC.

        The delegated handler owns a repository unit of work and applies cascade and
        restricted-user operation rules.

        Args:
            cmd: Link CRUD operation, inputs, and user context.

        Returns:
            Links, identifiers, existence flags, or ``None`` for the operation.

        Raises:
            UnauthorizedAuthError: If a restricted user requests an unsupported
                bulk or mutation operation.
        """
        return case_service_crud_case_set_data_collection_link(self, cmd)

    def crud_case_set_member(
        self, cmd: command.CaseSetMemberCrudCommand
    ) -> (
        list[model.CaseSetMember]
        | model.CaseSetMember
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-set membership CRUD under case-data ABAC.

        The delegated handler owns a repository unit of work. Writes by an
        unrestricted user verify that each case and case set share a case type;
        restricted-user updates and bulk deletes are rejected.

        Args:
            cmd: Membership CRUD operation, inputs, and user context.

        Returns:
            Memberships, identifiers, existence flags, or ``None`` for the operation.

        Raises:
            InvalidArgumentsError: If a member links different case types.
            UnauthorizedAuthError: If a restricted user updates or bulk deletes.
        """
        return case_service_crud_case_set_member(self, cmd)

    def crud_case_set_status(
        self, cmd: command.CaseSetStatusCrudCommand
    ) -> (
        list[model.CaseSetStatus]
        | model.CaseSetStatus
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-set-status CRUD in a repository unit of work.

        Args:
            cmd: Status CRUD operation, inputs, and user context.

        Returns:
            Statuses, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_case_set_status(self, cmd)

    def crud_col(
        self, cmd: command.ColCrudCommand
    ) -> list[model.Col] | model.Col | list[UUID] | UUID | list[bool] | bool | None:
        """Handle case-type-column CRUD under reference-data ABAC.

        Writes by reference-data administrators validate that each column, dimension,
        reference column, and reference dimension are compatible. The delegated
        handler owns a repository unit of work.

        Args:
            cmd: Column CRUD operation, inputs, and user context.

        Returns:
            Columns, identifiers, existence flags, or ``None`` for the operation.

        Raises:
            InvalidArgumentsError: If column and dimension metadata are incompatible.
        """
        return case_service_crud_col(self, cmd)

    def crud_col_set(
        self, cmd: command.ColSetCrudCommand
    ) -> (
        list[model.ColSet] | model.ColSet | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle column-set CRUD under reference-data ABAC.

        Args:
            cmd: Column-set CRUD operation, inputs, and user context.

        Returns:
            Column sets, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_col_set(self, cmd)

    def crud_col_set_member(
        self, cmd: command.ColSetMemberCrudCommand
    ) -> (
        list[model.ColSetMember]
        | model.ColSetMember
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle column-set membership CRUD under reference-data ABAC.

        Args:
            cmd: Membership CRUD operation, inputs, and user context.

        Returns:
            Memberships, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_col_set_member(self, cmd)

    def crud_case_type(
        self, cmd: command.CaseTypeCrudCommand
    ) -> (
        list[model.CaseType]
        | model.CaseType
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-type CRUD under reference-data ABAC.

        The delegated handler owns a repository unit of work. Every non-read
        operation clears the complete-case-type cache after repository handling.

        Args:
            cmd: Case-type CRUD operation, inputs, and user context.

        Returns:
            Case types, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_case_type(self, cmd)

    def crud_case_type_set_category(
        self, cmd: command.CaseTypeSetCategoryCrudCommand
    ) -> (
        list[model.CaseTypeSetCategory]
        | model.CaseTypeSetCategory
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-type-set-category CRUD in a repository unit of work.

        Args:
            cmd: Category CRUD operation, inputs, and user context.

        Returns:
            Categories, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_case_type_set_category(self, cmd)

    def crud_case_type_set(
        self, cmd: command.CaseTypeSetCrudCommand
    ) -> (
        list[model.CaseTypeSet]
        | model.CaseTypeSet
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-type-set CRUD under reference-data ABAC.

        Args:
            cmd: Case-type-set CRUD operation, inputs, and user context.

        Returns:
            Case-type sets, IDs, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_case_type_set(self, cmd)

    def crud_case_type_set_member(
        self, cmd: command.CaseTypeSetMemberCrudCommand
    ) -> (
        list[model.CaseTypeSetMember]
        | model.CaseTypeSetMember
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle case-type-set membership CRUD under reference-data ABAC.

        Args:
            cmd: Membership CRUD operation, inputs, and user context.

        Returns:
            Memberships, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_case_type_set_member(self, cmd)

    def crud_dim(
        self, cmd: command.DimCrudCommand
    ) -> list[model.Dim] | model.Dim | list[UUID] | UUID | list[bool] | bool | None:
        """Handle case-type-dimension CRUD under reference-data ABAC.

        The delegated handler owns a repository unit of work and validates case-date
        and reference-dimension invariants for writes.

        Args:
            cmd: Dimension CRUD operation, inputs, and user context.

        Returns:
            Dimensions, identifiers, existence flags, or ``None`` for the operation.

        Raises:
            InvalidArgumentsError: If case-date or reference-dimension metadata is
                invalid.
        """
        return case_service_crud_dim(self, cmd)

    def crud_ref_col(
        self, cmd: command.RefColCrudCommand
    ) -> (
        list[model.RefCol] | model.RefCol | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle reference-column CRUD with metadata validation.

        Writes validate dimension, concept or region set, unit, and column-type
        compatibility in repository units of work.

        Args:
            cmd: Reference-column CRUD operation, inputs, and user context.

        Returns:
            Reference columns, IDs, existence flags, or ``None`` for the operation.

        Raises:
            InvalidArgumentsError: If linked metadata or the operation is invalid.
        """
        return case_service_crud_ref_col(self, cmd)

    def crud_ref_dim(
        self, cmd: command.RefDimCrudCommand
    ) -> (
        list[model.RefDim] | model.RefDim | list[UUID] | UUID | list[bool] | bool | None
    ):
        """Handle reference-dimension CRUD in a repository unit of work.

        Args:
            cmd: Reference-dimension CRUD operation, inputs, and user context.

        Returns:
            Reference dimensions, IDs, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_ref_dim(self, cmd)

    def crud_genetic_distance_protocol(
        self, cmd: command.GeneticDistanceProtocolCrudCommand
    ) -> (
        list[model.GeneticDistanceProtocol]
        | model.GeneticDistanceProtocol
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle genetic-distance-protocol CRUD in a repository unit of work.

        Args:
            cmd: Protocol CRUD operation, inputs, and user context.

        Returns:
            Protocols, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_genetic_distance_protocol(self, cmd)

    def crud_tree_algorithm_class(
        self, cmd: command.TreeAlgorithmClassCrudCommand
    ) -> (
        list[model.TreeAlgorithmClass]
        | model.TreeAlgorithmClass
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle tree-algorithm-class CRUD in a repository unit of work.

        Args:
            cmd: Algorithm-class CRUD operation, inputs, and user context.

        Returns:
            Algorithm classes, IDs, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_tree_algorithm_class(self, cmd)

    def crud_tree_algorithm(
        self, cmd: command.TreeAlgorithmCrudCommand
    ) -> (
        list[model.TreeAlgorithm]
        | model.TreeAlgorithm
        | list[UUID]
        | UUID
        | list[bool]
        | bool
        | None
    ):
        """Handle tree-algorithm CRUD in a repository unit of work.

        Args:
            cmd: Tree-algorithm CRUD operation, inputs, and user context.

        Returns:
            Algorithms, identifiers, existence flags, or ``None`` for the operation.
        """
        return case_service_crud_tree_algorithm(self, cmd)

    @staticmethod
    def _compose_id_filter(*key_and_ids: tuple[str, set[UUID]]) -> Filter:
        """Compose an intersection filter from field and identifier pairs.

        Args:
            *key_and_ids: Field names paired with accepted identifier sets.

        Returns:
            A UUID-set filter for one pair, or an AND-composite for multiple pairs.
        """
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
