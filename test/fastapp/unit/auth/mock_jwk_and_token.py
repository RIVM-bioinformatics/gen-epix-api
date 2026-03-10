import base64
from datetime import datetime, timedelta, timezone
from math import floor

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class MockJWKAndToken:
    def __init__(
        self, token_expiration_minutes: int, token_iat_minutes_ago: int = 0
    ) -> None:
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()

        # Serialize the private key for signing the JWT
        self.private_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Serialize the public key for the JWK
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        # Create the JWK dict from the public key (extract n and e)
        pub_numbers = self.public_key.public_numbers()

        def _int_to_base64url(n: int) -> str:
            b = n.to_bytes((n.bit_length() + 7) // 8, "big")
            return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

        n_b64 = _int_to_base64url(pub_numbers.n)
        e_b64 = _int_to_base64url(pub_numbers.e)

        self.public_jwk_dict = {
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": "EgDRMr2n3vd3s09HMiwU",
            "n": n_b64,
            "e": e_b64,
            "x5t": "EgDRMr2n3vd3s09HMiwU",
            "issuer": "https://idp1.org/issuer",
        }

        # Create a payload for the JWT
        now = datetime.now(timezone.utc)
        self.payload = {
            "aud": "POv1bEMlzAunu6LD0BcmV4pvxInkNRXY",  # client id
            "iss": "https://idp1.org/issuer",  # authorization server
            "iat": floor(
                (now - timedelta(minutes=token_iat_minutes_ago)).timestamp()
            ),  # issued at
            "nbf": floor(now.timestamp()),
            "exp": floor(
                (now + timedelta(minutes=token_expiration_minutes)).timestamp()
            ),
            "sub": "5KaDjVTAxeeFDikvll8WAPLbp0A8rAFjNFk6RsL1iuk",  # subject, usually the user id
            "app_displayname": "spn-rivm-az-LabSentiNL-poc",
            "family_name": "mock_family_name",
            "given_name": "mock_given_name",
            "name": "mock_given_name mock_family_name",
            "oid": "46212d53-d5bb-4f2c-b076-8223c394be85",  # user id in the directory
            "scp": "User.Read profile openid email",  # scope
            "tid": "cd8466c6-d7ce-410a-be13-33e40185fdab",  # tenant id
            "roles": ["admin"],  # roles
            "amr": ["pwd"],  # authentication method reference
            "email": "user1@org1.org",
            "ver": "1.0",
        }

        self.public_jwk_dict_backup = self.public_jwk_dict.copy()
        self.payload_backup = self.payload.copy()

        # Sign the JWT with the private key
        self.token = self._get_token()

    def _get_token(self) -> str:
        return jwt.encode(
            self.payload,
            self.private_key_pem,
            algorithm=self.public_jwk_dict["alg"],
            headers={"kid": self.public_jwk_dict["kid"]},
        )

    def edit_claim(
        self, key: str, value: str | None = None, remove: bool = False
    ) -> str:
        if remove:
            self.payload.pop(key)
        else:
            assert value, "Value must be provided to edit the claim"
            self.payload[key] = value
        token = self._get_token()
        self.payload = self.payload_backup.copy()
        return token

    def edit_jwk(self, key: str, value: str | None = None, remove: bool = False) -> str:
        if remove:
            self.public_jwk_dict.pop(key)
        else:
            assert value, "Value must be provided to edit the jwk"
            self.public_jwk_dict[key] = value

        token = self._get_token()
        self.public_jwk_dict = self.public_jwk_dict_backup.copy()
        return token
