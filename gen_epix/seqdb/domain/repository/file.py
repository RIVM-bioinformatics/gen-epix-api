"""Define seqdb domain interfaces and policies for domain.repository.file."""

from gen_epix.fastapp.repository import BaseRepository


# This class intentionally inherits the abstract repository contract unchanged.
# type: ignore[abstract-method]
class BaseFileRepository(BaseRepository):
    """Encapsulates the shared repository base for seqdb file persistence."""
