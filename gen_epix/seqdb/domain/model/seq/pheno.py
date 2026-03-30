from typing import ClassVar


from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ContentMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.protocol import HasProtocolMixin, Protocol
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample


class PcrMeasurement(
    Model,
    HasSampleMixin,
    HasProtocolMixin,
    ContentMixin[enum.PcrResultFormat],
    QualityMixin,
):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="pcr_measurements",
        table_name="pcr_measurement",
        persistable=True,
        keys=create_keys({1: ("sample_id", "protocol_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("protocol_id", Protocol, "protocol"),
            }
        ),
    )


class AstMeasurement(
    Model,
    HasSampleMixin,
    HasProtocolMixin,
    ContentMixin[enum.PcrResultFormat],
    QualityMixin,
):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_measurements",
        table_name="ast_measurement",
        persistable=True,
        keys=create_keys({1: ("sample_id", "protocol_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("protocol_id", Protocol, "protocol"),
            }
        ),
    )
