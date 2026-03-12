from gen_epix.commondb.domain.model import IdentifierForUpload as IdentifierForUpload

# pylint: disable=useless-import-alias
from gen_epix.seqdb.domain.model.seq.alignment import (
    AlignmentProtocol as AlignmentProtocol,
)
from gen_epix.seqdb.domain.model.seq.alignment import AlleleAlignment as AlleleAlignment
from gen_epix.seqdb.domain.model.seq.alignment import ContigAlignment as ContigAlignment
from gen_epix.seqdb.domain.model.seq.alignment import (
    MultipleAlignment as MultipleAlignment,
)
from gen_epix.seqdb.domain.model.seq.alignment import SeqAlignment as SeqAlignment
from gen_epix.seqdb.domain.model.seq.base import AlignmentMixin as AlignmentMixin
from gen_epix.seqdb.domain.model.seq.base import BaseSeq as BaseSeq
from gen_epix.seqdb.domain.model.seq.base import CodeMixin as CodeMixin
from gen_epix.seqdb.domain.model.seq.base import ProtocolMixin as ProtocolMixin
from gen_epix.seqdb.domain.model.seq.base import QualityMixin as QualityMixin
from gen_epix.seqdb.domain.model.seq.classification import (
    AstPrediction as AstPrediction,
)
from gen_epix.seqdb.domain.model.seq.classification import SeqCategory as SeqCategory
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqCategorySet as SeqCategorySet,
)
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqClassification as SeqClassification,
)
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqClassificationProtocol as SeqClassificationProtocol,
)
from gen_epix.seqdb.domain.model.seq.classification import SeqTaxonomy as SeqTaxonomy
from gen_epix.seqdb.domain.model.seq.classification import (
    TaxonomyProtocol as TaxonomyProtocol,
)
from gen_epix.seqdb.domain.model.seq.distance import SeqDistance as SeqDistance
from gen_epix.seqdb.domain.model.seq.distance import (
    SeqDistanceProtocol as SeqDistanceProtocol,
)
from gen_epix.seqdb.domain.model.seq.locus import Allele as Allele
from gen_epix.seqdb.domain.model.seq.locus import Locus as Locus
from gen_epix.seqdb.domain.model.seq.locus import LocusCodeMap as LocusCodeMap
from gen_epix.seqdb.domain.model.seq.locus import LocusSet as LocusSet
from gen_epix.seqdb.domain.model.seq.locus import RefAllele as RefAllele
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement as AstMeasurement
from gen_epix.seqdb.domain.model.seq.pheno import AstProtocol as AstProtocol
from gen_epix.seqdb.domain.model.seq.pheno import PcrMeasurement as PcrMeasurement
from gen_epix.seqdb.domain.model.seq.pheno import PcrProtocol as PcrProtocol
from gen_epix.seqdb.domain.model.seq.profile import AlleleProfile as AlleleProfile
from gen_epix.seqdb.domain.model.seq.profile import (
    AlleleProfileIdentifier as AlleleProfileIdentifier,
)
from gen_epix.seqdb.domain.model.seq.profile import (
    KmerDetectionProtocol as KmerDetectionProtocol,
)
from gen_epix.seqdb.domain.model.seq.profile import KmerProfile as KmerProfile
from gen_epix.seqdb.domain.model.seq.profile import (
    KmerProfileIdentifier as KmerProfileIdentifier,
)
from gen_epix.seqdb.domain.model.seq.profile import (
    LocusDetectionProtocol as LocusDetectionProtocol,
)
from gen_epix.seqdb.domain.model.seq.profile import LocusProfile as LocusProfile
from gen_epix.seqdb.domain.model.seq.profile import (
    LocusProfileIdentifier as LocusProfileIdentifier,
)
from gen_epix.seqdb.domain.model.seq.profile import (
    MlvaDetectionProtocol as MlvaDetectionProtocol,
)
from gen_epix.seqdb.domain.model.seq.profile import MlvaProfile as MlvaProfile
from gen_epix.seqdb.domain.model.seq.profile import (
    MlvaProfileIdentifier as MlvaProfileIdentifier,
)
from gen_epix.seqdb.domain.model.seq.profile import (
    SnpDetectionProtocol as SnpDetectionProtocol,
)
from gen_epix.seqdb.domain.model.seq.profile import SnpProfile as SnpProfile
from gen_epix.seqdb.domain.model.seq.profile import (
    SnpProfileIdentifier as SnpProfileIdentifier,
)
from gen_epix.seqdb.domain.model.seq.reads import ReadSet as ReadSet
from gen_epix.seqdb.domain.model.seq.reads import ReadSetIdentifier as ReadSetIdentifier
from gen_epix.seqdb.domain.model.seq.reads import (
    SequencingProtocol as SequencingProtocol,
)
from gen_epix.seqdb.domain.model.seq.sample import Sample as Sample
from gen_epix.seqdb.domain.model.seq.sample import (
    SampleDataCollectionLink as SampleDataCollectionLink,
)
from gen_epix.seqdb.domain.model.seq.sample import SampleIdentifier as SampleIdentifier
from gen_epix.seqdb.domain.model.seq.seq import AssemblyProtocol as AssemblyProtocol
from gen_epix.seqdb.domain.model.seq.seq import Contig as Contig
from gen_epix.seqdb.domain.model.seq.seq import RefSeq as RefSeq
from gen_epix.seqdb.domain.model.seq.seq import RefSnp as RefSnp
from gen_epix.seqdb.domain.model.seq.seq import RefSnpSet as RefSnpSet
from gen_epix.seqdb.domain.model.seq.seq import RefSnpSetMember as RefSnpSetMember
from gen_epix.seqdb.domain.model.seq.seq import Seq as Seq
from gen_epix.seqdb.domain.model.seq.seq import SeqIdentifier as SeqIdentifier
from gen_epix.seqdb.domain.model.seq.taxon import Taxon as Taxon
from gen_epix.seqdb.domain.model.seq.taxon import TaxonSet as TaxonSet
from gen_epix.seqdb.domain.model.seq.taxon import TaxonSetMember as TaxonSetMember
from gen_epix.seqdb.domain.model.seq.tree import PhylogeneticTree as PhylogeneticTree
from gen_epix.seqdb.domain.model.seq.tree import TreeAlgorithm as TreeAlgorithm
from gen_epix.seqdb.domain.model.seq.tree import (
    TreeAlgorithmClass as TreeAlgorithmClass,
)
from gen_epix.seqdb.domain.model.seq.upload import AlleleForUpload as AlleleForUpload
from gen_epix.seqdb.domain.model.seq.upload import (
    AlleleProfileForUpload as AlleleProfileForUpload,
)
from gen_epix.seqdb.domain.model.seq.upload import (
    CalculateSeqDistancesResult as CalculateSeqDistancesResult,
)
from gen_epix.seqdb.domain.model.seq.upload import (
    KmerProfileForUpload as KmerProfileForUpload,
)
from gen_epix.seqdb.domain.model.seq.upload import (
    MlvaProfileForUpload as MlvaProfileForUpload,
)
from gen_epix.seqdb.domain.model.seq.upload import ReadSetForUpload as ReadSetForUpload
from gen_epix.seqdb.domain.model.seq.upload import (
    SampleBatchForUpload as SampleBatchForUpload,
)
from gen_epix.seqdb.domain.model.seq.upload import (
    SampleBatchUploadResult as SampleBatchUploadResult,
)
from gen_epix.seqdb.domain.model.seq.upload import SampleDataIssue as SampleDataIssue
from gen_epix.seqdb.domain.model.seq.upload import SampleForUpload as SampleForUpload
from gen_epix.seqdb.domain.model.seq.upload import (
    SampleUploadResult as SampleUploadResult,
)
from gen_epix.seqdb.domain.model.seq.upload import SeqForUpload as SeqForUpload
from gen_epix.seqdb.domain.model.seq.upload import (
    SnpProfileForUpload as SnpProfileForUpload,
)
from gen_epix.seqdb.domain.model.seq.protocol import Protocol as Protocol
