import abc

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.commondb.domain.command import Command
from gen_epix.commondb.services import AbacService as CommonAbacService


class BaseAbacService(CommonAbacService):
    SERVICE_TYPE = ServiceType.ABAC

    ORGANIZATION_ADMIN_WRITE_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.ORGANIZATION_ADMIN_WRITE_COMMANDS
    } | {
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    READ_ORGANIZATION_RESULTS_ONLY_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.READ_ORGANIZATION_RESULTS_ONLY_COMMANDS
    } | {
        command.OrganizationAccessCasePolicyCrudCommand,
        command.OrganizationShareCasePolicyCrudCommand,
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    READ_SELF_RESULTS_ONLY_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.READ_SELF_RESULTS_ONLY_COMMANDS
    } | {
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    READ_USER_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.READ_USER_COMMANDS
    } | set()

    UPDATE_USER_COMMANDS: set[type[Command]] = {  # type: ignore[assignment]
        command.COMMON_COMMAND_MAP.get(x, x)
        for x in CommonAbacService.UPDATE_USER_COMMANDS
    } | set()

    CASE_ABAC_COMMANDS: set[type[Command]] = {
        command.RetrieveCompleteCaseTypeCommand,
        command.RetrieveCasesByQueryCommand,
        command.RetrieveCasesByIdCommand,
        command.RetrieveCaseRightsCommand,
        command.RetrieveCaseSetRightsCommand,
        command.RetrieveCaseTypeStatsCommand,
        command.RetrieveCaseSetStatsCommand,
        command.CaseTypeCrudCommand,
        command.CaseTypeSetMemberCrudCommand,
        command.CaseTypeSetCrudCommand,
        command.CaseTypeColCrudCommand,
        command.CaseTypeColSetCrudCommand,
        command.CaseTypeColSetMemberCrudCommand,
        command.CaseCrudCommand,
        command.CreateReadSetsForCasesCommand,
        command.CreateFileForReadSetCommand,
        command.CreateFileForSeqCommand,
        command.CreateSeqsForCasesCommand,
        # command.CaseDataCollectionUpdateAssociationCommand,
        command.CreateCaseSetCommand,
        command.CreateCasesCommand,
        command.CaseSetCrudCommand,
        # command.CaseSetCaseUpdateAssociationCommand,
        # command.CaseSetDataCollectionUpdateAssociationCommand,
        command.CaseDataCollectionLinkCrudCommand,
        command.CaseSetDataCollectionLinkCrudCommand,
        command.DataCollectionCrudCommand,
        command.RetrievePhylogeneticTreeByCasesCommand,
        command.RetrieveGeneticSequenceByCaseCommand,
        command.RetrieveGeneticSequenceFastaByCaseCommand,
        command.ValidateCasesCommand,
    }

    @abc.abstractmethod
    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        raise NotImplementedError
