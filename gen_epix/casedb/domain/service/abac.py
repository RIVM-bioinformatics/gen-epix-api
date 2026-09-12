"""Define the Casedb ABAC service contract and command classifications."""

import abc

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.commondb.domain.command import Command
from gen_epix.commondb.services import AbacService as CommonAbacService


class BaseAbacService(CommonAbacService):
    """Encapsulates Casedb access resolution and command scope metadata.

    The command sets extend shared Commondb ABAC classifications with Casedb
    policy and case operations. Concrete services resolve case and reference
    data access for policies in the command lifecycle.
    """

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
        command.RetrieveIsOwnCasesCommand,
        command.RetrieveCaseRightsCommand,
        command.RetrieveCaseSetRightsCommand,
        command.RetrieveCaseSetStatsCommand,
        command.RetrieveCaseTypeStatsCommand,
        command.CaseTypeCrudCommand,
        command.CaseTypeSetMemberCrudCommand,
        command.CaseTypeSetCrudCommand,
        command.ColCrudCommand,
        command.ColSetCrudCommand,
        command.ColSetMemberCrudCommand,
        command.CaseCrudCommand,
        command.CaseIdentifierCrudCommand,
        command.CreateFileForReadSetCommand,
        command.CreateFileForSeqCommand,
        # command.CaseDataCollectionUpdateAssociationCommand,
        command.CreateCaseSetCommand,
        command.UploadCasesCommand,
        command.CaseSetCrudCommand,
        # command.CaseSetCaseUpdateAssociationCommand,
        # command.CaseSetDataCollectionUpdateAssociationCommand,
        command.CaseDataCollectionLinkCrudCommand,
        command.CaseSetDataCollectionLinkCrudCommand,
        command.DataCollectionCrudCommand,
        command.RefColCrudCommand,
        command.RefDimCrudCommand,
        command.RetrievePhylogeneticTreeByCasesCommand,
        command.RetrieveSimilarCasesCommand,
        command.RetrieveGeneticSequenceFastaByCaseCommand,
        command.DimCrudCommand,
    }

    @abc.abstractmethod
    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        """Resolve case access control for a command.

        Args:
            cmd: Command whose user and operation determine access.

        Returns:
            Effective case access for the command.

        Raises:
            NotImplementedError: Always, until a concrete ABAC service
                implements the resolution.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_ref_data_access(self, cmd: command.Command) -> model.RefDataAccess:
        """Resolve reference-data access control for a command.

        Args:
            cmd: Command whose user determines reference-data access.

        Returns:
            Effective reference-data access for the command.

        Raises:
            NotImplementedError: Always, until a concrete ABAC service
                implements the resolution.
        """
        raise NotImplementedError()
