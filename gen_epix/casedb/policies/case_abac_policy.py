"""Resolve case-specific ABAC content for casedb commands."""

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.fastapp import Command


class CaseAbacPolicy(BaseCaseAbacPolicy):
    """Apply command-scoped casedb case access resolution."""

    def get_content(self, cmd: Command) -> model.CaseAbac:
        """Resolve the case access model for a command.

        Args:
            cmd: Command for which case access is resolved.

        Returns:
            The case-specific ABAC model produced by the casedb ABAC service.
        """
        return self.abac_service.get_case_abac(cmd)

    def get_content_return_type(self, cmd: Command) -> type[model.Model]:
        """See base method."""
        return model.CaseAbac
