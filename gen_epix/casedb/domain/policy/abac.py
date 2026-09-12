"""Define policy helpers for attaching Casedb ABAC data to commands."""

from typing import Any

from gen_epix.casedb.domain import command, exc, model
from gen_epix.casedb.domain.service import BaseAbacService
from gen_epix.fastapp.model import Policy


class BaseCaseAbacPolicy(Policy):
    """Encapsulates command-scoped case and reference-data access resolution.

    Policy implementations use the configured ABAC service to compute access
    models. Static helpers recover those models from policies already attached
    to a command and reject ambiguous policy configurations.

    Attributes:
        abac_service: Service used to resolve access models.
        props: Policy-specific configuration supplied during initialization.
    """

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        """Initialize the policy with an ABAC service and policy properties.

        Args:
            abac_service: Service used to resolve command access.
            **kwargs: Policy-specific properties retained for implementations.
        """
        self.abac_service = abac_service
        self.props = kwargs

    @staticmethod
    def get_case_abac_from_command(
        cmd: command.Command,
    ) -> model.CaseAbac | None:
        """Return the case access model produced by a command policy.

        Args:
            cmd: Command whose attached policies are inspected.

        Returns:
            The case access model, or ``None`` when no case ABAC policy is
            attached.

        Raises:
            InitializationServiceError: If multiple case ABAC policies produce
                content for the command.
        """
        case_abac: model.CaseAbac | None = None
        for policy in cmd._policies:
            if not issubclass(type(policy), BaseCaseAbacPolicy):
                continue
            if case_abac:
                raise exc.InitializationServiceError(
                    "3a0dbaf4", f"Multiple policies registered to retrieve CaseAbac"
                )
            case_abac = policy.get_content(cmd)

        return case_abac

    @staticmethod
    def get_ref_data_access_from_command(
        cmd: command.Command,
    ) -> model.RefDataAccess | None:
        """Return the reference-data access model produced by a command policy.

        Args:
            cmd: Command whose attached policies are inspected.

        Returns:
            The reference-data access model, or ``None`` when no case ABAC
            policy is attached.

        Raises:
            InitializationServiceError: If multiple case ABAC policies are
                attached to the command.
        """
        ref_data_access: model.RefDataAccess | None = None
        for policy in cmd._policies:
            if not issubclass(type(policy), BaseCaseAbacPolicy):
                continue
            if ref_data_access is not None:
                raise exc.InitializationServiceError(
                    "b9d1fd22", "Multiple policies registered to retrieve RefDataAccess"
                )
            assert isinstance(policy, BaseCaseAbacPolicy)
            ref_data_access = policy.get_ref_data_access(cmd)

        return ref_data_access

    def get_ref_data_access(self, cmd: command.Command) -> model.RefDataAccess:
        """Resolve reference-data access for a command through the ABAC service.

        Args:
            cmd: Command for which access is resolved.

        Returns:
            The command user's reference-data access model.
        """
        return self.abac_service.get_ref_data_access(cmd)
