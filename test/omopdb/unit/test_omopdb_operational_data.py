"""Test OmopDB operational-data deletion and retained reference data."""

from test.util.operational_data import BaseOperationalDataTests


class TestOmopOperationalData(BaseOperationalDataTests):
    """Encapsulates the OmopDB reset contract and retained-data boundary."""

    APP_NAME = "omopdb"
    SERVICE_NAME = "omop"
    EXPECTED_MODELS = {
        "Person",
        "PersonIdentifier",
        "ObservationPeriod",
        "ObservationPeriodIdentifier",
        "VisitOccurrence",
        "VisitOccurrenceIdentifier",
        "VisitDetail",
        "VisitDetailIdentifier",
        "ConditionOccurrence",
        "ConditionOccurrenceIdentifier",
        "ProcedureOccurrence",
        "ProcedureOccurrenceIdentifier",
        "DrugExposure",
        "DrugExposureIdentifier",
        "DeviceExposure",
        "DeviceExposureIdentifier",
        "Specimen",
        "SpecimenIdentifier",
        "Measurement",
        "MeasurementIdentifier",
        "Observation",
        "ObservationIdentifier",
        "Note",
        "NoteIdentifier",
        "NoteNlp",
        "NoteNlpIdentifier",
        "FactRelationship",
        "Death",
        "DeathIdentifier",
        "MeasurementRelation",
        "MeasurementRelationIdentifier",
        "PayerPlanPeriod",
        "Cost",
        "ConditionEra",
        "DrugEra",
        "DoseEra",
        "Cohort",
        "Episode",
        "EpisodeEvent",
    }
