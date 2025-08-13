from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.domain.repository import BaseSubjectRepository
from gen_epix.fastapp import BaseService


class BaseSubjectService(BaseService):
    SERVICE_TYPE = ServiceType.SUBJECT

    # Property overridden to provide narrower return value to support linter
    @property  # type: ignore
    def repository(self) -> BaseSubjectRepository:  # type: ignore
        return super().repository  # type: ignore

    def register_handlers(self) -> None:
        self.register_default_crud_handlers()
