# pylint: disable=too-few-public-methods


from typing import Any, Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.casedb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.SUBJECT.value)


class Subject(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Subject)

    data_collection_id: Mapped[UUID] = create_mapped_column(
        model.Subject, "data_collection_id"
    )
    external_ids: Mapped[dict[UUID, str] | None] = create_mapped_column(
        model.Subject, "external_ids"
    )
    content: Mapped[dict[str, Any]] = create_mapped_column(model.Subject, "content")


class SubjectIdentifier(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SubjectIdentifier)

    subject_id: Mapped[UUID] = create_mapped_column(
        model.SubjectIdentifier, "subject_id"
    )
    identifier_issuer_id: Mapped[UUID] = create_mapped_column(
        model.SubjectIdentifier, "identifier_issuer_id"
    )
    identifier: Mapped[str] = create_mapped_column(
        model.SubjectIdentifier, "identifier"
    )
