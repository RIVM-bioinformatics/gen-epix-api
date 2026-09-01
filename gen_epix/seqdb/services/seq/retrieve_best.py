"""Implement seqdb sequence service behavior for services.seq.retrieve_best."""

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
    """Retrieve the best SeqProfile ID for each requested sample."""
    return _get_best_id_per_sample(self, cmd)


def seq_service_retrieve_best_seq_per_sample(
    self: BaseSeqService,
    cmd: command.RetrieveBestSeqPerSampleCommand,
) -> dict[UUID, UUID]:
    """Retrieve the best Seq ID for each requested sample."""
    return _get_best_id_per_sample(self, cmd)


def seq_service_retrieve_best_seq_classification_per_sample(
    self: BaseSeqService,
    cmd: command.RetrieveBestSeqClassificationPerSampleCommand,
) -> dict[UUID, UUID]:
    """Retrieve the best SeqClassification ID for each requested sample."""
    return _get_best_id_per_sample(self, cmd)


def _get_best_id_per_sample(
    self: BaseSeqService,
    cmd: (
        command.RetrieveBestSeqPerSampleCommand
        | command.RetrieveBestSeqProfilePerSampleCommand
        | command.RetrieveBestSeqClassificationPerSampleCommand
    ),
) -> dict[UUID, UUID]:
    """Retrieve the best result identifier for each requested sample.

    Retrieves the best Seq, SeqProfile, or SeqClassification ID for the given
    protocol and sample IDs, based on the specified ranking strategy.

    For SeqClassification, if `cmd.return_primary_category_id` is True, the primary
    category ID will be returned instead of the SeqClassification ID.

    Args:
        self: Sequence service providing repository access.
        cmd: Typed best-result retrieval command.

    Returns:
        Mapping from sample IDs to the selected result identifiers.

    Raises:
        NotImplementedError: The command type is unsupported.
        ServiceException: The requested ranking strategy is unsupported.
    """
    model_class: type[model.Model]
    return_primary_category_id = False
    if isinstance(cmd, command.RetrieveBestSeqProfilePerSampleCommand):
        model_class = model.SeqProfile
    elif isinstance(cmd, command.RetrieveBestSeqPerSampleCommand):
        model_class = model.Seq
    elif isinstance(cmd, command.RetrieveBestSeqClassificationPerSampleCommand):
        model_class = model.SeqClassification
        return_primary_category_id = cmd.return_primary_category_id
    else:
        raise NotImplementedError(f"Unsupported command type: {type(cmd).__name__}")
    user_id = cmd.user.id if cmd.user else None
    if cmd.ranking_strategy not in {
        enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        enum.SeqRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        enum.SeqClassificationRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
    }:
        raise exc.ServiceException(
            "a3f7c2b1", f"Unsupported ranking strategy: {cmd.ranking_strategy}"
        )

    sample_ids = cmd.sample_ids or set()
    if not sample_ids:
        return {}
    protocol_ids = cmd.protocol_ids or set()

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
        field_names = ["id", "sample_id", "qc_result", "qc_score", "created_at"]
        if return_primary_category_id:
            field_names.append("primary_category_id")
        iter_fields = repository.read_fields(
            uow,
            user_id,
            model_class,
            field_names=field_names,
            filter=filter,
        )
        best_id_per_sample: dict[UUID, UUID] = {}
        if cmd.ranking_strategy in {
            enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
            enum.SeqRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
            enum.SeqClassificationRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        }:
            # Sort by (sample_id, qc_result, qc_score, created_at)
            map_qc_result_to_sort_key = {
                x: enum.QualityControlResult.get_sort_key(x)
                for x in enum.QualityControlResult
            }
            sort_fn = lambda x: (x[1], map_qc_result_to_sort_key[x[2]], x[3], x[4])
            sorted_iter = sorted(iter_fields, key=sort_fn)
            prev_sample_id = None
            for row in sorted_iter:
                sample_id = row[1]
                if sample_id != prev_sample_id:
                    best_id_per_sample[sample_id] = (
                        row[5] if return_primary_category_id else row[0]
                    )
                    prev_sample_id = sample_id
        else:  # pragma: no cover
            raise AssertionError(
                "Should not reach here due to earlier check on ranking strategy"
            )
    return best_id_per_sample
