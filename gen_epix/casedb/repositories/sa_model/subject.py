# pylint: disable=too-few-public-methods
from __future__ import (
    annotations,  # Resolves pylint not recognizing Mapped as subscriptable
)

from typing import Any
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped

from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)

Base: type = orm.declarative_base(name=enum.ServiceType.SUBJECT.value)


class Subject(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.Subject)

    data_collection_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Subject, "data_collection_id"
    )
    external_identifiers: Mapped[dict[UUID, str] | None] = create_mapped_column(
        DOMAIN, model.Subject, "external_identifiers"
    )
    content: Mapped[dict[str, Any]] = create_mapped_column(
        DOMAIN, model.Subject, "content"
    )


class SubjectIdentifier(Base, RowMetadataMixin):
    """
    SQLAlchemy model for the corresponding persistable domain model.
    """

    __tablename__, __table_args__ = create_table_args(model.SubjectIdentifier)

    subject_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SubjectIdentifier, "subject_id"
    )
    identifier_issuer_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SubjectIdentifier, "identifier_issuer_id"
    )
    identifier: Mapped[str] = create_mapped_column(
        DOMAIN, model.SubjectIdentifier, "identifier"
    )
