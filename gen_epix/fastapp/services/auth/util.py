"""Authentication value normalization and validation helpers."""

from typing import Any

from gen_epix.fastapp.services.auth.literal import EMAIL_PATTERN


def get_email_from_claims(
    claims: dict[str, Any],
) -> str | None:
    """Perform the get email from claims operation."""
    email = claims.get("email")
    if email is None:
        for claim in claims.values():
            if isinstance(claim, str) and EMAIL_PATTERN.match(claim.lower()):
                return claim.lower()
    else:
        return email.lower()
    return None


def get_name_from_claims(
    claims: dict[str, Any], name_claims: list[str | list[str]]
) -> str | None:
    """Get the name from the claims, checking against a list of possible name claims."""
    for name_claim in name_claims:
        if isinstance(name_claim, str):
            if name_claim in claims:
                return str(claims[name_claim])
        else:
            # Check if every subclaim exists and if so return space concatenated string
            values = [claims[x] for x in name_claim if x in claims]
            if len(values) == len(name_claim):
                return " ".join(str(x) for x in values)
    return None
