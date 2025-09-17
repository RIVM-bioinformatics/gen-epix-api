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


# CRUD
