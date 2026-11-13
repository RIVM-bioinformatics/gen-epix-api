"""Check sample uploads directly and over HTTP on DICT and SQLite."""

import json
from test.seqdb.integration.upload_samples.ref_data import (
    SeqUploadRefData,
    create_sample_for_upload,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import UploadAction
from gen_epix.commondb.domain.model import IdentifierForUpload, IdentifierIssuer
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model


def _upload(
    env: SeqdbTestClient,
    samples: list[model.SampleForUpload],
    **kwargs: Any,
) -> model.SampleBatchUploadResult:
    return env.handle(  # type: ignore[no-any-return]
        command.UploadSamplesCommand(
            user=env.get_root_user(),
            sample_batch=model.SampleBatchForUpload(samples=samples, alleles=[]),
            calculate_distances=False,
            **kwargs,
        )
    )


def _stored(env: SeqdbTestClient) -> set[UUID]:
    samples: list[model.Sample] = env.app.handle(
        command.SampleCrudCommand(
            user=env.get_root_user(), operation=CrudOperation.READ_ALL
        )
    )
    return {sample.id for sample in samples if sample.id is not None}


def test_empty_batch(env: SeqdbTestClient) -> None:
    result = _upload(env, [])
    assert result.status == EtlStatus.SKIPPED
    assert result.samples == []


def test_new_sample_with_read_set_and_seq(
    env: SeqdbTestClient, ref_data: SeqUploadRefData
) -> None:
    sample = create_sample_for_upload(ref_data)
    sample.read_sets = [
        model.ReadSetForUpload(protocol_id=ref_data.sequencing_protocol_id)
    ]
    sample.seqs = [
        model.SeqForUpload(
            protocol_id=ref_data.assembly_protocol_id,
            contigs=[
                model.Contig(
                    seq="ACGT" + "".join("ACGT"[int(x, 16) % 4] for x in uuid4().hex),
                    seq_format=enum.SeqFormat.STR_DNA,
                )
            ],
        )
    ]
    result = _upload(env, [sample])
    assert result.status == EtlStatus.CREATED
    assert result.samples[0].id is not None
    assert result.samples[0].read_sets is not None
    assert result.samples[0].seqs is not None
    assert result.samples[0].read_sets[0].id is not None
    assert result.samples[0].seqs[0].id is not None


def test_upload_actions_and_verify_only(
    env: SeqdbTestClient, ref_data: SeqUploadRefData
) -> None:
    sample = create_sample_for_upload(ref_data)
    created = _upload(env, [sample])
    assert created.status == EtlStatus.CREATED
    sample.id = created.samples[0].id
    assert (
        _upload(env, [sample], on_exists=UploadAction.SKIP).status == EtlStatus.SKIPPED
    )
    assert sample.sample is not None
    sample.sample.props = {"revision": 2}
    assert (
        _upload(env, [sample], on_exists=UploadAction.UPDATE).status
        == EtlStatus.UPDATED
    )
    assert (
        _upload(env, [sample], on_exists=UploadAction.ERROR).status == EtlStatus.FAILED
    )

    new_sample = create_sample_for_upload(ref_data)
    assert (
        _upload(env, [new_sample], on_new=UploadAction.SKIP).status == EtlStatus.SKIPPED
    )
    assert (
        _upload(env, [new_sample], on_new=UploadAction.ERROR).status == EtlStatus.FAILED
    )
    before = _stored(env)
    verified = _upload(env, [new_sample], verify_only=True)
    assert verified.status == EtlStatus.SKIPPED
    assert verified.samples[0].is_new is True
    assert _stored(env) == before


def test_allele_profile_uses_reference_data(
    env: SeqdbTestClient,
    ref_data: SeqUploadRefData,
    allele_ref_data: tuple[UUID, UUID],
) -> None:
    user = env.get_root_user()
    locus_id, protocol_id = allele_ref_data
    allele = model.AlleleForUpload(
        seq="ACGTACGT", seq_format=enum.SeqFormat.STR_DNA, locus_id=locus_id
    )
    assert allele.id is not None
    sample = create_sample_for_upload(ref_data)
    sample.seq_profiles = [
        model.SeqProfileForUpload(  # type: ignore[call-arg]
            protocol_id=protocol_id,
            seq_profile_type=enum.SeqProfileType.ALLELE,
            format=enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            allele_ids=[allele.id],
            content_hash=model.SeqProfile.get_allele_profile_hash([allele.id]),
        )
    ]
    result: model.SampleBatchUploadResult = env.handle(
        command.UploadSamplesCommand(
            user=user,
            sample_batch=model.SampleBatchForUpload(samples=[sample], alleles=[allele]),
            calculate_distances=False,
        )
    )
    assert result.status == EtlStatus.CREATED
    assert result.samples[0].seq_profiles is not None
    assert result.samples[0].seq_profiles[0].status == EtlStatus.CREATED


@pytest.mark.parametrize("child_field", ["read_sets", "seqs"])
def test_conflicting_child_identifier_is_in_http_response(
    env: SeqdbTestClient, ref_data: SeqUploadRefData, child_field: str
) -> None:
    if env.endpoint_test_client is None:
        pytest.skip("Raw HTTP response requires endpoints")
    user = env.get_root_user()
    issuer: IdentifierIssuer = env.app.handle(
        command.IdentifierIssuerCrudCommand(
            user=user,
            operation=CrudOperation.CREATE_ONE,
            objs=IdentifierIssuer(code=f"issuer_{uuid4().hex}", name="Upload test"),
        )
    )
    identifier = IdentifierForUpload(
        identifier_issuer_id=issuer.id, external_id=f"reads_{uuid4().hex}"
    )
    child_model = (
        model.ReadSetForUpload if child_field == "read_sets" else model.SeqForUpload
    )
    protocol_id = (
        ref_data.sequencing_protocol_id
        if child_field == "read_sets"
        else ref_data.assembly_protocol_id
    )
    sample = create_sample_for_upload(ref_data)
    setattr(
        sample,
        child_field,
        [child_model(id=uuid4(), protocol_id=protocol_id, identifiers=[identifier])],  # type: ignore[call-arg]
    )
    first = _upload(env, [sample])
    assert first.status == EtlStatus.CREATED
    sample.id = first.samples[0].id
    sample.sample = None
    setattr(
        sample,
        child_field,
        [child_model(id=uuid4(), protocol_id=protocol_id, identifiers=[identifier])],  # type: ignore[call-arg]
    )
    cmd = command.UploadSamplesCommand(
        user=user,
        sample_batch=model.SampleBatchForUpload(samples=[sample], alleles=[]),
        on_exists=UploadAction.UPDATE,  # type: ignore[call-arg]
        calculate_distances=False,
    )
    client = env.endpoint_test_client
    response = client.test_client.post(
        env.default_route_prefix + "/upload/samples",
        headers=client.get_dummy_jwt_header(user.get_key()),
        json=json.loads(cmd.model_dump_json(exclude={"user"})),
    )
    assert response.status_code == 200
    identifier_result = response.json()["samples"][0][child_field][0]["identifiers"][0]
    assert identifier_result["status"] == EtlStatus.FAILED.value
    assert "0561ecd7" in {item["code"] for item in identifier_result["logs"]}


def test_malformed_body_returns_422(env: SeqdbTestClient) -> None:
    if env.endpoint_test_client is None:
        pytest.skip("HTTP validation requires endpoints")
    user = env.get_root_user()
    client = env.endpoint_test_client
    response = client.test_client.post(
        env.default_route_prefix + "/upload/samples",
        headers=client.get_dummy_jwt_header(user.get_key()),
        json={"sample_batch": {"samples": [{"sample": {"code": "incomplete"}}]}},
    )
    assert response.status_code == 422
