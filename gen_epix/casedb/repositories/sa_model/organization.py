# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import datetime
from typing import Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.casedb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.ORGANIZATION.value)


class Organization(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Organization)

    name: Mapped[str] = create_mapped_column(model.Organization, "name")
    legal_entity_code: Mapped[str] = create_mapped_column(
        model.Organization, "legal_entity_code"
    )
    legal_region_id: Mapped[UUID | None] = create_mapped_column(
        model.Organization, "legal_region_id"
    )


class User(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.User)

    email: Mapped[str] = create_mapped_column(model.User, "email")
    name: Mapped[str | None] = create_mapped_column(model.User, "name")
    is_active: Mapped[bool] = create_mapped_column(model.User, "is_active")
    roles: Mapped[set[enum.Role]] = create_mapped_column(model.User, "roles")
    organization_id: Mapped[UUID] = create_mapped_column(model.User, "organization_id")

    organization: Mapped[Organization] = relationship(
        Organization, foreign_keys=[organization_id]
    )


class OrganizationSet(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationSet)

    name: Mapped[str] = create_mapped_column(model.OrganizationSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        model.OrganizationSet, "description"
    )


class OrganizationSetMember(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationSetMember)

    organization_set_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationSetMember, "organization_set_id"
    )
    organization_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationSetMember, "organization_id"
    )

    organization_set: Mapped[OrganizationSet] = relationship(
        OrganizationSet, foreign_keys=[organization_set_id]
    )
    organization: Mapped[Organization] = relationship(
        Organization, foreign_keys=[organization_id]
    )


class Site(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Site)

    organization_id: Mapped[UUID] = create_mapped_column(model.Site, "organization_id")
    name: Mapped[str] = create_mapped_column(model.Site, "name")
    location_region_id: Mapped[UUID] = create_mapped_column(
        model.Site, "location_region_id"
    )

    organization: Mapped[Organization] = relationship(
        Organization, foreign_keys=[organization_id]
    )


class Contact(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Contact)

    site_id: Mapped[UUID | None] = create_mapped_column(model.Contact, "site_id")
    name: Mapped[str] = create_mapped_column(model.Contact, "name")
    email: Mapped[str | None] = create_mapped_column(model.Contact, "email")
    phone: Mapped[str | None] = create_mapped_column(model.Contact, "phone")

    site: Mapped[Site] = relationship(Site, foreign_keys=[site_id])


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

    data_collection_set: Mapped[DataCollectionSet] = relationship(
        DataCollectionSet, foreign_keys=[data_collection_set_id]
    )
    data_collection: Mapped[DataCollection] = relationship(
        DataCollection, foreign_keys=[data_collection_id]
    )


class DataCollectionRelation(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollectionRelation)

    from_data_collection_id: Mapped[UUID] = create_mapped_column(
        model.DataCollectionRelation, "from_data_collection_id"
    )
    to_data_collection_id: Mapped[UUID] = create_mapped_column(
        model.DataCollectionRelation, "to_data_collection_id"
    )
    share_case: Mapped[bool] = create_mapped_column(
        model.DataCollectionRelation, "share_case"
    )

    from_data_collection: Mapped[DataCollection] = relationship(
        DataCollection, foreign_keys=[from_data_collection_id]
    )
    to_data_collection: Mapped[DataCollection] = relationship(
        DataCollection, foreign_keys=[to_data_collection_id]
    )


class UserInvitation(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.UserInvitation)

    email: Mapped[str] = create_mapped_column(model.UserInvitation, "email")
    token: Mapped[str] = create_mapped_column(model.UserInvitation, "token")
    expires_at: Mapped[datetime.datetime] = create_mapped_column(
        model.UserInvitation, "expires_at"
    )
    roles: Mapped[set[enum.Role]] = create_mapped_column(model.UserInvitation, "roles")
    invited_by_user_id: Mapped[UUID] = create_mapped_column(
        model.UserInvitation, "invited_by_user_id"
    )
    organization_id: Mapped[UUID] = create_mapped_column(
        model.UserInvitation, "organization_id"
    )

    invited_by_user: Mapped[User] = relationship(
        User, foreign_keys=[invited_by_user_id]
    )
    organization: Mapped[Organization] = relationship(
        Organization, foreign_keys=[organization_id]
    )
