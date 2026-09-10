"""Unit tests for casedb case upload functionality."""

import datetime
from test.util.mock_compat import Mock, patch
from typing import cast
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, exc, model
from gen_epix.casedb.domain.model import STORED_MODEL_FIELD_PROPS
from gen_epix.casedb.domain.model.abac.rights import CaseTypeAccessAbac
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.upload import (
    CaseBatchUploader,
    case_service_upload_cases,
)
from gen_epix.commondb.domain.enum import (
    DataIssueType,
    EtlStatus,
    RoleSet,
    UploadAction,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload, User
from gen_epix.fastapp import CrudOperation
from gen_epix.fastapp.app import App
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import model as seqdb_model


def _mock_uow() -> Mock:
    uow: Mock = Mock(spec=BaseUnitOfWork)
    uow.__enter__ = Mock(return_value=uow)
    uow.__exit__ = Mock(return_value=None)
    return uow


def _to_casedb_role_set(role_set: RoleSet) -> set[str]:
    """Map commondb role enums to casedb role strings with CASEDB_ prefix."""
    return {f"CASEDB_{x.name}" for x in role_set.value}


class BaseUploadTestCase:
    """Base test case with common fixtures and utility methods."""

    def setup_method(self) -> None:
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
        self.cohort_id = UUID("550e8400-e29b-41d4-a716-446655440009")
        self.cohort_definition_id = UUID("550e8400-e29b-41d4-a716-446655440010")
        self.timed_at = datetime.datetime(2026, 1, 1)

        self.service = Mock(spec=BaseCaseService)
        self.service.generate_id = Mock(side_effect=uuid4)
        self.service.repository = Mock()
        self.service.app = Mock(spec=App)
        self.service.role_set_map = {
            RoleSet.GE_ORG_USER: _to_casedb_role_set(RoleSet.GE_ORG_USER)
        }

        self.uow = _mock_uow()
        self.service.repository.uow.return_value = self.uow
        self.service.repository.crud.return_value = []
        self.service.repository.read_fields.return_value = []

        self.batch_uploader = CaseBatchUploader(self.service)

    def create_case_for_upload(
        self,
        case_id: UUID | None = None,
        case_type_id: UUID | None = None,
        created_in_data_collection_id: UUID | None = None,
        cohort: dict[UUID, UUID | None] | None = None,
        timed_at: datetime.datetime | None = None,
        content: dict[UUID, str | None] | None = None,
        read_sets: list[model.ReadSetForUpload] | None = None,
        seqs: list[model.SeqForUpload] | None = None,
    ) -> model.CaseForUpload:
        case = self.create_case(
            case_id=case_id,
            case_type_id=case_type_id,
            created_in_data_collection_id=created_in_data_collection_id,
            cohort=cohort,
            timed_at=timed_at,
            content=content,
        )
        return model.CaseForUpload(
            id=case_id or self.case_id,
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
        default_created_in_data_collection_id: UUID | None = None,
    ) -> tuple[command.UploadCasesCommand, model.CaseBatchUploadResult]:
        if not isinstance(cases, list):
            cases = [cases]
        case_batch = model.CaseBatchForUpload(batch_id=self.batch_id, cases=cases)  # type: ignore[call-arg]
        cmd = command.UploadCasesCommand(
            user=self.user,
            case_type_id=self.case_type_id,
            default_created_in_data_collection_id=default_created_in_data_collection_id
            or self.data_collection_id,
            case_batch=case_batch,
            on_exists=UploadAction.UPDATE,  # type: ignore[call-arg]
            on_new=UploadAction.CREATE,  # type: ignore[call-arg]
        )
        batch_result: model.CaseBatchUploadResult = self.batch_uploader.init_batch_upload_result(cmd)  # type: ignore[assignment]
        return cmd, batch_result

    def create_org_user(self) -> User:
        return User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={enum.Role.ORG_USER.value},
            organization_id=uuid4(),
            is_active=True,
        )

    def create_uploader(self) -> tuple[CaseBatchUploader, Mock]:
        service = Mock(spec=BaseCaseService)
        service.repository = Mock()
        service.role_set_map = {
            RoleSet.GE_ORG_USER: _to_casedb_role_set(RoleSet.GE_ORG_USER)
        }
        uploader = CaseBatchUploader(service)
        return uploader, service

    def create_case(
        self,
        case_id: UUID | None = None,
        case_type_id: UUID | None = None,
        created_in_data_collection_id: UUID | None = None,
        cohort: dict[UUID, UUID | None] | None = None,
        timed_at: datetime.datetime | None = None,
        content: dict[UUID, str | None] | None = None,
    ) -> model.Case:
        return model.Case(
            id=case_id or self.case_id,
            case_type_id=case_type_id or self.case_type_id,
            created_in_data_collection_id=created_in_data_collection_id
            or self.data_collection_id,
            cohort=cohort or {},
            timed_at=timed_at or self.timed_at,
            content=content or {},
        )

    def update_case(
        self,
        existing_case: model.Case,
        uploaded_case: model.Case,
    ) -> tuple[bool, model.UploadResult, list[model.Case]]:
        uploader, service = self.create_uploader()
        uow = Mock()
        result = model.UploadResult(status=EtlStatus.PENDING)
        updated_objs: list[model.Case] = []

        def _crud_side_effect(
            _uow: Mock,
            _user_id: UUID | None,
            _model_class: type[model.Model],
            operation: CrudOperation,
            **kwargs: object,
        ) -> list[model.Case] | list[UUID]:
            if operation == CrudOperation.READ_SOME:
                return [existing_case]
            if operation == CrudOperation.UPDATE_SOME:
                objs = kwargs.get("objs")
                assert isinstance(objs, list)
                updated_objs.extend(objs)
                assert existing_case.id is not None
                return [existing_case.id]
            raise AssertionError(f"Unexpected operation: {operation}")

        service.repository.crud.side_effect = _crud_side_effect

        success = uploader.update_objects(
            uow,
            None,
            model.Case,
            [(uploaded_case, result)],
        )
        return success, result, updated_objs


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseServiceUploadCasesFeatureFlag(BaseUploadTestCase):
    def test_upload_cases_raises_when_upload_feature_disabled(self) -> None:
        case_for_upload = self.create_case_for_upload()
        cmd, _ = self.create_command_and_result(case_for_upload)
        self.service.app.get_feature_flag.return_value = True

        with pytest.raises(exc.FeatureDisabledServiceError):
            case_service_upload_cases(self.service, cmd)

        self.service.app.get_feature_flag.assert_called_once_with(
            enum.FeatureFlag.DISABLE_UPLOAD.value
        )

    def test_upload_cases_delegates_when_upload_feature_enabled(self) -> None:
        case_for_upload = self.create_case_for_upload()
        cmd, batch_result = self.create_command_and_result(case_for_upload)
        self.service.app.get_feature_flag.return_value = False
        batch_uploader = Mock()
        batch_uploader.upload_batch.return_value = batch_result

        with patch(
            "gen_epix.casedb.services.case.upload.CaseBatchUploader",
            return_value=batch_uploader,
        ) as batch_uploader_cls:
            result = case_service_upload_cases(self.service, cmd)

        assert result is batch_result
        batch_uploader_cls.assert_called_once_with(self.service)
        batch_uploader.upload_batch.assert_called_once_with(cmd)


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseUploadSeqdbBridge(BaseUploadTestCase):
    """Tests for the casedb-to-seqdb upload bridge in CaseBatchUploader."""

    def test_get_upload_samples_command_returns_none_without_children(self) -> None:
        case_for_upload = self.create_case_for_upload(read_sets=[], seqs=[])
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        success, upload_samples_cmd, child_map = (
            self.batch_uploader._get_upload_samples_command(
                cmd,
                batch_result,
            )
        )

        assert success
        assert upload_samples_cmd is None
        assert dict(child_map) == {}

    def test_get_upload_samples_command_builds_seqdb_batch(self) -> None:
        case_for_upload = self.create_case_for_upload(
            read_sets=[self.create_read_set_for_upload()],
            seqs=[self.create_seq_for_upload()],
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        success, upload_samples_cmd, child_map = (
            self.batch_uploader._get_upload_samples_command(
                cmd,
                batch_result,
            )
        )

        assert success
        assert upload_samples_cmd is not None
        assert len(upload_samples_cmd.sample_batch.samples) == 1
        sample = upload_samples_cmd.sample_batch.samples[0]
        assert len(sample.read_sets or []) == 1
        assert len(sample.seqs or []) == 1
        assert upload_samples_cmd.user == self.user
        assert (0, 0) in child_map[seqdb_model.ReadSetForUpload]
        assert (0, 0) in child_map[seqdb_model.SeqForUpload]

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

        assert success
        handled_cmd = self.service.app.handle.call_args[0][0]
        assert handled_cmd.verify_only
        assert case_for_upload.case is not None
        assert case_for_upload.case.content[self.reads_col_id] == str(
            created_read_set_id
        )
        assert case_for_upload.case.content[self.seq_col_id] == str(created_seq_id)
        assert batch_result.cases[0].read_sets is not None
        assert batch_result.cases[0].seqs is not None
        assert batch_result.cases[0].read_sets[0].id == created_read_set_id
        assert batch_result.cases[0].seqs[0].id == created_seq_id

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

        assert not success

    def test_get_upload_samples_command_accepts_sample_id_without_external_id(
        self,
    ) -> None:
        case_for_upload = self.create_case_for_upload(
            read_sets=[self.create_read_set_for_upload_sample_id_only()],
            seqs=None,
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        success, upload_samples_cmd, child_map = (
            self.batch_uploader._get_upload_samples_command(
                cmd,
                batch_result,
            )
        )

        assert success
        assert upload_samples_cmd is not None
        assert len(upload_samples_cmd.sample_batch.samples) == 1
        sample = upload_samples_cmd.sample_batch.samples[0]
        assert sample.id == self.sample_id
        assert sample.sample is not None
        assert sample.sample.id == self.sample_id
        assert sample.identifiers == []
        assert len(sample.read_sets or []) == 1
        assert (0, 0) in child_map[seqdb_model.ReadSetForUpload]


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseDateMutability:
    def test_timed_at_is_mutable_always(self) -> None:
        props = STORED_MODEL_FIELD_PROPS.get(model.Case, {})
        timed_at_props = props.get("timed_at")
        assert (
            timed_at_props is not None
        ), "timed_at missing from STORED_MODEL_FIELD_PROPS"
        assert (
            timed_at_props.is_mutable_always
        ), "timed_at.is_mutable_always must be True so updates persist"


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestUpsertBatchCaseDate(BaseUploadTestCase):
    def test_calculated_timed_at_preserved_for_existing_case(self) -> None:
        """After re-validation, timed_at set by calculate_timed_at must not
        be reset to None."""
        uploader, service = self.create_uploader()

        case_type_id = uuid4()
        created_in_data_collection_id = uuid4()
        case_id = uuid4()
        sampling_col_id = uuid4()
        content: dict = {sampling_col_id: "2024-03-15"}
        expected_date = datetime.datetime(2024, 3, 15)

        case = model.Case(
            id=case_id,
            case_type_id=case_type_id,
            created_in_data_collection_id=created_in_data_collection_id,
            content=dict(content),
        )
        case_for_upload = model.CaseForUpload(case=case)
        case_result = model.CaseUploadResult(validated_content=dict(content))
        cmd = command.UploadCasesCommand(
            user=self.create_org_user(),
            case_type_id=case_type_id,
            default_created_in_data_collection_id=created_in_data_collection_id,
            case_batch=model.CaseBatchForUpload(cases=[case_for_upload]),
            on_exists=UploadAction.UPDATE.value,  # type: ignore[call-arg]
        )
        batch_result = model.CaseBatchUploadResult(cases=[case_result])

        # read_fields returns rows with JSON-serialised (string-keyed) content,
        # mirroring what the actual repository layer produces.
        service.repository.read_fields.return_value = [
            (case_id, {str(x): y for x, y in content.items()})
        ]

        mock_validator = Mock()

        def _set_date(inner_cmd: command.UploadCasesCommand, _result: object) -> None:
            for cfu in inner_cmd.case_batch.cases:
                if cfu.case is not None:
                    cfu.case.timed_at = expected_date

        mock_validator.validate_and_transform.side_effect = _set_date

        with (
            patch.object(uploader, "_get_complete_case_type", return_value=Mock()),
            patch.object(uploader, "_get_case_validator", return_value=mock_validator),
            patch(
                "gen_epix.commondb.services.upload.BatchUploader.upsert_batch",
                return_value=True,
            ),
        ):
            uploader.upsert_batch(cmd, batch_result, Mock())

        assert case.timed_at == expected_date


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseCohortUploadUpdates(BaseUploadTestCase):
    @pytest.mark.parametrize(
        "existing_cohort, uploaded_cohort, expected_cohort",
        [
            ({}, "same", "same"),
            ("old", "new", "new"),
            ("same", None, {}),
        ],
    )
    def test_upload_case_cohort_updates(
        self,
        existing_cohort: dict[UUID, UUID | None] | str,
        uploaded_cohort: dict[UUID, UUID | None] | str | None,
        expected_cohort: dict[UUID, UUID | None] | str,
    ) -> None:
        cohort_id = UUID("550e8400-e29b-41d4-a716-446655440009")
        old_definition_id = UUID("550e8400-e29b-41d4-a716-446655440010")
        new_definition_id = UUID("550e8400-e29b-41d4-a716-446655440011")

        def _resolve(
            value: dict[UUID, UUID | None] | str | None,
        ) -> dict[UUID, UUID | None]:
            if isinstance(value, dict):
                return value
            if value == "same":
                return {cohort_id: old_definition_id}
            if value == "old":
                return {cohort_id: old_definition_id}
            if value == "new":
                return {cohort_id: new_definition_id}
            if value is None:
                return {cohort_id: None}
            raise AssertionError(f"Unexpected value: {value}")

        existing_case = self.create_case(cohort=_resolve(existing_cohort))
        uploaded_case = self.create_case(cohort=_resolve("same"))
        uploaded_case.cohort = _resolve(uploaded_cohort)

        success, result, updated_objs = self.update_case(existing_case, uploaded_case)

        assert success
        assert result.status == EtlStatus.UPDATED
        assert len(updated_objs) == 1

        if isinstance(expected_cohort, dict):
            expected = expected_cohort
        elif expected_cohort == "same":
            expected = {cohort_id: old_definition_id}
        elif expected_cohort == "new":
            expected = {cohort_id: new_definition_id}
        else:
            raise AssertionError(f"Unexpected expected value: {expected_cohort}")

        assert updated_objs[0].cohort == expected


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestExistingContentKeyNormalization(BaseUploadTestCase):
    """read_fields row[1] keys may be UUID objects (DICT) or strings (SQL);
    both must be normalised to UUID before content merging."""

    def _run_upsert_with_existing_key(self, existing_key: UUID | str) -> dict:
        uploader, service = self.create_uploader()
        col_id = self.reads_col_id
        case = model.Case(
            id=self.case_id,
            case_type_id=self.case_type_id,
            created_in_data_collection_id=self.data_collection_id,
            content={col_id: "new"},
        )
        case_result = model.CaseUploadResult(validated_content={col_id: "new"})
        cmd = command.UploadCasesCommand(
            user=self.create_org_user(),
            case_type_id=self.case_type_id,
            default_created_in_data_collection_id=self.data_collection_id,
            case_batch=model.CaseBatchForUpload(cases=[model.CaseForUpload(case=case)]),
            on_exists=UploadAction.UPDATE.value,  # type: ignore[call-arg]
        )
        batch_result = model.CaseBatchUploadResult(cases=[case_result])
        service.repository.read_fields.return_value = [
            (self.case_id, {existing_key: "old"})
        ]
        with (
            patch.object(uploader, "_get_complete_case_type", return_value=Mock()),
            patch.object(uploader, "_get_case_validator", return_value=Mock()),
            patch(
                "gen_epix.commondb.services.upload.BatchUploader.upsert_batch",
                return_value=True,
            ),
        ):
            uploader.upsert_batch(cmd, batch_result, Mock())
        return case.content

    def test_uuid_keys_from_dict_repo_are_accepted(self) -> None:
        # Pre-fix: UUID(uuid_obj) raised AttributeError; must not raise now
        content = self._run_upsert_with_existing_key(self.reads_col_id)
        assert self.reads_col_id in content

    def test_string_keys_from_sql_repo_are_converted_to_uuid(self) -> None:
        content = self._run_upsert_with_existing_key(str(self.reads_col_id))
        assert self.reads_col_id in content


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseContentUploadUpdates(BaseUploadTestCase):
    @pytest.mark.parametrize(
        "existing_value, uploaded_value, expected_content",
        [
            (None, "new-value", "new-value"),
            ("old-value", "new-value", "new-value"),
            ("old-value", None, {}),
        ],
    )
    def test_upload_case_content_updates(
        self,
        existing_value: str | None,
        uploaded_value: str | None,
        expected_content: str | dict[UUID, str],
    ) -> None:
        col_id = self.reads_col_id

        existing_content: dict[UUID, str | None] = {}
        if existing_value is not None:
            existing_content = {col_id: existing_value}

        existing_case = self.create_case(
            content=cast(dict[UUID, str | None], existing_content)
        )
        uploaded_case = self.create_case(
            content=cast(dict[UUID, str | None], dict(existing_content))
        )
        uploaded_case.content = {col_id: uploaded_value}

        success, result, updated_objs = self.update_case(existing_case, uploaded_case)

        assert success
        assert result.status == EtlStatus.UPDATED
        assert len(updated_objs) == 1

        if isinstance(expected_content, dict):
            expected = expected_content
        else:
            expected = {col_id: expected_content}

        assert updated_objs[0].content == expected
        assert all(value is not None for value in updated_objs[0].content.values())


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseContentUpsertPersistence(BaseUploadTestCase):
    def test_upsert_batch_create_does_not_persist_none_content_values(self) -> None:
        col_to_drop = uuid4()
        col_to_keep = self.reads_col_id
        created_case_id = uuid4()

        case_for_upload = self.create_case_for_upload(
            case_id=NULL_ID,
            content={col_to_drop: None, col_to_keep: "new"},
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)
        batch_result.cases[0].is_new = True
        batch_result.cases[0].validated_content = dict(case_for_upload.case.content)  # type: ignore[union-attr]

        uploader, service = self.create_uploader()
        service.generate_id = Mock(return_value=created_case_id)
        persisted_create_objs: list[model.Case] = []

        def _crud_side_effect(
            _uow: Mock,
            _user_id: UUID | None,
            model_class: type[model.Model],
            operation: CrudOperation,
            **kwargs: object,
        ) -> list[model.Case] | list[UUID]:
            if model_class is not model.Case:
                return []
            if operation == CrudOperation.CREATE_SOME:
                objs = kwargs.get("objs")
                assert isinstance(objs, list)
                persisted_create_objs.extend(cast(list[model.Case], objs))
                return [created_case_id]
            return []

        service.repository.crud.side_effect = _crud_side_effect

        with (
            patch.object(uploader, "_get_complete_case_type", return_value=Mock()),
            patch.object(uploader, "_get_case_validator", return_value=Mock()),
        ):
            success = uploader.upsert_batch(cmd, batch_result, Mock())

        assert success
        assert len(persisted_create_objs) == 1
        assert persisted_create_objs[0].content == {col_to_keep: "new"}
        assert all(
            value is not None for value in persisted_create_objs[0].content.values()
        )

    def test_upsert_batch_update_does_not_persist_none_content_values(self) -> None:
        col_to_delete = uuid4()
        col_to_keep = self.reads_col_id
        case_id = self.case_id

        case_for_upload = self.create_case_for_upload(
            case_id=case_id,
            content={col_to_delete: None, col_to_keep: "new"},
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)
        batch_result.cases[0].is_new = False
        batch_result.cases[0].validated_content = dict(case_for_upload.case.content)  # type: ignore[union-attr]

        uploader, service = self.create_uploader()
        persisted_update_objs: list[model.Case] = []
        existing_case = self.create_case(
            case_id=case_id,
            content={col_to_delete: "old", col_to_keep: "old"},
        )

        def _crud_side_effect(
            _uow: Mock,
            _user_id: UUID | None,
            model_class: type[model.Model],
            operation: CrudOperation,
            **kwargs: object,
        ) -> list[model.Case] | list[UUID]:
            if model_class is not model.Case:
                return []
            if operation == CrudOperation.READ_SOME:
                return [existing_case]
            if operation == CrudOperation.UPDATE_SOME:
                objs = kwargs.get("objs")
                assert isinstance(objs, list)
                persisted_update_objs.extend(cast(list[model.Case], objs))
                return [case_id]
            return []

        service.repository.crud.side_effect = _crud_side_effect
        service.repository.read_fields.return_value = [
            (case_id, {str(col_to_delete): "old", str(col_to_keep): "old"})
        ]

        with (
            patch.object(uploader, "_get_complete_case_type", return_value=Mock()),
            patch.object(uploader, "_get_case_validator", return_value=Mock()),
        ):
            success = uploader.upsert_batch(cmd, batch_result, Mock())

        assert success
        assert len(persisted_update_objs) == 1
        assert persisted_update_objs[0].content == {col_to_keep: "new"}
        assert all(
            value is not None for value in persisted_update_objs[0].content.values()
        )


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestUpsertBatchContentDeletionDelta(BaseUploadTestCase):
    """
    LSP-3647 regression: CaseBatchUploader.upsert_batch merges incoming
    content into the existing DB content to re-validate the full resulting
    state, which resolves a deletion into mere key-absence. If that merged
    state were passed on as-is, the generic BatchUploader.upsert_batch could
    never detect the deletion, since it re-derives its own diff from a fresh
    DB read and only recognizes a deletion via an explicit {key: None}
    entry. The content handed to the generic upsert must therefore still be
    the pre-merge delta, not the merged state.
    """

    def test_content_deletion_delta_is_restored_before_generic_upsert(self) -> None:
        col_id = self.reads_col_id
        case = self.create_case(content={col_id: None})
        case_result = model.CaseUploadResult(validated_content={col_id: None})
        cmd = command.UploadCasesCommand(
            user=self.create_org_user(),
            case_type_id=self.case_type_id,
            default_created_in_data_collection_id=self.data_collection_id,
            case_batch=model.CaseBatchForUpload(cases=[model.CaseForUpload(case=case)]),
            on_exists=UploadAction.UPDATE.value,  # type: ignore[call-arg]
        )
        batch_result = model.CaseBatchUploadResult(cases=[case_result])

        uploader, service = self.create_uploader()
        service.repository.read_fields.return_value = [
            (self.case_id, {col_id: "old-value"})
        ]
        with (
            patch.object(uploader, "_get_complete_case_type", return_value=Mock()),
            patch.object(uploader, "_get_case_validator", return_value=Mock()),
            patch(
                "gen_epix.commondb.services.upload.BatchUploader.upsert_batch",
                return_value=True,
            ) as mock_generic_upsert,
        ):
            uploader.upsert_batch(cmd, batch_result, Mock())

        persisted_cmd = mock_generic_upsert.call_args.args[0]
        persisted_case = persisted_cmd.case_batch.cases[0].case
        assert persisted_case.content == {col_id: None}


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseForUploadContentSerialization(BaseUploadTestCase):
    """
    LSP-3645: a None content value signals "delete this key" and must
    survive serialization for both upload wrappers and plain Case payloads.
    Persistence logic must still interpret None as delete-intent and not
    store None in the final persisted case content.
    """

    def test_case_for_upload_preserves_none_content_value(self) -> None:
        deleted_col_id = uuid4()
        case_for_upload = self.create_case_for_upload(
            content={deleted_col_id: None, self.reads_col_id: "kept"}
        )

        dumped = case_for_upload.model_dump(mode="json")

        assert dumped["case"]["content"] == {
            str(deleted_col_id): None,
            str(self.reads_col_id): "kept",
        }

    def test_plain_case_also_serializes_none_content_value(self) -> None:
        deleted_col_id = uuid4()
        case = self.create_case(
            content={deleted_col_id: None, self.reads_col_id: "kept"}
        )

        dumped = case.model_dump(mode="json")

        assert dumped["content"] == {
            str(deleted_col_id): None,
            str(self.reads_col_id): "kept",
        }


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestVerifyUserRights(BaseUploadTestCase):
    """Tests for RBAC verification in CaseBatchUploader.verify_user_rights."""

    def _make_cmd(self, user: User | None = None) -> command.UploadCasesCommand:
        case_batch = model.CaseBatchForUpload(
            batch_id=self.batch_id,  # type: ignore[call-arg]
            cases=[self.create_case_for_upload()],
        )
        return command.UploadCasesCommand(
            user=user,
            case_type_id=self.case_type_id,
            default_created_in_data_collection_id=self.data_collection_id,
            case_batch=case_batch,
            on_exists=UploadAction.UPDATE,  # type: ignore[call-arg]
            on_new=UploadAction.CREATE,  # type: ignore[call-arg]
        )

    def test_raises_for_invalid_command_type(self) -> None:
        with pytest.raises(exc.InvalidArgumentsError):
            self.batch_uploader.verify_user_rights(Mock())

    def test_raises_for_user_with_only_guest_role(self) -> None:
        # GUEST is not in GE_ORG_USER (ROOT, APP_ADMIN, ORG_ADMIN, ORG_USER)
        guest_user = User(
            id=uuid4(),
            key="guest@example.com",
            email="guest@example.com",
            roles={enum.Role.GUEST.value},
            organization_id=uuid4(),
            is_active=True,
        )
        cmd = self._make_cmd(user=guest_user)
        with pytest.raises(exc.UnauthorizedAuthError):
            self.batch_uploader.verify_user_rights(cmd)

    @pytest.mark.parametrize(
        "email, role",
        [
            ("org@example.com", enum.Role.ORG_USER),
            ("admin@example.com", enum.Role.APP_ADMIN),
        ],
    )
    def test_succeeds_for_allowed_roles(self, email: str, role: enum.Role) -> None:
        user = User(
            id=uuid4(),
            key=email,
            email=email,
            roles={role.value},
            organization_id=uuid4(),
            is_active=True,
        )
        self.batch_uploader.verify_user_rights(self._make_cmd(user=user))

    def test_succeeds_for_none_user(self) -> None:
        # user=None bypasses the role intersection check entirely
        self.batch_uploader.verify_user_rights(self._make_cmd(user=None))


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestSetDefaultCreatedInDataCollectionId(BaseUploadTestCase):
    """Tests for default_created_in_data_collection_id behavior.

    NOTE: Direct unit testing of set_default_created_in_data_collection_id is complex
    due to DataCollectionCrudCommand validation. Integration tests in the
    service layer verify the overall behavior.
    """

    def test_error_when_no_default_and_case_needs_one(self) -> None:
        """When new case has NULL_ID and no default, should add error."""
        case_for_upload = self.create_case_for_upload(
            created_in_data_collection_id=NULL_ID
        )
        cmd, batch_result = self.create_command_and_result(
            case_for_upload,
            default_created_in_data_collection_id=NULL_ID,
        )
        batch_result.cases[0].is_new = True

        success = self.batch_uploader._set_default_created_in_data_collection_id(
            cmd, batch_result
        )

        assert not success
        assert batch_result.cases[0].status == EtlStatus.FAILED
        assert batch_result.cases[0].has_errors()

    def test_new_case_with_explicit_created_in_dc_id_unchanged(self) -> None:
        """When case explicitly sets created_in_data_collection_id, don't override."""
        dc_id_explicit = uuid4()
        case_for_upload = self.create_case_for_upload(
            created_in_data_collection_id=dc_id_explicit
        )
        cmd, batch_result = self.create_command_and_result(
            case_for_upload,
            default_created_in_data_collection_id=self.data_collection_id,
        )
        batch_result.cases[0].is_new = True

        with (
            patch(
                "gen_epix.casedb.services.case.upload.command.DataCollectionCrudCommand",
                return_value=Mock(),
            ),
            patch.object(
                self.batch_uploader.service.app,
                "handle",
                return_value=True,
            ),
        ):
            success = self.batch_uploader._set_default_created_in_data_collection_id(
                cmd, batch_result
            )

        assert success
        assert case_for_upload.case is not None
        assert case_for_upload.case.created_in_data_collection_id == dc_id_explicit

    def test_existing_case_created_in_dc_id_preserved(self) -> None:
        """Existing cases should not be modified by default setting."""
        dc_id_existing = uuid4()
        case_for_upload = self.create_case_for_upload(
            case_id=uuid4(),
            created_in_data_collection_id=dc_id_existing,
        )
        cmd, batch_result = self.create_command_and_result(
            case_for_upload,
            default_created_in_data_collection_id=self.data_collection_id,
        )
        batch_result.cases[0].is_new = False

        with (
            patch(
                "gen_epix.casedb.services.case.upload.command.DataCollectionCrudCommand",
                return_value=Mock(),
            ),
            patch.object(
                self.batch_uploader.service.app,
                "handle",
                return_value=True,
            ),
        ):
            success = self.batch_uploader._set_default_created_in_data_collection_id(
                cmd, batch_result
            )

        assert success
        assert case_for_upload.case is not None
        assert case_for_upload.case.created_in_data_collection_id == dc_id_existing


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseDataCollectionIdHandling(BaseUploadTestCase):
    """Tests for handling cases with different created_in_data_collection_id values."""

    def test_new_case_with_explicit_data_collection_id(self) -> None:
        """New case with explicit DC ID should use that DC for ABAC."""
        explicit_dc_id = uuid4()
        case_for_upload = self.create_case_for_upload(
            created_in_data_collection_id=explicit_dc_id
        )
        cmd, batch_result = self.create_command_and_result(
            case_for_upload,
            default_created_in_data_collection_id=self.data_collection_id,
        )

        assert case_for_upload.case is not None
        assert case_for_upload.case.created_in_data_collection_id == explicit_dc_id

    def test_batch_with_multiple_different_data_collection_ids(self) -> None:
        """Batch can contain cases from different DCs."""
        dc_id_1 = uuid4()
        dc_id_2 = uuid4()

        case1 = self.create_case_for_upload(
            case_id=uuid4(), created_in_data_collection_id=dc_id_1
        )
        case2 = self.create_case_for_upload(
            case_id=uuid4(), created_in_data_collection_id=dc_id_2
        )

        cmd, batch_result = self.create_command_and_result([case1, case2])

        assert len(batch_result.cases) == 2
        assert case1.case is not None
        assert case2.case is not None
        assert case1.case.created_in_data_collection_id == dc_id_1
        assert case2.case.created_in_data_collection_id == dc_id_2


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestExistingCaseDataCollectionMutability(BaseUploadTestCase):
    """
    Tests for existing case data collection handling, including NULL_ID edge case.

    NOTE: Currently (per upload.py line 284-285), uploading an existing case with
    created_in_data_collection_id=NULL_ID is not implemented. This would require:

    1. In verify_batch: Detect cases where is_new=False and created_in_data_collection_id=NULL_ID
    2. Query DB for the existing case's actual created_in_data_collection_id
    3. Replace NULL_ID with the actual value
    4. Validation in commondb.BatchUploader checks immutability (field should not change)

    This prevents accidental modification of the case's origin DC. If needed, a new
    method like 'replace_null_id_with_actual_created_in_dc' should be added to
    set_default_created_in_data_collection_id or called separately in verify_batch.
    """

    def test_existing_case_preserves_created_in_data_collection_id(self) -> None:
        """Existing case should maintain its created_in_data_collection_id."""
        dc_id_existing = uuid4()
        case_id_existing = uuid4()

        case_for_upload = self.create_case_for_upload(
            case_id=case_id_existing,
            created_in_data_collection_id=dc_id_existing,
        )
        existing_case = self.create_case(
            case_id=case_id_existing,
            created_in_data_collection_id=dc_id_existing,
        )
        assert case_for_upload.case is not None

        success, result, updated_objs = self.update_case(
            existing_case, case_for_upload.case
        )

        assert success
        assert result.status == EtlStatus.SKIPPED
        assert len(updated_objs) == 0

    def test_existing_case_with_different_created_in_data_collection_id_fails(
        self,
    ) -> None:
        """Existing cases must not be changed to a different created_in_data_collection_id."""
        case_id_existing = uuid4()
        existing_dc_id = uuid4()
        different_dc_id = uuid4()

        existing_case = self.create_case(
            case_id=case_id_existing,
            created_in_data_collection_id=existing_dc_id,
        )
        uploaded_case = self.create_case(
            case_id=case_id_existing,
            created_in_data_collection_id=different_dc_id,
        )

        success, result, updated_objs = self.update_case(existing_case, uploaded_case)

        # update_objects logs per-object immutable-field errors but does not abort batch.
        assert success
        assert result.status == EtlStatus.FAILED
        assert len(updated_objs) == 0


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestVerifyAbacRights(BaseUploadTestCase):
    """Tests for ABAC column and creation-right verification in verify_abac_rights."""

    def _make_abac(
        self,
        data_collection_id: UUID,
        is_private: bool = True,
        add_case: bool = True,
        read_col_ids: set[UUID] | None = None,
        write_col_ids: set[UUID] | None = None,
    ) -> CaseTypeAccessAbac:
        return CaseTypeAccessAbac(
            case_type_id=self.case_type_id,
            data_collection_id=data_collection_id,
            is_private=is_private,
            add_case=add_case,
            remove_case=False,
            add_case_set=False,
            remove_case_set=False,
            read_col_ids=read_col_ids or set(),
            write_col_ids=write_col_ids or set(),
            read_case_set=False,
            write_case_set=False,
        )

    def _call(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
        case_type_access_abacs: dict[UUID, CaseTypeAccessAbac],
        case_data_collections: list[frozenset[UUID]] | None = None,
    ) -> bool:
        mock_cct = Mock()
        mock_cct.case_type_access_abacs = case_type_access_abacs
        if case_data_collections is None:
            case_data_collections = [
                frozenset({self.data_collection_id}) for _ in cmd.case_batch.cases
            ]
        with (
            patch.object(
                self.batch_uploader, "_get_complete_case_type", return_value=mock_cct
            ),
            patch.object(
                self.batch_uploader,
                "_get_case_data_collections",
                return_value=case_data_collections,
            ),
        ):
            return self.batch_uploader._verify_abac_rights(cmd, batch_result, self.uow)

    # --- new-case creation rights ---

    def test_new_case_in_allowed_private_dc_succeeds(self) -> None:
        col_id = uuid4()
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={col_id: "v"})
        )
        batch_result.cases[0].is_new = True
        abac = self._make_abac(
            self.data_collection_id,
            is_private=True,
            add_case=True,
            write_col_ids={col_id},
        )
        result = self._call(cmd, batch_result, {self.data_collection_id: abac})

        assert result
        assert batch_result.cases[0].status == EtlStatus.PENDING
        assert len(batch_result.cases[0].data_issues) == 0

    def test_new_case_in_dc_without_add_case_fails(self) -> None:
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={})
        )
        batch_result.cases[0].is_new = True
        abac = self._make_abac(self.data_collection_id, is_private=True, add_case=False)
        result = self._call(cmd, batch_result, {self.data_collection_id: abac})

        assert not result
        assert batch_result.cases[0].status == EtlStatus.FAILED

    def test_new_case_in_non_private_dc_fails(self) -> None:
        # is_private=False → DC never enters allowed_created_data_collection_ids
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={})
        )
        batch_result.cases[0].is_new = True
        abac = self._make_abac(self.data_collection_id, is_private=False, add_case=True)
        result = self._call(cmd, batch_result, {self.data_collection_id: abac})

        assert not result

    def test_existing_case_skips_creation_check(self) -> None:
        # is_new=False → creation check is skipped even when add_case=False
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={})
        )
        batch_result.cases[0].is_new = False
        abac = self._make_abac(self.data_collection_id, is_private=True, add_case=False)
        result = self._call(cmd, batch_result, {self.data_collection_id: abac})

        assert result

    # --- column access ---

    def test_writeable_col_causes_no_data_issue(self) -> None:
        col_id = uuid4()
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={col_id: "value"})
        )
        abac = self._make_abac(self.data_collection_id, write_col_ids={col_id})
        self._call(cmd, batch_result, {self.data_collection_id: abac})

        assert len(batch_result.cases[0].data_issues) == 0
        # col is still in content
        assert col_id in cmd.case_batch.cases[0].case.content  # type: ignore[union-attr]

    def test_read_only_col_adds_unauthorized_issue_and_removes_from_content(
        self,
    ) -> None:
        col_id = uuid4()
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={col_id: "value"})
        )
        abac = self._make_abac(
            self.data_collection_id,
            read_col_ids={col_id},
            write_col_ids=set(),
        )
        self._call(cmd, batch_result, {self.data_collection_id: abac})

        issues = batch_result.cases[0].data_issues
        assert len(issues) == 1
        assert issues[0].data_issue_type == DataIssueType.UNAUTHORIZED
        assert issues[0].code == "3e7c1a9f"
        assert issues[0].original_value == "value"
        assert col_id not in cmd.case_batch.cases[0].case.content  # type: ignore[union-attr]

    def test_inaccessible_col_adds_unknown_col_issue_and_removes_from_content(
        self,
    ) -> None:
        col_id = uuid4()
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={col_id: "secret"})
        )
        abac = self._make_abac(
            self.data_collection_id,
            read_col_ids=set(),
            write_col_ids=set(),
        )
        self._call(cmd, batch_result, {self.data_collection_id: abac})

        issues = batch_result.cases[0].data_issues
        assert len(issues) == 1
        assert issues[0].data_issue_type == DataIssueType.UNAUTHORIZED
        assert issues[0].code == "a7b3f9d2"
        assert col_id not in cmd.case_batch.cases[0].case.content  # type: ignore[union-attr]

    def test_unauthorized_read_set_col_adds_issue_with_none_orig_value(
        self,
    ) -> None:
        # col_id comes from a read_set (not content) → original_value must be None
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(
                content={}, read_sets=[self.create_read_set_for_upload()]
            )
        )
        abac = self._make_abac(self.data_collection_id, write_col_ids=set())
        self._call(cmd, batch_result, {self.data_collection_id: abac})

        issues = batch_result.cases[0].data_issues
        assert len(issues) == 1
        assert issues[0].col_id == self.reads_col_id
        assert issues[0].original_value is None

    def test_unauthorized_seq_col_adds_issue_with_none_orig_value(self) -> None:
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={}, seqs=[self.create_seq_for_upload()])
        )
        abac = self._make_abac(self.data_collection_id, write_col_ids=set())
        self._call(cmd, batch_result, {self.data_collection_id: abac})

        issues = batch_result.cases[0].data_issues
        assert len(issues) == 1
        assert issues[0].col_id == self.seq_col_id
        assert issues[0].original_value is None

    def test_dc_absent_from_abacs_denies_all_col_access(self) -> None:
        col_id = uuid4()
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={col_id: "v"})
        )
        # empty dict → DC not found → no write access
        self._call(cmd, batch_result, {})

        assert len(batch_result.cases[0].data_issues) == 1

    def test_col_access_cached_for_repeated_data_collection(self) -> None:
        col_id = uuid4()
        case1 = self.create_case_for_upload(case_id=uuid4(), content={col_id: "v1"})
        case2 = self.create_case_for_upload(case_id=uuid4(), content={col_id: "v2"})
        cmd, batch_result = self.create_command_and_result([case1, case2])

        abac = self._make_abac(self.data_collection_id, write_col_ids={col_id})
        result = self._call(
            cmd,
            batch_result,
            {self.data_collection_id: abac},
            case_data_collections=[
                frozenset({self.data_collection_id}),
                frozenset({self.data_collection_id}),
            ],
        )

        assert result
        assert len(batch_result.cases[0].data_issues) == 0
        assert len(batch_result.cases[1].data_issues) == 0

    def test_write_access_is_union_across_multiple_data_collections(self) -> None:
        col1_id, col2_id = uuid4(), uuid4()
        dc2_id = uuid4()
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={col1_id: "a", col2_id: "b"})
        )
        abac1 = self._make_abac(self.data_collection_id, write_col_ids={col1_id})
        abac2 = self._make_abac(dc2_id, write_col_ids={col2_id})
        result = self._call(
            cmd,
            batch_result,
            {self.data_collection_id: abac1, dc2_id: abac2},
            case_data_collections=[frozenset({self.data_collection_id, dc2_id})],
        )

        assert result
        assert len(batch_result.cases[0].data_issues) == 0


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestGetUploadSamplesCommandNoCaseGuard(BaseUploadTestCase):
    """Tests for the has_case guard added to _get_upload_samples_command."""

    def test_read_set_without_case_returns_failure_and_marks_result_failed(
        self,
    ) -> None:
        case_for_upload = model.CaseForUpload(
            id=self.case_id,
            case=None,
            read_sets=[self.create_read_set_for_upload()],
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        success, upload_samples_cmd, _ = (
            self.batch_uploader._get_upload_samples_command(cmd, batch_result)
        )

        assert not success
        # Command is still built (contains the sample) but upload_samples will abort
        assert upload_samples_cmd is not None
        assert batch_result.cases[0].read_sets[0].status == EtlStatus.FAILED  # type: ignore[index]

    def test_seq_without_case_returns_failure_and_marks_result_failed(self) -> None:
        case_for_upload = model.CaseForUpload(
            id=self.case_id,
            case=None,
            seqs=[self.create_seq_for_upload()],
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        success, upload_samples_cmd, _ = (
            self.batch_uploader._get_upload_samples_command(cmd, batch_result)
        )

        assert not success
        assert upload_samples_cmd is not None
        assert batch_result.cases[0].seqs[0].status == EtlStatus.FAILED  # type: ignore[index]

    def test_upload_samples_aborts_early_when_no_case(self) -> None:
        # upload_samples should return False immediately without calling seqdb
        case_for_upload = model.CaseForUpload(
            id=self.case_id,
            case=None,
            read_sets=[self.create_read_set_for_upload()],
        )
        cmd, batch_result = self.create_command_and_result(case_for_upload)

        success = self.batch_uploader.upload_samples(
            cmd, batch_result, verify_only=True
        )

        assert not success
        self.service.app.handle.assert_not_called()


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCaseBatchHasSamples(BaseUploadTestCase):
    """Tests for CaseBatchForUpload.has_samples (the pure predicate on the batch model)."""

    def test_has_samples_false_when_no_children_fields_set(self) -> None:
        cmd, _ = self.create_command_and_result(self.create_case_for_upload())
        assert not cmd.case_batch.has_samples()

    def test_has_samples_false_with_empty_read_sets_and_seqs(self) -> None:
        cmd, _ = self.create_command_and_result(
            self.create_case_for_upload(read_sets=[], seqs=[])
        )
        assert not cmd.case_batch.has_samples()

    @pytest.mark.parametrize("sample_kind", ["read_sets", "seqs"])
    def test_has_samples_true_when_case_has_children(self, sample_kind: str) -> None:
        if sample_kind == "read_sets":
            case_for_upload = self.create_case_for_upload(
                read_sets=[self.create_read_set_for_upload()]
            )
        else:
            case_for_upload = self.create_case_for_upload(
                seqs=[self.create_seq_for_upload()]
            )

        cmd, _ = self.create_command_and_result(case_for_upload)
        assert cmd.case_batch.has_samples()

    def test_upsert_batch_skips_seqdb_upload_when_no_samples(self) -> None:
        # When has_samples() is False, upload_samples must never be called
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload(content={})
        )
        with (
            patch.object(
                self.batch_uploader, "_get_complete_case_type", return_value=Mock()
            ),
            patch.object(
                self.batch_uploader, "_get_case_validator", return_value=Mock()
            ),
            patch(
                "gen_epix.commondb.services.upload.BatchUploader.upsert_batch",
                return_value=True,
            ),
            patch.object(self.batch_uploader, "upload_samples") as mock_upload_samples,
        ):
            self.batch_uploader.upsert_batch(cmd, batch_result, self.uow)

        mock_upload_samples.assert_not_called()


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestGetCaseDataCollections(BaseUploadTestCase):
    """Tests for _get_case_data_collections in CaseBatchUploader."""

    def test_new_case_uses_only_created_in_dc_and_skips_db_query(self) -> None:
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload()
        )
        batch_result.cases[0].is_new = True  # is_existing = False → no DB query

        result = self.batch_uploader._get_case_data_collections(
            cmd, batch_result, self.uow
        )

        assert len(result) == 1
        assert result[0] == frozenset({self.data_collection_id})
        self.service.repository.crud.assert_not_called()

    def test_existing_case_includes_dc_links_from_db(self) -> None:
        cmd, batch_result = self.create_command_and_result(
            self.create_case_for_upload()
        )
        batch_result.cases[0].is_new = False  # is_existing = True → DB queried

        extra_dc_id = uuid4()
        link = model.CaseDataCollectionLink.model_construct(
            case_id=self.case_id, data_collection_id=extra_dc_id
        )
        self.service.repository.crud.return_value = [link]

        result = self.batch_uploader._get_case_data_collections(
            cmd, batch_result, self.uow
        )

        assert len(result) == 1
        assert self.data_collection_id in result[0]
        assert extra_dc_id in result[0]

    def test_case_without_case_object_falls_back_to_null_id(self) -> None:
        case_for_upload = model.CaseForUpload(id=self.case_id, case=None)
        cmd, batch_result = self.create_command_and_result(case_for_upload)
        batch_result.cases[0].is_new = True

        result = self.batch_uploader._get_case_data_collections(
            cmd, batch_result, self.uow
        )

        assert len(result) == 1
        assert NULL_ID in result[0]

    def test_mixed_batch_queries_db_only_for_existing_cases(self) -> None:
        new_id = uuid4()
        existing_id = uuid4()
        new_case = self.create_case_for_upload(case_id=new_id)
        existing_case = self.create_case_for_upload(case_id=existing_id)
        cmd, batch_result = self.create_command_and_result([new_case, existing_case])
        batch_result.cases[0].is_new = True  # new_case
        batch_result.cases[1].is_new = False  # existing_case

        self.service.repository.crud.return_value = []

        result = self.batch_uploader._get_case_data_collections(
            cmd, batch_result, self.uow
        )

        assert len(result) == 2
        self.service.repository.crud.assert_called_once()
        # Only existing_id should appear in the filter
        call_kwargs = self.service.repository.crud.call_args
        members = call_kwargs.kwargs["filter"].members
        assert existing_id in members
        assert new_id not in members
