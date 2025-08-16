from gen_epix.common.config import AppCfg
from gen_epix.common.util import get_package_version
from gen_epix.omopdb.app_setup import create_fast_api
from gen_epix.omopdb.domain import enum
from gen_epix.omopdb.env import AppEnv

APP_NAME = "OMOPDB"

# Data for OpenAPI schema
SCHEMA_KWARGS = {
    "title": "BioBase master database",
    "description": "BioBase API",
    "summary": "Summary goes here",
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
        "auth_service": APP_ENV.services[enum.ServiceType.AUTH],
    },
)

# TODO: app variable added for backwards compatibility with startup code that imports "app". Remove once that code is updated as well.
app = FAST_API
