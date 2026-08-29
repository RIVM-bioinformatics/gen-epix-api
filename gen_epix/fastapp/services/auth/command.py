"""Authentication-related application commands."""

from pydantic import Field

from gen_epix.fastapp.model import Command


class GetIdentityProvidersCommand(Command):
    """Provide the get identity providers command framework abstraction."""

    public: bool = Field(
        default=False, description="Whether to get only public identity providers"
    )
