# pylint: disable=useless-import-alias
from gen_epix.casedb.domain import DOMAIN, enum, model
from gen_epix.casedb.repositories.sa_model.abac import (
    OrganizationAccessCasePolicy as OrganizationAccessCasePolicy,
)
from gen_epix.casedb.repositories.sa_model.abac import (
    OrganizationShareCasePolicy as OrganizationShareCasePolicy,
)
from gen_epix.casedb.repositories.sa_model.abac import (
    UserAccessCasePolicy as UserAccessCasePolicy,
)
from gen_epix.casedb.repositories.sa_model.abac import (
    UserShareCasePolicy as UserShareCasePolicy,
)
from gen_epix.casedb.repositories.sa_model.case import Case as Case
from gen_epix.casedb.repositories.sa_model.case import (
    CaseDataCollectionLink as CaseDataCollectionLink,
)
from gen_epix.casedb.repositories.sa_model.case import CaseSet as CaseSet
from gen_epix.casedb.repositories.sa_model.case import (
    CaseSetCategory as CaseSetCategory,
)
from gen_epix.casedb.repositories.sa_model.case import (
    CaseSetDataCollectionLink as CaseSetDataCollectionLink,
)
from gen_epix.casedb.repositories.sa_model.case import CaseSetMember as CaseSetMember
from gen_epix.casedb.repositories.sa_model.case import CaseSetStatus as CaseSetStatus
from gen_epix.casedb.repositories.sa_model.case import CaseType as CaseType
from gen_epix.casedb.repositories.sa_model.case import CaseTypeCol as CaseTypeCol
from gen_epix.casedb.repositories.sa_model.case import CaseTypeColSet as CaseTypeColSet
from gen_epix.casedb.repositories.sa_model.case import (
    CaseTypeColSetMember as CaseTypeColSetMember,
)
from gen_epix.casedb.repositories.sa_model.case import CaseTypeDim as CaseTypeDim
from gen_epix.casedb.repositories.sa_model.case import CaseTypeSet as CaseTypeSet
from gen_epix.casedb.repositories.sa_model.case import (
    CaseTypeSetCategory as CaseTypeSetCategory,
)
from gen_epix.casedb.repositories.sa_model.case import (
    CaseTypeSetMember as CaseTypeSetMember,
)
from gen_epix.casedb.repositories.sa_model.case import Col as Col
from gen_epix.casedb.repositories.sa_model.case import Dim as Dim
from gen_epix.casedb.repositories.sa_model.case import (
    GeneticDistanceProtocol as GeneticDistanceProtocol,
)
from gen_epix.casedb.repositories.sa_model.case import TreeAlgorithm as TreeAlgorithm
from gen_epix.casedb.repositories.sa_model.case import (
    TreeAlgorithmClass as TreeAlgorithmClass,
)
from gen_epix.casedb.repositories.sa_model.geo import Region as Region
from gen_epix.casedb.repositories.sa_model.geo import RegionRelation as RegionRelation
from gen_epix.casedb.repositories.sa_model.geo import RegionSet as RegionSet
from gen_epix.casedb.repositories.sa_model.geo import RegionSetShape as RegionSetShape
from gen_epix.casedb.repositories.sa_model.ontology import Concept as Concept
from gen_epix.casedb.repositories.sa_model.ontology import (
    ConceptRelation as ConceptRelation,
)
from gen_epix.casedb.repositories.sa_model.ontology import ConceptSet as ConceptSet
from gen_epix.casedb.repositories.sa_model.ontology import Disease as Disease
from gen_epix.casedb.repositories.sa_model.ontology import (
    EtiologicalAgent as EtiologicalAgent,
)
from gen_epix.casedb.repositories.sa_model.ontology import Etiology as Etiology
from gen_epix.casedb.repositories.sa_model.subject import Subject as Subject
from gen_epix.casedb.repositories.sa_model.subject import (
    SubjectIdentifier as SubjectIdentifier,
)
from gen_epix.commondb.repositories.sa_model import Contact as Contact
from gen_epix.commondb.repositories.sa_model import DataCollection as DataCollection
from gen_epix.commondb.repositories.sa_model import (
    DataCollectionSet as DataCollectionSet,
)
from gen_epix.commondb.repositories.sa_model import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.repositories.sa_model import (
    ExternalIdentifier as ExternalIdentifier,
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
    create_field_metadata,
    set_entity_repository_model_classes,
)

SA_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, dict[type[model.Model], type]] = {
    enum.ServiceType.ABAC: {
        model.OrganizationAdminPolicy: OrganizationAdminPolicy,
        model.OrganizationAccessCasePolicy: OrganizationAccessCasePolicy,
        model.OrganizationShareCasePolicy: OrganizationShareCasePolicy,
        model.UserAccessCasePolicy: UserAccessCasePolicy,
        model.UserShareCasePolicy: UserShareCasePolicy,
    },
    enum.ServiceType.ORGANIZATION: {
        model.Contact: Contact,
        model.DataCollection: DataCollection,
        model.DataCollectionSet: DataCollectionSet,
        model.DataCollectionSetMember: DataCollectionSetMember,
        model.IdentifierIssuer: IdentifierIssuer,
        model.ExternalIdentifier: ExternalIdentifier,
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
    enum.ServiceType.GEO: {
        model.Region: Region,
        model.RegionRelation: RegionRelation,
        model.RegionSet: RegionSet,
        model.RegionSetShape: RegionSetShape,
    },
    enum.ServiceType.ONTOLOGY: {
        model.Concept: Concept,
        model.ConceptRelation: ConceptRelation,
        model.ConceptSet: ConceptSet,
        model.Disease: Disease,
        model.EtiologicalAgent: EtiologicalAgent,
        model.Etiology: Etiology,
    },
    enum.ServiceType.SUBJECT: {
        model.Subject: Subject,
        model.SubjectIdentifier: SubjectIdentifier,
    },
    enum.ServiceType.CASE: {
        model.Case: Case,
        model.CaseDataCollectionLink: CaseDataCollectionLink,
        model.CaseSet: CaseSet,
        model.CaseSetCategory: CaseSetCategory,
        model.CaseSetDataCollectionLink: CaseSetDataCollectionLink,
        model.CaseSetMember: CaseSetMember,
        model.CaseSetStatus: CaseSetStatus,
        model.CaseType: CaseType,
        model.CaseTypeCol: CaseTypeCol,
        model.CaseTypeColSet: CaseTypeColSet,
        model.CaseTypeColSetMember: CaseTypeColSetMember,
        model.CaseTypeDim: CaseTypeDim,
        model.CaseTypeSet: CaseTypeSet,
        model.CaseTypeSetCategory: CaseTypeSetCategory,
        model.CaseTypeSetMember: CaseTypeSetMember,
        model.Col: Col,
        model.Dim: Dim,
        model.GeneticDistanceProtocol: GeneticDistanceProtocol,
        model.TreeAlgorithm: TreeAlgorithm,
        model.TreeAlgorithmClass: TreeAlgorithmClass,
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
