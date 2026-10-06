"""Expose local and remote seqdb collaborators used by casedb services.

``SeqdbService`` dispatches casedb sequence requests, while ``SeqdbClient``
provides the remote seqdb application client used for cross-domain commands.
"""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports

if TYPE_CHECKING:
    from gen_epix.casedb.services.seqdb.service import SeqdbService as SeqdbService
    from gen_epix.seqdb.services import SeqdbClient as SeqdbClient

# Resolved on first access, so that importing the remote client does not load
# the seqdb application composition used for the local variant
_LAZY_EXPORTS: dict[str, LazyExport] = {
    **exports_from("gen_epix.casedb.services.seqdb.service", "SeqdbService"),
    **exports_from("gen_epix.seqdb.services", "SeqdbClient"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)
