from typing import Any

from gen_epix.casedb.domain import command, exc, model
from gen_epix.casedb.domain.service import BaseAbacService
from gen_epix.fastapp.model import Policy


class BaseCaseAbacPolicy(Policy):
    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        self.abac_service = abac_service
        self.props = kwargs

    @staticmethod
    def get_case_abac_from_command(
        cmd: command.Command,
    ) -> model.CaseAbac | None:
        case_abac: model.CaseAbac | None = None
        for policy in cmd._policies:
            if not issubclass(type(policy), BaseCaseAbacPolicy):
                continue
            if case_abac:
                raise exc.InitializationServiceError(
                    f"Multiple policies registered to retrieve CaseAbac"
                )
            case_abac = policy.get_content(cmd)

        return case_abac

    @staticmethod
    def get_ref_data_access_from_command(
        cmd: command.Command,
    ) -> model.RefDataAccess | None:
        ref_data_access: model.RefDataAccess | None = None
        for policy in cmd._policies:
            if not issubclass(type(policy), BaseCaseAbacPolicy):
                continue
            if ref_data_access is not None:
                raise exc.InitializationServiceError(
                    "Multiple policies registered to retrieve RefDataAccess"
                )
            assert isinstance(policy, BaseCaseAbacPolicy)
            ref_data_access = policy.get_ref_data_access(cmd)

        return ref_data_access

    def get_ref_data_access(self, cmd: command.Command) -> model.RefDataAccess:
        return self.abac_service.get_ref_data_access(cmd)
