from typing import Any

from gen_epix.fastapp.services.auth.util import get_name_from_claims


class TestGetNameFromClaims:
    def test_extracts_name_prefers_name(self) -> None:
        claims: dict[str, Any] = {
            "name": "Jane Doe",
            "preferred_username": "jane",
        }
        assert get_name_from_claims(claims, ["name"]) == "Jane Doe"

    def test_extracts_name_given_family(self) -> None:
        claims: dict[str, Any] = {"given_name": "Ada", "family_name": "Lovelace"}
        assert (
            get_name_from_claims(claims, [["given_name", "family_name"]])
            == "Ada Lovelace"
        )

    def test_extracts_preferred_username(self) -> None:
        claims: dict[str, Any] = {"preferred_username": "mockuser"}
        assert get_name_from_claims(claims, ["preferred_username"]) == "mockuser"

    def test_does_not_fall_back_to_email(self) -> None:
        claims: dict[str, Any] = {"email": "user1@org1.org"}
        assert get_name_from_claims(claims, ["name"]) is None

    def test_returns_none_when_no_name_claims_are_present(self) -> None:
        assert get_name_from_claims({}, ["name", "preferred_username"]) is None
