import json
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


class SeqDistanceProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distance_protocols",
        table_name="seq_distance_protocol",
        persistable=True,
        keys=create_keys(
            {
                1: "code",
                2: ("name", "version"),
            }
        ),
        links=create_links(
            {
                1: ("locus_set_id", LocusSet, "locus_set"),
                2: ("ref_seq_id", RefSeq, "ref_seq"),
            }
        ),
    )
    seq_distance_protocol_type: enum.SeqDistanceProtocolType = Field(
        description="The type of genetic distance protocol.",
    )
    locus_set_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the locus set, if applicable. FOREIGN KEY",
    )
    locus_set: LocusSet | None = Field(default=None, description="The locus set.")
    ref_seq_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the reference sequence, if applicable. FOREIGN KEY",
    )
    ref_seq: RefSeq | None = Field(default=None, description="The reference sequence.")
    is_integer_distance: bool = Field(
        description="Whether the distances calculated by this protocol are integers"
    )
    max_stored_distance: float = Field(
        description="The maximum distance that is guaranteedto be stored"
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if (
            self.seq_distance_protocol_type
            in enum.SeqDistanceProtocolTypeSet.LOCUS_SET_BASED.value
        ):
            if self.locus_set_id is None:
                raise ValueError(
                    f"locus_set_id must be provided for seq_distance_protocol_type {self.seq_distance_protocol_type}"
                )
        else:
            if self.locus_set_id is not None:
                raise ValueError(
                    f"locus_set_id must be None for seq_distance_protocol_type {self.seq_distance_protocol_type}"
                )
        if (
            self.seq_distance_protocol_type
            in enum.SeqDistanceProtocolTypeSet.REF_SEQ_BASED.value
        ):
            if self.ref_seq_id is None:
                raise ValueError(
                    f"ref_seq_id must be provided for seq_distance_protocol_type {self.seq_distance_protocol_type}"
                )
        else:
            if self.ref_seq_id is not None:
                raise ValueError(
                    f"ref_seq_id must be None for seq_distance_protocol_type {self.seq_distance_protocol_type}"
                )
        return self

    @field_serializer("seq_distance_protocol_type", mode="plain")
    def _serialize_seq_format(self, value: str | enum.SeqDistanceProtocolType) -> str:
        if isinstance(value, enum.SeqDistanceProtocolType):
            return value.value
        return value


class SeqDistance(Model, HasSampleMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distances",
        table_name="seq_distance",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_distance_protocol_id",
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
                    "seq_distance_protocol_id",
                    SeqDistanceProtocol,
                    "seq_distance_protocol",
                ),
            }
        ),
    )
    seq_distance_protocol_id: UUID = Field(
        description="The unique identifier for the genetic distance protocol. FOREIGN KEY"
    )
    seq_distance_protocol: SeqDistanceProtocol | None = Field(
        default=None, description="The genetic distance protocol."
    )
    profile_id: UUID = Field(
        description="The unique identifier for the profile.",
    )
    distance_format: enum.SeqDistanceFormat = Field(
        default=enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT,
        description="The representation format of the distances.",
    )
    distances: str = Field(description="The distances to other sequences.")
