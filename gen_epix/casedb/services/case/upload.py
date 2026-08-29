from collections import defaultdict
from hashlib import sha256
from typing import cast
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.model as model
import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import enum, exc
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_validator import CaseValidator
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.commondb.domain.enum import DataIssueType, EtlStatus, RoleSet
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
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
            raise exc.InvalidArgumentsError("915489e8", "Invalid service type")
        self.service: BaseCaseService = service

    def verify_user_rights(self, cmd: UploadBatchCommandMixin) -> None:
        """
        Implements user RBAC rights verification for uploading cases.
        ABAC rights are not verified here since this requires knowing per case whether
        it already exists in the database and what data collection(s) it belongs to,
        which is only determined during batch verification. ABAC rights are therefore
        verified during batch verification.
        """
        # Verify command type
        if not isinstance(cmd, command.UploadCasesCommand):
            raise exc.InvalidArgumentsError("510ea98a", "Invalid command type")

        # Verify user has at least one role that may manipulate case data
        if cmd.user is not None and not cmd.user.roles.intersection(
            self.service.role_set_map[RoleSet.GE_ORG_USER]
        ):
            raise exc.UnauthorizedAuthError(
                "d8c05dc7",
                f"User {None if cmd.user is None else cmd.user.id} is not allowed to manipulate case data",
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

        # Set default created_in_data_collection_id where relevant
        success &= self._set_default_created_in_data_collection_id(cmd, batch_result)

        # Verify ABAC rights
        success &= self._verify_abac_rights(cmd, batch_result, uow)

        # Verify case content. Derived values and data issues are also added in the
        # form of ValidatedCaseForUpload objects in the result.
        success &= self._verify_case_content(cmd, batch_result)

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
            case = new_case_for_upload.case
            if case is None:
                continue
            if case.content != case_result.validated_content:
                # Set case content to validated content. Since the case is a reference
                # shared with the original cmd, it will be updated there as well
                case.content = case_result.validated_content
            if case_result.is_new and case.content:
                # For creates, None has no deletion semantics and must never be
                # persisted as content value.
                case.content = {x: y for x, y in case.content.items() if y is not None}
            if not self.is_null(case.id) and case.content:
                # Case and its content will be updated and has to be validated again
                cases_for_validation.append(case)

        # Merge case content with that already in the database for updates, and
        # validate the merged content again so that there are no inconsistencies
        if cases_for_validation:
            # Get content of existing cases, keyed by case id to avoid relying on
            # result ordering from the DB.
            case_ids: list[UUID] = [
                x.id for x in cases_for_validation  # type: ignore[misc]
            ]
            existing_content_by_id: dict[UUID, dict] = {
                row[0]: {
                    x if isinstance(x, UUID) else UUID(x): y for x, y in row[1].items()
                }
                for row in self.service.repository.read_fields(
                    uow,
                    None if cmd.user is None else cmd.user.id,
                    model.Case,
                    ["id", "content"],
                    filter=UuidSetFilter(key="id", members=frozenset(case_ids)),
                )
                if row[1] is not None
            }
            self._validate_merged_content(cmd, batch_result, existing_content_by_id)

        # Use the general parent method for upserting the cases
        is_pending_before_cases_only_upsert = [
            x.status == EtlStatus.PENDING for x in batch_result.cases
        ]
        success &= super().upsert_batch(cases_only_cmd, batch_result, uow)

        # Determine if there are samples to be created or updated
        if not cmd.case_batch.has_samples():
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
                # Reset case_result status to pending for cases that were pending before the cases only, since the content update may have fixed the issues that caused them to be failed, and they should be retried in the next batch upload attempt. Cases that were not pending before should keep their status since they may have other issues that need to be fixed.
                for case_result, was_pending in zip(
                    batch_result.cases, is_pending_before_cases_only_upsert
                ):
                    if was_pending:
                        case_result.status = EtlStatus.PENDING
                        case_result.is_new = (
                            False  # TODO: Check if this fixes the actual bug
                        )
                success &= super().upsert_batch(cases_only_cmd, batch_result, uow)
        success &= curr_success

        return success

    def _validate_merged_content(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
        existing_content_by_id: dict[UUID, dict],
    ) -> None:
        """
        Re-validate each case's content merged with what is already in the
        database, so inconsistencies in the resulting state are caught, not
        just in the incoming change.

        The merge and validation temporarily replace each case's content
        with the full merged state (existing content with the incoming
        change applied, so deleted keys are simply absent rather than
        explicitly None) directly on the real case object, since
        CaseValidator.validate_and_transform mutates the case in place for
        more than just content (e.g. it recalculates case_date). Afterward,
        only the deleted keys are put back as explicit None: the generic
        upsert that runs after this re-derives its own diff from a fresh DB
        read and can only detect a deletion via an explicit {key: None}
        entry, not a key's mere absence. Added or changed keys are already
        correctly represented by their new value in the merged content, so
        only deletions need reinstating; anything else validation may do to
        content in place (e.g. normalizing a value) is left untouched.
        """
        deleted_col_ids_by_case_id: dict[UUID, set[UUID]] = {}
        for case_for_upload in cmd.case_batch.cases:
            case = case_for_upload.case
            if case is None:
                continue
            existing_content = existing_content_by_id.get(case.id)  # type: ignore[arg-type]
            if existing_content is None:
                continue
            deleted_col_ids_by_case_id[case.id] = {  # type: ignore[index]
                col_id for col_id, value in case.content.items() if value is None
            }
            merged_content = dict(existing_content)
            BatchUploader.update_sub_field_dict(merged_content, case.content)
            case.content = merged_content

        complete_case_type = self._get_complete_case_type(cmd, ignore_abac=True)
        case_validator = self._get_case_validator(
            complete_case_type,
            cmd.user.id if cmd.user and cmd.user.id else NULL_ID,
        )
        case_validator.validate_and_transform(cmd, batch_result)

        for case_for_upload in cmd.case_batch.cases:
            case = case_for_upload.case
            if case is None:
                continue
            deleted_col_ids = deleted_col_ids_by_case_id.get(case.id)  # type: ignore[arg-type]
            if not deleted_col_ids:
                continue
            for col_id in deleted_col_ids:
                case.content[col_id] = None

    def upload_samples(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
        verify_only: bool,
    ) -> bool:
        success = True
        # Get UploadSamplesCommand for any samples to be created
        curr_success, upload_samples_cmd, sample_case_index_map = (
            self._get_upload_samples_command(cmd, batch_result)
        )
        success &= curr_success
        if not success:
            # There were issues with the samples to be uploaded that should prevent the upload from being attempted, such as missing case for read sets or seqs.
            return success
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
                # only update content if there is an ID, otherwise a unknown value appears in the content,
                # causing a data validation issue in the case upload
                if seqdb_result.id is not None:
                    case_content[case.read_sets[child_index].col_id] = str(
                        seqdb_result.id
                    )
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
                if seqdb_result.id is not None:
                    case_content[case.seqs[child_index].col_id] = str(seqdb_result.id)

        return success

    def _set_default_created_in_data_collection_id(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
    ) -> bool:
        """
        Set the created_in_data_collection_id for each new case to the default value
        if not provided.

        This does not check that created_in_data_collection_id for an existing case
        would be altered: this is assumed to have been checked through immutability
        of fields. It also does not replace any
        created_in_data_collection_id=NULL_ID of an existing case with the actual
        created_in_data_collection_id.
        """
        success = True

        # Verify default created_in_data_collection_id, if provided, is a valid data collection ID
        has_default_created_in_data_collection_id = not self.is_null(
            cmd.default_created_in_data_collection_id
        )
        if has_default_created_in_data_collection_id:
            is_existing = self.service.app.handle(
                command.DataCollectionCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.EXISTS_SOME,
                    obj_ids=[cmd.default_created_in_data_collection_id],
                )
            )
            if not is_existing:
                batch_result.add_error(
                    "d1f9e8c3",
                    f"Default created_in_data_collection_id {cmd.default_created_in_data_collection_id} does not exist.",
                )
                success = False

        # Set default created_in_data_collection_id where relevant
        for case_for_upload, case_result in zip(
            cmd.case_batch.cases, batch_result.cases
        ):
            if not case_result.is_new:
                # Existing case: nothing to do
                continue
            case = case_for_upload.case
            assert case is not None
            if not self.is_null(case.created_in_data_collection_id):
                # created_in_data_collection_id provided at case level: nothing to do
                continue
            if has_default_created_in_data_collection_id:
                # Set default created_in_data_collection_id at case level
                case.created_in_data_collection_id = (
                    cmd.default_created_in_data_collection_id
                )
                case_result.add_info(
                    "d2a7b9f4",
                    f"created_in_data_collection_id set to default value {cmd.default_created_in_data_collection_id}.",
                )
            else:
                case_result.add_error(
                    "c1f8e9d4",
                    "created_in_data_collection_id not provided and no default available.",
                )
                success = False
        return success

    def _verify_abac_rights(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Verify ABAC rights for the cases to be uploaded. This requires knowing per case
        whether it already exists in the database and what data collection(s) it
        belongs to, since ABAC rights are based on data collection membership. This
        information is only determined during batch verification, so ABAC rights are
        verified here rather than in verify_user_rights.

        This method assumes that the cases have already been verified to be valid in
        terms of existence of parents and children, and filling in
        case.created_in_data_collection_id.
        """
        success = True
        # Get complete CaseType with no ABAC applied to get all columns for validation
        complete_case_type = self._get_complete_case_type(cmd, ignore_abac=True)

        # Get private data collections in which the user may create new cases
        allowed_created_data_collection_ids = set()
        for (
            data_collection_id,
            access_abac,
        ) in complete_case_type.case_type_access_abacs.items():
            if access_abac.is_private and access_abac.add_case:
                allowed_created_data_collection_ids.add(data_collection_id)

        # Get data collection IDs for each case
        case_data_collections = self._get_case_data_collections(cmd, batch_result, uow)

        # Get readable and writeable columns for each unique combination of data collection IDs
        uq_col_access: dict[frozenset[UUID], tuple[set[UUID], set[UUID]]] = {}
        for case_for_upload, case_result, data_collection_ids in zip(
            cmd.case_batch.cases, batch_result.cases, case_data_collections
        ):
            # Determine if the case, if new, may be created by this user
            if case_result.is_new:
                case = case_for_upload.case
                assert case is not None
                if (
                    case.created_in_data_collection_id
                    not in allowed_created_data_collection_ids
                ):
                    # Case would be created in a data collection in which the user has no create access
                    case_result.add_error(
                        "29e256f1",
                        f"Not allowed to create cases in data collection {case.created_in_data_collection_id}",
                    )
                    success = False

            # Get all column IDs that would be written, including those from the case content, read sets and seqs
            content: dict[UUID, str | None] | None = (
                case_for_upload.case.content
                if case_for_upload.case is not None
                else None
            )
            content_col_ids = set(content.keys()) if content is not None else set()
            col_ids = (
                content_col_ids
                | {x.col_id for x in case_for_upload.read_sets or []}
                | {x.col_id for x in case_for_upload.seqs or []}
            )

            # Retrieve readable_col_ids, writeable_col_ids for this combination of data_collection_ids, or calculate and cache if not seen before
            readable_col_ids, writeable_col_ids = uq_col_access.get(
                data_collection_ids, (None, None)
            )
            if readable_col_ids is None or writeable_col_ids is None:
                readable_col_ids = set()
                writeable_col_ids = set()
                for data_collection_id in data_collection_ids:
                    if (
                        data_collection_id
                        not in complete_case_type.case_type_access_abacs
                    ):
                        # Case data collection not found in CaseType access ABACs for this user -> no access to any columns for this data collection
                        continue
                    access_abac = complete_case_type.case_type_access_abacs[
                        data_collection_id
                    ]
                    readable_col_ids.update(access_abac.read_col_ids)
                    writeable_col_ids.update(access_abac.write_col_ids)
                uq_col_access[data_collection_ids] = (
                    readable_col_ids,
                    writeable_col_ids,
                )
            # Check if all provided columns are writeable
            no_write_access_col_ids = col_ids - writeable_col_ids
            if not no_write_access_col_ids:
                # All columns are writeable -> no ABAC issues
                continue
            # Go over columns with no write access -> remove value and add data issue
            for col_id in no_write_access_col_ids:
                if content is not None and col_id in content:
                    orig_value = content[col_id]
                    del content[col_id]
                else:
                    # Column is not in content, so it must be from a read set or seq. These are not included in the content and therefore no value can be removed, but a data issue should still be added if there is no write access.
                    orig_value = None
                if col_id in readable_col_ids:
                    # Read access but no write access -> not authorized but informative message since the user can see the column but not update it
                    code = "3e7c1a9f"
                    message = "No write access, only read access"
                else:
                    # No access to this col_id, whether it actually exists or not -> treat as unauthorized since the user should not know the difference
                    code = "a7b3f9d2"
                    message = "Unknown Col"
                case_result.data_issues.append(
                    model.CaseDataIssue(
                        col_id=col_id,
                        original_value=orig_value,
                        updated_value=None,
                        data_issue_type=DataIssueType.UNAUTHORIZED,
                        code=code,
                        message=message,
                    )
                )

        return success

    def _verify_case_content(
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

    def _get_case_data_collections(
        self,
        cmd: command.UploadCasesCommand,
        batch_result: model.CaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> list[frozenset[UUID]]:
        """
        Get the data collection IDs associated with each case ID from the cases to be
        uploaded, including both the created in data collection ID and any data
        collection IDs from CaseDataCollectionLink if the case already exists.
        """
        # Get case IDs, their created in data collection IDs and whether the case is existing
        case_id_created_in_data_collection_ids = []
        for x, y in zip(cmd.case_batch.cases, batch_result.cases):
            case_id = cast(UUID, x.id)
            created_in_data_collection_id = (
                x.case.created_in_data_collection_id if x.case is not None else NULL_ID
            )
            is_existing = not y.is_new
            case_id_created_in_data_collection_ids.append(
                (
                    case_id,
                    created_in_data_collection_id,
                    is_existing,
                    {created_in_data_collection_id},
                )
            )

        # Get CaseDataCollectionLink objects for existing cases
        case_data_collection_links: list[model.CaseDataCollectionLink] = []
        if any(
            x[2] for x in case_id_created_in_data_collection_ids
        ):  # Only query for links if there are any existing cases, since links can only exist for existing cases:
            case_data_collection_links = self.service.repository.crud(
                uow,
                None if cmd.user is None else cmd.user.id,
                model.CaseDataCollectionLink,
                CrudOperation.READ_ALL,
                filter=UuidSetFilter(
                    key="case_id",
                    members=frozenset(
                        [x[0] for x in case_id_created_in_data_collection_ids if x[2]]
                    ),
                ),
            )
            # Add data collection IDs from links to the sets in case_id_created_in_data_collection_ids. Optimised by sorting both lists by case ID and iterating through them in a single pass, relying on the fact that the links for each case are grouped together since they have the same case ID.
            case_id_to_idx = {
                x[0]: i for i, x in enumerate(case_id_created_in_data_collection_ids)
            }
            case_data_collection_links.sort(key=lambda x: x.case_id)
            curr_case_id: UUID = NULL_ID
            curr_set: set[UUID] = set()
            case_idx = -1
            for link in case_data_collection_links:
                if link.case_id != curr_case_id:
                    curr_case_id = link.case_id
                    case_idx = case_id_to_idx[curr_case_id]
                    curr_set = case_id_created_in_data_collection_ids[case_idx][3]
                curr_set.add(link.data_collection_id)

        # Create output as list of frozenset
        case_data_collections = [
            frozenset(x[3]) for x in case_id_created_in_data_collection_ids
        ]

        return case_data_collections

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
        bool,
        seqdb_command.UploadSamplesCommand | None,
        dict[type[model.Model], dict[tuple[int, int], tuple[int, int]]],
    ]:
        """
        Extracts any samples to be created in seqdb from the cases to be uploaded and
        create an UploadSamplesCommand. The batch_id of the latter command is set to
        the first 16 bytes of sha256 hash of the ID of the UploadCasesCommand, so that
        the link can be made between the two batches.
        """
        success = True
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
            has_id = not self.is_null(sample_id)
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
                    created_in_data_collection_id=cmd.default_created_in_data_collection_id,
                ),
                identifiers=[external_sample_id] if has_external_id else [],  # type: ignore[call-arg]
                read_sets=[],
                seqs=[],
            )
            #  Add to list and maps
            sample_index = len(samples_for_upload)
            samples_for_upload.append(sample_for_upload)
            if has_id:
                assert sample_id is not None
                sample_id_to_index_map[sample_id] = sample_index
            if has_external_id:
                assert external_sample_id is not None
                sample_external_id_to_index_map[external_sample_id] = sample_index
            sample_case_index_map[sample_index] = case_index
            return sample_index

        # Process cases to extract samples for upload
        for case_index, (case_for_upload, case_result) in enumerate(
            zip(cmd.case_batch.cases, batch_result.cases)
        ):
            has_case = case_for_upload.case is not None
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
                if not has_case:
                    # Case is required for read sets, so if there is no case, the read set cannot be uploaded and should be marked as failed with an appropriate message
                    success = False
                    curr_result = case_result.read_sets[i]  # type: ignore[index]
                    curr_result.status = EtlStatus.FAILED
                    curr_result.add_error(
                        "cea1cae9",
                        "Case must be provided for read sets to be uploaded",
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
                if not has_case:
                    # Case is required for seqs, so if there is no case, the seq cannot be uploaded and should be marked as failed with an appropriate message
                    success = False
                    assert case_result.seqs is not None
                    curr_result = case_result.seqs[i]  # type: ignore[index]
                    curr_result.status = EtlStatus.FAILED
                    curr_result.add_error(
                        "1f1c3c29",
                        "Case must be provided for seqs to be uploaded",
                    )
        # Create command if any samples for upload were found
        if not samples_for_upload:
            return True, None, child_index_map
        batch_id = UUID(sha256(cmd.id.bytes).digest()[:16].hex())
        upload_samples_cmd = seqdb_command.UploadSamplesCommand(  # type: ignore[call-arg]
            user=cmd.user,
            sample_batch=seqdb_model.SampleBatchForUpload(
                id=batch_id, samples=samples_for_upload
            ),
            on_exists=cmd.on_exists,
            on_new=cmd.on_new,
        )
        return success, upload_samples_cmd, child_index_map


def case_service_upload_cases(
    self: BaseCaseService, cmd: command.UploadCasesCommand
) -> model.CaseBatchUploadResult:
    if self.app.get_feature_flag(enum.FeatureFlag.DISABLE_UPLOAD.value):
        raise exc.FeatureDisabledServiceError("a756246d", "Upload is disabled")
    batch_uploader = CaseBatchUploader(cast(BaseService, self))

    batch_result: model.CaseBatchUploadResult = batch_uploader.upload_batch(cmd)  # type: ignore[assignment]
    return batch_result
