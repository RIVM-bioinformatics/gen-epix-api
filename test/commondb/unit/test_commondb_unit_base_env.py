"""Unit tests for the shared application composer contract."""

from enum import Enum
from test.util.mock_compat import Mock, patch

import pytest

from gen_epix.commondb.base_env import BaseAppComposer
from gen_epix.commondb.domain.enum import RepositoryType, ServiceType
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository


def test_base_app_composer_init_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        BaseAppComposer()


def test_base_app_composer_properties_return_composition_state() -> None:
    composer = object.__new__(BaseAppComposer)
    state = {
        "_cfg": Mock(),
        "_app": Mock(),
        "_services": {},
        "_repositories": {},
        "_registered_user_dependency": Mock(),
        "_new_user_dependency": Mock(),
        "_idp_user_dependency": Mock(),
    }
    for name, value in state.items():
        setattr(composer, name, value)

    assert composer.cfg is state["_cfg"]
    assert composer.app is state["_app"]
    assert composer.services is state["_services"]
    assert composer.repositories is state["_repositories"]
    assert composer.registered_user_dependency is state["_registered_user_dependency"]
    assert composer.new_user_dependency is state["_new_user_dependency"]
    assert composer.idp_user_dependency is state["_idp_user_dependency"]


def test_create_dict_repository_forwards_file_and_options() -> None:
    entities = [Mock()]
    timestamp_factory = Mock()
    repository = Mock()
    repository_cfg = {"props": {"file": "repository.pkl.gz"}}

    with patch.object(
        DictRepository, "create_repository_from_pkl", return_value=repository
    ) as create_repository:
        result = BaseAppComposer.create_repository(
            ServiceType.ABAC,
            timestamp_factory,
            entities,
            RepositoryType.DICT,
            repository_cfg,
            DictRepository,
            option="value",
        )

    assert result is repository
    create_repository.assert_called_once_with(
        DictRepository,
        entities,
        "repository.pkl.gz",
        timestamp_factory=timestamp_factory,
        option="value",
    )


def test_create_dict_repository_requires_file() -> None:
    with pytest.raises(KeyError, match="file"):
        BaseAppComposer.create_repository(
            ServiceType.ABAC,
            Mock(),
            [],
            RepositoryType.DICT,
            {"props": {}},
            DictRepository,
        )


def test_create_sqlite_repository_converts_file_to_connection_string() -> None:
    entities = [Mock()]
    timestamp_factory = Mock()
    repository = Mock()

    with patch.object(
        SARepository, "create_sa_repository", return_value=repository
    ) as create_repository:
        result = BaseAppComposer.create_repository(
            ServiceType.ABAC,
            timestamp_factory,
            entities,
            RepositoryType.SA_SQLITE,
            {"props": {"file": "repository.sqlite"}},
            SARepository,
        )

    assert result is repository
    create_repository.assert_called_once_with(
        entities,
        connection_string="sqlite:///repository.sqlite",
        name=ServiceType.ABAC.value,
        timestamp_factory=timestamp_factory,
    )


def test_create_sqlite_repository_prefers_connection_string() -> None:
    with patch.object(
        SARepository, "create_sa_repository", return_value=Mock()
    ) as create_repository:
        BaseAppComposer.create_repository(
            ServiceType.ABAC,
            Mock(),
            [],
            RepositoryType.SA_SQLITE,
            {
                "props": {
                    "file": "ignored.sqlite",
                    "connection_string": "sqlite:///explicit.sqlite",
                }
            },
            SARepository,
        )

    assert create_repository.call_args.kwargs["connection_string"] == (
        "sqlite:///explicit.sqlite"
    )


def test_create_sqlite_repository_uses_memory_when_unconfigured() -> None:
    with patch.object(
        SARepository, "create_sa_repository", return_value=Mock()
    ) as create_repository:
        BaseAppComposer.create_repository(
            ServiceType.ABAC,
            Mock(),
            [],
            RepositoryType.SA_SQLITE,
            {},
            SARepository,
        )

    assert create_repository.call_args.kwargs["connection_string"] is None


def test_create_sqlite_repository_falls_back_from_empty_connection_string() -> None:
    with patch.object(
        SARepository, "create_sa_repository", return_value=Mock()
    ) as create_repository:
        BaseAppComposer.create_repository(
            ServiceType.ABAC,
            Mock(),
            [],
            RepositoryType.SA_SQLITE,
            {"props": {"file": "repository.sqlite", "connection_string": ""}},
            SARepository,
        )

    assert create_repository.call_args.kwargs["connection_string"] == (
        "sqlite:///repository.sqlite"
    )


def test_create_sqlite_repository_uses_memory_for_empty_connection_string() -> None:
    with patch.object(
        SARepository, "create_sa_repository", return_value=Mock()
    ) as create_repository:
        BaseAppComposer.create_repository(
            ServiceType.ABAC,
            Mock(),
            [],
            RepositoryType.SA_SQLITE,
            {"props": {"connection_string": ""}},
            SARepository,
        )

    assert create_repository.call_args.kwargs["connection_string"] is None


def test_create_sql_repository_forwards_connection_and_options() -> None:
    entities = [Mock()]
    timestamp_factory = Mock()
    repository = Mock()

    with patch.object(
        SARepository, "create_sa_repository", return_value=repository
    ) as create_repository:
        result = BaseAppComposer.create_repository(
            ServiceType.ABAC,
            timestamp_factory,
            entities,
            RepositoryType.SA_SQL,
            {"props": {"connection_string": "mssql+pyodbc://db"}},
            SARepository,
            option="value",
        )

    assert result is repository
    create_repository.assert_called_once_with(
        entities,
        connection_string="mssql+pyodbc://db",
        name=ServiceType.ABAC.value,
        timestamp_factory=timestamp_factory,
        option="value",
    )


def test_create_sql_repository_requires_connection_string() -> None:
    with pytest.raises(KeyError, match="connection_string"):
        BaseAppComposer.create_repository(
            ServiceType.ABAC,
            Mock(),
            [],
            RepositoryType.SA_SQL,
            {"props": {}},
            SARepository,
        )


def test_create_repository_rejects_unsupported_backend() -> None:
    class UnsupportedRepositoryType(Enum):
        """Represent a backend not supported by the composer."""

        UNSUPPORTED = "UNSUPPORTED"

    with pytest.raises(NotImplementedError):
        BaseAppComposer.create_repository(
            ServiceType.ABAC,
            Mock(),
            [],
            UnsupportedRepositoryType.UNSUPPORTED,
            {},
            SARepository,
        )
