"""Compose and expose the configured SeqDB FastAPI application."""

from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg
from gen_epix.seqdb.api.router import create_routers
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.env import AppComposer
from gen_epix.util import get_package_version

APP_NAME = "SEQDB"

# Data for OpenAPI schema
SCHEMA_KWARGS = {
    "title": "Gen-EpiX seqdb",
    "summary": "Genomic Epidemiology platform for disease X, seqdb app",
    "description": "The seqdb app manages genomic sequencing data.",
    "version": get_package_version(),
    "terms_of_service": "http://example.com/terms/",
    "contact": {
        "name": "RIVM CIb IDS bioinformatics group",
        "url": "https://github.com/RIVM-bioinformatics/gen-epix-api",
        "email": "ids-bioinformatics@rivm.nl",
    },
    "license_info": {
        "name": "License to be confirmed",
        "identifier": "Apache-2.0",
    },
}

# Get configuration data and environment
APP_CFG = AppCfg(APP_NAME, enum.ServiceType, enum.RepositoryType)
APP_COMPOSER = AppComposer(APP_CFG)

# Create fastapi
FAST_API = create_fast_api(
    app=APP_COMPOSER.app,
    create_routers_fn=create_routers,
    setup_logger=APP_CFG.setup_logger,
    api_logger=APP_CFG.api_logger,
    debug=APP_CFG.cfg.app.debug,
    update_openapi_schema=True,
    update_openapi_kwargs={
        "get_openapi_kwargs": SCHEMA_KWARGS,
        "fix_schema": True,
        "auth_service": APP_COMPOSER.services[enum.ServiceType.AUTH],
    },
)

# TODO: app variable added for backwards compatibility with startup code that imports "app". Remove once that code is updated as well.
app = FAST_API
