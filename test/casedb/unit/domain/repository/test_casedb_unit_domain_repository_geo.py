"""Unit tests for the casedb geographic repository base class."""

from typing import Any

import pytest

from gen_epix.casedb.domain.repository.geo import BaseGeoRepository
from gen_epix.fastapp import BaseRepository


def _noop(*_args: Any, **_kwargs: Any) -> None:
    """Accept any arguments and do nothing."""


@pytest.fixture(name="concrete_class")
def concrete_class_fixture() -> type[BaseGeoRepository]:
    """Return a concrete subclass implementing every abstract member."""
    namespace: dict[str, Any] = {
        name: _noop for name in BaseGeoRepository.__abstractmethods__
    }
    namespace["create_repository"] = classmethod(lambda cls, **kw: cls(**kw))
    return type("ConcreteGeoRepository", (BaseGeoRepository,), namespace)


def test_inherits_from_base_repository() -> None:
    """The geo base class extends the shared repository base."""
    assert issubclass(BaseGeoRepository, BaseRepository)


def test_base_class_is_abstract() -> None:
    """The geo base class cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseGeoRepository()  # type: ignore[abstract] # pylint: disable=E0110


def test_concrete_subclass_uses_default_identity(
    concrete_class: type[BaseGeoRepository],
) -> None:
    """Without kwargs the name defaults to the generated id."""
    repo = concrete_class()  # pylint: disable=E0110
    assert repo.id
    assert repo.name == repo.id


def test_concrete_subclass_accepts_identity_kwargs(
    concrete_class: type[BaseGeoRepository],
) -> None:
    """Explicit id and name kwargs are honored."""
    repo = concrete_class.create_repository(id="geo-1", name="Geo")
    assert (repo.id, repo.name) == ("geo-1", "Geo")
