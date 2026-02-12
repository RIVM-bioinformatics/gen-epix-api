from gen_epix.commondb.app_setup import create_fast_api
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb import enum
from gen_epix.commondb.env import AppComposer
from gen_epix.util import get_package_version

APP_NAME = "COMMONDB"

# Data for OpenAPI schema
SCHEMA_KWARGS = {
    "title": "Gen-EpiX commondb basis for casedb, seqdb and omopdb apps",
    "summary": "Genomic Epidemiology platform for disease X, commondb app",
    "description": "The commondb app is meant for testing the common aspects of the actual applications.",
    "version": get_package_version(),
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
APP_COMPOSER = AppComposer(APP_CFG)

# Create fastapi
FAST_API = create_fast_api(
    app=APP_COMPOSER.app,
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
