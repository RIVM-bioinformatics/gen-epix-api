"""Unit tests for gen_epix.seqdb.services.seq.retrieve_best."""

from datetime import datetime, timezone
from test.util.mock_compat import Mock
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import Role
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp.exc import ServiceException
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, enum
from gen_epix.seqdb.services.seq.retrieve_best import (
    _get_best_id_per_sample,
    seq_service_retrieve_best_seq_classification_per_sample,
    seq_service_retrieve_best_seq_per_sample,
    seq_service_retrieve_best_seq_profile_per_sample,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DT_OLD = datetime(2020, 1, 1, tzinfo=timezone.utc)
_DT_NEW = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _make_user() -> User:
    return User(
        id=uuid4(),
        key="test@example.com",
        email="test@example.com",
        roles={Role.APP_ADMIN.value},
        organization_id=uuid4(),
        is_active=True,
    )


def _mock_uow() -> Mock:
    uow: Mock = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


def _mock_service(rows: list[tuple]) -> Mock:
    """Return a minimal mock service whose repository yields *rows* from read_fields."""
    repo = Mock()
    repo.uow = Mock(return_value=_mock_uow())
    repo.read_fields = Mock(return_value=iter(rows))
    svc = Mock()
    svc.repository = repo
    return svc


def _row(
    *,
    entry_id: UUID | None = None,
    sample_id: UUID | None = None,
    qc_result: enum.QualityControlResult = enum.QualityControlResult.PASS,
    qc_score: float = 1.0,
    created_at: datetime = _DT_OLD,
) -> tuple:
    return (
        entry_id or uuid4(),
        sample_id or uuid4(),
        qc_result,
        qc_score,
        created_at,
    )


def _seq_cmd(**kwargs: Any) -> command.RetrieveBestSeqPerSampleCommand:
    return command.RetrieveBestSeqPerSampleCommand(
        ranking_strategy=enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        **kwargs,
    )


def _profile_cmd(**kwargs: Any) -> command.RetrieveBestSeqProfilePerSampleCommand:
    protocol_ids = kwargs.pop("protocol_ids", {uuid4()})
    return command.RetrieveBestSeqProfilePerSampleCommand(
        protocol_ids=protocol_ids,
        ranking_strategy=enum.SeqProfileRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        **kwargs,
    )


def _classification_cmd(
    **kwargs: Any,
) -> command.RetrieveBestSeqClassificationPerSampleCommand:
    protocol_ids = kwargs.pop("protocol_ids", {uuid4()})
    return command.RetrieveBestSeqClassificationPerSampleCommand(
        protocol_ids=protocol_ids,
        ranking_strategy=enum.SeqClassificationRankingStrategy.QC_RESULT_THEN_SCORE_THEN_CREATED,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Public function delegation
# ---------------------------------------------------------------------------


class TestPublicFunctions:
    """Each public function delegates to _get_best_id_per_sample."""

    def test_retrieve_best_seq_profile_per_sample(self) -> None:
        sample_id = uuid4()
        entry_id = uuid4()
        svc = _mock_service([_row(entry_id=entry_id, sample_id=sample_id)])
        cmd = _profile_cmd(sample_ids={sample_id})
        result = seq_service_retrieve_best_seq_profile_per_sample(svc, cmd)
        assert result == {sample_id: entry_id}

    def test_retrieve_best_seq_per_sample(self) -> None:
        sample_id = uuid4()
        entry_id = uuid4()
        svc = _mock_service([_row(entry_id=entry_id, sample_id=sample_id)])
        cmd = _seq_cmd(sample_ids={sample_id})
        result = seq_service_retrieve_best_seq_per_sample(svc, cmd)
        assert result == {sample_id: entry_id}

    def test_retrieve_best_seq_classification_per_sample(self) -> None:
        sample_id = uuid4()
        entry_id = uuid4()
        svc = _mock_service([_row(entry_id=entry_id, sample_id=sample_id)])
        cmd = _classification_cmd(sample_ids={sample_id})
        result = seq_service_retrieve_best_seq_classification_per_sample(svc, cmd)
        assert result == {sample_id: entry_id}


# ---------------------------------------------------------------------------
# Empty sample_ids
# ---------------------------------------------------------------------------


class TestEmptySampleIds:
    def test_none_sample_ids_returns_empty(self) -> None:
        svc = _mock_service([])
        cmd = _profile_cmd(sample_ids=None)
        assert _get_best_id_per_sample(svc, cmd) == {}

    def test_empty_set_sample_ids_returns_empty(self) -> None:
        # sample_ids=set() is falsy, so we also get {}
        svc = _mock_service([])
        cmd = _seq_cmd(sample_ids=set())
        assert _get_best_id_per_sample(svc, cmd) == {}


# ---------------------------------------------------------------------------
# Filter construction
# ---------------------------------------------------------------------------


class TestFilterConstruction:
    """Verify UuidSetFilter vs CompositeFilter based on protocol_ids presence."""

    def test_with_protocol_ids_passes_composite_filter(self) -> None:
        from gen_epix.filter.composite import CompositeFilter

        sample_id = uuid4()
        entry_id = uuid4()
        protocol_id = uuid4()
        svc = _mock_service([_row(entry_id=entry_id, sample_id=sample_id)])
        cmd = _profile_cmd(sample_ids={sample_id}, protocol_ids={protocol_id})
        _get_best_id_per_sample(svc, cmd)
        _, call_kwargs = svc.repository.read_fields.call_args
        assert isinstance(call_kwargs["filter"], CompositeFilter)

    def test_without_protocol_ids_passes_uuid_set_filter(self) -> None:
        from gen_epix.filter.uuid_set import UuidSetFilter

        sample_id = uuid4()
        entry_id = uuid4()
        svc = _mock_service([_row(entry_id=entry_id, sample_id=sample_id)])
        cmd = _seq_cmd(sample_ids={sample_id}, protocol_ids=None)
        _get_best_id_per_sample(svc, cmd)
        _, call_kwargs = svc.repository.read_fields.call_args
        assert isinstance(call_kwargs["filter"], UuidSetFilter)

    def test_user_id_passed_to_read_fields(self) -> None:
        user = _make_user()
        sample_id = uuid4()
        svc = _mock_service([_row(sample_id=sample_id)])
        cmd = _profile_cmd(sample_ids={sample_id}, user=user)
        _get_best_id_per_sample(svc, cmd)
        args, _ = svc.repository.read_fields.call_args
        assert args[1] == user.id

    def test_none_user_passes_none_user_id(self) -> None:
        sample_id = uuid4()
        svc = _mock_service([_row(sample_id=sample_id)])
        cmd = _profile_cmd(sample_ids={sample_id}, user=None)
        _get_best_id_per_sample(svc, cmd)
        args, _ = svc.repository.read_fields.call_args
        assert args[1] is None


# ---------------------------------------------------------------------------
# Ranking logic
# ---------------------------------------------------------------------------


class TestRankingLogic:
    """
    The sort key is (sample_id, qc_result_sort_key, qc_score, created_at) ascending.
    The first entry per sample after sorting is selected as the "best".
    """

    def test_single_entry_per_sample_is_selected(self) -> None:
        s1, e1 = uuid4(), uuid4()
        s2, e2 = uuid4(), uuid4()
        svc = _mock_service(
            [_row(entry_id=e1, sample_id=s1), _row(entry_id=e2, sample_id=s2)]
        )
        cmd = _profile_cmd(sample_ids={s1, s2})
        result = _get_best_id_per_sample(svc, cmd)
        assert result == {s1: e1, s2: e2}

    def test_lower_qc_result_sort_key_wins(self) -> None:
        # Ascending sort → lowest qc_result value wins per sample.
        sample_id = uuid4()
        id_pending = uuid4()
        id_pass = uuid4()
        rows = [
            _row(
                entry_id=id_pass,
                sample_id=sample_id,
                qc_result=enum.QualityControlResult.PASS,
            ),
            _row(
                entry_id=id_pending,
                sample_id=sample_id,
                qc_result=enum.QualityControlResult.PENDING,
            ),
        ]
        svc = _mock_service(rows)
        cmd = _profile_cmd(sample_ids={sample_id})
        result = _get_best_id_per_sample(svc, cmd)
        # PENDING (sort key 1) < PASS (sort key 4), so PENDING wins
        assert result[sample_id] == id_pending

    def test_lower_qc_score_wins_when_qc_result_equal(self) -> None:
        sample_id = uuid4()
        id_low_score = uuid4()
        id_high_score = uuid4()
        rows = [
            _row(entry_id=id_high_score, sample_id=sample_id, qc_score=9.0),
            _row(entry_id=id_low_score, sample_id=sample_id, qc_score=1.0),
        ]
        svc = _mock_service(rows)
        cmd = _profile_cmd(sample_ids={sample_id})
        result = _get_best_id_per_sample(svc, cmd)
        assert result[sample_id] == id_low_score

    def test_earlier_created_at_wins_when_qc_result_and_score_equal(self) -> None:
        sample_id = uuid4()
        id_old = uuid4()
        id_new = uuid4()
        rows = [
            _row(entry_id=id_new, sample_id=sample_id, created_at=_DT_NEW),
            _row(entry_id=id_old, sample_id=sample_id, created_at=_DT_OLD),
        ]
        svc = _mock_service(rows)
        cmd = _profile_cmd(sample_ids={sample_id})
        result = _get_best_id_per_sample(svc, cmd)
        assert result[sample_id] == id_old

    def test_multiple_samples_each_gets_independent_best(self) -> None:
        s1, s2 = uuid4(), uuid4()
        best_s1 = uuid4()
        worst_s1 = uuid4()
        best_s2 = uuid4()
        rows = [
            _row(
                entry_id=worst_s1,
                sample_id=s1,
                qc_result=enum.QualityControlResult.PASS,
            ),
            _row(
                entry_id=best_s1,
                sample_id=s1,
                qc_result=enum.QualityControlResult.PENDING,
            ),
            _row(
                entry_id=best_s2, sample_id=s2, qc_result=enum.QualityControlResult.FAIL
            ),
        ]
        svc = _mock_service(rows)
        cmd = _profile_cmd(sample_ids={s1, s2})
        result = _get_best_id_per_sample(svc, cmd)
        assert result[s1] == best_s1
        assert result[s2] == best_s2

    def test_seq_classification_model_class_passed_to_read_fields(self) -> None:
        from gen_epix.seqdb.domain import model

        sample_id = uuid4()
        svc = _mock_service([_row(sample_id=sample_id)])
        cmd = _classification_cmd(sample_ids={sample_id})
        _get_best_id_per_sample(svc, cmd)
        args, _ = svc.repository.read_fields.call_args
        assert args[2] is model.SeqClassification

    def test_seq_profile_model_class_passed_to_read_fields(self) -> None:
        from gen_epix.seqdb.domain import model

        sample_id = uuid4()
        svc = _mock_service([_row(sample_id=sample_id)])
        cmd = _profile_cmd(sample_ids={sample_id})
        _get_best_id_per_sample(svc, cmd)
        args, _ = svc.repository.read_fields.call_args
        assert args[2] is model.SeqProfile

    def test_seq_model_class_passed_to_read_fields(self) -> None:
        from gen_epix.seqdb.domain import model

        sample_id = uuid4()
        svc = _mock_service([_row(sample_id=sample_id)])
        cmd = _seq_cmd(sample_ids={sample_id})
        _get_best_id_per_sample(svc, cmd)
        args, _ = svc.repository.read_fields.call_args
        assert args[2] is model.Seq


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


class TestErrorPaths:
    def test_unsupported_ranking_strategy_raises_service_exception(self) -> None:
        sample_id = uuid4()
        svc = _mock_service([])
        cmd = Mock(spec=command.RetrieveBestSeqProfilePerSampleCommand)
        cmd.ranking_strategy = "UNSUPPORTED_STRATEGY"
        cmd.sample_ids = {sample_id}
        cmd.user = None
        with pytest.raises(ServiceException):
            _get_best_id_per_sample(svc, cmd)

    def test_unsupported_command_type_raises_not_implemented(self) -> None:
        svc = _mock_service([])
        cmd = Mock()  # no spec — passes no isinstance check
        cmd.sample_ids = {uuid4()}
        with pytest.raises(NotImplementedError):
            _get_best_id_per_sample(svc, cmd)
