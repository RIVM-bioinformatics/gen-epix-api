"""Unit tests for the casedb ontology repository contract."""

import inspect

import pytest

from gen_epix.casedb.domain import repository as repository_package
from gen_epix.casedb.domain.repository import ontology
from gen_epix.casedb.domain.repository.ontology import BaseOntologyRepository
from gen_epix.fastapp import BaseRepository


def test_subclasses_base_repository():
    assert issubclass(BaseOntologyRepository, BaseRepository)


def test_adds_no_members_of_its_own():
    own_members = {
        name for name in vars(BaseOntologyRepository) if not name.startswith("_")
    }

    assert own_members == set()


def test_remains_abstract_with_inherited_abstract_methods():
    assert inspect.isabstract(BaseOntologyRepository)
    assert BaseOntologyRepository.__abstractmethods__ == (
        BaseRepository.__abstractmethods__
    )


def test_direct_instantiation_raises_type_error():
    with pytest.raises(TypeError, match="abstract"):
        BaseOntologyRepository()  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated


def test_concrete_subclass_must_implement_abstract_methods():
    class Incomplete(BaseOntologyRepository):  # pylint: disable=abstract-method
        pass

    with pytest.raises(TypeError, match="abstract"):
        Incomplete()  # type: ignore[abstract]  # pylint: disable=abstract-class-instantiated


def test_reexported_from_repository_package():
    assert repository_package.BaseOntologyRepository is BaseOntologyRepository
    assert ontology.BaseOntologyRepository is BaseOntologyRepository
