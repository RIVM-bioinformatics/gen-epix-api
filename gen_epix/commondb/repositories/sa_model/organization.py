import datetime
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, declarative_mixin, declared_attr, relationship

from gen_epix.commondb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: type = orm.declarative_base(name=enum.ServiceType.ORGANIZATION.value)


@declarative_mixin
class OrganizationMixin(RowMetadataMixin):
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Organization, "name")
    legal_entity_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.Organization, "legal_entity_code"
    )


@declarative_mixin
class UserMixin(RowMetadataMixin):
    key: Mapped[str] = create_mapped_column(DOMAIN, model.User, "key")
    email: Mapped[str | None] = create_mapped_column(DOMAIN, model.User, "email")
    name: Mapped[str | None] = create_mapped_column(DOMAIN, model.User, "name")
    is_active: Mapped[bool] = create_mapped_column(DOMAIN, model.User, "is_active")
    roles: Mapped[set[str]] = create_mapped_column(DOMAIN, model.User, "roles")

    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        return create_mapped_column(DOMAIN, model.User, "organization_id")

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        return relationship("Organization", foreign_keys="User.organization_id")


@declarative_mixin
class OrganizationSetMixin(RowMetadataMixin):
    name: Mapped[str] = create_mapped_column(DOMAIN, model.OrganizationSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.OrganizationSet, "description"
    )


@declarative_mixin
class OrganizationSetMemberMixin(RowMetadataMixin):
    @declared_attr
    def organization_set_id(cls) -> Mapped[UUID]:
        return create_mapped_column(
            DOMAIN, model.OrganizationSetMember, "organization_set_id"
        )

    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        return create_mapped_column(
            DOMAIN, model.OrganizationSetMember, "organization_id"
        )

    @declared_attr
    def organization_set(cls) -> Mapped[model.OrganizationSet]:
        return relationship(
            "OrganizationSet",
            foreign_keys="OrganizationSetMember.organization_set_id",
        )

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        return relationship(
            "Organization", foreign_keys="OrganizationSetMember.organization_id"
        )


@declarative_mixin
class SiteMixin(RowMetadataMixin):
    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        return create_mapped_column(DOMAIN, model.Site, "organization_id")

    name: Mapped[str] = create_mapped_column(DOMAIN, model.Site, "name")

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        return relationship("Organization", foreign_keys="Site.organization_id")


@declarative_mixin
class ContactMixin(RowMetadataMixin):
    @declared_attr
    def site_id(cls) -> Mapped[UUID | None]:
        return create_mapped_column(DOMAIN, model.Contact, "site_id")

    name: Mapped[str] = create_mapped_column(DOMAIN, model.Contact, "name")
    email: Mapped[str | None] = create_mapped_column(DOMAIN, model.Contact, "email")
    phone: Mapped[str | None] = create_mapped_column(DOMAIN, model.Contact, "phone")

    @declared_attr
    def site(cls) -> Mapped[SiteMixin | None]:
        return relationship("Site", foreign_keys="Contact.site_id")


@declarative_mixin
class DataCollectionMixin(RowMetadataMixin):
    name: Mapped[str] = create_mapped_column(DOMAIN, model.DataCollection, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DataCollection, "description"
    )


@declarative_mixin
class DataCollectionSetMixin(RowMetadataMixin):
    name: Mapped[str] = create_mapped_column(DOMAIN, model.DataCollectionSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DataCollectionSet, "description"
    )


@declarative_mixin
class DataCollectionSetMemberMixin(RowMetadataMixin):
    @declared_attr
    def data_collection_set_id(cls) -> Mapped[UUID]:
        return create_mapped_column(
            DOMAIN,
            model.DataCollectionSetMember,
            "data_collection_set_id",
        )

    @declared_attr
    def data_collection_id(cls) -> Mapped[UUID]:
        return create_mapped_column(
            DOMAIN,
            model.DataCollectionSetMember,
            "data_collection_id",
        )

    @declared_attr
    def data_collection_set(cls) -> Mapped[DataCollectionSetMixin]:
        return relationship(
            "DataCollectionSet",
            foreign_keys="DataCollectionSetMember.data_collection_set_id",
        )

    @declared_attr
    def data_collection(cls) -> Mapped[DataCollectionMixin]:
        return relationship(
            "DataCollection", foreign_keys="DataCollectionSetMember.data_collection_id"
        )


@declarative_mixin
class UserInvitationMixin(RowMetadataMixin):
    key: Mapped[str] = create_mapped_column(DOMAIN, model.UserInvitation, "key")
    email: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UserInvitation, "email"
    )
    name: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UserInvitation, "name"
    )
    token: Mapped[str] = create_mapped_column(DOMAIN, model.UserInvitation, "token")
    expires_at: Mapped[datetime.datetime] = create_mapped_column(
        DOMAIN, model.UserInvitation, "expires_at"
    )
    roles: Mapped[set[str]] = create_mapped_column(
        DOMAIN, model.UserInvitation, "roles"
    )

    @declared_attr
    def invited_by_user_id(cls) -> Mapped[UUID]:
        return create_mapped_column(DOMAIN, model.UserInvitation, "invited_by_user_id")

    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        return create_mapped_column(DOMAIN, model.UserInvitation, "organization_id")

    @declared_attr
    def invited_by_user(cls) -> Mapped[UserMixin]:
        return relationship("User", foreign_keys="UserInvitation.invited_by_user_id")

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        return relationship(
            "Organization", foreign_keys="UserInvitation.organization_id"
        )


@declarative_mixin
class IdentifierIssuerMixin(RowMetadataMixin):
    code: Mapped[str] = create_mapped_column(DOMAIN, model.IdentifierIssuer, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.IdentifierIssuer, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.IdentifierIssuer, "description"
    )


@declarative_mixin
class OrganizationIdentifierIssuerLinkMixin(RowMetadataMixin):
    organization_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.OrganizationIdentifierIssuerLink, "organization_id"
    )
    identifier_issuer_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.OrganizationIdentifierIssuerLink, "identifier_issuer_id"
    )


class Organization(Base, OrganizationMixin):
    __tablename__, __table_args__ = create_table_args(model.Organization)


class User(Base, UserMixin):
    __tablename__, __table_args__ = create_table_args(model.User)


class OrganizationSet(Base, OrganizationSetMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationSet)


class OrganizationSetMember(Base, OrganizationSetMemberMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationSetMember)


class Site(Base, SiteMixin):
    __tablename__, __table_args__ = create_table_args(model.Site)


class Contact(Base, ContactMixin):
    __tablename__, __table_args__ = create_table_args(model.Contact)


class DataCollection(Base, DataCollectionMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollection)


class DataCollectionSet(Base, DataCollectionSetMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollectionSet)


class DataCollectionSetMember(Base, DataCollectionSetMemberMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollectionSetMember)


class UserInvitation(Base, UserInvitationMixin):
    __tablename__, __table_args__ = create_table_args(model.UserInvitation)


class IdentifierIssuer(Base, IdentifierIssuerMixin):
    __tablename__, __table_args__ = create_table_args(model.IdentifierIssuer)


class OrganizationIdentifierIssuerLink(Base, OrganizationIdentifierIssuerLinkMixin):
    __tablename__, __table_args__ = create_table_args(
        model.OrganizationIdentifierIssuerLink
    )
