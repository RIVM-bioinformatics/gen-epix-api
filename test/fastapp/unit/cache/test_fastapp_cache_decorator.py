"""Tests for the cached callables produced by a region decorator."""

import asyncio

import pytest

from gen_epix.fastapp.cache.key import KeySpec
from gen_epix.fastapp.cache.model import NO_VALUE, RegionConfig
from gen_epix.fastapp.cache.region import CacheRegion


@pytest.fixture(name="region")
def fixture_region() -> CacheRegion:
    """Return a region with a generous time to live."""
    return CacheRegion(RegionConfig(name="test", ttl=1000.0))


def test_repeated_calls_run_the_function_once(region: CacheRegion) -> None:
    """A decorated function is memoized on its arguments."""
    calls: list[int] = []

    @region.cache_on_arguments()
    def load(case_id: int) -> str:
        """Count invocations and return a value."""
        calls.append(case_id)
        return f"case-{case_id}"

    assert load(1) == "case-1"
    assert load(1) == "case-1"
    assert load(2) == "case-2"
    assert calls == [1, 2]


def test_invalidate_removes_one_argument_combination(region: CacheRegion) -> None:
    """A writer can drop exactly the entry that became wrong."""
    calls: list[int] = []

    @region.cache_on_arguments()
    def load(case_id: int) -> int:
        """Count invocations and return the argument."""
        calls.append(case_id)
        return case_id

    load(1)
    load(2)

    load.invalidate(1)

    load(1)
    load(2)
    assert calls == [1, 2, 1]


def test_invalidate_all_removes_every_entry_of_that_function(
    region: CacheRegion,
) -> None:
    """Bulk invalidation must work without enumerating keys."""
    calls: list[int] = []

    @region.cache_on_arguments()
    def load(case_id: int) -> int:
        """Count invocations and return the argument."""
        calls.append(case_id)
        return case_id

    @region.cache_on_arguments()
    def other(case_id: int) -> int:
        """Count invocations and return the argument."""
        calls.append(100 + case_id)
        return case_id

    load(1)
    load(2)
    other(1)

    load.invalidate_all()

    load(1)
    other(1)
    assert calls == [1, 2, 101, 1]


def test_a_tag_invalidates_across_functions(region: CacheRegion) -> None:
    """Two views of the same object are dropped by one tag."""
    calls: list[str] = []

    @region.cache_on_arguments(tags=("case:{case_id}",))
    def summary(case_id: int) -> str:
        """Count invocations and return a value."""
        calls.append("summary")
        return "s"

    @region.cache_on_arguments(tags=("case:{case_id}",))
    def detail(case_id: int) -> str:
        """Count invocations and return a value."""
        calls.append("detail")
        return "d"

    summary(1)
    detail(1)

    region.invalidate_tags("case:1")

    summary(1)
    detail(1)
    assert calls == ["summary", "detail", "summary", "detail"]


def test_set_publishes_a_value_without_calling_the_function(
    region: CacheRegion,
) -> None:
    """A writer that knows the new value can avoid the miss a delete causes."""
    calls: list[int] = []

    @region.cache_on_arguments()
    def load(case_id: int) -> str:
        """Count invocations and return a value."""
        calls.append(case_id)
        return "computed"

    load.set("published", 1)

    assert load(1) == "published"
    assert calls == []


def test_refresh_recomputes_and_stores(region: CacheRegion) -> None:
    """Refreshing avoids the window in which nothing is cached."""
    calls: list[int] = []

    @region.cache_on_arguments()
    def load(case_id: int) -> int:
        """Count invocations and return the invocation number."""
        calls.append(case_id)
        return len(calls)

    load(1)

    assert load.refresh(1) == 2
    assert load(1) == 2


def test_original_bypasses_the_cache_in_both_directions(
    region: CacheRegion,
) -> None:
    """A caller must be able to force a read through to the origin."""
    calls: list[int] = []

    @region.cache_on_arguments()
    def load(case_id: int) -> int:
        """Count invocations and return the invocation number."""
        calls.append(case_id)
        return len(calls)

    load(1)

    assert load.original(1) == 2
    assert load(1) == 1


def test_get_reports_a_miss_without_computing(region: CacheRegion) -> None:
    """Inspecting the cache must not populate it."""
    calls: list[int] = []

    @region.cache_on_arguments()
    def load(case_id: int) -> str:
        """Count invocations and return a value."""
        calls.append(case_id)
        return "value"

    assert load.get(1) is NO_VALUE
    load(1)

    assert load.get(1) == "value"
    assert calls == [1]


def test_a_condition_bypasses_the_cache_for_selected_calls(
    region: CacheRegion,
) -> None:
    """Some arguments are not worth caching, and must not be stored either."""
    calls: list[int] = []

    @region.cache_on_arguments(condition=lambda case_id: case_id > 0)
    def load(case_id: int) -> int:
        """Count invocations and return the invocation number."""
        calls.append(case_id)
        return len(calls)

    load(-1)
    load(-1)
    load(1)
    load(1)

    assert calls == [-1, -1, 1]


def test_a_key_template_narrows_what_participates_in_the_key(
    region: CacheRegion,
) -> None:
    """A parameter that must not affect a hit is kept out of the key."""
    calls: list[int] = []

    @region.cache_on_arguments(key_spec=KeySpec(template="case:{case_id}"))
    def load(case_id: int, unit_of_work: object = None) -> int:
        """Count invocations and return the argument."""
        calls.append(case_id)
        return case_id

    load(1, object())
    load(1, object())

    assert calls == [1]


def test_a_writer_can_reproduce_the_key_of_a_reader(region: CacheRegion) -> None:
    """The inverse handle is what removes the need to duplicate key logic."""

    @region.cache_on_arguments(key_spec=KeySpec(template="case:{case_id}"))
    def load(case_id: int) -> int:
        """Return the argument."""
        return case_id

    assert load.key(1).endswith("case:1")
    assert load.tags(1) == frozenset({load.function_tag})


def test_a_cached_method_shares_entries_across_instances(
    region: CacheRegion,
) -> None:
    """The receiver is excluded from the key unless the caller adds it."""
    calls: list[int] = []

    class Service:
        """Service whose reads are cached."""

        @region.cache_on_arguments()
        def load(self, case_id: int) -> int:
            """Count invocations and return the argument."""
            calls.append(case_id)
            return case_id

    first = Service()
    second = Service()

    first.load(1)
    second.load(1)

    assert calls == [1]


def test_a_cached_method_can_be_invalidated_through_an_instance(
    region: CacheRegion,
) -> None:
    """Binding must reach the same entry the call created."""
    calls: list[int] = []

    class Service:
        """Service whose reads are cached."""

        @region.cache_on_arguments()
        def load(self, case_id: int) -> int:
            """Count invocations and return the argument."""
            calls.append(case_id)
            return case_id

    service = Service()
    service.load(1)

    service.load.invalidate(1)

    service.load(1)
    assert calls == [1, 1]


def test_a_coroutine_function_is_cached_and_invalidated_the_same_way(
    region: CacheRegion,
) -> None:
    """Async callers need the same handles as synchronous ones."""
    calls: list[int] = []

    @region.cache_on_arguments()
    async def load(case_id: int) -> str:
        """Count invocations and return a value."""
        calls.append(case_id)
        return f"case-{case_id}"

    async def scenario() -> list[str]:
        """Read twice, invalidate, then read again."""
        first = await load(1)
        second = await load(1)
        load.invalidate(1)
        third = await load(1)
        return [first, second, third]

    assert asyncio.run(scenario()) == ["case-1"] * 3
    assert calls == [1, 1]


def test_concurrent_awaits_run_the_coroutine_once(region: CacheRegion) -> None:
    """An awaited loader must not be started once per waiting task."""
    calls: list[int] = []

    @region.cache_on_arguments()
    async def load(case_id: int) -> str:
        """Count invocations after yielding to the event loop."""
        calls.append(case_id)
        await asyncio.sleep(0.01)
        return "value"

    async def scenario() -> list[str]:
        """Await the same key from four concurrent tasks."""
        return list(await asyncio.gather(*(load(1) for _ in range(4))))

    assert asyncio.run(scenario()) == ["value"] * 4
    assert calls == [1]


def test_the_wrapper_keeps_the_identity_of_the_function(
    region: CacheRegion,
) -> None:
    """Introspection and documentation tooling must still work."""

    @region.cache_on_arguments()
    def load(case_id: int) -> int:
        """Return the argument."""
        return case_id

    assert load.__name__ == "load"
    assert load.__doc__ == "Return the argument."
    assert load.cache_info().requests == 0
