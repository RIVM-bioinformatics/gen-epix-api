from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.model.case.ops_data import (
    Case,
    CaseDataCollectionLink,
    CaseIdentifier,
    CaseSet,
    CaseSetDataCollectionLink,
    CaseSetMember,
)


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestModelCaseOpsData:
    def test_case_defaults_and_count_validation(self) -> None:
        case = Case(
            case_type_id=uuid4(),
            created_in_data_collection_id=uuid4(),
            content={},
        )
        assert case.count == 1
        assert isinstance(case.case_date, datetime)

        with pytest.raises(ValidationError):
            Case(
                case_type_id=uuid4(),
                created_in_data_collection_id=uuid4(),
                content={},
                count=-1,
            )

    def test_case_serializers_drop_none_and_stringify_ids(self) -> None:
        cohort_id = uuid4()
        cohort_definition_id = uuid4()
        col_id = uuid4()
        case = Case(
            case_type_id=uuid4(),
            created_in_data_collection_id=uuid4(),
            cohort={cohort_id: cohort_definition_id, uuid4(): None},
            content={col_id: "value", uuid4(): None},
        )

        dumped = case.model_dump()
        assert dumped["cohort"] == {str(cohort_id): str(cohort_definition_id)}
        assert dumped["content"] == {str(col_id): "value"}

    def test_case_identifier_instantiation(self) -> None:
        case = Case(
            case_type_id=uuid4(),
            created_in_data_collection_id=uuid4(),
            content={},
        )
        identifier = CaseIdentifier(
            identifier_issuer_id=uuid4(),
            external_id=" external-id ",
            internal_id=uuid4(),
            case=case,
        )
        assert identifier.case is case
        assert identifier.external_id == "external-id"
        assert identifier.id is not None

    def test_case_data_collection_link_instantiation(self) -> None:
        case_id = uuid4()
        data_collection_id = uuid4()
        link = CaseDataCollectionLink(
            case_id=case_id,
            data_collection_id=data_collection_id,
        )
        assert link.case_id == case_id
        assert link.data_collection_id == data_collection_id

    def test_case_set_instantiation(self) -> None:
        case_set = CaseSet(
            case_type_id=uuid4(),
            created_in_data_collection_id=uuid4(),
            name="set-name",
            code="set-code",
            description="desc",
            case_set_category_id=uuid4(),
            case_set_status_id=uuid4(),
        )
        assert case_set.name == "set-name"
        assert case_set.code == "set-code"

    def test_case_set_member_and_data_collection_link_instantiation(self) -> None:
        member = CaseSetMember(
            case_set_id=uuid4(),
            case_id=uuid4(),
            classification=enum.CaseClassification.CONFIRMED,
        )
        assert member.classification == enum.CaseClassification.CONFIRMED

        link = CaseSetDataCollectionLink(
            case_set_id=uuid4(),
            data_collection_id=uuid4(),
        )
        assert link.data_collection_id is not None
