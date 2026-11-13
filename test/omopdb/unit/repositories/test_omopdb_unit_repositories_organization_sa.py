from sqlalchemy import create_engine

from gen_epix.omopdb.domain import model
from gen_epix.omopdb.repositories import sa_model
from gen_epix.omopdb.repositories.organization_sa import OrganizationSARepository


def test_uses_omopdb_user_models() -> None:
    """Configure shared storage with OMOP domain and SQLAlchemy user models."""
    engine = create_engine("sqlite://")
    try:
        repository = OrganizationSARepository(engine)

        assert repository.user_class is model.User
        assert repository.user_invitation_class is model.UserInvitation
        assert repository.sa_user_class is sa_model.User
        assert repository.sa_user_invitation_class is sa_model.UserInvitation
    finally:
        engine.dispose()
