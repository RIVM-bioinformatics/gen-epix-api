"""Unit tests for casedb case upload functionality."""

import datetime
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.model import STORED_MODEL_FIELD_PROPS
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.upload import CaseBatchUploader
from gen_epix.commondb.domain.enum import EtlStatus, UploadAction
from gen_epix.commondb.domain.model.organization import IdentifierForUpload, User
from gen_epix.fastapp.app import App
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import model as seqdb_model


def _mock_uow() -> Mock:
    uow: Mock = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


class BaseUploadTestCase(TestCase):
    """Base test case with common fixtures and utility methods."""

    def setUp(self) -> None:
        self.user = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={enum.Role.APP_ADMIN.value},
            organization_id=uuid4(),
            is_active=True,
        )

        self.batch_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.case_type_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.data_collection_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.case_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.sample_id = UUID("550e8400-e29b-41d4-a716-446655440005")
        self.protocol_id = UUID("550e8400-e29b-41d4-a716-446655440006")
        self.reads_col_id = UUID("550e8400-e29b-41d4-a716-446655440007")
        self.seq_col_id = UUID("550e8400-e29b-41d4-a716-446655440008")

        self.service = Mock(spec=BaseCaseService)
        self.service.generate_id = Mock(side_effect=uuid4)
        self.service.repository = Mock()
        self.service.app = Mock(spec=App)

        self.uow = _mock_uow()
        self.service.repository.uow.return_value = self.uow
        self.service.repository.crud.return_value = []
        self.service.repository.read_fields.return_value = []

        self.batch_uploader = CaseBatchUploader(self.service)

    def create_case_for_upload(
        self,
        read_sets: list[model.ReadSetForUpload] | None = None,
        seqs: list[model.SeqForUpload] | None = None,
    ) -> model.CaseForUpload:
        case = model.Case(
            id=self.case_id,
            case_type_id=self.case_type_id,
            created_in_data_collection_id=self.data_collection_id,
            content={},
        )
        return model.CaseForUpload(
            id=self.case_id,
            case=case,
            read_sets=read_sets,
            seqs=seqs,
        )

    def create_read_set_for_upload(self) -> model.ReadSetForUpload:
        return model.ReadSetForUpload(
            case_id=self.case_id,
            col_id=self.reads_col_id,
            sample_id=self.sample_id,
            other_sample_identifier=IdentifierForUpload(
                identifier_issuer_id=uuid4(),
                identifier_issuer_code="issuer",
                external_id="sample-external-id",
            ),
            protocol_id=self.protocol_id,
        )

    def create_read_set_for_upload_sample_id_only(self) -> model.ReadSetForUpload:
        return model.ReadSetForUpload(
            case_id=self.case_id,
            col_id=self.reads_col_id,
            sample_id=self.sample_id,
            other_sample_identifier=None,
            protocol_id=self.protocol_id,
        )

    def create_seq_for_upload(self) -> model.SeqForUpload:
        return model.SeqForUpload(
            case_id=self.case_id,
            col_id=self.seq_col_id,
            sample_id=self.sample_id,
            other_sample_identifier=IdentifierForUpload(
                identifier_issuer_id=uuid4(),
                identifier_issuer_code="issuer",
                external_id="sample-external-id",
            ),
            protocol_id=self.protocol_id,
        )

    def create_command_and_result(
        self,
        cases: list[model.CaseForUpload] | model.CaseForUpload,
    ) -> tuple[command.UploadCasesCommand, model.CaseBatchUploadResult]:
        if not isinstance(cases, list):
            cases = [cases]
        case_batch = model.CaseBatchForUpload(batch_id=self.batch_id, cases=cases)  # type: ignore[call-arg]
        cmd = command.UploadCasesCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            created_in_data_collection_id=self.data_collection_id,
            case_batch=case_batch,
            on_exists=UploadAction.UPDATE,  # type: ignore[call-arg]
            on_new=UploadAction.CREATE,  # type: ignore[call-arg]
        )
        batch_result: model.CaseBatchUploadResult = self.batch_uploader.init_batch_upload_result(cmd)  # type: ignore[assignment]
        return cmd, batch_result


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseUploadSeqdbBridge(BaseUploadTestCase):
    """Tests for the casedb-to-seqdb upload bridge in CaseBatchUploader."""

    def test_get_upload_samples_command_returns_none_without_children(self) -> None:
        case_for_upload = self.create_case_for_upload(read_sets=[], seqs=[])
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        upload_samples_cmd, child_map = self.batch_uploader._get_upload_samples_command(
            cmd,
            batch_result,
        )

        self.assertIsNone(upload_samples_cmd)
        self.assertEqual(dict(child_map), {})

    def test_get_upload_samples_command_builds_seqdb_batch(self) -> None:
        case_for_upload = self.create_case_for_upload(
            read_sets=[self.create_read_set_for_upload()],
            seqs=[self.create_seq_for_upload()],
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        upload_samples_cmd, child_map = self.batch_uploader._get_upload_samples_command(
            cmd,
            batch_result,
        )

        self.assertIsNotNone(upload_samples_cmd)
        assert upload_samples_cmd is not None
        self.assertEqual(len(upload_samples_cmd.sample_batch.samples), 1)
        sample = upload_samples_cmd.sample_batch.samples[0]
        self.assertEqual(len(sample.read_sets or []), 1)
        self.assertEqual(len(sample.seqs or []), 1)
        self.assertEqual(upload_samples_cmd.user, self.user)
        self.assertIn((0, 0), child_map[seqdb_model.ReadSetForUpload])
        self.assertIn((0, 0), child_map[seqdb_model.SeqForUpload])

    def test_upload_samples_maps_results_to_case_and_upload_result(self) -> None:
        case_for_upload = self.create_case_for_upload(
            read_sets=[self.create_read_set_for_upload()],
            seqs=[self.create_seq_for_upload()],
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        created_read_set_id = uuid4()
        created_seq_id = uuid4()
        seqdb_read_set_result = model.UploadResult.model_construct(
            id=created_read_set_id,
            status=EtlStatus.CREATED,
            is_new=True,
            logs=[],
        )
        seqdb_seq_result = model.UploadResult.model_construct(
            id=created_seq_id,
            status=EtlStatus.CREATED,
            is_new=True,
            logs=[],
        )
        seqdb_sample_result = seqdb_model.SampleUploadResult.model_construct(
            id=self.sample_id,
            status=EtlStatus.CREATED,
            is_new=False,
            logs=[],
            read_sets=[seqdb_read_set_result],
            seqs=[seqdb_seq_result],
        )
        seqdb_batch_result = seqdb_model.SampleBatchUploadResult.model_construct(
            id=uuid4(),
            status=EtlStatus.PROCESSED,
            is_new=False,
            logs=[],
            samples=[seqdb_sample_result],
            seq_distances=[],
        )
        self.service.app.handle.return_value = seqdb_batch_result

        success = self.batch_uploader.upload_samples(
            cmd, batch_result, verify_only=True
        )

        self.assertTrue(success)
        handled_cmd = self.service.app.handle.call_args[0][0]
        self.assertTrue(handled_cmd.verify_only)
        self.assertEqual(
            case_for_upload.case.content[self.reads_col_id],
            str(created_read_set_id),
        )
        self.assertEqual(
            case_for_upload.case.content[self.seq_col_id],
            str(created_seq_id),
        )
        self.assertEqual(batch_result.cases[0].read_sets[0].id, created_read_set_id)
        self.assertEqual(batch_result.cases[0].seqs[0].id, created_seq_id)

    def test_upload_samples_returns_false_when_seqdb_result_has_failures(self) -> None:
        case_for_upload = self.create_case_for_upload(
            read_sets=[self.create_read_set_for_upload()],
            seqs=None,
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        failed_sample_result = seqdb_model.SampleUploadResult.model_construct(
            id=self.sample_id,
            status=EtlStatus.FAILED,
            is_new=False,
            logs=[],
            read_sets=[],
            seqs=[],
        )
        seqdb_batch_result = seqdb_model.SampleBatchUploadResult.model_construct(
            id=uuid4(),
            status=EtlStatus.MIXED,
            is_new=False,
            logs=[],
            samples=[failed_sample_result],
            seq_distances=[],
        )
        self.service.app.handle.return_value = seqdb_batch_result

        success = self.batch_uploader.upload_samples(
            cmd, batch_result, verify_only=False
        )

        self.assertFalse(success)

    def test_get_upload_samples_command_accepts_sample_id_without_external_id(
        self,
    ) -> None:
        case_for_upload = self.create_case_for_upload(
            read_sets=[self.create_read_set_for_upload_sample_id_only()],
            seqs=None,
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        upload_samples_cmd, child_map = self.batch_uploader._get_upload_samples_command(
            cmd,
            batch_result,
        )

        self.assertIsNotNone(upload_samples_cmd)
        assert upload_samples_cmd is not None
        self.assertEqual(len(upload_samples_cmd.sample_batch.samples), 1)
        sample = upload_samples_cmd.sample_batch.samples[0]
        self.assertEqual(sample.id, self.sample_id)
        self.assertEqual(sample.sample.id, self.sample_id)
        self.assertEqual(sample.identifiers, [])
        self.assertEqual(len(sample.read_sets or []), 1)
        self.assertIn((0, 0), child_map[seqdb_model.ReadSetForUpload])


def _make_org_user() -> User:
    return User(
        id=uuid4(),
        key="test@example.com",
        email="test@example.com",
        roles={enum.Role.ORG_USER.value},
        organization_id=uuid4(),
        is_active=True,
    )


class TestCaseDateMutability(TestCase):
    def test_case_date_is_mutable_always(self) -> None:
        props = STORED_MODEL_FIELD_PROPS.get(model.Case, {})
        case_date_props = props.get("case_date")
        self.assertIsNotNone(
            case_date_props,
            "case_date missing from STORED_MODEL_FIELD_PROPS",
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
            user=_make_org_user(),
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
