"""Authentication-related application commands."""

from pydantic import Field

from gen_epix.fastapp.model import Command


class GetIdentityProvidersCommand(Command):
    """Command that retrieves the configured identity providers."""

    public: bool = Field(
        default=False, description="Whether to get only public identity providers"
    )
