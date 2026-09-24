"""Tests for cache key composition."""

import pytest

from gen_epix.fastapp.cache.exc import CacheConfigurationError
from gen_epix.fastapp.cache.key import (
    KeySpec,
    arg_key_generator,
    bind_arguments,
    compose_key,
    function_namespace,
    kwarg_key_generator,
    length_conditional_mangler,
    sha256_mangle_key,
)


def sample(case_id: int, verbose: bool = False, unit_of_work: object = None) -> str:
    """Sample function used as a key-generation target."""
    return f"{case_id}-{verbose}-{unit_of_work}"


class Holder:
    """Class used to check that the receiver is excluded from keys."""

    def method(self, case_id: int) -> int:
        """Sample method used as a key-generation target."""
        return case_id


def test_keyword_and_positional_calls_share_one_key() -> None:
    """Binding against the signature collapses equivalent call forms."""
    generate = kwarg_key_generator("ns", sample)

    assert generate(1) == generate(case_id=1)
    assert generate(1, False) == generate(1)
    assert generate(1) != generate(2)


def test_positional_generator_rejects_keyword_arguments() -> None:
    """The positional generator cannot represent keyword calls unambiguously."""
    generate = arg_key_generator("ns", sample)

    assert generate(1) != generate(2)
    with pytest.raises(ValueError):
        generate(case_id=1)


def test_excluded_parameter_does_not_change_the_key() -> None:
    """A parameter listed in exclude is kept out of the key."""
    generate = KeySpec(exclude=("unit_of_work",)).build(sample)

    assert generate(1, False, object()) == generate(1, False, object())
    assert generate(1, True, None) != generate(1, False, None)


def test_included_parameters_are_the_only_ones_that_matter() -> None:
    """An include list narrows the key to the named parameters."""
    generate = KeySpec(include=("case_id",)).build(sample)

    assert generate(1, True, None) == generate(1, False, object())


def test_include_and_exclude_together_are_rejected() -> None:
    """Combining include and exclude is ambiguous and refused."""
    with pytest.raises(CacheConfigurationError):
        KeySpec(include=("case_id",), exclude=("verbose",)).build(sample)


def test_unknown_parameter_names_are_rejected() -> None:
    """Naming a parameter that does not exist would silently widen the key."""
    with pytest.raises(CacheConfigurationError):
        KeySpec(exclude=("missing",)).build(sample)
    with pytest.raises(CacheConfigurationError):
        KeySpec(template="x:{missing}").build(sample)


def test_template_keys_use_only_the_named_parameters() -> None:
    """A template names exactly what participates in the key."""
    generate = KeySpec(template="case:{case_id}").build(sample)

    assert generate(1, True, object()).endswith("case:1")
    assert generate(1, False, None) == generate(1, True, object())


def test_positional_templates_are_rejected() -> None:
    """Positional template fields cannot be mapped back to parameters."""
    with pytest.raises(CacheConfigurationError):
        KeySpec(template="case:{0}").build(sample)


def test_receiver_is_excluded_from_method_keys() -> None:
    """Two instances of the same class produce the same method key."""
    generate = KeySpec().build(Holder.method)

    assert generate(Holder(), 1) == generate(Holder(), 1)


def test_bind_arguments_applies_defaults_and_drops_the_receiver() -> None:
    """Tag templates need every parameter by name, defaults included."""
    assert bind_arguments(sample, (1,), {}) == {
        "case_id": 1,
        "verbose": False,
        "unit_of_work": None,
    }
    assert "self" not in bind_arguments(Holder.method, (Holder(), 1), {})


def test_bind_arguments_rejects_a_call_that_does_not_match() -> None:
    """A mismatched call cannot produce a meaningful key."""
    with pytest.raises(TypeError):
        bind_arguments(sample, (), {})


def test_namespace_distinguishes_same_named_functions() -> None:
    """The namespace disambiguates functions the decorator cannot tell apart."""
    assert function_namespace(sample) != function_namespace(sample, "other")


def test_manglers_bound_key_length_only_when_needed() -> None:
    """Short keys stay readable while long keys are digested."""
    mangle = length_conditional_mangler(10)

    assert mangle("short") == "short"
    assert mangle("x" * 50) == sha256_mangle_key("x" * 50)
    assert len(sha256_mangle_key("x" * 50)) == 64


def test_compose_key_skips_empty_parts() -> None:
    """An absent prefix or scope must not leave a dangling separator."""
    assert compose_key(("", "region", "g0", "", "key")) == "region:g0:key"
