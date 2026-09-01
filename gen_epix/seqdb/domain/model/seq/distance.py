"""Define seqdb domain models for domain.model.seq.distance."""

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
    """Store profile-to-profile distances produced by a protocol.

    Model validation: The content must encode a JSON profile-distance map in
    ``PROFILE_DISTANCE_MAP`` format. Validation resets ``content_hash`` to its
    required sentinel because this model does not use content hashes.
    """

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
        """Validate the profile-distance-map content and reset its unused hash."""
        self.content_hash = NULL_ID
        self.get_profile_distance_map()  # This will raise an error if the content is not a valid profile distance map
        return self

    def get_profile_distance_map(self) -> dict[UUID, float]:
        """Decode the stored JSON profile-distance map.

        Returns:
            Distances keyed by sequence-profile identifier.

        Raises:
            ValueError: If the content uses an unsupported sequence-distance format.
            json.JSONDecodeError: If the content is not valid JSON.
            ValueError: If a JSON map key is not a valid UUID.
        """
        if self.format != enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP:
            raise ValueError(f"Unsupported format: {self.format}")
        content_dict = json.loads(self.content)
        return {UUID(x): y for x, y in content_dict.items()}
