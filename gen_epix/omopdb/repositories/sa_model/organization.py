# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import datetime
from typing import Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from gen_epix.omopdb.domain import enum, model
from gen_epix.omopdb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.omopdb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.ORGANIZATION.value)


class User(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.User)

    email: Mapped[str] = create_mapped_column(model.User, "email")
    name: Mapped[str | None] = create_mapped_column(model.User, "name")
    is_active: Mapped[bool] = create_mapped_column(model.User, "is_active")
    roles: Mapped[set[enum.Role]] = create_mapped_column(model.User, "roles")
    data_collection_ids: Mapped[set[UUID]] = create_mapped_column(
        model.User, "data_collection_ids"
    )


class UserInvitation(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.UserInvitation)

    email: Mapped[str] = create_mapped_column(model.UserInvitation, "email")
    token: Mapped[str] = create_mapped_column(model.UserInvitation, "token")
    expires_at: Mapped[datetime.datetime] = create_mapped_column(
        model.UserInvitation, "expires_at"
    )
    roles: Mapped[set[enum.Role]] = create_mapped_column(model.UserInvitation, "roles")
    data_collection_ids: Mapped[set[UUID]] = create_mapped_column(
        model.UserInvitation, "data_collection_ids"
    )
    invited_by_user_id: Mapped[UUID] = create_mapped_column(
        model.UserInvitation, "invited_by_user_id"
    )


class IdentifierIssuer(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.IdentifierIssuer)

    name: Mapped[str] = create_mapped_column(model.IdentifierIssuer, "name")


class DataCollection(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollection)

    name: Mapped[str] = create_mapped_column(model.DataCollection, "name")
    description: Mapped[str | None] = create_mapped_column(
        model.DataCollection, "description"
    )


class DataCollectionSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollectionSet)

    name: Mapped[str] = create_mapped_column(model.DataCollectionSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        model.DataCollectionSet, "description"
    )


class DataCollectionSetMember(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollectionSetMember)

    data_collection_set_id: Mapped[UUID] = create_mapped_column(
        model.DataCollectionSetMember, "data_collection_set_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        model.DataCollectionSetMember, "data_collection_id"
    )
