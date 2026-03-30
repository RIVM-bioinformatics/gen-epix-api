from test.test_client.enum import EnumTestType

from gen_epix.commondb.domain.enum import DevRepositoryConfig
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain import model

TEST_TYPE = EnumTestType.SEQDB_PERFORMANCE

SKIP_ENDPOINTS = False
SKIP_RAISE = False
SKIP_CREATE_DATA = False
VERBOSE = False
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_EMPTY


ENTITIES: list[Entity] = [
    model.LocusSet.ENTITY,
    model.Protocol.ENTITY,
    model.Sample.ENTITY,
    model.Seq.ENTITY,
    model.SeqProfile.ENTITY,
    model.SeqDistance.ENTITY,
]
