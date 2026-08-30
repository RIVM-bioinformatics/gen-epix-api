"""Cache key construction.

A key generator turns a decorated function and its call arguments into a stable
string. The module offers the positional generator used by default, a keyword
aware generator, a template generator in which the caller names the participating
parameters, and manglers that bound key length. `KeySpec` bundles those choices
so that a region or a decorator can be configured declaratively.
"""

import hashlib
import inspect
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from gen_epix.fastapp.cache.exc import CacheConfigurationError

SELF_PARAMETER_NAMES: frozenset[str] = frozenset({"self", "cls"})
"""Parameter names dropped from a key because they identify the receiver."""


@runtime_checkable
class KeyGeneratorFactory(Protocol):
    """Produce the key generator for one decorated function."""

    def __call__(
        self,
        namespace: str,
        fn: Callable[..., Any],
    ) -> Callable[..., str]:
        """Return a callable that maps the arguments of `fn` to a key.

        Args:
            namespace: Discriminator that separates same-named functions.
            fn: The function whose calls are cached.
        """
        ...


def function_namespace(fn: Callable[..., Any], namespace: str | None = None) -> str:
    """Return the qualified name identifying `fn` inside a region.

    Args:
        fn: The function whose calls are cached.
        namespace: Optional extra discriminator appended to the name. It is
            needed for same-named methods on different classes, because a
            decorator sees the function before the class exists.

    Returns:
        A string of the form ``module:qualname`` with the namespace appended.
    """
    module = getattr(fn, "__module__", "") or ""
    qualname = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", "fn")
    base = f"{module}:{qualname}"
    return f"{base}|{namespace}" if namespace else base


def bind_arguments(
    fn: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
) -> dict[str, Any]:
    """Return the call arguments of `fn` by parameter name, defaults applied.

    Tag templates and key templates both need arguments addressed by name, so
    that a writer can reproduce them without replaying the call positionally.

    Args:
        fn: The called function.
        args: Positional arguments of the call.
        kwargs: Keyword arguments of the call.

    Returns:
        A mapping from parameter name to value, with the receiver removed.

    Raises:
        TypeError: If the arguments do not match the signature of `fn`.
    """
    bound = inspect.signature(fn).bind(*args, **kwargs)
    bound.apply_defaults()
    return {
        name: value
        for name, value in bound.arguments.items()
        if name not in SELF_PARAMETER_NAMES
    }


def arg_key_generator(
    namespace: str,
    fn: Callable[..., Any],
    to_str: Callable[[Any], str] = str,
) -> Callable[..., str]:
    """Build a generator that keys on positional arguments only.

    This mirrors the default behavior of dogpile.cache: it is fast because it
    avoids signature binding, but a call made with keyword arguments produces a
    different key than the same call made positionally.

    Args:
        namespace: Qualified function namespace to prefix.
        fn: The function whose calls are cached.
        to_str: Conversion applied to each argument.

    Returns:
        A callable that accepts the arguments of `fn` and returns a key.
    """

    def generate_key(*args: Any, **kwargs: Any) -> str:
        """Return the key for one call.

        Args:
            *args: Positional arguments of the cached function.
            **kwargs: Keyword arguments, which this generator cannot represent.

        Returns:
            The composed key.

        Raises:
            ValueError: If keyword arguments are supplied, which this generator
                cannot represent unambiguously.
        """
        if kwargs:
            raise ValueError(
                "arg_key_generator does not support keyword arguments; "
                "use kwarg_key_generator or a template instead"
            )
        positional = args[1:] if _has_receiver(fn) else args
        return namespace + "|" + " ".join(to_str(x) for x in positional)

    return generate_key


def kwarg_key_generator(
    namespace: str,
    fn: Callable[..., Any],
    to_str: Callable[[Any], str] = str,
) -> Callable[..., str]:
    """Build a generator that keys on every parameter by name.

    Binding the call against the signature makes ``f(1)``, ``f(a=1)`` and the
    default value of ``a`` collapse onto one key, which is usually what callers
    expect and what makes an inverse invalidation call reproducible.

    Args:
        namespace: Qualified function namespace to prefix.
        fn: The function whose calls are cached.
        to_str: Conversion applied to each argument value.

    Returns:
        A callable that accepts the arguments of `fn` and returns a key.
    """

    def generate_key(*args: Any, **kwargs: Any) -> str:
        """Return the key for one call."""
        arguments = bind_arguments(fn, args, kwargs)
        rendered = " ".join(
            f"{name}={to_str(value)}" for name, value in sorted(arguments.items())
        )
        return namespace + "|" + rendered

    return generate_key


def template_key_generator(
    template: str,
    to_str: Callable[[Any], str] = str,
) -> KeyGeneratorFactory:
    """Build a factory whose keys follow an explicit format string.

    A template such as ``"case:{case_id}"`` names exactly the parameters that
    participate in the key. Everything else is deliberately excluded, which both
    controls key cardinality and makes the key reproducible from a mutating
    method that never calls the cached function.

    Args:
        template: A format string referencing parameter names of the function.
        to_str: Conversion applied to each substituted value.

    Returns:
        A key generator factory usable wherever a generator is configured.
    """

    def factory(namespace: str, fn: Callable[..., Any]) -> Callable[..., str]:
        """Return the template generator bound to one function.

        Args:
            namespace: Qualified function namespace to prefix.
            fn: The function whose calls are cached.

        Returns:
            A callable mapping the arguments of `fn` to a key.

        Raises:
            CacheConfigurationError: If the template references a parameter that
                `fn` does not declare.
        """
        required = _template_field_names(template)
        parameters = set(inspect.signature(fn).parameters)
        missing = required - parameters
        if missing:
            raise CacheConfigurationError(
                f"Key template references unknown parameters {sorted(missing)} "
                f"of {getattr(fn, '__qualname__', fn)}"
            )

        def generate_key(*args: Any, **kwargs: Any) -> str:
            """Return the key for one call."""
            arguments = bind_arguments(fn, args, kwargs)
            rendered = template.format(
                **{name: to_str(arguments.get(name)) for name in required}
            )
            return namespace + "|" + rendered

        return generate_key

    return factory


def _template_field_names(template: str) -> set[str]:
    """Return the field names referenced by a format string.

    Args:
        template: The format string to inspect.

    Returns:
        The referenced parameter names.

    Raises:
        CacheConfigurationError: If the template uses positional fields, which
            cannot be resolved to parameter names.
    """
    import string

    names: set[str] = set()
    for _, field_name, _, _ in string.Formatter().parse(template):
        if field_name is None:
            continue
        root = field_name.split(".")[0].split("[")[0]
        if not root or root.isdigit():
            raise CacheConfigurationError(
                "Key templates must reference parameters by name"
            )
        names.add(root)
    return names


def _has_receiver(fn: Callable[..., Any]) -> bool:
    """Return whether the first parameter of `fn` is `self` or `cls`."""
    try:
        parameters = list(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        return False
    return bool(parameters) and parameters[0] in SELF_PARAMETER_NAMES


def sha256_mangle_key(key: str) -> str:
    """Return a fixed-length digest of `key`.

    Digesting keeps keys within the length limits of stores such as memcached
    at the cost of losing readability in cache dumps.

    Args:
        key: The composed cache key.
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def length_conditional_mangler(
    length: int,
    mangler: Callable[[str], str] = sha256_mangle_key,
) -> Callable[[str], str]:
    """Build a mangler that only digests keys longer than a threshold.

    Args:
        length: Maximum key length left untouched.
        mangler: Mangler applied to longer keys.

    Returns:
        A mangler preserving readable short keys and bounding long ones.
    """

    def mangle(key: str) -> str:
        """Return `key` unchanged when short enough, otherwise mangled."""
        return key if len(key) <= length else mangler(key)

    return mangle


@dataclass(slots=True)
class KeySpec:
    """Declare how the keys of one cached function are composed.

    Attributes:
        namespace: Extra discriminator appended to the function namespace.
        template: Explicit format string naming the participating parameters.
            When set it takes precedence over `include` and `exclude`.
        include: Parameter names that alone make up the key. Empty means all.
        exclude: Parameter names removed from the key, for values such as a
            unit of work or a logger that must not influence a cache hit.
        to_str: Conversion applied to argument values.
        mangler: Post-processing applied to the composed key.
    """

    namespace: str | None = None
    template: str | None = None
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    to_str: Callable[[Any], str] = str
    mangler: Callable[[str], str] | None = None
    _factory: KeyGeneratorFactory | None = field(default=None, repr=False)

    def build(self, fn: Callable[..., Any]) -> Callable[..., str]:
        """Return the key generator for `fn` implied by this specification.

        Args:
            fn: The function whose calls are cached.

        Returns:
            A callable mapping the arguments of `fn` to a mangled key.

        Raises:
            CacheConfigurationError: If both `include` and `exclude` are set, or
                if a named parameter does not exist on `fn`.
        """
        if self.include and self.exclude:
            raise CacheConfigurationError(
                "A KeySpec accepts either include or exclude, not both"
            )
        namespace = function_namespace(fn, self.namespace)
        factory = self._factory
        if factory is not None:
            generate = factory(namespace, fn)
        elif self.template is not None:
            generate = template_key_generator(self.template, self.to_str)(namespace, fn)
        elif self.include or self.exclude:
            generate = self._selective_generator(namespace, fn)
        else:
            generate = kwarg_key_generator(namespace, fn, self.to_str)
        mangler = self.mangler
        if mangler is None:
            return generate

        def generate_mangled(*args: Any, **kwargs: Any) -> str:
            """Return the mangled key for one call."""
            return mangler(generate(*args, **kwargs))

        return generate_mangled

    def _selective_generator(
        self,
        namespace: str,
        fn: Callable[..., Any],
    ) -> Callable[..., str]:
        """Return a generator restricted to the included or excluded names.

        Args:
            namespace: Qualified function namespace to prefix.
            fn: The function whose calls are cached.

        Returns:
            A callable mapping the selected arguments of `fn` to a key.

        Raises:
            CacheConfigurationError: If a named parameter is not declared by
                `fn`, which would otherwise silently widen the key.
        """
        parameters = set(inspect.signature(fn).parameters)
        named = set(self.include) | set(self.exclude)
        unknown = named - parameters
        if unknown:
            raise CacheConfigurationError(
                f"KeySpec references unknown parameters {sorted(unknown)} "
                f"of {getattr(fn, '__qualname__', fn)}"
            )
        include = set(self.include)
        exclude = set(self.exclude)
        to_str = self.to_str

        def generate_key(*args: Any, **kwargs: Any) -> str:
            """Return the key for one call."""
            arguments = bind_arguments(fn, args, kwargs)
            if include:
                selected = {k: v for k, v in arguments.items() if k in include}
            else:
                selected = {k: v for k, v in arguments.items() if k not in exclude}
            rendered = " ".join(
                f"{name}={to_str(value)}" for name, value in sorted(selected.items())
            )
            return namespace + "|" + rendered

        return generate_key


def compose_key(parts: Iterable[str], separator: str = ":") -> str:
    """Join non-empty key parts with a separator.

    Args:
        parts: Ordered fragments such as a prefix, scope and function key.
        separator: String placed between fragments.

    Returns:
        The composed key.
    """
    return separator.join(part for part in parts if part)
