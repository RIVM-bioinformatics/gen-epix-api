# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar

from gen_epix.common.domain.command import CrudCommand
from gen_epix.omopdb.domain import model


class PersonCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Person


class ObservationPeriodCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ObservationPeriod


class VisitOccurrenceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.VisitOccurrence


class VisitDetailCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.VisitDetail


class ConditionOccurrenceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConditionOccurrence


class DrugExposureCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DrugExposure


class ProcedureOccurrenceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ProcedureOccurrence


class DeviceExposureCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DeviceExposure


class MeasurementCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Measurement


class ObservationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Observation


class NoteCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Note


class NoteNlpCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.NoteNlp


class SpecimenCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Specimen


class FactRelationshipCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.FactRelationship


class SurveyConductCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SurveyConduct


class LocationCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Location


class LocationHistoryCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.LocationHistory


class CareSiteCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CareSite


class ProviderCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Provider


class PayerPlanPeriodCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.PayerPlanPeriod


class CostCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Cost


class DrugEraCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DrugEra


class DoseEraCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DoseEra


class ConditionEraCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConditionEra


class MetadataCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Metadata


class CdmSourceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CdmSource


class ConceptCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Concept


class VocabularyCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Vocabulary


class DomainCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Domain


class ConceptClassCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptClass


class ConceptRelationshipCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptRelationship


class RelationshipCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Relationship


class ConceptSynonymCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptSynonym


class ConceptAncestorCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.ConceptAncestor


class SourceToConceptMapCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SourceToConceptMap


class DrugStrengthCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.DrugStrength


class CohortCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Cohort


class CohortDefinitionCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.CohortDefinition


class ProvenanceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Provenance


class EtlCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Etl


class SourceCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Source
