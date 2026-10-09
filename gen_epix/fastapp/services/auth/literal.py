"""Regular expressions used to validate authentication values."""

import re

# TODO: LSP-3893 `user@example.com\n` can match before `$`; confirm trailing newlines
# should be rejected, since the current caller accepts this as a valid email.
EMAIL_PATTERN = re.compile(
    r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
)
