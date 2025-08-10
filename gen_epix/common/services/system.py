from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.service import BaseSystemService
from gen_epix.common.policies.has_system_outage_policy import HasSystemOutagePolicy
from gen_epix.fastapp import CrudOperation, EventTiming


class SystemService(BaseSystemService):
    def register_policies(self) -> None:
        """
        Registers policies that checks if the system has a current outage

        """
        policy = HasSystemOutagePolicy(system_service=self)
        for command_class in self.app.domain.commands:
            self.app.register_policy(command_class, policy, EventTiming.BEFORE)

    def retrieve_outages(
        self, _cmd: command.RetrieveOutagesCommand
    ) -> list[model.Outage]:
        with self.repository.uow() as uow:
            outages = self.repository.crud(
                uow,
                None,
                model.Outage,
                None,
                None,
                CrudOperation.READ_ALL,
            )
        return outages
