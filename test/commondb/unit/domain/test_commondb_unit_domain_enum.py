from gen_epix.commondb.domain.enum import FeatureFlag


def test_feature_flag_has_no_auto_create_new_users_member() -> None:
    """Auth's auto-create flag is intentionally owned by FastApp's enum."""
    assert "AUTO_CREATE_NEW_USERS" not in FeatureFlag.__members__
