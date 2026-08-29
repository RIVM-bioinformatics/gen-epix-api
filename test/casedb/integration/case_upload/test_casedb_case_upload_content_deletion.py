"""
End-to-end regression test for LSP-3645 and LSP-3647: a case content key set
to None must actually be deleted via UploadCasesCommand.

LSP-3645 (Case.content field_serializer silently stripping None on
serialization) and LSP-3647 (BatchUploader.upsert_batch re-deriving its own
"changed?" check from a fresh DB read, unable to see a deletion already
resolved into key-absence) each independently block this from working; both
must be fixed for the key to actually disappear from the persisted case.
This test therefore serializes the upload command to JSON and back (to
exercise LSP-3645) before handling it through the real, non-mocked upload
and persistence path (to exercise LSP-3647), rather than mocking either.
"""

import logging
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import EnumTestType

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.domain.enum import (
    AppType,
    DevRepositoryConfig,
    EtlStatus,
    UploadAction,
)
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

TEST_TYPE = EnumTestType.CASEDB_INTEGRATION_CONTENT

SKIP_ENDPOINTS = True  # The UploadCasesCommand HTTP endpoint test client is stale
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_EMPTY

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=CASEDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


class TestCaseUploadContentDeletion:
    def test_content_key_deletion_via_upload(self, env: Env) -> None:
        root_user = env.get_root_user()
        env.set_obj(root_user)

        # Minimal reference data: one CaseType with a single TEXT Col
        env.create_disease(root_user, "disease_1")
        env.create_etiological_agent(root_user, "etiological_agent_1")
        case_type = env.create_case_type(
            root_user, "case_type1", "disease_1", "etiological_agent_1"
        )
        env.create_ref_dim(root_user, "ref_dim1", enum.DimType.TEXT)
        env.create_ref_col(root_user, "ref_col1_1", enum.ColType.TEXT)
        env.create_dim(root_user, "dim1_1_1")
        col = env.create_col(root_user, "col1_1_1_1")
        data_collection = env.create_data_collection(root_user, "data_collection1")

        # Create a case with a value for the Col. Built manually via
        # UploadCasesCommand rather than env.create_case(), whose Col lookup
        # (read_some_by_property(..., cascade=True)) has an unrelated bug
        # that clobbers case_type_id with a list of linked CaseType objects,
        # making it match nothing.
        create_cmd = command.UploadCasesCommand(
            user=root_user,
            case_type_id=case_type.id,
            default_created_in_data_collection_id=data_collection.id,
            case_batch=model.CaseBatchForUpload(
                cases=[
                    model.CaseForUpload(
                        case=model.Case(
                            case_type_id=case_type.id,
                            created_in_data_collection_id=data_collection.id,
                            content={col.id: "initial-value"},
                        ),
                    )
                ]
            ),
        )
        create_result: model.CaseBatchUploadResult = env.handle(create_cmd)
        assert create_result.cases[0].status == EtlStatus.CREATED
        case_id = create_result.cases[0].id
        assert case_id is not None

        # Build an update command that deletes the Col's content value
        delete_cmd = command.UploadCasesCommand(
            user=root_user,
            case_type_id=case_type.id,
            default_created_in_data_collection_id=data_collection.id,
            on_exists=UploadAction.UPDATE.value,  # type: ignore[call-arg]
            case_batch=model.CaseBatchForUpload(
                cases=[
                    model.CaseForUpload(
                        case=model.Case(
                            id=case_id,
                            case_type_id=case_type.id,
                            created_in_data_collection_id=data_collection.id,
                            content={col.id: None},
                        ),
                    )
                ]
            ),
        )

        # Round-trip through JSON, exactly as a real client's HTTP request
        # would, to verify the None delete marker actually survives the wire
        # (LSP-3645) rather than being silently stripped by Case.content's
        # field_serializer.
        restored_cmd = command.UploadCasesCommand.model_validate_json(
            delete_cmd.model_dump_json()
        )

        # Handle the command through the real, non-mocked upload and
        # persistence path, to verify the deletion is actually persisted
        # (LSP-3647) rather than silently marked SKIPPED.
        result: model.CaseBatchUploadResult = env.handle(restored_cmd)
        assert result.cases[0].status == EtlStatus.UPDATED

        updated_case: model.Case = env.app.handle(
            command.CaseCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ONE,
                obj_ids=case_id,
            )
        )
        assert col.id not in updated_case.content
