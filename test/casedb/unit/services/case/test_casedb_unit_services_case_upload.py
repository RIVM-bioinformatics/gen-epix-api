from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

import gen_epix.casedb.services.case.upload as case_upload
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload


@pytest.fixture
def sample_identifier() -> IdentifierForUpload:
    return IdentifierForUpload(identifier_issuer_code="LAB", external_id="sample-1")


def _make_uploader(monkeypatch: pytest.MonkeyPatch) -> case_upload.CaseBatchUploader:
    uploader = object.__new__(case_upload.CaseBatchUploader)
    monkeypatch.setattr(
        uploader, "is_null", lambda value: value is None or value == NULL_ID
    )
    return uploader


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
