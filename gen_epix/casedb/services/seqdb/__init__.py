"""Expose local and remote seqdb collaborators used by casedb services.

``SeqdbService`` dispatches casedb sequence requests, while ``SeqdbRemoteApp``
provides the remote seqdb application client used for cross-domain commands.
"""

# pylint: disable=useless-import-alias
from gen_epix.casedb.services.seqdb.service import SeqdbService as SeqdbService
from gen_epix.seqdb.services import SeqdbRemoteApp as SeqdbRemoteApp
