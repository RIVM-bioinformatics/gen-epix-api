"""Unit tests for authentication command models."""

import pytest

from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand


def test_public_defaults_to_false() -> None:
    assert GetIdentityProvidersCommand().public is False


@pytest.mark.parametrize(
    "public",
    [True, False],
    ids=["public-only", "all-providers"],
)
def test_public_accepts_explicit_filter(public: bool) -> None:
    command = GetIdentityProvidersCommand(public=public)

    assert command.public is public
