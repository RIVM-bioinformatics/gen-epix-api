# pylint: disable=useless-import-alias
from gen_epix.commondb.repositories.sa_model import Contact as Contact
from gen_epix.commondb.repositories.sa_model import DataCollection as DataCollection
from gen_epix.commondb.repositories.sa_model import (
    DataCollectionSet as DataCollectionSet,
)
from gen_epix.commondb.repositories.sa_model import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.repositories.sa_model import IdentifierIssuer as IdentifierIssuer
from gen_epix.commondb.repositories.sa_model import Organization as Organization
from gen_epix.commondb.repositories.sa_model import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.commondb.repositories.sa_model import OrganizationSet as OrganizationSet
from gen_epix.commondb.repositories.sa_model import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.repositories.sa_model import Outage as Outage
from gen_epix.commondb.repositories.sa_model import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model import Site as Site
from gen_epix.commondb.repositories.sa_model import User as User
from gen_epix.commondb.repositories.sa_model import UserInvitation as UserInvitation
from gen_epix.commondb.repositories.sa_model import (
    create_field_metadata,
    set_entity_repository_model_classes,
)
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.repositories.sa_model.file import File as File
from gen_epix.seqdb.repositories.sa_model.seq import (
    AlignmentProtocol as AlignmentProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import Allele as Allele
from gen_epix.seqdb.repositories.sa_model.seq import AlleleAlignment as AlleleAlignment
from gen_epix.seqdb.repositories.sa_model.seq import AlleleProfile as AlleleProfile
from gen_epix.seqdb.repositories.sa_model.seq import (
    AssemblyProtocol as AssemblyProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import AstMeasurement as AstMeasurement
from gen_epix.seqdb.repositories.sa_model.seq import AstPrediction as AstPrediction
from gen_epix.seqdb.repositories.sa_model.seq import AstProtocol as AstProtocol
from gen_epix.seqdb.repositories.sa_model.seq import (
    KmerDetectionProtocol as KmerDetectionProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import KmerProfile as KmerProfile
from gen_epix.seqdb.repositories.sa_model.seq import Locus as Locus
from gen_epix.seqdb.repositories.sa_model.seq import LocusCode as LocusCode
from gen_epix.seqdb.repositories.sa_model.seq import (
    LocusDetectionProtocol as LocusDetectionProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import LocusProfile as LocusProfile
from gen_epix.seqdb.repositories.sa_model.seq import LocusSet as LocusSet
from gen_epix.seqdb.repositories.sa_model.seq import (
    MlvaDetectionProtocol as MlvaDetectionProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import MlvaProfile as MlvaProfile
from gen_epix.seqdb.repositories.sa_model.seq import PcrMeasurement as PcrMeasurement
from gen_epix.seqdb.repositories.sa_model.seq import PcrProtocol as PcrProtocol
from gen_epix.seqdb.repositories.sa_model.seq import RawSeq as RawSeq
from gen_epix.seqdb.repositories.sa_model.seq import ReadSet as ReadSet
from gen_epix.seqdb.repositories.sa_model.seq import RefAllele as RefAllele
from gen_epix.seqdb.repositories.sa_model.seq import RefSeq as RefSeq
from gen_epix.seqdb.repositories.sa_model.seq import RefSnp as RefSnp
from gen_epix.seqdb.repositories.sa_model.seq import RefSnpSet as RefSnpSet
from gen_epix.seqdb.repositories.sa_model.seq import RefSnpSetMember as RefSnpSetMember
from gen_epix.seqdb.repositories.sa_model.seq import Sample as Sample
from gen_epix.seqdb.repositories.sa_model.seq import (
    SampleDataCollectionLink as SampleDataCollectionLink,
)
from gen_epix.seqdb.repositories.sa_model.seq import (
    SampleIdentifier as SampleIdentifier,
)
from gen_epix.seqdb.repositories.sa_model.seq import Seq as Seq
from gen_epix.seqdb.repositories.sa_model.seq import SeqAlignment as SeqAlignment
from gen_epix.seqdb.repositories.sa_model.seq import SeqCategory as SeqCategory
from gen_epix.seqdb.repositories.sa_model.seq import SeqCategorySet as SeqCategorySet
from gen_epix.seqdb.repositories.sa_model.seq import (
    SeqClassification as SeqClassification,
)
from gen_epix.seqdb.repositories.sa_model.seq import (
    SeqClassificationProtocol as SeqClassificationProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import SeqDistance as SeqDistance
from gen_epix.seqdb.repositories.sa_model.seq import (
    SeqDistanceProtocol as SeqDistanceProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import SeqTaxonomy as SeqTaxonomy
from gen_epix.seqdb.repositories.sa_model.seq import (
    SequencingProtocol as SequencingProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import (
    SnpDetectionProtocol as SnpDetectionProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import SnpProfile as SnpProfile
from gen_epix.seqdb.repositories.sa_model.seq import Taxon as Taxon
from gen_epix.seqdb.repositories.sa_model.seq import TaxonLocusLink as TaxonLocusLink
from gen_epix.seqdb.repositories.sa_model.seq import (
    TaxonomyProtocol as TaxonomyProtocol,
)
from gen_epix.seqdb.repositories.sa_model.seq import TaxonSet as TaxonSet
from gen_epix.seqdb.repositories.sa_model.seq import TaxonSetMember as TaxonSetMember
from gen_epix.seqdb.repositories.sa_model.seq import TreeAlgorithm as TreeAlgorithm
from gen_epix.seqdb.repositories.sa_model.seq import (
    TreeAlgorithmClass as TreeAlgorithmClass,
)

SA_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, dict[type[model.Model], type]] = {
    enum.ServiceType.ABAC: {
        model.OrganizationAdminPolicy: OrganizationAdminPolicy,
    },
    enum.ServiceType.ORGANIZATION: {
        model.Contact: Contact,
        model.DataCollection: DataCollection,
        model.DataCollectionSet: DataCollectionSet,
        model.DataCollectionSetMember: DataCollectionSetMember,
        model.IdentifierIssuer: IdentifierIssuer,
        model.Organization: Organization,
        model.OrganizationSet: OrganizationSet,
        model.OrganizationSetMember: OrganizationSetMember,
        model.Site: Site,
        model.User: User,
        model.UserInvitation: UserInvitation,
    },
    enum.ServiceType.SYSTEM: {
        model.Outage: Outage,
    },
    enum.ServiceType.SEQ: {
        model.AlignmentProtocol: AlignmentProtocol,
        model.Allele: Allele,
        model.AlleleAlignment: AlleleAlignment,
        model.AlleleProfile: AlleleProfile,
        model.AssemblyProtocol: AssemblyProtocol,
        model.AstMeasurement: AstMeasurement,
        model.AstPrediction: AstPrediction,
        model.AstProtocol: AstProtocol,
        model.KmerDetectionProtocol: KmerDetectionProtocol,
        model.KmerProfile: KmerProfile,
        model.SequencingProtocol: SequencingProtocol,
        model.Locus: Locus,
        model.LocusCode: LocusCode,
        model.LocusDetectionProtocol: LocusDetectionProtocol,
        model.LocusProfile: LocusProfile,
        model.LocusSet: LocusSet,
        model.MlvaDetectionProtocol: MlvaDetectionProtocol,
        model.MlvaProfile: MlvaProfile,
        model.PcrMeasurement: PcrMeasurement,
        model.PcrProtocol: PcrProtocol,
        model.RawSeq: RawSeq,
        model.ReadSet: ReadSet,
        model.RefAllele: RefAllele,
        model.RefSeq: RefSeq,
        model.RefSnp: RefSnp,
        model.RefSnpSet: RefSnpSet,
        model.RefSnpSetMember: RefSnpSetMember,
        model.Sample: Sample,
        model.SampleDataCollectionLink: SampleDataCollectionLink,
        model.SampleIdentifier: SampleIdentifier,
        model.Seq: Seq,
        model.SeqAlignment: SeqAlignment,
        model.SeqCategory: SeqCategory,
        model.SeqCategorySet: SeqCategorySet,
        model.SeqClassification: SeqClassification,
        model.SeqClassificationProtocol: SeqClassificationProtocol,
        model.SeqDistance: SeqDistance,
        model.SeqDistanceProtocol: SeqDistanceProtocol,
        model.SeqTaxonomy: SeqTaxonomy,
        model.SnpDetectionProtocol: SnpDetectionProtocol,
        model.SnpProfile: SnpProfile,
        model.Taxon: Taxon,
        model.TaxonLocusLink: TaxonLocusLink,
        model.TaxonomyProtocol: TaxonomyProtocol,
        model.TaxonSet: TaxonSet,
        model.TaxonSetMember: TaxonSetMember,
        model.TreeAlgorithm: TreeAlgorithm,
        model.TreeAlgorithmClass: TreeAlgorithmClass,
    },
    enum.ServiceType.FILE: {
        model.File: File,
    },
}

FIELD_NAME_MAP: dict[type, dict[str, str]] = {}

set_entity_repository_model_classes(
    DOMAIN,
    SA_MODELS_BY_SERVICE_TYPE,
    RowMetadataMixin,
    field_name_map=FIELD_NAME_MAP,
)

SERVICE_METADATA_FIELDS, DB_METADATA_FIELDS, GENERATE_SERVICE_METADATA = (
    create_field_metadata(DOMAIN)
)
