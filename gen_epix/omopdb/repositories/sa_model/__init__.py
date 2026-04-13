# pylint: disable=useless-import-alias

from gen_epix import fastapp
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
from gen_epix.commondb.repositories.sa_model import RowMetadataMixin
from gen_epix.commondb.repositories.sa_model import Site as Site
from gen_epix.commondb.repositories.sa_model import User as User
from gen_epix.commondb.repositories.sa_model import UserInvitation as UserInvitation
from gen_epix.commondb.repositories.sa_model import set_entity_repository_model_classes
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
from gen_epix.omopdb.repositories.sa_model.omop import (
    ConditionOccurrenceIdentifier as ConditionOccurrenceIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import Cost as Cost
from gen_epix.omopdb.repositories.sa_model.omop import Death as Death
from gen_epix.omopdb.repositories.sa_model.omop import (
    DeathIdentifier as DeathIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import DeviceExposure as DeviceExposure
from gen_epix.omopdb.repositories.sa_model.omop import (
    DeviceExposureIdentifier as DeviceExposureIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import Domain as Domain
from gen_epix.omopdb.repositories.sa_model.omop import DoseEra as DoseEra
from gen_epix.omopdb.repositories.sa_model.omop import DrugEra as DrugEra
from gen_epix.omopdb.repositories.sa_model.omop import DrugExposure as DrugExposure
from gen_epix.omopdb.repositories.sa_model.omop import (
    DrugExposureIdentifier as DrugExposureIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import DrugStrength as DrugStrength
from gen_epix.omopdb.repositories.sa_model.omop import Episode as Episode
from gen_epix.omopdb.repositories.sa_model.omop import EpisodeEvent as EpisodeEvent
from gen_epix.omopdb.repositories.sa_model.omop import (
    FactRelationship as FactRelationship,
)
from gen_epix.omopdb.repositories.sa_model.omop import Location as Location
from gen_epix.omopdb.repositories.sa_model.omop import Measurement as Measurement
from gen_epix.omopdb.repositories.sa_model.omop import (
    MeasurementIdentifier as MeasurementIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    MeasurementRelation as MeasurementRelation,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    MeasurementRelationIdentifier as MeasurementRelationIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import Metadata as Metadata
from gen_epix.omopdb.repositories.sa_model.omop import Note as Note
from gen_epix.omopdb.repositories.sa_model.omop import NoteIdentifier as NoteIdentifier
from gen_epix.omopdb.repositories.sa_model.omop import NoteNlp as NoteNlp
from gen_epix.omopdb.repositories.sa_model.omop import (
    NoteNlpIdentifier as NoteNlpIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import Observation as Observation
from gen_epix.omopdb.repositories.sa_model.omop import (
    ObservationIdentifier as ObservationIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    ObservationPeriod as ObservationPeriod,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    ObservationPeriodIdentifier as ObservationPeriodIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    PayerPlanPeriod as PayerPlanPeriod,
)
from gen_epix.omopdb.repositories.sa_model.omop import Person as Person
from gen_epix.omopdb.repositories.sa_model.omop import (
    PersonIdentifier as PersonIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    ProcedureOccurrence as ProcedureOccurrence,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    ProcedureOccurrenceIdentifier as ProcedureOccurrenceIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import Provider as Provider
from gen_epix.omopdb.repositories.sa_model.omop import Relationship as Relationship
from gen_epix.omopdb.repositories.sa_model.omop import (
    SourceToConceptMap as SourceToConceptMap,
)
from gen_epix.omopdb.repositories.sa_model.omop import Specimen as Specimen
from gen_epix.omopdb.repositories.sa_model.omop import (
    SpecimenIdentifier as SpecimenIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import VisitDetail as VisitDetail
from gen_epix.omopdb.repositories.sa_model.omop import (
    VisitDetailIdentifier as VisitDetailIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    VisitOccurrence as VisitOccurrence,
)
from gen_epix.omopdb.repositories.sa_model.omop import (
    VisitOccurrenceIdentifier as VisitOccurrenceIdentifier,
)
from gen_epix.omopdb.repositories.sa_model.omop import Vocabulary as Vocabulary

SA_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, dict[type[fastapp.Model], type]] = {
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
        model.ConditionOccurrenceIdentifier: ConditionOccurrenceIdentifier,
        model.Cost: Cost,
        model.Death: Death,
        model.DeathIdentifier: DeathIdentifier,
        model.DeviceExposure: DeviceExposure,
        model.DeviceExposureIdentifier: DeviceExposureIdentifier,
        model.Domain: Domain,
        model.DoseEra: DoseEra,
        model.DrugEra: DrugEra,
        model.DrugExposure: DrugExposure,
        model.DrugExposureIdentifier: DrugExposureIdentifier,
        model.DrugStrength: DrugStrength,
        model.Episode: Episode,
        model.EpisodeEvent: EpisodeEvent,
        model.FactRelationship: FactRelationship,
        model.Location: Location,
        model.Measurement: Measurement,
        model.MeasurementIdentifier: MeasurementIdentifier,
        model.MeasurementRelation: MeasurementRelation,
        model.MeasurementRelationIdentifier: MeasurementRelationIdentifier,
        model.Metadata: Metadata,
        model.Note: Note,
        model.NoteIdentifier: NoteIdentifier,
        model.NoteNlp: NoteNlp,
        model.NoteNlpIdentifier: NoteNlpIdentifier,
        model.Observation: Observation,
        model.ObservationIdentifier: ObservationIdentifier,
        model.ObservationPeriod: ObservationPeriod,
        model.ObservationPeriodIdentifier: ObservationPeriodIdentifier,
        model.PayerPlanPeriod: PayerPlanPeriod,
        model.Person: Person,
        model.PersonIdentifier: PersonIdentifier,
        model.ProcedureOccurrence: ProcedureOccurrence,
        model.ProcedureOccurrenceIdentifier: ProcedureOccurrenceIdentifier,
        model.Provider: Provider,
        model.Relationship: Relationship,
        model.SourceToConceptMap: SourceToConceptMap,
        model.Specimen: Specimen,
        model.SpecimenIdentifier: SpecimenIdentifier,
        model.VisitDetail: VisitDetail,
        model.VisitDetailIdentifier: VisitDetailIdentifier,
        model.VisitOccurrence: VisitOccurrence,
        model.VisitOccurrenceIdentifier: VisitOccurrenceIdentifier,
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
