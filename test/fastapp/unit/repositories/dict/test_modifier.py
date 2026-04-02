"""
Unit tests for BaseDictModelModifier.

Verifies that:
- BaseDictModelModifier cannot be instantiated directly (ABC contract).
- A concrete subclass must implement on_create and on_update.
- on_create and on_update are called with the correct arguments by DictRepository.
"""

from typing import Any
from unittest import TestCase
from uuid import uuid4

import pytest

from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.dict.modifier import BaseDictModelModifier


class _ConcreteModifier(BaseDictModelModifier):
    """Minimal concrete modifier that records calls for assertion."""

    def __init__(self) -> None:
        self.create_calls: list[tuple[Any, Any]] = []
        self.update_calls: list[tuple[Any, Any, Any]] = []

    def on_create(self, user_id: Any, obj: Model) -> None:
        self.create_calls.append((user_id, obj))

    def on_update(self, user_id: Any, obj: Model, stored_obj: Model) -> None:
        self.update_calls.append((user_id, obj, stored_obj))


@pytest.mark.scenario_ids("TC-SEC-28-03")
class TestBaseDictModelModifier(TestCase):
    def test_cannot_instantiate_abstract_class(self) -> None:
        # 1. Input / 2. Mocks (none)

        # 3. Execute / 4. Verify
        with pytest.raises(TypeError):
            BaseDictModelModifier()  # type: ignore[abstract]

    def test_concrete_subclass_can_be_instantiated(self) -> None:
        # 1. Input / 2. Mocks (none)

        # 3. Execute
        modifier = _ConcreteModifier()

        # 4. Verify
        assert isinstance(modifier, BaseDictModelModifier)

    def test_on_create_calrled_with_user_id_and_obj(self) -> None:
        # 1. Input
        modifier = _ConcreteModifier()
        user_id = uuid4()

        class _M(Model):
            pass

        obj = _M()

        # 2. Mocks (none)

        # 3. Execute
        modifier.on_create(user_id, obj)

        # 4. Verify
        assert len(modifier.create_calls) == 1
        assert modifier.create_calls[0] == (user_id, obj)

    def test_on_update_called_with_user_id_obj_and_stored_obj(self) -> None:
        # 1. Input
        modifier = _ConcreteModifier()
        user_id = uuid4()

        class _M(Model):
            pass

        obj = _M()
        stored_obj = _M()

        # 2. Mocks (none)

        # 3. Execute
        modifier.on_update(user_id, obj, stored_obj)

        # 4. Verify
        assert len(modifier.update_calls) == 1
        assert modifier.update_calls[0] == (user_id, obj, stored_obj)
