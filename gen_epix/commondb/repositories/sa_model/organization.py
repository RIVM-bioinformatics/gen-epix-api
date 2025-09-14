# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, declarative_mixin, declared_attr, relationship

from gen_epix.common.domain import DOMAIN, model
from gen_epix.common.repositories.sa_model.base import RowMetadataMixin
from gen_epix.common.repositories.sa_model.util import create_mapped_column


@declarative_mixin
class OrganizationMixin(RowMetadataMixin):
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Organization, "name")
    legal_entity_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.Organization, "legal_entity_code"
    )


@declarative_mixin
class UserMixin(RowMetadataMixin):
    email: Mapped[str] = create_mapped_column(DOMAIN, model.User, "email")
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
class IdentifierIssuerMixin(RowMetadataMixin):
    name: Mapped[str] = create_mapped_column(DOMAIN, model.IdentifierIssuer, "name")


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
    email: Mapped[str] = create_mapped_column(DOMAIN, model.UserInvitation, "email")
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
