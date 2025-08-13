from typing import Type

import sqlalchemy as sa

from gen_epix.common.repositories.sa_model import ContactMixin as ContactMixin
from gen_epix.common.repositories.sa_model import (
    DataCollectionMixin as DataCollectionMixin,
)
from gen_epix.common.repositories.sa_model import (
    DataCollectionSetMemberMixin as DataCollectionSetMemberMixin,
)
from gen_epix.common.repositories.sa_model import (
    DataCollectionSetMixin as DataCollectionSetMixin,
)
from gen_epix.common.repositories.sa_model import (
    IdentifierIssuerMixin as IdentifierIssuerMixin,
)
from gen_epix.common.repositories.sa_model import OrganizationMixin as OrganizationMixin
from gen_epix.common.repositories.sa_model import (
    OrganizationSetMemberMixin as OrganizationSetMemberMixin,
)
from gen_epix.common.repositories.sa_model import (
    OrganizationSetMixin as OrganizationSetMixin,
)
from gen_epix.common.repositories.sa_model import SiteMixin as SiteMixin
from gen_epix.common.repositories.sa_model import (
    UserInvitationMixin as UserInvitationMixin,
)
from gen_epix.common.repositories.sa_model import UserMixin as UserMixin
from gen_epix.common.repositories.sa_model import create_table_args
from gen_epix.seqdb.domain import enum, model

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.ORGANIZATION.value)


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
