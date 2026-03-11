from test.test_client.enum import ServerType
from test.test_client.server_manager import ServerManager


def test_base_url_uses_configured_host_for_auth_server() -> None:
    server = ServerManager(
        service=ServerType.OAUTH,
        host="127.0.0.1",
        port=9100,
    )

    assert server.base_url == "http://127.0.0.1:9100"
    assert (
        server.get_discovery_url()
        == "http://127.0.0.1:9100/.well-known/openid-configuration"
    )


def test_base_url_uses_configured_host_for_non_auth_server() -> None:
    server = ServerManager(
        service=ServerType.SEQDB,
        host="127.0.0.2",
        port=8101,
        app_import_path="gen_epix.seqdb.app:app",
    )

    assert server.base_url == "http://127.0.0.2:8101"
