from uuid import UUID

import gen_epix.seqdb.domain.command as command
import gen_epix.seqdb.domain.model as model
from gen_epix.filter.base import Filter
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import enum, exc
from gen_epix.seqdb.domain.repository import BaseSeqRepository
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_retrieve_best_seq_profile_per_sample(
    self: BaseSeqService,
    cmd: command.RetrieveBestSeqProfilePerSampleCommand,
) -> dict[UUID, UUID]:
    """
    Retrieve the best SeqProfile ID per sample for the given protocol and sample IDs.
    """
    return _get_best_id_per_sample(self, cmd)


def seq_service_retrieve_best_seq_per_sample(
    self: BaseSeqService,
    cmd: command.RetrieveBestSeqPerSampleCommand,
) -> dict[UUID, UUID]:
    """
    Retrieve the best Seq ID per sample for the given protocol and sample IDs.
    """
    return _get_best_id_per_sample(self, cmd)


def _get_best_id_per_sample(
    self: BaseSeqService,
    cmd: (
        command.RetrieveBestSeqPerSampleCommand
        | command.RetrieveBestSeqProfilePerSampleCommand
    ),
) -> dict[UUID, UUID]:
    """
    Retrieve the best Seq or SeqProfile ID per sample for the given protocol and sample
    IDs, based on the specified ranking strategy.
    """
    model_class = (
        model.SeqProfile
        if isinstance(cmd, command.RetrieveBestSeqProfilePerSampleCommand)
        else model.Seq
    )
    user_id = cmd.user.id if cmd.user else None
    if cmd.ranking_strategy not in {
        enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        enum.SeqRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
    }:
        raise exc.ServiceException(
            "a3f7c2b1", f"Unsupported ranking strategy: {cmd.ranking_strategy}"
        )

    protocol_ids = cmd.protocol_ids or set()
    sample_ids = cmd.sample_ids or set()
    if not protocol_ids or not sample_ids:
        return {}

    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    sample_filter = UuidSetFilter(key="sample_id", members=frozenset(sample_ids))
    filter: Filter
    if protocol_ids:
        protocol_filter = UuidSetFilter(
            key="protocol_id", members=frozenset(protocol_ids)
        )
        filter = CompositeFilter(
            filters=[sample_filter, protocol_filter], operator=LogicalOperator.AND
        )
    else:
        filter = sample_filter
    with repository.uow() as uow:
        iter_fields = repository.read_fields(
            uow,
            user_id,
            model_class,
            field_names=["id", "sample_id", "qc_result", "qc_score", "created_at"],
            filter=filter,
        )
        best_id_per_sample: dict[UUID, UUID] = {}
        if cmd.ranking_strategy in {
            enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
            enum.SeqRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        }:
            # Sort by (sample_id, qc_result, qc_score, created_at)
            map_qc_result_to_sort_key = {
                x: enum.QualityControlResult.get_sort_key(x)
                for x in enum.QualityControlResult
            }
            sort_fn = lambda x: (x[1], map_qc_result_to_sort_key[x[2]], x[3], x[4])
            sorted_iter = sorted(iter_fields, key=sort_fn)
            prev_sample_id = None
            for entry_id, sample_id, qc_result, qc_score, created_at in sorted_iter:
                if sample_id != prev_sample_id:
                    best_id_per_sample[sample_id] = entry_id
                    prev_sample_id = sample_id
        else:
            raise AssertionError(
                "Should not reach here due to earlier check on ranking strategy"
            )
    return best_id_per_sample
