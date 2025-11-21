import ssl
from collections.abc import Hashable
from pathlib import Path

LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def serialize_id(value: Hashable) -> str | None:
    return str(value) if value else None


def create_ssl_context(
    host: str, ssl_cert_file: Path | str | None = None, disable_ssl_verification: bool = False
) -> ssl.SSLContext | bool:
    """Get SSL verification setting using similar logic to OidcClient."""
    if disable_ssl_verification:
        return False

    # For local development hosts, disable verification
    if host in LOCAL_HOSTS:
        return False

    # If a cert file is given, use that for verification
    if ssl_cert_file is not None:
        if isinstance(ssl_cert_file, str):
            ssl_cert_file = Path(ssl_cert_file)
        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(ssl_cert_file.absolute().as_posix())
        return ssl_context

    # Use default verification
    return True
