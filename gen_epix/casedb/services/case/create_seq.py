from uuid import UUID

import gen_epix.casedb.domain.command as command
import gen_epix.casedb.domain.enum as enum
import gen_epix.casedb.domain.model as model
import gen_epix.seqdb.domain.command as seqdb_command
from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.domain.service import BaseCaseService as DomainBaseCaseService
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.fastapp import CrudOperation


def case_service_create_read_sets_for_cases(
    self: BaseCaseService, cmd: command.CreateReadSetsForCasesCommand
) -> list[model.ReadSet] | None:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    case_ids: set[UUID] = {x.case_id for x in cmd.case_read_sets}
    case_type_col_ids: set[UUID] = {x.case_type_col_id for x in cmd.case_read_sets}

    with repository.uow() as uow:
        # get case_type_col data
        case_type_cols: list[model.CaseTypeCol] = (
            self.repository.crud(  # type:ignore[assignment]
                uow,
                user.id if user else None,
                model.CaseTypeCol,
                None,
                list(case_type_col_ids),
                CrudOperation.READ_SOME,
            )
        )
        case_type_col_by_id: dict[UUID, model.CaseTypeCol] = {
            x.id: x for x in case_type_cols if x.id is not None
        }

        col_ids: set[UUID] = {case_type_col.col_id for case_type_col in case_type_cols}
        cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            list(col_ids),
            CrudOperation.READ_SOME,
        )
        col_by_id: dict[UUID, model.Col] = {x.id: x for x in cols if x.id is not None}

        # get case data
        cases: list[model.Case] = self.repository.crud(  # type:ignore[assignment]
            uow,
            user.id if user else None,
            model.Case,
            None,
            list(case_ids),
            CrudOperation.READ_SOME,
        )
        case_by_id: dict[UUID, model.Case] = {
            x.id: x for x in cases if x.id is not None
        }

        if not case_abac.is_full_access:
            # check verify access rights (for cmd.case_read_sets loop)
            writable_data_collections_by_case_type_col: dict[UUID, set[UUID]] = {
                x: case_abac.get_data_collections_with_access_right_for_case_type_col(
                    x, enum.CaseRight.WRITE_CASE
                )
                for x in case_type_col_ids
            }
            # Retrieve data collections by case id for ABAC column-level write checks
            case_to_data_collections: dict[UUID, set[UUID]] = (
                self._retrieve_case_data_collections_map(uow, user.id)
            )
            # For each requested (case, case_type_col), ensure the user has write access
            # to that column in at least one data collection the case belongs to
            for case_read_set in cmd.case_read_sets:
                # Membership includes created_in_data_collection_id
                case_data_collection_memberships = set(
                    case_to_data_collections.get(case_read_set.case_id, set())
                )
                case_data_collection_memberships.add(
                    case_by_id[case_read_set.case_id].created_in_data_collection_id
                )
                writable_in_data_collections = (
                    writable_data_collections_by_case_type_col.get(
                        case_read_set.case_type_col_id, set()
                    )
                )
                if case_data_collection_memberships.isdisjoint(
                    writable_in_data_collections
                ):
                    raise exc.UnauthorizedAuthError(
                        "User has no WRITE_CASE access to the specified column in any data collection of the case"
                    )

        # process each case
        created_read_sets: list[model.ReadSet] = []
        for case_read_set in cmd.case_read_sets:
            case = case_by_id[case_read_set.case_id]
            case_type_col = case_type_col_by_id[case_read_set.case_type_col_id]
            # check if case type col belongs to case type of case

            if case_type_col.case_type_id != case.case_type_id:
                raise exc.InvalidArgumentsError(
                    f"Column {case_read_set.case_type_col_id} not part of case type {case.case_type_id}"
                )
            # Check if col is of type GENETIC_READS
            col = col_by_id[case_type_col.col_id]
            if col.col_type != enum.ColType.GENETIC_READS:
                raise exc.InvalidArgumentsError(
                    f"Column {col.id} is not of type GENETIC_READS"
                )

            created_read_set: list[model.ReadSet] = self.app.handle(
                seqdb_command.ReadSetCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.CREATE_ONE,
                    objs=case_read_set.read_set,
                )
            )
            case.content[case_type_col.id] = created_read_set.id
            super(DomainBaseCaseService, self).crud(
                command.CaseCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.UPDATE_ONE,
                    objs=case,
                )
            )
            created_read_sets.append(created_read_set)

    return created_read_sets


def case_service_create_seqs_for_cases(
    self: BaseCaseService, cmd: command.CreateSeqsForCasesCommand
) -> list[model.Seq]:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None
    # Short-circuit: nothing to create
    if not cmd.case_seqs:
        return []

    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    case_ids: set[UUID] = {x.case_id for x in cmd.case_seqs}
    case_type_col_ids: set[UUID] = {x.case_type_col_id for x in cmd.case_seqs}

    with repository.uow() as uow:
        # Retrieve and validate cases
        cases: list[model.Case] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id if user else None,
            model.Case,
            None,
            list(case_ids),
            CrudOperation.READ_SOME,
        )
        if len(cases) != len(case_ids):
            raise exc.InvalidArgumentsError("Some case ids do not exist")

        # Case and column-level ABAC check
        self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.WRITE_CASE,
            case_ids=list(case_ids),
            filter_content=True,
            extra_access_case_type_col_ids=case_type_col_ids,
        )

        # Retrieve and validate case type columns
        case_type_cols: list[model.CaseTypeCol] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id if user else None,
            model.CaseTypeCol,
            None,
            list(case_type_col_ids),
            CrudOperation.READ_SOME,
        )
        if len(case_type_cols) != len(case_type_col_ids):
            raise exc.InvalidArgumentsError("Some case type column ids do not exist")

        # Retrieve underlying columns and maps for quick lookup
        col_ids: set[UUID] = {x.col_id for x in case_type_cols}
        cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            list(col_ids),
            CrudOperation.READ_SOME,
        )

        case_by_id: dict[UUID, model.Case] = {
            x.id: x for x in cases if x.id is not None
        }
        case_type_col_by_id: dict[UUID, model.CaseTypeCol] = {
            x.id: x for x in case_type_cols if x.id is not None
        }
        col_by_id: dict[UUID, model.Col] = {x.id: x for x in cols if x.id is not None}

        if not case_abac.is_full_access:
            writable_data_collections_by_case_type_col: dict[UUID, set[UUID]] = {
                x: case_abac.get_data_collections_with_access_right_for_case_type_col(
                    x, enum.CaseRight.WRITE_CASE
                )
                for x in case_type_col_ids
            }
            # Retrieve data collections by case id for ABAC column-level write checks
            case_to_data_collections: dict[UUID, set[UUID]] = (
                self._retrieve_case_data_collections_map(uow, user.id)
            )
            # For each requested (case, case_type_col), ensure the user has write access
            # to that column in at least one data collection the case belongs to
            for case_seq in cmd.case_seqs:
                # Membership includes created_in_data_collection_id
                case_data_collection_memberships = set(
                    case_to_data_collections.get(case_seq.case_id, set())
                )
                case_data_collection_memberships.add(
                    case_by_id[case_seq.case_id].created_in_data_collection_id
                )
                writable_in_data_collections = (
                    writable_data_collections_by_case_type_col.get(
                        case_seq.case_type_col_id, set()
                    )
                )
                if case_data_collection_memberships.isdisjoint(
                    writable_in_data_collections
                ):
                    raise exc.UnauthorizedAuthError(
                        "User has no WRITE_CASE access to the specified column in any data collection of the case"
                    )

        created_seqs: list[model.Seq] = []
        for case_seq in cmd.case_seqs:
            case = case_by_id[case_seq.case_id]
            case_type_col = case_type_col_by_id[case_seq.case_type_col_id]
            if case_type_col.case_type_id != case.case_type_id:
                raise exc.InvalidArgumentsError(
                    f"Column {case_seq.case_type_col_id} not part of case type {case.case_type_id}"
                )
            col = col_by_id[case_type_col.col_id]
            if col.col_type != enum.ColType.GENETIC_SEQUENCE:
                raise exc.InvalidArgumentsError(
                    f"Column {col.id} is not of type {enum.ColType.GENETIC_SEQUENCE.value}"
                )

            # naieve create and update directly to seqdb in CREATE_ONE
            created_seq: model.Seq = self.app.handle(
                seqdb_command.SeqCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.CREATE_ONE,
                    objs=case_seq.seq,
                )
            )
            case.content[case_seq.case_type_col_id] = created_seq.id  # type:ignore

            super(DomainBaseCaseService, self).crud(
                command.CaseCrudCommand(
                    user=cmd.user, operation=CrudOperation.UPDATE_ONE, objs=case
                )
            )

            created_seqs.append(created_seq)

    return created_seqs


def case_service_create_file_for_read_set(
    self: BaseCaseService, cmd: command.CreateFileForReadSetCommand
) -> UUID | None:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    # Retrieve case, case type col and col, and perform validations
    with repository.uow() as uow:
        # Check case exists
        case: model.Case = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id if user else None,
            model.Case,
            None,
            cmd.case_id,
            CrudOperation.READ_ONE,
        )

        # Case and column-level ABAC check
        self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.WRITE_CASE,
            case_ids=[cmd.case_id],
            filter_content=True,
            extra_access_case_type_col_ids={cmd.case_type_col_id},
        )

        if not case_abac.is_full_access:
            self.validate_case_access_rights_with_case_type_col(
                cmd, user, case_abac, uow, case
            )

        # Retrieve case type column and underlying column
        case_type_col: model.CaseTypeCol = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id if user else None,
            model.CaseTypeCol,
            None,
            cmd.case_type_col_id,
            CrudOperation.READ_ONE,
        )

        # Verify the column belongs to the case type of the case
        if case_type_col.case_type_id != case.case_type_id:
            raise exc.InvalidArgumentsError(
                f"Column {cmd.case_type_col_id} not part of case type {case.case_type_id}"
            )

        col: model.Col = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            case_type_col.col_id,
            CrudOperation.READ_ONE,
        )
        if col.col_type != enum.ColType.GENETIC_READS:
            raise exc.InvalidArgumentsError(
                f"Column {col.id} is not of type GENETIC_READS"
            )

        # Retrieve ReadSet id from case content
        if cmd.case_type_col_id not in case.content:
            raise exc.InvalidArgumentsError(
                "No ReadSet linked to case for the given case type column"
            )
        read_set_val = case.content[cmd.case_type_col_id]
        read_set_id: UUID = (
            read_set_val if isinstance(read_set_val, UUID) else UUID(str(read_set_val))
        )

    # file_hash = hashlib.sha256(cmd.file_content).digest()
    file_to_create = model.File(
        # TODO: remove size_bytes and hash_sha256? Was in original idea?
        # size_bytes=len(cmd.file_content),
        # hash_sha256=file_hash,
        content=cmd.file_content,
    )
    created_file: model.File = self.app.handle(
        seqdb_command.FileCrudCommand(
            user=cmd.user,
            operation=CrudOperation.CREATE_ONE,
            objs=file_to_create,
        )
    )

    # Read current ReadSet to avoid overwriting unrelated fields
    existing_read_set: model.ReadSet = self.app.handle(
        seqdb_command.ReadSetCrudCommand(
            user=cmd.user,
            operation=CrudOperation.READ_ONE,
            obj_ids=read_set_id,
        )
    )

    if cmd.is_fwd:
        if existing_read_set.fwd_file_id is not None:
            raise exc.InvalidArgumentsError("Forward file already linked to ReadSet")
        existing_read_set.fwd_file_id = created_file.id
    else:
        if existing_read_set.rev_file_id is not None:
            raise exc.InvalidArgumentsError("Reverse file already linked to ReadSet")
        existing_read_set.rev_file_id = created_file.id

    # Update ReadSet with the new file link
    self.app.handle(
        seqdb_command.ReadSetCrudCommand(
            user=cmd.user,
            operation=CrudOperation.UPDATE_ONE,
            objs=existing_read_set,
        )
    )

    return created_file.id


def case_service_create_file_for_seq(
    self: BaseCaseService, cmd: command.CreateFileForSeqCommand
) -> UUID | None:
    user, repository = self._get_user_and_repository(cmd)
    assert isinstance(user, model.User) and user.id is not None

    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None
    # Retrieve case, case type col and col, and perform validations
    with repository.uow() as uow:
        # Check case exists
        case: model.Case = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id if user else None,
            model.Case,
            None,
            cmd.case_id,
            CrudOperation.READ_ONE,
        )

        # Case and column-level ABAC check
        self._retrieve_cases_with_content_right(
            uow,
            user.id,
            case_abac,
            enum.CaseRight.WRITE_CASE,
            case_ids=[cmd.case_id],
            filter_content=True,
            extra_access_case_type_col_ids={cmd.case_type_col_id},
        )

        if not case_abac.is_full_access:
            self.validate_case_access_rights_with_case_type_col(
                cmd, user, case_abac, uow, case
            )

        # Retrieve case type column and underlying column
        case_type_col: model.CaseTypeCol = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id if user else None,
            model.CaseTypeCol,
            None,
            cmd.case_type_col_id,
            CrudOperation.READ_ONE,
        )

        # Verify the column belongs to the case type of the case
        if case_type_col.case_type_id != case.case_type_id:
            raise exc.InvalidArgumentsError(
                f"Column {cmd.case_type_col_id} not part of case type {case.case_type_id}"
            )

        col: model.Col = self.repository.crud(  # type: ignore[assignment]
            uow,
            user.id,
            model.Col,
            None,
            case_type_col.col_id,
            CrudOperation.READ_ONE,
        )
        if col.col_type != enum.ColType.GENETIC_SEQUENCE:
            raise exc.InvalidArgumentsError(
                f"Column {col.id} is not of type GENETIC_SEQUENCE"
            )

        # Retrieve Seq id from case content
        if cmd.case_type_col_id not in case.content:
            raise exc.InvalidArgumentsError(
                "No Seq linked to case for the given case type column"
            )
        seq_val = case.content[cmd.case_type_col_id]
        seq_id: UUID = seq_val if isinstance(seq_val, UUID) else UUID(str(seq_val))

    # file_hash = hashlib.sha256(cmd.file_content).digest()
    file_to_create = model.File(
        # size_bytes=len(cmd.file_content),
        # hash_sha256=file_hash,
        content=cmd.file_content,
    )
    created_file: model.File = self.app.handle(
        seqdb_command.FileCrudCommand(
            user=cmd.user,
            operation=CrudOperation.CREATE_ONE,
            objs=file_to_create,
        )
    )

    # Read current Seq to avoid overwriting unrelated fields
    existing_seq: model.Seq = self.app.handle(
        seqdb_command.SeqCrudCommand(
            user=cmd.user,
            operation=CrudOperation.READ_ONE,
            obj_ids=seq_id,
        )
    )

    if existing_seq.file_id is not None:
        raise exc.InvalidArgumentsError("File already linked to Seq")
    existing_seq.file_id = created_file.id

    # Update Seq with the new file link
    self.app.handle(
        seqdb_command.SeqCrudCommand(
            user=cmd.user,
            operation=CrudOperation.UPDATE_ONE,
            objs=existing_seq,
        )
    )

    return created_file.id
