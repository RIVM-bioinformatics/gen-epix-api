from collections import defaultdict
from hashlib import sha256
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.enum import DataIssueTypeSet
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_transformer import CaseValidator
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.commondb.domain.model.upload import BaseBatchUploadResult
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp.enum import CrudOperation
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
            raise exc.InvalidArgumentsError("Invalid service type")
        self.service: BaseCaseService = service

    def verify_user_rights(self, cmd: UploadBatchCommandMixin) -> None:
        """
        Implements user rights verification for uploading cases. Only ABAC rights are
        verified: the user must have write access to all case type columns contained in
        the uploaded cases for the created in data collection.
        """
        # Verify command type
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("Invalid command type")
        # Determine case type columns with write access
        complete_case_type = self._get_complete_case_type(cmd)
        case_type_access_abac = complete_case_type.case_type_access_abacs.get(
            cmd.created_in_data_collection_id
        )
        if case_type_access_abac is None:
            raise exc.UnauthorizedAuthError(
                f"User {None if cmd.user is None else cmd.user.id} is not allowed to access cases in the given data collection"
            )
        write_case_type_col_ids = case_type_access_abac.write_case_type_col_ids
        if not write_case_type_col_ids:
            raise exc.UnauthorizedAuthError(
                f"User {None if cmd.user is None else cmd.user.id} is not allowed to write any case type columns for cases in the given data collection"
            )

        # Determine if uploaded cases only contain writable columns
        unauthorized_case_type_cols = set()
        for case_for_upload in cmd.case_batch.cases:
            case = case_for_upload.case
            if case is None:
                continue
            content = case.content
            if not content:
                continue
            # Determine unauthorized columns in case content
            unauthorized_case_type_cols.update(
                set(content.keys()) - write_case_type_col_ids
            )
            # Determine unauthorized columns in read sets
            unauthorized_case_type_cols.update(
                set(x.case_type_col_id for x in case_for_upload.read_sets or [])
                - write_case_type_col_ids
            )
            # Determine unauthorized columns in seqs
            unauthorized_case_type_cols.update(
                set(x.case_type_col_id for x in case_for_upload.seqs or [])
                - write_case_type_col_ids
            )
        if unauthorized_case_type_cols:
            unauthorized_case_type_cols_str = ", ".join(
                str(x) for x in sorted(unauthorized_case_type_cols)
            )
            raise exc.UnauthorizedAuthError(
                f"User {None if cmd.user is None else cmd.user.id} is not allowed to write case type columns {unauthorized_case_type_cols_str} contained in the batch case , for the given data collection"
            )

    def verify_batch(
        self,
        cmd: UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Extends batch verification to the case content as well as the read sets and
        seqs, which are verified by seqdb.
        """
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("Invalid command type")
        if not isinstance(retval, model.CaseBatchUploadResult):
            raise exc.InvalidArgumentsError("Invalid return value type")
        success = True

        # Verify samples via seqdb service
        success &= self.upload_samples(cmd, retval, True)

        # Verify generic aspects. This will fill in any case IDs based on external
        # identifiers. The case IDs are needed for case content validation when the
        # case is being updated, since the merged content is validated and the IDs
        # are needed to retrieve the cases.
        success &= super().verify_batch(cmd, retval, uow)

        # Verify case content. Derived values and data issues are also added in the
        # form of ValidatedCaseForUpload objects in the result.
        success &= self.verify_case_content(cmd, retval)

        return success

    def upsert_batch(
        self,
        cmd: UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Extends batch upload to uploading the cases with this service, and the read
        sets and seqs to seqdb.
        """
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("Invalid command type")
        if not isinstance(retval, model.CaseBatchUploadResult):
            raise exc.InvalidArgumentsError("Invalid return value type")
        success = True

        # Create new command with only cases and content updated during verification
        cases_only_cmd = cmd.model_copy()
        cases_only_cmd.case_batch = cmd.case_batch.model_copy()
        cases_only_cmd.case_batch.cases = [x.model_copy() for x in cmd.case_batch.cases]
        cases_for_validation: list[model.Case] = []
        for i, (case_for_upload, case_result) in enumerate(
            zip(cases_only_cmd.case_batch.cases, retval.cases)
        ):
            # Create a new case for upload without any read sets or seqs, and with
            # updated case content equal to the validated content from the verification
            # step.
            new_case_for_upload = case_for_upload.model_copy()
            new_case_for_upload.read_sets = None
            new_case_for_upload.seqs = None
            cases_only_cmd.case_batch.cases[i] = new_case_for_upload
            case = new_case_for_upload.case
            if case is None:
                continue
            if case.content != case_result.validated_content:
                # Set case content to validated content. Since the case is a reference
                # shared with the original cmd, it will be updated there as well
                case.content = case_result.validated_content
            if case.id is not None and case.content:
                # Case and its content will be updated and has to be validated again
                cases_for_validation.append(case)

        # Merge case content with that already in the database for updates, and
        # validate the merged content again so that there are no inconsistencies
        if cases_for_validation:
            # Get content of existing cases
            case_ids: list[UUID] = [
                x.id for x in cases_for_validation  # type: ignore[misc]
            ]
            existing_content_tuples: list[dict[UUID, str | None] | None] = (
                self.service.repository.read_fields(  # type:ignore[assignment]
                    uow,
                    None if cmd.user is None else cmd.user.id,
                    model.Case,
                    ["content"],
                    filter=UuidSetFilter(key="id", members=frozenset(case_ids)),
                )
            )
            # Merge new content into existing
            for case, existing_content in zip(
                cases_for_validation, existing_content_tuples
            ):
                if existing_content is None:
                    continue
                BatchUploader.update_sub_field_dict(existing_content, case.content)
                case.content = existing_content
            # Validate cases again, this time with a complete case type that includes
            # all columns, i.e. with no ABAC applied
            complete_case_type = self._get_complete_case_type(cmd, ignore_abac=True)
            case_validator = self._get_case_validator(
                complete_case_type, cmd.user.id if cmd.user and cmd.user.id else NULL_ID
            )
            case_validator.validate_and_transform(cmd, retval)
            # TODO: scrub any calculated case dates that are based on case type columns
            # that are not writable by the user

        # Use the general parent method for upserting the cases
        success &= super().upsert_batch(cases_only_cmd, retval, uow)

        # Upsert samples via seqdb service, again through full upload including verification
        curr_success = True
        if success:
            # Only upload samples if case upload succeeded
            curr_success = self.upload_samples(cmd, retval, False)
        if not curr_success:
            # Sample upload failed but cases were already created: the rest of the
            # upload will be rolled back as well, with the exception of any new external
            # identifiers since these are not within the scope of the transaction.
            # An attempt is made to delete these again, which may fail silently if
            # they were already deleted.
            success &= self.delete_new_external_identifiers(cmd, retval)
        success &= curr_success

        return success

    def upload_samples(
        self,
        cmd: command.UploadCasesCommand,
        retval: model.CaseBatchUploadResult,
        verify_only: bool,
    ) -> bool:
        success = True
        # Get UploadSamplesCommand for any samples to be created
        upload_samples_cmd, sample_case_index_map = self._get_upload_samples_command(
            cmd, retval
        )
        if upload_samples_cmd is None:
            # No samples to verify
            return success

        # Upload to seqdb, possibly only verifying
        upload_samples_cmd.verify_only = verify_only
        seqdb_retval: seqdb_model.SampleBatchUploadResult = self.service.app.handle(
            upload_samples_cmd
        )
        success = seqdb_retval.get_status_count()[UploadStatus.FAILED] == 0

        # Map verification results back to cases
        for sample_index, sample_result in enumerate(seqdb_retval.samples):
            # Map read sets and seqs back to cases
            for i, seqdb_result in enumerate(sample_result.read_sets or []):
                case_index, child_index = sample_case_index_map[
                    seqdb_model.ReadSetForUpload
                ][(sample_index, i)]
                result = retval.cases[case_index].read_sets[child_index]  # type: ignore[index]
                result.id = seqdb_result.id
                result.status = seqdb_result.status
                result.add_logs(seqdb_result.logs)
            # Map seqs back to cases
            for i, seqdb_result in enumerate(sample_result.seqs or []):
                case_index, child_index = sample_case_index_map[
                    seqdb_model.SeqForUpload
                ][(sample_index, i)]
                result = retval.cases[case_index].seqs[child_index]  # type: ignore[index]
                result.id = seqdb_result.id
                result.status = seqdb_result.status
                result.add_logs(seqdb_result.logs)

        return success

    def verify_case_content(
        self,
        cmd: command.UploadCasesCommand,
        retval: model.CaseBatchUploadResult,
    ) -> bool:
        """
        Verify the case content and add any derived values.
        """
        success = True
        # Initialize some
        status_count_before = retval.get_status_count()
        complete_case_type = self._get_complete_case_type(cmd)
        case_validator = self._get_case_validator(
            complete_case_type, cmd.user.id if cmd.user and cmd.user.id else NULL_ID
        )

        # Validate and transform each case
        case_validator.validate_and_transform(cmd, retval)

        # Convert data issues found into failed upload status
        for case_result in retval.cases:
            data_issues = case_result.data_issues
            if data_issues is None:
                continue
            # Errors
            error_codes = {
                x.code
                for x in data_issues
                if x.data_issue_type in DataIssueTypeSet.ERROR.value
            }
            if error_codes:
                error_codes_str = ", ".join(sorted(error_codes))
                case_result.add_error(
                    "d3f5c1a2",
                    f"Case has content error(s): {error_codes_str}",
                )
            # Warnings
            warning_codes = {
                x.code
                for x in data_issues
                if x.data_issue_type in DataIssueTypeSet.WARNING.value
            }
            if warning_codes:
                warning_codes_str = ", ".join(sorted(warning_codes))
                case_result.add_warning(
                    "b4e6d2c3",
                    f"Case has content warning(s): {warning_codes_str}",
                )
            # Info
            info_codes = {
                x.code
                for x in data_issues
                if x.data_issue_type in DataIssueTypeSet.INFO.value
            }
            if info_codes:
                info_codes_str = ", ".join(sorted(info_codes))
                case_result.add_info(
                    "c5d7e8f9",
                    f"Case has content info(s): {info_codes_str}",
                )

        # Update batch status if necessary
        status_count_after = retval.get_status_count()
        if (
            status_count_after[UploadStatus.FAILED]
            > status_count_before[UploadStatus.FAILED]
        ):
            success = False
        return success

    def delete_new_external_identifiers(
        self, cmd: command.UploadCasesCommand, retval: model.CaseBatchUploadResult
    ) -> bool:
        success = True
        external_identifier_ids: list[UUID] = [
            y.id  # type:ignore[misc]
            for x in retval.cases
            for y in x.external_identifiers or []
            if y.status == UploadStatus.CREATED
        ]
        if not external_identifier_ids:
            return success
        existing_new_external_identifier_ids: list[UUID] = self.service.app.handle(
            command.ExternalIdentifierCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ALL,
                query_filter=UuidSetFilter(
                    key="id", members=frozenset(external_identifier_ids)
                ),
                props={"return_id": True},
            )
        )
        try:
            self.service.app.handle(
                command.ExternalIdentifierCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.DELETE_SOME,
                    obj_ids=existing_new_external_identifier_ids,
                    props={"return_id": True},
                )
            )
            retval.add_info(
                "f0g1h2i3",
                "Case upload failed due to associated sample upload errors, new external identifiers successfully deleted again.",
            )
        except:
            success = False
            retval.add_error(
                "f1g2h3i4",
                "Case upload failed due to associated sample upload errors, new external identifiers could not be deleted.",
            )
        return success

    def _get_complete_case_type(
        self, cmd: command.UploadCasesCommand, ignore_abac: bool = False
    ) -> model.CompleteCaseType:
        """Get complete case type"""
        case_type_id = cmd.case_type_id
        user: model.User | None
        if ignore_abac:
            # Get complete case type without ABAC restrictions
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
        """Get case validator for the given complete case type"""
        return CaseValidator(self.service, complete_case_type, user_id)

    def _get_upload_samples_command(
        self,
        cmd: UploadBatchCommandMixin,
        retval: BaseBatchUploadResult,
    ) -> tuple[
        seqdb_command.UploadSamplesCommand | None,
        dict[type[model.Model], dict[tuple[int, int], tuple[int, int]]],
    ]:
        """
        Extracts any samples to be created in seqdb from the cases to be uploaded and
        create an UploadSamplesCommand. The batch_id of the latter command is set to
        the first 16 bytes of sha256 hash of the id of the UploadCasesCommand, so that
        the link can be made between the two batches.
        """
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("Invalid command type")
        if not isinstance(retval, model.CaseBatchUploadResult):
            raise exc.InvalidArgumentsError("Invalid return value type")

        # Initialise some
        samples_for_upload: list[seqdb_model.SampleForUpload] = []
        sample_id_to_index_map: dict[UUID, int] = {}
        sample_external_id_to_index_map: dict[ExternalIdentifierForUpload, int] = {}
        sample_case_index_map: dict[int, int] = {}
        child_index_map: dict[
            type[model.Model], dict[tuple[int, int], tuple[int, int]]
        ] = defaultdict(dict)

        # Functionality to get/create new sample for upload
        def _get_or_create_sample_for_upload(
            case_index: int,
            sample_id: UUID | None,
            external_sample_id: ExternalIdentifierForUpload | None,
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
            assert sample_id is not None
            assert external_sample_id is not None
            sample_for_upload = seqdb_model.SampleForUpload(
                id=sample_id,
                sample=seqdb_model.Sample(
                    id=sample_id,
                    created_in_data_collection_id=cmd.created_in_data_collection_id,
                ),
                external_identifiers=[external_sample_id] if has_external_id else [],
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
            zip(cmd.case_batch.cases, retval.cases)
        ):
            # Add read sets
            for i, read_set_for_upload in enumerate(case_for_upload.read_sets or []):
                sample_index = _get_or_create_sample_for_upload(
                    case_index,
                    read_set_for_upload.sample_id,
                    read_set_for_upload.external_sample_id,
                )
                sample_for_upload = samples_for_upload[sample_index]
                # Add read set
                assert sample_for_upload.read_sets is not None
                sample_for_upload.read_sets.append(
                    seqdb_model.ReadSetForUpload(
                        sample_id=NULL_ID,
                        sequencing_protocol_id=read_set_for_upload.sequencing_protocol_id,
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
                    seq_for_upload.external_sample_id,
                )
                sample_for_upload = samples_for_upload[sample_index]
                # Add read set
                assert sample_for_upload.seqs is not None
                sample_for_upload.seqs.append(
                    seqdb_model.SeqForUpload(
                        sample_id=NULL_ID,
                        assembly_protocol_id=seq_for_upload.assembly_protocol_id,
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

    retval: model.CaseBatchUploadResult = batch_uploader.upload_batch(cmd)  # type: ignore[assignment]
    return retval
