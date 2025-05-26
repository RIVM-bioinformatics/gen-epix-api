import json
from datetime import date, datetime
from uuid import UUID, uuid4

import pytest

# Import the Pydantic models from omop.py
from gen_epix.omopdb.domain.model.omop import (
    Location,
    LocationHistory,
    Measurement,
    Observation,
    Person,
    Specimen,
)


# use an encoder to ensure consistent datetime format with pydantic (use ISO 8601 format, i.e. with 'T' separator)
# and then take care of some other types as well
class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


@pytest.fixture
def common_data():
    person_id = uuid4()
    provider_id = uuid4()
    location_id = uuid4()
    care_site_id = uuid4()
    provenance_id = uuid4()
    source_traceback = "source_traceback_example"

    return {
        "person_id": person_id,
        "provider_id": provider_id,
        "location_id": location_id,
        "care_site_id": care_site_id,
        "provenance_id": provenance_id,
        "source_traceback": source_traceback,
    }


@pytest.fixture
def person_data(common_data):
    return {
        "person_id": common_data["person_id"],
        "gender_concept_id": 8507,
        "year_of_birth": 1980,
        "month_of_birth": 7,
        "day_of_birth": 15,
        "race_concept_id": 8527,
        "ethnicity_concept_id": 38003563,
        "location_id": common_data["location_id"],
        "provider_id": common_data["provider_id"],
        "care_site_id": common_data["care_site_id"],
        "person_source_value": "P1",
        "gender_source_value": "M",
        "gender_source_concept_id": 0,
        "race_source_value": "White",
        "race_source_concept_id": 0,
        "ethnicity_source_value": "Not Hispanic or Latino",
        "ethnicity_source_concept_id": 0,
        "birth_datetime": datetime(1980, 7, 15),
        "death_datetime": None,
        "person_type_concept_id": 1,
        "provenance_id": common_data["provenance_id"],
        "source_traceback": common_data["source_traceback"],
    }


@pytest.fixture
def observation_data(common_data, person_data):
    return {
        "observation_id": uuid4(),
        "person_id": person_data["person_id"],
        "observation_concept_id": 40757130,
        "observation_date": date(2023, 1, 1),
        "observation_datetime": datetime(2023, 1, 1, 8, 0, 0),
        "observation_iso_interval": "2023-01-08/2023-01-08",
        "observation_type_concept_id": 38000280,
        "value_as_datetime": None,
        "value_as_iso_interval": None,
        "value_as_number": None,
        "value_as_string": "Observation value",
        "value_as_concept_id": None,
        "qualifier_concept_id": None,
        "unit_concept_id": None,
        "provider_id": person_data["provider_id"],
        "visit_occurrence_id": uuid4(),
        "visit_detail_id": None,
        "observation_source_value": "OBS1",
        "observation_source_concept_id": 0,
        "unit_source_value": None,
        "qualifier_source_value": None,
        "observation_event_id": None,
        "obs_event_field_concept_id": None,
        "provenance_id": common_data["provenance_id"],
        "source_traceback": common_data["source_traceback"],
    }


@pytest.fixture
def location_data(common_data):
    return {
        "location_id": common_data["location_id"],
        "address_1": "123 Main St",
        "address_2": None,
        "city": "Anytown",
        "state": "CA",
        "zip": "12345",
        "county": "Anycounty",
        "location_source_value": "LOC1",
        "provenance_id": common_data["provenance_id"],
        "source_traceback": common_data["source_traceback"],
    }


@pytest.fixture
def location_history_data(common_data, person_data, location_data):
    return {
        "location_history_id": uuid4(),
        "entity_id": person_data["person_id"],  # in this case, the entity is a person
        "domain_id": "person",
        "location_id": location_data["location_id"],
        "relationship_type_concept_id": 44818987,
        "start_date": date(2023, 1, 1),
        "start_iso_interval": "2023-01-01/2023-01-01",
        "end_iso_interval": None,
        "provenance_id": common_data["provenance_id"],
        "source_traceback": common_data["source_traceback"],
    }


@pytest.fixture
def measurement_data(common_data, person_data):
    return {
        "measurement_id": uuid4(),
        "person_id": person_data["person_id"],
        "measurement_concept_id": 3025315,
        "measurement_date": date(2023, 1, 1),
        "measurement_datetime": datetime(2023, 1, 1, 8, 30, 0),
        "measurement_iso_interval": "2023/01/01T08:30:00/2023/01/01T08:30:00",
        "measurement_type_concept_id": 44818702,
        "operator_concept_id": None,
        "value_as_number": 120.5,
        "value_as_concept_id": None,
        "unit_concept_id": 8576,
        "range_low": 80.0,
        "range_high": 140.0,
        "provider_id": person_data["provider_id"],
        "visit_occurrence_id": uuid4(),
        "measurement_source_value": "MEAS1",
        "measurement_source_concept_id": 0,
        "unit_source_value": "mmHg",
        "provenance_id": common_data["provenance_id"],
        "source_traceback": common_data["source_traceback"],
    }


@pytest.fixture
def specimen_data(common_data, person_data):
    return {
        "specimen_id": uuid4(),
        "person_id": person_data["person_id"],
        "specimen_concept_id": 4000001,
        "specimen_type_concept_id": 44814721,
        "specimen_date": date(2023, 1, 1),
        "specimen_datetime": datetime(2023, 1, 1, 8, 0, 0),
        "specimen_iso_interval": "2023/01/01T08:00:00/2023/01/01T08:00:00",
        "quantity": 1.0,
        "unit_concept_id": 8576,
        "anatomic_site_concept_id": None,
        "disease_status_concept_id": None,
        "specimen_source_id": "SPEC1",
        "specimen_source_value": "Specimen value",
        "unit_source_value": "mL",
        "anatomic_site_source_value": None,
        "disease_status_source_value": None,
        "provenance_id": common_data["provenance_id"],
        "source_traceback": common_data["source_traceback"],
    }


# Create Pydantic model instances
def test_create_instances(
    person_data,
    observation_data,
    location_data,
    location_history_data,
    measurement_data,
    specimen_data,
):
    person = Person(**person_data)
    observation = Observation(**observation_data)
    location = Location(**location_data)
    location_history = LocationHistory(**location_history_data)
    measurement = Measurement(**measurement_data)
    specimen = Specimen(**specimen_data)


def test_serialize_instances(
    person_data,
    observation_data,
    location_data,
    location_history_data,
    measurement_data,
    specimen_data,
):
    person = Person(**person_data)
    observation = Observation(**observation_data)
    location = Location(**location_data)
    location_history = LocationHistory(**location_history_data)
    measurement = Measurement(**measurement_data)
    specimen = Specimen(**specimen_data)

    # Serialize the model instances to JSON
    dumps_args = {"sort_keys": True, "cls": Encoder}
    model_dump_args = {"mode": "json", "exclude_unset": True}
    person_json = json.dumps(person.model_dump(**model_dump_args), **dumps_args)
    observation_json = json.dumps(
        observation.model_dump(**model_dump_args), **dumps_args
    )
    location_json = json.dumps(location.model_dump(**model_dump_args), **dumps_args)
    location_history_json = json.dumps(
        location_history.model_dump(**model_dump_args), **dumps_args
    )
    measurement_json = json.dumps(
        measurement.model_dump(**model_dump_args), **dumps_args
    )
    specimen_json = json.dumps(specimen.model_dump(**model_dump_args), **dumps_args)

    # Expected JSON output (for comparison)
    expected_person_json = json.dumps(person_data, **dumps_args)
    expected_observation_json = json.dumps(observation_data, **dumps_args)
    expected_location_json = json.dumps(location_data, **dumps_args)
    expected_location_history_json = json.dumps(location_history_data, **dumps_args)
    expected_measurement_json = json.dumps(measurement_data, **dumps_args)
    expected_specimen_json = json.dumps(specimen_data, **dumps_args)

    # Test that the serialized JSON matches the expected output
    assert person_json == expected_person_json
    assert observation_json == expected_observation_json
    assert location_json == expected_location_json
    assert location_history_json == expected_location_history_json
    assert measurement_json == expected_measurement_json
    assert specimen_json == expected_specimen_json
