import datetime
import uuid
from collections.abc import Hashable
from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
import gen_epix.seqdb.domain.command as seqdb_command
import gen_epix.seqdb.domain.model as seqdb_model
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.case_date import (
    case_service_calculate_case_date,
    case_service_get_case_date_case_type_col_mappers_from_cols,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.fastapp import CrudOperation


def case_service_upload_cases(
    self: BaseCaseService, cmd: command.UploadCasesCommand
) -> list[model.Case] | None:
    # Special case: zero cases to be created
    cases_for_upload = cmd.case_batch.cases
    if not cases_for_upload:
        return []

    # TODO handle cmd.is_update=True and cmd.cases_set.cases[i].has_content=False
    if cmd.is_update:
        raise NotImplementedError("Updating cases via upload is not yet implemented")
    if any(x.has_content is False for x in cases_for_upload):
        raise NotImplementedError(
            "Uploading cases without content is not yet implemented"
        )

    # Get case type and created_in data collection IDs
    case_type_id = cmd.case_type_id
    created_in_data_collection_id = cmd.created_in_data_collection_id

    # @ABAC: verify if case set or cases may be created in the given data collection(s)
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    is_allowed = case_abac.is_allowed(
        case_type_id,
        enum.CaseRight.ADD_CASE,
        True,
        created_in_data_collection_id=created_in_data_collection_id,
        tgt_data_collection_ids=cmd.data_collection_ids,
    )
    if not is_allowed:
        assert cmd.user is not None
        raise exc.UnauthorizedAuthError(
            f"User {cmd.user.id} is not allowed to create cases in the given data collection(s)"
        )

    # Convert cases for upload to regular cases
    # TODO: validate content and add derived values
    now = datetime.datetime.now()
    cases: list[model.Case] = [
        model.Case(
            id=x.id,
            case_type_id=cmd.case_type_id,
            subject_id=x.subject_id,
            created_in_data_collection_id=cmd.created_in_data_collection_id,
            case_date=now,
            content={y: z for y, z in x.content.items() if z is not None},
        )
        for x in cases_for_upload
    ]

    # Get complete case type
    sub_cmd = command.RetrieveCompleteCaseTypeCommand(
        user=cmd.user, case_type_id=case_type_id
    )
    sub_cmd._policies.extend(cmd._policies)
    complete_case_type: model.CompleteCaseType = self.retrieve_complete_case_type(
        sub_cmd
    )

    # Create cases and case data collection links
    with self.repository.uow() as uow:
        # Validate case data
        case_validation_report = self.validate_cases(cmd)
        for validated_case in case_validation_report.validated_cases:
            if any(
                x.data_rule in enum.CaseColDataRuleSet.PREVENTS_UPLOAD.value
                for x in validated_case.data_issues
            ):
                raise exc.InvalidArgumentsError(
                    f"Some cases have invalid data. None will be created."
                )

        # Create seqdb samples for upload containing any read sets and seqs
        seqdb_sample_map: dict[Hashable, seqdb_model.SampleForUpload] = {}
        for case_for_upload in cases_for_upload:
            for read_set in case_for_upload.read_sets or []:
                sample = _get_seqdb_sample(
                    seqdb_sample_map, read_set, created_in_data_collection_id
                )
                seqdb_read_set = seqdb_model.ReadSetForUpload(**read_set.model_dump())
                seqdb_read_set.sample_id = NULL_ID
                if sample.read_sets is None:
                    sample.read_sets = [seqdb_read_set]
                else:
                    sample.read_sets.append(seqdb_read_set)
            for seq in case_for_upload.seqs or []:
                sample = _get_seqdb_sample(
                    seqdb_sample_map, seq, created_in_data_collection_id
                )
                seqdb_seq = seqdb_model.SeqForUpload(**seq.model_dump())
                seqdb_seq.sample_id = NULL_ID
                if sample.seqs is None:
                    sample.seqs = [seqdb_seq]
                else:
                    sample.seqs.append(seqdb_seq)

        # Create any read sets, seqs and samples in seqdb
        if seqdb_sample_map:
            # TODO: implement seqdb_command.UploadSamplesCommand and parse SampleBatchUploadResult
            # seqdb_sample_upload_result: seqdb_model.SampleBatchUploadResult = self.app.handle(
            #     seqdb_command.UploadSamplesCommand(
            #         user=cmd.user,
            #         sample_batch=seqdb_model.SampleBatchForUpload(
            #             samples=list(seqdb_sample_map.values())
            #         ),
            #     )
            # )
            # TODO: TEMPORARY assign random IDs to samples, read sets and seqs
            for case_for_upload in cases_for_upload:
                for read_set in case_for_upload.read_sets or []:
                    read_set.id = uuid.uuid4()
                    case_for_upload.content[read_set.case_type_col_id] = str(
                        read_set.id
                    )
                for seq in case_for_upload.seqs or []:
                    seq.id = uuid.uuid4()
                    case_for_upload.content[seq.case_type_col_id] = str(seq.id)

        # Calculate case date where possible
        case_date_case_type_dim_id = complete_case_type.case_date_case_type_dim_id
        if case_date_case_type_dim_id is None:
            case_date_case_type_col_mappers = {}
        else:
            case_type_cols = [
                complete_case_type.case_type_cols[x]
                for x in complete_case_type.ordered_case_type_col_ids_by_dim[
                    case_date_case_type_dim_id
                ]
            ]
            case_date_case_type_col_mappers = (
                case_service_get_case_date_case_type_col_mappers_from_cols(
                    case_type_cols,
                    complete_case_type.cols,
                )
            )
        case_service_calculate_case_date(cases, case_date_case_type_col_mappers)

        # Create cases, using the parent class method to avoid ABAC
        # restrictions
        cases = super(DomainBaseCaseService, self).crud(  # type: ignore[assignment]
            command.CaseCrudCommand(
                user=cmd.user,
                operation=CrudOperation.CREATE_SOME,
                objs=cases,  # type: ignore[arg-type]
                props=cmd.props,
            )
        )

        # Fill in uploaded case IDs in the original case for upload objects
        for case_for_upload, created_case in zip(cases_for_upload, cases):
            case_for_upload.id = created_case.id
            for read_set in case_for_upload.read_sets or []:
                read_set.case_id = created_case.id
            for seq in case_for_upload.seqs or []:
                seq.case_id = created_case.id

        # TODO Create seqdb ReadSets and Seqs and add their IDs to the case content

        # Associate cases with data collections
        curr_cmd = command.CaseDataCollectionLinkCrudCommand(
            user=cmd.user,
            operation=CrudOperation.CREATE_SOME,
            objs=[
                model.CaseDataCollectionLink(
                    case_id=x.id, data_collection_id=y  # type: ignore[arg-type]
                )
                for x in cases
                for y in cmd.data_collection_ids
            ],
        )
        curr_cmd._policies.extend(cmd._policies)
        case_data_collection_links = self.crud(curr_cmd)
    return cases


def _get_seqdb_sample(
    samples_map: dict[Hashable, seqdb_model.SampleForUpload],
    value: model.ReadSetForUpload | model.SeqForUpload,
    created_in_data_collection_id: UUID,
) -> seqdb_model.SampleForUpload:
    if value.sample_id != NULL_ID:
        key = value.sample_id
    else:
        key = value.external_sample_id
    if key in samples_map:
        return samples_map[key]
    sample = seqdb_model.SampleForUpload(
        id=value.sample_id,
        created_in_data_collection_id=created_in_data_collection_id,
        external_ids=(
            None if value.external_sample_id is None else {value.external_sample_id}
        ),
    )
    samples_map[key] = sample
    return sample


def _upload_read_sets_or_seqs_for_cases(
    self: BaseCaseService,
    cmd: command.CreateReadSetsForCasesCommand | command.CreateSeqsForCasesCommand,
) -> list[model.ReadSet] | list[model.Seq]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    # Parse input
    read_sets: list[model.ReadSet] = []
    seqs: list[model.Seq] = []
    case_ids: list[UUID] = []
    case_type_col_ids: list[UUID] = []
    if isinstance(cmd, command.CreateReadSetsForCasesCommand):
        is_read_set = True
        read_sets = [x.read_set for x in cmd.read_sets]  # type:ignore
        case_ids = [x.case_id for x in cmd.read_sets]
        case_type_col_ids = [x.case_type_col_id for x in cmd.read_sets]
    elif isinstance(cmd, command.CreateSeqsForCasesCommand):
        is_read_set = False
        seqs = [x.seq for x in cmd.seqs]  # type:ignore
        case_ids = [x.case_id for x in cmd.seqs]
        case_type_col_ids = [x.case_type_col_id for x in cmd.seqs]
    else:
        raise exc.InvalidArgumentsError("Invalid command type")

    # Special case: nothing to create
    if is_read_set and not read_sets:
        return []
    if not is_read_set and not seqs:
        return []

    # Retrieve case ABAC
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    # Handle transactions
    with repository.uow() as uow:
        cases = _get_cases_for_create_read_sets_or_seqs(
            self, cmd, case_abac, uow, user.id, case_ids, case_type_col_ids
        )

        # Create ReadSets or Seqs
        created_objs: list[model.ReadSet] | list[model.Seq]
        command_class = (
            seqdb_command.ReadSetCrudCommand
            if is_read_set
            else seqdb_command.SeqCrudCommand
        )
        created_objs = self.app.handle(
            command_class(
                user=cmd.user,
                operation=CrudOperation.CREATE_SOME,
                objs=read_sets if is_read_set else seqs,  # type: ignore[arg-type]
            )
        )

        # Update Cases with created ReadSet or Seq IDs
        for case, case_type_col_id, created_obj in zip(
            cases, case_type_col_ids, created_objs
        ):
            case.content[case_type_col_id] = str(created_obj.id)
        super(DomainBaseCaseService, self).crud(
            command.CaseCrudCommand(
                user=cmd.user,
                operation=CrudOperation.UPDATE_SOME,
                objs=cases,  # type: ignore[arg-type]
            )
        )

    return created_objs
