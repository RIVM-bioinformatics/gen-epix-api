from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.protocol import Protocol
from gen_epix.seqdb.domain.model.seq.sample import Sample


class PcrProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="pcr_protocols",
        table_name="pcr_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )
    target_names: list[str] = Field(
        description="The names of the targets for which PCR is performed"
    )

    @field_validator("target_names", mode="before")
    @classmethod
    def _validate_target_names(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return json.loads(value)
        return value


class AstProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_protocols",
        table_name="ast_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )
    is_predicted: bool = Field(
        description="Whether the AST results are predicted from sequence data"
    )
    antimicrobial_names: list[str] = Field(
        description="The names of the antimicrobials for which AST is performed"
    )

    @field_validator("antimicrobial_names", mode="before")
    @classmethod
    def _validate_antimicrobial_names(cls, value: list[str] | str) -> list[str]:
        if isinstance(value, str):
            return json.loads(value)
        return value


class PcrMeasurement(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="pcr_measurements",
        table_name="pcr_measurement",
        persistable=True,
        keys=create_keys({1: ("sample_id", "protocol_id", "index")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("protocol_id", Protocol, "protocol"),
            }
        ),
    )
    sample_id: UUID = Field(
        description="The unique identifier for the sample. FOREIGN KEY"
    )
    sample: Sample | None = Field(default=None, description="The sample.")
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    pcr_result: str = Field(description="The result of the PCR experiment.")
    pcr_result_format: enum.PcrResultFormat = Field(
        default=enum.PcrResultFormat.PCR_RESULT_FORMAT1,
        description="The representation format of the PCR result.",
    )
    index: int = Field(default=1, description="The index of the measurement.")


class AstMeasurement(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_measurements",
        table_name="ast_measurement",
        persistable=True,
        keys=create_keys({1: ("sample_id", "protocol_id", "index")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("protocol_id", Protocol, "protocol"),
            }
        ),
    )
    sample_id: UUID = Field(
        description="The unique identifier for the sample. FOREIGN KEY"
    )
    sample: Sample | None = Field(default=None, description="The sample.")
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    ast_result: str = Field(description="The result of the AST experiment.")
    ast_result_format: enum.AstResultFormat = Field(
        default=enum.AstResultFormat.AST_RESULT_FORMAT1,
        description="The representation format of the AST result.",
    )
    index: int = Field(default=1, description="The index of the measurement.")
