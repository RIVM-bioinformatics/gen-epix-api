"""Utilities for the fastapp link module."""

from pydantic import BaseModel


class MultiLink(BaseModel, frozen=True):
    """
    Represents a link between entities, whereby the linking entity can be associated
    with multiple instances of the linked entity.

    Attributes:
    ----------
    link_field_name : str
        The name of the field that represents the link.
    link_model_class : type[BaseModel]
        The model class that the link points to.
    """

    link_field_name: str
    link_model_class: type[BaseModel]

    def to_tuple(self) -> tuple[str, type[BaseModel]]:
        """Perform the to tuple operation."""
        return (self.link_field_name, self.link_model_class)

    @classmethod
    def from_tuple(cls, tuple_: tuple[str, type[BaseModel]]) -> "MultiLink":
        """Perform the from tuple operation."""
        return cls(link_field_name=tuple_[0], link_model_class=tuple_[1])


class Link(BaseModel, frozen=True):
    """
    Represents a link between entities.

    Attributes:
    ----------
    link_field_name : str
        The name of the field that represents the link.
    link_model_class : type[BaseModel]
        The model class that the link points to.
    relationship_field_name : str, optional
        The name of the field used for back-population, by default None.

    Methods:
    -------
    None
    """

    link_field_name: str
    link_model_class: type[BaseModel]
    relationship_field_name: str | None = None

    def to_tuple(self) -> tuple[str, type[BaseModel], str | None]:
        """Perform the to tuple operation."""
        return (
            self.link_field_name,
            self.link_model_class,
            self.relationship_field_name,
        )

    @classmethod
    def from_tuple(cls, tuple_: tuple[str, type[BaseModel], str | None]) -> "Link":
        """Perform the from tuple operation."""
        return cls(
            link_field_name=tuple_[0],
            link_model_class=tuple_[1],
            relationship_field_name=tuple_[2],
        )
