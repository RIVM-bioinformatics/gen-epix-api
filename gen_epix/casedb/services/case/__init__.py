"""Expose the concrete service that handles casedb case-domain commands.

``CaseService`` coordinates case validation, persistence, retrieval, statistics,
uploads, and seqdb collaboration through the command lifecycle.
"""

# pylint: disable=useless-import-alias
from gen_epix.casedb.services.case.service import CaseService as CaseService
