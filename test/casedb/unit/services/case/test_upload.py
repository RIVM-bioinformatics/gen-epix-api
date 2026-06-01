"""Unit tests for CaseBatchUploader (LSP-3356: case_date mutability)."""

import datetime
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import uuid4

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain.model import STORED_MODEL_FIELD_PROPS
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.upload import CaseBatchUploader
from gen_epix.commondb.domain.enum import Role, UploadAction
from gen_epix.commondb.domain.model.organization import User


def _make_user() -> User:
    return User(
        id=uuid4(),
        key="test@example.com",
        email="test@example.com",
        roles={Role.ORG_USER.value},
        organization_id=uuid4(),
        is_active=True,
    )


class TestCaseDateMutability(TestCase):
    def test_case_date_is_mutable_always(self) -> None:
        props = STORED_MODEL_FIELD_PROPS.get(model.Case, {})
        case_date_props = props.get("case_date")
        self.assertIsNotNone(
            case_date_props, "case_date missing from STORED_MODEL_FIELD_PROPS"
        )
        self.assertTrue(
            case_date_props.is_mutable_always,
            "case_date.is_mutable_always must be True so updates persist",
        )


class TestUpsertBatchCaseDate(TestCase):
    def _make_uploader(self) -> tuple[CaseBatchUploader, Mock]:
        service = Mock(spec=BaseCaseService)
        service.repository = Mock()
        uploader = CaseBatchUploader(service)
        return uploader, service

    def test_calculated_case_date_preserved_for_existing_case(self) -> None:
        """After re-validation, case_date set by calculate_case_date must not
        be reset to None — the old LSP-3356 workaround has been removed."""
        uploader, service = self._make_uploader()

        case_type_id = uuid4()
        data_collection_id = uuid4()
        case_id = uuid4()
        sampling_col_id = uuid4()
        content: dict = {sampling_col_id: "2024-03-15"}
        expected_date = datetime.datetime(2024, 3, 15)

        case = model.Case(
            id=case_id,
            case_type_id=case_type_id,
            created_in_data_collection_id=data_collection_id,
            content=dict(content),
        )
        case_for_upload = model.CaseForUpload(case=case)
        case_result = model.CaseUploadResult(validated_content=dict(content))
        cmd = command.UploadCasesCommand(
            user=_make_user(),
            case_type_id=case_type_id,
            created_in_data_collection_id=data_collection_id,
            case_batch=model.CaseBatchForUpload(cases=[case_for_upload]),
            on_exists=UploadAction.UPDATE.value,
        )
        batch_result = model.CaseBatchUploadResult(cases=[case_result])

        service.repository.read_fields.return_value = [(case_id, dict(content))]

        mock_validator = Mock()

        def _set_date(inner_cmd: command.UploadCasesCommand, _result: object) -> None:
            for cfu in inner_cmd.case_batch.cases:
                if cfu.case is not None:
                    cfu.case.case_date = expected_date

        mock_validator.validate_and_transform.side_effect = _set_date

        with (
            patch.object(uploader, "_get_complete_case_type", return_value=Mock()),
            patch.object(uploader, "_get_case_validator", return_value=mock_validator),
            patch(
                "gen_epix.commondb.services.upload.BatchUploader.upsert_batch",
                return_value=True,
            ),
            patch.object(uploader, "has_samples", return_value=False),
        ):
            uploader.upsert_batch(cmd, batch_result, Mock())

        self.assertEqual(case.case_date, expected_date)
