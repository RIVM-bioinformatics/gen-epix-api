import base64
import hashlib
import json
import struct
from typing import Any, ClassVar, Self
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model import Model, validate_int_enum_value
from gen_epix.commondb.domain.model.base import Model
from gen_epix.commondb.domain.model.organization import BaseIdentifier
from gen_epix.fastapp import Entity
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.literal import (
    MLVA_NO_LOCUS_REPEAT_NUMBER,
    REQUIRED_NEXTCLADE_KEYS,
    REQUIRED_NEXTCLADE_SEQ_KEYS,
)
from gen_epix.seqdb.domain.model.seq.base import ContentMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.protocol import HasProtocolMixin, Protocol
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample
from gen_epix.seqdb.domain.model.seq.seq import HasSeqMixin, Seq


class SeqProfile(
    Model,
    HasSampleMixin,
    HasSeqMixin,
    HasProtocolMixin,
    ContentMixin[enum.SeqProfileFormat],
    QualityMixin,
):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_profiles",
        table_name="seq_profile",
        persistable=True,
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
            }
        ),
    )
    FORMATS_BY_SEQ_PROFILE_TYPE: ClassVar[
        dict[enum.SeqProfileType, frozenset[enum.SeqProfileFormat]]
    ] = {
        enum.SeqProfileType.LOCUS: frozenset(
            {
                enum.SeqProfileFormat.LOCUS_PROFILE_FORMAT1,
            }
        ),
        enum.SeqProfileType.ALLELE: frozenset(
            {
                enum.SeqProfileFormat.ORDERED_ALLELE_IDS,
            }
        ),
        enum.SeqProfileType.SNP: frozenset(
            {
                enum.SeqProfileFormat.NEXTCLADE,
            }
        ),
        enum.SeqProfileType.MLVA: frozenset(
            {
                enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS,
            }
        ),
        enum.SeqProfileType.KMER: frozenset(
            {
                enum.SeqProfileFormat.KMER_FREQUENCY_MAP,
            }
        ),
    }

    seq_profile_type: enum.SeqProfileType = Field(
        description="The type of the sequence profile."
    )

    @field_validator("seq_profile_type", mode="before")
    @classmethod
    def _validate_seq_profile_type(
        cls, value: str | int | float | enum.SeqProfileType
    ) -> enum.SeqProfileType:
        return validate_int_enum_value(enum.SeqProfileType, value)  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_format_for_seq_profile_type(self) -> Self:
        """
        Validate that the content format is compatible with the sequence profile type.
        """
        if self.format not in self.FORMATS_BY_SEQ_PROFILE_TYPE[self.seq_profile_type]:
            raise ValueError(
                f"Invalid format {self.format} for sequence profile type {self.seq_profile_type}"
            )
        return self

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """
        Verify the representation of the content depending on the format. Verify or set
        the content hash.
        """
        if self.content == "" and any(
            getattr(self, field_name, None) is not None
            for field_name in (
                "aligned_nucleotide_seq",
                "allele_ids",
                "locus_allele_id_map",
                "repeat_numbers",
                "locus_repeat_number_map",
                "kmer_frequency_map",
            )
        ):
            return self

        profile_hash = self.content_hash
        computed_profile_hash = profile_hash
        if self.seq_profile_type == enum.SeqProfileType.LOCUS:
            computed_profile_hash = self._generate_locus_profile_hash(profile_hash)
        elif self.seq_profile_type == enum.SeqProfileType.ALLELE:
            # Parse allele profile and derive values depending on allele_profile_format
            computed_profile_hash = self._generate_allele_profile_hash()
        elif self.seq_profile_type == enum.SeqProfileType.MLVA:
            # Parse MLVA SeqProfile and derive values depending on format
            computed_profile_hash = self._generate_mlva_profile_hash()
        elif self.seq_profile_type == enum.SeqProfileType.KMER:
            # Parse KMER SeqProfile and derive hash depending on format
            computed_profile_hash = self._generate_kmer_profile_hash()
        elif self.seq_profile_type == enum.SeqProfileType.SNP:
            # Parse SNP profile and derive values depending on snp_profile_format
            computed_profile_hash = self._generate_snp_profile_hash()
        else:
            raise NotImplementedError(
                f"Unable to calculate profile hash for this sequence profile type: {self.seq_profile_type}"
            )
        if profile_hash == NULL_ID:
            self.content_hash = computed_profile_hash
        elif profile_hash != computed_profile_hash:
            raise ValueError("Provided content hash does not match computed hash")
        return self

    def _generate_snp_profile_hash(self) -> UUID:
        if self.format == enum.SeqProfileFormat.NEXTCLADE:
            # content is a flat JSON dict of NextClade fields for this single sample
            nextclade_fields: dict[str, Any] = json.loads(self.content)
            # Validate required fields at the top level of the flat dict
            if any(
                field not in REQUIRED_NEXTCLADE_SEQ_KEYS for field in nextclade_fields
            ):
                raise ValueError(
                    f"Missing required NextClade fields for SNP profile content with format {self.format}: {REQUIRED_NEXTCLADE_SEQ_KEYS}"
                )
            computed_profile_hash = SeqProfile.get_snp_profile_hash(nextclade_fields)
        else:
            SeqProfile._raise_no_computable_hash()
        return computed_profile_hash

    def _generate_kmer_profile_hash(self) -> UUID:
        if self.format == enum.SeqProfileFormat.KMER_FREQUENCY_MAP:
            # Parse the profile from json object
            kmer_frequency_map: dict[str, float] = json.loads(self.content)
            # Compute hash
            computed_profile_hash = SeqProfile.get_kmer_profile_hash(kmer_frequency_map)
        else:
            SeqProfile._raise_no_computable_hash()

        return computed_profile_hash

    def _generate_mlva_profile_hash(self) -> UUID:
        if self.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
            # Parse the profile from json array
            repeat_numbers: list[int] = json.loads(self.content)
            # Compute hash
            computed_profile_hash = SeqProfile.get_mlva_profile_hash(repeat_numbers)
        else:
            SeqProfile._raise_no_computable_hash()
        return computed_profile_hash

    def _generate_allele_profile_hash(self) -> UUID:
        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            # Parse the profile from base64 encoded concatenated 128-bit allele IDs
            allele_bytes = base64.b64decode(self.content)
            if len(allele_bytes) % 16 != 0:
                raise ValueError("Allele profile bytes length is not a multiple of 16")
            sha256 = hashlib.sha256()
            sha256.update(allele_bytes)
            computed_profile_hash = UUID(sha256.digest()[:16].hex())
        else:
            SeqProfile._raise_no_computable_hash()

        return computed_profile_hash

    def _generate_locus_profile_hash(self, profile_hash: UUID) -> UUID:
        if self.format == enum.SeqProfileFormat.LOCUS_PROFILE_FORMAT1:
            # TODO: implement calculation of hash based on the content of the locus profile
            return profile_hash
        else:
            if profile_hash == NULL_ID:
                raise ValueError(
                    "Unable to calculate locus profile hash for this format"
                )
        return profile_hash

    @field_serializer("seq_profile_type", mode="plain")
    def _serialize_seq_profile_type(self, value: enum.SeqProfileType) -> int:
        return value.value

    def get_aligned_nucleotide_seq(
        self, ref_seq_str: str | None = None, **kwargs: Any
    ) -> str:
        """
        Parse and return the aligned nucleotide sequence from the SNP profile based on its
        format. The sequence is guaranteed to be lower case.
        """
        if self.seq_profile_type != enum.SeqProfileType.SNP:
            raise ValueError(
                "Aligned nucleotide sequence can only be retrieved for SNP profiles"
            )
        # TODO: LSP-3268-Implement-SNP-profile-support-seqdb:
        # - derive aligned nucleotide seq for SNP profiles format other than NextClade
        return self.content

    def get_allele_id_bytes(self, **kwargs: Any) -> list[bytes | None]:
        """Return allele IDs as raw 16-byte chunks."""
        if self.seq_profile_type != enum.SeqProfileType.ALLELE:
            raise ValueError("Allele IDs can only be retrieved for allele profiles")
        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            allele_bytes = base64.b64decode(self.content)
            n_loci = len(allele_bytes) // 16
            result: list[bytes | None] = [None] * n_loci
            null_id_bytes = NULL_ID.bytes
            for i in range(n_loci):
                offset = i * 16
                chunk = allele_bytes[offset : offset + 16]
                if chunk != null_id_bytes:
                    result[i] = chunk
            return result
        raise NotImplementedError(
            "Unable to parse allele IDs for this allele profile format"
        )

    def get_allele_ids(self, **kwargs: Any) -> list[UUID | None]:
        """
        Parse and return the allele IDs from the allele profile based on its format.
        """
        if self.seq_profile_type != enum.SeqProfileType.ALLELE:
            raise ValueError("Allele IDs can only be retrieved for allele profiles")

        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            allele_bytes = base64.b64decode(self.content)
            n_loci = len(allele_bytes) // 16
            allele_ids: list[UUID | None] = [None] * n_loci
            null_id_bytes = NULL_ID.bytes
            for i, j in zip(range(0, len(allele_bytes), 16), range(n_loci)):
                allele_id_bytes = allele_bytes[i : i + 16]
                if allele_id_bytes != null_id_bytes:
                    allele_ids[j] = UUID(bytes=allele_id_bytes)
            return allele_ids
        raise NotImplementedError(
            "Unable to parse allele IDs for this allele profile format"
        )

    def get_n_loci(self, **kwargs: Any) -> int:
        """
        Parse and return the number of loci from the allele profile based on its format.
        """
        if self.seq_profile_type != enum.SeqProfileType.ALLELE:
            raise ValueError("Number of loci can only be retrieved for allele profiles")
        if self.format == enum.SeqProfileFormat.ORDERED_ALLELE_IDS:
            allele_bytes = base64.b64decode(self.content)
            computed_n_loci = sum(
                allele_bytes[i : i + 16] != NULL_ID.bytes
                for i in range(0, len(allele_bytes), 16)
            )
            return computed_n_loci
        raise NotImplementedError(
            "Unable to parse number of loci for this allele profile format"
        )

    def get_repeat_numbers(self, **kwargs: Any) -> list[int]:
        """
        Parse and return the repeat numbers from the MLVA profile based on its format.
        """
        if self.format == enum.SeqProfileFormat.ORDERED_REPEAT_NUMBERS:
            return json.loads(self.content)
        raise NotImplementedError(
            "Unable to parse repeat numbers for this MLVA profile format"
        )

    def get_kmer_frequency_map(self, **kwargs: Any) -> dict[str, float]:
        """
        Parse and return the k-mer frequency map from the k-mer profile based on its format.
        """
        if self.format == enum.SeqProfileFormat.KMER_FREQUENCY_MAP:
            retval: dict[str, float] = json.loads(self.content)
            return retval
        raise NotImplementedError(
            "Unable to parse k-mer frequency map for this k-mer profile format"
        )

    @staticmethod
    def get_ordered_allele_ids_representation(allele_ids: list[UUID | None]) -> str:
        """
        Generate and return the allele profile in ORDERED_ALLELE_IDS format based on
        the ordered allele IDs.
        """
        return base64.b64encode(
            b"".join(NULL_ID.bytes if x is None else x.bytes for x in allele_ids)
        ).decode("ascii")

    @staticmethod
    def get_ordered_repeat_numbers_representation(
        repeat_numbers: list[int | None],
    ) -> str:
        """
        Generate and return the MLVA profile in ORDERED_REPEAT_NUMBERS format based on
        the ordered repeat numbers.
        """
        return json.dumps(
            [
                int(x) if x is not None else MLVA_NO_LOCUS_REPEAT_NUMBER
                for x in repeat_numbers
            ]
        )

    @staticmethod
    def get_allele_profile_hash(allele_ids: list[UUID | None]) -> UUID:
        sha256 = hashlib.sha256()
        for allele_id in allele_ids:
            if allele_id is not None:
                sha256.update(allele_id.bytes)
            else:
                sha256.update(NULL_ID.bytes)
        return UUID(sha256.digest()[:16].hex())

    @staticmethod
    def get_mlva_profile_hash(repeat_numbers: list[int | None]) -> UUID:
        sha256 = hashlib.sha256()
        for repeat_number in repeat_numbers:
            if repeat_number is not None:
                sha256.update(repeat_number.to_bytes(4, byteorder="big", signed=True))
            else:
                sha256.update(
                    MLVA_NO_LOCUS_REPEAT_NUMBER.to_bytes(
                        4, byteorder="big", signed=True
                    )
                )
        return UUID(sha256.digest()[:16].hex())

    @staticmethod
    def get_kmer_profile_hash(kmer_frequency_map: dict[str, float]) -> UUID:
        sha256 = hashlib.sha256()
        for kmer in sorted(kmer_frequency_map.keys()):
            freq = kmer_frequency_map[kmer]
            sha256.update(kmer.encode("ascii"))
            sha256.update(bytearray(struct.pack(">d", freq)))
        return UUID(sha256.digest()[:16].hex())

    @staticmethod
    def get_snp_profile_hash(nextclade_fields: dict[str, Any]) -> UUID:
        """Compute a deterministic hash from the flat NextClade fields of a single
        sample. Field names and values are iterated in sorted order."""
        sha256 = hashlib.sha256()
        for field_name in sorted(nextclade_fields.keys()):
            value = nextclade_fields[field_name]
            sha256.update(field_name.encode("ascii"))
            if isinstance(value, str):
                sha256.update(value.encode("ascii"))
            elif isinstance(value, list):
                for item in value:
                    sha256.update(str(item).encode("ascii"))
            elif value is not None:
                sha256.update(str(value).encode("ascii"))
        return UUID(sha256.digest()[:16].hex())

    @staticmethod
    def _raise_no_computable_hash() -> None:
        raise NotImplementedError("Unable to compute content hash for this format")

    # TODO: Uncomment if required in the validation of SNP-profile content
    # @staticmethod
    # def nextclade_get_ref_alignment(
    #     nextclade_df: pd.DataFrame | dict[str, dict[str, Any]],
    #     ref_seq: str | None = None,
    #     remove_conserved: bool | str = False,
    #     uppercase: bool = True,
    #     verify: bool = False,
    # ) -> pd.DataFrame:
    #     """
    #     Derive the alignment to the reference that is encoded in NextClade output. The alignment is represented
    #     as a dataframe with the same order of rows, the NextClade 'seqName' column used as index and an ordered series
    #     of alignment columns containing the uppercase symbols. Column names start with the reference sequence symbol
    #     followed by the reference sequence position. Insertions with respect to the reference each have a separate
    #     column with symbol 'X' or '-' depending on whether the insertion is present, and the column name has an
    #     additional suffix of : followed by the inserted symbols. Before the first and after the last aligned position,
    #     the '*' symbol is used instead of '-', to distinguish from a deletion.

    #     If no reference sequence is provided, the alignment will only contain columns that are not conserved with
    #     respect to the reference, i.e. for which at least one sequence has either a substitution, a deletion, an
    #     insertion or a non-ACGTN. In that case, remove_conserved must be set to True. Without the reference
    #     sequence, columns with no subsitutions and only deletions, insertions or non-ACGTNs, have an 'X' put as symbol
    #     where the reference sequence symbol should otherwise be put (if a substitution is present, the reference
    #     sequence symbol can be derived from the way the substitution is encoded in the NextClade output).

    #     :param nextclade_df: NextClade output as a DataFrame or dict. If dict, keys are sample names and
    #         values are dicts with NextClade fields (substitutions, deletions, insertions, missing,
    #         non_acgtns, alignment_start, alignment_end)
    #     :type nextclade_df: pd.DataFrame or dict[str, dict[str, Any]]
    #     :param ref_seq: reference sequence
    #     :type ref_seq: str
    #     :param remove_conserved: whether conserved positions should be removed. Can also be string 'ALL' (equivalent to True)
    #     or 'REF_ONLY' (only conserved positions that are also equal to the reference sequence are removed).
    #     :type remove_conserved: bool or str
    #     :param uppercase: whether the symbols should be in uppercase
    #     :type uppercase: bool
    #     :param verify: whether the generated reference alignment should be verified against the source NextClade output
    #     :type verify: bool
    #     :return: alignment to a reference as described above
    #     :rtype: dataframe
    #     """
    #     # Convert dict input to DataFrame if needed
    #     if isinstance(nextclade_df, dict):
    #         records = []
    #         for seq_name, fields in nextclade_df.items():
    #             record = {"seqName": seq_name}
    #             record.update(fields)
    #             records.append(record)
    #         nextclade_df = pd.DataFrame.from_records(records)

    #     # Process input
    #     if isinstance(remove_conserved, str):
    #         if remove_conserved == "REF_ONLY":
    #             remove_conserved_ref = True
    #             remove_conserved_non_ref = False
    #         elif remove_conserved == "ALL":
    #             remove_conserved_ref = True
    #             remove_conserved_non_ref = True
    #         else:
    #             raise ValueError(
    #                 "Invalid string value for remove_conserved: {:s}".format(
    #                     remove_conserved
    #                 )
    #             )
    #     else:
    #         if remove_conserved:
    #             remove_conserved_ref = True
    #             remove_conserved_non_ref = True
    #         else:
    #             remove_conserved_ref = False
    #             remove_conserved_non_ref = False
    #     if ref_seq is None and not remove_conserved_ref:
    #         raise ValueError(
    #             "Invalid input combination: keep conserved reference positions and and no reference sequence given"
    #         )
    #     if ref_seq is not None:
    #         # Force uppercase
    #         ref_seq = ref_seq.upper()

    #     # Initialise some
    #     n_seqs = nextclade_df.shape[0]
    #     if not remove_conserved_ref:
    #         columns = {str(i + 1): [x] * n_seqs for i, x in enumerate(ref_seq)}
    #     else:
    #         columns = {}
    #     if ref_seq is not None:
    #         partial_ref_seq = {str(i + 1): x for i, x in enumerate(ref_seq)}
    #     else:
    #         partial_ref_seq = {}

    #     # Special case: no sequences
    #     if nextclade_df.shape[0] == 0:
    #         if remove_conserved_ref:
    #             # Zero alignment positions
    #             alignment_df = nextclade_df.loc[:, ["seqName"]].copy()
    #         else:
    #             # All reference positions
    #             columns = {x + str(i): [] for i, x in enumerate(ref_seq)}
    #             alignment_df = pd.concat(
    #                 [nextclade_df.loc[:, ["seqName"]].copy(), pd.from_dict(columns)],
    #                 axis=1,
    #                 ignore_index=True,
    #             )
    #         return alignment_df

    #     # Process substitutions
    #     for i, substitutions in enumerate(nextclade_df["substitutions"]):
    #         if substitutions is None:
    #             continue
    #         elif not isinstance(substitutions, str) and np.isnan(substitutions):
    #             continue
    #         for substitution in substitutions.split(","):
    #             reference_nucleotide = substitution[0]
    #             position = substitution[1:-1]
    #             mutated_nucleotide = substitution[-1]
    #             if position not in columns:
    #                 columns[position] = [reference_nucleotide] * n_seqs
    #                 if ref_seq is None:
    #                     partial_ref_seq[position] = reference_nucleotide
    #                 elif partial_ref_seq[position] != reference_nucleotide:
    #                     raise ValueError(
    #                         "Provided reference sequence does not match with reference positions encoded in substitutions at position {:s}: {s} provided, found {:s}".format(
    #                             position,
    #                             partial_ref_seq[position],
    #                             reference_nucleotide,
    #                         )
    #                     )
    #             columns[position][i] = mutated_nucleotide

    #     # Process non-ACTGNs
    #     for i, nonACGTN_ranges in enumerate(nextclade_df["non_acgtns"]):
    #         if nonACGTN_ranges is None:
    #             continue
    #         elif not isinstance(nonACGTN_ranges, str):
    #             if np.isnan(nonACGTN_ranges):
    #                 continue
    #             nonACGTN_ranges = str(nonACGTN_ranges)
    #         for nonACGTN_range in nonACGTN_ranges.split(","):
    #             nonACGTN = nonACGTN_range[0]
    #             nonACGTN_range = nonACGTN_range[2:].split("-")
    #             nonACGTN_start = int(nonACGTN_range[0])
    #             if len(nonACGTN_range) == 2:
    #                 nonACGTN_end = int(nonACGTN_range[1])
    #             else:
    #                 nonACGTN_end = nonACGTN_start
    #             for j in range(nonACGTN_start, nonACGTN_end + 1):
    #                 position = str(j)
    #                 if position not in columns:
    #                     if ref_seq is None:
    #                         columns[position] = ["X"] * n_seqs
    #                     else:
    #                         columns[position] = [ref_seq[int(position) - 1]] * n_seqs
    #                 columns[position][i] = nonACGTN

    #     # Process deletions
    #     for i, deletion_ranges in enumerate(nextclade_df["deletions"]):
    #         if deletion_ranges is None:
    #             continue
    #         elif not isinstance(deletion_ranges, str):
    #             if np.isnan(deletion_ranges):
    #                 continue
    #             deletion_ranges = str(deletion_ranges)
    #         for deletion_range in deletion_ranges.split(","):
    #             deletion_range = deletion_range.split("-")
    #             deletion_start = int(deletion_range[0])
    #             if len(deletion_range) == 2:
    #                 deletion_end = int(deletion_range[1])
    #             else:
    #                 deletion_end = deletion_start
    #             for j in range(deletion_start, deletion_end + 1):
    #                 position = str(j)
    #                 if position not in columns:
    #                     if ref_seq is None:
    #                         columns[position] = ["X"] * n_seqs
    #                     else:
    #                         columns[position] = [ref_seq[int(position) - 1]] * n_seqs
    #                 columns[position][i] = "-"

    #     # Process insertions
    #     for i, insertions in enumerate(nextclade_df["insertions"]):
    #         if insertions is None:
    #             continue
    #         elif not isinstance(insertions, str) and np.isnan(insertions):
    #             continue
    #         for insertion in insertions.split(","):
    #             if insertion not in columns:
    #                 columns[insertion] = ["-"] * n_seqs
    #             columns[insertion][i] = "X"

    #     # Process missing
    #     for i, missing_ranges in enumerate(nextclade_df["missings"]):
    #         if missing_ranges is None:
    #             continue
    #         elif not isinstance(missing_ranges, str):
    #             if np.isnan(missing_ranges):
    #                 continue
    #             missing_ranges = str(missing_ranges)
    #         for missing_range in missing_ranges.split(","):
    #             missing_range = missing_range.split("-")
    #             missing_start = int(missing_range[0])
    #             if len(missing_range) == 2:
    #                 missing_end = int(missing_range[1])
    #             else:
    #                 missing_end = missing_start
    #             for j in range(missing_start, missing_end + 1):
    #                 position = str(j)
    #                 column = columns.get(position)
    #                 if column is None:
    #                     # Missing position not considered by itself as polymorphic, only added completely when remove_conserved_ref=False
    #                     continue
    #                 column[i] = "N"

    #     # Process alignment start
    #     for i, alignment_start in enumerate(nextclade_df["alignment_start"]):
    #         if alignment_start is None:
    #             continue
    #         for j in range(1, int(alignment_start)):
    #             position = str(j)
    #             if position not in columns:
    #                 continue
    #             columns[position][i] = "*"

    #     # Process alignment end
    #     for i, alignment_end in enumerate(nextclade_df["alignment_end"]):
    #         if alignment_end is None:
    #             continue
    #         j = int(alignment_end) + 1
    #         while str(j) in columns:
    #             columns[str(j)][i] = "*"
    #             j = j + 1

    #     # Get column properties and order
    #     column_name_df = pd.DataFrame.from_dict(
    #         {"name_without_ref": list(columns.keys())}
    #     )
    #     split_columns_df = column_name_df["name_without_ref"].str.split(
    #         pat=":", n=2, expand=True
    #     )
    #     if split_columns_df.shape[1] == 2:
    #         column_name_df[["position_str", "insertion_symbols"]] = split_columns_df
    #     else:
    #         column_name_df["position_str"] = column_name_df["name_without_ref"]
    #         column_name_df["insertion_symbols"] = None
    #     column_name_df["position_int"] = column_name_df["position_str"].apply(int)
    #     column_name_df["ref_symbol"] = column_name_df["position_str"].apply(
    #         lambda x: partial_ref_seq.get(x, "X")
    #     )
    #     column_name_df["is_insertion"] = column_name_df["insertion_symbols"].apply(
    #         lambda x: False if pd.isna(x) or len(x) == 0 else True
    #     )
    #     column_name_df["name"] = (
    #         column_name_df["ref_symbol"] + column_name_df["name_without_ref"]
    #     )
    #     column_name_df.sort_values(
    #         by=["position_int", "is_insertion", "insertion_symbols"], inplace=True
    #     )
    #     column_name_df.set_index("name_without_ref", drop=False)

    #     # Verify if NextClade data can be reconstructed from alignment
    #     # If no reference sequence is provided, alignment start/end and missing ranges cannot be fully reconstructed and are ignored
    #     if verify:
    #         # Get some indexing information
    #         position_names = column_name_df["name_without_ref"].tolist()
    #         position_is_insertion = column_name_df["is_insertion"].tolist()
    #         position_indexes = column_name_df["position_int"].tolist()
    #         ref_seq_length = max(position_indexes)
    #         # Get sequences from columns, i.e. the transpose, in an optimised way
    #         template_seq = [partial_ref_seq.get(x, "X") for x in position_names]
    #         seqs = [copy.deepcopy(template_seq) for i in range(0, n_seqs)]
    #         for i, position in enumerate(position_names):
    #             column = columns[position]
    #             template_symbol = template_seq[i]
    #             for j, mutated_nucleotide in enumerate(column):
    #                 if mutated_nucleotide != template_symbol:
    #                     seqs[j][i] = mutated_nucleotide
    #         seqs = {x: "".join(y) for x, y in zip(nextclade_df["seqName"], seqs)}
    #         # Go over each sequence
    #         for seq_name, seq in seqs.items():
    #             # Initialise some
    #             substitutions = []
    #             deletion_ranges = []
    #             insertions = []
    #             nonACGTN_ranges = []
    #             missing_ranges = []
    #             prev_index = -1
    #             prev_symbol = "X"
    #             deletion_start = -1
    #             deletion_length = 0
    #             missing_start = -1
    #             missing_length = 0
    #             nonACGTN_start = -1
    #             nonACGTN_length = 0
    #             # Determine alignment start and end, as one-based indexes
    #             i = 0
    #             alignment_start = 1
    #             while i < len(seq) and seq[i] == "*":
    #                 if not position_is_insertion[i]:
    #                     alignment_start = alignment_start + 1
    #                 i = i + 1
    #             i = len(seq) - 1
    #             alignment_end = ref_seq_length
    #             while i >= 0 and seq[i] == "*":
    #                 if not position_is_insertion[i]:
    #                     alignment_end = alignment_end - 1
    #                 i = i - 1
    #             # Go over each symbol and compose substitutions, deletions, insertions, nonACTGNs and missing
    #             for i, mutated_nucleotide in enumerate(seq):
    #                 position = position_names[i]
    #                 index = position_indexes[i]
    #                 is_insertion = position_is_insertion[i]
    #                 if prev_index < index - 1 or (
    #                     mutated_nucleotide != prev_symbol and not is_insertion
    #                 ):
    #                     # Non-consecutive reference position or different symbol -> add previous missing or deletion range if any
    #                     if deletion_length == 1:
    #                         deletion_ranges.append(str(prev_index))
    #                     elif deletion_length > 1:
    #                         deletion_ranges.append(
    #                             str(prev_index - deletion_length + 1)
    #                             + "-"
    #                             + str(prev_index)
    #                         )
    #                     deletion_start = -1
    #                     deletion_length = 0
    #                     if missing_length == 1:
    #                         missing_ranges.append(str(prev_index))
    #                     elif missing_length > 1:
    #                         missing_ranges.append(
    #                             str(prev_index - missing_length + 1)
    #                             + "-"
    #                             + str(prev_index)
    #                         )
    #                     missing_start = -1
    #                     missing_length = 0
    #                     if nonACGTN_length == 1:
    #                         nonACGTN_length.append(prev_symbol + ":" + str(prev_index))
    #                     elif nonACGTN_length > 1:
    #                         nonACGTN_ranges.append(
    #                             prev_symbol
    #                             + ":"
    #                             + str(prev_index - nonACGTN_length + 1)
    #                             + "-"
    #                             + str(prev_index)
    #                         )
    #                     nonACGTN_start = -1
    #                     nonACGTN_length = 0
    #                 if is_insertion:
    #                     # Insertion position
    #                     if mutated_nucleotide == "X":
    #                         # Insertion
    #                         insertions.append(position)
    #                 elif mutated_nucleotide == "*":
    #                     # Outside alignment
    #                     pass
    #                 elif mutated_nucleotide == "N":
    #                     # Missing
    #                     if prev_index == index - 1 and missing_length > 0:
    #                         # Consecutive missing
    #                         missing_length += 1
    #                     else:
    #                         # Start of new missing
    #                         missing_start = index
    #                         missing_length = 1
    #                 elif mutated_nucleotide == "-":
    #                     # Deletion
    #                     if prev_index == index - 1 and deletion_length > 0:
    #                         # Consecutive deletion
    #                         deletion_length += 1
    #                     else:
    #                         # Start of new deletion
    #                         deletion_start = index
    #                         deletion_length = 1
    #                 elif mutated_nucleotide in "ACGT":
    #                     # Substitution or identical to reference
    #                     if mutated_nucleotide != template_seq[i]:
    #                         # Substitution
    #                         substitutions.append(
    #                             template_seq[i] + position + mutated_nucleotide
    #                         )
    #                 else:
    #                     # nonACGTN
    #                     if prev_index == index - 1 and deletion_length > 0:
    #                         # Consecutive nonACTGN
    #                         nonACGTN_length += 1
    #                     else:
    #                         # Start of new deletion
    #                         nonACGTN_start = index
    #                         nonACGTN_length = 1
    #                 if not is_insertion:
    #                     prev_index = index
    #                     prev_symbol = mutated_nucleotide
    #             # Add final missing or deletion range if any
    #             if deletion_length == 1:
    #                 deletion_ranges.append(str(prev_index))
    #             elif deletion_length > 1:
    #                 deletion_ranges.append(
    #                     str(prev_index - deletion_length + 1) + "-" + str(prev_index)
    #                 )
    #             if missing_length == 1:
    #                 missing_ranges.append(str(prev_index))
    #             elif missing_length > 1:
    #                 missing_ranges.append(
    #                     str(prev_index - missing_length + 1) + "-" + str(prev_index)
    #                 )
    #             if nonACGTN_length == 1:
    #                 nonACGTN_ranges.append(mutated_nucleotide + ":" + str(prev_index))
    #             elif nonACGTN_length > 1:
    #                 nonACGTN_ranges.append(
    #                     mutated_nucleotide
    #                     + ":"
    #                     + str(prev_index - nonACGTN_length + 1)
    #                     + "-"
    #                     + str(prev_index)
    #                 )
    #             # Compare with original NextClade data
    #             mask = nextclade_df["seqName"] == seq_name
    #             verification_pairs = {
    #                 "substitutions": substitutions,
    #                 "non_acgtns": nonACGTN_ranges,
    #                 "insertions": insertions,
    #                 "deletions": deletion_ranges,
    #             }
    #             if not remove_conserved_ref:
    #                 verification_pairs = verification_pairs | {
    #                     "missings": missing_ranges,
    #                     "alignment_start": [str(alignment_start)],
    #                     "alignment_end": [str(alignment_end)],
    #                 }
    #             for column_name, reconstructed_values in verification_pairs.items():
    #                 actual_values = nextclade_df.loc[mask, column_name].iloc[0]
    #                 if column_name == "alignment_start":
    #                     # actual_values = int(actual_values) + 1
    #                     actual_values = int(actual_values)
    #                 if actual_values is None or isinstance(actual_values, str):
    #                     pass
    #                 elif np.isnan(actual_values):
    #                     actual_values = None
    #                 elif isinstance(actual_values, int) or isinstance(
    #                     actual_values, float
    #                 ):
    #                     # Alignment start and end are normally numeric, potentially also single deletions and missing if only singles present -> convert to str
    #                     actual_values = str(int(actual_values))
    #                 actual_values = (
    #                     [] if actual_values is None else actual_values.split(",")
    #                 )
    #                 if collections.Counter(reconstructed_values) != collections.Counter(
    #                     actual_values
    #                 ):
    #                     raise AssertionError(
    #                         "Unable to reconstruct NextClade {:s} data for sequence {:s}".format(
    #                             column_name, str(seq_name)
    #                         )
    #                     )

    #     # Determine columns to remove
    #     columns_to_remove = []
    #     if remove_conserved_ref or remove_conserved_non_ref:
    #         for key, value in columns.items():
    #             symbols = str(set(value))
    #             if len(symbols) == 1:
    #                 # Conserved column
    #                 if symbols == ref_seq[column_name_df.loc[key, "position_int"] - 1]:
    #                     # Reference sequence symbol
    #                     if remove_conserved_ref:
    #                         columns_to_remove.append(key)
    #                 else:
    #                     # Other symbol
    #                     if remove_conserved_non_ref:
    #                         columns_to_remove.append(key)

    #     # Create alignment df, with alignment columns having also the reference symbol as prefix, and symbols set to lowercase if necessary
    #     ordered_column_names = {
    #         x: y
    #         for x, y in zip(column_name_df["name_without_ref"], column_name_df["name"])
    #         if x not in columns_to_remove
    #     }
    #     ref_alignment = pd.DataFrame.from_dict(
    #         {
    #             y: columns[x] if uppercase else [z.lower() for z in columns[x]]
    #             for x, y in ordered_column_names.items()
    #         }
    #     )
    #     ref_alignment.index = nextclade_df["seqName"]

    #     return ref_alignment


class SeqProfileIdentifier(BaseIdentifier):
    ENTITY: ClassVar = BaseIdentifier.create_entity(
        SeqProfile,
        relationship_field_name="seq_profile",
        snake_case_plural_name="seq_profile_identifiers",
        table_name="seq_profile_identifier",
    )
    NAME: ClassVar = "SeqProfileIdentifier"
    MODEL_CLASS: ClassVar = SeqProfile

    seq_profile: SeqProfile | None = Field(
        default=None,
        description="The sequence profile associated with this identifier.",
    )
