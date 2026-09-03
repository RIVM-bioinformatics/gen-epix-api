"""Read association models with endpoint constraints and selectable return shapes."""

from uuid import UUID

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation
from gen_epix.filter import CompositeFilter, Filter, LogicalOperator, UuidSetFilter


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
    # Create filter
    filter: Filter | None
    if valid_ids1 is not None:
        if not isinstance(valid_ids1, frozenset):
            valid_ids1 = frozenset(valid_ids1)
        if not valid_ids1:
            # Empty set of valid values -> no matches
            if return_type in {"id_map12", "id_map21"}:
                return dict()
            return []
        if valid_ids2 is not None:
            if not valid_ids2:
                # Empty set of valid values -> no matches
                if return_type in {"id_map12", "id_map21"}:
                    return dict()
                return []
            if not isinstance(valid_ids2, frozenset):
                valid_ids2 = frozenset(valid_ids2)
            filter = CompositeFilter(
                filters=[
                    UuidSetFilter(key=field_name1, members=valid_ids1),
                    UuidSetFilter(key=field_name2, members=valid_ids2),
                ],
                operator=LogicalOperator.AND,
            )
        else:
            if match_all2:
                raise ValueError("match_all2 must be False if valid_ids2 is None")
            if not isinstance(valid_ids1, frozenset):
                valid_ids2 = frozenset(valid_ids2)
            filter = UuidSetFilter(key=field_name1, members=valid_ids1)
    elif valid_ids2 is not None:
        if not valid_ids2:
            # Empty set of valid values -> no matches
            if return_type in {"id_map12", "id_map21"}:
                return dict()
            return []
        if match_all1:
            raise ValueError("match_all1 must be False if valid_ids1 is None")
        if not isinstance(valid_ids2, frozenset):
            valid_ids2 = frozenset(valid_ids2)
        filter = UuidSetFilter(key=field_name2, members=valid_ids2)
    else:
        if match_all1 or match_all2:
            raise ValueError(
                "match_all1 and match_all2 must be False if valid_ids1 and valid_ids2 are None"
            )
        filter = None
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
    # Apply id_map12/id_map21 and match_all1/match_all2 if necessary
    if id_map12 or id_map21 or match_all1 or match_all2:
        id_map: dict[UUID, set[UUID]] = {}
        if id_map12 or match_all2:
            # Create dict[id1, set[id2]]
            for id1, id2 in zip(ids1, ids2):
                if id1 in id_map:
                    id_map[id1].add(id2)
                else:
                    id_map[id1] = {id2}
            if match_all2:
                # Keep only ids1 linked to all valid ids2
                id_map = {
                    x: y for x, y in id_map.items() if len(y) == len(valid_ids2)  # type: ignore[arg-type]
                }
                if id_map12:
                    return id_map
                elif return_type == "objects":
                    return [x for x, y in zip(objs, ids1) if y in id_map]
                elif return_type == "ids1":
                    return list(id_map.keys())
            elif id_map12:
                return id_map
            else:
                raise AssertionError("Unexpected case")
        elif id_map21 or match_all1:
            # Create dict[id2, set[id1]]
            for id1, id2 in zip(ids1, ids2):
                if id2 in id_map:
                    id_map[id2].add(id1)
                else:
                    id_map[id2] = {id1}
            if match_all1:
                # Keep only ids2 linked to all valid ids1
                id_map = {
                    x: y for x, y in id_map.items() if len(y) == len(valid_ids1)  # type: ignore[arg-type]
                }
                if id_map21:
                    return id_map
                elif return_type == "objects":
                    return [x for x, y in zip(objs, ids2) if y in id_map]
                elif return_type == "ids2":
                    return list(id_map.keys())
            elif id_map21:
                return id_map
            else:
                raise AssertionError("Unexpected case")
        else:
            raise AssertionError("Unexpected case")
    # Return objs or IDs for remaining cases
    if return_type == "objects":
        return objs
    if return_type == "ids1":
        return ids1
    if return_type == "ids2":
        return ids2
    raise AssertionError(f"Unexpected return_type: {return_type}")
