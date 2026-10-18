"""Test an Alembic revision whose numeric filename is loaded dynamically."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace

SOURCE_PATH = (
    Path(__file__).resolve().parents[6]
    / "gen_epix"
    / "omopdb"
    / "repositories"
    / "sa_alembic"
    / "versions"
    / "4c60bf3993c5_add_cohort_definition_foreign_key.py"
)
SPEC = spec_from_file_location("cohort_definition_foreign_key_migration", SOURCE_PATH)
assert SPEC is not None and SPEC.loader is not None
MIGRATION = module_from_spec(SPEC)
SPEC.loader.exec_module(MIGRATION)

FOREIGN_KEY_NAME = "fk_cohort_cohort_definition_id"
COHORT_DEFINITION_ID = "cohort_definition_id"


def test_upgrade_creates_cohort_definition_foreign_key(monkeypatch):
    """Verify the upgrade creates the foreign key in the OMOP schema."""
    calls = []
    monkeypatch.setattr(
        MIGRATION,
        "op",
        SimpleNamespace(
            create_foreign_key=lambda *args, **kwargs: calls.append((args, kwargs))
        ),
    )

    MIGRATION.upgrade()

    assert calls == [
        (
            (
                FOREIGN_KEY_NAME,
                "cohort",
                "cohort_definition",
                [COHORT_DEFINITION_ID],
                [COHORT_DEFINITION_ID],
            ),
            {"source_schema": "omop", "referent_schema": "omop"},
        )
    ]


def test_downgrade_drops_cohort_definition_foreign_key(monkeypatch):
    """Verify the downgrade removes the foreign key from the OMOP schema."""
    calls = []
    monkeypatch.setattr(
        MIGRATION,
        "op",
        SimpleNamespace(
            drop_constraint=lambda *args, **kwargs: calls.append((args, kwargs))
        ),
    )

    MIGRATION.downgrade()

    assert calls == [
        (
            (FOREIGN_KEY_NAME, "cohort"),
            {"schema": "omop", "type_": "foreignkey"},
        )
    ]
