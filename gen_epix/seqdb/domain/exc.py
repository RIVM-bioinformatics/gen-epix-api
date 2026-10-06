"""Provide seqdb functionality for domain.exc."""

# pylint: disable=wildcard-import, unused-wildcard-import
# because this is a package, and imported as such in other modules

from typing import TYPE_CHECKING

from gen_epix._lazy import lazy_star_exports
from gen_epix.fastapp.exc import *

if TYPE_CHECKING:
    from gen_epix.fastapp.api.exc import *

# The HTTP exceptions depend on FastAPI and are resolved on first access, so that
# the domain exceptions can be imported without it
if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_star_exports(__name__, "gen_epix.fastapp.api.exc")
