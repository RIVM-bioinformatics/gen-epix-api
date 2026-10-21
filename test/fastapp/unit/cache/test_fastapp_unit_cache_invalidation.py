"""Tests for cache invalidation requests, delivery, and dependencies."""

from gen_epix.fastapp.cache.clock import ManualClock
from gen_epix.fastapp.cache.enum import InvalidationMode
from gen_epix.fastapp.cache.invalidation import (
    DependencyRegistry,
    Invalidation,
    InvalidationStrategy,
    LocalInvalidationBus,
)


def test_the_invalidation_strategy_separates_hard_from_soft_cut_offs() -> None:
    """Readers distinguish a hard miss from a stale-while-refresh hit."""
    clock = ManualClock()
    strategy = InvalidationStrategy(clock)
    written_at = clock.monotonic()
    clock.advance(1)

    strategy.invalidate(InvalidationMode.SOFT)

    assert strategy.is_soft_invalidated(written_at)
    assert not strategy.is_hard_invalidated(written_at)
    strategy.invalidate(InvalidationMode.HARD)
    assert strategy.is_hard_invalidated(written_at)
    assert not strategy.is_soft_invalidated(written_at)


def test_a_published_request_carries_the_origin_of_the_bus() -> None:
    """A transport can recognize the echo of its own message."""
    bus = LocalInvalidationBus(origin="worker-1")
    received: list[Invalidation] = []
    bus.subscribe(received.append)

    bus.publish(Invalidation.for_tags(["case:1"]))

    assert received[0].origin == "worker-1"


def test_a_forwarded_request_keeps_the_origin_it_arrived_with() -> None:
    """Republishing does not disguise a request's original source."""
    bus = LocalInvalidationBus(origin="worker-1")
    received: list[Invalidation] = []
    bus.subscribe(received.append)
    inbound = Invalidation.for_tags(["case:1"], origin="worker-2")

    bus.publish(inbound)

    assert received[0].origin == "worker-2"
    assert received[0].message_id == inbound.message_id


def test_a_repeated_invalidation_message_is_applied_once() -> None:
    """At-least-once transports may safely redeliver a request."""
    bus = LocalInvalidationBus()
    received: list[Invalidation] = []
    bus.subscribe(received.append)
    message = Invalidation.for_tags(["case:1"])

    assert bus.deliver(message) is True
    assert bus.deliver(message) is False

    assert len(received) == 1


def test_a_failing_subscriber_does_not_block_the_others() -> None:
    """One broken cache tier does not keep other subscribers stale."""
    bus = LocalInvalidationBus()
    received: list[Invalidation] = []

    def explode(invalidation: Invalidation) -> None:
        """Simulate a defective subscriber."""
        raise RuntimeError("subscriber defect")

    bus.subscribe(explode)
    bus.subscribe(received.append)

    bus.publish(Invalidation.for_all())

    assert len(received) == 1


def test_declared_dependencies_translate_a_change_into_invalidations() -> None:
    """Writers name the changed entity, not the caches that depend on it."""
    registry = DependencyRegistry()
    registry.declare("case", tags=("case:{case_id}",))
    registry.declare("case", regions=("reports",))

    invalidations = registry.resolve("case", {"case_id": 7})

    assert {"case:7"} in [invalidation.tags for invalidation in invalidations]
    assert "reports" in [invalidation.region for invalidation in invalidations]
    assert registry.resolve("unknown") == []
