"""
OAuth 2.0 Client Test Script

This script demonstrates how to use the OAuth 2.0 provider with the Client Credentials flow.
It shows how to obtain access tokens and call protected endpoints.
"""

import base64
import json
from typing import Any

import requests  # type: ignore[import-untyped]


class OAuth2Client:
    """Simple OAuth 2.0 client for testing."""

    def __init__(self, base_url: str, client_id: str, client_secret: str):
        """Initialize OAuth client."""
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: str | None = None

    def get_discovery_document(self) -> dict[str, Any]:
        """Get OpenID Connect discovery document."""
        url = f"{self.base_url}/.well-known/openid-configuration"
        response = requests.get(url)
        response.raise_for_status()
        return dict(response.json())

    def get_jwks(self) -> dict[str, Any]:
        """Get JSON Web Key Set."""
        url = f"{self.base_url}/.well-known/jwks.json"
        response = requests.get(url)
        response.raise_for_status()
        return dict(response.json())

    def get_client_credentials_token(self, scope: str = "") -> dict[str, Any]:
        """Get access token using Client Credentials flow."""
        url = f"{self.base_url}/oauth/token"

        # Prepare credentials
        auth = (self.client_id, self.client_secret)

        # Prepare form data
        data = {"grant_type": "client_credentials"}
        if scope:
            data["scope"] = scope

        # Make request
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get("access_token")

        return dict(token_data)

    def introspect_token(self, token: str | None = None) -> dict[str, Any]:
        """Introspect a token."""
        if not token:
            token = self.access_token

        if not token:
            raise ValueError("No token provided or stored")

        url = f"{self.base_url}/oauth/introspect"
        auth = (self.client_id, self.client_secret)
        data = {"token": token}

        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()

        return dict(response.json())

    def get_userinfo(self, token: str | None = None) -> dict[str, Any]:
        """Get user info using access token."""
        if not token:
            token = self.access_token

        if not token:
            raise ValueError("No token provided or stored")

        url = f"{self.base_url}/oauth/userinfo"
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return dict(response.json())

    def decode_jwt_payload(self, token: str | None = None) -> dict[str, Any]:
        """Decode JWT payload without verification (for demo purposes)."""
        if not token:
            token = self.access_token

        if not token:
            raise ValueError("No token provided or stored")

        # Split JWT into parts
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        # Decode payload (add padding if needed)
        payload_part = parts[1]
        padding = len(payload_part) % 4
        if padding:
            payload_part += "=" * (4 - padding)

        payload_bytes = base64.urlsafe_b64decode(payload_part)
        return dict(json.loads(payload_bytes.decode("utf-8")))

    def create_client(
        self,
        client_id: str,
        client_secret: str,
        client_name: str,
        scopes: list[str],
        grant_types: list[str] | None = None,
        redirect_uris: list[str] | None = None,
        audience: str | None = None,
    ) -> dict[str, Any]:
        """Create a new OAuth client."""
        url = f"{self.base_url}/admin/clients"

        if grant_types is None:
            grant_types = ["client_credentials"]
        if redirect_uris is None:
            redirect_uris = []

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": client_name,
            "scopes": scopes,
            "grant_types": grant_types,
            "redirect_uris": redirect_uris,
            "audience": audience,
        }

        response = requests.post(url, json=data)
        response.raise_for_status()
        return dict(response.json())

    def delete_client(self, client_id: str) -> None:
        """Delete an OAuth client."""
        url = f"{self.base_url}/admin/clients/{client_id}"
        response = requests.delete(url)
        response.raise_for_status()

    def list_clients(self) -> list[dict[str, Any]]:
        """List all OAuth clients."""
        url = f"{self.base_url}/admin/clients"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_client(self, client_id: str) -> dict[str, Any]:
        """Get a specific OAuth client."""
        url = f"{self.base_url}/admin/clients/{client_id}"
        response = requests.get(url)
        response.raise_for_status()
        return dict(response.json())


def demo_client_credentials_flow() -> None:
    """Demonstrate the Client Credentials flow."""
    print("=== OAuth 2.0 Client Credentials Flow Demo ===\n")

    # Initialize admin client for management operations
    admin_client = OAuth2Client(
        base_url="http://127.0.0.1:8080",
        client_id="admin",
        client_secret="admin",
    )

    try:
        # 0. Create demo client dynamically
        print("0. Creating demo client...")
        try:
            demo_client_info = admin_client.create_client(
                client_id="demo-client",
                client_secret="demo-secret",
                client_name="Demo Client",
                scopes=["read", "write", "openid", "profile"],
                grant_types=["client_credentials"],
            )
            print(f"   Created client: {demo_client_info['client_name']}")
            print(f"   Client ID: {demo_client_info['client_id']}")
            print(f"   Scopes: {demo_client_info['scopes']}")
            print()
        except requests.RequestException as e:
            if "409" in str(e):  # Client already exists
                print("   Demo client already exists, continuing...")
                print()
            else:
                raise

        # Initialize client for OAuth operations
        client = OAuth2Client(
            base_url="http://127.0.0.1:8080",
            client_id="demo-client",
            client_secret="demo-secret",
        )

        # 1. Get discovery document
        print("1. Getting OpenID Connect Discovery Document...")
        discovery = client.get_discovery_document()
        print(f"   Issuer: {discovery.get('issuer')}")
        print(f"   Token Endpoint: {discovery.get('token_endpoint')}")
        print(f"   JWKS URI: {discovery.get('jwks_uri')}")
        print(f"   Supported Scopes: {discovery.get('scopes_supported')}")
        print()

        # 2. Get JWKS
        print("2. Getting JSON Web Key Set...")
        jwks = client.get_jwks()
        print(f"   Number of keys: {len(jwks.get('keys', []))}")
        if jwks.get("keys"):
            key = jwks["keys"][0]
            print(f"   Key ID: {key.get('kid')}")
            print(f"   Algorithm: {key.get('alg')}")
        print()

        # 3. Get access token with basic scopes
        print("3. Getting access token with 'read write' scopes...")
        token_response = client.get_client_credentials_token("read write")
        print(f"   Access Token: {token_response.get('access_token', '')[:50]}...")
        print(f"   Token Type: {token_response.get('token_type')}")
        print(f"   Expires In: {token_response.get('expires_in')} seconds")
        print(f"   Scope: {token_response.get('scope')}")
        print()

        # 4. Decode token payload
        print("4. Decoding JWT payload...")
        payload = client.decode_jwt_payload()
        print(f"   Subject: {payload.get('sub')}")
        print(f"   Issuer: {payload.get('iss')}")
        print(f"   Audience: {payload.get('aud')}")
        print(f"   Expires: {payload.get('exp')}")
        print(f"   Scope: {payload.get('scope')}")
        print()

        # 5. Introspect token
        print("5. Introspecting token...")
        introspection = client.introspect_token()
        print(f"   Active: {introspection.get('active')}")
        print(f"   Client ID: {introspection.get('client_id')}")
        print(f"   Scope: {introspection.get('scope')}")
        print()

        # 6. Get access token with OpenID scope
        print("6. Getting access token with 'openid profile' scopes...")
        oidc_token_response = client.get_client_credentials_token("openid profile")
        print(f"   Access Token: {oidc_token_response.get('access_token', '')[:50]}...")
        print(f"   ID Token Present: {'id_token' in oidc_token_response}")
        if "id_token" in oidc_token_response:
            print(f"   ID Token: {oidc_token_response.get('id_token', '')[:50]}...")
        print()

        # 7. Call userinfo endpoint
        print("7. Calling UserInfo endpoint...")
        userinfo = client.get_userinfo(oidc_token_response.get("access_token"))
        print(f"   Subject: {userinfo.get('sub')}")
        print(f"   Client ID: {userinfo.get('client_id')}")
        print()

        # 8. Demonstrate client management
        print("8. Demonstrating client management...")

        # List all clients
        print("   Listing all clients...")
        clients = admin_client.list_clients()
        print(f"   Found {len(clients)} clients:")
        for client_info in clients:
            print(f"     - {client_info['client_id']}: {client_info['client_name']}")
        print()

        # Create and delete a temporary client
        print("   Creating temporary client...")
        temp_client = admin_client.create_client(
            client_id="temp-client",
            client_secret="temp-secret",
            client_name="Temporary Client",
            scopes=["read"],
            grant_types=["client_credentials"],
        )
        print(f"   Created: {temp_client['client_name']}")

        print("   Deleting temporary client...")
        admin_client.delete_client("temp-client")
        print("   Deleted temporary client")
        print()

        print("✅ Demo completed successfully!")

    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        print("Make sure the OAuth server is running on http://127.0.0.1:8080")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    demo_client_credentials_flow()
