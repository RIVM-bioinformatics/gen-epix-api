"""Verify ETL lifecycle status values and groups."""

import pytest

from gen_epix.etl.enum import EtlStatus, EtlStatusSet


@pytest.mark.parametrize(
    ("status", "value"),
    [
        pytest.param(EtlStatus.PENDING, "PENDING", id="pending"),
        pytest.param(EtlStatus.SKIPPED, "SKIPPED", id="skipped"),
        pytest.param(EtlStatus.FAILED, "FAILED", id="failed"),
        pytest.param(EtlStatus.CREATED, "CREATED", id="created"),
        pytest.param(EtlStatus.UPDATED, "UPDATED", id="updated"),
        pytest.param(EtlStatus.DELETED, "DELETED", id="deleted"),
        pytest.param(EtlStatus.MIXED, "MIXED", id="mixed"),
        pytest.param(EtlStatus.PROCESSED, "PROCESSED", id="processed"),
        pytest.param(EtlStatus.SUCCESS, "SUCCESS", id="success"),
    ],
)
def test_etl_status_values(status, value):
    """Keep the public status values stable."""
    assert status.value == value


@pytest.mark.parametrize(
    ("status_set", "members"),
    [
        pytest.param(
            EtlStatusSet.NOT_FAILED,
            frozenset(
                {
                    EtlStatus.PENDING,
                    EtlStatus.SKIPPED,
                    EtlStatus.CREATED,
                    EtlStatus.UPDATED,
                    EtlStatus.DELETED,
                    EtlStatus.PROCESSED,
                    EtlStatus.SUCCESS,
                }
            ),
            id="not-failed",
        ),
        pytest.param(
            EtlStatusSet.FAILED,
            frozenset({EtlStatus.FAILED}),
            id="failed",
        ),
        pytest.param(
            EtlStatusSet.SUCCEEDED,
            frozenset(
                {
                    EtlStatus.SKIPPED,
                    EtlStatus.CREATED,
                    EtlStatus.UPDATED,
                    EtlStatus.DELETED,
                    EtlStatus.PROCESSED,
                    EtlStatus.SUCCESS,
                }
            ),
            id="succeeded",
        ),
        pytest.param(
            EtlStatusSet.COMPOUND,
            frozenset(
                {
                    EtlStatus.PENDING,
                    EtlStatus.FAILED,
                    EtlStatus.SUCCESS,
                }
            ),
            id="compound",
        ),
    ],
)
def test_etl_status_set_members(status_set, members):
    """Keep each status group aligned with its declared contract."""
    assert status_set.value == members
