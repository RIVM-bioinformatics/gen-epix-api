from gen_epix.seqdb.domain.model import SampleSetForUpload, SampleForUpload, SeqForUpload
from gen_epix.seqdb.domain.model.seq.seq import Contig
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from uuid import UUID, uuid4


sample_set = SampleSetForUpload(
    samples=[
        SampleForUpload(
            external_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_code="LAB_001",
                    identifier="SAMPLE_001"
                )
            ],
            seqs=[
                SeqForUpload(
                    sample_id=uuid4(), # Add?
                    code="seq_001_single",
                    contigs=[
                        Contig(seq="atcgatcgtagctagcatcgatcgtagctagcatcgatcgtagctagc")
                    ]
                )
            ],
            created_in_data_collection_id=UUID("11111111-2222-3333-4444-555555555555"),
            data_collection_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_id=uuid4()
                    ), 
                ExternalIdentifierForUpload(
                    identifier_issuer_id=uuid4()
                    )
                ], # Add?
            #external_ids=[ExternalIdentifierForUpload(), ExternalIdentifierForUpload()] # Add?
        ),
        SampleForUpload(
            external_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_code="LAB_002",
                    identifier="SAMPLE_002"
                )
            ],
            seqs=[
                SeqForUpload(
                    sample_id=uuid4(), # Add?
                    code="seq_002_double",
                    contigs=[
                        Contig(seq="gctagcatcgatcgtagctagcatcgatcgtagctagcatcgatcgat"),
                        Contig(seq="cgatcgtagctagcatcgatcgtagctagcatcgatcgtagctagcac")
                    ]
                )
            ],
            created_in_data_collection_id=UUID("22222222-3333-4444-5555-666666666666")
        ),
        SampleForUpload(
            external_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_code="LAB_003",
                    identifier="SAMPLE_003"
                )
            ],
            seqs=[
                SeqForUpload(
                    sample_id=uuid4(), # Add?
                    code="seq_003a_single",
                    contigs=[
                        Contig(seq="tagctagcatcgatcgtagctagcatcgatcgtagctagcatcgatcg")
                    ]
                ),
                SeqForUpload(
                    sample_id=uuid4(), # Add?
                    code="seq_003b_single",
                    contigs=[
                        Contig(seq="gatcgtagctagcatcgatcgtagctagcatcgatcgtagctagcatc")
                    ]
                )
            ],
            created_in_data_collection_id=UUID("33333333-4444-5555-6666-777777777777")
        ),
        SampleForUpload(
            external_ids=[
                ExternalIdentifierForUpload(
                    identifier_issuer_code="LAB_004",
                    identifier="SAMPLE_004"
                )
            ],
            seqs=[
                SeqForUpload(
                    sample_id=uuid4(), # Add?
                    code="seq_004a_double",
                    contigs=[
                        Contig(seq="tcgtagctagcatcgatcgtagctagcatcgatcgtagctagcatcga"),
                        Contig(seq="agctagcatcgatcgtagctagcatcgatcgtagctagcatcgatcgt")
                    ]
                ),
                SeqForUpload(
                    sample_id=uuid4(), # Add?
                    code="seq_004b_double",
                    contigs=[
                        Contig(seq="ctagcatcgatcgtagctagcatcgatcgtagctagcatcgatcgtag"),
                        Contig(seq="atcgatcgtagctagcatcgatcgtagctagcatcgatcgtagctagc")
                    ]
                )
            ],
            created_in_data_collection_id=UUID("44444444-5555-6666-7777-888888888888")
        )
    ]
    # alleles = [AlleleForUpload(...), AlleleForUpload(...)] Add?
)

sample_set_json = sample_set.model_dump_json()
print(sample_set_json)

# TODO: fill SeqForUpload, SampleForUpload, and SampleSetForUpload with iRODS data
# TODO: integrage this with cgmlst code on GitLab/update cgmlst code to models -> gen_epix_api needed