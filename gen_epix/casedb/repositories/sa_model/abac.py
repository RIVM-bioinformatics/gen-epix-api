from typing import Type
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from gen_epix.casedb.domain import enum, model
from gen_epix.casedb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.casedb.repositories.sa_model.util import (
    create_mapped_column,
    create_table_args,
)

Base: Type = sa.orm.declarative_base(name=enum.ServiceType.ABAC.value)


class OrganizationAdminPolicy(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationAdminPolicy)

    organization_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationAdminPolicy, "organization_id"
    )
    user_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationAdminPolicy, "user_id"
    )
    is_active: Mapped[bool] = create_mapped_column(
        model.OrganizationAdminPolicy, "is_active"
    )


class OrganizationAccessCasePolicy(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(
        model.OrganizationAccessCasePolicy
    )

    organization_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "organization_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "data_collection_id"
    )
    case_type_set_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "case_type_set_id"
    )
    is_active: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "is_active"
    )
    is_private: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "is_private"
    )
    add_case: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "add_case"
    )
    remove_case: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "remove_case"
    )
    add_case_set: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "add_case_set"
    )
    remove_case_set: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "remove_case_set"
    )
    read_case_type_col_set_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "read_case_type_col_set_id"
    )
    write_case_type_col_set_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "write_case_type_col_set_id"
    )
    read_case_set: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "read_case_set"
    )
    write_case_set: Mapped[bool] = create_mapped_column(
        model.OrganizationAccessCasePolicy, "write_case_set"
    )


class UserAccessCasePolicy(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.UserAccessCasePolicy)

    user_id: Mapped[UUID] = create_mapped_column(model.UserAccessCasePolicy, "user_id")
    data_collection_id: Mapped[UUID] = create_mapped_column(
        model.UserAccessCasePolicy, "data_collection_id"
    )
    case_type_set_id: Mapped[UUID] = create_mapped_column(
        model.UserAccessCasePolicy, "case_type_set_id"
    )
    is_active: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "is_active"
    )
    add_case: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "add_case"
    )
    remove_case: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "remove_case"
    )
    add_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "add_case_set"
    )
    remove_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "remove_case_set"
    )
    read_case_type_col_set_id: Mapped[UUID] = create_mapped_column(
        model.UserAccessCasePolicy, "read_case_type_col_set_id"
    )
    write_case_type_col_set_id: Mapped[UUID] = create_mapped_column(
        model.UserAccessCasePolicy, "write_case_type_col_set_id"
    )
    read_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "read_case_set"
    )
    write_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "write_case_set"
    )


class OrganizationShareCasePolicy(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.OrganizationShareCasePolicy)

    organization_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationShareCasePolicy, "organization_id"
    )
    data_collection_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationShareCasePolicy, "data_collection_id"
    )
    case_type_set_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationShareCasePolicy, "case_type_set_id"
    )
    from_data_collection_id: Mapped[UUID] = create_mapped_column(
        model.OrganizationShareCasePolicy, "from_data_collection_id"
    )
    is_active: Mapped[bool] = create_mapped_column(
        model.OrganizationShareCasePolicy, "is_active"
    )
    add_case: Mapped[bool] = create_mapped_column(
        model.OrganizationShareCasePolicy, "add_case"
    )
    remove_case: Mapped[bool] = create_mapped_column(
        model.OrganizationShareCasePolicy, "remove_case"
    )
    add_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "add_case_set"
    )
    remove_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "remove_case_set"
    )


class UserShareCasePolicy(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.UserShareCasePolicy)

    user_id: Mapped[UUID] = create_mapped_column(model.UserShareCasePolicy, "user_id")
    data_collection_id: Mapped[UUID] = create_mapped_column(
        model.UserShareCasePolicy, "data_collection_id"
    )
    case_type_set_id: Mapped[UUID] = create_mapped_column(
        model.UserShareCasePolicy, "case_type_set_id"
    )
    from_data_collection_id: Mapped[UUID] = create_mapped_column(
        model.UserShareCasePolicy, "from_data_collection_id"
    )
    is_active: Mapped[bool] = create_mapped_column(
        model.UserShareCasePolicy, "is_active"
    )
    add_case: Mapped[bool] = create_mapped_column(model.UserShareCasePolicy, "add_case")
    remove_case: Mapped[bool] = create_mapped_column(
        model.UserShareCasePolicy, "remove_case"
    )
    add_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "add_case_set"
    )
    remove_case_set: Mapped[bool] = create_mapped_column(
        model.UserAccessCasePolicy, "remove_case_set"
    )
