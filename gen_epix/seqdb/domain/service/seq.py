import abc
import datetime
from collections.abc import Iterable
from uuid import UUID

from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ServiceType


class BaseSeqService(BaseService):
    SERVICE_TYPE = ServiceType.SEQ

    def register_handlers(self) -> None:
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(
            command.CalculatePhylogeneticTreeCommand,
            self.calculate_phylogenetic_tree,
        )
        f(command.RetrieveSamplesByQueryCommand, self.retrieve_samples_by_query)
        f(command.RetrieveSamplesByIdCommand, self.retrieve_samples_by_id)
        f(
            command.RetrieveSeqFastaCommand,
            self.retrieve_seq_fasta,
        )
        f(
            command.UploadSamplesCommand,
            self.upload_samples,
        )
        f(
            command.RetrieveSimilarProfilesCommand,
            self.retrieve_similar_profiles,
        )
        f(
            command.RetrieveSeqDistanceLastModifiedCommand,
            self.retrieve_seq_distance_last_modified,
        )
        f(
            command.CalculateSeqDistancesForNewProfilesCommand,
            self.calculate_seq_distances_for_new_profiles,
        )
        f(
            command.UpdateSeqDistancesCommand,
            self.update_seq_distances,
        )
        f(
            command.ProtocolCrudCommand,
            self.crud_protocol,
        )
        f(
            command.ProtocolSetCrudCommand,
            self.crud_protocol_set,
        )
        f(
            command.ProtocolSetMemberCrudCommand,
            self.crud_protocol_set_member,
        )
        f(
            command.AlleleCrudCommand,
            self.crud_allele,
        )
        f(
            command.AstMeasurementCrudCommand,
            self.crud_ast_measurement,
        )
        f(
            command.AstPredictionCrudCommand,
            self.crud_ast_prediction,
        )

        f(
            command.LocusCrudCommand,
            self.crud_locus,
        )
        f(
            command.LocusCodeMapCrudCommand,
            self.crud_locus_code_map,
        )
        f(
            command.SeqProfileCrudCommand,
            self.crud_seq_profile,
        )
        f(
            command.SeqProfileIdentifierCrudCommand,
            self.crud_seq_profile_identifier,
        )
        f(
            command.LocusSetCrudCommand,
            self.crud_locus_set,
        )
        f(
            command.PcrMeasurementCrudCommand,
            self.crud_pcr_measurement,
        )
        f(
            command.ReadSetCrudCommand,
            self.crud_read_set,
        )
        f(
            command.ReadSetIdentifierCrudCommand,
            self.crud_read_set_identifier,
        )
        f(
            command.RefAlleleCrudCommand,
            self.crud_ref_allele,
        )
        f(
            command.RefSeqCrudCommand,
            self.crud_ref_seq,
        )
        f(
            command.SampleCrudCommand,
            self.crud_sample,
        )
        f(
            command.SampleDataCollectionLinkCrudCommand,
            self.crud_sample_data_collection_link,
        )
        f(
            command.SampleIdentifierCrudCommand,
            self.crud_sample_identifier,
        )
        f(
            command.SeqCrudCommand,
            self.crud_seq,
        )
        f(
            command.SeqCategoryCrudCommand,
            self.crud_seq_category,
        )
        f(
            command.SeqCategorySetCrudCommand,
            self.crud_seq_category_set,
        )
        f(
            command.SeqClassificationCrudCommand,
            self.crud_seq_classification,
        )
        f(
            command.SeqDistanceCrudCommand,
            self.crud_seq_distance,
        )
        f(
            command.SeqIdentifierCrudCommand,
            self.crud_seq_identifier,
        )
        f(
            command.SeqTaxonomyCrudCommand,
            self.crud_seq_taxonomy,
        )
        f(
            command.TaxonCrudCommand,
            self.crud_taxon,
        )
        f(
            command.TaxonSetCrudCommand,
            self.crud_taxon_set,
        )
        f(
            command.TaxonSetMemberCrudCommand,
            self.crud_taxon_set_member,
        )
        f(
            command.TreeAlgorithmCrudCommand,
            self.crud_tree_algorithm,
        )
        f(
            command.TreeAlgorithmClassCrudCommand,
            self.crud_tree_algorithm_class,
        )

    @abc.abstractmethod
    def calculate_phylogenetic_tree(
        self, cmd: command.CalculatePhylogeneticTreeCommand
    ) -> model.PhylogeneticTree | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_samples_by_id(
        self,
        cmd: command.RetrieveSamplesByIdCommand,
    ) -> list[model.FullSample]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_samples_by_query(
        self,
        cmd: command.RetrieveSamplesByQueryCommand,
    ) -> model.SampleQueryResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_seq_fasta(self, cmd: command.RetrieveSeqFastaCommand) -> Iterable[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_similar_profiles(
        self,
        cmd: command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_seq_distance_last_modified(
        self,
        cmd: command.RetrieveSeqDistanceLastModifiedCommand,
    ) -> datetime.datetime | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def calculate_seq_distances_for_new_profiles(
        self,
        cmd: command.CalculateSeqDistancesForNewProfilesCommand,
    ) -> list[model.CalculateSeqDistancesResult]:
        raise NotImplementedError()

    @abc.abstractmethod
    def update_seq_distances(
        self,
        cmd: command.UpdateSeqDistancesCommand,
    ) -> list[model.CalculateSeqDistancesResult]:
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_allele(
        self,
        cmd: command.AlleleCrudCommand,
    ) -> (
        model.Allele | list[model.Allele] | UUID | list[UUID] | bool | list[bool] | None
    ):
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_locus(
        self,
        cmd: command.LocusCrudCommand,
    ) -> model.Locus | list[model.Locus] | UUID | list[UUID] | bool | list[bool] | None:
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_ref_seq(
        self,
        cmd: command.RefSeqCrudCommand,
    ) -> (
        model.RefSeq | list[model.RefSeq] | UUID | list[UUID] | bool | list[bool] | None
    ):
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_sample(
        self,
        cmd: command.SampleCrudCommand,
    ) -> (
        model.Sample | list[model.Sample] | UUID | list[UUID] | bool | list[bool] | None
    ):
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_seq(
        self,
        cmd: command.SeqCrudCommand,
    ) -> model.Seq | list[model.Seq] | UUID | list[UUID] | bool | list[bool] | None:
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_taxon(
        self,
        cmd: command.TaxonCrudCommand,
    ) -> model.Taxon | list[model.Taxon] | UUID | list[UUID] | bool | list[bool] | None:
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()

    @abc.abstractmethod
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
        raise NotImplementedError()
