import ssl
from collections.abc import Hashable
from pathlib import Path

LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def serialize_id(value: Hashable) -> str | None:
    return str(value) if value else None


def create_ssl_context(
    host: str,
    ssl_cert_file: Path | str | None = None,
    disable_ssl_verification: bool = False,
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
        # Enforce TLS 1.2/1.3 and restrict ciphers to match ingress controller
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        ssl_context.set_ciphers(
            "ECDHE-RSA-AES256-GCM-SHA384:"
            "ECDHE-RSA-AES128-GCM-SHA256:"
            "ECDHE-ECDSA-AES256-GCM-SHA384:"
            "ECDHE-ECDSA-AES128-GCM-SHA256"
        )
        return ssl_context

    # Use default verification
    return True
