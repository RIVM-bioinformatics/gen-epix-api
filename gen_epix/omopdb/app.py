"""Compose the configured OmopDB application and its FastAPI transport layer."""

from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.omopdb.api.router import create_routers
from gen_epix.omopdb.config import OmopdbAppCfg
from gen_epix.omopdb.domain import enum
from gen_epix.omopdb.env import AppComposer
from gen_epix.util import get_package_version

# Data for OpenAPI schema
SCHEMA_KWARGS = {
    "title": "Gen-EpiX omopdb",
    "summary": "Genomic Epidemiology platform for disease X, omopdb app",
    "description": "The omopdb app manages clinical and epidemiological data of persons or subjects of non-human origin.",
    "version": get_package_version(),
    "terms_of_service": "http://example.com/terms/",
    "contact": {
        "name": "RIVM CIb IDS bioinformatics group",
        "url": "https://github.com/RIVM-bioinformatics/gen-epix-api",
        "email": "ids-bioinformatics@rivm.nl",
    },
    "license_info": {
        "name": "European Union Public Licence Version 1.2",
        "identifier": "EUPL-1.2",
    },
}

# Get configuration data and environment
APP_CFG = OmopdbAppCfg()
APP_COMPOSER = AppComposer(APP_CFG)

# Create fastapi
FAST_API = create_fast_api(
    APP_COMPOSER.app,
    create_routers_fn=create_routers,
    setup_logger=APP_CFG.setup_logger,
    api_logger=APP_CFG.api_logger,
    debug=APP_CFG.cfg["app"]["debug"],
    update_openapi_schema=True,
    update_openapi_kwargs={
        "get_openapi_kwargs": SCHEMA_KWARGS,
        "fix_schema": True,
        "auth_service": APP_COMPOSER.services[enum.ServiceType.AUTH],
    },
)

# Keep the `app` alias while startup code still imports it.
app = FAST_API
