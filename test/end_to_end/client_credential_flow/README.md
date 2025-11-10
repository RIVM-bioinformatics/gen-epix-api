# OAuth OIDC Client Credential Authentication Flow Test

## Summary

This test module implements a comprehensive OAuth 2.0 Client Credentials flow test as described in [RFC 6749 Section 4.4](https://datatracker.ietf.org/doc/html/rfc6749#section-4.4).

## Refactored Architecture

The test has been refactored into a modular package structure with each class in its own module:

### Package Structure

```
test/end_to_end/client_credential_flow/
├── __init__.py
├── test_client_credential_flow.py       # Main test file with fixtures and tests
├── README.md                           # This documentation
└── apps/                              # Application modules package
    ├── __init__.py                    # Package exports
    ├── oauth_server_manager.py       # OAuth server process management
    ├── receiver_app.py               # ReceiverApp FastAPI application
    ├── receiver_app_manager.py       # ReceiverApp process management
    ├── receiver_app_cli.py           # ReceiverApp CLI using Fire
    └── requestor_app.py              # RequestorApp client application
```

### Module Responsibilities

#### 1. `oauth_server_manager.py`
- **Class**: `OAuthServerManager`
- **Purpose**: Manages the OAuth server process
- **Features**: Server startup/shutdown, health checking, log monitoring

#### 2. `receiver_app.py`  
- **Class**: `ReceiverApp`
- **Purpose**: FastAPI application for token validation
- **Features**: Protected endpoints, OIDC client integration, token validation

#### 3. `receiver_app_manager.py`
- **Class**: `ReceiverAppManager` 
- **Purpose**: Manages ReceiverApp server process
- **Features**: Process management, health checking, log monitoring

#### 4. `receiver_app_cli.py`
- **Class**: `ReceiverAppCLI`
- **Purpose**: Command-line interface using Fire package
- **Features**: Argument parsing, server startup with configurable parameters

#### 5. `requestor_app.py`
- **Class**: `RequestorApp`
- **Purpose**: OAuth client for requesting tokens and calling APIs
- **Features**: Token acquisition, API calls, invalid token generation for testing

## Command Line Interface

The ReceiverApp can now be started directly via CLI using the Fire package:

```bash
# Start ReceiverApp on default port (8001)
python -m test.end_to_end.client_credential_flow.apps.receiver_app_cli run --oauth_discovery_url="http://localhost:8000/.well-known/openid-configuration"

# Start on custom port
python -m test.end_to_end.client_credential_flow.apps.receiver_app_cli run --port=9001 --oauth_discovery_url="http://localhost:8000/.well-known/openid-configuration"

# Show help
python -m test.end_to_end.client_credential_flow.apps.receiver_app_cli run --help
```

## Architecture Benefits

### 1. Separation of Concerns
- Each class has a single responsibility
- Application logic separated from process management
- CLI separated from application code

### 2. Improved Maintainability
- Easier to test individual components
- Clear module boundaries
- Reduced code duplication

### 3. Enhanced Reusability
- Components can be used independently
- CLI provides standalone server capability
- Modules can be imported separately

### 4. Better Testability
- Each module can be unit tested
- Mocking is easier with separated concerns
- Integration tests remain comprehensive

## Test Scenarios

### 1. Successful Flow (`test_oauth_client_credentials_flow_success`)
1. RequestorApp requests access token from OAuth Server
2. OAuth Server validates client credentials and issues JWT token with audience "ReceiverApp"
3. RequestorApp calls ReceiverApp's protected endpoint with the token
4. ReceiverApp validates the token (signature, issuer, audience, expiry)
5. ReceiverApp returns success response

### 2. Invalid Token (`test_oauth_client_credentials_flow_invalid_token`)
1. RequestorApp creates a malformed JWT token
2. RequestorApp calls ReceiverApp's protected endpoint with invalid token
3. ReceiverApp rejects the token and returns 401 Unauthorized

### 3. Missing Token (`test_oauth_client_credentials_flow_missing_token`)
1. Client calls ReceiverApp's protected endpoint without any token
2. ReceiverApp returns 403 Forbidden

### 4. Discovery Tests
- Validates OAuth server's OpenID Connect discovery endpoint
- Validates JWKS endpoint functionality

## Key Technical Enhancements

### Fire CLI Integration
- Uses Fire package for argument parsing
- Supports both positional and keyword arguments
- Automatic help generation
- Type checking and validation

### Process Management Improvements
- Eliminated temporary file generation
- Proper CLI command execution
- Better error handling and logging
- Clean process shutdown

### Code Organization
- Clear import structure
- Proper package initialization
- Type hints throughout
- Consistent error handling

## OAuth 2.0 Compliance

The implementation follows OAuth 2.0 and OpenID Connect specifications:

- **RFC 6749**: OAuth 2.0 Authorization Framework
- **RFC 7662**: OAuth 2.0 Token Introspection
- **OpenID Connect Discovery 1.0**: Configuration discovery
- **RFC 7517**: JSON Web Key (JWK) format
- **RFC 7519**: JSON Web Token (JWT)

## Usage

```bash
# Run all tests
python -m pytest test/end_to_end/client_credential_flow/test_client_credential_flow.py -v

# Run specific test
python -m pytest test/end_to_end/client_credential_flow/test_client_credential_flow.py::test_oauth_client_credentials_flow_success -v -s

# Start ReceiverApp manually
python -m test.end_to_end.client_credential_flow.apps.receiver_app_cli run --oauth_discovery_url="http://localhost:8000/.well-known/openid-configuration"
```

## Dependencies

- **Fire**: Command-line interface generation
- **FastAPI**: Web framework for ReceiverApp
- **httpx**: HTTP client for API calls
- **pytest**: Testing framework
- **uvicorn**: ASGI server for FastAPI applications

## Test Environment

- Python 3.13.7
- FastAPI with OIDC support
- JWT token handling with RS256 signatures
- Process-based isolation for realistic testing
- Proper cleanup of server processes
- Fire-based CLI for enhanced usability