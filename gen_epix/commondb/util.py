from gen_epix.commondb.policies.model_metadata_policy import (
    MaskModelMetadataPolicy,
    SetModelMetadataPolicy,
)
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import EventTiming


def register_model_metadata_policies(
    app: App,
    privileged_roles: frozenset[str],
) -> None:
    """
    Registers SetModelMetadataPolicy (BEFORE) and MaskModelMetadataPolicy (AFTER)
    for every CrudCommand class known to the domain, so that:
    - Written ModelNoId objects get set_created / set_modified called automatically.
    - Returned ModelNoId objects have their metadata fields nulled out for
      non-privileged users.
    """
    set_policy = SetModelMetadataPolicy(privileged_roles)
    mask_policy = MaskModelMetadataPolicy(privileged_roles)
    crud_command_classes = set()
    for service_type in app.domain.get_service_types():
        crud_command_classes.update(
            app.domain.get_crud_commands_for_service_type(service_type)
        )
    for cmd_class in crud_command_classes:
        app.register_policy(cmd_class, set_policy, EventTiming.BEFORE)
        app.register_policy(cmd_class, mask_policy, EventTiming.AFTER)
