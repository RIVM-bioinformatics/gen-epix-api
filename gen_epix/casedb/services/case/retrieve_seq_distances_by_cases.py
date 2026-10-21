"""Retrieve sequence distances for cases through seqdb commands."""

import json

import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import command
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_seq import _retrieve_case_profile_map


def case_service_retrieve_seq_distances_by_cases(
    self: BaseCaseService, cmd: command.RetrieveSeqDistancesByCasesCommand
) -> list[seqdb_model.SeqDistance]:
    """Retrieve sequence distances and expose selected case IDs as row IDs."""
    user, repository = self._get_user_and_repository(cmd)
    with repository.uow() as uow:
        genetic_distance_protocol, case_profile_map, _ = _retrieve_case_profile_map(
            self, uow, cmd
        )
        if not case_profile_map:
            return []
        seq_distances: list[seqdb_model.SeqDistance] = self.app.handle(
            seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand(
                user=cmd.user,
                seq_profile_ids=list(case_profile_map.values()),
                protocol_id=genetic_distance_protocol.seqdb_seq_distance_protocol_id,
            )
        )
    profile_case_map = {
        profile_id: case_id for case_id, profile_id in case_profile_map.items()
    }
    profile_ids = set(profile_case_map)
    retval: list[seqdb_model.SeqDistance] = []
    for seq_distance in seq_distances:
        case_id = profile_case_map.get(seq_distance.seq_profile_id)
        if case_id is None:
            continue
        seq_distance.id = case_id
        if cmd.filter_other_cases:
            distance_map = seq_distance.get_profile_distance_map()
            seq_distance.content = json.dumps(
                {
                    str(profile_id): distance
                    for profile_id, distance in distance_map.items()
                    if profile_id in profile_ids
                }
            )
        retval.append(seq_distance)
    return retval
