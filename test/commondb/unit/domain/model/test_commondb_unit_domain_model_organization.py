"""Validate organization foreign-key descriptions in CommonDB schemas."""

import base64
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import (
    IdentifierForUpload,
    OrganizationIdentifierIssuerLink,
    OrganizationSetMember,
    Site,
)
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.model.seq.base import encode_ascii_as_gzip_base64

ORGANIZATION_ID_DESCRIPTION = "The ID of the organization. FOREIGN KEY"


@pytest.mark.parametrize(
    ("model_class", "field_name"),
    [
        (OrganizationIdentifierIssuerLink, "organization_id"),
        (OrganizationSetMember, "organization_id"),
        (Site, "organization_id"),
    ],
)
def test_organization_foreign_key_schema_description(
    model_class: type, field_name: str
) -> None:
    """Keep organization links described as foreign keys in the schema."""
    assert (
        model_class.model_fields[field_name].description == ORGANIZATION_ID_DESCRIPTION
    )


"""
Unit tests for IDSDB ETL model classes.

Tests the Identifier, AlleleForUpload, AlleleProfileForUpload,
and SampleBatchForUpload models with various validation scenarios.
"""


@pytest.mark.scenario_ids("TC-SEC-31-01")
class TestModelIdentifier:

    def test_valid_with_identifier_issuer_code(self) -> None:
        """Test valid Identifier with identifier_issuer_code."""
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER", external_id="SAMPLE123"
        )
        assert identifier_for_upload.identifier_issuer_code == "TEST_ISSUER"
        assert identifier_for_upload.identifier_issuer_id is None
        assert identifier_for_upload.external_id == "SAMPLE123"

    def test_valid_with_identifier_issuer_id(self) -> None:
        """Test valid Identifier with identifier_issuer_id."""
        issuer_id = uuid4()
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_id=issuer_id, external_id="SAMPLE123"
        )
        assert identifier_for_upload.identifier_issuer_code is None
        assert identifier_for_upload.identifier_issuer_id == issuer_id
        assert identifier_for_upload.external_id == "SAMPLE123"

    def test_valid_with_both_issuer_fields(self) -> None:
        """Test valid Identifier with both issuer fields."""
        issuer_id = uuid4()
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="TEST_ISSUER",
            identifier_issuer_id=issuer_id,
            external_id="SAMPLE123",
        )
        assert identifier_for_upload.identifier_issuer_code == "TEST_ISSUER"
        assert identifier_for_upload.identifier_issuer_id == issuer_id

    def test_invalid_missing_both_issuer_fields(self) -> None:
        """Test ValidationError when both issuer fields are missing."""
        with pytest.raises(ValidationError):
            model.IdentifierForUpload(external_id="SAMPLE123")

    def test_max_length_validation(self) -> None:
        """Test field length validation."""
        # Valid lengths
        identifier_for_upload = model.IdentifierForUpload(
            identifier_issuer_code="A" * 255, external_id="B" * 255
        )
        assert len(identifier_for_upload.identifier_issuer_code or []) == 255
        assert len(identifier_for_upload.external_id) == 255
        # Exceeding max lengths
        with pytest.raises(ValidationError):
            model.IdentifierForUpload(
                identifier_issuer_code="A" * 256, external_id="B" * 255
            )
            model.IdentifierForUpload(
                identifier_issuer_code="A" * 255, external_id="B" * 256
            )
