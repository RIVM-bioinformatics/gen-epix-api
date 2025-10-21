# OAuth 2.0 Provider with OpenID Connect Support

This module implements a comprehensive OAuth 2.0 Authorization Server with OpenID Connect (OIDC) support using `oauthlib` and `FastAPI`. It supports the Client Credentials flow and provides all the standard OAuth 2.0 and OIDC endpoints.

## Features

- ✅ **OAuth 2.0 Client Credentials Flow**
- ✅ **OpenID Connect (OIDC) Support**
- ✅ **JWT Access Tokens with RS256 signing**
- ✅ **Token Introspection (RFC 7662)**
- ✅ **JSON Web Key Set (JWKS) endpoint**
- ✅ **OpenID Connect Discovery**
- ✅ **UserInfo endpoint**
- ✅ **Proper client authentication**
- ✅ **Scope validation**
- ✅ **ID Token generation**

## Architecture

The OAuth server consists of several modules:

- `server.py` - Main FastAPI application with OAuth endpoints
- `client_store.py` - Client registration and management
- `token_store.py` - Access token storage and management
- `jwks.py` - JWT token generation and JWKS management
- `validators.py` - OAuth 2.0 request validation (oauthlib integration)
- `oidc_provider.py` - OpenID Connect specific functionality
- `demo_client.py` - Example client demonstrating usage

## Installation

The following packages are required:

```bash
pip install fastapi oauthlib PyJWT cryptography uvicorn
```

## Quick Start

1. **Start the OAuth Server:**

```bash
# From the oauth directory
python start_server.py

# Or with custom options
python start_server.py --host 0.0.0.0 --port 9000 --debug
```

The server will start on `http://localhost:8080` by default.

2. **Test with Demo Client:**

```bash
# In another terminal
python demo_client.py
```

3. **Run Comprehensive Tests:**

```bash
# Test all functionality
python test_server.py

# Test with verbose output
python test_server.py --verbose
```

## Available Scripts

- `start_server.py` - Production-ready server startup script with CLI options
- `demo_client.py` - Interactive demo showing OAuth flows
- `test_server.py` - Comprehensive test suite for all endpoints
- `server.py` - Core FastAPI application (can also be run directly)

## Endpoints

### OpenID Connect Discovery
- `GET /.well-known/openid-configuration` - Discovery document

### JSON Web Key Set
- `GET /.well-known/jwks.json` - Public keys for token verification

### OAuth 2.0 Endpoints
- `POST /oauth/token` - Token endpoint (Client Credentials flow)
- `POST /oauth/introspect` - Token introspection (RFC 7662)
- `GET /oauth/userinfo` - UserInfo endpoint (OIDC)

### Health Check
- `GET /health` - Server health status

## Client Credentials Flow

### 1. Token Request

```bash
curl -X POST http://localhost:8080/oauth/token \
  -u "demo-client:demo-secret" \
  -d "grant_type=client_credentials&scope=read write"
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read write"
}
```

### 2. Token with OpenID Scope

```bash
curl -X POST http://localhost:8080/oauth/token \
  -u "demo-client:demo-secret" \
  -d "grant_type=client_credentials&scope=openid profile"
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer", 
  "expires_in": 3600,
  "scope": "openid profile",
  "id_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIs..."
}
```

### 3. Token Introspection

```bash
curl -X POST http://localhost:8080/oauth/introspect \
  -u "demo-client:demo-secret" \
  -d "token=YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "active": true,
  "client_id": "demo-client", 
  "scope": "read write",
  "token_type": "Bearer",
  "exp": 1640995200,
  "iat": 1640991600,
  "sub": "demo-client",
  "aud": "demo-client",
  "iss": "http://localhost:8080"
}
```

### 4. UserInfo Endpoint

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8080/oauth/userinfo
```

**Response:**
```json
{
  "sub": "demo-client",
  "client_id": "demo-client", 
  "aud": "demo-client",
  "iss": "http://localhost:8080"
}
```

## Pre-configured Clients

The server comes with two demo clients:

### Demo Client
- **Client ID:** `demo-client`
- **Client Secret:** `demo-secret`
- **Scopes:** `read`, `write`, `openid`, `profile`
- **Grant Types:** `client_credentials`

### Test Client  
- **Client ID:** `test-client`
- **Client Secret:** `test-secret`
- **Scopes:** `read`, `openid`
- **Grant Types:** `client_credentials`

## JWT Token Structure

Access tokens are JWT tokens with the following structure:

**Header:**
```json
{
  "typ": "JWT",
  "alg": "RS256", 
  "kid": "key-id-here"
}
```

**Payload:**
```json
{
  "iss": "http://localhost:8080",
  "sub": "demo-client",
  "aud": "demo-client", 
  "iat": 1640991600,
  "exp": 1640995200,
  "scope": "read write",
  "client_id": "demo-client",
  "token_type": "Bearer"
}
```

## OpenID Connect Features

### Discovery Document

The server provides a complete OIDC discovery document at `/.well-known/openid-configuration`:

```json
{
  "issuer": "http://localhost:8080",
  "authorization_endpoint": "http://localhost:8080/oauth/authorize",
  "token_endpoint": "http://localhost:8080/oauth/token",
  "userinfo_endpoint": "http://localhost:8080/oauth/userinfo", 
  "jwks_uri": "http://localhost:8080/.well-known/jwks.json",
  "response_types_supported": ["code", "token"],
  "grant_types_supported": ["client_credentials", "authorization_code"],
  "subject_types_supported": ["public"],
  "id_token_signing_alg_values_supported": ["RS256"],
  "scopes_supported": ["openid", "profile", "email", "read", "write"]
}
```

### ID Tokens

When the `openid` scope is requested, the server returns an ID token alongside the access token. ID tokens follow the OIDC specification and include standard claims.

## Security Features

- **RSA-256 JWT Signing** - All tokens are signed with RSA-256
- **Client Secret Hashing** - Client secrets are hashed with SHA-256 + salt
- **Scope Validation** - Only registered scopes are allowed
- **Token Expiration** - Configurable token expiration (default: 1 hour)
- **Secure Headers** - Proper cache control headers on token responses

## Extending the Server

### Adding New Clients

```python
from client_store import Client, ClientStore

client_store = ClientStore()

new_client = Client(
    client_id="my-app",
    client_secret="my-secret", 
    client_name="My Application",
    scopes=["read", "write", "custom"],
    grant_types=["client_credentials"]
)

client_store.store_client(new_client)
```

### Custom Scopes

Modify the discovery document and client configurations to add custom scopes:

```python
# In server.py - discovery endpoint
"scopes_supported": [
    "openid", "profile", "email", 
    "read", "write",
    "admin", "custom:action"  # Custom scopes
]
```

### Database Integration

The current implementation uses in-memory storage. For production use, implement database backends:

```python
# Example: Database-backed client store
class DatabaseClientStore(ClientStore):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_client(self, client_id: str) -> Optional[Client]:
        # Query database for client
        pass
    
    def store_client(self, client: Client) -> None:
        # Save client to database  
        pass
```

## Production Considerations

1. **Key Management** - Use proper key rotation and secure key storage
2. **Database Backend** - Replace in-memory stores with persistent storage
3. **Rate Limiting** - Add rate limiting to prevent abuse
4. **Logging** - Implement comprehensive audit logging
5. **HTTPS** - Always use HTTPS in production
6. **Client Registration** - Implement dynamic client registration if needed
7. **Monitoring** - Add health checks and metrics

## Testing

The `demo_client.py` script provides a comprehensive test of all OAuth flows and endpoints. Run it to verify the server is working correctly:

```bash
python demo_client.py
```

Expected output:
```
=== OAuth 2.0 Client Credentials Flow Demo ===

1. Getting OpenID Connect Discovery Document...
   Issuer: http://localhost:8080
   Token Endpoint: http://localhost:8080/oauth/token
   ...

✅ Demo completed successfully!
```

## References

- [RFC 6749 - OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [RFC 7662 - OAuth 2.0 Token Introspection](https://tools.ietf.org/html/rfc7662)
- [OpenID Connect Core 1.0](https://openid.net/specs/openid-connect-core-1_0.html)
- [JSON Web Key (JWK) RFC 7517](https://tools.ietf.org/html/rfc7517)
- [JSON Web Token (JWT) RFC 7519](https://tools.ietf.org/html/rfc7519)