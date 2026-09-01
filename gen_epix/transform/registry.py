"""Named registry for transformer classes and transformer factory functions."""

from collections.abc import Callable
from typing import Any, TypeVar

from gen_epix.transform.transformer import Transformer

TransformerType = TypeVar("TransformerType", bound=Transformer)


class Registry:
    """Store named constructors and create transformers from configuration."""

    _transformers: dict[str, type[Transformer]] = {}
    _factories: dict[str, Callable[..., Transformer]] = {}

    @classmethod
    def register(cls, name: str, transformer_class: type[Transformer]) -> None:
        """Register a transformer class by name."""
        cls._transformers[name] = transformer_class

    @classmethod
    def register_factory(
        cls, name: str, factory_fn: Callable[..., Transformer]
    ) -> None:
        """Register a factory function for creating transformer instances."""
        cls._factories[name] = factory_fn

    @classmethod
    def create(cls, name: str, **kwargs: Any) -> Transformer:
        """Create a named transformer, preferring a registered factory over a class.

        Args:
            name: Registered transformer or factory name.
            **kwargs: Arguments forwarded to the selected constructor.

        Returns:
            Transformer created by the registered factory or class.

        Raises:
            ValueError: If no transformer class or factory is registered as ``name``.
        """
        if name in cls._factories:
            return cls._factories[name](**kwargs)
        elif name in cls._transformers:
            return cls._transformers[name](**kwargs)
        else:
            raise ValueError(f"Unknown transformer: {name}")

    @classmethod
    def list_available(cls) -> list[str]:
        """List all available transformer names."""
        return list(set(cls._transformers.keys()) | set(cls._factories.keys()))

    @classmethod
    def decorator(
        cls, name: str
    ) -> Callable[[type[TransformerType]], type[TransformerType]]:
        """Decorator for registering transformer classes."""

        def wrapper(transformer_class: type[TransformerType]) -> type[TransformerType]:
            """Register the decorated transformer class and return it unchanged."""
            cls.register(name, transformer_class)
            return transformer_class

        return wrapper

    @classmethod
    def factory_decorator(
        cls, name: str
    ) -> Callable[[Callable[..., TransformerType]], Callable[..., TransformerType]]:
        """Decorator for registering factory functions."""

        def wrapper(
            factory_fn: Callable[..., TransformerType],
        ) -> Callable[..., TransformerType]:
            """Register the decorated factory function and return it unchanged."""
            cls.register_factory(name, factory_fn)
            return factory_fn

        return wrapper

    @classmethod
    def clear(cls) -> None:
        """Clear all registered transformers and factories."""
        cls._transformers.clear()
        cls._factories.clear()


# Convenience decorators
def register_transformer(
    name: str,
) -> Callable[[type[TransformerType]], type[TransformerType]]:
    """Decorator to register a transformer class."""
    return Registry.decorator(name)


def register_factory(
    name: str,
) -> Callable[[Callable[..., TransformerType]], Callable[..., TransformerType]]:
    """Decorator to register a transformer factory function."""
    return Registry.factory_decorator(name)
