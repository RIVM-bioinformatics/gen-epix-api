"""Framework service implementations."""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports
from gen_epix.fastapp.services.auth import BaseAuthService as BaseAuthService
from gen_epix.fastapp.services.rbac import BaseRbacService as BaseRbacService
from gen_epix.fastapp.services.rbac import RbacPolicy as RbacPolicy

if TYPE_CHECKING:
    from gen_epix.fastapp.services.auth import AuthService as AuthService

# The authentication service depends on FastAPI and is resolved on first access,
# so that clients can use the service contracts without FastAPI installed
_LAZY_EXPORTS: dict[str, LazyExport] = exports_from(
    "gen_epix.fastapp.services.auth", "AuthService"
)

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)
