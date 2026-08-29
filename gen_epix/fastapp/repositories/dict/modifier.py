"""Mutation helpers for dictionary-backed repositories."""

import abc
from collections.abc import Hashable

from gen_epix.fastapp.model import Model


class BaseDictModelModifier(abc.ABC):
    """
    Hook applied to model objects before they are stored in DictRepository.

    Register per model class via DictRepository.register_model_modifier().
    Analogous to SAMapper's dump()/update() for the dict backend: the fastapp
    layer knows nothing about which fields are touched — that logic lives in
    the db-layer subclass (e.g. CommondbDictModelModifier).
    """

    @abc.abstractmethod
    def on_create(self, user_id: Hashable | None, obj: Model) -> None:
        """
        Mutate obj in-place just after it has been copied for storage.

        Called before the copy is inserted into the dict.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def on_update(
        self, user_id: Hashable | None, obj: Model, stored_obj: Model
    ) -> None:
        """
        Mutate obj in-place before its field values are applied to stored_obj.

        stored_obj holds the current stored state and may be read but not written.
        """
        raise NotImplementedError()
