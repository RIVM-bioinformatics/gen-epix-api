from test.seqdb.seqdb_test_client import SeqdbTestClient, SeqGenerationSettings

from gen_epix.seqdb.domain import model
import pytest


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestGenerateSequences:

    def test_generate_sequences_happy_flow(self) -> None:
        settings = SeqGenerationSettings(
            n_loci=5,
            locus_length=20,
            p_locus_deletion=0.01,
            p_nucleotide_substitution=0.02,
            p_nucleotide_deletion=0.005,
            seed=1001,
        )
        batch = SeqdbTestClient.generate_random_sequences(
            n_seqs=10,
            settings=settings,
        )

        assert isinstance(batch, model.SampleBatchForUpload)
        assert len(batch.samples) == 10
        assert all(
            isinstance(sample, model.SampleForUpload) for sample in batch.samples
        )

    def test_generate_sequences_reproducibility(self) -> None:
        settings = SeqGenerationSettings(
            n_loci=5,
            locus_length=20,
            p_locus_deletion=0.01,
            p_nucleotide_substitution=0.02,
            p_nucleotide_deletion=0.005,
            seed=1001,
        )
        batch1 = SeqdbTestClient.generate_random_sequences(
            n_seqs=10,
            settings=settings,
        )
        batch2 = SeqdbTestClient.generate_random_sequences(
            n_seqs=10,
            settings=settings,
        )

        seqs1 = [
            contig.seq
            for sample in batch1.samples
            for seq in (sample.seqs or [])
            for contig in getattr(seq, "contigs", [])
        ]

        seqs2 = [
            contig.seq
            for sample in batch2.samples
            for seq in (sample.seqs or [])
            for contig in getattr(seq, "contigs", [])
        ]

        assert seqs1 == seqs2

    def test_generate_sequences_uniqueness(self) -> None:
        settings1 = SeqGenerationSettings(
            n_loci=5,
            locus_length=20,
            seed=1001,
        )
        batch1 = SeqdbTestClient.generate_random_sequences(
            n_seqs=5,
            settings=settings1,
        )
        settings2 = SeqGenerationSettings(
            n_loci=5,
            locus_length=20,
            seed=1002,
        )
        batch2 = SeqdbTestClient.generate_random_sequences(
            n_seqs=5,
            settings=settings2,
        )

        seqs1 = [
            contig.seq
            for sample in batch1.samples
            for seq in (sample.seqs or [])
            for contig in getattr(seq, "contigs", [])
        ]

        seqs2 = [
            contig.seq
            for sample in batch2.samples
            for seq in (sample.seqs or [])
            for contig in getattr(seq, "contigs", [])
        ]

        assert seqs1 != seqs2
