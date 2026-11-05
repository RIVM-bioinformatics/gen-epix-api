"""Integration test: one bad sample in an upload no longer keeps the others out.

Runs UploadSamplesCommand against empty DICT and SQLite SEQDB apps, directly and over
HTTP, so the whole upload path is exercised: verification, upsert and storage. With
fail_batch_on_item_error=False the samples that pass verification are stored even
when another sample in the same batch fails.
"""

from test.seqdb.integration.upload_samples.ref_data import (
    SeqUploadRefData,
    sample_for_upload,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from typing import Any
from uuid import uuid4

import pytest

from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, model


def _read_all(env: Env, crud_command_class: type[command.CrudCommand]) -> list:
    return env.handle(  # type: ignore[no-any-return]
        crud_command_class(
            user=env.get_root_user(),
            obj_ids=None,
            operation=CrudOperation.READ_ALL,
        ),
        use_endpoint=False,
    )


def _bad_protocol(ref_data: SeqUploadRefData, kind: str) -> dict[str, Any]:
    """Protocol fields that fail verification for one seq."""
    if kind == "wrong_protocol_type":
        return {"protocol_id": ref_data.sequencing_protocol_id}
    if kind == "unknown_protocol_id":
        return {"protocol_id": uuid4()}
    return {"protocol_code": f"unknown_{uuid4().hex[:8]}"}


@pytest.mark.parametrize(
    "bad_kind", ["wrong_protocol_type", "unknown_protocol_id", "unknown_protocol_code"]
)
class TestOneBadSampleFailsOnItsOwn:
    """A sample with a bad seq protocol fails; the other samples are stored."""

    def _upload(
        self,
        env: Env,
        ref_data: SeqUploadRefData,
        bad_kind: str,
        fail_batch_on_item_error: bool,
    ) -> tuple[list[str], model.SampleBatchUploadResult]:
        good_protocol = {"protocol_id": ref_data.assembly_protocol_id}
        run_id = uuid4().hex[:8]
        codes = [f"item_error_{run_id}_{i}" for i in range(3)]
        protocols = [good_protocol, _bad_protocol(ref_data, bad_kind), good_protocol]
        sample_batch = model.SampleBatchForUpload(
            samples=[
                sample_for_upload(ref_data, code, seq_protocol=protocol)
                for code, protocol in zip(codes, protocols)
            ],
            alleles=[],
        )
        batch_result: model.SampleBatchUploadResult = env.handle(
            command.UploadSamplesCommand(
                user=env.get_root_user(),
                sample_batch=sample_batch,
                calculate_distances=False,
                fail_batch_on_item_error=fail_batch_on_item_error,  # type: ignore[call-arg]
            ),
        )
        return codes, batch_result

    def test_good_samples_are_stored(
        self, env: Env, ref_data: SeqUploadRefData, bad_kind: str
    ) -> None:
        codes, batch_result = self._upload(
            env, ref_data, bad_kind, fail_batch_on_item_error=False
        )

        stored_codes = {x.code for x in _read_all(env, command.SampleCrudCommand)}
        assert codes[0] in stored_codes
        assert codes[1] not in stored_codes
        assert codes[2] in stored_codes
        assert [x.status for x in batch_result.samples] == [
            EtlStatus.CREATED,
            EtlStatus.FAILED,
            EtlStatus.CREATED,
        ]
        assert batch_result.status == EtlStatus.FAILED
        assert batch_result.has_log_code("c0f70912")

    def test_default_stores_nothing(
        self, env: Env, ref_data: SeqUploadRefData, bad_kind: str
    ) -> None:
        codes, batch_result = self._upload(
            env, ref_data, bad_kind, fail_batch_on_item_error=True
        )

        stored_codes = {x.code for x in _read_all(env, command.SampleCrudCommand)}
        assert not stored_codes.intersection(codes)
        assert batch_result.has_log_code("02095f22")
