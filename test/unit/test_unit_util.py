import asyncio
import hashlib
from uuid import UUID

import pytest
from pydantic import BaseModel, Field, ValidationError

import gen_epix.util as util


@pytest.fixture(autouse=True)
def clear_package_version_cache():
    util.get_package_version.cache_clear()
    yield
    util.get_package_version.cache_clear()


def test_sync_returns_value(tmp_path):
    @util.profile_method(path=str(tmp_path))
    def sync_add(a, b):
        return a + b

    assert sync_add(1, 2) == 3


def test_sync_writes_log_file(tmp_path):
    @util.profile_method(path=str(tmp_path))
    def sync_add(a, b):
        return a + b

    sync_add(1, 2)
    logs = list(tmp_path.glob("sync_add-*.log"))
    assert len(logs) == 1
    assert logs[0].stat().st_size > 0


def test_async_returns_value(tmp_path):
    @util.profile_method(path=str(tmp_path))
    async def async_add(a, b):
        return a + b

    assert asyncio.run(async_add(1, 2)) == 3


def test_async_writes_log_file(tmp_path):
    @util.profile_method(path=str(tmp_path))
    async def async_add(a, b):
        return a + b

    asyncio.run(async_add(1, 2))
    logs = list(tmp_path.glob("async_add-*.log"))
    assert len(logs) == 1
    assert logs[0].stat().st_size > 0


def test_sync_propagates_exception(tmp_path):
    @util.profile_method(path=str(tmp_path))
    def boom():
        raise ValueError("oops")

    with pytest.raises(ValueError, match="oops"):
        boom()
    with pytest.raises(ValueError, match="oops"):
        boom()


def test_generate_ulid_returns_distinct_uuids():
    first = util.generate_ulid()
    second = util.generate_ulid()

    assert isinstance(first, UUID)
    assert isinstance(second, UUID)
    assert first != second


def test_get_package_root_finds_repository_root():
    assert (util.get_package_root() / "pyproject.toml").is_file()


def test_get_package_root_raises_when_no_project_metadata_exists(monkeypatch, tmp_path):
    monkeypatch.setattr(util, "__file__", str(tmp_path / "isolated" / "util.py"))

    with pytest.raises(FileNotFoundError, match="Could not find pyproject.toml"):
        util.get_package_root()


def test_get_package_version_reads_and_caches_project_version(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    project_file = tmp_path / "pyproject.toml"
    project_file.write_text('[project]\nversion = "1.2.3"\n', encoding="utf-8")

    assert util.get_package_version() == "1.2.3"

    project_file.write_text('[project]\nversion = "4.5.6"\n', encoding="utf-8")
    assert util.get_package_version() == "1.2.3"


def test_get_package_version_raises_for_missing_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(FileNotFoundError):
        util.get_package_version()


def test_get_package_version_raises_when_project_version_is_missing(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'example'\n")

    with pytest.raises(KeyError, match="version"):
        util.get_package_version()


def test_map_paired_elements_supports_list_set_and_frozen_set_values():
    data = [("a", 1), ("b", 2), ("a", 1), ("a", 3)]

    assert util.map_paired_elements(data) == {"a": [1, 1, 3], "b": [2]}
    assert util.map_paired_elements(data, as_set=True) == {
        "a": {1, 3},
        "b": {2},
    }
    frozen_result = util.map_paired_elements(data, as_set=True, frozen=True)
    assert frozen_result == {"a": frozenset({1, 3}), "b": frozenset({2})}
    assert util.map_paired_elements([], as_set=True, frozen=True) == {}


def test_copy_model_field_preserves_constraints_and_applies_overrides():
    class SourceModel(BaseModel):
        count: int = Field(default=1, ge=1, description="Source count")

    class TargetModel(BaseModel):
        count: int = util.copy_model_field(
            SourceModel, "count", default=2, description="Target count"
        )

    assert TargetModel().count == 2
    assert TargetModel.model_fields["count"].description == "Target count"
    with pytest.raises(ValidationError):
        TargetModel(count=0)


def test_copy_model_field_raises_for_unknown_field():
    class SourceModel(BaseModel):
        value: str

    with pytest.raises(KeyError, match="missing"):
        util.copy_model_field(SourceModel, "missing")


def test_add_parent_class_docs_appends_parent_docs_and_respects_exclusions():
    class Parent:
        """Parent details."""

    class Child(Parent):
        """Child details."""

    result = util.add_parent_class_docs(Child)

    assert result == Child.__doc__
    assert "PARENT CLASS DOCUMENTATION" in result
    assert "Parent details." in result

    class ExcludedParent:
        """Excluded details."""

    class ExcludedChild(ExcludedParent):
        """Child remains unchanged."""

    exclusions = {ExcludedParent}
    result = util.add_parent_class_docs(ExcludedChild, exclude=exclusions)

    assert result == "Child remains unchanged."
    assert object in exclusions


def test_add_parent_class_docs_processes_class_sets_parent_first():
    class Root:
        """Root details."""

    class Child(Root):
        """Child details."""

    assert util.add_parent_class_docs({Child, Root}) is None
    assert "Root details." in Child.__doc__
    assert "PARENT CLASS DOCUMENTATION" in Child.__doc__


def test_order_classes_by_parent_retries_children_before_parents():
    class Parent:
        pass

    class Child(Parent):
        pass

    result = util._order_classes_by_parent({Child: {Parent}, Parent: set()})

    assert result == [Parent, Child]


def test_add_parent_class_docs_handles_parent_without_documentation():
    class Parent:
        pass

    class Child(Parent):
        """Child details."""

    assert util.add_parent_class_docs(Child) == "Child details."
    assert Child.__doc__ == "Child details."


def test_add_parent_class_docs_handles_none_exclusions_and_missing_child_doc():
    class Parent:
        """Parent details."""

    class UndocumentedChild(Parent):
        pass

    result = util.add_parent_class_docs(UndocumentedChild, exclude=None)

    assert result is not None
    assert result.startswith("PARENT CLASS DOCUMENTATION")
    assert "Parent details." in result


def test_str_to_uuid_is_deterministic_for_utf8_text():
    value = "patient-identifier-å"
    expected = UUID(hashlib.sha256(value.encode("utf-8")).digest()[:16].hex())

    assert util.str_to_uuid(value) == expected
    assert util.str_to_uuid(value) == util.str_to_uuid(value)
    assert util.str_to_uuid(value) != util.str_to_uuid("another-value")


@pytest.mark.parametrize("value", [0, (1 << 64) - 1], ids=["zero", "max-u64"])
def test_int_to_uuid_hashes_unsigned_64_bit_values(value):
    expected = UUID(
        hashlib.sha256(value.to_bytes(length=8, byteorder="big", signed=False))
        .digest()[:16]
        .hex()
    )

    assert util.int_to_uuid(value) == expected


@pytest.mark.parametrize("value", [-1, 1 << 64], ids=["negative", "overflow"])
def test_int_to_uuid_rejects_values_outside_unsigned_64_bit_range(value):
    with pytest.raises(OverflowError):
        util.int_to_uuid(value)


def test_chunk_list_handles_empty_unbounded_and_partial_chunks():
    values = [1, 2, 3, 4, 5]

    assert util.chunk_list([], 2) == []
    assert util.chunk_list([], None) == []
    assert util.chunk_list(values, None) == [values]
    assert util.chunk_list(values, 2) == [[1, 2], [3, 4], [5]]
    assert util.chunk_list(values, len(values)) == [values]


@pytest.mark.parametrize("chunk_size", [0, -1], ids=["zero", "negative"])
def test_chunk_list_rejects_non_positive_chunk_sizes(chunk_size):
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        util.chunk_list([1, 2], chunk_size)


def test_profile_method_uses_package_root_when_path_is_omitted(monkeypatch, tmp_path):
    monkeypatch.setattr(util, "get_package_root", lambda: tmp_path)

    @util.profile_method()
    def default_path_call():
        return "complete"

    assert default_path_call() == "complete"
    assert len(list(tmp_path.glob("default_path_call-*.log"))) == 1


def test_async_profile_propagates_exception_and_writes_log(tmp_path):
    @util.profile_method(path=str(tmp_path))
    async def async_boom():
        raise ValueError("async failure")

    with pytest.raises(ValueError, match="async failure"):
        asyncio.run(async_boom())

    assert len(list(tmp_path.glob("async_boom-*.log"))) == 1
