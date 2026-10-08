from datetime import datetime, timezone
from test.util.mock_compat import MagicMock, Mock, patch
from types import SimpleNamespace
from uuid import UUID

from gen_epix.fastapp.enum import AuthProtocol, HttpMethod
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.client import OmopdbClient


def _fake_app_init(self: object, domain: object, **kwargs: object) -> None:
    setattr(self, "_domain", domain)
    setattr(self, "_logger", None)
    setattr(self, "_command_handler_map", {})
    setattr(self, "_command_listeners", {})
    setattr(self, "_command_stack", [])


def _make_app() -> OmopdbClient:
    domain = SimpleNamespace(crud_commands=[])
    with (
        patch("gen_epix.omopdb.services.client.DOMAIN", domain),
        patch("gen_epix.fastapp.client.App.__init__", _fake_app_init),
    ):
        return OmopdbClient(
            host="example.org",
            port=8000,
            auth_protocol=AuthProtocol.NONE,
        )


def test_registers_person_retrieval_routes_and_handlers() -> None:
    app = _make_app()

    query_cmd = command.RetrievePersonsByQueryCommand(
        person_query=model.PersonQuery(
            modified_since=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
    )
    ids_cmd = command.RetrievePersonsByIdCommand(
        person_ids=[UUID("11111111-1111-1111-1111-111111111111")]
    )

    assert app.get_route(query_cmd).endswith("/retrieve/person_ids_by_query")
    assert app.get_route(ids_cmd).endswith("/retrieve/persons_by_ids")
    assert (
        app.get_handler(type(query_cmd)).__func__
        is OmopdbClient.retrieve_persons_by_query
    )
    assert (
        app.get_handler(type(ids_cmd)).__func__ is OmopdbClient.retrieve_persons_by_id
    )


def test_retrieve_persons_by_query_posts_query_body() -> None:
    app = _make_app()
    query = model.PersonQuery(
        modified_since=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    cmd = command.RetrievePersonsByQueryCommand(person_query=query)
    response_payload = {
        "person_query": query.model_dump(mode="json"),
        "person_ids": ["11111111-1111-1111-1111-111111111111"],
        "is_max_results_exceeded": False,
    }
    response = Mock()
    response.raise_for_status.return_value = None
    response.content = b"1"
    response.json.return_value = response_payload
    client = Mock()
    client.request.return_value = response
    client_context = MagicMock()
    client_context.__enter__.return_value = client
    client_context.__exit__.return_value = None

    with (
        patch.object(app, "get_client", return_value=client_context),
        patch.object(app, "get_headers", return_value={"X-Test": "1"}),
    ):
        result = app.retrieve_persons_by_query(cmd)

    assert result.person_ids == [UUID("11111111-1111-1111-1111-111111111111")]
    client.request.assert_called_once()
    method, posted_route = client.request.call_args.args
    posted_json = client.request.call_args.kwargs["json"]
    assert method == "POST"
    assert posted_route.endswith("/retrieve/person_ids_by_query")
    assert posted_json == query.model_dump(mode="json")


def test_upload_persons_sends_command_and_parses_result() -> None:
    app = _make_app()
    cmd = command.UploadPersonsCommand(
        person_batch=model.PersonBatchForUpload(persons=[])
    )
    response = {
        "batch_id": "11111111-1111-1111-1111-111111111111",
        "persons": [],
    }

    with patch.object(app, "request", return_value=response) as request:
        result = app.upload_persons(cmd)

    assert result == model.PersonBatchUploadResult(**response)
    request.assert_called_once_with(cmd, HttpMethod.POST, model=cmd, exclude={"user"})


def test_retrieve_persons_by_id_posts_ids_and_parses_response() -> None:
    app = _make_app()
    person_id = UUID("11111111-1111-1111-1111-111111111111")
    cmd = command.RetrievePersonsByIdCommand(person_ids=[person_id])

    with patch.object(app, "request", return_value=[]) as request:
        result = app.retrieve_persons_by_id(cmd)

    assert result == []
    request.assert_called_once()
    assert request.call_args.args == (cmd, HttpMethod.POST)
    assert request.call_args.kwargs["model"].person_ids == [person_id]


def test_retrieve_specimen_ids_by_cohort_ids_posts_cohort_data() -> None:
    app = _make_app()
    cohort_definition_id = UUID("11111111-1111-1111-1111-111111111111")
    cohort_id = UUID("22222222-2222-2222-2222-222222222222")
    cmd = command.RetrieveSpecimenIdsByCohortIdsCommand(
        cohort_definition_id=cohort_definition_id,
        cohort_ids=[cohort_id],
    )
    response = {"specimen_ids_by_cohort_id": {}}

    with patch.object(app, "request", return_value=response) as request:
        result = app.retrieve_specimen_ids_by_cohort_ids(cmd)

    assert result == model.SpecimenIdsByCohortResult(**response)
    request.assert_called_once()
    assert request.call_args.args == (cmd, HttpMethod.POST)
    body = request.call_args.kwargs["model"]
    assert body.cohort_definition_id == cohort_definition_id
    assert body.cohort_ids == [cohort_id]


def test_delete_all_ref_data_route_and_timeout_are_registered() -> None:
    assert OmopdbClient.ROUTE_MAP[command.DeleteAllRefDataCommand] == "/ref_data"
    assert OmopdbClient.DEFAULT_HTTP_TIMEOUTS[command.DeleteAllRefDataCommand] == 300.0
