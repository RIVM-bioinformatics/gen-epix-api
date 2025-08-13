import abc
import uuid
from typing import Type

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseAbacRepository
from gen_epix.fastapp import BaseService
from gen_epix.fastapp.model import Command


class BaseAbacService(BaseService):
    SERVICE_TYPE = ServiceType.ABAC

    ORGANIZATION_ADMIN_WRITE_COMMANDS: set[Type[Command]] = {
        command.ContactCrudCommand,
        command.SiteCrudCommand,
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    UPDATE_USER_COMMANDS: set[Type[Command]] = {
        command.InviteUserCommand,
        command.UpdateUserCommand,
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

    READ_ORGANIZATION_RESULTS_ONLY_COMMANDS: set[Type[Command]] = {
        command.UserCrudCommand,
        command.OrganizationAdminPolicyCrudCommand,
        command.OrganizationAccessCasePolicyCrudCommand,
        command.OrganizationShareCasePolicyCrudCommand,
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
        command.UserInvitationCrudCommand,
    }

    READ_SELF_RESULTS_ONLY_COMMANDS: set[Type[Command]] = {
        command.UserCrudCommand,
        command.UserAccessCasePolicyCrudCommand,
        command.UserShareCasePolicyCrudCommand,
    }

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseAbacRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(
            command.RetrieveOrganizationAdminNameEmailsCommand,
            self.retrieve_organization_admin_name_emails,
        )
        f(
            command.UpdateUserOwnOrganizationCommand,
            self.temp_update_user_own_organization,
        )

    @abc.abstractmethod
    def register_policies(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve_organization_admin_name_emails(
        self,
        cmd: command.RetrieveOrganizationAdminNameEmailsCommand,
    ) -> list[model.UserNameEmail]:
        raise NotImplementedError

    @abc.abstractmethod
    def temp_update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
    ) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_case_abac(self, cmd: command.Command) -> model.CaseAbac:
        raise NotImplementedError

    @abc.abstractmethod
    def get_organizations_under_admin(self, user: model.User) -> set[uuid.UUID]:
        raise NotImplementedError
