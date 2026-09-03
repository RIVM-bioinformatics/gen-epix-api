"""Define SQLAlchemy rows and mixins for commondb organization persistence."""

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
    """Encapsulates SQLAlchemy columns for Organization-derived row models."""

    code: Mapped[str] = create_mapped_column(DOMAIN, model.Organization, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Organization, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Organization, "description"
    )


@declarative_mixin
class UserMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns and organization relationship for user rows."""

    key: Mapped[str] = create_mapped_column(DOMAIN, model.User, "key")
    email: Mapped[str | None] = create_mapped_column(DOMAIN, model.User, "email")
    name: Mapped[str | None] = create_mapped_column(DOMAIN, model.User, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.User, "description"
    )
    is_active: Mapped[bool] = create_mapped_column(DOMAIN, model.User, "is_active")
    roles: Mapped[set[str]] = create_mapped_column(DOMAIN, model.User, "roles")

    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        """Map the user's owning organization ID column."""
        return create_mapped_column(DOMAIN, model.User, "organization_id")

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        """Map the user's owning organization relationship."""
        return relationship("Organization", foreign_keys="User.organization_id")


@declarative_mixin
class OrganizationSetMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns for OrganizationSet-derived row models."""

    name: Mapped[str] = create_mapped_column(DOMAIN, model.OrganizationSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.OrganizationSet, "description"
    )


@declarative_mixin
class OrganizationSetMemberMixin(RowMetadataMixin):
    """Encapsulates columns and relationships for organization-set membership rows."""

    @declared_attr
    def organization_set_id(cls) -> Mapped[UUID]:
        """Map the organization-set ID column."""
        return create_mapped_column(
            DOMAIN, model.OrganizationSetMember, "organization_set_id"
        )

    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        """Map the member organization ID column."""
        return create_mapped_column(
            DOMAIN, model.OrganizationSetMember, "organization_id"
        )

    @declared_attr
    def organization_set(cls) -> Mapped[model.OrganizationSet]:
        """Map the organization-set relationship."""
        return relationship(
            "OrganizationSet",
            foreign_keys="OrganizationSetMember.organization_set_id",
        )

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        """Map the member organization relationship."""
        return relationship(
            "Organization", foreign_keys="OrganizationSetMember.organization_id"
        )


@declarative_mixin
class SiteMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns and organization relationship for site rows."""

    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        """Map the owning organization ID column."""
        return create_mapped_column(DOMAIN, model.Site, "organization_id")

    name: Mapped[str] = create_mapped_column(DOMAIN, model.Site, "name")

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        """Map the owning organization relationship."""
        return relationship("Organization", foreign_keys="Site.organization_id")


@declarative_mixin
class ContactMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns and site relationship for contact rows."""

    @declared_attr
    def site_id(cls) -> Mapped[UUID | None]:
        """Map the optional site ID column."""
        return create_mapped_column(DOMAIN, model.Contact, "site_id")

    name: Mapped[str] = create_mapped_column(DOMAIN, model.Contact, "name")
    email: Mapped[str | None] = create_mapped_column(DOMAIN, model.Contact, "email")
    phone: Mapped[str | None] = create_mapped_column(DOMAIN, model.Contact, "phone")

    @declared_attr
    def site(cls) -> Mapped[SiteMixin | None]:
        """Map the optional site relationship."""
        return relationship("Site", foreign_keys="Contact.site_id")


@declarative_mixin
class DataCollectionMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns for DataCollection-derived row models."""

    name: Mapped[str] = create_mapped_column(DOMAIN, model.DataCollection, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DataCollection, "description"
    )


@declarative_mixin
class DataCollectionSetMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns for DataCollectionSet-derived row models."""

    name: Mapped[str] = create_mapped_column(DOMAIN, model.DataCollectionSet, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DataCollectionSet, "description"
    )


@declarative_mixin
class DataCollectionSetMemberMixin(RowMetadataMixin):
    """Encapsulates columns and relationships for data-collection-set membership rows."""

    @declared_attr
    def data_collection_set_id(cls) -> Mapped[UUID]:
        """Map the data-collection-set ID column."""
        return create_mapped_column(
            DOMAIN,
            model.DataCollectionSetMember,
            "data_collection_set_id",
        )

    @declared_attr
    def data_collection_id(cls) -> Mapped[UUID]:
        """Map the member data-collection ID column."""
        return create_mapped_column(
            DOMAIN,
            model.DataCollectionSetMember,
            "data_collection_id",
        )

    @declared_attr
    def data_collection_set(cls) -> Mapped[DataCollectionSetMixin]:
        """Map the data-collection-set relationship."""
        return relationship(
            "DataCollectionSet",
            foreign_keys="DataCollectionSetMember.data_collection_set_id",
        )

    @declared_attr
    def data_collection(cls) -> Mapped[DataCollectionMixin]:
        """Map the member data-collection relationship."""
        return relationship(
            "DataCollection", foreign_keys="DataCollectionSetMember.data_collection_id"
        )


@declarative_mixin
class UserInvitationMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns and relationships for user invitation rows."""

    key: Mapped[str | None] = create_mapped_column(DOMAIN, model.UserInvitation, "key")
    email: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UserInvitation, "email"
    )
    name: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UserInvitation, "name"
    )
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.UserInvitation, "description"
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
        """Map the inviting user's ID column."""
        return create_mapped_column(DOMAIN, model.UserInvitation, "invited_by_user_id")

    @declared_attr
    def invited_by_user(cls) -> Mapped[UserMixin]:
        """Map the inviting user relationship."""
        return relationship("User", foreign_keys="UserInvitation.invited_by_user_id")

    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        """Map the invited user's organization ID column."""
        return create_mapped_column(DOMAIN, model.UserInvitation, "organization_id")

    @declared_attr
    def organization(cls) -> Mapped[model.Organization]:
        """Map the invited user's organization relationship."""
        return relationship(
            "Organization", foreign_keys="UserInvitation.organization_id"
        )


@declarative_mixin
class IdentifierIssuerMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns for IdentifierIssuer-derived row models."""

    code: Mapped[str] = create_mapped_column(DOMAIN, model.IdentifierIssuer, "code")
    name: Mapped[str] = create_mapped_column(DOMAIN, model.IdentifierIssuer, "name")
    description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.IdentifierIssuer, "description"
    )


@declarative_mixin
class OrganizationIdentifierIssuerLinkMixin(RowMetadataMixin):
    """Encapsulates columns for organization-to-identifier issuer link row models."""

    organization_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.OrganizationIdentifierIssuerLink, "organization_id"
    )
    identifier_issuer_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.OrganizationIdentifierIssuerLink, "identifier_issuer_id"
    )


@declarative_mixin
class IdentifierMixin(RowMetadataMixin):
    """Encapsulates SQLAlchemy columns for external identifier-derived row models."""

    @declared_attr
    def identifier_issuer_id(cls) -> Mapped[UUID]:
        """Map the identifier issuer ID column."""
        return create_mapped_column(
            DOMAIN, model.BaseIdentifier, "identifier_issuer_id"
        )

    external_id: Mapped[str] = create_mapped_column(
        DOMAIN, model.BaseIdentifier, "external_id"
    )


class Organization(Base, OrganizationMixin):
    """Encapsulates persistence of the commondb Organization domain model."""

    __tablename__, __table_args__ = create_table_args(model.Organization)


class User(Base, UserMixin):
    """Encapsulates persistence of the commondb User domain model."""

    __tablename__, __table_args__ = create_table_args(model.User)


class OrganizationSet(Base, OrganizationSetMixin):
    """Encapsulates persistence of the commondb OrganizationSet domain model."""

    __tablename__, __table_args__ = create_table_args(model.OrganizationSet)


class OrganizationSetMember(Base, OrganizationSetMemberMixin):
    """Encapsulates persistence of the commondb OrganizationSetMember domain model."""

    __tablename__, __table_args__ = create_table_args(model.OrganizationSetMember)


class Site(Base, SiteMixin):
    """Encapsulates persistence of the commondb Site domain model."""

    __tablename__, __table_args__ = create_table_args(model.Site)


class Contact(Base, ContactMixin):
    """Encapsulates persistence of the commondb Contact domain model."""

    __tablename__, __table_args__ = create_table_args(model.Contact)


class DataCollection(Base, DataCollectionMixin):
    """Encapsulates persistence of the commondb DataCollection domain model."""

    __tablename__, __table_args__ = create_table_args(model.DataCollection)


class DataCollectionSet(Base, DataCollectionSetMixin):
    """Encapsulates persistence of the commondb DataCollectionSet domain model."""

    __tablename__, __table_args__ = create_table_args(model.DataCollectionSet)


class DataCollectionSetMember(Base, DataCollectionSetMemberMixin):
    """Encapsulates persistence of the commondb DataCollectionSetMember domain model."""

    __tablename__, __table_args__ = create_table_args(model.DataCollectionSetMember)


class UserInvitation(Base, UserInvitationMixin):
    """Encapsulates persistence of the commondb UserInvitation domain model."""

    __tablename__, __table_args__ = create_table_args(model.UserInvitation)


class IdentifierIssuer(Base, IdentifierIssuerMixin):
    """Encapsulates persistence of the commondb IdentifierIssuer domain model."""

    __tablename__, __table_args__ = create_table_args(model.IdentifierIssuer)


class OrganizationIdentifierIssuerLink(Base, OrganizationIdentifierIssuerLinkMixin):
    """Encapsulates persistence of the commondb OrganizationIdentifierIssuerLink domain model."""

    __tablename__, __table_args__ = create_table_args(
        model.OrganizationIdentifierIssuerLink
    )
