from typing import Any

from sqlalchemy import Engine

from gen_epix.casedb.domain.repository import BaseSubjectRepository
from gen_epix.casedb.repositories.sa_model import (
    DB_METADATA_FIELDS,
    GENERATE_SERVICE_METADATA,
    SERVICE_METADATA_FIELDS,
)
from gen_epix.fastapp.repositories import SARepository


class SubjectSARepository(SARepository, BaseSubjectRepository):
    def __init__(self, engine: Engine, **kwargs: Any):
        entities = kwargs.pop("entities", BaseSubjectRepository.ENTITIES)
        super().__init__(
            engine,
            entities=entities,
            service_metadata_fields=SERVICE_METADATA_FIELDS,
            db_metadata_fields=DB_METADATA_FIELDS,
            generate_service_metadata=GENERATE_SERVICE_METADATA,
            **kwargs,
        )
