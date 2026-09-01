"""Define seqdb domain models for domain.model.seq.pheno."""

from typing import ClassVar, Self

from pydantic import model_validator

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
    """Store a PCR measurement produced from a sample by a protocol.

    Model validation: Content-hash validation is not implemented yet, so the
    model currently accepts content unchanged after its inherited validation.
    """

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

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Reserve post-validation for future content-hash verification."""
        # TODO: implement content hash validation
        return self


class AstMeasurement(
    Model,
    HasSampleMixin,
    HasProtocolMixin,
    ContentMixin[enum.PcrResultFormat],
    QualityMixin,
):
    """Store an antimicrobial-susceptibility measurement from a sample.

    Model validation: Content-hash validation is not implemented yet, so the
    model currently accepts content unchanged after its inherited validation.
    """

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

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Reserve post-validation for future content-hash verification."""
        # TODO: implement content hash validation
        return self
