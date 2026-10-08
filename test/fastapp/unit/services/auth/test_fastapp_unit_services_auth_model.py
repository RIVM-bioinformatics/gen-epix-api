import pytest

from gen_epix.fastapp.services.auth.model import OidcServerCfg


class TestOidcServerCfg:
    def test_claim_map_validator_rejects_bad_types(self) -> None:
        with pytest.raises(ValueError):
            OidcServerCfg(
                claim_map="notadict",
                name="x",
                label="x",
                client_id="x",
                scope="openid",
            )
        with pytest.raises(ValueError):
            OidcServerCfg(
                claim_map={"__key__": 123},
                name="x",
                label="x",
                client_id="x",
                scope="openid",
            )
        with pytest.raises(ValueError):
            OidcServerCfg(
                claim_map={"__key__": ["email", 123]},
                name="x",
                label="x",
                client_id="x",
                scope="openid",
            )
