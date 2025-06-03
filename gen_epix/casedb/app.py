from gen_epix.casedb.app_setup import create_fast_api
from gen_epix.casedb.domain import enum
from gen_epix.casedb.domain.enum import ServiceType
from gen_epix.casedb.env import AppEnv
from util.cfg import AppCfg

APP_NAME = "CASEDB"

# Data for OpenAPI schema
# TODO: make the version in this file dynamic, e.g. from git tag or commit
SCHEMA_KWARGS = {
    "title": "Gen-EpiX",
    "summary": "Genomic Epidemiology platform for disease X",
    "description": "Gen-EpiX is platform for visualizing and analyzing genomic epidemiology data. It has fine-grained access controls for collaboration between multiple organizations.",
    "version": "0.0.0",
    "contact": {
        "name": "RIVM CIb IDS bioinformatics group",
        "url": "https://github.com/RIVM-bioinformatics/gen-epix-api",
        "email": "ids-bioinformatics@rivm.nl",
    },
    "license_info": {
        "name": "EUPL-1.2",
        "identifier": "EUPL-1.2",
    },
}

# Get configuration data and environment
APP_CFG = AppCfg(APP_NAME, enum.ServiceType, enum.RepositoryType)
APP_ENV = AppEnv(APP_CFG)

# Create fastapi
FAST_API = create_fast_api(
    APP_CFG.cfg,
    app=APP_ENV.app,
    registered_user_dependency=APP_ENV.registered_user_dependency,
    new_user_dependency=APP_ENV.new_user_dependency,
    idp_user_dependency=APP_ENV.idp_user_dependency,
    app_id=APP_ENV.app.generate_id(),
    setup_logger=APP_CFG.setup_logger,
    api_logger=APP_CFG.api_logger,
    debug=APP_CFG.cfg.app.debug,
    update_openapi_schema=True,
    update_openapi_kwargs={
        "get_openapi_kwargs": SCHEMA_KWARGS,
        "fix_schema": True,
        "auth_service": APP_ENV.services[ServiceType.AUTH],
    },
)

# TODO: app variable added for backwards compatibility with startup code that imports "app". Remove once that code is updated as well.
app = FAST_API
