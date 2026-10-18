"""Verify the abstract seqdb sequence-service handler contract."""

import inspect
from test.util.mock_compat import MagicMock, call

from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def test_register_handlers_binds_sequence_commands_to_service_methods():
    """Register each sequence-specific command with its matching method."""
    service = MagicMock(spec=BaseSeqService)
    app = MagicMock()
    service.app = app

    BaseSeqService.register_handlers(service)

    expected_handlers = [
        (command.CalculatePhylogeneticTreeCommand, "calculate_phylogenetic_tree"),
        (command.RetrieveSamplesByQueryCommand, "retrieve_samples_by_query"),
        (command.RetrieveSamplesByIdCommand, "retrieve_samples_by_id"),
        (
            command.RetrieveSampleIdentifiersByIdCommand,
            "retrieve_sample_identifiers_by_id",
        ),
        (
            command.RetrieveSeqDistancesBySeqProfilesCommand,
            "retrieve_seq_distances_by_seq_profiles",
        ),
        (command.RetrieveSeqFastaCommand, "retrieve_seq_fasta"),
        (command.ConvertSeqFormatCommand, "convert_seq_format"),
        (command.UploadSamplesCommand, "upload_samples"),
        (command.RetrieveSimilarProfilesCommand, "retrieve_similar_profiles"),
        (
            command.RetrieveSeqDistanceLastModifiedCommand,
            "retrieve_seq_distance_last_modified",
        ),
        (
            command.CalculateSeqDistancesForNewProfilesCommand,
            "calculate_seq_distances_for_new_profiles",
        ),
        (command.UpdateSeqDistancesCommand, "update_seq_distances"),
        (command.RetrieveBestSeqPerSampleCommand, "retrieve_best_seq_per_sample"),
        (
            command.RetrieveBestSeqProfilePerSampleCommand,
            "retrieve_best_seq_profile_per_sample",
        ),
        (
            command.RetrieveBestSeqClassificationPerSampleCommand,
            "retrieve_best_seq_classification_per_sample",
        ),
        (command.ProtocolCrudCommand, "crud_protocol"),
        (command.ProtocolSetCrudCommand, "crud_protocol_set"),
        (command.ProtocolSetMemberCrudCommand, "crud_protocol_set_member"),
        (command.AlleleCrudCommand, "crud_allele"),
        (command.AstMeasurementCrudCommand, "crud_ast_measurement"),
        (command.AstPredictionCrudCommand, "crud_ast_prediction"),
        (command.LocusCrudCommand, "crud_locus"),
        (command.LocusCodeMapCrudCommand, "crud_locus_code_map"),
        (command.SeqProfileCrudCommand, "crud_seq_profile"),
        (command.SeqProfileIdentifierCrudCommand, "crud_seq_profile_identifier"),
        (command.LocusSetCrudCommand, "crud_locus_set"),
        (command.PcrMeasurementCrudCommand, "crud_pcr_measurement"),
        (command.ReadSetCrudCommand, "crud_read_set"),
        (command.ReadSetIdentifierCrudCommand, "crud_read_set_identifier"),
        (command.RefAlleleCrudCommand, "crud_ref_allele"),
        (command.RefSeqCrudCommand, "crud_ref_seq"),
        (command.SampleCrudCommand, "crud_sample"),
        (
            command.SampleDataCollectionLinkCrudCommand,
            "crud_sample_data_collection_link",
        ),
        (command.SampleIdentifierCrudCommand, "crud_sample_identifier"),
        (command.SeqCrudCommand, "crud_seq"),
        (command.SeqCategoryCrudCommand, "crud_seq_category"),
        (command.SeqCategorySetCrudCommand, "crud_seq_category_set"),
        (command.SeqClassificationCrudCommand, "crud_seq_classification"),
        (command.SeqDistanceCrudCommand, "crud_seq_distance"),
        (command.SeqIdentifierCrudCommand, "crud_seq_identifier"),
        (command.SeqTaxonomyCrudCommand, "crud_seq_taxonomy"),
        (command.TaxonCrudCommand, "crud_taxon"),
        (command.TaxonSetCrudCommand, "crud_taxon_set"),
        (command.TaxonSetMemberCrudCommand, "crud_taxon_set_member"),
        (command.TreeAlgorithmCrudCommand, "crud_tree_algorithm"),
        (command.TreeAlgorithmClassCrudCommand, "crud_tree_algorithm_class"),
    ]

    service.register_default_crud_handlers.assert_called_once_with()
    assert app.register_handler.call_args_list == [
        call(command_type, getattr(service, method_name))
        for command_type, method_name in expected_handlers
    ]


def test_base_seq_service_remains_abstract():
    """Keep sequence operations abstract on the shared base service."""
    assert inspect.isabstract(BaseSeqService)
