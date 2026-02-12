"""
Utility functions for working with Model and ModelFieldProps.

This module is separate from fastapp.domain.util to avoid circular import issues.
"""

from typing import Any

from gen_epix.fastapp.model import Model, ModelFieldProps


def complete_stored_model_field_props(
    stored_model_field_props: dict[type[Model], dict[str, ModelFieldProps]],
    sorted_models_by_service_type: dict[Any, list[type[Model]]],
) -> None:
    """
    Complete the stored_model_field_props with default props for all other models/fields
    """
    # Complete the stored model field props with default props for all other models/fields
    for model_classes in sorted_models_by_service_type.values():
        for model_class in model_classes:
            entity = model_class.ENTITY
            if entity is None:
                raise ValueError(
                    f"Model class {model_class.__name__} does not have an ENTITY defined."
                )
            if not entity.persistable:
                if model_class in stored_model_field_props:
                    raise ValueError(
                        f"Model class {model_class.__name__} is not persistable but has stored field props defined."
                    )
                continue
            if model_class not in stored_model_field_props:
                # Add default props for all fields
                stored_model_field_props[model_class] = {
                    x: ModelFieldProps() for x in model_class.model_fields
                }  # Default props
                continue
            for field_name in model_class.model_fields:
                # Add default props for any missing fields
                if field_name not in stored_model_field_props[model_class]:
                    stored_model_field_props[model_class][
                        field_name
                    ] = ModelFieldProps()  # Default props
