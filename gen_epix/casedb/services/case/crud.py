from typing import Any, Type
from uuid import UUID

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.commondb.util import map_paired_elements
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation, CrudOperationSet
from gen_epix.filter import CompositeFilter, Filter, LogicalOperator


def crud(
    self: BaseCaseService, cmd: command.CrudCommand
) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
    """
    Override the base crud method to apply ABAC restrictions and cascade delete
    where necessary
    """
    # Handle no ABAC restrictions
    if any(isinstance(cmd, x) for x in DomainBaseCaseService.NO_ABAC_COMMAND_CLASSES):
        # No ABAC restrictions
        return super(DomainBaseCaseService, self).crud(cmd)  # type: ignore[return-value]

    # Start unit of work and execute all within this scope
    with self.repository.uow() as uow:
        # Metadata commands
        if any(
            isinstance(cmd, x)
            for x in DomainBaseCaseService.ABAC_METADATA_COMMAND_CLASSES
        ):
            return _crud_metadata(self, uow, cmd)  # type: ignore[no-any-return]
        # Data commands
        elif any(
            isinstance(cmd, x) for x in DomainBaseCaseService.ABAC_DATA_COMMAND_CLASSES
        ):
            return _crud_data(self, uow, cmd)
        else:
            raise AssertionError(
                f"Unexpected command {cmd.__class__.__name__} with operation {cmd.operation.value}"
            )


def _crud_metadata(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CrudCommand,
) -> Any:
    """Logic for handling metadata commands"""
    # Metadata admin or above: no @ABAC applied
    assert cmd.user
    if cmd.user.roles.intersection(enum.RoleSet.GE_REFDATA_ADMIN.value):
        # Metadata admin and above have access to all metadata: no ABAC
        # applied, only RBAC
        return _crud_metadata_by_admin(self, uow, cmd)
    return _crud_metadata_by_non_admin(self, uow, cmd)


def _crud_metadata_by_admin(
    self: BaseCaseService, uow: BaseUnitOfWork, cmd: command.CrudCommand
) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
    """Metadata admin command handling, no ABAC applied"""
    _crud_cascade_delete(self, uow, cmd)
    return super(DomainBaseCaseService, self).crud(cmd)  # type:ignore[return-value]


def _crud_metadata_by_non_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CrudCommand,
) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
    """Metadata user command handling, ABAC applied"""
    # @ABAC: get case abac
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)

    # Special case: no policy, allows for internal commands to retrieve all
    if not case_abac:
        # No policy: allows for internal commands to retrieve all
        return super(DomainBaseCaseService, self).crud(cmd)  # type:ignore[return-value]

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
        access_filter = self._compose_id_filter(("id", valid_case_type_ids))
        # No cascade delete to force conscious decision to delete from other models
        return _crud_with_access_filter(self, uow, cmd, access_filter)

    elif isinstance(cmd, command.CaseTypeSetMemberCrudCommand):
        valid_case_type_ids = case_abac.get_case_types_with_any_rights()
        access_filter = self._compose_id_filter(("case_type_id", valid_case_type_ids))
        return _crud_with_access_filter(self, uow, cmd, access_filter)

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
        access_filter = self._compose_id_filter(("id", valid_case_type_set_ids))
        # No cascade delete to force conscious decision to delete from other models
        return _crud_with_access_filter(self, uow, cmd, access_filter)

    elif isinstance(cmd, command.CaseTypeColCrudCommand):
        valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
        access_filter = self._compose_id_filter(("id", valid_case_type_col_ids))
        # No cascade delete to force conscious decision to delete from other models
        return _crud_with_access_filter(self, uow, cmd, access_filter)

    elif isinstance(cmd, command.CaseTypeColSetMemberCrudCommand):
        valid_case_type_col_ids = case_abac.get_case_type_cols_with_any_rights()
        access_filter = self._compose_id_filter(
            ("case_type_col_id", valid_case_type_col_ids)
        )
        return _crud_with_access_filter(self, uow, cmd, access_filter)

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
        access_filter = self._compose_id_filter(("id", valid_case_type_col_set_ids))
        # No cascade delete to force conscious decision to delete from other models
        return _crud_with_access_filter(self, uow, cmd, access_filter)

    raise AssertionError("Unexpected operation")


def _crud_data(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CrudCommand,
) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
    """Logic for handling data commands"""
    assert cmd.user
    # App admin or above: no @ABAC applied
    if cmd.user.roles.intersection(enum.RoleSet.GE_APP_ADMIN.value):
        return _crud_data_by_admin(self, uow, cmd)
    return _crud_data_by_non_admin(self, uow, cmd)


def _crud_data_by_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CrudCommand,
) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
    """Data admin command handling, no ABAC applied"""
    # Non-ABAC restrictions not enforced anywhere else
    is_create = cmd.operation in CrudOperationSet.CREATE.value
    is_update = cmd.operation in CrudOperationSet.UPDATE.value
    if (is_create or is_update) and isinstance(cmd, command.CaseSetMemberCrudCommand):
        # Verify that the case set and case have the same case type
        self._verify_case_set_member_case_type(
            cmd.user, cmd.get_objs()  # type:ignore[arg-type]
        )

    # Any other operation
    _crud_cascade_delete(self, uow, cmd)
    return super(DomainBaseCaseService, self).crud(cmd)  # type:ignore[return-value]


def _crud_data_by_non_admin(
    self: BaseCaseService,
    uow: BaseUnitOfWork,
    cmd: command.CrudCommand,
) -> list[model.Model] | model.Model | list[UUID] | UUID | list[bool] | bool | None:
    """Data user command handling, ABAC applied"""
    # @ABAC: get case abac
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)

    # Special case: no policy, allows for internal commands to retrieve all
    if case_abac is None:
        # No policy: allows for internal commands to retrieve all
        return super(DomainBaseCaseService, self).crud(cmd)  # type:ignore[return-value]

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
            return super(DomainBaseCaseService, self).crud(cmd)  # type: ignore[return-value]
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
            case_set_data_collection_map = self._retrieve_case_set_data_collections_map(
                uow,
                cmd.user.id,
                obj_ids1=case_set_ids,
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
            _crud_cascade_delete(self, uow, cmd)
            return super(DomainBaseCaseService, self).crud(
                cmd
            )  # type:ignore[return-value]
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
            case_data_collection_map = self._retrieve_case_data_collections_map(
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
            _crud_cascade_delete(self, uow, cmd)
            return super(DomainBaseCaseService, self).crud(
                cmd
            )  # type:ignore[return-value]
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
            on_invalid_case_id=("ignore" if is_read_all or is_delete_all else "raise"),
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
            return super(DomainBaseCaseService, self).crud(
                cmd
            )  # type:ignore[return-value]
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
            raise AssertionError("Update not allowed for case data collection links")
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
            return super(DomainBaseCaseService, self).crud(
                cmd
            )  # type:ignore[return-value]
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
            case_set_data_collection_links = cmd.get_objs()  # type:ignore[assignment]
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
            return super(DomainBaseCaseService, self).crud(
                cmd
            )  # type:ignore[return-value]
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
    self: BaseCaseService, uow: BaseUnitOfWork, cmd: command.CrudCommand
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
    obj_ids: set[UUID] | None = cmd.get_obj_ids(as_set=True)  # type:ignore[assignment]
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
        link_obj_ids = [get_obj_id(x) for x in link_objs if get_link_id(x) in obj_ids]
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
    self: BaseCaseService,
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
        _crud_cascade_delete(self, uow, cmd)
    retval = super(DomainBaseCaseService, self).crud(cmd)
    cmd.access_filter = orig_access_filter
    return retval  # type:ignore[return-value]
