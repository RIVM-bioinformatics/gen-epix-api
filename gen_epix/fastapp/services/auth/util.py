from typing import Any

from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import AuthProtocol
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.literal import EMAIL_PATTERN
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oidc_client import OidcClient


def get_email_from_claims(
    claims: dict[str, Any],
) -> str | None:
    email = claims.get("email")
    if email is None:
        for claim in claims.values():
            if isinstance(claim, str) and EMAIL_PATTERN.match(claim.lower()):
                return claim.lower()
    else:
        return email.lower()
    return None


def get_name_from_claims(
    claims: dict[str, Any], name_claims: list[str | list[str]]
) -> str | None:
    """
    Get the name from the claims, checking against a list of possible name claims.
    """
    for name_claim in name_claims:
        if isinstance(name_claim, str):
            if name_claim in claims:
                return str(claims[name_claim])
        else:
            # Check if every subclaim exists and if so return space concatenated string
            values = [claims[x] for x in name_claim if x in claims]
            if len(values) == len(name_claim):
                return " ".join(str(x) for x in values)
    return None


def create_idp_clients_from_config(
    app: App, idps_cfg: list[dict[str, str | list]] | None
) -> list[IdpClient]:
    if not idps_cfg:
        idps_cfg = []
    idp_clients: list[IdpClient] = []
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

        oidc_discovery_doc_keys = set(OidcServerCfg.model_fields.keys())
        try:
            protocol = AuthProtocol[str(idp_cfg["protocol"])]
            if protocol == AuthProtocol.OIDC:
                discovery_doc = {
                    x: y for x, y in idp_cfg.items() if x in oidc_discovery_doc_keys
                }
                idp_client = OidcClient(
                    OidcServerCfg(**idp_cfg),  # type: ignore
                    logger=logger,
                    log_item_class=app.log_item_class,
                    discovery_doc=discovery_doc,  # Provide again to avoid fetching from discovery URL (again)
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
        if isinstance(idp_client, OidcClient):
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
