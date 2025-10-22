from gen_epix.fastapp.model import Command


class GetIdentityProvidersCommand(Command):
    public: bool = False  # Whether to get only public identity providers
