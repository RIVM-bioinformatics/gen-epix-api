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
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


def case_service_create_read_sets_or_seqs_for_cases(
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
        read_sets = [x.read_set for x in cmd.case_read_sets]  # type:ignore
        case_ids = [x.case_id for x in cmd.case_read_sets]
        case_type_col_ids = [x.case_type_col_id for x in cmd.case_read_sets]
    elif isinstance(cmd, command.CreateSeqsForCasesCommand):
        is_read_set = False
        seqs = [x.seq for x in cmd.case_seqs]  # type:ignore
        case_ids = [x.case_id for x in cmd.case_seqs]
        case_type_col_ids = [x.case_type_col_id for x in cmd.case_seqs]
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
                objs=read_sets,  # type:ignore[arg-type]
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


def case_service_create_file_for_read_set_or_seq(
    self: BaseCaseService,
    cmd: command.CreateFileForReadSetCommand | command.CreateFileForSeqCommand,
) -> UUID:
    user, repository = self._get_user_and_repository(cmd)
    user_id: UUID = user.id  # type: ignore[assignment]

    if isinstance(cmd, command.CreateFileForReadSetCommand):
        is_read_set = True
    elif isinstance(cmd, command.CreateFileForSeqCommand):
        is_read_set = False
    else:
        raise exc.InvalidArgumentsError("Invalid command type")

    # Retrieve case ABAC
    case_abac = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)
    assert case_abac is not None

    # Handle transaction for reading case
    with repository.uow() as uow:
        cases = _get_cases_for_create_read_sets_or_seqs(
            self, cmd, case_abac, uow, user_id, [cmd.case_id], [cmd.case_type_col_id]
        )
        case = cases[0]

        # Retrieve ReadSet or Seq ID from case content
        if cmd.case_type_col_id not in case.content:
            raise exc.InvalidArgumentsError(
                "No ReadSet linked to case for the given case type column"
            )
        read_set_or_seq_id = UUID(case.content[cmd.case_type_col_id])

    # Retrieve ReadSet or Seq, and verify no file linked yet
    if is_read_set:
        assert isinstance(cmd, command.CreateFileForReadSetCommand)
        read_set = self.app.handle(
            seqdb_command.ReadSetCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ONE,
                obj_ids=read_set_or_seq_id,
            )
        )
        if cmd.is_fwd and read_set.fwd_file_id is not None:
            raise exc.InvalidArgumentsError(
                "The ReadSet already has a forward file linked"
            )
        if not cmd.is_fwd and read_set.rev_file_id is not None:
            raise exc.InvalidArgumentsError(
                "The ReadSet already has a reverse file linked"
            )
    else:
        assert isinstance(cmd, command.CreateFileForSeqCommand)
        seq = self.app.handle(
            seqdb_command.SeqCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ONE,
                obj_ids=read_set_or_seq_id,
            )
        )
        if seq.file_id is not None:
            raise exc.InvalidArgumentsError("The Seq already has a file linked")

    # Create File and update ReadSet or Seq with the new file link
    created_file: model.File = self.app.handle(
        seqdb_command.FileCrudCommand(
            user=cmd.user,
            operation=CrudOperation.CREATE_ONE,
            objs=model.File(content=cmd.file_content),
        )
    )
    if is_read_set:
        assert isinstance(cmd, command.CreateFileForReadSetCommand)
        if cmd.is_fwd:
            read_set.fwd_file_id = created_file.id  # type: ignore
        else:
            read_set.rev_file_id = created_file.id  # type: ignore
        self.app.handle(
            seqdb_command.ReadSetCrudCommand(
                user=cmd.user,
                operation=CrudOperation.UPDATE_ONE,
                objs=read_set,
            )
        )
    else:
        seq.file_id = created_file.id  # type: ignore
        self.app.handle(
            seqdb_command.SeqCrudCommand(
                user=cmd.user,
                operation=CrudOperation.UPDATE_ONE,
                objs=seq,  # type: ignore[arg-type]
            )
        )

    assert created_file.id is not None
    return created_file.id


def _get_cases_for_create_read_sets_or_seqs(
    self: BaseCaseService,
    cmd: (
        command.CreateReadSetsForCasesCommand
        | command.CreateSeqsForCasesCommand
        | command.CreateFileForReadSetCommand
        | command.CreateFileForSeqCommand
    ),
    case_abac: model.CaseAbac,
    uow: BaseUnitOfWork,
    user_id: UUID,
    case_ids: list[UUID],
    case_type_col_ids: list[UUID],
) -> list[model.Case]:
    # Get CaseTypeCol and col data
    case_type_cols: list[model.CaseTypeCol] = (
        self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            model.CaseTypeCol,
            None,
            list(set(case_type_col_ids)),
            CrudOperation.READ_SOME,
        )
    )
    case_type_col_by_id: dict[UUID, model.CaseTypeCol] = {
        x.id: x for x in case_type_cols if x.id is not None
    }

    # Get Col data
    col_ids: set[UUID] = {case_type_col.col_id for case_type_col in case_type_cols}
    cols: list[model.Col] = self.repository.crud(  # type: ignore[assignment]
        uow,
        user_id,
        model.Col,
        None,
        list(col_ids),
        CrudOperation.READ_SOME,
    )
    col_by_id: dict[UUID, model.Col] = {x.id: x for x in cols if x.id is not None}

    # TODO: Verify all case type cols are for the given case type

    # Verify all case type cols are of type GENETIC_READS
    if isinstance(
        cmd,
        (command.CreateReadSetsForCasesCommand, command.CreateFileForReadSetCommand),
    ):
        expected_col_type = enum.ColType.GENETIC_READS
    elif isinstance(
        cmd, (command.CreateSeqsForCasesCommand, command.CreateFileForSeqCommand)
    ):
        expected_col_type = enum.ColType.GENETIC_SEQUENCE
    else:
        raise exc.InvalidArgumentsError("Invalid command type")
    invalid_case_type_col_ids = [
        x.col_id
        for x in case_type_cols
        if col_by_id[x.col_id].col_type != expected_col_type
    ]
    if invalid_case_type_col_ids:
        invalid_case_type_col_ids_str = ", ".join(
            str(x) for x in invalid_case_type_col_ids
        )
        raise exc.InvalidArgumentsError(
            f"Some columns are not of type GENETIC_READS: {invalid_case_type_col_ids_str}"
        )

    # Get Case data
    cases: list[model.Case] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user_id,
        model.Case,
        None,
        list(case_ids),
        CrudOperation.READ_SOME,
    )

    # Verify if all case type cols are for the same case type as the cases
    # TODO: remove once the command is adjusted to be for only one case type
    invalid_case_type_col_ids = [
        y
        for x, y in zip(cases, case_type_col_ids)
        if case_type_col_by_id[y].case_type_id != x.case_type_id
    ]
    if invalid_case_type_col_ids:
        invalid_case_type_col_ids_str = ", ".join(
            str(x) for x in invalid_case_type_col_ids
        )
        raise exc.InvalidArgumentsError(
            f"Some case type column ids are for a different case type than the given cases: {invalid_case_type_col_ids_str}"
        )

    # @ABAC: Verify write rights to case_type_col for each case
    if not case_abac.is_full_access:
        # Get some write rights to case_type_col
        writable_data_collections_by_case_type_col: dict[UUID, set[UUID]] = {
            x: case_abac.get_data_collections_with_access_right_for_case_type_col(
                x, enum.CaseRight.WRITE_CASE
            )
            for x in case_type_col_ids
        }
        # Retrieve data collections by case id for ABAC column-level write checks
        case_data_collections_map: dict[UUID, set[UUID]] = (
            self._retrieve_case_data_collections_map(uow, user_id, case_ids=case_ids)
        )
        # For each requested (case, case_type_col), ensure the user has write access
        # to that column in at least one data collection the case belongs to
        for case, case_type_col_id in zip(cases, case_type_col_ids):
            # Membership includes created_in_data_collection_id
            assert case.id is not None
            case_data_collections = set(case_data_collections_map.get(case.id, set()))
            case_data_collections.add(case.created_in_data_collection_id)
            if case_data_collections.isdisjoint(
                writable_data_collections_by_case_type_col[case_type_col_id]
            ):
                raise exc.UnauthorizedAuthError(
                    "User has no WRITE_CASE access to the specified column in any data collection of the case"
                )
    return cases
