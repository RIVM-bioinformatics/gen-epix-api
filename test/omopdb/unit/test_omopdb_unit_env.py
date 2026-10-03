"""Unit tests for the omopdb application composers."""

# pylint: disable=duplicate-code

from test.util.mock_compat import Mock, patch

from gen_epix.omopdb import env


def _assert_composer_forwards_configuration(composer_class, base_class) -> None:
    app_cfg = Mock()

    with patch.object(base_class, "__init__", return_value=None) as init:
        composer_class(app_cfg, log_setup=False, custom_option="value")

    init.assert_called_once_with(
        app_cfg,
        log_setup=False,
        domain=env.DOMAIN,
        sorted_service_types=env.model.SORTED_SERVICE_TYPES,
        model_class_map=env.model.COMMON_MODEL_MAP,
        command_class_map=env.command.COMMON_COMMAND_MAP,
        policy_class_map=env.COMMON_POLICY_MAP,
        role_generator_class=env.RoleGenerator,
        rbac_service_class=env.RbacService,
        custom_option="value",
    )


def test_app_composer_forwards_configuration() -> None:
    """Forward omopdb registrations to the shared application composer."""
    _assert_composer_forwards_configuration(env.AppComposer, env.CommonAppComposer)


def test_no_app_composer_forwards_configuration() -> None:
    """Forward omopdb registrations to the shared no-app composer."""
    _assert_composer_forwards_configuration(env.NoAppComposer, env.CommonNoAppComposer)
