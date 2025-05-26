from typing import Any

from gen_epix.fastapp import App, exc
from gen_epix.fastapp.enum import AuthProtocol
from gen_epix.fastapp.services.auth.idp_client import IDPClient
from gen_epix.fastapp.services.auth.literal import EMAIL_PATTERN
from gen_epix.fastapp.services.auth.model import OIDCConfiguration
from gen_epix.fastapp.services.auth.oidc_client import OIDCClient

OIDC_DISCOVERY_DOCUMENT_KEYS = {
    "issuer",
    "authorization_endpoint",
    "token_endpoint",
    "jwks_uri",
    "userinfo_endpoint",
    "response_types_supported",
    "subject_types_supported",
    "id_token_signing_alg_values_supported",
}


def get_email_from_claims(
    claims: dict[str, Any],
) -> str | None:
    if "email" in claims and isinstance(claims["email"], str):
        return claims["email"].lower()
    for claim in claims.values():
        if isinstance(claim, str) and EMAIL_PATTERN.match(claim.lower()):
            return claim.lower()
    return None


def create_idp_clients_from_config(
    app: App, idps_cfg: list[dict[str, str | list]] | None
) -> list[IDPClient]:
    if not idps_cfg:
        idps_cfg = []
    idp_clients: list[IDPClient] = []
    idp_names = set()
    idp_labels = set()
    logger = app.logger
    for idp_cfg in idps_cfg:
        idp_name = idp_cfg["name"]
        idp_label = idp_cfg["label"]
        if idp_name in idp_names or idp_label in idp_labels:
            msg = (
                "Authentication service name and/or label are not unique: "
                f"{idp_cfg['name']}, {idp_cfg['label']}"
            )
            if logger:
                logger.error(app.create_log_message("30a9a272", msg))
            raise exc.InitializationServiceError(msg)
        idp_names.add(idp_name)
        idp_labels.add(idp_label)

        try:
            protocol = AuthProtocol[str(idp_cfg["protocol"])]
            if protocol == AuthProtocol.OIDC:
                discovery_document = (
                    idp_cfg
                    if OIDC_DISCOVERY_DOCUMENT_KEYS.issubset(set(idp_cfg.keys()))
                    else None
                )
                idp_client = OIDCClient(
                    OIDCConfiguration(**idp_cfg),  # type: ignore
                    logger=logger,
                    log_item_class=app.log_item_class,
                    discovery_document=discovery_document,
                )
            else:
                raise exc.InitializationServiceError(
                    f"Protocol {protocol.value} not implemented"
                )
            idp_clients.append(idp_client)
        except Exception as exception:
            # Unable to initialize authentication service: do not raise
            # an error to avoid entire app not starting up
            msg = "Could not initialize authentication service " f"{idp_cfg['name']}"
            if logger:
                logger.error(
                    app.create_log_message("48b7e021", msg, exception=exception)
                )
    for idp_client in idp_clients:  # type: ignore
        if isinstance(idp_client, OIDCClient):
            if logger:
                logger.info(
                    app.create_log_message(
                        "7e0b64cc",
                        f"OIDC service on {idp_client._issuer} initialized",
                    )
                )
        else:
            raise exc.InitializationServiceError(
                f"Authentication service of type {type(idp_client)} " "not implemented"
            )
    return idp_clients
