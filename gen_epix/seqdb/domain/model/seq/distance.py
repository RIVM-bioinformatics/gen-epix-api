import json
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ContentMixin
from gen_epix.seqdb.domain.model.seq.profile import NULL_ID, SeqProfile
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
    content_hash: UUID = Field(
        default=NULL_ID,
        description="The content hash is not used for this model, but is required by the ContentMixin. It is set to a default value and not validated against the content.",
    )

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """
        Validate that the content representation is valid.
        """
        self.content_hash = NULL_ID
        self.get_profile_distance_map()  # This will raise an error if the content is not a valid profile distance map
        return self

    def get_profile_distance_map(self) -> dict[UUID, float]:
        """
        Get the profile distance map from the content.
        """
        if self.format != enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP:
            raise ValueError(f"Unsupported format: {self.format}")
        content_dict = json.loads(self.content)
        return {UUID(x): y for x, y in content_dict.items()}


class SeqDistancePair(Model, HasProtocolMixin):
    """One row per ordered pair (profile_a → profile_b) in seq_distance_pair.

    Both directions are stored explicitly, so retrieval only needs a single
    WHERE profile_id_a IN (...) query without a UNION. The seq_distance_pair
    table coexists with seq_distance while both paths are benchmarked; existing
    SeqDistance records are not modified when use_row_per_pair is active.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distance_pairs",
        table_name="seq_distance_pair",
        persistable=True,
        keys=create_keys({1: ("protocol_id", "profile_id_a", "profile_id_b")}),
        links=create_links(
            {
                1: ("protocol_id", Protocol, "protocol"),
                2: ("profile_id_a", SeqProfile, "profile_a"),
                3: ("profile_id_b", SeqProfile, "profile_b"),
            }
        ),
    )

    profile_id_a: UUID = Field(description="Source profile of the directed pair.")
    profile_a: SeqProfile | None = Field(default=None)

    profile_id_b: UUID = Field(description="Target profile of the directed pair.")
    profile_b: SeqProfile | None = Field(default=None)

    distance: float = Field(description="Hamming distance between the two profiles.")
