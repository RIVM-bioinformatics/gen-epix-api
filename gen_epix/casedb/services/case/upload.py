from collections import defaultdict
from hashlib import sha256
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_validator import CaseValidator
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.commondb.domain.model.upload import BaseBatchUploadResult
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter.uuid_set import UuidSetFilter


class CaseBatchUploader(BatchUploader):
    def __init__(self, service: BaseService) -> None:
        super().__init__(
            command.UploadCasesCommand,
            model.STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
            service,
        )
        if not isinstance(service, BaseCaseService):
            raise exc.InvalidArgumentsError("915489e8", "Invalid service type")
        self.service: BaseCaseService = service

    def verify_user_rights(self, cmd: UploadBatchCommandMixin) -> None:
        """
        Implements user rights verification for uploading cases. Only ABAC rights are
        verified: the user must have write access to all Cols contained in
        the uploaded cases for the created in data collection.
        """
        # Verify command type
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("510ea98a", "Invalid command type")
        # Determine Cols with write access
        complete_case_type = self._get_complete_case_type(cmd)
        case_type_access_abac = complete_case_type.case_type_access_abacs.get(
            cmd.created_in_data_collection_id
        )
        if case_type_access_abac is None:
            # Full-access users (ROOT / APP_ADMIN) can upload to any data
            # collection; fall back to all cols for the case type. The
            # DataCollection existence is still enforced by DB constraints.
            case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
            if case_abac is None or not case_abac.is_full_access:
                raise exc.UnauthorizedAuthError(
                    "d8c05dc7",
                    f"User {None if cmd.user is None else cmd.user.id} is not allowed to access cases in the given data collection",
                )
            write_col_ids = set(complete_case_type.cols.keys())
        else:
            write_col_ids = case_type_access_abac.write_col_ids
        if not write_col_ids:
            raise exc.UnauthorizedAuthError(
                "96851164",
                f"User {None if cmd.user is None else cmd.user.id} is not allowed to write any Cols for cases in the given data collection",
            )

        # Determine if uploaded cases only contain writable columns
        unauthorized_cols = set()
        for case_for_upload in cmd.case_batch.cases:
            case = case_for_upload.case
            if case is None:
                continue
            content = case.content
            if not content:
                continue
            # Determine unauthorized columns in case content
            unauthorized_cols.update(set(content.keys()) - write_col_ids)
            # Determine unauthorized columns in read sets
            unauthorized_cols.update(
                set(x.col_id for x in case_for_upload.read_sets or []) - write_col_ids
            )
            # Determine unauthorized columns in seqs
            unauthorized_cols.update(
                set(x.col_id for x in case_for_upload.seqs or []) - write_col_ids
            )
        if unauthorized_cols:
            unauthorized_cols_str = ", ".join(str(x) for x in sorted(unauthorized_cols))
            raise exc.UnauthorizedAuthError(
                "ec85ffb9",
                f"User {None if cmd.user is None else cmd.user.id} is not allowed to write columns {unauthorized_cols_str} contained in the batch case, for the given data collection",
            )

    def verify_batch(
        self,
        cmd: UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Extends batch verification to the case content as well as the read sets and
        seqs, which are verified by seqdb.
        """
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("92bef72e", "Invalid command type")
        if not isinstance(batch_result, model.CaseBatchUploadResult):
            raise exc.InvalidArgumentsError("42b47de6", "Invalid return value type")
        success = True

        # Verify samples via seqdb service
        success &= self.upload_samples(cmd, batch_result, True)

        # Verify generic aspects. This will fill in any case IDs based on external
        # identifiers. The case IDs are needed for case content validation when the
        # case is being updated, since the merged content is validated and the IDs
        # are needed to retrieve the cases.
        success &= super().verify_batch(cmd, batch_result, uow)

        # Verify case content. Derived values and data issues are also added in the
        # form of ValidatedCaseForUpload objects in the result.
        success &= self.verify_case_content(cmd, batch_result)

        return success

    def upsert_batch(
        self,
        cmd: UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Extends batch upload to uploading the cases with this service, and the read
        sets and seqs to seqdb.
        """
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("0935eb52", "Invalid command type")
        if not isinstance(batch_result, model.CaseBatchUploadResult):
            raise exc.InvalidArgumentsError("078d4af1", "Invalid return value type")
        success = True

        # Create new command with only cases and content updated during verification
        cases_only_cmd = cmd.model_copy()
        cases_only_cmd.case_batch = cmd.case_batch.model_copy()
        cases_only_cmd.case_batch.cases = [x.model_copy() for x in cmd.case_batch.cases]
        cases_for_validation: list[model.Case] = []
        for i, (case_for_upload, case_result) in enumerate(
            zip(cases_only_cmd.case_batch.cases, batch_result.cases)
        ):
            # Create a new case for upload without any read sets or seqs, and with
            # updated case content equal to the validated content from the verification
            # step. This is a shallow copy so that the case contained in both the
            # original and the new case for upload is the shared.
            new_case_for_upload = case_for_upload.model_copy(deep=False)
            new_case_for_upload.read_sets = None
            new_case_for_upload.seqs = None
            cases_only_cmd.case_batch.cases[i] = new_case_for_upload
            case_for_upload = new_case_for_upload.case
            if case_for_upload is None:
                continue
            if case_for_upload.content != case_result.validated_content:
                # Set case content to validated content. Since the case is a reference
                # shared with the original cmd, it will be updated there as well
                case_for_upload.content = case_result.validated_content
            if case_for_upload.id is not None and case_for_upload.content:
                # Case and its content will be updated and has to be validated again
                cases_for_validation.append(case_for_upload)

        # Merge case content with that already in the database for updates, and
        # validate the merged content again so that there are no inconsistencies
        if cases_for_validation:
            # Get content of existing cases, keyed by case id to avoid relying on
            # result ordering from the DB.
            case_ids: list[UUID] = [
                x.id for x in cases_for_validation  # type: ignore[misc]
            ]
            existing_content_by_id: dict[UUID, dict] = {
                row[0]: row[1]
                for row in self.service.repository.read_fields(
                    uow,
                    None if cmd.user is None else cmd.user.id,
                    model.Case,
                    ["id", "content"],
                    filter=UuidSetFilter(key="id", members=frozenset(case_ids)),
                )
                if row[1] is not None
            }
            # Merge new content into existing
            for case_for_upload in cases_for_validation:
                existing_content = existing_content_by_id.get(case_for_upload.id)  # type: ignore[arg-type]
                if existing_content is None:
                    continue
                BatchUploader.update_sub_field_dict(
                    existing_content, case_for_upload.content
                )
                case_for_upload.content = existing_content
            # Validate cases again, this time with a complete CaseType that includes
            # all columns, i.e. with no ABAC applied
            complete_case_type = self._get_complete_case_type(cmd, ignore_abac=True)
            case_validator = self._get_case_validator(
                complete_case_type, cmd.user.id if cmd.user and cmd.user.id else NULL_ID
            )
            case_validator.validate_and_transform(cmd, batch_result)
            # # Reset case_date on existing cases after re-validation so that
            # # the immutability check in _upsert_existing_objs treats it as
            # # "not specified" (None) rather than an attempt to overwrite the
            # # stored value. The stored case_date is preserved unchanged.
            # # TODO LSP-3356: case date should be able to update
            # for case in cases_for_validation:
            #     case.case_date = None

        # Use the general parent method for upserting the cases
        success &= super().upsert_batch(cases_only_cmd, batch_result, uow)

        # Determine if there are samples to be created
        has_samples = self.has_samples(cmd, batch_result)
        if not has_samples:
            return success

        # Upsert samples via seqdb service, again through full upload including verification
        curr_success = True
        if success:
            # Only upload samples if case upload succeeded
            curr_success = self.upload_samples(cmd, batch_result, False)
            if curr_success:
                # The upload of samples may have updated the case content with IDs of created read sets and seqs, so the cases in the database need to be updated with the new content.
                for case_for_upload, case_only_for_upload in zip(
                    cmd.case_batch.cases, cases_only_cmd.case_batch.cases
                ):
                    assert (
                        case_for_upload is not None and case_for_upload.case is not None
                    )
                    assert case_only_for_upload.case is not None
                    case_only_for_upload.case.content = case_for_upload.case.content
                success &= super().upsert_batch(cases_only_cmd, batch_result, uow)
        success &= curr_success

        return success

    def has_samples(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
    ) -> bool:
        """
        Determine if there are any samples to be created in seqdb from the cases to
        be uploaded.
        """
        upload_samples_cmd, _ = self._get_upload_samples_command(cmd, batch_result)
        return upload_samples_cmd is not None

    def upload_samples(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
        verify_only: bool,
    ) -> bool:
        success = True
        # Get UploadSamplesCommand for any samples to be created
        upload_samples_cmd, sample_case_index_map = self._get_upload_samples_command(
            cmd, batch_result
        )
        if upload_samples_cmd is None:
            # No samples to verify
            return success

        # Upload to seqdb, possibly only verifying
        upload_samples_cmd.verify_only = verify_only
        seqdb_retval: seqdb_model.SampleBatchUploadResult = self.service.app.handle(
            upload_samples_cmd
        )
        success = seqdb_retval.get_status_count()[EtlStatus.FAILED] == 0

        # Map verification results back to cases and child IDs back to cases
        for sample_index, sample_result in enumerate(seqdb_retval.samples):
            # Map read sets and seqs back to cases
            for i, seqdb_result in enumerate(sample_result.read_sets or []):
                case_index, child_index = sample_case_index_map[
                    seqdb_model.ReadSetForUpload
                ][(sample_index, i)]
                case = cmd.case_batch.cases[case_index]
                assert case is not None and case.case is not None
                case_content = case.case.content
                result = batch_result.cases[case_index].read_sets[child_index]  # type: ignore[index]
                result.id = seqdb_result.id
                result.status = seqdb_result.status
                result.add_logs(seqdb_result.logs)
                assert case.read_sets is not None
                case_content[case.read_sets[child_index].col_id] = str(seqdb_result.id)
            # Map seqs back to cases
            for i, seqdb_result in enumerate(sample_result.seqs or []):
                case_index, child_index = sample_case_index_map[
                    seqdb_model.SeqForUpload
                ][(sample_index, i)]
                case = cmd.case_batch.cases[case_index]
                assert case is not None and case.case is not None
                case_content = case.case.content
                result = batch_result.cases[case_index].seqs[child_index]  # type: ignore[index]
                result.id = seqdb_result.id
                result.status = seqdb_result.status
                result.add_logs(seqdb_result.logs)
                assert case.seqs is not None
                case_content[case.seqs[child_index].col_id] = str(seqdb_result.id)

        return success

    def verify_case_content(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
    ) -> bool:
        """
        Verify the case content and add any derived values.
        """
        success = True
        # Initialize some
        status_count_before = batch_result.get_status_count()
        complete_case_type = self._get_complete_case_type(cmd)
        case_validator = self._get_case_validator(
            complete_case_type, cmd.user.id if cmd.user and cmd.user.id else NULL_ID
        )

        # Validate and transform each case
        case_validator.validate_and_transform(cmd, batch_result)

        # Update status of each result with data issues found
        for case_result in batch_result.cases:
            case_result.update_status_with_data_issues()

        # Update batch status if necessary
        status_count_after = batch_result.get_status_count()
        if status_count_after[EtlStatus.FAILED] > status_count_before[EtlStatus.FAILED]:
            success = False
        return success

    def _get_complete_case_type(
        self, cmd: command.UploadCasesCommand, ignore_abac: bool = False
    ) -> model.CompleteCaseType:
        """Get complete CaseType"""
        case_type_id = cmd.case_type_id
        user: model.User | None
        if ignore_abac:
            # Get complete CaseType without ABAC restrictions
            user = None
        else:
            user = cmd.user
        sub_cmd = command.RetrieveCompleteCaseTypeCommand(
            user=user, case_type_id=case_type_id
        )
        if not ignore_abac:
            sub_cmd._policies.extend(cmd._policies)
        complete_case_type: model.CompleteCaseType = (
            self.service.retrieve_complete_case_type(sub_cmd)
        )
        return complete_case_type

    def _get_case_validator(
        self, complete_case_type: model.CompleteCaseType, user_id: UUID
    ) -> CaseValidator:
        """Get case validator for the given complete CaseType"""
        return CaseValidator(self.service, complete_case_type, user_id)

    def _get_upload_samples_command(
        self,
        cmd: UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
    ) -> tuple[
        seqdb_command.UploadSamplesCommand | None,
        dict[type[model.Model], dict[tuple[int, int], tuple[int, int]]],
    ]:
        """
        Extracts any samples to be created in seqdb from the cases to be uploaded and
        create an UploadSamplesCommand. The batch_id of the latter command is set to
        the first 16 bytes of sha256 hash of the ID of the UploadCasesCommand, so that
        the link can be made between the two batches.
        """
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("7b5a31ae", "Invalid command type")
        if not isinstance(batch_result, model.CaseBatchUploadResult):
            raise exc.InvalidArgumentsError("e46018b7", "Invalid return value type")

        # Initialise some
        samples_for_upload: list[seqdb_model.SampleForUpload] = []
        sample_id_to_index_map: dict[UUID, int] = {}
        sample_external_id_to_index_map: dict[IdentifierForUpload, int] = {}
        sample_case_index_map: dict[int, int] = {}
        child_index_map: dict[
            type[model.Model], dict[tuple[int, int], tuple[int, int]]
        ] = defaultdict(dict)

        # Functionality to get/create new sample for upload
        def _get_or_create_sample_for_upload(
            case_index: int,
            sample_id: UUID | None,
            external_sample_id: IdentifierForUpload | None,
        ) -> int:
            has_id = sample_id is not None and sample_id != NULL_ID
            has_external_id = external_sample_id is not None
            if has_id and sample_id in sample_id_to_index_map:
                assert sample_id is not None
                return sample_id_to_index_map[sample_id]
            if (
                has_external_id
                and external_sample_id in sample_external_id_to_index_map
            ):
                return sample_external_id_to_index_map[external_sample_id]
            # New sample for upload: create
            sample_for_upload_id = sample_id if has_id else NULL_ID
            sample_for_upload = seqdb_model.SampleForUpload(
                id=sample_for_upload_id,
                sample=seqdb_model.Sample(
                    id=sample_for_upload_id,
                    created_in_data_collection_id=cmd.created_in_data_collection_id,
                ),
                identifiers=[external_sample_id] if has_external_id else [],  # type: ignore[call-arg]
                read_sets=[],
                seqs=[],
            )
            #  Add to list and maps
            sample_index = len(samples_for_upload)
            samples_for_upload.append(sample_for_upload)
            if has_id:
                sample_id_to_index_map[sample_id] = sample_index
            if has_external_id:
                sample_external_id_to_index_map[external_sample_id] = sample_index
            sample_case_index_map[sample_index] = case_index
            return sample_index

        # Process cases to extract samples for upload
        for case_index, (case_for_upload, case_result) in enumerate(
            zip(cmd.case_batch.cases, batch_result.cases)
        ):
            # Add read sets
            for i, read_set_for_upload in enumerate(case_for_upload.read_sets or []):
                sample_index = _get_or_create_sample_for_upload(
                    case_index,
                    read_set_for_upload.sample_id,
                    read_set_for_upload.other_sample_identifier,
                )
                sample_for_upload = samples_for_upload[sample_index]
                # Add read set
                assert sample_for_upload.read_sets is not None
                sample_for_upload.read_sets.append(
                    seqdb_model.ReadSetForUpload(
                        sample_id=NULL_ID,
                        protocol_id=read_set_for_upload.protocol_id,
                    )
                )
                child_index_map[seqdb_model.ReadSetForUpload][(sample_index, i)] = (
                    case_index,
                    i,
                )
            # Add seqs
            for i, seq_for_upload in enumerate(case_for_upload.seqs or []):
                sample_index = _get_or_create_sample_for_upload(
                    case_index,
                    seq_for_upload.sample_id,
                    seq_for_upload.other_sample_identifier,
                )
                sample_for_upload = samples_for_upload[sample_index]
                # Add sequence
                assert sample_for_upload.seqs is not None
                sample_for_upload.seqs.append(
                    seqdb_model.SeqForUpload(
                        sample_id=NULL_ID,
                        protocol_id=seq_for_upload.protocol_id,
                    )
                )
                child_index_map[seqdb_model.SeqForUpload][(sample_index, i)] = (
                    case_index,
                    i,
                )

        # Create command if any samples for upload were found
        if not samples_for_upload:
            return None, child_index_map
        batch_id = UUID(sha256(cmd.id.bytes).digest()[:16].hex())
        upload_samples_cmd = seqdb_command.UploadSamplesCommand(
            user=cmd.user,
            sample_batch=seqdb_model.SampleBatchForUpload(
                id=batch_id, samples=samples_for_upload
            ),
        )
        return upload_samples_cmd, child_index_map


def case_service_upload_cases(
    self: BaseCaseService, cmd: command.UploadCasesCommand
) -> model.CaseBatchUploadResult:
    batch_uploader = CaseBatchUploader(self)

    batch_result: model.CaseBatchUploadResult = batch_uploader.upload_batch(cmd)  # type: ignore[assignment]
    return batch_result
