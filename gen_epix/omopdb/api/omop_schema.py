"""Request and response models of the omopdb OMOP API.

These models are kept apart from the routes that use them, so that a remote
client can import them without importing the web framework.
"""

from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel

from gen_epix.omopdb.domain import command
from gen_epix.util import copy_model_field


class RetrievePersonsByIdsRequestBody(PydanticBaseModel):
    """Represents unique person identifiers for a full-person retrieval request."""

    person_ids: list[UUID] = copy_model_field(
        command.RetrievePersonsByIdCommand, "person_ids"
    )


class RetrieveSpecimenIdsByCohortIdsRequestBody(PydanticBaseModel):
    """Represents cohort identifiers for a cohort-to-specimen retrieval request."""

    cohort_definition_id: UUID = copy_model_field(
        command.RetrieveSpecimenIdsByCohortIdsCommand, "cohort_definition_id"
    )
    cohort_ids: list[UUID] = copy_model_field(
        command.RetrieveSpecimenIdsByCohortIdsCommand, "cohort_ids"
    )
