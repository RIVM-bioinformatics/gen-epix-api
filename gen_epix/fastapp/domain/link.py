from typing import Type

from pydantic import BaseModel


class Link(BaseModel, frozen=True):
    """
    Represents a link between entities.

    Attributes
    ----------
    link_field_name : str
        The name of the field that represents the link.
    link_model_class : Type[BaseModel]
        The model class that the link points to.
    relationship_field_name : str, optional
        The name of the field used for back-population, by default None.

    Methods
    -------
    None
    """

    link_field_name: str
    link_model_class: Type[BaseModel]
    relationship_field_name: str | None = None

    def to_tuple(self) -> tuple[str, Type[BaseModel], str | None]:
        return (
            self.link_field_name,
            self.link_model_class,
            self.relationship_field_name,
        )

    @classmethod
    def from_tuple(cls, tuple_: tuple[str, Type[BaseModel], str | None]) -> "Link":
        return cls(
            link_field_name=tuple_[0],
            link_model_class=tuple_[1],
            relationship_field_name=tuple_[2],
        )
