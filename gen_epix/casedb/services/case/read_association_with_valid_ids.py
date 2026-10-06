"""Read association models with endpoint constraints and selectable return shapes."""

from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter import CompositeFilter, Filter, LogicalOperator, UuidSetFilter

_UNEXPECTED_CASE = "Unexpected case"


def _validate_read_association_args(
    return_type: str, match_all1: bool, match_all2: bool
) -> tuple[bool, bool]:
    # Parse arguments
    if return_type not in {"objects", "ids1", "ids2", "id_map12", "id_map21"}:
        raise ValueError(f"Invalid return_type: {return_type}")
    if match_all1 and match_all2:
        raise ValueError("match_all1 and match_all2 cannot both be True")
    id_map12 = return_type == "id_map12"
    id_map21 = return_type == "id_map21"
    if id_map12 and match_all1:
        raise ValueError("match_all1 must be False if id_map12 is True")
    if id_map21 and match_all2:
        raise ValueError("match_all2 must be False if id_map21 is True")
    if return_type == "ids1" and match_all1:
        raise ValueError("match_all1 must be False if return_type is ids1")
    if return_type == "ids2" and match_all2:
        raise ValueError("match_all2 must be False if return_type is ids2")
    return id_map12, id_map21


def _empty_association_result(
    return_type: str,
) -> list[model.Model] | list[UUID] | dict[UUID, set[UUID]]:
    if return_type in {"id_map12", "id_map21"}:
        return {}
    return []


def _create_association_filter(
    field_name1: str,
    field_name2: str,
    valid_ids1: set[UUID] | frozenset[UUID] | None,
    valid_ids2: set[UUID] | frozenset[UUID] | None,
    match_all1: bool,
    match_all2: bool,
    return_type: str,
) -> tuple[
    Filter | None,
    list[model.Model] | list[UUID] | dict[UUID, set[UUID]] | None,
]:
    # Create filter
    ids1 = frozenset(valid_ids1) if valid_ids1 is not None else None
    ids2 = frozenset(valid_ids2) if valid_ids2 is not None else None
    if ids1 is not None:
        if not ids1:
            # Empty set of valid values -> no matches
            return None, _empty_association_result(return_type)
        if ids2 is not None:
            if not ids2:
                # Empty set of valid values -> no matches
                return None, _empty_association_result(return_type)
            return (
                CompositeFilter(
                    filters=[
                        UuidSetFilter(key=field_name1, members=ids1),
                        UuidSetFilter(key=field_name2, members=ids2),
                    ],
                    operator=LogicalOperator.AND,
                ),
                None,
            )
        if match_all2:
            raise ValueError("match_all2 must be False if valid_ids2 is None")
        return UuidSetFilter(key=field_name1, members=ids1), None
    if ids2 is not None:
        if not ids2:
            # Empty set of valid values -> no matches
            return None, _empty_association_result(return_type)
        if match_all1:
            raise ValueError("match_all1 must be False if valid_ids1 is None")
        return UuidSetFilter(key=field_name2, members=ids2), None
    if match_all1 or match_all2:
        raise ValueError(
            "match_all1 and match_all2 must be False if valid_ids1 and valid_ids2 are None"
        )
    return None, None


def _group_association_ids(
    key_ids: list[UUID], value_ids: list[UUID]
) -> dict[UUID, set[UUID]]:
    # Create dict[id1, set[id2]]
    grouped_ids: dict[UUID, set[UUID]] = {}
    for key_id, value_id in zip(key_ids, value_ids):
        grouped_ids.setdefault(key_id, set()).add(value_id)
    return grouped_ids


def _get_mapped_association_result(
    objs: list[model.Model],
    endpoint_ids: list[UUID],
    id_map: dict[UUID, set[UUID]],
    return_type: str,
    id_return_type: str,
) -> list[model.Model] | list[UUID]:
    if return_type == "objects":
        return [
            obj for obj, endpoint_id in zip(objs, endpoint_ids) if endpoint_id in id_map
        ]
    if return_type == id_return_type:
        return list(id_map)
    raise AssertionError(_UNEXPECTED_CASE)


def _get_directional_association_result(
    objs: list[model.Model],
    key_ids: list[UUID],
    value_ids: list[UUID],
    return_type: str,
    map_return_type: str,
    ids_return_type: str,
    match_all: bool,
    valid_ids: set[UUID] | frozenset[UUID] | None,
) -> list[model.Model] | list[UUID] | dict[UUID, set[UUID]]:
    """Build one directional ID map, optionally requiring every valid link."""
    id_map = _group_association_ids(key_ids, value_ids)
    if match_all:
        expected_count = len(valid_ids or ())
        id_map = {
            key_id: linked_ids
            for key_id, linked_ids in id_map.items()
            if len(linked_ids) == expected_count
        }
        if return_type == map_return_type:
            return id_map
        return _get_mapped_association_result(
            objs, key_ids, id_map, return_type, ids_return_type
        )
    if return_type == map_return_type:
        return id_map
    raise AssertionError(_UNEXPECTED_CASE)


def _format_association_result(
    objs: list[model.Model],
    ids1: list[UUID],
    ids2: list[UUID],
    return_type: str,
    id_map12: bool,
    id_map21: bool,
    match_all1: bool,
    match_all2: bool,
    valid_ids1: set[UUID] | frozenset[UUID] | None,
    valid_ids2: set[UUID] | frozenset[UUID] | None,
) -> list[model.Model] | list[UUID] | dict[UUID, set[UUID]]:
    """Shape association objects and endpoint IDs into the requested result."""
    if id_map12 or match_all2:
        return _get_directional_association_result(
            objs,
            ids1,
            ids2,
            return_type,
            "id_map12",
            "ids1",
            match_all2,
            valid_ids2,
        )
    if id_map21 or match_all1:
        return _get_directional_association_result(
            objs,
            ids2,
            ids1,
            return_type,
            "id_map21",
            "ids2",
            match_all1,
            valid_ids1,
        )
    if return_type == "objects":
        return objs
    if return_type == "ids1":
        return ids1
    if return_type == "ids2":
        return ids2
    raise AssertionError(f"Unexpected return_type: {return_type}")


def case_service_read_association_with_valid_ids(
    self: BaseCaseService,
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

    Matching can require each returned endpoint to be linked to all valid identifiers
    on the opposite side. Empty valid-ID sets return an empty result without querying.

    Args:
        self: Case service used for CRUD handling.
        command_class: Association CRUD command class to instantiate.
        field_name1: Model field for the first endpoint.
        field_name2: Model field for the second endpoint.
        valid_ids1: Optional valid identifiers for the first endpoint.
        valid_ids2: Optional valid identifiers for the second endpoint.
        match_all1: Require returned second endpoints to link to every valid first ID.
        match_all2: Require returned first endpoints to link to every valid second ID.
        return_type: Return objects, either endpoint IDs, or a directional ID map.
        uow: Existing unit of work, or ``None`` to open one.
        user: Optional user attached to the generated read command.

    Returns:
        Association objects, endpoint IDs, or sets of linked IDs keyed by endpoint.

    Raises:
        ValueError: If ``return_type`` or match-all argument combinations are invalid.
        AssertionError: If a validated return mode reaches an unexpected branch.
    """
    # TODO: this can be a generic service/repository method (ids should be Hashable instead of UUID)
    id_map12, id_map21 = _validate_read_association_args(
        return_type, match_all1, match_all2
    )
    filter, empty_result = _create_association_filter(
        field_name1,
        field_name2,
        valid_ids1,
        valid_ids2,
        match_all1,
        match_all2,
        return_type,
    )
    if empty_result is not None:
        return empty_result
    # Query repository
    cmd = command_class(
        user=user, operation=CrudOperation.READ_ALL, query_filter=filter
    )
    objs: list[model.Model]
    if uow:
        objs = self.crud_repository(uow, cmd)  # type: ignore[assignment]
    else:
        with self.repository.uow() as uow:
            objs = self.crud_repository(uow, cmd)  # type: ignore[assignment]
    ids1 = [getattr(x, field_name1) for x in objs]
    ids2 = [getattr(x, field_name2) for x in objs]
    return _format_association_result(
        objs,
        ids1,
        ids2,
        return_type,
        id_map12,
        id_map21,
        match_all1,
        match_all2,
        valid_ids1,
        valid_ids2,
    )
