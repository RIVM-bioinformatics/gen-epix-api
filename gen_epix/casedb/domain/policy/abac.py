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
    def get_readable_reference_data_from_command(
        cmd: command.Command,
    ) -> model.ReadableReferenceData | None:
        readable_reference_data: model.ReadableReferenceData | None = None
        for policy in cmd._policies:
            if not issubclass(type(policy), BaseCaseAbacPolicy):
                continue
            if readable_reference_data:
                raise exc.InitializationServiceError(
                    "Multiple policies registered to retrieve ReadableReferenceData"
                )
            readable_reference_data = policy.get_readable_reference_data_content(cmd)
        return readable_reference_data

    def get_readable_reference_data_content(
        self, cmd: command.Command
    ) -> model.ReadableReferenceData:
        return self.abac_service.get_readable_reference_data(cmd)
