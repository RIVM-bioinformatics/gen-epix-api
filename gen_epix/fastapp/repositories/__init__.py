"""Repository implementations and unit-of-work exports."""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, lazy_exports
from gen_epix.fastapp.repositories.dict import DictRepository as DictRepository
from gen_epix.fastapp.repositories.dict import DictUnitOfWork as DictUnitOfWork

if TYPE_CHECKING:
    from gen_epix.fastapp.repositories.sa import SAMapper as SAMapper
    from gen_epix.fastapp.repositories.sa import SARepository as SARepository
    from gen_epix.fastapp.repositories.sa import SAUnitOfWork as SAUnitOfWork
    from gen_epix.fastapp.repositories.sa import (
        ServerUtcCurrentTime as ServerUtcCurrentTime,
    )
    from gen_epix.fastapp.repositories.sa import (
        ServerUtcTimestamp as ServerUtcTimestamp,
    )
    from gen_epix.fastapp.repositories.sa import (
        create_sa_type_from_field_info as create_sa_type_from_field_info,
    )

# The SQLAlchemy implementations are resolved on first access, so that the
# dictionary implementations can be imported without SQLAlchemy installed
_LAZY_EXPORTS: dict[str, LazyExport] = {
    "SAMapper": ("gen_epix.fastapp.repositories.sa", "SAMapper"),
    "SARepository": ("gen_epix.fastapp.repositories.sa", "SARepository"),
    "SAUnitOfWork": ("gen_epix.fastapp.repositories.sa", "SAUnitOfWork"),
    "ServerUtcCurrentTime": (
        "gen_epix.fastapp.repositories.sa",
        "ServerUtcCurrentTime",
    ),
    "ServerUtcTimestamp": ("gen_epix.fastapp.repositories.sa", "ServerUtcTimestamp"),
    "create_sa_type_from_field_info": (
        "gen_epix.fastapp.repositories.sa",
        "create_sa_type_from_field_info",
    ),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)
