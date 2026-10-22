"""Integration test: one bad sample in an upload no longer keeps the others out.

Runs UploadSamplesCommand against a real (DICT demo) SEQDB app, so the whole upload
path is exercised: verification, upsert and storage. With
fail_batch_on_item_error=False the samples that pass verification are stored even
when another sample in the same batch fails (LSP-4119).
"""

import logging
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.test_client.enum import EnumTestType
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain import enum as commondb_enum
from gen_epix.commondb.domain.enum import AppType
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model

TEST_TYPE = EnumTestType.SEQDB_INTEGRATION_UPLOAD_SAMPLES
REPOSITORY_CONFIG = commondb_enum.DevRepositoryConfig.DICT_DEMO

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    log_any=False,
)


@pytest.fixture(scope="module", name="env")
def env() -> Env:
    """Return a test client on the DICT demo repository."""
    test_type = f"{TEST_TYPE.value}__{REPOSITORY_CONFIG.value}"
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=test_type,
        app_cfg=SEQDB_APP_CFGS[test_type],
        log_level=logging.ERROR,
    )


def _read_all(env: Env, crud_command_class: type[command.CrudCommand]) -> list:
    return env.handle(  # type: ignore[no-any-return]
        crud_command_class(
            user=env.get_root_user(),
            obj_ids=None,
            operation=CrudOperation.READ_ALL,
        ),
        use_endpoint=False,
    )


def _sample_for_upload(
    code: str, data_collection_id: UUID, **protocol: Any
) -> model.SampleForUpload:
    """A new sample with one assembly seq; ``protocol`` holds its protocol id or code."""
    return model.SampleForUpload(
        sample=model.Sample(
            code=code, created_in_data_collection_id=data_collection_id
        ),
        seqs=[
            model.SeqForUpload(
                id=uuid4(),
                contigs=[
                    model.Contig(
                        # A random sequence, so no two test seqs share a hash
                        seq="".join("ACGT"[int(x, 16) % 4] for x in uuid4().hex),
                        seq_format=enum.SeqFormat.STR_DNA,
                    )
                ],
                **protocol,
            )
        ],
    )


def _protocol_id_of_type(
    env: Env, protocol_types: frozenset[enum.ProtocolType]
) -> UUID:
    return next(  # type: ignore[no-any-return]
        x.id
        for x in _read_all(env, command.ProtocolCrudCommand)
        if x.protocol_type in protocol_types
    )


def _bad_protocol(env: Env, kind: str) -> dict[str, Any]:
    """Protocol fields that fail verification for one seq, attributed to its sample."""
    if kind == "wrong_protocol_type":
        return {
            "protocol_id": _protocol_id_of_type(
                env, enum.ProtocolTypeSet.SEQUENCING.value
            )
        }
    if kind == "unknown_protocol_id":
        return {"protocol_id": uuid4()}
    return {"protocol_code": f"unknown_{uuid4().hex[:8]}"}


@pytest.mark.parametrize(
    "bad_kind", ["wrong_protocol_type", "unknown_protocol_id", "unknown_protocol_code"]
)
class TestOneBadSampleFailsOnItsOwn:
    """A sample with a bad seq protocol fails; the other samples are stored."""

    def _upload(
        self, env: Env, bad_kind: str, fail_batch_on_item_error: bool
    ) -> tuple[list[str], model.SampleBatchUploadResult]:
        data_collection_id = _read_all(env, command.SampleCrudCommand)[
            0
        ].created_in_data_collection_id
        good_protocol = {
            "protocol_id": _protocol_id_of_type(
                env, enum.ProtocolTypeSet.ASSEMBLY.value
            )
        }
        run_id = uuid4().hex[:8]
        codes = [f"lsp4119_{run_id}_{i}" for i in range(3)]
        protocols = [good_protocol, _bad_protocol(env, bad_kind), good_protocol]
        sample_batch = model.SampleBatchForUpload(
            samples=[
                _sample_for_upload(code, data_collection_id, **protocol)
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
            use_endpoint=False,
        )
        return codes, batch_result

    def test_good_samples_are_stored(self, env: Env, bad_kind: str) -> None:
        codes, batch_result = self._upload(
            env, bad_kind, fail_batch_on_item_error=False
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

    def test_default_stores_nothing(self, env: Env, bad_kind: str) -> None:
        codes, batch_result = self._upload(env, bad_kind, fail_batch_on_item_error=True)

        stored_codes = {x.code for x in _read_all(env, command.SampleCrudCommand)}
        assert not stored_codes.intersection(codes)
        assert batch_result.has_log_code("02095f22")
