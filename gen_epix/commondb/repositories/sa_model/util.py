"""Build and validate commondb SQLAlchemy mappings from domain metadata."""

import typing
from enum import Enum
from typing import Any

import sqlalchemy as sa
from pydantic import BaseModel
from pydantic.fields import ComputedFieldInfo, FieldInfo
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from gen_epix.fastapp import Domain, Entity, Model
from gen_epix.fastapp.repositories import create_sa_type_from_field_info
from gen_epix.fastapp.repositories.sa.util import get_sa_type_kwargs_from_field_info


def create_table_args(
    model_class: type[Model],
    field_name_map: dict[str, str] | None = None,
    **kwargs: Any,
) -> tuple[str, tuple]:
    """Create SQLAlchemy table arguments from a domain model's entity keys.

    The arguments include unique constraints
    based on the entity's keys, and optionally applying a field name mapping.

    Args:
        model_class: Domain model whose entity defines the table.
        field_name_map: Optional domain-to-SQL field name mapping.
        **kwargs: Additional keyword arguments for each unique constraint.

    Returns:
        Table name and SQLAlchemy table arguments.
    """
    assert model_class.ENTITY is not None
    entity: Entity = model_class.ENTITY
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
    domain: Domain,
    model_class: type[Model],
    field_name: str,
    field_name_map: dict[type[Model], dict[str, str]] | None = None,
    sql_field_name: str | None = None,
    **kwargs: Any,
) -> MappedColumn[Any]:
    """Create a SQLAlchemy mapped column for a domain model field.

    If the field
    is a link to another entity, also create the appropriate foreign key constraint, but
    only if the linked entity is in the same service (to avoid cross-service foreign
    keys).

    Args:
        domain: The domain object containing the model.
        model_class: The model class containing the field.
        field_name: The name of the field in the model class.
        field_name_map: Optional mapping of model class to field name mappings.
        sql_field_name: Optional explicit SQL column name.
        **kwargs: Additional keyword arguments to pass to the mapped_column function.

    Returns:
        A SQLAlchemy MappedColumn object.

    Raises:
        ValueError: If ``field_name`` is not defined by the domain model.
    """
    assert model_class.ENTITY is not None
    entity: Entity = model_class.ENTITY
    computed_or_field_info: FieldInfo | ComputedFieldInfo
    annotation: type[Any] | None
    if field_name in model_class.model_fields:
        field_info: FieldInfo = model_class.model_fields[field_name]
        annotation = field_info.annotation
        is_required = field_info.is_required()
        computed_or_field_info = field_info
    elif field_name in model_class.model_computed_fields:
        computed_field_info: ComputedFieldInfo = model_class.model_computed_fields[
            field_name
        ]
        annotation = computed_field_info.return_type
        is_required = True
        computed_or_field_info = computed_field_info
    else:
        raise ValueError(
            f"Field '{field_name}' not found in model '{model_class.__name__}'"
        )
    sa_type = create_sa_type_from_field_info(computed_or_field_info, annotation)
    nullable = kwargs.get("nullable", not is_required)
    doc = kwargs.pop("doc", computed_or_field_info.description)
    link_entity = entity.get_link_entity(field_name)
    if link_entity and domain.get_service_type_for_entity(
        link_entity
    ) != domain.get_service_type_for_entity(entity):
        # Create foreign keys only within the same service
        link_entity = None
    ondelete = kwargs.pop("ondelete", None)
    onupdate = kwargs.pop("onupdate", None)
    if field_name_map is None:
        field_name_map = {}
    if model_class not in field_name_map:
        sa_field_name = field_name
    else:
        sa_field_name = field_name_map[model_class].get(field_name, field_name)
    sql_field_name = sql_field_name or sa_field_name
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
            sql_field_name,
            sa_type,
            sa.ForeignKey(
                ref_column_name, ondelete=ondelete, onupdate=onupdate, name=fk_name
            ),
            nullable=nullable,
            doc=doc,
            **kwargs,
        )
    return mapped_column(
        sql_field_name,
        sa_type,
        nullable=nullable,
        primary_key=entity.id_field_name == field_name,
        doc=doc,
        **kwargs,
    )


def create_composite_primary_key_mapper_args(
    model_class: type[Model],
    field_name_map: dict[type[Model], dict[str, str]] | None = None,
    mapper_args: dict | None = None,
) -> dict[str, list[str]]:
    """Create SQLAlchemy mapper arguments with composite primary-key fields.

    The arguments include composite primary
    key constraints based on the entity's keys.

    Args:
        model_class: Domain model whose entity defines the mapped fields.
        field_name_map: Optional domain-to-SQL field name mapping.
        mapper_args: Optional mapper arguments to extend.

    Returns:
        Mapper arguments containing SQL primary-key field names.
    """
    assert model_class.ENTITY is not None
    entity: Entity = model_class.ENTITY
    field_name_map = field_name_map or {}
    mapper_args = mapper_args if mapper_args is not None else {}
    if model_class not in field_name_map:
        sa_field_names = entity.get_field_names()
    else:
        sa_field_names = [
            field_name_map[model_class].get(x, x) for x in entity.get_field_names()
        ]
    return {"primary_key": sa_field_names}


def set_entity_repository_model_classes(
    domain: Domain,
    sa_models_by_service_type: dict[Enum, dict[type[BaseModel], type]],
    row_metadata_mixin_class: type,
    field_name_map: dict[type, dict[str, str]] | None = None,
) -> None:
    """Register SQLAlchemy model classes and validate their domain field parity.

    The function sets the db_model_class for each entity in the domain based on provided
    models, and verify that the SA models have the same fields as the corresponding
    model classes.

    Args:
        domain: Domain whose persistable entities will be registered.
        sa_models_by_service_type: SQLAlchemy models grouped by service type.
        row_metadata_mixin_class: Audit metadata mixin used by registered rows.
        field_name_map: Optional domain-to-SQL field name mappings.

    Raises:
        ValueError: If a persistable domain model has no SQLAlchemy model or mapped
            fields differ between the domain and SQLAlchemy models.
    """
    if field_name_map is None:
        field_name_map = {}
    sa_metadata_field_names = (
        set()
    )  # Currently no SA-specific metadata fields, but this would be the place to add any if needed in the future, based on row_metadata_mixin_class
    sa_model_map = _build_sa_model_map(sa_models_by_service_type)
    for entity in domain.get_dag_sorted_entities():
        if not entity.persistable:
            continue
        model_class = entity.model_class
        sa_model_class = sa_model_map.get(model_class)
        if not sa_model_class:
            raise ValueError(
                f"Model {model_class.__name__} does not have a corresponding SA model"
            )
        entity.set_db_model_class(sa_model_class)
        # Verify that the SA model has exactly the same fields as the model
        _validate_entity_fields(
            field_name_map, sa_metadata_field_names, entity, model_class, sa_model_class
        )


def _validate_entity_fields(
    field_name_map: dict[type, dict[str, str]],
    sa_metadata_field_names: set[str],
    entity: Entity,
    model_class: type,
    sa_model_class: type,
) -> None:
    """Verify SQLAlchemy and domain model fields match after supported mappings.

    Field comparison ignores SQLAlchemy metadata and relationship-only fields.

    Args:
        field_name_map: Domain-to-SQL field name mappings.
        sa_metadata_field_names: SQLAlchemy-only metadata fields to ignore.
        entity: Domain entity whose fields are validated.
        model_class: Domain model class associated with the entity.
        sa_model_class: SQLAlchemy row class associated with the domain model.

    Raises:
        ValueError: If either model has non-relationship fields absent from the other.
    """
    field_names = set(entity.get_field_names())
    relationship_field_names = set(entity.get_relationship_field_names())
    curr_field_name_map = field_name_map.get(model_class)
    if curr_field_name_map:
        field_names = {curr_field_name_map.get(x, x) for x in field_names}

    field_names = field_names - sa_metadata_field_names
    sa_field_names: set[str] = (
        set(sa_model_class.__table__.columns.keys())  # type: ignore[attr-defined]
        - sa_metadata_field_names
        - relationship_field_names
    )
    extra_field_names = field_names - sa_field_names - relationship_field_names
    extra_field_names = {x for x in extra_field_names if f"{x}_id" not in field_names}
    if extra_field_names:
        extra_field_names_str = ", ".join(extra_field_names)
        raise ValueError(
            f"Model {model_class.__name__} has fields {extra_field_names_str} that are not in SA model {sa_model_class.__name__}"
        )
    extra_sa_field_names = sa_field_names - field_names
    if extra_sa_field_names:
        extra_sa_field_names_str = ", ".join(extra_sa_field_names)
        raise ValueError(
            f"SA model {sa_model_class.__name__} has fields {extra_sa_field_names_str} that are not in model {model_class.__name__}"
        )


def _build_sa_model_map(
    sa_models_by_service_type: dict[Enum, dict[type[BaseModel], type]],
) -> dict[type[BaseModel], type]:
    """Build a domain-to-SQLAlchemy model mapping without duplicate domain models.

    The function verifies that there are no
    duplicate model classes across service types.

    Args:
        sa_models_by_service_type: SQLAlchemy models grouped by service type.

    Returns:
        Mapping of each domain model class to its SQLAlchemy row class.

    Raises:
        ValueError: If a domain model occurs in multiple service-type mappings.
    """
    sa_model_map: dict[type[BaseModel], type] = {}
    for curr_sa_model_map in sa_models_by_service_type.values():
        for model_class, sa_model_class in curr_sa_model_map.items():
            if model_class in sa_model_map:
                raise ValueError(f"Duplicate SA model for {model_class.__name__}")
            sa_model_map[model_class] = sa_model_class
    return sa_model_map


def get_mixin_mapped_column(
    model_mixin_class: type,
    field_name: str,
    sa_column_type: type[sa.types.TypeEngine],
    **kwargs: Any,
) -> Mapped:
    """Create a mapped column from a Pydantic model-mixin field.

    The helper derives field annotation and nullability from the mixin, then applies
    explicit SQLAlchemy column arguments.

    Args:
        model_mixin_class: Model mixin class containing the field.
        field_name: Name of the mixin field to map.
        sa_column_type: SQLAlchemy column type for the mapped field.
        **kwargs: Additional mapped-column arguments, including optional nullability.

    Returns:
        SQLAlchemy mapped column configured from the mixin field metadata.
    """
    annotation = model_mixin_class.__annotations__[field_name]
    field_info: FieldInfo
    if hasattr(model_mixin_class, field_name):
        # Mixin class has the field as an attribute (should normally not be the case to avoid warnings about shadowing variables), so we can get the FieldInfo directly
        field_info = getattr(model_mixin_class, field_name)
    else:
        if hasattr(model_mixin_class, "__pydantic_fields__"):
            # Mixin class has the field as an attribute (should normally not be the case to avoid warnings about shadowing variables), so we can get the FieldInfo directly
            field_info = model_mixin_class.__pydantic_fields__[field_name]
        else:
            # Mixin class has the field as an annotation only (normal case)
            annotation_args = typing.get_args(annotation)
            field_info = annotation_args[1]
    # Extract SA arguments from mixin class based on sa_type
    kwargs["nullable"] = kwargs.get(  # pyright: ignore[reportArgumentType]
        "nullable", not field_info.is_required()
    )
    sa_column_type_kwargs = kwargs.pop(
        "sa_column_type_kwargs",
        get_sa_type_kwargs_from_field_info(sa_column_type, field_info),
    )
    # Create and return mapped column
    return mapped_column(
        create_sa_type_from_field_info(field_info, annotation, **sa_column_type_kwargs),
        **kwargs,
    )
