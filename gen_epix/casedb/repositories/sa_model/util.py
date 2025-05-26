from typing import Any, Type

import sqlalchemy as sa
from sqlalchemy.orm import MappedColumn, mapped_column

from gen_epix.casedb.domain.model import Model
from gen_epix.casedb.domain.model.base import Model
from gen_epix.fastapp import Entity
from gen_epix.fastapp.repositories import get_pydantic_field_sa_type


def create_table_args(
    model_class: Type[Model],
    field_name_map: dict[str, str] | None = None,
    **kwargs: dict,
) -> tuple:
    entity: Entity = model_class.ENTITY  # type: ignore[attr-defined]
    uq_constraints = []
    for field_names in entity.get_keys_field_names():
        sa_field_names = (
            [field_name_map.get(x, x) for x in field_names]
            if field_name_map
            else field_names
        )
        sa_field_name_str = "_".join(sa_field_names)
        uq_constraints.append(
            sa.UniqueConstraint(
                *sa_field_names,
                name=f"uq_{entity.table_name}_{sa_field_name_str}",
                **kwargs,
            )
        )
    if entity.schema_name:
        return entity.table_name, tuple(
            [*uq_constraints, {"schema": entity.schema_name}]
        )
    return entity.table_name, tuple([*uq_constraints])


def create_mapped_column(
    model_class: Type[Model],
    field_name: str,
    field_name_map: dict[str, str] | None = None,
    **kwargs: dict,
) -> MappedColumn[Any]:
    entity: Entity = model_class.ENTITY  # type: ignore[attr-defined]
    fieldinfo = model_class.model_fields[field_name]
    sa_type = get_pydantic_field_sa_type(fieldinfo)
    nullable = kwargs.get("nullable", fieldinfo.is_required() is False)
    doc = kwargs.pop("doc", fieldinfo.description)
    link_entity = entity.get_link_entity(field_name)
    if link_entity and link_entity.service_type != entity.service_type:
        # Create foreign keys only within the same service
        link_entity = None
    ondelete = kwargs.pop("ondelete", None)
    onupdate = kwargs.pop("onupdate", None)
    sa_field_name = (
        field_name_map[model_class][field_name] if field_name_map else field_name
    )
    fk_name = kwargs.pop("fk_name", f"fk_{entity.table_name}_{sa_field_name}")
    if link_entity:
        link_model_class = link_entity.model_class
        link_sa_id_field_name = (
            field_name_map[link_model_class][link_entity.id_field_name]
            if field_name_map
            else link_entity.id_field_name
        )
        ref_column_name = (
            f"{link_entity.schema_name}.{link_entity.table_name}.{link_sa_id_field_name}"
            if link_entity.schema_name
            else f"{link_entity.table_name}.{link_sa_id_field_name}"
        )
        return mapped_column(
            sa_type,
            sa.ForeignKey(
                ref_column_name, ondelete=ondelete, onupdate=onupdate, name=fk_name
            ),
            nullable=nullable,
            doc=doc,
            **kwargs,
        )
    return mapped_column(
        sa_type,
        nullable=nullable,
        primary_key=entity.id_field_name == field_name,
        doc=doc,
        **kwargs,
    )
