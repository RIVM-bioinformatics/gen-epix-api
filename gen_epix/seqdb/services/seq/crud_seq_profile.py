from typing import cast
from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.seqdb.services.seq.calculate_seq_distance import (
    seq_service_calculate_seq_distances_for_new_profiles,
)
from gen_epix.seqdb.services.seq.crud_common import _get_not_implemented_message


def seq_service_crud_seq_profile(
    self: BaseSeqService, cmd: command.SeqProfileCrudCommand
) -> (
    list[model.SeqProfile]
    | model.SeqProfile
    | list[UUID]
    | UUID
    | list[bool]
    | bool
    | None
):
    """Handle CRUD operations for SeqProfile entities."""
    user_id = cmd.user.id if cmd.user else None
    seq_profiles: list[model.SeqProfile] = cmd.get_objs()  # type: ignore[assignment]
    if cmd.is_create():
        # Calculate all distances for these seq profiles between themselves and with all stored seq profiles
        seq_profiles: list[model.SeqProfile] = cmd.get_objs()
        # TODO: 3034 Check if seq_profile.seq_profile_type and seq_profile.protocol.protocol_type are consistent with each other.

    elif cmd.is_read():
        # Nothing to do extra
        pass
    elif cmd.is_update():
        # May only change the representation format, not the profile itself
        raise NotImplementedError(_get_not_implemented_message(cmd))
    elif cmd.is_delete():
        # TODO: 3428 Delete all distances for these allele profiles as well
        # NotImplementedError commented out in order to get the seqdb uploads to PROD working, but should be implemented properly.
        # # Delete all distances for these allele profiles as well
        # raise NotImplementedError(_get_not_implemented_message(cmd))
        pass
    else:
        raise AssertionError(f"Unsupported operation type: {cmd.operation.value}")

    retval = self.crud(cmd)  # type: ignore[return-value]

    if cmd.is_create():
        # After creating new profiles, calculate distances between these new profiles and
        # all existing profiles, as well as between the new profiles themselves, and store these distances in the database. This is needed to make sure that distance information is available immediately after upload for all profiles, without needing to wait for a separate distance calculation step to complete.
        for seq_profile_id, seq_profile in zip(cast(list[UUID], retval), seq_profiles):
            seq_profile.id = seq_profile_id
        sub_cmd = command.CalculateSeqDistancesForNewProfilesCommand(
            user=cmd.user,
            seq_profiles=seq_profiles,
        )
        seq_service_calculate_seq_distances_for_new_profiles(self, sub_cmd)

    return retval
