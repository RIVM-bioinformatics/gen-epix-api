from datetime import date
from test.omopdb.integration.person_upload.ref_data import RefData
from test.omopdb.omopdb_test_client import OmopdbTestClient as Env
from typing import Any

import pytest

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.domain.model.omop.base import int_to_uuid


def _create(env: Env, root_user: model.User, crud_command_class: type, obj: Any) -> Any:
    return env.app.handle(
        crud_command_class(user=root_user, operation=CrudOperation.CREATE_ONE, objs=obj)
    )


@pytest.fixture(scope="module", name="ref_data")
def create_ref_data(env: Env) -> RefData:
    """Create one concept, used for every concept field, and an identifier issuer.

    The domain, vocabulary and class refer to the same concept created below.
    """
    root_user = env.get_root_user()
    concept_id = int_to_uuid(1)
    domain: model.Domain = _create(
        env,
        root_user,
        command.DomainCrudCommand,
        model.Domain(
            domain_str_id="test", domain_name="Test", domain_concept_id=concept_id
        ),
    )
    vocabulary: model.Vocabulary = _create(
        env,
        root_user,
        command.VocabularyCrudCommand,
        model.Vocabulary(
            vocabulary_str_id="test",
            vocabulary_name="Test",
            vocabulary_concept_id=concept_id,
        ),
    )
    concept_class: model.ConceptClass = _create(
        env,
        root_user,
        command.ConceptClassCrudCommand,
        model.ConceptClass(
            concept_class_str_id="test",
            concept_class_name="Test",
            concept_class_concept_id=concept_id,
        ),
    )
    assert domain.domain_id is not None
    assert vocabulary.vocabulary_id is not None
    assert concept_class.concept_class_id is not None
    concept: model.Concept = _create(
        env,
        root_user,
        command.ConceptCrudCommand,
        model.Concept(
            concept_int_id=1,
            concept_name="Test",
            domain_id=domain.domain_id,
            vocabulary_id=vocabulary.vocabulary_id,
            concept_class_id=concept_class.concept_class_id,
            concept_code="test",
            valid_start_date=date(2000, 1, 1),
            valid_end_date=date(2099, 12, 31),
        ),
    )
    identifier_issuer: model.IdentifierIssuer = _create(
        env,
        root_user,
        command.IdentifierIssuerCrudCommand,
        model.IdentifierIssuer(code="test_issuer", name="Test"),
    )
    assert concept.concept_id is not None
    assert identifier_issuer.id is not None
    return RefData(root_user, concept.concept_id, identifier_issuer.id)
