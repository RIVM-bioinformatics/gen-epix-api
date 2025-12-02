from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, model_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ProtocolMixin
from gen_epix.seqdb.domain.model.seq.locus import LocusSet
from gen_epix.seqdb.domain.model.seq.profile import (
    AlleleProfile,
    KmerProfile,
    SnpProfile,
)
from gen_epix.seqdb.domain.model.seq.seq import RefSeq, Seq


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
    max_stored_distance: float = Field(description="The maximum distance to be stored")
    min_scale_unit: float = Field(description="The minimum unit to be shown in a scale")
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

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if (
            self.seq_distance_protocol_type
            in enum.SeqDistanceProtocolTypeSet.ALLELE_BASED.value
            and self.locus_set_id is None
        ):
            raise ValueError("locus_set_id must be provided for allele based type")
        elif (
            self.seq_distance_protocol_type
            in enum.SeqDistanceProtocolTypeSet.SNP_BASED.value
            and self.ref_seq_id is None
        ):
            raise ValueError("ref_seq_id must be provided for snp based type")
        return self

    @field_serializer("seq_distance_protocol_type", mode="plain")
    def _serialize_seq_format(self, value: str | enum.SeqDistanceProtocolType) -> str:
        if isinstance(value, enum.SeqDistanceProtocolType):
            return value.value
        return value


class SeqDistance(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_distances",
        table_name="seq_distance",
        persistable=True,
        keys=create_keys(
            {
                1: (
                    "seq_id",
                    "seq_distance_protocol_id",
                    "allele_profile_id",
                    "snp_profile_id",
                    "kmer_profile_id",
                )
            }
        ),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "seq_distance_protocol_id",
                    SeqDistanceProtocol,
                    "seq_distance_protocol",
                ),
                3: ("allele_profile_id", AlleleProfile, "allele_profile"),
                4: ("snp_profile_id", SnpProfile, "snp_profile"),
                5: ("kmer_profile_id", KmerProfile, "kmer_profile"),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    seq_distance_protocol_id: UUID = Field(
        description="The unique identifier for the genetic distance protocol. FOREIGN KEY"
    )
    seq_distance_protocol: SeqDistanceProtocol | None = Field(
        default=None, description="The genetic distance protocol."
    )
    allele_profile_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the allele profile, if applicable. FOREIGN KEY",
    )
    allele_profile: AlleleProfile | None = Field(
        default=None, description="The allele profile."
    )
    snp_profile_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the SNP profile, if applicable. FOREIGN KEY",
    )
    snp_profile: SnpProfile | None = Field(default=None, description="The SNP profile.")
    kmer_profile_id: UUID | None = Field(
        default=None,
        description="The unique identifier for the k-mer profile, if applicable. FOREIGN KEY",
    )
    kmer_profile: SnpProfile | None = Field(
        default=None, description="The k-mer profile."
    )
    distance_format: enum.SeqDistanceFormat = Field(
        default=enum.SeqDistanceFormat.SEQ_ID_DISTANCE_DICT,
        description="The representation format of the distances.",
    )
    distances: str = Field(description="The distances to other sequences.")

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        ids = [self.allele_profile_id, self.snp_profile_id, self.kmer_profile_id]
        has_ids = [x is not None for x in ids]
        if not any(has_ids):
            raise ValueError(
                "Either allele_profile_id, snp_profile_id or kmer_profile_id must be provided"
            )
        elif sum(has_ids) > 1:
            raise ValueError(
                "Only one of allele_profile_id, snp_profile_id or kmer_profile_id must be provided"
            )
        objs = [self.allele_profile, self.snp_profile, self.kmer_profile]
        for has_id, obj in zip(has_ids, objs):
            if not has_id and obj is not None:
                raise ValueError(f"{obj.__class__.__name__} must be None")
        return self

    @field_serializer("distance_format", mode="plain")
    def _serialize_distance_format(self, value: str | enum.SeqDistanceFormat) -> str:
        if isinstance(value, enum.SeqDistanceFormat):
            return value.value
        return value
