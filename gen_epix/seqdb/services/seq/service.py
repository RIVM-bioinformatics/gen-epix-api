from collections.abc import Iterable
from uuid import UUID

from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.repository import BaseSeqRepository
from gen_epix.seqdb.domain.service import BaseSeqService
from gen_epix.seqdb.services.seq.calculate_phylogenetic_tree import (
    seq_service_calculate_phylogenetic_tree,
)
from gen_epix.seqdb.services.seq.calculate_seq_distance import (
    seq_service_calculate_seq_distances_for_new_profiles,
)
from gen_epix.seqdb.services.seq.crud_allele import seq_service_crud_allele
from gen_epix.seqdb.services.seq.crud_ast_measurement import (
    seq_service_crud_ast_measurement,
)
from gen_epix.seqdb.services.seq.crud_ast_prediction import (
    seq_service_crud_ast_prediction,
)

from gen_epix.seqdb.services.seq.crud_locus import seq_service_crud_locus
from gen_epix.seqdb.services.seq.crud_locus_code_map import (
    seq_service_crud_locus_code_map,
)
from gen_epix.seqdb.services.seq.crud_locus_set import seq_service_crud_locus_set
from gen_epix.seqdb.services.seq.crud_pcr_measurement import (
    seq_service_crud_pcr_measurement,
)
from gen_epix.seqdb.services.seq.crud_protocol import seq_service_crud_protocol
from gen_epix.seqdb.services.seq.crud_protocol_set import seq_service_crud_protocol_set
from gen_epix.seqdb.services.seq.crud_protocol_set_member import (
    seq_service_crud_protocol_set_member,
)
from gen_epix.seqdb.services.seq.crud_read_set import seq_service_crud_read_set
from gen_epix.seqdb.services.seq.crud_read_set_identifier import (
    seq_service_crud_read_set_identifier,
)
from gen_epix.seqdb.services.seq.crud_ref_allele import seq_service_crud_ref_allele
from gen_epix.seqdb.services.seq.crud_ref_seq import seq_service_crud_ref_seq
from gen_epix.seqdb.services.seq.crud_sample import seq_service_crud_sample
from gen_epix.seqdb.services.seq.crud_sample_data_collection_link import (
    seq_service_crud_sample_data_collection_link,
)
from gen_epix.seqdb.services.seq.crud_sample_identifier import (
    seq_service_crud_sample_identifier,
)
from gen_epix.seqdb.services.seq.crud_seq import seq_service_crud_seq
from gen_epix.seqdb.services.seq.crud_seq_category import seq_service_crud_seq_category
from gen_epix.seqdb.services.seq.crud_seq_category_set import (
    seq_service_crud_seq_category_set,
)
from gen_epix.seqdb.services.seq.crud_seq_classification import (
    seq_service_crud_seq_classification,
)
from gen_epix.seqdb.services.seq.crud_seq_distance import seq_service_crud_seq_distance
from gen_epix.seqdb.services.seq.crud_seq_identifier import (
    seq_service_crud_seq_identifier,
)
from gen_epix.seqdb.services.seq.crud_seq_profile import (
    seq_service_crud_seq_profile,
)
from gen_epix.seqdb.services.seq.crud_seq_profile_identifier import (
    seq_service_crud_seq_profile_identifier,
)
from gen_epix.seqdb.services.seq.crud_seq_taxonomy import seq_service_crud_seq_taxonomy
from gen_epix.seqdb.services.seq.crud_taxon import seq_service_crud_taxon
from gen_epix.seqdb.services.seq.crud_taxon_set import seq_service_crud_taxon_set
from gen_epix.seqdb.services.seq.crud_taxon_set_member import (
    seq_service_crud_taxon_set_member,
)
from gen_epix.seqdb.services.seq.crud_tree_algorithm import (
    seq_service_crud_tree_algorithm,
)
from gen_epix.seqdb.services.seq.crud_tree_algorithm_class import (
    seq_service_crud_tree_algorithm_class,
)
from gen_epix.seqdb.services.seq.upload import seq_service_upload_samples


class SeqService(BaseSeqService):

    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        return seq_service_upload_samples(self, cmd)

    def retrieve_phylogenetic_tree(
        self, cmd: command.CalculatePhylogeneticTreeCommand
    ) -> model.PhylogeneticTree | None:
        return seq_service_calculate_phylogenetic_tree(self, cmd)

    def retrieve_samples(
        self, cmd: command.RetrieveSamplesCommand
    ) -> list[model.SampleForUpload]:
        raise NotImplementedError()

    def retrieve_seq_fasta(self, cmd: command.RetrieveSeqFastaCommand) -> Iterable[str]:
        wrap = cmd.wrap or cmd.model_fields["wrap"].default
        self.repository: BaseSeqRepository
        with self.repository.uow() as uow:
            for seq_id, contigs in self.repository.retrieve_seq_fasta(uow, cmd.seq_ids):
                for contig_seq_hash, raw_seq in contigs:
                    header = f">{seq_id}:{contig_seq_hash}\n"
                    if not wrap:
                        yield f"{header}{raw_seq}\n"
                    seq_length = len(raw_seq)
                    n_chunks = (seq_length // wrap) + (seq_length % wrap > 0)
                    yield header + "\n".join(
                        raw_seq[i * wrap : min((i + 1) * wrap, seq_length)]
                        for i in range(n_chunks)
                    )

    def retrieve_similar_profiles(
        self,
        cmd: command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        # Special case: zero query profile ids
        if not cmd.profile_ids:
            return []
        # Use dedicated repository method to retrieve similar profiles, which allows for more efficient retrieval of distances and distance formats
        with self.repository.uow() as uow:
            similar_profile_ids: list[UUID] = self.repository.retrieve_similar_profiles(
                uow,
                cmd.protocol_id,
                cmd.profile_ids,
                cmd.max_distance,
            )
        return similar_profile_ids

    def calculate_seq_distances_for_new_profiles(
        self,
        cmd: command.CalculateSeqDistancesForNewProfilesCommand,
    ) -> list[model.CalculateSeqDistancesResult]:
        return seq_service_calculate_seq_distances_for_new_profiles(self, cmd)

    def crud_protocol(
        self,
        cmd: command.ProtocolCrudCommand,
    ) -> (
        model.Protocol
        | list[model.Protocol]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_protocol(self, cmd)

    def crud_protocol_set(
        self,
        cmd: command.ProtocolSetCrudCommand,
    ) -> (
        model.ProtocolSet
        | list[model.ProtocolSet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_protocol_set(self, cmd)

    def crud_protocol_set_member(
        self,
        cmd: command.ProtocolSetMemberCrudCommand,
    ) -> (
        model.ProtocolSetMember
        | list[model.ProtocolSetMember]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_protocol_set_member(self, cmd)

    def crud_allele(
        self,
        cmd: command.AlleleCrudCommand,
    ) -> (
        model.Allele | list[model.Allele] | UUID | list[UUID] | bool | list[bool] | None
    ):
        return seq_service_crud_allele(self, cmd)

    def crud_ast_measurement(
        self,
        cmd: command.AstMeasurementCrudCommand,
    ) -> (
        model.AstMeasurement
        | list[model.AstMeasurement]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_ast_measurement(self, cmd)

    def crud_ast_prediction(
        self,
        cmd: command.AstPredictionCrudCommand,
    ) -> (
        model.AstPrediction
        | list[model.AstPrediction]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_ast_prediction(self, cmd)

    def crud_locus(
        self,
        cmd: command.LocusCrudCommand,
    ) -> model.Locus | list[model.Locus] | UUID | list[UUID] | bool | list[bool] | None:
        return seq_service_crud_locus(self, cmd)

    def crud_locus_code_map(
        self,
        cmd: command.LocusCodeMapCrudCommand,
    ) -> (
        model.LocusCodeMap
        | list[model.LocusCodeMap]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_locus_code_map(self, cmd)

    def crud_seq_profile(
        self,
        cmd: command.SeqProfileCrudCommand,
    ) -> (
        model.SeqProfile
        | list[model.SeqProfile]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_profile(self, cmd)

    def crud_seq_profile_identifier(
        self,
        cmd: command.SeqProfileIdentifierCrudCommand,
    ) -> (
        model.SeqProfileIdentifier
        | list[model.SeqProfileIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_profile_identifier(self, cmd)

    def crud_locus_set(
        self,
        cmd: command.LocusSetCrudCommand,
    ) -> (
        model.LocusSet
        | list[model.LocusSet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_locus_set(self, cmd)

    def crud_pcr_measurement(
        self,
        cmd: command.PcrMeasurementCrudCommand,
    ) -> (
        model.PcrMeasurement
        | list[model.PcrMeasurement]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_pcr_measurement(self, cmd)

    def crud_read_set(
        self,
        cmd: command.ReadSetCrudCommand,
    ) -> (
        model.ReadSet
        | list[model.ReadSet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_read_set(self, cmd)

    def crud_read_set_identifier(
        self,
        cmd: command.ReadSetIdentifierCrudCommand,
    ) -> (
        model.ReadSetIdentifier
        | list[model.ReadSetIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_read_set_identifier(self, cmd)

    def crud_ref_allele(
        self,
        cmd: command.RefAlleleCrudCommand,
    ) -> (
        model.RefAllele
        | list[model.RefAllele]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_ref_allele(self, cmd)

    def crud_ref_seq(
        self,
        cmd: command.RefSeqCrudCommand,
    ) -> (
        model.RefSeq | list[model.RefSeq] | UUID | list[UUID] | bool | list[bool] | None
    ):
        return seq_service_crud_ref_seq(self, cmd)

    def crud_sample(
        self,
        cmd: command.SampleCrudCommand,
    ) -> (
        model.Sample | list[model.Sample] | UUID | list[UUID] | bool | list[bool] | None
    ):
        return seq_service_crud_sample(self, cmd)

    def crud_sample_data_collection_link(
        self,
        cmd: command.SampleDataCollectionLinkCrudCommand,
    ) -> (
        model.SampleDataCollectionLink
        | list[model.SampleDataCollectionLink]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_sample_data_collection_link(self, cmd)

    def crud_sample_identifier(
        self,
        cmd: command.SampleIdentifierCrudCommand,
    ) -> (
        model.SampleIdentifier
        | list[model.SampleIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_sample_identifier(self, cmd)

    def crud_seq(
        self,
        cmd: command.SeqCrudCommand,
    ) -> model.Seq | list[model.Seq] | UUID | list[UUID] | bool | list[bool] | None:
        return seq_service_crud_seq(self, cmd)

    def crud_seq_category(
        self,
        cmd: command.SeqCategoryCrudCommand,
    ) -> (
        model.SeqCategory
        | list[model.SeqCategory]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_category(self, cmd)

    def crud_seq_category_set(
        self,
        cmd: command.SeqCategorySetCrudCommand,
    ) -> (
        model.SeqCategorySet
        | list[model.SeqCategorySet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_category_set(self, cmd)

    def crud_seq_classification(
        self,
        cmd: command.SeqClassificationCrudCommand,
    ) -> (
        model.SeqClassification
        | list[model.SeqClassification]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_classification(self, cmd)

    def crud_seq_distance(
        self,
        cmd: command.SeqDistanceCrudCommand,
    ) -> (
        model.SeqDistance
        | list[model.SeqDistance]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_distance(self, cmd)

    def crud_seq_identifier(
        self,
        cmd: command.SeqIdentifierCrudCommand,
    ) -> (
        model.SeqIdentifier
        | list[model.SeqIdentifier]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_identifier(self, cmd)

    def crud_seq_taxonomy(
        self,
        cmd: command.SeqTaxonomyCrudCommand,
    ) -> (
        model.SeqTaxonomy
        | list[model.SeqTaxonomy]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_seq_taxonomy(self, cmd)

    def crud_taxon(
        self,
        cmd: command.TaxonCrudCommand,
    ) -> model.Taxon | list[model.Taxon] | UUID | list[UUID] | bool | list[bool] | None:
        return seq_service_crud_taxon(self, cmd)

    def crud_taxon_set(
        self,
        cmd: command.TaxonSetCrudCommand,
    ) -> (
        model.TaxonSet
        | list[model.TaxonSet]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_taxon_set(self, cmd)

    def crud_taxon_set_member(
        self,
        cmd: command.TaxonSetMemberCrudCommand,
    ) -> (
        model.TaxonSetMember
        | list[model.TaxonSetMember]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_taxon_set_member(self, cmd)

    def crud_tree_algorithm(
        self,
        cmd: command.TreeAlgorithmCrudCommand,
    ) -> (
        model.TreeAlgorithm
        | list[model.TreeAlgorithm]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_tree_algorithm(self, cmd)

    def crud_tree_algorithm_class(
        self,
        cmd: command.TreeAlgorithmClassCrudCommand,
    ) -> (
        model.TreeAlgorithmClass
        | list[model.TreeAlgorithmClass]
        | UUID
        | list[UUID]
        | bool
        | list[bool]
        | None
    ):
        return seq_service_crud_tree_algorithm_class(self, cmd)
