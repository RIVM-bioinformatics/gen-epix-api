import datetime
from collections.abc import Callable, Hashable
from functools import partial
from uuid import UUID

from gen_epix.commondb.domain.model import ModelNoId
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.dict.modifier import BaseDictModelModifier


class CommondbDictModelModifier(BaseDictModelModifier):
    """
    DictRepository modifier for all databases that use RowMetadataMixin.

    Mirrors CommondbSAMapper's create/update semantics for the dict backend:
    - on_create : stamps created_at and modified_at with current time;
                  sets modified_by = user_id.
    - on_update : preserves created_at from the stored object (never overwritten);
                  stamps modified_at with current time;
                  sets modified_by = user_id.
    """

    def __init__(
        self,
        timestamp_factory: Callable[[], datetime.datetime] = partial(
            datetime.datetime.now, datetime.timezone.utc
        ),
    ) -> None:
        self._timestamp_factory = timestamp_factory

    def on_create(self, user_id: Hashable | None, obj: Model) -> None:
        assert user_id is None or isinstance(user_id, UUID)
        assert isinstance(obj, ModelNoId)
        now = self._timestamp_factory()
        obj.created_at = now
        obj.modified_at = now
        obj.modified_by = user_id

    def on_update(
        self, user_id: Hashable | None, obj: Model, stored_obj: Model
    ) -> None:
        assert user_id is None or isinstance(user_id, UUID)
        assert isinstance(obj, ModelNoId)
        assert isinstance(stored_obj, ModelNoId)
        # created_at — never overwritten on update, same rule as CommondbSAMapper
        obj.created_at = stored_obj.created_at
        # modified_at — set current time
        obj.modified_at = self._timestamp_factory()
        # modified_by — always the acting user, overrides any value on the incoming obj
        obj.modified_by = user_id
