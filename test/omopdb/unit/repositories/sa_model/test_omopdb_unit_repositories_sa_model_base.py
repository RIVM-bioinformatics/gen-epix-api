"""Verify shared SQLAlchemy mixins used by OmopDB mappings."""

import sqlalchemy as sa
from sqlalchemy_utils.types.uuid import UUIDType

from gen_epix.commondb.repositories.sa_model import NoIdRowMetadataMixin
from gen_epix.omopdb.repositories.sa_model import base

Base = sa.orm.declarative_base()
LineageRow = type(
    "LineageRow",
    (base.DataLineageMixin, Base),
    {
        "__tablename__": "lineage_row",
        "id": sa.orm.mapped_column(sa.Integer, primary_key=True),
    },
)


def test_data_lineage_mixin_adds_optional_columns() -> None:
    """Map provenance and bounded source-traceback columns as nullable."""
    columns = sa.inspect(LineageRow).columns

    assert isinstance(columns.provenance_id.type, UUIDType)
    assert columns.provenance_id.nullable
    assert isinstance(columns.source_traceback.type, sa.Unicode)
    assert columns.source_traceback.type.length == 255
    assert columns.source_traceback.nullable


def test_base_reexports_common_no_id_row_metadata_mixin() -> None:
    """Expose the common metadata mixin without wrapping or replacing it."""
    assert base.NoIdRowMetadataMixin is NoIdRowMetadataMixin
