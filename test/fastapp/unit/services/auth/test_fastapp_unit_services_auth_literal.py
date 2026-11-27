"""Verify authentication value validation patterns."""

import pytest

from gen_epix.fastapp.services.auth.literal import EMAIL_PATTERN


@pytest.mark.parametrize("email", ["user@example.com", "user.name+tag@example.org"])
def test_email_pattern_accepts_complete_addresses(email: str) -> None:
    """Accept valid addresses that occupy the complete input string."""
    assert EMAIL_PATTERN.match(email) is not None


@pytest.mark.parametrize("email", ["user@example.com\n", "user@example.com\r\n"])
def test_email_pattern_rejects_trailing_line_terminators(email: str) -> None:
    """Reject addresses followed by line terminators."""
    assert EMAIL_PATTERN.match(email) is None
