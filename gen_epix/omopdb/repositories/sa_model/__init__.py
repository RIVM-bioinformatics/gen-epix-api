# pylint: disable=useless-import-alias
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
from gen_epix.omopdb.domain import DOMAIN, enum, model
from gen_epix.omopdb.repositories.sa_model.omop import CareSite as CareSite
from gen_epix.omopdb.repositories.sa_model.omop import CdmSource as CdmSource
from gen_epix.omopdb.repositories.sa_model.omop import Cohort as Cohort
from gen_epix.omopdb.repositories.sa_model.omop import (
    CohortDefinition as CohortDefinition,
)
from gen_epix.omopdb.repositories.sa_model.omop import Concept as Concept
from gen_epix.omopdb.repositories.sa_model.omop import (
    ConceptAncestor as ConceptAncestor,
)
from gen_epix.omopdb.repositories.sa_model.omop import ConceptClass as ConceptClass
from gen_epix.omopdb.repositories.sa_model.omop import (
    ConceptRelationship as ConceptRelationship,
)
from gen_epix.omopdb.repositories.sa_model.omop import ConceptSynonym as ConceptSynonym
from gen_epix.omopdb.repositories.sa_model.omop import ConditionEra as ConditionEra
from gen_epix.omopdb.repositories.sa_model.omop import (
    ConditionOccurrence as ConditionOccurrence,
)
from gen_epix.omopdb.repositories.sa_model.omop import Cost as Cost
from gen_epix.omopdb.repositories.sa_model.omop import DeviceExposure as DeviceExposure
from gen_epix.omopdb.repositories.sa_model.omop import Domain as Domain
from gen_epix.omopdb.repositories.sa_model.omop import DoseEra as DoseEra
from gen_epix.omopdb.repositories.sa_model.omop import DrugEra as DrugEra
from gen_epix.omopdb.repositories.sa_model.omop import DrugExposure as DrugExposure
from gen_epix.omopdb.repositories.sa_model.omop import DrugStrength as DrugStrength
from gen_epix.omopdb.repositories.sa_model.omop import (
    FactRelationship as FactRelationship,
)
from gen_epix.omopdb.repositories.sa_model.omop import Location as Location
from gen_epix.omopdb.repositories.sa_model.omop import (
    LocationHistory as LocationHistory,
)
from gen_epix.omopdb.repositories.sa_model.omop import Measurement as Measurement
from gen_epix.omopdb.repositories.sa_model.omop import (
    MeasurementRelation as MeasurementRelation,
)
from gen_epix.omopdb.repositories.sa_model.omop import Metadata as Metadata
from gen_epix.omopdb.repositories.sa_model.omop import Note as Note
from gen_epix.omopdb.repositories.sa_model.omop import NoteNlp as NoteNlp
from gen_epix.omopdb.repositories.sa_model.omop import Observation as Observation
from gen_epix.omopdb.repositories.sa_model.omop import (
    ObservationPeriod as ObservationPeriod,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    PayerPlanPeriod as PayerPlanPeriod,
)
from gen_epix.omopdb.repositories.sa_model.omop import Person as Person
from gen_epix.omopdb.repositories.sa_model.omop import (
    ProcedureOccurrence as ProcedureOccurrence,
)
from gen_epix.omopdb.repositories.sa_model.omop import Provider as Provider
from gen_epix.omopdb.repositories.sa_model.omop import Relationship as Relationship
from gen_epix.omopdb.repositories.sa_model.omop import (
    SourceToConceptMap as SourceToConceptMap,
)
from gen_epix.omopdb.repositories.sa_model.omop import Specimen as Specimen
from gen_epix.omopdb.repositories.sa_model.omop import SurveyConduct as SurveyConduct
from gen_epix.omopdb.repositories.sa_model.omop import VisitDetail as VisitDetail
from gen_epix.omopdb.repositories.sa_model.omop import (
    VisitOccurrence as VisitOccurrence,
)
from gen_epix.omopdb.repositories.sa_model.omop import Vocabulary as Vocabulary

SA_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, dict[type[model.Model], type]] = {
    enum.ServiceType.ABAC: {
        model.OrganizationAdminPolicy: OrganizationAdminPolicy,
    },
    enum.ServiceType.ORGANIZATION: {
        model.Contact: Contact,
        model.DataCollection: DataCollection,
        model.DataCollectionSet: DataCollectionSet,
        model.DataCollectionSetMember: DataCollectionSetMember,
        model.ExternalIdentifier: ExternalIdentifier,
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
    enum.ServiceType.OMOP: {
        model.CareSite: CareSite,
        model.CdmSource: CdmSource,
        model.Cohort: Cohort,
        model.CohortDefinition: CohortDefinition,
        model.Concept: Concept,
        model.ConceptAncestor: ConceptAncestor,
        model.ConceptClass: ConceptClass,
        model.ConceptRelationship: ConceptRelationship,
        model.ConceptSynonym: ConceptSynonym,
        model.ConditionEra: ConditionEra,
        model.ConditionOccurrence: ConditionOccurrence,
        model.Cost: Cost,
        model.DeviceExposure: DeviceExposure,
        model.Domain: Domain,
        model.DoseEra: DoseEra,
        model.DrugEra: DrugEra,
        model.DrugExposure: DrugExposure,
        model.DrugStrength: DrugStrength,
        model.FactRelationship: FactRelationship,
        model.Location: Location,
        model.LocationHistory: LocationHistory,
        model.Measurement: Measurement,
        model.MeasurementRelation: MeasurementRelation,
        model.Metadata: Metadata,
        model.Note: Note,
        model.NoteNlp: NoteNlp,
        model.Observation: Observation,
        model.ObservationPeriod: ObservationPeriod,
        model.PayerPlanPeriod: PayerPlanPeriod,
        model.Person: Person,
        model.ProcedureOccurrence: ProcedureOccurrence,
        model.Provider: Provider,
        model.Relationship: Relationship,
        model.SourceToConceptMap: SourceToConceptMap,
        model.Specimen: Specimen,
        model.SurveyConduct: SurveyConduct,
        model.VisitDetail: VisitDetail,
        model.VisitOccurrence: VisitOccurrence,
        model.Vocabulary: Vocabulary,
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
