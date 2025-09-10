"""
Transformer registry for managing and creating transformer instances.
"""

from typing import Any, Callable, Type, TypeVar

from gen_epix.transform.transformer import Transformer

T = TypeVar("T", bound=Transformer)


class Registry:
    """Central registry for transformer types and factory methods."""

    _transformers: dict[str, Type[Transformer]] = {}
    _factories: dict[str, Callable[..., Transformer]] = {}

    @classmethod
    def register(cls, name: str, transformer_class: Type[Transformer]) -> None:
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
        """Create transformer instance by name."""
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
    def decorator(cls, name: str) -> Callable[[Type[T]], Type[T]]:
        """Decorator for registering transformer classes."""

        def wrapper(transformer_class: Type[T]) -> Type[T]:
            cls.register(name, transformer_class)
            return transformer_class

        return wrapper

    @classmethod
    def factory_decorator(
        cls, name: str
    ) -> Callable[[Callable[..., T]], Callable[..., T]]:
        """Decorator for registering factory functions."""

        def wrapper(factory_fn: Callable[..., T]) -> Callable[..., T]:
            cls.register_factory(name, factory_fn)
            return factory_fn

        return wrapper

    @classmethod
    def clear(cls) -> None:
        """Clear all registered transformers and factories."""
        cls._transformers.clear()
        cls._factories.clear()


# Convenience decorators
def register_transformer(name: str) -> Callable[[Type[T]], Type[T]]:
    """Decorator to register a transformer class."""
    return Registry.decorator(name)


def register_factory(name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to register a transformer factory function."""
    return Registry.factory_decorator(name)
