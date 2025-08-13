# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import Any, ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.casedb.domain import enum
from gen_epix.common.domain.model.base import Model
from gen_epix.common.domain.model.organization import DataCollection, IdentifierIssuer
from gen_epix.fastapp.domain import Entity, create_links

_SERVICE_TYPE = enum.ServiceType.SUBJECT
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class Subject(Model):
    """
    Represents a person context bound to a particular data collection.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="subjects",
        table_name="subject",
        persistable=True,
        links=create_links(
            {
                1: ("data_collection_id", DataCollection, "data_collection"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection"
    )
    external_ids: dict[IdentifierIssuer, str] | None = Field(
        default=None, description="A dictionary of external identifiers for the subject"
    )
    content: dict[str, Any] = Field(
        description="A dictionary containing the content of the subject"
    )


class SubjectIdentifier(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="subject_identifiers",
        table_name="subject_identifier",
        persistable=True,
        links=create_links(
            {
                1: ("subject_id", Subject, "subject"),
                2: ("identifier_issuer_id", IdentifierIssuer, "identifier_issuer"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    subject_id: UUID = Field(description="The ID of the subject. FOREIGN KEY")
    subject: Subject | None = Field(default=None, description="The subject")
    identifier_issuer_id: UUID = Field(
        description="The ID of the identifier issuer. FOREIGN KEY"
    )
    identifier_issuer: IdentifierIssuer | None = Field(
        default=None, description="The identifier issuer"
    )
    identifier: str = Field(description="The identifier")
