from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.fastapp.repositories import DictRepository


class GeoDictRepository(DictRepository, BaseGeoRepository):
    pass
