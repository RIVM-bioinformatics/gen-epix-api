import abc
from typing import Type

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.common.domain.command import Command
from gen_epix.common.domain.service import BaseAbacService as CommonBaseAbacService


class BaseAbacService(CommonBaseAbacService):
    SERVICE_TYPE = ServiceType.ABAC

    ORGANIZATION_ADMIN_WRITE_COMMANDS = {
        command.COMMON_COMMAND_IMPL.get(x, x)
        for x in CommonBaseAbacService.ORGANIZATION_ADMIN_WRITE_COMMANDS
    } | {
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    READ_ORGANIZATION_RESULTS_ONLY_COMMANDS = {
        command.COMMON_COMMAND_IMPL.get(x, x)
        for x in CommonBaseAbacService.READ_ORGANIZATION_RESULTS_ONLY_COMMANDS
    } | {
        command.OrganizationAccessCasePolicyCrudCommand,
        command.OrganizationShareCasePolicyCrudCommand,
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    READ_SELF_RESULTS_ONLY_COMMANDS = {
        command.COMMON_COMMAND_IMPL.get(x, x)
        for x in CommonBaseAbacService.READ_SELF_RESULTS_ONLY_COMMANDS
    } | {
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    CASE_ABAC_COMMANDS: set[Type[Command]] = {
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
        # command.CaseDataCollectionUpdateAssociationCommand,
        command.CaseSetCreateCommand,
        command.CasesCreateCommand,
        command.CaseSetCrudCommand,
        # command.CaseSetCaseUpdateAssociationCommand,
        # command.CaseSetDataCollectionUpdateAssociationCommand,
        command.CaseDataCollectionLinkCrudCommand,
        command.CaseSetDataCollectionLinkCrudCommand,
        command.DataCollectionCrudCommand,
        command.RetrievePhylogeneticTreeByCasesCommand,
        command.RetrieveGeneticSequenceByCaseCommand,
        command.RetrieveCaseSetStatsCommand,
        command.RetrieveCaseTypeStatsCommand,
    }

    def register_handlers(self) -> None:
        super().register_handlers()
        f = self.app.register_handler
        self.register_default_crud_handlers()

    @abc.abstractmethod
    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        raise NotImplementedError
