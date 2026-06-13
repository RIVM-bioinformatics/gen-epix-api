"""
Integration tests for the filtered unique index on SeqClassification and AstPrediction.

The unique index on (seq_id, protocol_id) fires only when seq_id IS NOT NULL.
This allows multiple pending rows (seq_id=NULL, same protocol_id) to coexist,
while still preventing two resolved rows from sharing the same (seq_id, protocol_id).
"""
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

# Importing repositories triggers domain initialization (set_model_class on all
# entities), which must complete before create_table_args is evaluated.
from gen_epix.seqdb.repositories.sa_model.seq.operational_data import (  # noqa: F401
    AstPrediction as SAAstPrediction,
    SeqClassification as SASeqClassification,
)
from gen_epix.seqdb.repositories.sa_model.seq.ref_data import Base
from gen_epix.seqdb.domain import enum


def _make_seq_classification(**kwargs) -> SASeqClassification:
    defaults = dict(
        id=uuid4(),
        sample_id=uuid4(),
        seq_id=None,
        protocol_id=uuid4(),
        primary_category_id=uuid4(),
        format=enum.SeqClassificationFormat.PRIMARY_CATEGORY_ONLY,
        content_hash=uuid4(),
        content="{}",
        qc_result=enum.QualityControlResult.PASS,
        qc_score=1.0,
    )
    defaults.update(kwargs)
    return SASeqClassification(**defaults)


def _make_ast_prediction(**kwargs) -> SAAstPrediction:
    defaults = dict(
        id=uuid4(),
        sample_id=uuid4(),
        seq_id=None,
        protocol_id=uuid4(),
        format=enum.AstResultFormat.AST_RESULT_FORMAT1,
        content_hash=uuid4(),
        content="{}",
        qc_result=enum.QualityControlResult.PASS,
        qc_score=1.0,
    )
    defaults.update(kwargs)
    return SAAstPrediction(**defaults)


@pytest.fixture(scope="module")
def engine():
    """In-memory SQLite engine with the seq schema attached and FK checks off."""
    e = sa.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with e.connect() as conn:
        conn.execute(sa.text("PRAGMA foreign_keys=OFF"))
        conn.execute(sa.text("ATTACH DATABASE ':memory:' AS seq"))
        conn.commit()
    Base.metadata.create_all(e)
    yield e
    e.dispose()


class TestSeqClassificationFilteredIndex:
    def test_null_seq_id_allows_multiple_pending_rows_and_enforces_non_null(
        self, engine: sa.Engine
    ) -> None:
        protocol_id = uuid4()
        # Two pending rows (seq_id=NULL) with the same protocol_id must coexist
        with Session(engine) as s:
            s.add(_make_seq_classification(seq_id=None, protocol_id=protocol_id))
            s.add(_make_seq_classification(seq_id=None, protocol_id=protocol_id))
            s.commit()

        # Two resolved rows with the same (seq_id, protocol_id) must be rejected
        shared_seq_id = uuid4()
        with pytest.raises(sa.exc.IntegrityError):
            with Session(engine) as s:
                s.add(
                    _make_seq_classification(
                        seq_id=shared_seq_id, protocol_id=protocol_id
                    )
                )
                s.add(
                    _make_seq_classification(
                        seq_id=shared_seq_id, protocol_id=protocol_id
                    )
                )
                s.commit()


class TestAstPredictionFilteredIndex:
    def test_null_seq_id_allows_multiple_pending_rows_and_enforces_non_null(
        self, engine: sa.Engine
    ) -> None:
        protocol_id = uuid4()
        # Two pending rows (seq_id=NULL) with the same protocol_id must coexist
        with Session(engine) as s:
            s.add(_make_ast_prediction(seq_id=None, protocol_id=protocol_id))
            s.add(_make_ast_prediction(seq_id=None, protocol_id=protocol_id))
            s.commit()

        # Two resolved rows with the same (seq_id, protocol_id) must be rejected
        shared_seq_id = uuid4()
        with pytest.raises(sa.exc.IntegrityError):
            with Session(engine) as s:
                s.add(
                    _make_ast_prediction(
                        seq_id=shared_seq_id, protocol_id=protocol_id
                    )
                )
                s.add(
                    _make_ast_prediction(
                        seq_id=shared_seq_id, protocol_id=protocol_id
                    )
                )
                s.commit()
