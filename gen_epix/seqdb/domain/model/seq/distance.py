from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ContentMixin
from gen_epix.seqdb.domain.model.seq.profile import SeqProfile
from gen_epix.seqdb.domain.model.seq.protocol import HasProtocolMixin, Protocol
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample


class SeqDistance(
    Model, HasSampleMixin, HasProtocolMixin, ContentMixin[enum.SeqDistanceFormat]
):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distances",
        table_name="seq_distance",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "protocol_id",
                    "seq_profile_id",
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
                3: (
                    "seq_profile_id",
                    SeqProfile,
                    "seq_profile",
                ),
            }
        ),
    )
    seq_profile_id: UUID = Field(
        description="The unique identifier for the sequence profile.",
    )
    seq_profile: SeqProfile | None = Field(
        default=None,
        description="The sequence profile.",
    )
