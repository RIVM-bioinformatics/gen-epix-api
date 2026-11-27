from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

import gen_epix.casedb.services.case.upload as case_upload
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload, User
from gen_epix.commondb.domain.model.upload import UploadResult


@pytest.fixture
def sample_identifier() -> IdentifierForUpload:
    return IdentifierForUpload(identifier_issuer_code="LAB", external_id="sample-1")


def _make_uploader(monkeypatch: pytest.MonkeyPatch) -> case_upload.CaseBatchUploader:
    uploader = object.__new__(case_upload.CaseBatchUploader)
    monkeypatch.setattr(
        uploader, "is_null", lambda value: value is None or value == NULL_ID
    )
    return uploader


def _make_sample_upload_cmd_and_result() -> tuple[
    case_upload.command.UploadCasesCommand,
    case_upload.model.CaseBatchUploadResult,
    case_upload.model.ReadSetForUpload,
    case_upload.model.SeqForUpload,
]:
    sample_id = uuid4()
    case = case_upload.model.Case(
        case_type_id=uuid4(),
        created_in_data_collection_id=uuid4(),
        content={},
    )
    read_set = case_upload.model.ReadSetForUpload(
        col_id=uuid4(), sample_id=sample_id, protocol_id=uuid4()
    )
    seq = case_upload.model.SeqForUpload(
        col_id=uuid4(), sample_id=sample_id, protocol_id=uuid4()
    )
    case_for_upload = case_upload.model.CaseForUpload(
        case=case, read_sets=[read_set], seqs=[seq]
    )
    cmd = case_upload.command.UploadCasesCommand(
        case_type_id=case.case_type_id,
        case_batch=case_upload.model.CaseBatchForUpload(cases=[case_for_upload]),
    )
    batch_result = case_upload.model.CaseBatchUploadResult(
        cases=[
            case_upload.model.CaseUploadResult(
                read_sets=[UploadResult()], seqs=[UploadResult()]
            )
        ]
    )
    return cmd, batch_result, read_set, seq


def test_build_sample_batch_rejects_conflicting_ids_across_child_groups(
    monkeypatch: pytest.MonkeyPatch, sample_identifier: IdentifierForUpload
) -> None:
    sample_ids = [uuid4(), uuid4()]
    read_set = Mock(
        sample_id=sample_ids[0],
        other_sample_identifier=sample_identifier,
        protocol_id=uuid4(),
    )
    seq = Mock(
        sample_id=sample_ids[1],
        other_sample_identifier=sample_identifier,
        protocol_id=uuid4(),
    )
    cases = [
        Mock(case=object(), read_sets=[read_set], seqs=[]),
        Mock(case=object(), read_sets=[], seqs=[seq]),
    ]
    cmd = Mock()
    cmd.case_batch.cases = cases
    cmd.default_created_in_data_collection_id = uuid4()
    batch_result = Mock(cases=[Mock(), Mock()])

    result = _make_uploader(monkeypatch)._build_sample_upload_batch(cmd, batch_result)

    assert result == (False, [], {})
    batch_result.add_error.assert_called_once()
    error_args = batch_result.add_error.call_args.args
    assert error_args[0] == "81bd9ed7"
    assert "Inconsistent mapping" in error_args[1]


def test_constructor_rejects_non_case_service() -> None:
    with pytest.raises(case_upload.exc.InvalidArgumentsError, match="915489e8"):
        case_upload.CaseBatchUploader(Mock())


def test_verify_user_rights_accepts_anonymous_command_without_role_lookup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, _, _, _ = _make_sample_upload_cmd_and_result()
    uploader.service = Mock(role_set_map={})

    uploader.verify_user_rights(cmd)

    assert cmd.user is None


def test_verify_user_rights_rejects_user_without_case_role(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, _, _, _ = _make_sample_upload_cmd_and_result()
    user = User(roles={"unrelated-role"}, organization_id=uuid4())
    cmd = cmd.model_copy(update={"user": user})
    uploader.service = Mock()
    uploader.service.role_set_map = {case_upload.RoleSet.GE_ORG_USER: {"case-writer"}}

    with pytest.raises(case_upload.exc.UnauthorizedAuthError, match="d8c05dc7"):
        uploader.verify_user_rights(cmd)


def test_verify_batch_rejects_invalid_command_and_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()

    with pytest.raises(case_upload.exc.InvalidArgumentsError, match="92bef72e"):
        uploader.verify_batch(object(), batch_result, Mock())
    with pytest.raises(case_upload.exc.InvalidArgumentsError, match="42b47de6"):
        uploader.verify_batch(cmd, object(), Mock())


def test_upsert_batch_rejects_invalid_command_and_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()

    with pytest.raises(case_upload.exc.InvalidArgumentsError, match="0935eb52"):
        uploader.upsert_batch(object(), batch_result, Mock())
    with pytest.raises(case_upload.exc.InvalidArgumentsError, match="078d4af1"):
        uploader.upsert_batch(cmd, object(), Mock())


def test_get_complete_case_type_forwards_user_and_policies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, _, _, _ = _make_sample_upload_cmd_and_result()
    user = User(roles={"role"}, organization_id=uuid4())
    cmd = cmd.model_copy(update={"user": user})
    policy = Mock()
    cmd._policies.append(policy)
    uploader.service = Mock()
    expected = Mock()
    uploader.service.retrieve_complete_case_type.return_value = expected

    actual = uploader._get_complete_case_type(cmd)

    assert actual is expected
    retrieve_cmd = uploader.service.retrieve_complete_case_type.call_args.args[0]
    assert retrieve_cmd.user is user
    assert retrieve_cmd._policies == [policy]

    uploader._get_complete_case_type(cmd, ignore_abac=True)
    complete_cmd = uploader.service.retrieve_complete_case_type.call_args.args[0]
    assert complete_cmd.user is None
    assert complete_cmd._policies == []


def test_get_upload_samples_command_preserves_empty_build_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd = case_upload.command.UploadCasesCommand(
        case_type_id=uuid4(),
        case_batch=case_upload.model.CaseBatchForUpload(cases=[]),
    )
    batch_result = case_upload.model.CaseBatchUploadResult(cases=[])
    monkeypatch.setattr(
        uploader, "_build_sample_upload_batch", lambda *_: (False, [], {})
    )

    assert uploader._get_upload_samples_command(cmd, batch_result) == (False, None, {})


def test_get_upload_samples_command_returns_success_for_empty_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd = case_upload.command.UploadCasesCommand(
        case_type_id=uuid4(),
        case_batch=case_upload.model.CaseBatchForUpload(cases=[]),
    )
    batch_result = case_upload.model.CaseBatchUploadResult(cases=[])

    assert uploader._get_upload_samples_command(cmd, batch_result) == (True, None, {})


def test_get_upload_samples_command_builds_deduplicated_sample_and_child_maps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()

    success, samples_cmd, child_index_map = uploader._get_upload_samples_command(
        cmd, batch_result
    )

    assert success
    assert samples_cmd is not None
    assert len(samples_cmd.sample_batch.samples) == 1
    assert len(samples_cmd.sample_batch.samples[0].read_sets or []) == 1
    assert len(samples_cmd.sample_batch.samples[0].seqs or []) == 1
    assert child_index_map[case_upload.seqdb_model.ReadSetForUpload] == {(0, 0): (0, 0)}
    assert child_index_map[case_upload.seqdb_model.SeqForUpload] == {(0, 0): (0, 0)}


def test_map_one_child_result_collection_updates_case_and_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, read_set, _ = _make_sample_upload_cmd_and_result()
    child_id = uuid4()
    seqdb_result = Mock(id=child_id, status=case_upload.EtlStatus.CREATED, logs=[])

    uploader._map_one_child_result_collection(
        cmd,
        batch_result,
        {case_upload.seqdb_model.ReadSetForUpload: {(0, 0): (0, 0)}},
        0,
        case_upload.seqdb_model.ReadSetForUpload,
        "read_sets",
        [seqdb_result],
    )

    assert batch_result.cases[0].read_sets[0].id == child_id
    assert batch_result.cases[0].read_sets[0].status == case_upload.EtlStatus.CREATED
    assert cmd.case_batch.cases[0].case.content[read_set.col_id] == str(child_id)


def test_upload_samples_returns_success_when_there_are_no_samples(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    cmd = case_upload.command.UploadCasesCommand(
        case_type_id=uuid4(),
        case_batch=case_upload.model.CaseBatchForUpload(cases=[]),
    )
    batch_result = case_upload.model.CaseBatchUploadResult(cases=[])

    assert uploader.upload_samples(cmd, batch_result, verify_only=True)

    uploader.service.app.handle.assert_not_called()


def test_upload_samples_skips_seqdb_when_a_child_has_no_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    cmd.case_batch.cases[0].case = None

    assert not uploader.upload_samples(cmd, batch_result, verify_only=True)

    uploader.service.app.handle.assert_not_called()
    assert batch_result.cases[0].read_sets[0].status == case_upload.EtlStatus.FAILED


def test_upload_samples_maps_successful_seqdb_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    cmd, batch_result, read_set, seq = _make_sample_upload_cmd_and_result()
    read_set_id = uuid4()
    seq_id = uuid4()
    seqdb_read_set = Mock(id=read_set_id, status=case_upload.EtlStatus.CREATED, logs=[])
    seqdb_seq = Mock(id=seq_id, status=case_upload.EtlStatus.CREATED, logs=[])
    uploader.service.app.handle.return_value = Mock(
        get_status_count=Mock(return_value={case_upload.EtlStatus.FAILED: 0}),
        samples=[Mock(read_sets=[seqdb_read_set], seqs=[seqdb_seq])],
    )

    assert uploader.upload_samples(cmd, batch_result, verify_only=False)

    upload_cmd = uploader.service.app.handle.call_args.args[0]
    assert not upload_cmd.verify_only
    assert batch_result.cases[0].read_sets[0].id == read_set_id
    assert batch_result.cases[0].seqs[0].id == seq_id
    assert cmd.case_batch.cases[0].case.content == {
        read_set.col_id: str(read_set_id),
        seq.col_id: str(seq_id),
    }


def test_verify_batch_runs_all_stages_after_a_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    verify_samples = Mock(return_value=False)
    verify_generic = Mock(return_value=True)
    set_default = Mock(return_value=True)
    verify_abac = Mock(return_value=True)
    verify_content = Mock(return_value=True)
    monkeypatch.setattr(uploader, "upload_samples", verify_samples)
    monkeypatch.setattr(case_upload.BatchUploader, "verify_batch", verify_generic)
    monkeypatch.setattr(
        uploader, "_set_default_created_in_data_collection_id", set_default
    )
    monkeypatch.setattr(uploader, "_verify_abac_rights", verify_abac)
    monkeypatch.setattr(uploader, "_verify_case_content", verify_content)

    assert not uploader.verify_batch(cmd, batch_result, Mock())

    verify_samples.assert_called_once_with(cmd, batch_result, True)
    verify_generic.assert_called_once()
    set_default.assert_called_once_with(cmd, batch_result)
    verify_abac.assert_called_once()
    verify_content.assert_called_once_with(cmd, batch_result)


def test_prepare_cases_only_command_preserves_input_children_and_strips_nulls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, read_set, seq = _make_sample_upload_cmd_and_result()
    value_col_id = uuid4()
    deleted_col_id = uuid4()
    batch_result.cases[0].is_new = True
    batch_result.cases[0].validated_content = {
        value_col_id: "value",
        deleted_col_id: None,
    }

    cases_only_cmd, cases_for_validation = uploader._prepare_cases_only_command(
        cmd, batch_result
    )

    original_case_for_upload = cmd.case_batch.cases[0]
    cases_only_case_for_upload = cases_only_cmd.case_batch.cases[0]
    assert original_case_for_upload.read_sets == [read_set]
    assert original_case_for_upload.seqs == [seq]
    assert cases_only_case_for_upload.read_sets is None
    assert cases_only_case_for_upload.seqs is None
    assert cases_only_case_for_upload.case.content == {value_col_id: "value"}
    assert cases_for_validation == []


@pytest.mark.parametrize("validation_fails", [False, True])
def test_verify_case_content_returns_status_delta(
    monkeypatch: pytest.MonkeyPatch, validation_fails: bool
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    validator = Mock()

    def _validate(*args: object) -> None:
        if validation_fails:
            batch_result.cases[0].add_error("test-code", "validation failed")
            batch_result.cases[0].status = case_upload.EtlStatus.FAILED

    validator.validate_and_transform.side_effect = _validate
    monkeypatch.setattr(
        uploader, "_get_complete_case_type", lambda *args, **kwargs: Mock()
    )
    monkeypatch.setattr(uploader, "_get_case_validator", lambda *args: validator)

    assert uploader._verify_case_content(cmd, batch_result) is not validation_fails


def test_upsert_samples_after_cases_retries_originally_pending_cases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    cases_only_cmd, _ = uploader._prepare_cases_only_command(cmd, batch_result)
    upload_samples = Mock(return_value=True)
    upsert_cases = Mock(return_value=True)
    monkeypatch.setattr(uploader, "upload_samples", upload_samples)
    monkeypatch.setattr(case_upload.BatchUploader, "upsert_batch", upsert_cases)

    success = uploader._upsert_samples_after_cases(
        cmd, cases_only_cmd, batch_result, Mock(), True, [True]
    )

    assert success
    upload_samples.assert_called_once_with(cmd, batch_result, False)
    upsert_cases.assert_called_once()
    assert batch_result.cases[0].status == case_upload.EtlStatus.PENDING
    assert not batch_result.cases[0].is_new


def test_upsert_samples_after_cases_skips_case_rewrite_when_sample_upload_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    cases_only_cmd, _ = uploader._prepare_cases_only_command(cmd, batch_result)
    upload_samples = Mock(return_value=False)
    upsert_cases = Mock(return_value=True)
    monkeypatch.setattr(uploader, "upload_samples", upload_samples)
    monkeypatch.setattr(case_upload.BatchUploader, "upsert_batch", upsert_cases)

    assert not uploader._upsert_samples_after_cases(
        cmd, cases_only_cmd, batch_result, Mock(), True, [True]
    )

    upload_samples.assert_called_once_with(cmd, batch_result, False)
    upsert_cases.assert_not_called()


def test_upsert_batch_handles_empty_batch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd = case_upload.command.UploadCasesCommand(
        case_type_id=uuid4(),
        case_batch=case_upload.model.CaseBatchForUpload(cases=[]),
    )
    batch_result = case_upload.model.CaseBatchUploadResult(cases=[])
    generic_upsert = Mock(return_value=True)
    monkeypatch.setattr(case_upload.BatchUploader, "upsert_batch", generic_upsert)

    assert uploader.upsert_batch(cmd, batch_result, Mock())

    generic_upsert.assert_called_once()


def test_upsert_batch_revalidates_existing_case_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    case = cmd.case_batch.cases[0].case
    assert case is not None
    case.id = uuid4()
    col_id = uuid4()
    case.content = {col_id: "updated"}
    batch_result.cases[0].validated_content = {col_id: "updated"}
    uploader.service = Mock()
    uploader.service.repository.read_fields.return_value = [
        (case.id, {col_id: "stored"})
    ]
    validate_merged = Mock()
    generic_upsert = Mock(return_value=True)
    finish_upsert = Mock(return_value=True)
    monkeypatch.setattr(uploader, "_validate_merged_content", validate_merged)
    monkeypatch.setattr(case_upload.BatchUploader, "upsert_batch", generic_upsert)
    monkeypatch.setattr(uploader, "_upsert_samples_after_cases", finish_upsert)

    assert uploader.upsert_batch(cmd, batch_result, Mock())

    validate_merged.assert_called_once()
    generic_upsert.assert_called_once()
    assert finish_upsert.call_args.args[-1] == [True]


def test_validate_merged_content_restores_explicit_deletions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    case = cmd.case_batch.cases[0].case
    assert case is not None
    case.id = uuid4()
    changed_col_id = uuid4()
    deleted_col_id = uuid4()
    unchanged_col_id = uuid4()
    case.content = {changed_col_id: "new", deleted_col_id: None}
    existing_content = {
        changed_col_id: "old",
        deleted_col_id: "deleted",
        unchanged_col_id: "keep",
    }
    validator = Mock()
    monkeypatch.setattr(
        uploader, "_get_complete_case_type", lambda *args, **kwargs: Mock()
    )
    monkeypatch.setattr(uploader, "_get_case_validator", lambda *args: validator)

    uploader._validate_merged_content(cmd, batch_result, {case.id: existing_content})

    validator.validate_and_transform.assert_called_once_with(cmd, batch_result)
    assert case.content == {
        changed_col_id: "new",
        deleted_col_id: None,
        unchanged_col_id: "keep",
    }


def test_get_case_validator_forwards_service_metadata_and_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    complete_case_type = Mock()
    user_id = uuid4()
    expected_validator = Mock()
    validator_factory = Mock(return_value=expected_validator)
    monkeypatch.setattr(case_upload, "CaseValidator", validator_factory)

    assert (
        uploader._get_case_validator(complete_case_type, user_id) is expected_validator
    )

    validator_factory.assert_called_once_with(
        uploader.service, complete_case_type, user_id
    )


def test_get_or_create_reuses_matching_sample_id_and_external_identifier(
    monkeypatch: pytest.MonkeyPatch, sample_identifier: IdentifierForUpload
) -> None:
    uploader = _make_uploader(monkeypatch)
    sample_id = uuid4()
    cmd = Mock(default_created_in_data_collection_id=uuid4())
    samples = []
    sample_id_to_index = {}
    external_id_to_index = {}
    sample_case_index = {}
    identity_errors = []

    first_index = uploader._get_or_create_sample_for_upload(
        cmd,
        0,
        sample_id,
        sample_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )
    second_index = uploader._get_or_create_sample_for_upload(
        cmd,
        1,
        sample_id,
        sample_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )

    assert first_index == second_index == 0
    assert len(samples) == 1
    assert identity_errors == []


def test_get_or_create_registers_new_identifier_for_known_sample_id(
    monkeypatch: pytest.MonkeyPatch, sample_identifier: IdentifierForUpload
) -> None:
    uploader = _make_uploader(monkeypatch)
    sample_id = uuid4()
    additional_identifier = IdentifierForUpload(
        identifier_issuer_code="ALT", external_id="sample-2"
    )
    cmd = Mock(default_created_in_data_collection_id=uuid4())
    samples = []
    sample_id_to_index = {}
    external_id_to_index = {}
    sample_case_index = {}
    identity_errors = []

    first_index = uploader._get_or_create_sample_for_upload(
        cmd,
        0,
        sample_id,
        sample_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )
    second_index = uploader._get_or_create_sample_for_upload(
        cmd,
        1,
        sample_id,
        additional_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )
    identifier_only_index = uploader._get_or_create_sample_for_upload(
        cmd,
        2,
        NULL_ID,
        additional_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )

    assert first_index == second_index == identifier_only_index == 0
    assert len(samples) == 1
    assert samples[0].identifiers == [sample_identifier, additional_identifier]
    assert identity_errors == []


def test_get_or_create_promotes_identifier_only_sample_to_known_id(
    monkeypatch: pytest.MonkeyPatch, sample_identifier: IdentifierForUpload
) -> None:
    uploader = _make_uploader(monkeypatch)
    sample_id = uuid4()
    cmd = Mock(default_created_in_data_collection_id=uuid4())
    samples = []
    sample_id_to_index = {}
    external_id_to_index = {}
    sample_case_index = {}
    identity_errors = []

    first_index = uploader._get_or_create_sample_for_upload(
        cmd,
        0,
        NULL_ID,
        sample_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )
    second_index = uploader._get_or_create_sample_for_upload(
        cmd,
        1,
        sample_id,
        sample_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )

    assert first_index == second_index == 0
    assert samples[0].id == sample_id
    assert samples[0].sample.id == sample_id
    assert sample_id_to_index[sample_id] == 0
    assert identity_errors == []


def test_get_or_create_reports_conflicting_identity_through_output_list(
    monkeypatch: pytest.MonkeyPatch, sample_identifier: IdentifierForUpload
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd = Mock(default_created_in_data_collection_id=uuid4())
    samples = []
    sample_id_to_index = {}
    external_id_to_index = {}
    sample_case_index = {}
    identity_errors = []

    uploader._get_or_create_sample_for_upload(
        cmd,
        0,
        uuid4(),
        sample_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )
    conflicting_index = uploader._get_or_create_sample_for_upload(
        cmd,
        1,
        uuid4(),
        sample_identifier,
        samples,
        sample_id_to_index,
        external_id_to_index,
        sample_case_index,
        identity_errors,
    )

    assert conflicting_index is None
    assert len(identity_errors) == 1
    assert "Inconsistent mapping" in identity_errors[0]


def test_verify_case_creation_access_accepts_existing_and_allowed_new_cases() -> None:
    collection_id = uuid4()
    existing_result = Mock(is_new=False)
    allowed_result = Mock(is_new=True)
    existing_case = Mock(case=None)
    allowed_case = Mock(case=Mock(created_in_data_collection_id=collection_id))

    assert case_upload.CaseBatchUploader._verify_case_creation_access(
        existing_case, existing_result, set()
    )
    assert case_upload.CaseBatchUploader._verify_case_creation_access(
        allowed_case, allowed_result, {collection_id}
    )
    existing_result.add_error.assert_not_called()
    allowed_result.add_error.assert_not_called()


def test_verify_case_creation_access_rejects_disallowed_new_case() -> None:
    collection_id = uuid4()
    case_result = Mock(is_new=True)
    case_for_upload = Mock(case=Mock(created_in_data_collection_id=collection_id))

    assert not case_upload.CaseBatchUploader._verify_case_creation_access(
        case_for_upload, case_result, set()
    )

    case_result.add_error.assert_called_once()
    assert case_result.add_error.call_args.args[0] == "29e256f1"


def test_verify_abac_rights_accepts_allowed_new_case_and_writable_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    case = cmd.case_batch.cases[0].case
    assert case is not None
    collection_id = case.created_in_data_collection_id
    col_id = uuid4()
    case.content = {col_id: "value"}
    batch_result.cases[0].is_new = True
    case_for_upload = cmd.case_batch.cases[0]
    writable_col_ids = {
        col_id,
        case_for_upload.read_sets[0].col_id,
        case_for_upload.seqs[0].col_id,
    }
    access = Mock(
        is_private=True,
        add_case=True,
        read_col_ids=writable_col_ids,
        write_col_ids=writable_col_ids,
    )
    complete_case_type = Mock(case_type_access_abacs={collection_id: access})
    monkeypatch.setattr(
        uploader, "_get_complete_case_type", lambda *args, **kwargs: complete_case_type
    )
    monkeypatch.setattr(
        uploader,
        "_get_case_data_collections",
        lambda *args: [frozenset([collection_id])],
    )

    assert uploader._verify_abac_rights(cmd, batch_result, Mock())

    assert case.content == {col_id: "value"}
    assert batch_result.cases[0].data_issues == []


def test_verify_abac_rights_rejects_new_case_and_removes_unwritable_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    uploader = _make_uploader(monkeypatch)
    cmd, batch_result, _, _ = _make_sample_upload_cmd_and_result()
    case = cmd.case_batch.cases[0].case
    assert case is not None
    collection_id = case.created_in_data_collection_id
    col_id = uuid4()
    case.content = {col_id: "secret"}
    batch_result.cases[0].is_new = True
    complete_case_type = Mock(case_type_access_abacs={})
    monkeypatch.setattr(
        uploader, "_get_complete_case_type", lambda *args, **kwargs: complete_case_type
    )
    monkeypatch.setattr(
        uploader,
        "_get_case_data_collections",
        lambda *args: [frozenset([collection_id])],
    )

    assert not uploader._verify_abac_rights(cmd, batch_result, Mock())

    assert case.content == {}
    issue_by_col_id = {
        issue.col_id: issue for issue in batch_result.cases[0].data_issues
    }
    assert issue_by_col_id[col_id].code == "a7b3f9d2"
    assert issue_by_col_id[col_id].original_value == "secret"


def test_get_column_access_for_collections_caches_union() -> None:
    collection_ids = frozenset([uuid4(), uuid4()])
    collection_id_list = list(collection_ids)
    readable_ids_by_collection = [
        {uuid4()},
        {uuid4()},
    ]
    writeable_ids = {uuid4()}
    access_abacs = {
        collection_id_list[0]: Mock(
            read_col_ids=readable_ids_by_collection[0], write_col_ids=writeable_ids
        ),
        collection_id_list[1]: Mock(
            read_col_ids=readable_ids_by_collection[1], write_col_ids=writeable_ids
        ),
    }
    expected_readable_ids = set().union(*readable_ids_by_collection)
    complete_case_type = Mock(case_type_access_abacs=access_abacs)
    cache = {}

    access = case_upload.CaseBatchUploader._get_column_access_for_collections(
        complete_case_type, collection_ids, cache
    )
    cached_access = case_upload.CaseBatchUploader._get_column_access_for_collections(
        complete_case_type, collection_ids, cache
    )

    assert access == (expected_readable_ids, writeable_ids)
    assert cached_access is access


def test_record_unwritable_column_issues_removes_and_classifies_values() -> None:
    readable_only_col_id = uuid4()
    unknown_col_id = uuid4()
    content = {readable_only_col_id: "visible", unknown_col_id: "hidden"}
    case_result = Mock(data_issues=[])

    case_upload.CaseBatchUploader._record_unwritable_column_issues(
        content,
        {readable_only_col_id, unknown_col_id},
        {readable_only_col_id},
        set(),
        case_result,
    )

    assert content == {}
    issues = {issue.col_id: issue for issue in case_result.data_issues}
    assert issues[readable_only_col_id].original_value == "visible"
    assert issues[readable_only_col_id].code == "3e7c1a9f"
    assert issues[unknown_col_id].original_value == "hidden"
    assert issues[unknown_col_id].code == "a7b3f9d2"


def test_get_case_data_collections_includes_existing_links_in_upload_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case_ids = [uuid4(), uuid4(), uuid4()]
    created_collection_ids = [uuid4(), uuid4(), uuid4()]
    linked_collection_ids = [uuid4(), uuid4(), uuid4()]
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    uploader.service.repository.crud.return_value = [
        Mock(case_id=case_ids[2], data_collection_id=linked_collection_ids[2]),
        Mock(case_id=case_ids[0], data_collection_id=linked_collection_ids[0]),
        Mock(case_id=case_ids[0], data_collection_id=linked_collection_ids[1]),
    ]
    cmd = Mock(
        user=None,
        case_batch=Mock(
            cases=[
                Mock(id=case_id, case=Mock(created_in_data_collection_id=collection_id))
                for case_id, collection_id in zip(
                    case_ids, created_collection_ids, strict=True
                )
            ]
        ),
    )
    batch_result = Mock(
        cases=[Mock(is_new=False), Mock(is_new=True), Mock(is_new=False)]
    )

    actual = uploader._get_case_data_collections(cmd, batch_result, Mock())

    assert actual == [
        frozenset([created_collection_ids[0], *linked_collection_ids[:2]]),
        frozenset([created_collection_ids[1]]),
        frozenset([created_collection_ids[2], linked_collection_ids[2]]),
    ]
    uploader.service.repository.crud.assert_called_once()


def test_get_case_data_collections_skips_link_query_for_new_cases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection_id = uuid4()
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    cmd = Mock(
        user=None,
        case_batch=Mock(
            cases=[
                Mock(id=uuid4(), case=Mock(created_in_data_collection_id=collection_id))
            ]
        ),
    )

    actual = uploader._get_case_data_collections(
        cmd, Mock(cases=[Mock(is_new=True)]), Mock()
    )

    assert actual == [frozenset([collection_id])]
    uploader.service.repository.crud.assert_not_called()


def test_set_default_created_in_data_collection_id_assigns_existing_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection_id = uuid4()
    existing_case = Mock(created_in_data_collection_id=NULL_ID)
    new_case = Mock(created_in_data_collection_id=NULL_ID)
    existing_result = Mock(is_new=False)
    new_result = Mock(is_new=True)
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    uploader.service.app.handle.return_value = True
    cmd = Mock(
        user=None,
        default_created_in_data_collection_id=collection_id,
        case_batch=Mock(cases=[Mock(case=existing_case), Mock(case=new_case)]),
    )
    batch_result = Mock(cases=[existing_result, new_result])

    assert uploader._set_default_created_in_data_collection_id(cmd, batch_result)

    assert existing_case.created_in_data_collection_id == NULL_ID
    assert new_case.created_in_data_collection_id == collection_id
    existing_result.add_info.assert_not_called()
    new_result.add_info.assert_called_once()


def test_set_default_created_in_data_collection_id_reports_missing_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = Mock(created_in_data_collection_id=NULL_ID)
    case_result = Mock(is_new=True)
    uploader = _make_uploader(monkeypatch)
    cmd = Mock(
        user=None,
        default_created_in_data_collection_id=NULL_ID,
        case_batch=Mock(cases=[Mock(case=case)]),
    )
    batch_result = Mock(cases=[case_result])

    assert not uploader._set_default_created_in_data_collection_id(cmd, batch_result)

    case_result.add_error.assert_called_once()
    assert case_result.add_error.call_args.args[0] == "c1f8e9d4"


def test_set_default_reports_invalid_default_but_keeps_case_level_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_default = uuid4()
    case_level_collection = uuid4()
    case = Mock(created_in_data_collection_id=case_level_collection)
    case_result = Mock(is_new=True)
    uploader = _make_uploader(monkeypatch)
    uploader.service = Mock()
    uploader.service.app.handle.return_value = False
    cmd = Mock(
        user=None,
        default_created_in_data_collection_id=invalid_default,
        case_batch=Mock(cases=[Mock(case=case)]),
    )
    batch_result = Mock(cases=[case_result])

    assert not uploader._set_default_created_in_data_collection_id(cmd, batch_result)

    assert case.created_in_data_collection_id == case_level_collection
    batch_result.add_error.assert_called_once()
    case_result.add_info.assert_not_called()


def test_case_service_upload_cases_honors_disabled_feature_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = Mock()
    service.app.get_feature_flag.return_value = True

    with pytest.raises(case_upload.exc.FeatureDisabledServiceError, match="a756246d"):
        case_upload.case_service_upload_cases(service, Mock())


def test_case_service_upload_cases_returns_uploader_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = Mock()
    service.app.get_feature_flag.return_value = False
    result = Mock()
    uploader = Mock()
    uploader.upload_batch.return_value = result
    monkeypatch.setattr(case_upload, "CaseBatchUploader", lambda _: uploader)

    assert case_upload.case_service_upload_cases(service, Mock()) is result

    uploader.upload_batch.assert_called_once()
