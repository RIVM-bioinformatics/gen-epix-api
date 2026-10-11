from contextlib import nullcontext
from datetime import datetime, timezone
from test.util.mock_compat import MagicMock, patch
from types import SimpleNamespace
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case import service as case_service_module
from gen_epix.casedb.services.case.service import CaseService
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.datetime_range import DatetimeRangeFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter


def _case(case_id=None, created_in_data_collection_id=None):
    return model.Case(
        id=case_id or uuid4(),
        case_type_id=uuid4(),
        created_in_data_collection_id=created_in_data_collection_id or uuid4(),
        content={},
    )


def _case_set(case_set_id=None, case_type_id=None, created_in_data_collection_id=None):
    return model.CaseSet(
        id=case_set_id or uuid4(),
        case_type_id=case_type_id or uuid4(),
        created_in_data_collection_id=created_in_data_collection_id or uuid4(),
        name="Example set",
        code="example-set",
        description="Example",
        case_set_category_id=uuid4(),
        case_set_status_id=uuid4(),
    )


def test_authorize_case_returns_collections_when_access_is_granted() -> None:
    created_collection_id = uuid4()
    linked_collection_id = uuid4()
    case = _case(created_in_data_collection_id=created_collection_id)

    result = CaseService._authorize_case(
        object.__new__(CaseService),
        case,
        True,
        uuid4(),
        {case.id: {linked_collection_id}},
        {created_collection_id},
    )

    assert result == frozenset({created_collection_id, linked_collection_id})


def test_authorize_case_returns_none_when_access_is_missing_and_not_raising() -> None:
    created_collection_id = uuid4()
    case = _case(created_in_data_collection_id=created_collection_id)

    result = CaseService._authorize_case(
        object.__new__(CaseService),
        case,
        False,
        uuid4(),
        {case.id: {uuid4()}},
        set(),
    )

    assert result is None


def test_authorize_case_raises_when_access_is_missing_and_requested() -> None:
    case = _case()

    with pytest.raises(exc.UnauthorizedAuthError):
        CaseService._authorize_case(
            object.__new__(CaseService),
            case,
            True,
            uuid4(),
            {},
            set(),
        )


def test_authorize_case_returns_none_when_case_has_no_id() -> None:
    case = _case(case_id=None)
    case.id = None

    result = CaseService._authorize_case(
        object.__new__(CaseService), case, True, uuid4(), {}, set()
    )

    assert result is None


def test_has_case_set_access_uses_creation_and_linked_collections() -> None:
    service = object.__new__(CaseService)
    case_type_id = uuid4()
    case_set_id = uuid4()
    created_collection_id = uuid4()
    linked_collection_id = uuid4()
    case_set = type(
        "CaseSetAccessTarget",
        (),
        {
            "id": case_set_id,
            "case_type_id": case_type_id,
            "created_in_data_collection_id": created_collection_id,
        },
    )()

    assert service._has_case_set_access(
        case_set,
        {case_set_id: {linked_collection_id}},
        {case_type_id: {created_collection_id}},
    )
    assert not service._has_case_set_access(case_set, {}, {})
    assert not service._has_case_set_access(
        case_set, {case_set_id: {linked_collection_id}}, {case_type_id: {uuid4()}}
    )


def test_validate_case_set_access_raises_only_when_requested_without_access() -> None:
    service = object.__new__(CaseService)
    user_id = uuid4()
    case_set = type(
        "CaseSetAccessTarget",
        (),
        {
            "id": uuid4(),
            "case_type_id": uuid4(),
            "created_in_data_collection_id": uuid4(),
        },
    )()

    assert not service._validate_case_set_access(case_set, user_id, False, {}, {})
    with pytest.raises(exc.UnauthorizedAuthError):
        service._validate_case_set_access(case_set, user_id, True, {}, {})


def test_filter_case_sets_by_type_filters_or_rejects_requested_mismatch() -> None:
    service = object.__new__(CaseService)
    case_type_id = uuid4()
    matching_set = type("CaseSetTarget", (), {"case_type_id": case_type_id})()
    other_set = type("CaseSetTarget", (), {"case_type_id": uuid4()})()

    assert service._filter_case_sets_by_same_case_type_id(
        [matching_set, other_set], None, case_type_id
    ) == [matching_set]
    with pytest.raises(exc.InvalidArgumentsError):
        service._filter_case_sets_by_same_case_type_id(
            [matching_set, other_set], [uuid4()], case_type_id
        )


def test_validate_case_right_accepts_content_right_and_rejects_other_right() -> None:
    service = object.__new__(CaseService)

    service.validate_case_right(enum.CaseRight.READ_CASE_SET)
    with pytest.raises(exc.InvalidArgumentsError):
        service.validate_case_right(enum.CaseRight.READ_CASE)


def test_filter_case_content_reuses_cached_columns_and_preserves_extra_access() -> None:
    service = object.__new__(CaseService)
    case = _case()
    allowed_col_id = uuid4()
    extra_col_id = uuid4()
    denied_col_id = uuid4()
    data_collection_id = uuid4()
    cache: dict[frozenset[object], set[object]] = {}
    access = {
        data_collection_id: type("Access", (), {"read_col_ids": {allowed_col_id}})()
    }

    service._filter_case_content(
        case,
        frozenset({data_collection_id}),
        access,
        {extra_col_id},
        enum.CaseRight.READ_CASE,
        uuid4(),
        cache,
    )
    case.content = {
        allowed_col_id: "allowed",
        extra_col_id: "extra",
        denied_col_id: "denied",
    }
    service._filter_case_content(
        case,
        frozenset({data_collection_id}),
        {},
        None,
        enum.CaseRight.READ_CASE,
        uuid4(),
        cache,
    )

    assert case.content == {allowed_col_id: "allowed", extra_col_id: "extra"}


def test_filter_case_content_rejects_zero_accessible_columns() -> None:
    service = object.__new__(CaseService)
    case = _case()

    with pytest.raises(AssertionError):
        service._filter_case_content(
            case,
            frozenset({uuid4()}),
            {},
            None,
            enum.CaseRight.READ_CASE,
            uuid4(),
            {},
        )


def test_retrieve_cases_by_ids_preserves_repo_results_and_validates_type() -> None:
    service = object.__new__(CaseService)
    case_type_id = uuid4()
    case = _case()
    case.case_type_id = case_type_id
    service._repository = MagicMock()
    service.repository.crud.return_value = [case]

    assert service._retrieve_cases_by_ids_or_case_type_filter(
        object(), uuid4(), case_type_id, [case.id]
    ) == ([case], False)

    case.case_type_id = uuid4()
    with pytest.raises(exc.InvalidArgumentsError):
        service._retrieve_cases_by_ids_or_case_type_filter(
            object(), uuid4(), case_type_id, [case.id]
        )


def test_retrieve_cases_by_type_applies_limit_and_date_filter() -> None:
    service = object.__new__(CaseService)
    case_type_id = uuid4()
    cases = [_case(), _case()]
    service._repository = MagicMock()
    service.repository.crud.return_value = cases

    result, is_limit_exceeded = service._retrieve_cases_by_ids_or_case_type_filter(
        object(), uuid4(), case_type_id, max_n_cases=1
    )

    assert result == cases[:1]
    assert is_limit_exceeded
    assert isinstance(
        service.repository.crud.call_args.kwargs["filter"], EqualsUuidFilter
    )


def test_retrieve_cases_rejects_ids_with_date_filter_and_excessive_ids() -> None:
    service = object.__new__(CaseService)
    service._repository = MagicMock()
    case_type_id = uuid4()

    with pytest.raises(exc.RequestLimitExceededAuthError):
        service._retrieve_cases_by_ids_or_case_type_filter(
            object(), uuid4(), case_type_id, [uuid4(), uuid4()], max_n_cases=1
        )
    with pytest.raises(exc.InvalidArgumentsError):
        service._retrieve_cases_by_ids_or_case_type_filter(
            object(),
            uuid4(),
            case_type_id,
            [uuid4()],
            DatetimeRangeFilter(key="timed_at", lower_bound=datetime.now(timezone.utc)),
        )


def test_retrieve_association_map_composes_filters_and_groups_results() -> None:
    service = object.__new__(CaseService)
    service._repository = MagicMock()
    left_id = uuid4()
    right_id = uuid4()
    service.repository.read_fields.return_value = [
        (left_id, right_id),
        (left_id, right_id),
    ]

    result = service._retrieve_association_map(
        object(), uuid4(), model.CaseDataCollectionLink, "case_id", "data_collection_id"
    )

    assert result == {left_id: {right_id}}
    assert service.repository.read_fields.call_args.kwargs["filter"] is None

    service._retrieve_association_map(
        object(),
        uuid4(),
        model.CaseDataCollectionLink,
        "case_id",
        "data_collection_id",
        frozenset({left_id}),
        frozenset({right_id}),
    )
    assert isinstance(
        service.repository.read_fields.call_args.kwargs["filter"], CompositeFilter
    )


def test_validate_case_access_args_rejects_invalid_right_and_incompatible_date() -> (
    None
):
    service = object.__new__(CaseService)

    service._validate_case_access_args(enum.CaseRight.READ_CASE, True, False)
    with pytest.raises(ValueError, match="Invalid case abac right"):
        service._validate_case_access_args(enum.CaseRight.READ_CASE_SET, True, False)
    with pytest.raises(ValueError, match="Cannot calculate case date"):
        service._validate_case_access_args(enum.CaseRight.READ_CASE, False, True)


@pytest.mark.parametrize(
    ("method_name", "handler_name"),
    [
        ("upload_cases", "case_service_upload_cases"),
        (
            "update_case_created_in_data_collection",
            "case_service_update_case_created_in_data_collection",
        ),
        ("create_case_set", "case_service_create_case_set"),
        ("create_file_for_read_set", "case_service_create_file_for_read_set_or_seq"),
        ("create_file_for_seq", "case_service_create_file_for_read_set_or_seq"),
        ("retrieve_case_stats", "case_service_retrieve_case_stats"),
        ("retrieve_cases_by_query", "case_service_retrieve_cases_by_query"),
        (
            "retrieve_case_cohort_links_by_case_type",
            "case_service_retrieve_case_cohort_links_by_case_type",
        ),
        ("retrieve_cases_by_id", "case_service_retrieve_cases_by_id"),
        ("retrieve_phylogenetic_tree", "case_service_retrieve_phylogenetic_tree"),
        (
            "retrieve_seq_distances_by_cases",
            "case_service_retrieve_seq_distances_by_cases",
        ),
        ("retrieve_similar_cases", "case_service_retrieve_similar_cases"),
        (
            "retrieve_genetic_sequence_fasta_by_case",
            "case_service_retrieve_genetic_sequence_fasta_by_case",
        ),
        ("retrieve_protocols", "case_service_retrieve_protocols"),
        ("retrieve_is_own_cases", "case_service_retrieve_is_own_cases"),
        ("crud_case", "case_service_crud_case"),
        (
            "crud_case_data_collection_link",
            "case_service_crud_case_data_collection_link",
        ),
        ("crud_case_identifier", "case_service_crud_case_identifier"),
        ("crud_case_set_category", "case_service_crud_case_set_category"),
        ("crud_case_set", "case_service_crud_case_set"),
        (
            "crud_case_set_data_collection_link",
            "case_service_crud_case_set_data_collection_link",
        ),
        ("crud_case_set_member", "case_service_crud_case_set_member"),
        ("crud_case_set_status", "case_service_crud_case_set_status"),
        ("crud_col", "case_service_crud_col"),
        ("crud_col_set", "case_service_crud_col_set"),
        ("crud_col_set_member", "case_service_crud_col_set_member"),
        ("crud_case_type", "case_service_crud_case_type"),
        ("crud_case_type_set_category", "case_service_crud_case_type_set_category"),
        ("crud_case_type_set", "case_service_crud_case_type_set"),
        ("crud_case_type_set_member", "case_service_crud_case_type_set_member"),
        ("crud_dim", "case_service_crud_dim"),
        ("crud_ref_col", "case_service_crud_ref_col"),
        ("crud_ref_dim", "case_service_crud_ref_dim"),
        (
            "crud_genetic_distance_protocol",
            "case_service_crud_genetic_distance_protocol",
        ),
        ("crud_tree_algorithm_class", "case_service_crud_tree_algorithm_class"),
        ("crud_tree_algorithm", "case_service_crud_tree_algorithm"),
    ],
)
def test_facade_methods_forward_service_and_command(
    monkeypatch: pytest.MonkeyPatch, method_name: str, handler_name: str
) -> None:
    service = object.__new__(CaseService)
    cmd = object()
    expected = object()
    handler = MagicMock(return_value=expected)
    monkeypatch.setattr(case_service_module, handler_name, handler)

    result = getattr(service, method_name)(cmd)

    assert result is expected
    handler.assert_called_once_with(service, cmd)


def test_compose_id_filter_builds_single_and_intersection_filters() -> None:
    first_ids = {uuid4()}
    second_ids = {uuid4()}

    single_filter = CaseService._compose_id_filter(("case_id", first_ids))
    intersection_filter = CaseService._compose_id_filter(
        ("case_id", first_ids), ("case_type_id", second_ids)
    )

    assert isinstance(single_filter, UuidSetFilter)
    assert single_filter.members == first_ids
    assert isinstance(intersection_filter, CompositeFilter)
    assert len(intersection_filter.filters) == 2


@pytest.mark.parametrize("is_case_set", [False, True], ids=["case", "case-set"])
def test_retrieve_case_or_set_rights_includes_all_collections(
    is_case_set: bool,
) -> None:
    service = object.__new__(CaseService)
    user = SimpleNamespace(id=uuid4())
    repository = MagicMock()
    repository.uow.return_value = nullcontext(object())
    service._repository = repository
    service._get_user_and_repository = MagicMock(return_value=(user, repository))
    entity_id = uuid4()
    created_collection_id = uuid4()
    linked_collection_id = uuid4()
    case_type_id = uuid4()
    entity = SimpleNamespace(
        id=entity_id,
        case_type_id=case_type_id,
        created_in_data_collection_id=created_collection_id,
    )
    link = SimpleNamespace(
        case_set_id=entity_id if is_case_set else None,
        case_id=None if is_case_set else entity_id,
        data_collection_id=linked_collection_id,
    )
    repository.crud.side_effect = [[entity], [link]]
    case_abac = SimpleNamespace(
        get_case_rights=MagicMock(return_value="case-rights"),
        get_case_set_rights=MagicMock(return_value="case-set-rights"),
    )
    cmd = SimpleNamespace(case_ids=[entity_id], case_type_id=case_type_id, user=user)
    if is_case_set:
        cmd = command.RetrieveCaseSetRightsCommand(case_set_ids=[entity_id])

    with patch.object(
        BaseCaseAbacPolicy, "get_case_abac_from_command", return_value=case_abac
    ):
        result = service.retrieve_case_or_set_rights(cmd)

    assert result == ["case-set-rights" if is_case_set else "case-rights"]
    rights_method = (
        case_abac.get_case_set_rights if is_case_set else case_abac.get_case_rights
    )
    rights_method.assert_called_once_with(
        entity_id,
        case_type_id,
        created_collection_id,
        {created_collection_id, linked_collection_id},
    )


def test_retrieve_case_or_set_rights_returns_empty_without_repository_reads() -> None:
    service = object.__new__(CaseService)
    repository = MagicMock()
    service._repository = repository
    service._get_user_and_repository = MagicMock(
        return_value=(SimpleNamespace(id=uuid4()), repository)
    )
    cmd = SimpleNamespace(case_ids=[], case_type_id=uuid4())

    assert service.retrieve_case_or_set_rights(cmd) == []
    repository.crud.assert_not_called()


def test_retrieve_case_sets_with_content_right_filters_unrestricted_sets() -> None:
    service = object.__new__(CaseService)
    service._repository = MagicMock()
    case_type_id = uuid4()
    accessible_set = _case_set(case_type_id=case_type_id)
    inaccessible_set = _case_set(case_type_id=case_type_id)
    service.repository.crud.return_value = [accessible_set, inaccessible_set]
    service._retrieve_case_set_data_collections_map = MagicMock(return_value={})
    case_abac = SimpleNamespace(
        is_full_access=False,
        get_combinations_with_access_right=MagicMock(
            return_value={case_type_id: {accessible_set.created_in_data_collection_id}}
        ),
    )

    result = service._retrieve_case_sets_with_content_right(
        object(),
        uuid4(),
        MagicMock(),
        case_abac,
        enum.CaseRight.READ_CASE_SET,
    )

    assert result == [accessible_set]


@pytest.mark.parametrize(
    ("right", "configured", "expected"),
    [
        (enum.CaseRight.READ_CASE, 12, 12),
        (enum.CaseRight.READ_CASE, 0, 1000),
        (enum.CaseRight.WRITE_CASE, 7, 7),
        (enum.CaseRight.WRITE_CASE, 0, 1000),
    ],
)
def test_resolve_case_date_mappers_and_limits_uses_configured_or_default(
    right: enum.CaseRight, configured: int, expected: int
) -> None:
    service = object.__new__(CaseService)
    service._default_props = model.CaseTypeProps(
        create_max_n_cases=1000,
        read_max_n_cases=1000,
        read_max_tree_size=1000,
        update_max_n_cases=1000,
        delete_max_n_cases=1000,
    )
    case_type = SimpleNamespace(
        id=uuid4(),
        props=SimpleNamespace(
            read_max_n_cases=configured, update_max_n_cases=configured
        ),
    )

    mappers, limit = service._resolve_case_date_mappers_and_limits(
        object(), uuid4(), case_type, right, True, True
    )

    assert mappers == {}
    assert limit == expected


def test_resolve_case_date_mappers_skips_limit_and_reads_restricted_mappers() -> None:
    service = object.__new__(CaseService)
    case_type = SimpleNamespace(id=uuid4(), props=SimpleNamespace())
    expected_mappers = {uuid4(): str}
    with patch.object(
        case_service_module,
        "case_service_get_case_date_col_mappers",
        return_value=expected_mappers,
    ) as get_mappers:
        mappers, limit = service._resolve_case_date_mappers_and_limits(
            object(), uuid4(), case_type, enum.CaseRight.READ_CASE, False, False
        )

    assert mappers == expected_mappers
    assert limit == 0
    get_mappers.assert_called_once()


def test_load_case_type_returns_first_and_raises_when_absent() -> None:
    service = object.__new__(CaseService)
    case_type = object()
    service._repository = MagicMock()
    service.repository.crud.return_value = [case_type]

    assert service._load_case_type(object(), uuid4(), uuid4()) is case_type
    service.repository.crud.return_value = []
    with pytest.raises(exc.InvalidArgumentsError):
        service._load_case_type(object(), uuid4(), uuid4())


def test_resolve_case_type_access_requires_rights_for_restricted_users() -> None:
    service = object.__new__(CaseService)
    user_id = uuid4()
    case_type_id = uuid4()
    collection_id = uuid4()
    access_map = {case_type_id: {collection_id}}
    access_abacs = {case_type_id: {collection_id: object()}}
    case_abac = SimpleNamespace(
        is_full_access=False,
        case_type_access_abacs=access_abacs,
        get_combinations_with_access_right=MagicMock(return_value=access_map),
    )

    assert service._resolve_case_type_access(
        user_id, case_abac, enum.CaseRight.READ_CASE, case_type_id
    ) == (access_map[case_type_id], access_abacs[case_type_id])

    case_abac.get_combinations_with_access_right.return_value = {}
    with pytest.raises(exc.UnauthorizedAuthError):
        service._resolve_case_type_access(
            user_id, case_abac, enum.CaseRight.READ_CASE, case_type_id
        )


def test_retrieve_association_map_builds_either_single_filter() -> None:
    service = object.__new__(CaseService)
    service._repository = MagicMock()
    for ids, expected_field in [
        ((frozenset({uuid4()}), None), "case_id"),
        ((None, frozenset({uuid4()})), "data_collection_id"),
    ]:
        service._retrieve_association_map(
            object(),
            uuid4(),
            model.CaseDataCollectionLink,
            "case_id",
            "data_collection_id",
            *ids,
        )
        filter_value = service.repository.read_fields.call_args.kwargs["filter"]
        assert isinstance(filter_value, UuidSetFilter)
        assert filter_value.key == expected_field


def test_retrieve_complete_case_type_forwards_to_handler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = object.__new__(CaseService)
    cmd = SimpleNamespace(case_type_id=uuid4(), user=None)
    expected = object()
    handler = MagicMock(return_value=expected)
    monkeypatch.setattr(
        case_service_module, "case_service_retrieve_complete_case_type", handler
    )

    assert service.retrieve_complete_case_type(cmd) is expected
    handler.assert_called_once_with(service, cmd)


def test_read_association_with_valid_ids_forwards_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = object.__new__(CaseService)
    expected = [uuid4()]
    handler = MagicMock(return_value=expected)
    monkeypatch.setattr(
        case_service_module, "case_service_read_association_with_valid_ids", handler
    )

    result = service._read_association_with_valid_ids(
        command.CaseDataCollectionLinkCrudCommand,
        "case_id",
        "data_collection_id",
        valid_ids1={uuid4()},
        return_type="ids",
    )

    assert result is expected
    assert handler.call_args.args[:4] == (
        service,
        command.CaseDataCollectionLinkCrudCommand,
        "case_id",
        "data_collection_id",
    )
    assert handler.call_args.kwargs["return_type"] == "ids"


def test_retrieve_case_sets_with_content_right_full_access_filters_by_type() -> None:
    service = object.__new__(CaseService)
    service._repository = MagicMock()
    case_type_id = uuid4()
    matching_set = _case_set(case_type_id=case_type_id)
    other_set = _case_set()
    service.repository.crud.return_value = [matching_set, other_set]
    case_abac = SimpleNamespace(is_full_access=True)

    result = service._retrieve_case_sets_with_content_right(
        object(),
        uuid4(),
        MagicMock(),
        case_abac,
        enum.CaseRight.READ_CASE_SET,
        case_type_id=case_type_id,
    )

    assert result == [matching_set]


def test_retrieve_case_sets_with_content_right_raises_for_requested_no_access() -> None:
    service = object.__new__(CaseService)
    service._repository = MagicMock()
    case_set = _case_set()
    service.repository.crud.return_value = [case_set]
    service._retrieve_case_set_data_collections_map = MagicMock(return_value={})
    case_abac = SimpleNamespace(
        is_full_access=False,
        get_combinations_with_access_right=MagicMock(return_value={}),
    )

    with pytest.raises(exc.UnauthorizedAuthError):
        service._retrieve_case_sets_with_content_right(
            object(),
            uuid4(),
            MagicMock(),
            case_abac,
            enum.CaseRight.READ_CASE_SET,
            case_set_ids=[case_set.id],
        )


def test_filter_cases_by_access_drops_denied_cases_and_stops_at_weighted_limit() -> (
    None
):
    service = object.__new__(CaseService)
    service._retrieve_case_data_collections_map = MagicMock(return_value={})
    service._authorize_case = MagicMock(
        side_effect=[None, frozenset({uuid4()}), frozenset({uuid4()})]
    )
    service._filter_case_content = MagicMock()
    cases = [_case(), _case(), _case()]
    cases[1].count = 2

    result, exceeded = service._filter_cases_by_access_and_content(
        object(),
        uuid4(),
        enum.CaseRight.READ_CASE,
        None,
        True,
        None,
        set(),
        {},
        1,
        cases,
        False,
    )

    assert result == []
    assert exceeded
    service._filter_case_content.assert_not_called()


def test_retrieve_cases_with_content_right_returns_full_access_cases() -> None:
    service = object.__new__(CaseService)
    case_type_id = uuid4()
    user_id = uuid4()
    cases = [_case()]
    service._validate_case_access_args = MagicMock()
    service._resolve_case_type_access = MagicMock(return_value=(set(), {}))
    service._load_case_type = MagicMock(return_value=object())
    service._resolve_case_date_mappers_and_limits = MagicMock(return_value=({}, 0))
    service._retrieve_cases_by_ids_or_case_type_filter = MagicMock(
        return_value=(cases, False)
    )
    case_abac = SimpleNamespace(is_full_access=True)

    result = service._retrieve_cases_with_content_right(
        object(), user_id, case_abac, enum.CaseRight.READ_CASE, case_type_id
    )

    assert result == (cases, False)
    service._filter_cases_by_access_and_content = MagicMock()
    service._filter_cases_by_access_and_content.assert_not_called()


def test_retrieve_cases_with_content_right_filters_and_calculates_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = object.__new__(CaseService)
    case_type_id = uuid4()
    user_id = uuid4()
    cases = [_case()]
    filtered_cases = [cases[0]]
    date_filter = DatetimeRangeFilter(
        key="", lower_bound=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    mappers = {uuid4(): str}
    service._validate_case_access_args = MagicMock()
    service._resolve_case_type_access = MagicMock(return_value=({uuid4()}, {}))
    service._load_case_type = MagicMock(return_value=object())
    service._resolve_case_date_mappers_and_limits = MagicMock(return_value=(mappers, 3))
    service._retrieve_cases_by_ids_or_case_type_filter = MagicMock(
        return_value=(cases, False)
    )
    service._filter_cases_by_access_and_content = MagicMock(
        return_value=(filtered_cases, False)
    )
    calculate_date = MagicMock()
    monkeypatch.setattr(
        case_service_module, "case_service_calculate_case_date", calculate_date
    )

    result = service._retrieve_cases_with_content_right(
        object(),
        user_id,
        SimpleNamespace(is_full_access=False),
        enum.CaseRight.READ_CASE,
        case_type_id,
        datetime_range_filter=date_filter,
        calculate_case_date=True,
    )

    assert result == (filtered_cases, False)
    assert date_filter.key == "timed_at"
    calculate_date.assert_called_once_with(cases, mappers)


def test_retrieve_cases_with_content_right_rejects_invalid_date_key() -> None:
    service = object.__new__(CaseService)
    service._validate_case_access_args = MagicMock()
    service._resolve_case_type_access = MagicMock(return_value=(set(), {}))
    service._load_case_type = MagicMock(return_value=object())
    service._resolve_case_date_mappers_and_limits = MagicMock(return_value=({}, 0))
    date_filter = DatetimeRangeFilter(
        key="wrong", lower_bound=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )

    with pytest.raises(exc.InvalidArgumentsError):
        service._retrieve_cases_with_content_right(
            object(),
            uuid4(),
            SimpleNamespace(is_full_access=True),
            enum.CaseRight.READ_CASE,
            uuid4(),
            datetime_range_filter=date_filter,
        )


def test_resolve_case_date_mappers_rejects_unsupported_right() -> None:
    service = object.__new__(CaseService)
    case_type = SimpleNamespace(props=SimpleNamespace())

    with pytest.raises(NotImplementedError):
        service._resolve_case_date_mappers_and_limits(
            object(), uuid4(), case_type, enum.CaseRight.READ_CASE_SET, True, True
        )


def test_retrieve_seq_column_data_accepts_genetic_sequence_and_rejects_other_type() -> (
    None
):
    service = object.__new__(CaseService)
    user = SimpleNamespace(id=uuid4())
    seq_col = SimpleNamespace(id=uuid4(), ref_col_id=uuid4())
    ref_col = SimpleNamespace(col_type=enum.ColType.GENETIC_SEQUENCE)
    service._repository = MagicMock()
    service.repository.crud.side_effect = [seq_col, ref_col]

    assert service._retrieve_seq_column_data(object(), user, seq_col.id) == (
        seq_col,
        ref_col,
    )
    ref_col.col_type = enum.ColType.TEXT
    service.repository.crud.side_effect = [seq_col, ref_col]
    with pytest.raises(exc.InvalidArgumentsError):
        service._retrieve_seq_column_data(object(), user, seq_col.id)


def test_verify_case_set_member_case_type_accepts_match_and_rejects_mismatch() -> None:
    service = object.__new__(CaseService)
    service._repository = MagicMock()
    service.repository.uow.return_value = nullcontext(object())
    case_type_id = uuid4()
    case_set_id = uuid4()
    case_id = uuid4()
    member = model.CaseSetMember(id=uuid4(), case_set_id=case_set_id, case_id=case_id)
    case_set = _case_set(case_set_id=case_set_id, case_type_id=case_type_id)
    case = _case(case_id=case_id)
    case.case_type_id = case_type_id
    service.repository.crud.side_effect = [[case_set], [case]]

    service._verify_case_set_member_case_type(None, [member])

    case.case_type_id = uuid4()
    service.repository.crud.side_effect = [[case_set], [case]]
    with pytest.raises(exc.InvalidArgumentsError):
        service._verify_case_set_member_case_type(None, [member])
