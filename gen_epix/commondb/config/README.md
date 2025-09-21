# Configuration Management Refactoring

This document describes the refactored configuration management system that separates settings from secrets and provides multiple secret management strategies.

## Overview

The new configuration system uses the Strategy Pattern with a Factory to provide:

1. **Separate Settings and Secrets Management**: Clear separation between configuration settings and sensitive data
2. **Configurable App Prefixes**: Support for different applications (COMMONDB, CASEDB, SEQDB, OMOPDB)
3. **Multiple Secret Strategies**: Environment variables, file system, and Azure Key Vault
4. **Backward Compatibility**: Existing code continues to work with the new system

## Architecture

```
config/
├── settings/                    # Settings management
│   ├── manager.py              # SettingsManager class
│   ├── schema.py               # Pydantic validation schema
│   └── defaults.toml           # Default settings
├── secrets/                    # Secret management
│   ├── factory.py              # SecretProviderFactory
│   ├── schema.py               # Secret validation schema
│   └── strategies/             # Secret provider strategies
│       ├── base.py             # Abstract base class
│       ├── environment.py      # Environment variable provider
│       ├── file.py      # File-based provider
│       └── azure_kv.py         # Azure Key Vault provider
├── cfg_new.py                  # Refactored AppCfg class
└── examples/                   # Example configurations
```

## Environment Variables

### Core Configuration

The system uses configurable prefixes based on the application:

- **COMMONDB**: `COMMONDB_*`
- **CASEDB**: `CASEDB_*`
- **SEQDB**: `SEQDB_*`
- **OMOPDB**: `OMOPDB_*`

### Required Environment Variables

```bash
# Secret strategy (required)
{APP_PREFIX}_SECRETS_STRATEGY=environment|file|azure_key_vault

# Logging configuration (required)
{APP_PREFIX}_LOGGING_CONFIG_FILE=/path/to/logging.yaml
```

### Optional Environment Variables

```bash
# Custom settings file (optional - uses defaults if not provided)
{APP_PREFIX}_SETTINGS_FILES=/path/to/custom/settings.toml

# Whether to use log level from secrets (default: 1)
{APP_PREFIX}_LOGGING_LEVEL_FROM_SECRET=1

# Identity provider configuration (optional)
{APP_PREFIX}_IDPS_CONFIG_FILE=/path/to/idps.json
```

## Settings Management

### Default Settings

Settings are loaded from `settings/defaults.toml` and can be overridden by:

1. **Custom Settings File**: Set `{APP_PREFIX}_SETTINGS_FILE` environment variable
2. **Environment Variable Overrides**: Use double underscore for nesting

### Environment Variable Overrides

Use double underscores (`__`) to represent nested configuration paths:

```bash
# Override app.host
COMMONDB_APP__HOST=localhost

# Override api.http_header.general.CacheControl
COMMONDB_API__HTTP_HEADER__GENERAL__CACHECONTROL="no-store"

# Override service.rbac.user_invitation_time_to_live
COMMONDB_SERVICE__RBAC__USER_INVITATION_TIME_TO_LIVE=86400
```

## Secret Management Strategies

### 1. Environment Variables Strategy

Set `{APP_PREFIX}_SECRETS_STRATEGY=environment`

**Configuration:**
```bash
# Optional: custom prefix for secret variables (default: SECRET)
{APP_PREFIX}_SECRET_PREFIX=SECRET
```

**Usage:**
```bash
# Database configuration
COMMONDB_SECRET_DB__REPOSITORY_TYPE=DICT

# Nested configuration
COMMONDB_SECRET_ROOT__USER__ID=12345
COMMONDB_SECRET_ROOT__USER__EMAIL=user@example.com

# Repository configuration
COMMONDB_SECRET_REPOSITORY__SA_SQL__DEFAULTS__PWD=secretpassword
```

### 2. Filesystem Strategy

Set `{APP_PREFIX}_SECRETS_STRATEGY=file`

**Configuration:**
```bash
# Path to secrets directory (required)
{APP_PREFIX}_SECRETS_PATH=/path/to/secrets
```

**Directory Structure:**
```
secrets/
├── db/
│   └── repository_type          # Contains: "DICT"
├── root/
│   └── user/
│       ├── id                   # Contains: "12345"
│       └── email               # Contains: "user@example.com"
└── repository/
    └── sa_sql/
        └── defaults/
            └── pwd             # Contains: "secretpassword"
```

### 3. Azure Key Vault Strategy

Set `{APP_PREFIX}_SECRETS_STRATEGY=azure_key_vault`

**Configuration:**
```bash
# Azure Key Vault URL (required)
{APP_PREFIX}_AZURE_KEYVAULT_URL=https://your-vault.vault.azure.net/

# Authentication option 1: Service Principal
{APP_PREFIX}_AZURE_CLIENT_ID=your-client-id
{APP_PREFIX}_AZURE_CLIENT_SECRET=your-client-secret
{APP_PREFIX}_AZURE_TENANT_ID=your-tenant-id

# Authentication option 2: Use managed identity (no additional config needed)
```

**Secret Names in Key Vault:**
```
secret-db-repository-type
secret-root-user-id
secret-root-user-email
secret-repository-sa-sql-defaults-pwd
```

## Usage Examples

### For COMMONDB

```bash
# Required configuration
export COMMONDB_SECRETS_STRATEGY=file
export COMMONDB_SECRETS_PATH=/app/secrets
export COMMONDB_LOGGING_CONFIG_FILE=/app/config/logging.yaml

# Optional: custom settings
export COMMONDB_SETTINGS_FILE=/app/config/custom-settings.toml

# Optional: override specific settings
export COMMONDB_APP__HOST=0.0.0.0
export COMMONDB_APP__PORT=8080
```

### For CASEDB

```bash
# Required configuration
export CASEDB_SECRETS_STRATEGY=azure_key_vault
export CASEDB_AZURE_KEYVAULT_URL=https://casedb-vault.vault.azure.net/
export CASEDB_LOGGING_CONFIG_FILE=/app/config/logging.yaml

# Azure authentication
export CASEDB_AZURE_CLIENT_ID=your-client-id
export CASEDB_AZURE_CLIENT_SECRET=your-client-secret
export CASEDB_AZURE_TENANT_ID=your-tenant-id
```

## Migration Guide

### From Old System

1. **Update imports**: Replace `cfg.py` import with `cfg_new.py`
2. **Set environment variables**: Configure the required environment variables
3. **Migrate secrets**: Move secrets from `secrets.default.toml` and `.secret/` files to your chosen strategy
4. **Test**: The new system provides backward compatibility through the `cfg` property

### Code Changes Required

**Before:**
```python
from gen_epix.commondb.config.cfg import AppCfg
```

**After:**
```python
from gen_epix.commondb.config.cfg_new import AppCfg
```

**Accessing Configuration (no changes required):**
```python
# These continue to work as before
app_cfg = AppCfg(...)
host = app_cfg.cfg.app.host
secret_value = app_cfg.cfg.secret.db.repository_type
```

## Dependencies

### Required Packages
- `pydantic`: For configuration validation
- `dynaconf`: For settings management with environment variable support
- `pyyaml`: For YAML configuration files

### Optional Packages
- `azure-keyvault-secrets`: For Azure Key Vault strategy
- `azure-identity`: For Azure authentication

Install optional Azure dependencies:
```bash
pip install azure-keyvault-secrets azure-identity
```

## Security Considerations

1. **Environment Variables**: Be careful with environment variables in containerized environments
2. **File Permissions**: Ensure secret files have appropriate permissions (600 or 400)
3. **Azure Key Vault**: Use managed identity when possible, avoid storing client secrets in code
4. **Logging**: The system logs configuration loading but never logs secret values

## Troubleshooting

### Common Issues

1. **Missing SECRETS_STRATEGY**: Set `{APP_PREFIX}_SECRETS_STRATEGY` environment variable
2. **File Not Found**: Check paths in environment variables are correct
3. **Azure Authentication**: Verify Azure credentials and Key Vault permissions
4. **Secret Format**: Ensure secrets are properly formatted (JSON where applicable)

### Debug Mode

Set `{APP_PREFIX}_LOG__LEVEL=DEBUG` to enable detailed logging of configuration loading process.

## Examples

See the `examples/` directory for:
- `settings-custom.toml`: Custom settings file example
- `settings-override.env`: Environment variable overrides
- `secrets/environment-vars.env`: Environment variable secrets
- `secrets/files/`: Filesystem-based secrets structure
- `secrets/azure-keyvault.example.json`: Azure Key Vault configuration