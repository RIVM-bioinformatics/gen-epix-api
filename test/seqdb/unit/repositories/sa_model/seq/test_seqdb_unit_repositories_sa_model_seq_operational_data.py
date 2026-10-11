"""Test SQLAlchemy relationships for operational seqdb data mappings."""

from typing import Any

import pytest

from gen_epix.seqdb.repositories.sa_model.seq import operational_data


@pytest.mark.parametrize(
    ("mapped_model", "expected_relationships"),
    [
        (operational_data.Sample, {}),
        (operational_data.SampleDataCollectionLink, {}),
        (operational_data.SampleIdentifier, {"sample": "Sample"}),
        (operational_data.ReadSet, {"sample": "Sample", "protocol": "Protocol"}),
        (operational_data.ReadSetIdentifier, {"read_set": "ReadSet"}),
        (
            operational_data.Seq,
            {
                "sample": "Sample",
                "read_set": "ReadSet",
                "read_set2": "ReadSet",
                "protocol": "Protocol",
            },
        ),
        (operational_data.SeqIdentifier, {"seq": "Seq"}),
        (
            operational_data.AstMeasurement,
            {"sample": "Sample", "protocol": "Protocol"},
        ),
        (
            operational_data.AstPrediction,
            {"sample": "Sample", "seq": "Seq", "protocol": "Protocol"},
        ),
        (
            operational_data.PcrMeasurement,
            {"sample": "Sample", "protocol": "Protocol"},
        ),
        (
            operational_data.SeqClassification,
            {
                "sample": "Sample",
                "seq": "Seq",
                "protocol": "Protocol",
                "primary_category": "SeqCategory",
            },
        ),
        (
            operational_data.SeqTaxonomy,
            {
                "sample": "Sample",
                "seq": "Seq",
                "protocol": "Protocol",
                "primary_taxon": "Taxon",
            },
        ),
        (
            operational_data.SeqProfile,
            {"sample": "Sample", "seq": "Seq", "protocol": "Protocol"},
        ),
        (operational_data.SeqProfileIdentifier, {"seq_profile": "SeqProfile"}),
        (
            operational_data.SeqDistance,
            {
                "sample": "Sample",
                "seq_profile": "SeqProfile",
                "protocol": "Protocol",
            },
        ),
    ],
    ids=lambda mapped_model: (
        mapped_model.__name__ if isinstance(mapped_model, type) else None
    ),
)
def test_operational_data_relationship_targets(
    mapped_model: type[Any], expected_relationships: dict[str, str]
) -> None:
    """Map each operational-data relationship to its declared entity."""
    actual_relationships = {
        relationship.key: relationship.mapper.class_.__name__
        for relationship in mapped_model.__mapper__.relationships
    }

    assert actual_relationships == expected_relationships
