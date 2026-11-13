from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain.model.abac import policy as policy_module
from gen_epix.casedb.domain.model.abac.policy import (
    BaseCasePolicy,
    OrganizationAccessCasePolicy,
    OrganizationShareCasePolicy,
    UserAccessCasePolicy,
    UserShareCasePolicy,
)

BASE_FLAGS = (
    "is_active",
    "add_case",
    "remove_case",
    "add_case_set",
    "remove_case_set",
)

# model class -> (owner field, plural name, table name, key fields)
ACCESS_METADATA: dict[type, tuple[str, str, str, tuple[str, ...]]] = {
    OrganizationAccessCasePolicy: (
        "organization_id",
        "organization_access_case_policies",
        "organization_access_case_policy",
        ("organization_id", "data_collection_id"),
    ),
    UserAccessCasePolicy: (
        "user_id",
        "user_access_case_policies",
        "user_access_case_policy",
        ("user_id", "data_collection_id"),
    ),
}
SHARE_METADATA: dict[type, tuple[str, str, str, tuple[str, ...]]] = {
    OrganizationShareCasePolicy: (
        "organization_id",
        "organization_share_case_policies",
        "organization_share_case_policy",
        ("organization_id", "data_collection_id", "from_data_collection_id"),
    ),
    UserShareCasePolicy: (
        "user_id",
        "user_share_case_policies",
        "user_share_case_policy",
        ("user_id", "data_collection_id", "from_data_collection_id"),
    ),
}

ACCESS_PARAMS = [
    pytest.param(cls, meta[0], id=cls.__name__) for cls, meta in ACCESS_METADATA.items()
]
SHARE_PARAMS = [
    pytest.param(cls, meta[0], id=cls.__name__) for cls, meta in SHARE_METADATA.items()
]


def _base_kwargs() -> dict[str, Any]:
    return {
        "data_collection_id": uuid4(),
        "case_type_set_id": uuid4(),
        "is_active": True,
        "add_case": False,
        "remove_case": True,
        "add_case_set": False,
        "remove_case_set": True,
    }


def _access_kwargs(owner_field: str) -> dict[str, Any]:
    kwargs = _base_kwargs()
    kwargs[owner_field] = uuid4()
    kwargs["read_case_set"] = True
    kwargs["write_case_set"] = False
    if owner_field == "organization_id":
        kwargs["is_private"] = False
    return kwargs


def _share_kwargs(owner_field: str) -> dict[str, Any]:
    kwargs = _base_kwargs()
    kwargs[owner_field] = uuid4()
    kwargs["from_data_collection_id"] = uuid4()
    return kwargs


def _link_map(entity: Any) -> dict[str, str]:
    return {
        link.link_field_name: link.relationship_field_name
        for link in entity.links.values()
    }


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestBaseCasePolicy:
    def test_valid_construction_and_defaults(self) -> None:
        kwargs = _base_kwargs()
        obj = BaseCasePolicy(**kwargs)
        assert obj.data_collection_id == kwargs["data_collection_id"]
        assert obj.case_type_set_id == kwargs["case_type_set_id"]
        assert obj.data_collection is None
        assert obj.case_type_set is None

    @pytest.mark.parametrize(
        "missing", ["data_collection_id", "case_type_set_id", *BASE_FLAGS]
    )
    def test_missing_required_field(self, missing: str) -> None:
        kwargs = _base_kwargs()
        del kwargs[missing]
        with pytest.raises(ValidationError):
            BaseCasePolicy(**kwargs)

    def test_invalid_uuid_rejected(self) -> None:
        kwargs = _base_kwargs()
        kwargs["data_collection_id"] = "not-a-uuid"
        with pytest.raises(ValidationError):
            BaseCasePolicy(**kwargs)

    def test_none_flag_rejected(self) -> None:
        kwargs = _base_kwargs()
        kwargs["is_active"] = None
        with pytest.raises(ValidationError):
            BaseCasePolicy(**kwargs)

    def test_has_no_entity(self) -> None:
        assert "ENTITY" not in vars(BaseCasePolicy)


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestAccessCasePolicies:
    @pytest.mark.parametrize("model_class", list(ACCESS_METADATA))
    def test_entity_metadata(self, model_class: Any) -> None:
        owner_field, plural_name, table_name, key_fields = ACCESS_METADATA[model_class]
        entity = model_class.ENTITY
        assert entity.snake_case_plural_name == plural_name
        assert entity.table_name == table_name
        assert entity.persistable is True
        assert list(entity.keys) == [1]
        assert entity.keys[1].field_names == key_fields
        assert _link_map(entity) == {
            owner_field: owner_field.removesuffix("_id"),
            "data_collection_id": "data_collection",
            "case_type_set_id": "case_type_set",
            "read_col_set_id": "read_col_set",
            "write_col_set_id": "write_col_set",
        }

    @pytest.mark.parametrize("model_class, owner_field", ACCESS_PARAMS)
    def test_defaults(self, model_class: Any, owner_field: str) -> None:
        obj = model_class(**_access_kwargs(owner_field))
        assert obj.read_col_set_id is None
        assert obj.write_col_set_id is None
        assert obj.read_col_set is None
        assert obj.write_col_set is None
        assert getattr(obj, owner_field.removesuffix("_id")) is None
        assert obj.read_case_set is True
        assert obj.write_case_set is False

    @pytest.mark.parametrize("model_class, owner_field", ACCESS_PARAMS)
    def test_col_set_ids_accepted(self, model_class: Any, owner_field: str) -> None:
        read_id, write_id = uuid4(), uuid4()
        obj = model_class(
            **_access_kwargs(owner_field),
            read_col_set_id=read_id,
            write_col_set_id=write_id,
        )
        assert obj.read_col_set_id == read_id
        assert obj.write_col_set_id == write_id

    @pytest.mark.parametrize("model_class, owner_field", ACCESS_PARAMS)
    @pytest.mark.parametrize("missing", ["read_case_set", "write_case_set"])
    def test_missing_required_case_set_flags(
        self, model_class: Any, owner_field: str, missing: str
    ) -> None:
        kwargs = _access_kwargs(owner_field)
        del kwargs[missing]
        with pytest.raises(ValidationError):
            model_class(**kwargs)

    @pytest.mark.parametrize("model_class, owner_field", ACCESS_PARAMS)
    def test_missing_owner_id(self, model_class: Any, owner_field: str) -> None:
        kwargs = _access_kwargs(owner_field)
        del kwargs[owner_field]
        with pytest.raises(ValidationError):
            model_class(**kwargs)

    def test_organization_requires_is_private(self) -> None:
        kwargs = _access_kwargs("organization_id")
        del kwargs["is_private"]
        with pytest.raises(ValidationError):
            OrganizationAccessCasePolicy(**kwargs)

    def test_user_policy_has_no_is_private(self) -> None:
        fields: dict[str, Any] = dict(UserAccessCasePolicy.model_fields)
        assert "is_private" not in fields

    @pytest.mark.parametrize("model_class, owner_field", ACCESS_PARAMS)
    def test_key_uses_owner_and_collection_only(
        self, model_class: Any, owner_field: str
    ) -> None:
        kwargs = _access_kwargs(owner_field)
        key = model_class.ENTITY.keys[1]
        obj = model_class(**kwargs)
        same_key = model_class(
            **{**kwargs, "case_type_set_id": uuid4(), "add_case": True}
        )
        other_collection = model_class(**{**kwargs, "data_collection_id": uuid4()})
        assert key(obj) == key(same_key)
        assert key(obj) != key(other_collection)


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestShareCasePolicies:
    @pytest.mark.parametrize("model_class", list(SHARE_METADATA))
    def test_entity_metadata(self, model_class: Any) -> None:
        owner_field, plural_name, table_name, key_fields = SHARE_METADATA[model_class]
        entity = model_class.ENTITY
        assert entity.snake_case_plural_name == plural_name
        assert entity.table_name == table_name
        assert entity.persistable is True
        assert entity.keys[1].field_names == key_fields
        assert _link_map(entity) == {
            owner_field: owner_field.removesuffix("_id"),
            "data_collection_id": "data_collection",
            "case_type_set_id": "case_type_set",
            "from_data_collection_id": "from_data_collection",
        }

    @pytest.mark.parametrize("model_class, owner_field", SHARE_PARAMS)
    def test_valid_construction_defaults(
        self, model_class: Any, owner_field: str
    ) -> None:
        kwargs = _share_kwargs(owner_field)
        obj = model_class(**kwargs)
        assert obj.from_data_collection_id == kwargs["from_data_collection_id"]
        assert obj.from_data_collection is None
        assert getattr(obj, owner_field.removesuffix("_id")) is None

    @pytest.mark.parametrize("model_class, owner_field", SHARE_PARAMS)
    @pytest.mark.parametrize("missing_kind", ["owner", "from"])
    def test_missing_required_ids(
        self, model_class: Any, owner_field: str, missing_kind: str
    ) -> None:
        kwargs = _share_kwargs(owner_field)
        missing = owner_field if missing_kind == "owner" else "from_data_collection_id"
        del kwargs[missing]
        with pytest.raises(ValidationError):
            model_class(**kwargs)

    @pytest.mark.parametrize("model_class, owner_field", SHARE_PARAMS)
    def test_key_distinguishes_source_collection(
        self, model_class: Any, owner_field: str
    ) -> None:
        kwargs = _share_kwargs(owner_field)
        key = model_class.ENTITY.keys[1]
        first = model_class(**kwargs)
        other_source = model_class(**{**kwargs, "from_data_collection_id": uuid4()})
        same_key = model_class(**{**kwargs, "add_case": True})
        assert key(first) != key(other_source)
        assert key(first) == key(same_key)


@pytest.mark.scenario_ids("TC-SEC-29-01")
@pytest.mark.parametrize(
    "name",
    [
        "OrganizationAccessCasePolicy",
        "UserAccessCasePolicy",
        "OrganizationShareCasePolicy",
        "UserShareCasePolicy",
    ],
)
def test_policies_derive_from_base(name: str) -> None:
    assert issubclass(getattr(policy_module, name), BaseCasePolicy)
