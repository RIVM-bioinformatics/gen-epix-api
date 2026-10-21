"""Focused tests for association reads constrained by endpoint identifiers."""

# Pytest injects fixtures through parameters with the fixture's name.
# pylint: disable=redefined-outer-name

from test.util.mock_compat import MagicMock, Mock
from types import SimpleNamespace
from uuid import UUID

import pytest

from gen_epix.casedb.services.case.read_association_with_valid_ids import (
    case_service_read_association_with_valid_ids,
)
from gen_epix.fastapp import CrudOperation

ID_A = UUID(int=1)
ID_B = UUID(int=2)
ID_X = UUID(int=3)
ID_Y = UUID(int=4)


# pylint: disable=too-few-public-methods
class ReadAssociationCommand:
    """Capture command values passed to the CRUD service."""

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


def _association(id1: UUID, id2: UUID) -> SimpleNamespace:
    return SimpleNamespace(endpoint_id1=id1, endpoint_id2=id2)


def _read(rows: list[SimpleNamespace], **kwargs: object) -> tuple[Mock, object]:
    service = Mock()
    service.crud_repository.return_value = rows
    result = case_service_read_association_with_valid_ids(
        service,
        ReadAssociationCommand,  # type: ignore[arg-type]
        "endpoint_id1",
        "endpoint_id2",
        uow=object(),
        **kwargs,
    )
    return service, result


@pytest.fixture
def associations() -> list[SimpleNamespace]:
    """Provide repeated and distinct endpoint pairs for association reads."""
    return [
        _association(ID_A, ID_X),
        _association(ID_A, ID_Y),
        _association(ID_B, ID_X),
        _association(ID_A, ID_X),
    ]


@pytest.mark.parametrize(
    ("return_type", "expected"),
    [
        ("objects", [0, 1, 2, 3]),
        ("ids1", [ID_A, ID_A, ID_B, ID_A]),
        ("ids2", [ID_X, ID_Y, ID_X, ID_X]),
        ("id_map12", {ID_A: {ID_X, ID_Y}, ID_B: {ID_X}}),
        ("id_map21", {ID_X: {ID_A, ID_B}, ID_Y: {ID_A}}),
    ],
)
def test_read_returns_requested_shape(
    associations: list[SimpleNamespace], return_type: str, expected: object
) -> None:
    """Return association objects, endpoint IDs, or directional maps as requested."""
    service, result = _read(associations, return_type=return_type)

    if return_type == "objects":
        assert result == associations
    else:
        assert result == expected
    command = service.crud_repository.call_args.args[1]
    assert command.kwargs["operation"] == CrudOperation.READ_ALL
    assert command.kwargs["query_filter"] is None


@pytest.mark.parametrize(
    ("return_type", "valid_ids1", "valid_ids2", "expected"),
    [
        ("objects", set(), None, []),
        ("ids1", set(), None, []),
        ("ids2", set(), None, []),
        ("id_map12", set(), None, {}),
        ("id_map21", set(), None, {}),
        ("objects", None, set(), []),
        ("id_map12", None, set(), {}),
    ],
)
def test_empty_valid_ids_return_empty_without_query(
    return_type: str,
    valid_ids1: set[UUID] | None,
    valid_ids2: set[UUID] | None,
    expected: object,
) -> None:
    """Return the correct empty shape without querying for an empty endpoint set."""
    service, result = _read(
        [], valid_ids1=valid_ids1, valid_ids2=valid_ids2, return_type=return_type
    )

    assert result == expected
    service.crud_repository.assert_not_called()


@pytest.mark.parametrize(
    ("valid_ids1", "valid_ids2", "matching", "nonmatching"),
    [
        ({ID_A}, {ID_Y}, (ID_A, ID_Y), (ID_A, ID_X)),
        ({ID_A}, None, (ID_A, ID_X), (ID_B, ID_X)),
        (None, {ID_Y}, (ID_A, ID_Y), (ID_A, ID_X)),
    ],
)
def test_valid_ids_create_endpoint_filter(
    associations: list[SimpleNamespace],
    valid_ids1: set[UUID] | None,
    valid_ids2: set[UUID] | None,
    matching: tuple[UUID, UUID],
    nonmatching: tuple[UUID, UUID],
) -> None:
    """Filter by whichever endpoint ID sets were provided."""
    service, _ = _read(associations, valid_ids1=valid_ids1, valid_ids2=valid_ids2)

    query_filter = service.crud_repository.call_args.args[1].kwargs["query_filter"]
    assert query_filter.match_row(
        {"endpoint_id1": matching[0], "endpoint_id2": matching[1]}
    )
    assert not query_filter.match_row(
        {"endpoint_id1": nonmatching[0], "endpoint_id2": nonmatching[1]}
    )


@pytest.mark.parametrize(
    ("return_type", "expected"),
    [
        ("id_map21", {ID_X: {ID_A, ID_B}}),
        ("ids2", [ID_X]),
        ("objects", [0, 2, 3]),
    ],
)
def test_match_all1_keeps_endpoints_linked_to_every_valid_id(
    associations: list[SimpleNamespace], return_type: str, expected: object
) -> None:
    """Keep second endpoints linked to every requested first endpoint."""
    _, result = _read(
        associations,
        valid_ids1={ID_A, ID_B},
        match_all1=True,
        return_type=return_type,
    )

    if return_type == "objects":
        assert result == [associations[index] for index in expected]  # type: ignore[arg-type]
    else:
        assert result == expected


@pytest.mark.parametrize(
    ("return_type", "expected"),
    [
        ("id_map12", {ID_A: {ID_X, ID_Y}}),
        ("ids1", [ID_A]),
        ("objects", [0, 1, 3]),
    ],
)
def test_match_all2_keeps_endpoints_linked_to_every_valid_id(
    associations: list[SimpleNamespace], return_type: str, expected: object
) -> None:
    """Keep first endpoints linked to every requested second endpoint."""
    _, result = _read(
        associations,
        valid_ids2={ID_X, ID_Y},
        match_all2=True,
        return_type=return_type,
    )

    if return_type == "objects":
        assert result == [associations[index] for index in expected]  # type: ignore[arg-type]
    else:
        assert result == expected


def test_read_opens_and_closes_unit_of_work_when_not_provided(
    associations: list[SimpleNamespace],
) -> None:
    """Manage a unit of work when the caller does not provide one."""
    service = MagicMock()
    service.crud_repository.return_value = associations
    unit_of_work = service.repository.uow.return_value
    unit_of_work.__enter__.return_value = object()
    unit_of_work.__exit__.return_value = False

    result = case_service_read_association_with_valid_ids(
        service,
        ReadAssociationCommand,  # type: ignore[arg-type]
        "endpoint_id1",
        "endpoint_id2",
    )

    assert result == associations
    service.repository.uow.assert_called_once_with()
    unit_of_work.__enter__.assert_called_once_with()
    unit_of_work.__exit__.assert_called_once()


@pytest.mark.parametrize(
    ("return_type", "kwargs"),
    [
        ("invalid", {}),
        ("objects", {"match_all1": True, "match_all2": True}),
        ("id_map12", {"match_all1": True}),
        ("id_map21", {"match_all2": True}),
        ("ids1", {"match_all1": True}),
        ("ids2", {"match_all2": True}),
        ("objects", {"match_all2": True}),
    ],
)
def test_invalid_return_and_match_options_raise(
    return_type: str, kwargs: dict[str, bool]
) -> None:
    """Reject unsupported return types and incompatible match options."""
    service = Mock()

    with pytest.raises(ValueError):
        case_service_read_association_with_valid_ids(
            service,
            ReadAssociationCommand,  # type: ignore[arg-type]
            "endpoint_id1",
            "endpoint_id2",
            return_type=return_type,
            uow=object(),
            **kwargs,
        )

    service.crud_repository.assert_not_called()
