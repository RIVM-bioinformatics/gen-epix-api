from pydantic import Field

from gen_epix.fastapp.model import Command


class GetIdentityProvidersCommand(Command):
    public: bool = Field(
        default=False, description="Whether to get only public identity providers"
    )
