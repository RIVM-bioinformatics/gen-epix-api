"""Authentication-related application commands."""

from pydantic import Field

from gen_epix.fastapp.model import Command


class GetIdentityProvidersCommand(Command):
    """Represents a request to execute identity-provider retrieval.

    Set `public` to restrict results to publicly available providers.
    """

    public: bool = Field(
        default=False, description="Whether to get only public identity providers"
    )
