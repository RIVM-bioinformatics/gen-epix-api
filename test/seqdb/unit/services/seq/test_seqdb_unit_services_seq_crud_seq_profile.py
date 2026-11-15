"""Verify sequence-profile CRUD post-processing for single creates."""

from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.services.seq.crud_seq_profile import (
    seq_service_crud_seq_profile,
)


@pytest.mark.parametrize("return_model", [False, True])
def test_create_one_profile_calculates_distances_with_created_id(
    return_model: bool,
) -> None:
    profile_id = uuid4()
    profile = model.SeqProfile.model_construct(id=None)
    created_result = (
        model.SeqProfile.model_construct(id=profile_id) if return_model else profile_id
    )
    cmd = command.SeqProfileCrudCommand.model_construct(
        user=None,
        operation=CrudOperation.CREATE_ONE,
        objs=profile,
    )
    service = Mock()
    service.crud.return_value = created_result

    with (
        patch(
            "gen_epix.seqdb.services.seq.crud_seq_profile.seq_service_calculate_seq_distances_for_new_profiles"
        ) as calculate_distances,
        patch.object(
            command, "CalculateSeqDistancesForNewProfilesCommand"
        ) as command_cls,
    ):
        result = seq_service_crud_seq_profile(service, cmd)

    assert result is created_result
    assert profile.id == profile_id
    command_cls.assert_called_once_with(user=None, seq_profiles=[profile])
    calculate_distances.assert_called_once_with(service, command_cls.return_value)
