"""Relationship metadata for domain models."""

from pydantic import BaseModel


class MultiLink(BaseModel, frozen=True):
    """Describe a field that relates a model to multiple instances of another model."""

    link_field_name: str
    link_model_class: type[BaseModel]

    def to_tuple(self) -> tuple[str, type[BaseModel]]:
        """Return the tuple representation accepted by ``from_tuple``."""
        return (self.link_field_name, self.link_model_class)

    @classmethod
    def from_tuple(cls, tuple_: tuple[str, type[BaseModel]]) -> "MultiLink":
        """Create a multi-link from its tuple representation."""
        return cls(link_field_name=tuple_[0], link_model_class=tuple_[1])


class Link(BaseModel, frozen=True):
    """Describe a field that relates a model to another model."""

    link_field_name: str
    link_model_class: type[BaseModel]
    relationship_field_name: str | None = None

    def to_tuple(self) -> tuple[str, type[BaseModel], str | None]:
        """Return the tuple representation accepted by ``from_tuple``."""
        return (
            self.link_field_name,
            self.link_model_class,
            self.relationship_field_name,
        )

    @classmethod
    def from_tuple(cls, tuple_: tuple[str, type[BaseModel], str | None]) -> "Link":
        """Create a link from its tuple representation."""
        return cls(
            link_field_name=tuple_[0],
            link_model_class=tuple_[1],
            relationship_field_name=tuple_[2],
        )
