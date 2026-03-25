"""
Unit tests for BaseResult and ResultLogItem.

Verifies that:
- add_error / add_warning / add_info append the correct log items.
- add_error calls _set_error_status on the concrete class.
- has_errors / has_warnings / has_infos / has_log_code query correctly.
- UploadResult._set_error_status sets EtlStatus.FAILED.
- UploadResult.add_logs sets FAILED when any item is an error.
"""

from unittest import TestCase

import pytest

from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.commondb.domain.model.base import BaseEtlResult, EtlLogItem
from gen_epix.commondb.domain.model.upload import UploadLogItem, UploadResult
from gen_epix.fastapp.enum import LogLevel

# ---------------------------------------------------------------------------
# Minimal concrete class for testing BaseResult in isolation
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class _ConcreteResult(BaseEtlResult):
    """Minimal Pydantic model used to test BaseResult in isolation."""

    status: EtlStatus = EtlStatus.INITIALIZED

    def set_error_status(self) -> None:
        self.status = EtlStatus.ERROR


# ---------------------------------------------------------------------------
# Tests for ResultLogItem
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestResultLogItem(TestCase):
    def test_has_required_fields(self) -> None:
        item = EtlLogItem(
            code="E001", message="Something broke", severity=LogLevel.ERROR
        )
        self.assertEqual(item.code, "E001")
        self.assertEqual(item.message, "Something broke")
        self.assertEqual(item.severity, LogLevel.ERROR)
        self.assertIsNotNone(item.timestamp)

    def test_upload_log_item_is_result_log_item(self) -> None:
        """UploadLogItem must be the same class as ResultLogItem (alias)."""
        self.assertIs(UploadLogItem, EtlLogItem)


# ---------------------------------------------------------------------------
# Tests for BaseResult via _ConcreteResult
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestBaseResult(TestCase):
    def setUp(self) -> None:
        self.result = _ConcreteResult()

    # -- add_error ------------------------------------------------------------

    def test_add_error_appends_error_log(self) -> None:
        self.result.add_error("E001", "an error")
        self.assertEqual(len(self.result.logs), 1)
        self.assertEqual(self.result.logs[0].severity, LogLevel.ERROR)
        self.assertEqual(self.result.logs[0].code, "E001")
        self.assertEqual(self.result.logs[0].message, "an error")

    def test_add_error_calls_set_error_status(self) -> None:
        self.result.add_error("E001", "an error")
        self.assertEqual(self.result.status, EtlStatus.ERROR)

    # -- add_warning ----------------------------------------------------------

    def test_add_warning_appends_warn_log(self) -> None:
        self.result.add_warning("W001", "a warning")
        self.assertEqual(len(self.result.logs), 1)
        self.assertEqual(self.result.logs[0].severity, LogLevel.WARN)

    def test_add_warning_does_not_change_status(self) -> None:
        self.result.add_warning("W001", "a warning")
        self.assertEqual(self.result.status, EtlStatus.INITIALIZED)

    # -- add_info -------------------------------------------------------------

    def test_add_info_appends_info_log(self) -> None:
        self.result.add_info("I001", "some info")
        self.assertEqual(len(self.result.logs), 1)
        self.assertEqual(self.result.logs[0].severity, LogLevel.INFO)

    def test_add_info_does_not_change_status(self) -> None:
        self.result.add_info("I001", "some info")
        self.assertEqual(self.result.status, EtlStatus.INITIALIZED)

    # -- has_errors / has_warnings / has_infos --------------------------------

    def test_has_errors_false_when_no_logs(self) -> None:
        self.assertFalse(self.result.has_errors())

    def test_has_errors_false_when_only_warnings(self) -> None:
        self.result.add_warning("W001", "warn")
        self.assertFalse(self.result.has_errors())

    def test_has_errors_true_after_add_error(self) -> None:
        self.result.add_error("E001", "err")
        self.assertTrue(self.result.has_errors())

    def test_has_warnings_false_when_no_logs(self) -> None:
        self.assertFalse(self.result.has_warnings())

    def test_has_warnings_true_after_add_warning(self) -> None:
        self.result.add_warning("W001", "warn")
        self.assertTrue(self.result.has_warnings())

    def test_has_warnings_false_when_only_errors(self) -> None:
        self.result.add_error("E001", "err")
        self.assertFalse(self.result.has_warnings())

    def test_has_infos_false_when_no_logs(self) -> None:
        self.assertFalse(self.result.has_infos())

    def test_has_infos_true_after_add_info(self) -> None:
        self.result.add_info("I001", "info")
        self.assertTrue(self.result.has_infos())

    # -- has_log_code ---------------------------------------------------------

    def test_has_log_code_false_when_no_logs(self) -> None:
        self.assertFalse(self.result.has_log_code("E001"))

    def test_has_log_code_true_when_code_present(self) -> None:
        self.result.add_error("E001", "err")
        self.assertTrue(self.result.has_log_code("E001"))

    def test_has_log_code_false_when_different_code(self) -> None:
        self.result.add_error("E001", "err")
        self.assertFalse(self.result.has_log_code("E002"))

    def test_has_log_code_matches_across_severities(self) -> None:
        self.result.add_warning("SHARED_CODE", "warn")
        self.result.add_info("SHARED_CODE", "info")
        self.assertTrue(self.result.has_log_code("SHARED_CODE"))

    # -- multiple log items ---------------------------------------------------

    def test_multiple_log_items_accumulated(self) -> None:
        self.result.add_info("I001", "info")
        self.result.add_warning("W001", "warn")
        self.result.add_error("E001", "err")
        self.assertEqual(len(self.result.logs), 3)
        self.assertTrue(self.result.has_errors())
        self.assertTrue(self.result.has_warnings())
        self.assertTrue(self.result.has_infos())


# ---------------------------------------------------------------------------
# Tests for UploadResult._set_error_status and add_logs
# ---------------------------------------------------------------------------


def _make_pending_upload_result() -> UploadResult:
    """Construct an UploadResult in PENDING state (no logs required)."""
    return UploadResult.model_construct(
        id=None,
        status=EtlStatus.PENDING,
        is_new=False,
        logs=[],
    )


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestUploadResult(TestCase):
    def setUp(self) -> None:
        self.result = _make_pending_upload_result()

    def test_add_error_sets_upload_status_failed(self) -> None:
        self.result.add_error("E001", "upload broke")
        self.assertEqual(self.result.status, EtlStatus.FAILED)
        self.assertTrue(self.result.has_errors())

    def test_add_warning_does_not_change_status(self) -> None:
        self.result.add_warning("W001", "soft warning")
        self.assertEqual(self.result.status, EtlStatus.PENDING)
        self.assertTrue(self.result.has_warnings())

    def test_add_info_does_not_change_status(self) -> None:
        self.result.add_info("I001", "fyi")
        self.assertEqual(self.result.status, EtlStatus.PENDING)
        self.assertTrue(self.result.has_infos())

    def test_add_logs_list_with_error_sets_failed(self) -> None:
        items = [
            EtlLogItem(code="W001", message="warn", severity=LogLevel.WARN),
            EtlLogItem(code="E001", message="err", severity=LogLevel.ERROR),
        ]
        self.result.add_logs(items)
        self.assertEqual(self.result.status, EtlStatus.FAILED)
        self.assertEqual(len(self.result.logs), 2)

    def test_add_logs_list_without_error_keeps_status(self) -> None:
        items = [
            EtlLogItem(code="I001", message="info", severity=LogLevel.INFO),
            EtlLogItem(code="W001", message="warn", severity=LogLevel.WARN),
        ]
        self.result.add_logs(items)
        self.assertEqual(self.result.status, EtlStatus.PENDING)

    def test_add_logs_single_error_item_sets_failed(self) -> None:
        item = EtlLogItem(code="E001", message="err", severity=LogLevel.ERROR)
        self.result.add_logs(item)
        self.assertEqual(self.result.status, EtlStatus.FAILED)

    def test_add_logs_single_non_error_item_keeps_status(self) -> None:
        item = EtlLogItem(code="W001", message="warn", severity=LogLevel.WARN)
        self.result.add_logs(item)
        self.assertEqual(self.result.status, EtlStatus.PENDING)

    def test_has_log_code_works_on_upload_result(self) -> None:
        self.result.add_warning("SPECIFIC_CODE", "msg")
        self.assertTrue(self.result.has_log_code("SPECIFIC_CODE"))
        self.assertFalse(self.result.has_log_code("OTHER_CODE"))
