"""Test selective dictionary clearing and restoration after failures."""

from collections.abc import Hashable

import pytest

from gen_epix.commondb.repositories.operational_data import (
    delete_dict_operational_data,
)
from gen_epix.fastapp import Model


class FirstModel(Model):
    """Represent the first resettable table in focused tests."""

    value: str


class SecondModel(Model):
    """Represent another resettable table in focused tests."""

    value: str


class MissingModel(Model):
    """Represent a model without a registered table."""

    value: str


def test_delete_selected_tables_in_place_from_iterable() -> None:
    """Clear duplicate selections while retaining table identity and other data."""
    first_record = FirstModel(value="first")
    second_record = SecondModel(value="second")
    first_table = {1: first_record}
    second_table = {2: second_record}
    db: dict[type[Model], dict[Hashable, Model]] = {
        FirstModel: first_table,
        SecondModel: second_table,
    }

    delete_dict_operational_data(db, iter([FirstModel, FirstModel]))

    assert db[FirstModel] is first_table
    assert not first_table
    assert db[SecondModel] is second_table
    assert second_table == {2: second_record}


def test_delete_with_empty_model_iterable_is_noop() -> None:
    """Leave every table untouched when no models are selected."""
    first_record = FirstModel(value="first")
    table = {1: first_record}
    db: dict[type[Model], dict[Hashable, Model]] = {FirstModel: table}

    delete_dict_operational_data(db, iter(()))

    assert db[FirstModel] is table
    assert table == {1: first_record}


def test_missing_table_fails_before_any_table_is_cleared() -> None:
    """Reject a missing table before mutating an earlier selected table."""
    first_record = FirstModel(value="first")
    table = {1: first_record}
    db: dict[type[Model], dict[Hashable, Model]] = {FirstModel: table}

    with pytest.raises(KeyError):
        delete_dict_operational_data(db, [FirstModel, MissingModel])

    assert db[FirstModel] is table
    assert table == {1: first_record}


def test_clear_failure_restores_all_table_contents() -> None:
    """Restore prior contents and propagate a failure after partial clearing."""

    class FailingTable(dict[Hashable, Model]):
        """Clear partially before raising to exercise rollback."""

        def clear(self) -> None:
            """Empty the table and raise a representative failure."""
            super().clear()
            raise RuntimeError("clear failed after mutation")

    first_record = FirstModel(value="first")
    second_record = SecondModel(value="second")
    first_table = {1: first_record}
    failing_table = FailingTable({2: second_record})
    db: dict[type[Model], dict[Hashable, Model]] = {
        FirstModel: first_table,
        SecondModel: failing_table,
    }

    with pytest.raises(RuntimeError, match="clear failed after mutation"):
        delete_dict_operational_data(db, [FirstModel, SecondModel])

    assert db[FirstModel] is first_table
    assert first_table == {1: first_record}
    assert db[SecondModel] is failing_table
    assert failing_table == {2: second_record}
