from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, model_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ProtocolMixin
from gen_epix.seqdb.domain.model.seq.locus import LocusSet
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample
from gen_epix.seqdb.domain.model.seq.seq import RefSeq
from gen_epix.seqdb.domain.model.seq.protocol import Protocol


class SeqDistance(Model, HasSampleMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distances",
        table_name="seq_distance",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "protocol_id",
                    "profile_id",
                )
            }
        ),
        links=create_links(
            {
                1: (
                    "sample_id",
                    Sample,
                    "sample",
                ),
                2: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(
        default=None, description="The genetic distance protocol."
    )
    profile_id: UUID = Field(
        description="The unique identifier for the profile.",
    )
    distance_format: enum.SeqDistanceFormat = Field(
        default=enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
        description="The representation format of the distances.",
    )
    distances: str = Field(description="The distances to other sequences.")

    @field_serializer("distance_format", mode="plain")
    def _serialize_seq_format(self, value: str | enum.SeqDistanceFormat) -> str:
        if isinstance(value, enum.SeqDistanceFormat):
            return value.value
        return value
