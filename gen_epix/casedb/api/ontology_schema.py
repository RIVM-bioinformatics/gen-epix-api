"""Request and response models of the casedb ontology API.

These models are kept apart from the routes that use them, so that a remote
client can import them without importing the web framework.
"""

from pydantic import BaseModel as PydanticBaseModel

from gen_epix.casedb.domain import command, model
from gen_epix.commondb.domain.literal import MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH
from gen_epix.util import copy_model_field


class DiseaseEtiologicalAgentUpdateAssociationRequestBody(PydanticBaseModel):
    """Represents etiological agents associated with a disease."""

    etiologies: list[model.Etiology] = copy_model_field(
        command.DiseaseEtiologicalAgentUpdateAssociationCommand,
        "association_objs",
        max_length=MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH,
    )
