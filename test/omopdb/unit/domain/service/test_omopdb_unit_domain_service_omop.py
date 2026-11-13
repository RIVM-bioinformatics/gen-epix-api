from types import SimpleNamespace
from uuid import UUID

import pytest

from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.domain.service.omop import BaseOmopService


def test_register_handlers_registers_omop_commands() -> None:
    registrations = {}
    default_crud_registrations = []
    app = SimpleNamespace(
        register_handler=lambda command_type, handler: registrations.update(
            {command_type: handler}
        )
    )
    handlers = {
        command.UploadPersonsCommand: object(),
        command.RetrievePersonsByIdCommand: object(),
        command.RetrievePersonsByQueryCommand: object(),
        command.RetrieveSpecimenIdsByCohortIdsCommand: object(),
    }
    service = SimpleNamespace(
        app=app,
        register_default_crud_handlers=lambda: default_crud_registrations.append(True),
        upload_persons=handlers[command.UploadPersonsCommand],
        retrieve_persons_by_id=handlers[command.RetrievePersonsByIdCommand],
        retrieve_persons_by_query=handlers[command.RetrievePersonsByQueryCommand],
        retrieve_specimen_ids_by_cohort_ids=handlers[
            command.RetrieveSpecimenIdsByCohortIdsCommand
        ],
    )

    BaseOmopService.register_handlers(service)

    assert default_crud_registrations == [True]
    assert registrations == handlers


@pytest.mark.parametrize("cohort_count", [0, 2], ids=["empty", "multiple"])
def test_retrieve_specimen_ids_by_cohort_ids_forwards_query_and_wraps_result(
    cohort_count: int,
) -> None:
    cohort_definition_id = UUID(int=100)
    cohort_ids = [UUID(int=index) for index in range(1, cohort_count + 1)]
    specimen_ids_by_cohort_id = {
        cohort_id: [UUID(int=index + 1000)]
        for index, cohort_id in enumerate(cohort_ids, start=1)
    }

    class Repository:
        def __init__(self) -> None:
            self.received_arguments = None

        def get_specimen_ids_by_cohort_ids(self, *, cohort_definition_id, cohort_ids):
            self.received_arguments = (cohort_definition_id, cohort_ids)
            return specimen_ids_by_cohort_id

    repository = Repository()
    service = SimpleNamespace(repository=repository)
    cmd = command.RetrieveSpecimenIdsByCohortIdsCommand(
        cohort_definition_id=cohort_definition_id,
        cohort_ids=cohort_ids,
    )

    result = BaseOmopService.retrieve_specimen_ids_by_cohort_ids(service, cmd)

    assert repository.received_arguments == (cohort_definition_id, cohort_ids)
    assert result == model.SpecimenIdsByCohortResult(
        specimen_ids_by_cohort_id=specimen_ids_by_cohort_id
    )
