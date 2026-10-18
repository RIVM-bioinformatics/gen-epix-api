from gen_epix.commondb.domain import model
from gen_epix.commondb.repositories.sa_model.system import Outage


def test_outage_table_matches_domain_model() -> None:
    columns = Outage.__table__.columns

    assert Outage.__tablename__ == model.Outage.ENTITY.table_name
    for field_name, field_info in model.Outage.model_fields.items():
        assert field_name in columns
        expected_nullable = not field_info.is_required()
        if field_name in {"id", "created_at", "modified_at"}:
            expected_nullable = False
        assert columns[field_name].nullable is expected_nullable
