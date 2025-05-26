from typing import Hashable


def serialize_id(value: Hashable) -> str | None:
    return str(value) if value else None
