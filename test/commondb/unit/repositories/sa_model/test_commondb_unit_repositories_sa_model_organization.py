"""Verify SQLAlchemy organization model mappings."""

from gen_epix.commondb.repositories.sa_model.organization import Contact


def test_contact_site_mapping_is_required() -> None:
    """Keep contact site annotations aligned with the non-null database column."""
    assert Contact.__table__.c.site_id.nullable is False
