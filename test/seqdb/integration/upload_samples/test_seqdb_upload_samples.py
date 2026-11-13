"""Integration test: one bad sample in an upload no longer keeps the others out.

Runs UploadSamplesCommand against empty DICT and SQLite SEQDB apps, directly and over
HTTP, so the whole upload path is exercised: verification, upsert and storage. With
fail_batch_on_item_error=False the samples that pass verification are stored even
when another sample in the same batch fails.
"""

from test.seqdb.integration.upload_samples.ref_data import (
    SeqUploadRefData,
    create_sample_for_upload,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from typing import Any
from uuid import uuid4

import pytest

from gen_epix.commondb.domain.enum import UploadAction
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
                create_sample_for_upload(ref_data, code, seq_protocol=protocol)
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


class TestChangedUnchangeableFieldFailsOnItsOwn:
    """An existing sample re-uploaded with another code fails; the others are stored."""

    def _upload(
        self,
        env: Env,
        samples: list[model.SampleForUpload],
        fail_batch_on_item_error: bool,
        verify_only: bool = False,
    ) -> model.SampleBatchUploadResult:
        return env.handle(  # type: ignore[no-any-return]
            command.UploadSamplesCommand(
                user=env.get_root_user(),
                sample_batch=model.SampleBatchForUpload(samples=samples, alleles=[]),
                calculate_distances=False,
                fail_batch_on_item_error=fail_batch_on_item_error,  # type: ignore[call-arg]
                verify_only=verify_only,
                on_exists=UploadAction.UPDATE,
            ),
            use_endpoint=False,
        )

    def _store_sample(
        self, env: Env, ref_data: SeqUploadRefData
    ) -> model.SampleForUpload:
        """Store a new sample and return it as an upload item of the stored sample."""
        sample_for_upload = create_sample_for_upload(
            ref_data,
            f"immutable_{uuid4().hex[:8]}",
        )
        batch_result = self._upload(
            env, [sample_for_upload], fail_batch_on_item_error=True
        )
        assert batch_result.status == EtlStatus.CREATED
        stored_sample = next(
            x
            for x in _read_all(env, command.SampleCrudCommand)
            if x.code == sample_for_upload.sample.code
        )
        return model.SampleForUpload(sample=stored_sample)

    def _changed_and_new(
        self, env: Env, ref_data: SeqUploadRefData
    ) -> tuple[list[model.SampleForUpload], model.SampleForUpload]:
        existing = self._store_sample(env, ref_data)
        changed = model.SampleForUpload(
            sample=existing.sample.model_copy(
                update={"code": f"changed_{uuid4().hex[:8]}"}
            )
        )
        new = create_sample_for_upload(
            ref_data,
            f"immutable_new_{uuid4().hex[:8]}",
        )
        return [changed, new], new

    def test_good_sample_is_stored(self, env: Env, ref_data: SeqUploadRefData) -> None:
        samples, new = self._changed_and_new(env, ref_data)

        batch_result = self._upload(env, samples, fail_batch_on_item_error=False)

        stored_codes = {x.code for x in _read_all(env, command.SampleCrudCommand)}
        assert new.sample.code in stored_codes
        assert samples[0].sample.code not in stored_codes
        assert [x.status for x in batch_result.samples] == [
            EtlStatus.FAILED,
            EtlStatus.CREATED,
        ]
        assert batch_result.samples[0].has_log_code("f5e09001")

    def test_verify_only_reports_the_error(
        self, env: Env, ref_data: SeqUploadRefData
    ) -> None:
        samples, new = self._changed_and_new(env, ref_data)

        batch_result = self._upload(
            env, samples, fail_batch_on_item_error=False, verify_only=True
        )

        stored_codes = {x.code for x in _read_all(env, command.SampleCrudCommand)}
        assert new.sample.code not in stored_codes
        assert batch_result.samples[0].status == EtlStatus.FAILED
        assert batch_result.samples[0].has_log_code("f5e09001")
