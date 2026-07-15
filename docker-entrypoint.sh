#!/bin/bash
set -e

# Add the app directory to Python path
export PYTHONPATH="/app:$PYTHONPATH"

# Change to the config directory so relative paths resolve correctly
cd /lsp-data/

# Use APP_TYPE env var (defaults to CASEDB if not set)
APP_TYPE="${APP_TYPE:-CASEDB}"

# Run the FastAPI app
python << EOF
from pathlib import Path
import sys
sys.path.insert(0, "/lsp-data")

from test.config.common.PPR_test_dict_app.local_dict_app_ppr_dataset import init_fastapi_app
from gen_epix.commondb.domain.enum import AppType

app_type_str = "$APP_TYPE"
app_type = AppType[app_type_str]
init_fastapi_app(app_type, reload=False)
EOF