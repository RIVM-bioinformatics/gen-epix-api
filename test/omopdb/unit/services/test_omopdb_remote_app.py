from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID
from unittest.mock import MagicMock, Mock, patch

from gen_epix.fastapp.enum import AuthProtocol
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.remote_app import OmopdbRemoteApp


def _fake_app_init(self: object, domain: object, **kwargs: object) -> None:
    setattr(self, "_domain", domain)
    setattr(self, "_logger", None)
    setattr(self, "_command_handler_map", {})
    setattr(self, "_command_listeners", {})
    setattr(self, "_command_stack", [])


def _make_app() -> OmopdbRemoteApp:
    domain = SimpleNamespace(crud_commands=[])
    with patch("gen_epix.omopdb.services.remote_app.DOMAIN", domain), patch(
        "gen_epix.fastapp.remote_app.App.__init__", _fake_app_init
    ):
        return OmopdbRemoteApp(
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
    assert app.get_handler(type(query_cmd)).__func__ is OmopdbRemoteApp.retrieve_persons_by_query
    assert app.get_handler(type(ids_cmd)).__func__ is OmopdbRemoteApp.retrieve_persons_by_id


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
    response.json.return_value = response_payload
    client = Mock()
    client.post.return_value = response
    client_context = MagicMock()
    client_context.__enter__.return_value = client
    client_context.__exit__.return_value = None

    with patch.object(app, "get_client", return_value=client_context), patch.object(
        app, "get_headers", return_value={"X-Test": "1"}
    ):
        result = app.retrieve_persons_by_query(cmd)

    assert result.person_ids == [UUID("11111111-1111-1111-1111-111111111111")]
    client.post.assert_called_once()
    posted_route = client.post.call_args.args[0]
    posted_json = client.post.call_args.kwargs["json"]
    assert posted_route.endswith("/retrieve/person_ids_by_query")
    assert posted_json == query.model_dump(mode="json")
