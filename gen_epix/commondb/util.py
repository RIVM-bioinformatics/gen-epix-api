from gen_epix.commondb.policies.model_metadata_policy import (
    MaskModelProcessMetadataPolicy,
)
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import EventTiming


def _get_crud_command_classes(app: App) -> set:
    crud_command_classes = set()
    for service_type in app.domain.get_service_types():
        crud_command_classes.update(
            app.domain.get_crud_commands_for_service_type(service_type)
        )
    return crud_command_classes


def register_mask_model_metadata_policy(
    app: App,
    privileged_roles: frozenset[str],
) -> None:
    """
    Registers MaskModelProcessMetadataPolicy (AFTER) for every CrudCommand class
    known to the domain, so that returned objects have their metadata fields nulled
    out for non-privileged users.
    """
    policy = MaskModelProcessMetadataPolicy(privileged_roles)
    for cmd_class in _get_crud_command_classes(app):
        app.register_policy(cmd_class, policy, EventTiming.AFTER)
