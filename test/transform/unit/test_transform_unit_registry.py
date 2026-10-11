from collections.abc import Iterator

import pytest

from gen_epix.transform.adapter import ObjectAdapter
from gen_epix.transform.registry import (
    Registry,
    register_factory,
    register_transformer,
)
from gen_epix.transform.transformer import Transformer


class IdentityTransformer(Transformer):
    """Return the supplied adapter unchanged."""

    def transform(self, obj: ObjectAdapter) -> ObjectAdapter:
        """Return the input adapter."""
        return obj


class MarkedTransformer(IdentityTransformer):
    """Expose constructor keyword forwarding for registry tests."""

    def __init__(self, marker: str):
        """Store a caller-provided marker after initializing the transformer."""
        super().__init__()
        self.marker = marker


@pytest.fixture(autouse=True)
def clear_registry() -> Iterator[None]:
    """Isolate registry tests from global registrations."""
    Registry.clear()
    yield
    Registry.clear()


def test_create_uses_registered_transformer_class_and_forwards_arguments() -> None:
    """Instantiate the registered transformer class with caller arguments."""
    Registry.register("identity", MarkedTransformer)

    transformer = Registry.create("identity", marker="custom")

    assert isinstance(transformer, MarkedTransformer)
    assert transformer.marker == "custom"


def test_registered_factory_takes_precedence_over_class() -> None:
    """Prefer a same-named factory and forward its keyword arguments."""
    Registry.register("shared", MarkedTransformer)
    Registry.register_factory("shared", lambda marker: MarkedTransformer(marker=marker))

    transformer = Registry.create("shared", marker="from-factory")

    assert isinstance(transformer, MarkedTransformer)
    assert transformer.marker == "from-factory"


def test_decorators_register_classes_and_factories() -> None:
    """Register decorated constructors while returning the original objects."""

    @register_transformer("decorated-class")
    class DecoratedTransformer(IdentityTransformer):
        """Identify a class registered through the convenience decorator."""

    @register_factory("decorated-factory")
    def create_transformer() -> IdentityTransformer:
        """Create a transformer registered through the factory decorator."""
        return IdentityTransformer()

    assert isinstance(Registry.create("decorated-class"), DecoratedTransformer)
    assert isinstance(Registry.create("decorated-factory"), IdentityTransformer)


def test_list_available_unifies_names_and_unknown_names_raise() -> None:
    """List unique class and factory names and reject unknown constructors."""
    Registry.register("shared", IdentityTransformer)
    Registry.register_factory("shared", lambda: IdentityTransformer())
    Registry.register_factory("factory-only", lambda: IdentityTransformer())

    assert set(Registry.list_available()) == {"shared", "factory-only"}
    with pytest.raises(ValueError, match="Unknown transformer: missing"):
        Registry.create("missing")
