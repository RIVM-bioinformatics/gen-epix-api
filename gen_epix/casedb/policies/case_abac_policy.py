from typing import Type

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.fastapp import Command


class CaseAbacPolicy(BaseCaseAbacPolicy):
    def get_content(self, cmd: Command) -> model.CaseAbac:
        return self.abac_service.get_case_abac(cmd)

    def get_content_return_type(self, cmd: Command) -> Type[model.Model]:
        return model.CaseAbac
