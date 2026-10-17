"""Test SQLAlchemy mapping for the seqdb File model."""

import sqlalchemy as sa

from gen_epix.seqdb.repositories.sa_model.file import File


def test_file_maps_required_binary_content_column() -> None:
    """Verify content is stored as a required binary column."""
    content_column = File.__table__.c.content

    assert File.__tablename__ == "file"
    assert isinstance(content_column.type, sa.LargeBinary)
    assert content_column.nullable is False
