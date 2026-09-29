"""Define casedb commands that retrieve sequence data from seqdb."""

from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.command import Command

# Non-CRUD


class RetrieveGeneticSequenceByIdCommand(Command):
    """Represent a request for genetic sequences identified by ID."""

    seq_ids: list[UUID] = Field(
        description="The IDs of the genetic sequences to retrieve."
    )


class RetrieveGeneticSequenceFastaByIdCommand(Command):
    """Represent a request for genetic sequences in FASTA format.

    The response is an iterator that yields FASTA lines for the requested
    sequence IDs using the configured wrapping width.
    """

    seq_ids: list[UUID] = Field(
        description="The IDs of the genetic sequences to retrieve."
    )
    wrap: int = Field(
        default=80,
        description="The line length to wrap sequences at, or 0 for no wrapping.",
    )


# CRUD
