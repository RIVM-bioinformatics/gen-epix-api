"""Define seqdb domain interfaces and policies for domain.service.seq."""

import abc
import datetime
from collections.abc import Iterable
from uuid import UUID

from gen_epix.fastapp import BaseService
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.enum import ServiceType


class BaseSeqService(BaseService):
    """Define seqdb command handlers implemented by concrete sequence services."""

    SERVICE_TYPE = ServiceType.SEQ

    def register_handlers(self) -> None:
        """Register default CRUD and seqdb-specific sequence command handlers."""
        f = self.app.register_handler
        self.register_default_crud_handlers()
        f(
            command.CalculatePhylogeneticTreeCommand,
            self.calculate_phylogenetic_tree,
        )
        f(command.RetrieveSamplesByQueryCommand, self.retrieve_samples_by_query)
        f(command.RetrieveSamplesByIdCommand, self.retrieve_samples_by_id)
        f(
            command.RetrieveSampleIdentifiersByIdCommand,
            self.retrieve_sample_identifiers_by_id,
        )
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
            command.RetrieveBestSeqPerSampleCommand,
            self.retrieve_best_seq_per_sample,
        )
        f(
            command.RetrieveBestSeqProfilePerSampleCommand,
            self.retrieve_best_seq_profile_per_sample,
        )
        f(
            command.RetrieveBestSeqClassificationPerSampleCommand,
            self.retrieve_best_seq_classification_per_sample,
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
        """Calculate a phylogenetic tree.

        Args:
            cmd: Tree-calculation command to execute.

        Returns:
            The calculated tree, if one can be produced.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_samples_by_id(
        self,
        cmd: command.RetrieveSamplesByIdCommand,
    ) -> list[model.FullSample]:
        """Retrieve complete samples by identifier.

        Args:
            cmd: Sample-retrieval command to execute.

        Returns:
            Complete samples matching the command identifiers.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_sample_identifiers_by_id(
        self,
        cmd: command.RetrieveSampleIdentifiersByIdCommand,
    ) -> list[model.SampleIdentifier]:
        """Retrieve identifiers associated with samples.

        Args:
            cmd: Sample-identifier retrieval command to execute.

        Returns:
            Identifiers linked to the requested samples.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_samples_by_query(
        self,
        cmd: command.RetrieveSamplesByQueryCommand,
    ) -> model.SampleQueryResult:
        """Retrieve samples matching a query.

        Args:
            cmd: Sample-query command to execute.

        Returns:
            Matching sample identifiers and result-limit information.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_seq_fasta(self, cmd: command.RetrieveSeqFastaCommand) -> Iterable[str]:
        """Stream sequence data in FASTA format.

        Args:
            cmd: FASTA-retrieval command to execute.

        Returns:
            FASTA text chunks.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        """Upload a batch of samples.

        Args:
            cmd: Sample-upload command to execute.

        Returns:
            Per-sample upload results and data issues.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_similar_profiles(
        self,
        cmd: command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        """Retrieve profiles similar to the command's source profiles.

        Args:
            cmd: Similar-profile retrieval command to execute.

        Returns:
            Similar profile identifiers.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_seq_distance_last_modified(
        self,
        cmd: command.RetrieveSeqDistanceLastModifiedCommand,
    ) -> datetime.datetime | None:
        """Retrieve the latest sequence-distance modification time.

        Args:
            cmd: Last-modified retrieval command to execute.

        Returns:
            Latest modification time, if distance records exist.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def calculate_seq_distances_for_new_profiles(
        self,
        cmd: command.CalculateSeqDistancesForNewProfilesCommand,
    ) -> list[model.CalculateSeqDistancesResult]:
        """Calculate distances for profiles without distance records.

        Args:
            cmd: New-profile distance-calculation command to execute.

        Returns:
            Results for processed profiling protocols.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def update_seq_distances(
        self,
        cmd: command.UpdateSeqDistancesCommand,
    ) -> list[model.CalculateSeqDistancesResult]:
        """Update stored sequence-distance calculations.

        Args:
            cmd: Distance-update command to execute.

        Returns:
            Results for processed profiling protocols.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_best_seq_per_sample(
        self,
        cmd: command.RetrieveBestSeqPerSampleCommand,
    ) -> dict[UUID, UUID]:
        """Retrieve the best sequence selected for each sample.

        Args:
            cmd: Best-sequence retrieval command to execute.

        Returns:
            Mapping from sample IDs to sequence IDs.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_best_seq_profile_per_sample(
        self,
        cmd: command.RetrieveBestSeqProfilePerSampleCommand,
    ) -> dict[UUID, UUID]:
        """Retrieve the best sequence profile selected for each sample.

        Args:
            cmd: Best-profile retrieval command to execute.

        Returns:
            Mapping from sample IDs to sequence-profile IDs.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_best_seq_classification_per_sample(
        self,
        cmd: command.RetrieveBestSeqClassificationPerSampleCommand,
    ) -> dict[UUID, UUID]:
        """Retrieve the best sequence classification selected for each sample.

        Args:
            cmd: Best-classification retrieval command to execute.

        Returns:
            Mapping from sample IDs to sequence-classification IDs.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for protocol entities.

        Args:
            cmd: Typed protocol CRUD command to execute.

        Returns:
            The action-specific protocol result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for protocol-set entities.

        Args:
            cmd: Typed protocol-set CRUD command to execute.

        Returns:
            The action-specific protocol-set result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for protocol-set membership entities.

        Args:
            cmd: Typed protocol-set-member CRUD command to execute.

        Returns:
            The action-specific protocol-set-member result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_allele(
        self,
        cmd: command.AlleleCrudCommand,
    ) -> (
        model.Allele | list[model.Allele] | UUID | list[UUID] | bool | list[bool] | None
    ):
        """Handle a CRUD command for allele entities.

        Args:
            cmd: Typed allele CRUD command to execute.

        Returns:
            The action-specific allele result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for AST measurement entities.

        Args:
            cmd: Typed AST-measurement CRUD command to execute.

        Returns:
            The action-specific AST-measurement result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for AST prediction entities.

        Args:
            cmd: Typed AST-prediction CRUD command to execute.

        Returns:
            The action-specific AST-prediction result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_locus(
        self,
        cmd: command.LocusCrudCommand,
    ) -> model.Locus | list[model.Locus] | UUID | list[UUID] | bool | list[bool] | None:
        """Handle a CRUD command for locus entities.

        Args:
            cmd: Typed locus CRUD command to execute.

        Returns:
            The action-specific locus result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for locus-code-map entities.

        Args:
            cmd: Typed locus-code-map CRUD command to execute.

        Returns:
            The action-specific locus-code-map result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-profile entities.

        Args:
            cmd: Typed sequence-profile CRUD command to execute.

        Returns:
            The action-specific sequence-profile result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-profile identifier entities.

        Args:
            cmd: Typed sequence-profile-identifier CRUD command to execute.

        Returns:
            The action-specific sequence-profile-identifier result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for locus-set entities.

        Args:
            cmd: Typed locus-set CRUD command to execute.

        Returns:
            The action-specific locus-set result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for PCR measurement entities.

        Args:
            cmd: Typed PCR-measurement CRUD command to execute.

        Returns:
            The action-specific PCR-measurement result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for read-set entities.

        Args:
            cmd: Typed read-set CRUD command to execute.

        Returns:
            The action-specific read-set result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for read-set identifier entities.

        Args:
            cmd: Typed read-set-identifier CRUD command to execute.

        Returns:
            The action-specific read-set-identifier result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for reference-allele entities.

        Args:
            cmd: Typed reference-allele CRUD command to execute.

        Returns:
            The action-specific reference-allele result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_ref_seq(
        self,
        cmd: command.RefSeqCrudCommand,
    ) -> (
        model.RefSeq | list[model.RefSeq] | UUID | list[UUID] | bool | list[bool] | None
    ):
        """Handle a CRUD command for reference-sequence entities.

        Args:
            cmd: Typed reference-sequence CRUD command to execute.

        Returns:
            The action-specific reference-sequence result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_sample(
        self,
        cmd: command.SampleCrudCommand,
    ) -> (
        model.Sample | list[model.Sample] | UUID | list[UUID] | bool | list[bool] | None
    ):
        """Handle a CRUD command for sample entities.

        Args:
            cmd: Typed sample CRUD command to execute.

        Returns:
            The action-specific sample result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sample-data-collection link entities.

        Args:
            cmd: Typed sample-data-collection-link CRUD command to execute.

        Returns:
            The action-specific sample-data-collection-link result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sample identifier entities.

        Args:
            cmd: Typed sample-identifier CRUD command to execute.

        Returns:
            The action-specific sample-identifier result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_seq(
        self,
        cmd: command.SeqCrudCommand,
    ) -> model.Seq | list[model.Seq] | UUID | list[UUID] | bool | list[bool] | None:
        """Handle a CRUD command for sequence entities.

        Args:
            cmd: Typed sequence CRUD command to execute.

        Returns:
            The action-specific sequence result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-category entities.

        Args:
            cmd: Typed sequence-category CRUD command to execute.

        Returns:
            The action-specific sequence-category result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-category-set entities.

        Args:
            cmd: Typed sequence-category-set CRUD command to execute.

        Returns:
            The action-specific sequence-category-set result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-classification entities.

        Args:
            cmd: Typed sequence-classification CRUD command to execute.

        Returns:
            The action-specific sequence-classification result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-distance entities.

        Args:
            cmd: Typed sequence-distance CRUD command to execute.

        Returns:
            The action-specific sequence-distance result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-identifier entities.

        Args:
            cmd: Typed sequence-identifier CRUD command to execute.

        Returns:
            The action-specific sequence-identifier result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for sequence-taxonomy entities.

        Args:
            cmd: Typed sequence-taxonomy CRUD command to execute.

        Returns:
            The action-specific sequence-taxonomy result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def crud_taxon(
        self,
        cmd: command.TaxonCrudCommand,
    ) -> model.Taxon | list[model.Taxon] | UUID | list[UUID] | bool | list[bool] | None:
        """Handle a CRUD command for taxon entities.

        Args:
            cmd: Typed taxon CRUD command to execute.

        Returns:
            The action-specific taxon result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for taxon-set entities.

        Args:
            cmd: Typed taxon-set CRUD command to execute.

        Returns:
            The action-specific taxon-set result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for taxon-set membership entities.

        Args:
            cmd: Typed taxon-set-member CRUD command to execute.

        Returns:
            The action-specific taxon-set-member result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for tree-algorithm entities.

        Args:
            cmd: Typed tree-algorithm CRUD command to execute.

        Returns:
            The action-specific tree-algorithm result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
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
        """Handle a CRUD command for tree-algorithm-class entities.

        Args:
            cmd: Typed tree-algorithm-class CRUD command to execute.

        Returns:
            The action-specific tree-algorithm-class result.

        Raises:
            NotImplementedError: Always, until a concrete sequence service implements it.
        """
        raise NotImplementedError()
