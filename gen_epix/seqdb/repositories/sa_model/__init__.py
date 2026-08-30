# pylint: disable=useless-import-alias
"""Re-export SQLAlchemy persistence models registered for SeqDB entities."""

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
from gen_epix.commondb.repositories.sa_model import (
    OrganizationIdentifierIssuerLink as OrganizationIdentifierIssuerLink,
)
from gen_epix.commondb.repositories.sa_model import OrganizationSet as OrganizationSet
from gen_epix.commondb.repositories.sa_model import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.repositories.sa_model import Outage as Outage
from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
)
from gen_epix.commondb.repositories.sa_model import Site as Site
from gen_epix.commondb.repositories.sa_model import User as User
from gen_epix.commondb.repositories.sa_model import UserInvitation as UserInvitation
from gen_epix.commondb.repositories.sa_model import (
    set_entity_repository_model_classes,
)
from gen_epix.seqdb.domain import DOMAIN, enum, model
from gen_epix.seqdb.repositories.sa_model.file import File as File
from gen_epix.seqdb.repositories.sa_model.seq import Allele as Allele
from gen_epix.seqdb.repositories.sa_model.seq import AstMeasurement as AstMeasurement
from gen_epix.seqdb.repositories.sa_model.seq import AstPrediction as AstPrediction
from gen_epix.seqdb.repositories.sa_model.seq import Locus as Locus
from gen_epix.seqdb.repositories.sa_model.seq import LocusCodeMap as LocusCodeMap
from gen_epix.seqdb.repositories.sa_model.seq import LocusSet as LocusSet
from gen_epix.seqdb.repositories.sa_model.seq import PcrMeasurement as PcrMeasurement
from gen_epix.seqdb.repositories.sa_model.seq import Protocol as Protocol
from gen_epix.seqdb.repositories.sa_model.seq import ProtocolSet as ProtocolSet
from gen_epix.seqdb.repositories.sa_model.seq import (
    ProtocolSetMember as ProtocolSetMember,
)
from gen_epix.seqdb.repositories.sa_model.seq import ReadSet as ReadSet
from gen_epix.seqdb.repositories.sa_model.seq import (
    ReadSetIdentifier as ReadSetIdentifier,
)
from gen_epix.seqdb.repositories.sa_model.seq import RefAllele as RefAllele
from gen_epix.seqdb.repositories.sa_model.seq import RefSeq as RefSeq
from gen_epix.seqdb.repositories.sa_model.seq import Sample as Sample
from gen_epix.seqdb.repositories.sa_model.seq import (
    SampleDataCollectionLink as SampleDataCollectionLink,
)
from gen_epix.seqdb.repositories.sa_model.seq import (
    SampleIdentifier as SampleIdentifier,
)
from gen_epix.seqdb.repositories.sa_model.seq import Seq as Seq
from gen_epix.seqdb.repositories.sa_model.seq import SeqCategory as SeqCategory
from gen_epix.seqdb.repositories.sa_model.seq import SeqCategorySet as SeqCategorySet
from gen_epix.seqdb.repositories.sa_model.seq import (
    SeqClassification as SeqClassification,
)
from gen_epix.seqdb.repositories.sa_model.seq import SeqDistance as SeqDistance
from gen_epix.seqdb.repositories.sa_model.seq import SeqIdentifier as SeqIdentifier
from gen_epix.seqdb.repositories.sa_model.seq import SeqProfile as SeqProfile
from gen_epix.seqdb.repositories.sa_model.seq import (
    SeqProfileIdentifier as SeqProfileIdentifier,
)
from gen_epix.seqdb.repositories.sa_model.seq import SeqTaxonomy as SeqTaxonomy
from gen_epix.seqdb.repositories.sa_model.seq import Taxon as Taxon
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
        model.OrganizationIdentifierIssuerLink: OrganizationIdentifierIssuerLink,
    },
    enum.ServiceType.SYSTEM: {
        model.Outage: Outage,
    },
    enum.ServiceType.SEQ: {
        model.Allele: Allele,
        model.AstMeasurement: AstMeasurement,
        model.AstPrediction: AstPrediction,
        model.Locus: Locus,
        model.LocusCodeMap: LocusCodeMap,
        model.LocusSet: LocusSet,
        model.PcrMeasurement: PcrMeasurement,
        model.Protocol: Protocol,
        model.ProtocolSet: ProtocolSet,
        model.ProtocolSetMember: ProtocolSetMember,
        model.ReadSet: ReadSet,
        model.ReadSetIdentifier: ReadSetIdentifier,
        model.RefAllele: RefAllele,
        model.RefSeq: RefSeq,
        model.Sample: Sample,
        model.SampleDataCollectionLink: SampleDataCollectionLink,
        model.SampleIdentifier: SampleIdentifier,
        model.Seq: Seq,
        model.SeqIdentifier: SeqIdentifier,
        model.SeqCategory: SeqCategory,
        model.SeqCategorySet: SeqCategorySet,
        model.SeqClassification: SeqClassification,
        model.SeqDistance: SeqDistance,
        model.SeqProfile: SeqProfile,
        model.SeqProfileIdentifier: SeqProfileIdentifier,
        model.SeqTaxonomy: SeqTaxonomy,
        model.Taxon: Taxon,
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
