"""Test shared system service operations."""

import json
import logging
from importlib import import_module
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from test.util.mock_compat import MagicMock, Mock, patch

import pytest

from gen_epix.commondb import policies
from gen_epix.commondb.domain import command, model
from gen_epix.commondb.policies.model_metadata_policy import ModelMetadataPolicy
from gen_epix.commondb.services.system import SystemService
from gen_epix.fastapp import CrudOperation, EventTiming
from gen_epix.fastapp.domain import Domain


def _write_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: str
) -> None:
    pyproject_path = tmp_path / SystemService.REQUIREMENTS_FILE_NAME
    pyproject_path.write_text(content, encoding="utf-8")
    monkeypatch.setattr(
        f"{SystemService.__module__}.get_package_root", lambda: tmp_path
    )
    SystemService._parse_and_get_package_metadata.cache_clear()


def _make_operational_data_service(
    app_name: str, handle
) -> tuple[Mock, type, SystemService]:
    """Create a system service whose app dispatches commands to ``handle``."""
    domain_module = import_module(f"gen_epix.{app_name}.domain")
    command_module = import_module(f"gen_epix.{app_name}.domain.command")
    app = Mock()
    app.domain = domain_module.DOMAIN
    app.handle.side_effect = handle
    service = object.__new__(SystemService)
    service._app = app
    service._logger = Mock()
    return app, command_module.DeleteAllOperationalDataCommand, service


@pytest.mark.parametrize("app_name", ["casedb", "seqdb", "omopdb"])
def test_delete_all_operational_data_dispatches_each_model_in_order(
    app_name: str,
) -> None:
    """Delete every declared operational model and report individual failures."""
    failed_index = 1
    failed_models: list = []

    def handle(crud_command):
        if crud_command.MODEL_CLASS is failed_models[0]:
            raise RuntimeError("delete failed")
        return 7

    app, command_class, service = _make_operational_data_service(app_name, handle)
    failed_models.append(
        command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES[failed_index]
    )

    result = service.delete_all_operational_data(command_class(user=None))

    expected_models = command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES
    dispatched_commands = [call.args[0] for call in app.handle.call_args_list]
    assert [
        crud_command.MODEL_CLASS for crud_command in dispatched_commands
    ] == expected_models
    assert all(
        crud_command.operation == CrudOperation.DELETE_ALL
        and crud_command.return_count
        and not crud_command.return_id
        for crud_command in dispatched_commands
    )
    assert result.success is False
    assert result.details == {
        model_class.ENTITY.name: (
            "RuntimeError: delete failed" if model_class is failed_models[0] else "7"
        )
        for model_class in expected_models
    }


@pytest.mark.parametrize("app_name", ["casedb", "seqdb", "omopdb"])
def test_delete_all_operational_data_deletes_in_batches_until_a_short_batch(
    app_name: str,
) -> None:
    """Repeat the delete per model until a batch is smaller than the batch size."""
    remaining: dict = {}

    def handle(crud_command):
        n_remaining = remaining.setdefault(crud_command.MODEL_CLASS, 2500)
        n_deleted = min(n_remaining, crud_command.limit)
        remaining[crud_command.MODEL_CLASS] = n_remaining - n_deleted
        return n_deleted

    app, command_class, service = _make_operational_data_service(app_name, handle)

    result = service.delete_all_operational_data(command_class(user=None))

    assert result.success is True
    assert set(result.details.values()) == {"2500"}
    for model_class in command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES:
        batch_size = command_class.get_batch_size(model_class)
        calls = [
            call.args[0]
            for call in app.handle.call_args_list
            if call.args[0].MODEL_CLASS is model_class
        ]
        assert all(crud_command.limit == batch_size for crud_command in calls)
        assert len(calls) == 2500 // batch_size + 1


def test_delete_all_operational_data_one_more_call_when_the_last_batch_is_full() -> (
    None
):
    """A table with exactly a batch of rows needs a second call to see it is empty."""
    remaining: dict = {}

    def handle(crud_command):
        n_remaining = remaining.setdefault(crud_command.MODEL_CLASS, crud_command.limit)
        n_deleted = min(n_remaining, crud_command.limit)
        remaining[crud_command.MODEL_CLASS] = n_remaining - n_deleted
        return n_deleted

    app, command_class, service = _make_operational_data_service("casedb", handle)

    result = service.delete_all_operational_data(command_class(user=None))

    assert result.success is True
    n_models = len(command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES)
    assert app.handle.call_count == 2 * n_models
    assert set(result.details.values()) == {str(command_class.BATCH_SIZE)}


def test_delete_all_operational_data_logs_every_batch_and_each_model() -> None:
    """Log one line per batch, one per finished model and one per failed model."""
    failed_models: list = []
    remaining: dict = {}

    def handle(crud_command):
        if crud_command.MODEL_CLASS is failed_models[0]:
            raise RuntimeError("delete failed")
        n_remaining = remaining.setdefault(crud_command.MODEL_CLASS, 1)
        n_deleted = min(n_remaining, crud_command.limit)
        remaining[crud_command.MODEL_CLASS] = n_remaining - n_deleted
        return n_deleted

    app, command_class, service = _make_operational_data_service("casedb", handle)
    app.create_log_message.side_effect = lambda code, msg, **kwargs: f"{code} {msg}"
    failed_models.append(command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES[0])

    service.delete_all_operational_data(command_class(user=None))

    messages = [call.args[1] for call in service._logger.log.call_args_list]
    levels = [call.args[0] for call in service._logger.log.call_args_list]
    n_models = len(command_class.SORTED_OPERATIONAL_DATA_MODEL_CLASSES)
    # Failed model: one error line. Other models: one short batch and one summary
    # line each.
    assert len(messages) == 1 + (n_models - 1) * 2
    assert levels[0] == logging.ERROR
    assert "failed after 0 records" in messages[0]
    assert sum("Deleted batch 1 of" in m for m in messages) == n_models - 1
    assert sum("Deleted all 1 records" in m for m in messages) == n_models - 1


def test_seqdb_seq_uses_a_smaller_batch_size() -> None:
    """Delete the large SEQDB sequence rows in smaller batches than the default."""
    from gen_epix.seqdb.domain import model as seqdb_model
    from gen_epix.seqdb.domain.command import DeleteAllOperationalDataCommand

    assert DeleteAllOperationalDataCommand.get_batch_size(seqdb_model.Seq) == 100
    assert (
        DeleteAllOperationalDataCommand.get_batch_size(seqdb_model.Sample)
        == DeleteAllOperationalDataCommand.BATCH_SIZE
    )


@pytest.mark.parametrize("app_name", ["casedb", "seqdb", "omopdb"])
def test_delete_all_ref_data_requires_empty_operational_models(app_name: str) -> None:
    """Do not delete reference data while a domain operational model has records."""
    domain_module = import_module(f"gen_epix.{app_name}.domain")
    command_module = import_module(f"gen_epix.{app_name}.domain.command")
    command_class = command_module.DeleteAllRefDataCommand
    app = Mock()
    app.domain = domain_module.DOMAIN
    ref_models = set(command_class.SORTED_REF_DATA_MODEL_CLASSES)
    linked_models = set(ref_models)
    persistable_models = app.domain.get_dag_sorted_models(persistable=True)
    while True:
        newly_linked_models = {
            model_class
            for model_class in persistable_models
            if model_class not in linked_models
            and any(
                link.link_model_class in linked_models
                for link in app.domain.get_model_links(model_class).values()
            )
        }
        if not newly_linked_models:
            break
        linked_models.update(newly_linked_models)
    operational_models = [
        model_class
        for model_class in app.domain.get_dag_sorted_models(
            persistable=True, reverse=True
        )
        if model_class in linked_models and model_class not in ref_models
    ]
    remaining_model = operational_models[0]

    def handle(crud_command):
        if crud_command.operation is CrudOperation.READ_ALL:
            return [object()] if crud_command.MODEL_CLASS is remaining_model else []
        raise AssertionError("reference deletion should not start")

    app.handle.side_effect = handle
    service = object.__new__(SystemService)
    service._app = app

    result = service.delete_all_ref_data(command_class(user=None))

    assert result.success is False
    assert remaining_model.ENTITY.name in result.details
    assert "delete all operational data" in result.details[remaining_model.ENTITY.name]
    assert all(
        call.args[0].operation is CrudOperation.READ_ALL
        for call in app.handle.call_args_list
    )
    assert all(call.args[0].limit == 1 for call in app.handle.call_args_list)
    assert all(call.args[0].return_id for call in app.handle.call_args_list)


def test_delete_all_ref_data_keeps_casedb_user_policies_and_their_targets() -> None:
    """Delete organization policies but keep user policies and the sets they use."""
    from gen_epix.casedb.domain import DOMAIN, command, model

    app = Mock()
    app.domain = DOMAIN
    app.handle.return_value = []
    service = object.__new__(SystemService)
    service._app = app

    result = service.delete_all_ref_data(command.DeleteAllRefDataCommand(user=None))

    assert result.success
    delete_commands = [
        call.args[0]
        for call in app.handle.call_args_list
        if call.args[0].operation is CrudOperation.DELETE_ALL
    ]
    deleted_models = [crud_command.MODEL_CLASS for crud_command in delete_commands]
    assert {
        model.OrganizationAccessCasePolicy,
        model.OrganizationShareCasePolicy,
        model.CaseTypeSetMember,
        model.ColSetMember,
    } <= set(deleted_models)
    assert not {
        model.UserAccessCasePolicy,
        model.UserShareCasePolicy,
        model.CaseTypeSet,
        model.CaseTypeSetCategory,
        model.ColSet,
    } & set(deleted_models)
    assert result.details.keys().isdisjoint(
        {
            model.UserAccessCasePolicy.ENTITY.name,
            model.UserShareCasePolicy.ENTITY.name,
        }
    )


def test_delete_all_ref_data_reports_missing_crud_command() -> None:
    """Report a missing CRUD mapping instead of silently leaving data behind."""
    from gen_epix.casedb.domain import DOMAIN, command

    app = Mock()
    app.domain = DOMAIN
    app.handle.return_value = []
    missing_model = command.DeleteAllRefDataCommand.SORTED_REF_DATA_MODEL_CLASSES[0]
    original_get_crud_command = DOMAIN.get_crud_command_for_model

    def get_crud_command(model_class):
        if model_class is missing_model:
            raise LookupError("missing CRUD command")
        return original_get_crud_command(model_class)

    service = object.__new__(SystemService)
    service._app = app

    with patch.object(
        DOMAIN, "get_crud_command_for_model", side_effect=get_crud_command
    ):
        result = service.delete_all_ref_data(command.DeleteAllRefDataCommand(user=None))

    assert result.success is False
    assert (
        result.details[missing_model.ENTITY.name] == "LookupError: missing CRUD command"
    )


def test_package_metadata_supports_missing_project_urls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_pyproject(
        tmp_path,
        monkeypatch,
        '[project]\nname = "gen-epix-api"\nversion = "1.2.3"\n' 'license = "MIT"\n',
    )

    packages = SystemService._parse_and_get_package_metadata()

    assert len(packages) == 1
    assert packages[0].version == "1.2.3"
    assert packages[0].license == "MIT"
    assert packages[0].homepage is None


def test_init_resolves_concrete_policy_classes() -> None:
    class OutagePolicy:
        pass

    class MetadataPolicy:
        pass

    app = Mock()
    app.impl.get_mapped_class.side_effect = {
        policies.HasSystemOutagePolicy: OutagePolicy,
        ModelMetadataPolicy: MetadataPolicy,
    }.get

    service = SystemService(app, register_handlers=False)

    assert service.has_system_outage_policy_class is OutagePolicy
    assert service.model_metadata_policy_class is MetadataPolicy


def test_register_policies_uses_before_and_after_timings() -> None:
    command_classes = [command.RetrieveOutagesCommand, command.RetrieveLicensesCommand]
    app = Mock()
    app.domain.commands = command_classes
    service = object.__new__(SystemService)
    service._app = app
    service.has_system_outage_policy_class = Mock(return_value="outage-policy")
    service.model_metadata_policy_class = Mock(return_value="metadata-policy")

    service.register_policies()

    assert app.register_policy.call_args_list == [
        ((command_class, "outage-policy", EventTiming.BEFORE), {})
        for command_class in command_classes
    ] + [
        ((command_class, "metadata-policy", EventTiming.AFTER), {})
        for command_class in command_classes
    ]
    service.model_metadata_policy_class.assert_called_once_with(
        role_set_map=app.impl.role_set_map
    )


def test_retrieve_outages_and_feature_flags() -> None:
    outages = [object()]
    app = Mock()
    app.feature_flags = {object(): True}
    service = object.__new__(SystemService)
    service._app = app
    service._repository = MagicMock()
    service.repository.uow.return_value.__enter__.return_value = "uow"
    service.repository.crud.return_value = outages

    assert (
        service.retrieve_outages(command.RetrieveOutagesCommand(user=None)) == outages
    )
    service.repository.crud.assert_called_once_with(
        "uow", None, model.Outage, CrudOperation.READ_ALL
    )
    assert (
        service.retrieve_feature_flags(command.RetrieveFeatureFlagsCommand(user=None))
        is app.feature_flags
    )


def test_retrieve_licenses_returns_parsed_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    packages = [object()]
    monkeypatch.setattr(
        SystemService, "_parse_and_get_package_metadata", staticmethod(lambda: packages)
    )
    service = object.__new__(SystemService)

    assert (
        service.retrieve_licenses(command.RetrieveLicensesCommand(user=None))
        is packages
    )


def test_linked_models_are_found_transitively_in_reverse_order() -> None:
    class Ref:
        pass

    class DirectDependent:
        pass

    class IndirectDependent:
        pass

    class Unrelated:
        pass

    models = [Ref, DirectDependent, IndirectDependent, Unrelated]
    links = {
        DirectDependent: {1: Mock(link_model_class=Ref)},
        IndirectDependent: {1: Mock(link_model_class=DirectDependent)},
    }
    domain = Mock(spec=Domain)

    def get_models(*, persistable: bool, reverse: bool = False) -> list[type]:
        assert persistable
        return list(reversed(models)) if reverse else models

    domain.get_dag_sorted_models.side_effect = get_models
    domain.get_model_links.side_effect = lambda model_class: links.get(model_class, {})

    assert SystemService._get_models_linked_to_ref_data(domain, {Ref}) == [
        IndirectDependent,
        DirectDependent,
    ]


def test_delete_all_ref_data_reports_operational_lookup_failure() -> None:
    from gen_epix.casedb.domain import DOMAIN
    from gen_epix.casedb.domain import command as casedb_command

    command_class = casedb_command.DeleteAllRefDataCommand
    operational_models = SystemService._get_models_linked_to_ref_data(
        DOMAIN, set(command_class.SORTED_REF_DATA_MODEL_CLASSES)
    )
    failed_model = operational_models[0]
    app = Mock()
    app.domain = DOMAIN

    def handle(crud_command):
        if crud_command.MODEL_CLASS is failed_model:
            raise RuntimeError("could not read operational data")
        return []

    app.handle.side_effect = handle
    service = object.__new__(SystemService)
    service._app = app

    result = service.delete_all_ref_data(command_class(user=None))

    assert result.success is False
    assert result.details[failed_model.ENTITY.name] == (
        "RuntimeError: could not read operational data"
    )
    assert all(
        call.args[0].operation is CrudOperation.READ_ALL
        for call in app.handle.call_args_list
    )


def test_delete_all_ref_data_continues_after_delete_failure() -> None:
    from gen_epix.casedb.domain import DOMAIN
    from gen_epix.casedb.domain import command as casedb_command

    command_class = casedb_command.DeleteAllRefDataCommand
    failed_model = command_class.SORTED_REF_DATA_MODEL_CLASSES[0]
    app = Mock()
    app.domain = DOMAIN

    def handle(crud_command):
        if crud_command.operation is CrudOperation.DELETE_ALL:
            if crud_command.MODEL_CLASS is failed_model:
                raise RuntimeError("delete failed")
            return []
        return []

    app.handle.side_effect = handle
    service = object.__new__(SystemService)
    service._app = app

    result = service.delete_all_ref_data(command_class(user=None))

    assert result.success is False
    assert result.details[failed_model.ENTITY.name] == "RuntimeError: delete failed"
    assert sum(
        call.args[0].operation is CrudOperation.DELETE_ALL
        for call in app.handle.call_args_list
    ) == len(command_class.SORTED_REF_DATA_MODEL_CLASSES)


def test_package_metadata_skips_missing_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        f"{SystemService.__module__}.get_package_root", lambda: tmp_path
    )
    SystemService._parse_and_get_package_metadata.cache_clear()

    assert SystemService._parse_and_get_package_metadata() == []


def test_package_metadata_reads_dependency_homepage_and_skips_missing_packages(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_pyproject(
        tmp_path,
        monkeypatch,
        '[project]\nversion = "1.2.3"\n'
        'dependencies = ["demo_pkg>=1", "!!!", "missing_pkg>=1"]\n'
        '[project.urls]\nHomepage = "https://project.example"\n',
    )

    def get_metadata(package_name: str) -> dict[str, str]:
        if package_name == "missing_pkg":
            raise PackageNotFoundError(package_name)
        return {
            "Name": "demo-pkg",
            "Version": "4.5",
            "License": "BSD",
            "Project-URL": "Documentation, https://dependency.example",
        }

    with patch(
        f"{SystemService.__module__}.importlib.metadata.metadata",
        side_effect=get_metadata,
    ) as metadata:
        packages = SystemService._parse_and_get_package_metadata()

    metadata.assert_any_call("demo_pkg")
    metadata.assert_any_call("missing_pkg")
    assert [package.name for package in packages] == ["gen-epix-api", "demo-pkg"]
    assert packages[0].homepage == "https://project.example"
    assert packages[1].homepage == "https://dependency.example"


@pytest.mark.parametrize(
    ("urls", "expected"),
    [
        ("", ""),
        ("Docs, https://docs.example", "https://docs.example"),
        (
            "Repository, https://repo.example\nHomepage, https://home.example",
            "https://home.example",
        ),
        (
            "Custom Link, https://first.example\nOther, https://second.example",
            "https://first.example",
        ),
        ("invalid entry\nmissing delimiter", ""),
    ],
    ids=[
        "empty",
        "documentation-fallback",
        "homepage-priority",
        "first-url",
        "invalid",
    ],
)
def test_extract_homepage_from_project_urls(urls: str, expected: str) -> None:
    assert SystemService._extract_homepage_from_project_urls(urls) == expected


def test_normalize_project_url_label_removes_punctuation_and_whitespace() -> None:
    assert SystemService._normalize_project_url_label(" Source-Code ") == "sourcecode"
