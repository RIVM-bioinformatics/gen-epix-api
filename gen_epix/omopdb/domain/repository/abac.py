"""OmopDB specialization of the shared attribute-based access repository."""

from gen_epix.commondb.domain.repository import (
    BaseAbacRepository as CommonBaseAbacRepository,
)


class BaseAbacRepository(CommonBaseAbacRepository):
    """Encapsulates the commondb ABAC repository contract for OmopDB composition."""
