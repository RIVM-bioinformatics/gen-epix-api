from test.fastapp.enum import ServiceType
from typing import ClassVar, Type
from uuid import UUID

import sqlalchemy as sa
from pydantic import Field
from sqlalchemy.orm import declarative_mixin
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.fastapp.domain import Domain, Entity, create_links
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories import ServerUtcCurrentTime


@declarative_mixin
class RowMetadataMixin:
    _created_at = sa.Column(
        sa.DateTime, nullable=False, server_default=ServerUtcCurrentTime()
    )
    _modified_at = sa.Column(
        sa.DateTime,
        nullable=False,
        server_default=ServerUtcCurrentTime(),
        onupdate=ServerUtcCurrentTime(),
    )
    _modified_by = sa.Column(sa.UUID, nullable=True)
    _version = sa.Column(sa.Integer, nullable=False, default=1)
    _deleted = sa.Column(sa.Boolean, nullable=False, default=False)


class Model1_1(Model):
    ENTITY: ClassVar = Entity(
        id=UUID("ea7e423a-d7c3-4fba-a11d-64879c88ce12"),
        snake_case_plural_name="models1_1",
        service_type=ServiceType.SERVICE1,
        schema_name="schema1",
        table_name="model1_1",
        persistable=True,
        id_field_name="id",
    )
    id: UUID | None
    var1: int
    var2: str


class Model1_2(Model):
    ENTITY: ClassVar = Entity(
        id=UUID("08d0deb8-d4a2-48b0-94eb-6df1b8d81405"),
        snake_case_plural_name="models1_2",
        service_type=ServiceType.SERVICE1,
        schema_name="schema1",
        table_name="model1_1",
        persistable=True,
        id_field_name="id",
        links=create_links(
            {
                1: ("model1_1_id", Model1_1, "model1_1"),  # type: ignore
            }
        ),
    )
    id: UUID | None
    var1: int
    var2: str
    model1_1_id: UUID
    model1_1: Model1_1 | None = Field(default=None)


class Model2_1(Model):
    ENTITY: ClassVar = Entity(
        id=UUID("a6af25f1-1e61-4782-9051-4c4ce056f0c1"),
        snake_case_plural_name="models2_1",
        service_type=ServiceType.SERVICE2,
        schema_name="schema2",
        table_name="model2_1",
        persistable=True,
        id_field_name="id",
        links=create_links(
            {
                1: ("model1_2_id", Model1_2, "model1_2"),  # type: ignore
            }
        ),
    )
    id: UUID | None
    var1: int
    var2: str
    model1_2_id: UUID
    model1_2: Model1_2 | None = Field(default=None)


class Model2_2(Model):
    ENTITY: ClassVar = Entity(
        id=UUID("1fc5643c-7c11-4c2b-bb93-d420be1a4615"),
        snake_case_plural_name="models2_2",
        service_type=ServiceType.SERVICE2,
        schema_name="schema2",
        table_name="model2_2",
        persistable=True,
        id_field_name="id",
        links=create_links(
            {
                1: ("model2_1_id", Model2_1, "model2_1"),  # type: ignore
            }
        ),
    )
    id: UUID | None
    var1: int
    var2: str
    var3: dict
    model2_1_id: UUID
    model2_1: Model2_1 | None = Field(default=None)


Base1: Type = sa.orm.declarative_base(name="SERVICE1")


class SAModel1_1(Base1, RowMetadataMixin):
    __tablename__ = "model1_1"
    __table_args__ = {"schema": "schema1"}
    id = sa.Column(UUIDType(), nullable=False, primary_key=True)
    var1 = sa.Column(sa.Integer, nullable=False)
    var2 = sa.Column(sa.String, nullable=False)


class SAModel1_2(Base1, RowMetadataMixin):
    __tablename__ = "model1_2"
    __table_args__ = {"schema": "schema1"}
    id = sa.Column(UUIDType(), primary_key=True, nullable=False)
    var1 = sa.Column(sa.Integer, nullable=False)
    var2 = sa.Column(sa.String, nullable=False)
    model1_1_id = sa.Column(
        UUIDType(), sa.ForeignKey("schema1.model1_1.id"), nullable=False
    )
    model1_1 = sa.orm.relationship("SAModel1_1")


Base2: Type = sa.orm.declarative_base(name="SERVICE2")


class SAModel2_1(Base2, RowMetadataMixin):
    __tablename__ = "model2_1"
    __table_args__ = {"schema": "schema2"}
    id = sa.Column(UUIDType(), nullable=False, primary_key=True)
    var1 = sa.Column(sa.Integer, nullable=False)
    var2 = sa.Column(sa.String, nullable=False)
    model1_2_id = sa.Column(UUIDType(), nullable=False)


class SAModel2_2(Base2, RowMetadataMixin):
    __tablename__ = "model2_2"
    __table_args__ = {"schema": "schema2"}
    id = sa.Column(UUIDType(), nullable=False, primary_key=True)
    var1 = sa.Column(sa.Integer, nullable=False)
    var2 = sa.Column(sa.String, nullable=False)
    var3 = sa.Column(sa.JSON, nullable=False)
    model2_1_id = sa.Column(
        UUIDType(), sa.ForeignKey("schema2.model2_1.id"), nullable=False
    )
    model2_1 = sa.orm.relationship("SAModel2_1")


DOMAIN = Domain("service.test")
DOMAIN.register_locals(locals())

MODEL_MAP = {
    Model1_1: SAModel1_1,
    Model1_2: SAModel1_2,
    Model2_1: SAModel2_1,
    Model2_2: SAModel2_2,
}
for model_class, db_model_class in MODEL_MAP.items():
    assert isinstance(model_class.ENTITY, Entity)
    model_class.ENTITY.set_db_model_class(db_model_class)
