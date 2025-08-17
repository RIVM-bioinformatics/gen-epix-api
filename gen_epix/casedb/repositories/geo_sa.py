from gen_epix.casedb.domain.repository import BaseGeoRepository
from gen_epix.fastapp.repositories import SARepository


class GeoSARepository(SARepository, BaseGeoRepository):
    pass
