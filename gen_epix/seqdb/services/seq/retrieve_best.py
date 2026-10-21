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
    model_class, return_primary_category_id = _get_result_model(cmd)
    _validate_ranking_strategy(cmd)
    user_id = cmd.user.id if cmd.user else None
    sample_ids = cmd.sample_ids or set()
    if not sample_ids:
        return {}
    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    filter = _create_best_result_filter(sample_ids, cmd.protocol_ids or set())
    with repository.uow() as uow:
        # qc_result is a denormalized, cached copy of the effective quality result
        # that is only refreshed on create, not on update (see QualityMixin). Read
        # qc_result_machine/qc_result_human directly and resolve the effective
        # result below, so a quality result updated after creation (e.g. a manual
        # review added later) is still honored.
        field_names = [
            "id",
            "sample_id",
            "qc_result_machine",
            "qc_result_human",
            "qc_score",
            "created_at",
        ]
        if return_primary_category_id:
            field_names.append("primary_category_id")
        iter_fields = repository.read_fields(
            uow,
            user_id,
            model_class,
            field_names=field_names,
            filter=filter,
        )
        return _select_best_ids(iter_fields, return_primary_category_id)


def _get_result_model(
    cmd: (
        command.RetrieveBestSeqPerSampleCommand
        | command.RetrieveBestSeqProfilePerSampleCommand
        | command.RetrieveBestSeqClassificationPerSampleCommand
    ),
) -> tuple[type[model.Model], bool]:
    """Resolve the result model and optional primary-category projection."""
    if isinstance(cmd, command.RetrieveBestSeqProfilePerSampleCommand):
        return model.SeqProfile, False
    if isinstance(cmd, command.RetrieveBestSeqPerSampleCommand):
        return model.Seq, False
    if isinstance(cmd, command.RetrieveBestSeqClassificationPerSampleCommand):
        return model.SeqClassification, cmd.return_primary_category_id
    raise NotImplementedError(f"Unsupported command type: {type(cmd).__name__}")


def _validate_ranking_strategy(
    cmd: (
        command.RetrieveBestSeqPerSampleCommand
        | command.RetrieveBestSeqProfilePerSampleCommand
        | command.RetrieveBestSeqClassificationPerSampleCommand
    ),
) -> None:
    """Reject ranking strategies not supported by the shared ranking query."""
    if cmd.ranking_strategy not in {
        enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        enum.SeqRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        enum.SeqClassificationRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
    }:
        raise exc.ServiceException(
            "a3f7c2b1", f"Unsupported ranking strategy: {cmd.ranking_strategy}"
        )


def _create_best_result_filter(
    sample_ids: set[UUID], protocol_ids: set[UUID]
) -> Filter:
    """Create the sample filter, optionally constrained by protocol IDs."""
    sample_filter = UuidSetFilter(key="sample_id", members=frozenset(sample_ids))
    if not protocol_ids:
        return sample_filter
    protocol_filter = UuidSetFilter(key="protocol_id", members=frozenset(protocol_ids))
    return CompositeFilter(
        filters=[sample_filter, protocol_filter], operator=LogicalOperator.AND
    )


def _select_best_ids(
    iter_fields: list[tuple], return_primary_category_id: bool
) -> dict[UUID, UUID]:
    """Select the top-ranked result row for each sample."""
    map_qc_result_to_sort_key = {
        result: enum.QualityControlResult.get_sort_key(result)
        for result in enum.QualityControlResult
    }

    def effective_qc_result(
        qc_result_machine: enum.QualityControlResult,
        qc_result_human: enum.QualityControlResult,
    ) -> enum.QualityControlResult:
        if qc_result_human != enum.QualityControlResult.PENDING:
            return qc_result_human
        return qc_result_machine

    sort_fn = lambda row: (
        row[1],
        map_qc_result_to_sort_key[effective_qc_result(row[2], row[3])],
        row[4],
        row[5],
    )
    sorted_iter = sorted(iter_fields, key=sort_fn, reverse=True)
    best_id_per_sample: dict[UUID, UUID] = {}
    previous_sample_id = None
    for row in sorted_iter:
        sample_id = row[1]
        if sample_id != previous_sample_id:
            best_id_per_sample[sample_id] = (
                row[6] if return_primary_category_id else row[0]
            )
            previous_sample_id = sample_id
    return best_id_per_sample
