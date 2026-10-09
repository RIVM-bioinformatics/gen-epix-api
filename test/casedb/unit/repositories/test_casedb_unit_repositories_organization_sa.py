"""Test casedb SQLAlchemy organization repository configuration."""

from sqlalchemy import create_engine

from gen_epix.casedb.domain import model
from gen_epix.casedb.repositories.organization_sa import OrganizationSARepository
from gen_epix.commondb.repositories import sa_model


def test_init_binds_casedb_domain_and_shared_sql_models():
    engine = create_engine("sqlite://")
    try:
        repository = OrganizationSARepository(engine, register_mappers=False)

        assert repository.user_class is model.User
        assert repository.user_invitation_class is model.UserInvitation
        assert repository.sa_user_class is sa_model.User
        assert repository.sa_user_invitation_class is sa_model.UserInvitation
    finally:
        engine.dispose()
