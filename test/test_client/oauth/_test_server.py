#!/usr/bin/env python3
"""
OAuth 2.0 Server Test Suite

This script provides comprehensive testing of the OAuth 2.0 server functionality,
including all endpoints, error conditions, and edge cases.

Usage:
    python test_server.py [--server-url URL] [--verbose]

Examples:
    python test_server.py                                    # Test localhost:8080
    python test_server.py --server-url http://localhost:9000 # Test custom URL
    python test_server.py --verbose                          # Detailed output
"""

import argparse
import sys
from datetime import datetime

import requests


class OAuth2ServerTester:
    """Comprehensive test suite for OAuth 2.0 server."""

    def __init__(self, base_url: str, verbose: bool = False):
        """Initialize the tester."""
        self.base_url = base_url.rstrip("/")
        self.verbose = verbose
        self.test_results: dict[str, bool] = {}
        self.total_tests = 0
        self.passed_tests = 0

        # Test clients
        self.demo_client = ("demo-client", "demo-secret")
        self.test_client = ("test-client", "test-secret")
        self.invalid_client = ("invalid-client", "invalid-secret")

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with optional verbosity control."""
        if self.verbose or level in ["ERROR", "RESULT"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test and record the result."""
        self.total_tests += 1
        self.log(f"Running test: {test_name}")

        try:
            result = test_func()
            self.test_results[test_name] = result
            if result:
                self.passed_tests += 1
                self.log(f"✅ PASSED: {test_name}", "RESULT")
            else:
                self.log(f"❌ FAILED: {test_name}", "ERROR")
            return result
        except Exception as e:
            self.test_results[test_name] = False
            self.log(f"❌ ERROR in {test_name}: {str(e)}", "ERROR")
            return False

    def test_server_health(self) -> bool:
        """Test server health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return "status" in data and data["status"] == "healthy"
            return False
        except requests.RequestException:
            return False

    def test_discovery_document(self) -> bool:
        """Test OpenID Connect discovery document."""
        try:
            response = requests.get(f"{self.base_url}/.well-known/openid-configuration")
            if response.status_code != 200:
                return False

            discovery = response.json()
            required_fields = [
                "issuer",
                "token_endpoint",
                "jwks_uri",
                "userinfo_endpoint",
                "response_types_supported",
                "grant_types_supported",
                "scopes_supported",
                "subject_types_supported",
            ]

            for field in required_fields:
                if field not in discovery:
                    self.log(f"Missing field in discovery: {field}")
                    return False

            # Validate specific values
            if discovery["issuer"] != self.base_url:
                self.log(f"Invalid issuer: {discovery['issuer']}")
                return False

            if "client_credentials" not in discovery["grant_types_supported"]:
                self.log("Client credentials not in supported grant types")
                return False

            return True
        except Exception as e:
            self.log(f"Discovery test error: {e}")
            return False

    def test_jwks_endpoint(self) -> bool:
        """Test JWKS endpoint."""
        try:
            response = requests.get(f"{self.base_url}/.well-known/jwks.json")
            if response.status_code != 200:
                return False

            jwks = response.json()
            if "keys" not in jwks or not jwks["keys"]:
                return False

            key = jwks["keys"][0]
            required_fields = ["kty", "use", "kid", "alg", "n", "e"]

            for field in required_fields:
                if field not in key:
                    self.log(f"Missing field in JWK: {field}")
                    return False

            # Validate key type and algorithm
            if key["kty"] != "RSA" or key["alg"] != "RS256":
                return False

            return True
        except Exception as e:
            self.log(f"JWKS test error: {e}")
            return False

    def test_client_credentials_valid(self) -> bool:
        """Test valid client credentials flow."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                auth=self.demo_client,
                data={"grant_type": "client_credentials", "scope": "read write"},
            )

            if response.status_code != 200:
                self.log(f"Unexpected status: {response.status_code}")
                return False

            token_data = response.json()
            required_fields = ["access_token", "token_type", "expires_in", "scope"]

            for field in required_fields:
                if field not in token_data:
                    self.log(f"Missing field in token response: {field}")
                    return False

            if token_data["token_type"] != "Bearer":
                return False

            # Validate JWT format
            access_token = token_data["access_token"]
            if len(access_token.split(".")) != 3:
                self.log("Invalid JWT format")
                return False

            return True
        except Exception as e:
            self.log(f"Client credentials test error: {e}")
            return False

    def test_client_credentials_with_openid(self) -> bool:
        """Test client credentials with OpenID scope."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                auth=self.demo_client,
                data={"grant_type": "client_credentials", "scope": "openid profile"},
            )

            if response.status_code != 200:
                return False

            token_data = response.json()

            # Should include ID token when openid scope is requested
            if "id_token" not in token_data:
                self.log("Missing ID token with openid scope")
                return False

            # Validate ID token format
            id_token = token_data["id_token"]
            if len(id_token.split(".")) != 3:
                self.log("Invalid ID token JWT format")
                return False

            return True
        except Exception as e:
            self.log(f"OpenID test error: {e}")
            return False

    def test_invalid_client_credentials(self) -> bool:
        """Test invalid client credentials."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                auth=self.invalid_client,
                data={"grant_type": "client_credentials", "scope": "read"},
            )

            # Should return 401 Unauthorized
            return response.status_code == 401
        except Exception as e:
            self.log(f"Invalid credentials test error: {e}")
            return False

    def test_invalid_grant_type(self) -> bool:
        """Test invalid grant type."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                auth=self.demo_client,
                data={"grant_type": "invalid_grant", "scope": "read"},
            )

            # Should return 400 Bad Request
            return response.status_code == 400
        except Exception as e:
            self.log(f"Invalid grant type test error: {e}")
            return False

    def test_invalid_scope(self) -> bool:
        """Test requesting invalid scope."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                auth=self.test_client,  # Only has 'read' and 'openid' scopes
                data={
                    "grant_type": "client_credentials",
                    "scope": "write admin",  # Should be filtered/rejected
                },
            )

            if response.status_code != 200:
                return False

            token_data = response.json()
            # Scope should be empty or only contain valid scopes
            granted_scope = token_data.get("scope", "")
            invalid_scopes = ["write", "admin"]

            for invalid_scope in invalid_scopes:
                if invalid_scope in granted_scope:
                    self.log(f"Invalid scope granted: {invalid_scope}")
                    return False

            return True
        except Exception as e:
            self.log(f"Invalid scope test error: {e}")
            return False

    def get_valid_token(self) -> str | None:
        """Get a valid access token for testing."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/token",
                auth=self.demo_client,
                data={
                    "grant_type": "client_credentials",
                    "scope": "openid profile read",
                },
            )

            if response.status_code == 200:
                return response.json().get("access_token")
            return None
        except:
            return None

    def test_token_introspection_valid(self) -> bool:
        """Test token introspection with valid token."""
        try:
            # Get a valid token first
            token = self.get_valid_token()
            if not token:
                self.log("Could not get valid token for introspection test")
                return False

            response = requests.post(
                f"{self.base_url}/oauth/introspect",
                auth=self.demo_client,
                data={"token": token},
            )

            if response.status_code != 200:
                return False

            introspection = response.json()

            if not introspection.get("active"):
                self.log("Token should be active")
                return False

            required_fields = ["client_id", "scope", "token_type", "exp", "iat"]
            for field in required_fields:
                if field not in introspection:
                    self.log(f"Missing field in introspection: {field}")
                    return False

            return True
        except Exception as e:
            self.log(f"Token introspection test error: {e}")
            return False

    def test_token_introspection_invalid(self) -> bool:
        """Test token introspection with invalid token."""
        try:
            response = requests.post(
                f"{self.base_url}/oauth/introspect",
                auth=self.demo_client,
                data={"token": "invalid.token.here"},
            )

            if response.status_code != 200:
                return False

            introspection = response.json()

            # Should return active: false for invalid tokens
            return not introspection.get("active", True)
        except Exception as e:
            self.log(f"Invalid token introspection test error: {e}")
            return False

    def test_userinfo_endpoint(self) -> bool:
        """Test UserInfo endpoint with valid token."""
        try:
            # Get a valid token with openid scope
            token = self.get_valid_token()
            if not token:
                return False

            response = requests.get(
                f"{self.base_url}/oauth/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )

            if response.status_code != 200:
                return False

            userinfo = response.json()

            # Should at least contain subject
            if "sub" not in userinfo:
                self.log("Missing 'sub' in userinfo")
                return False

            return True
        except Exception as e:
            self.log(f"UserInfo test error: {e}")
            return False

    def test_userinfo_no_token(self) -> bool:
        """Test UserInfo endpoint without token."""
        try:
            response = requests.get(f"{self.base_url}/oauth/userinfo")

            # Should return 401 Unauthorized
            return response.status_code == 401
        except Exception as e:
            self.log(f"UserInfo no token test error: {e}")
            return False

    def test_userinfo_invalid_token(self) -> bool:
        """Test UserInfo endpoint with invalid token."""
        try:
            response = requests.get(
                f"{self.base_url}/oauth/userinfo",
                headers={"Authorization": "Bearer invalid.token.here"},
            )

            # Should return 401 Unauthorized
            return response.status_code == 401
        except Exception as e:
            self.log(f"UserInfo invalid token test error: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all tests."""
        print("🧪 Starting OAuth 2.0 Server Test Suite")
        print(f"🎯 Target server: {self.base_url}")
        print("=" * 60)

        # Basic connectivity and discovery tests
        self.run_test("Server Health Check", self.test_server_health)
        self.run_test("OpenID Connect Discovery", self.test_discovery_document)
        self.run_test("JWKS Endpoint", self.test_jwks_endpoint)

        # Token endpoint tests
        self.run_test(
            "Client Credentials Flow (Valid)", self.test_client_credentials_valid
        )
        self.run_test(
            "Client Credentials with OpenID", self.test_client_credentials_with_openid
        )
        self.run_test(
            "Invalid Client Credentials", self.test_invalid_client_credentials
        )
        self.run_test("Invalid Grant Type", self.test_invalid_grant_type)
        self.run_test("Invalid Scope Filtering", self.test_invalid_scope)

        # Token introspection tests
        self.run_test(
            "Token Introspection (Valid)", self.test_token_introspection_valid
        )
        self.run_test(
            "Token Introspection (Invalid)", self.test_token_introspection_invalid
        )

        # UserInfo endpoint tests
        self.run_test("UserInfo Endpoint", self.test_userinfo_endpoint)
        self.run_test("UserInfo No Token", self.test_userinfo_no_token)
        self.run_test("UserInfo Invalid Token", self.test_userinfo_invalid_token)

        # Print results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS")
        print("=" * 60)

        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")

        print(f"\n📈 Summary: {self.passed_tests}/{self.total_tests} tests passed")

        if self.passed_tests == self.total_tests:
            print("🎉 All tests passed! OAuth server is working correctly.")
            return True
        else:
            print(f"⚠️  {self.total_tests - self.passed_tests} tests failed.")
            return False


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="OAuth 2.0 Server Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    Test localhost:8080
  %(prog)s --server-url http://localhost:9000 Test custom URL
  %(prog)s --verbose                          Detailed output

Make sure the OAuth server is running before running tests:
  python start_server.py
        """,
    )

    parser.add_argument(
        "--server-url",
        default="http://localhost:8080",
        help="OAuth server URL (default: http://localhost:8080)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Create and run tester
    tester = OAuth2ServerTester(args.server_url, args.verbose)

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
