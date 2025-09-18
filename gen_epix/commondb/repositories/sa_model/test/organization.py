from typing import Type

import sqlalchemy.orm as orm

from gen_epix.commondb.repositories.sa_model.organization import (
    ContactMixin as ContactMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionMixin as DataCollectionMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionSetMemberMixin as DataCollectionSetMemberMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionSetMixin as DataCollectionSetMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    IdentifierIssuerMixin as IdentifierIssuerMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationMixin as OrganizationMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationSetMemberMixin as OrganizationSetMemberMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationSetMixin as OrganizationSetMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import SiteMixin as SiteMixin
from gen_epix.commondb.repositories.sa_model.organization import (
    UserInvitationMixin as UserInvitationMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import UserMixin as UserMixin
from gen_epix.commondb.repositories.sa_model.util import create_table_args
from gen_epix.seqdb.domain import enum, model

Base: Type = orm.declarative_base(name=enum.ServiceType.ORGANIZATION.value)


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


class IdentifierIssuer(Base, IdentifierIssuerMixin):
    __tablename__, __table_args__ = create_table_args(model.IdentifierIssuer)


class DataCollection(Base, DataCollectionMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollection)


class DataCollectionSet(Base, DataCollectionSetMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollectionSet)


class DataCollectionSetMember(Base, DataCollectionSetMemberMixin):
    __tablename__, __table_args__ = create_table_args(model.DataCollectionSetMember)


class UserInvitation(Base, UserInvitationMixin):
    __tablename__, __table_args__ = create_table_args(model.UserInvitation)
