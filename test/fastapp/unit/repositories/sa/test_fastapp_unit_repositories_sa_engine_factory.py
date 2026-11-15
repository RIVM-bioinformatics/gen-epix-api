"""Verify stable engine cache keys for nested DBAPI connect arguments."""

from gen_epix.fastapp.repositories.sa.engine_factory import EngineFactory


def test_compose_key_accepts_nested_connect_argument_mappings() -> None:
    """Hash equivalent nested connect arguments regardless of mapping order."""
    first = EngineFactory._compose_key(
        "driver://database",
        connect_args={"attrs_before": {1: b"one", 2: b"two"}},
    )
    second = EngineFactory._compose_key(
        "driver://database",
        connect_args={"attrs_before": {2: b"two", 1: b"one"}},
    )

    assert first == second
    assert hash(first)
