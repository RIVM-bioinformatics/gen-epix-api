from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.command import Command

# Non-CRUD


class RetrieveGeneticSequenceByIdCommand(Command):
    """
    Retrieve a genetic sequence by its ID.
    """

    seq_ids: list[UUID] = Field(
        description="The IDs of the genetic sequences to retrieve."
    )


class RetrieveGeneticSequenceFastaByIdCommand(Command):
    """
    Retrieve a set of genetic sequences in FASTA format based on a set of sequence IDs.
    An iterator is returned that yields the FASTA lines.
    """

    seq_ids: list[UUID] = Field(
        description="The IDs of the genetic sequences to retrieve."
    )
    wrap: int = Field(
        default=80,
        description="The line length to wrap sequences at, or 0 for no wrapping.",
    )


# CRUD
