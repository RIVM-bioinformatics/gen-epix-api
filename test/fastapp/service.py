from test.fastapp.command import (
    Model1_1CrudCommand,
    Model1_2CrudCommand,
    Model2_1CrudCommand,
    Model2_2CrudCommand,
)

from gen_epix.fastapp.service import BaseService


class Service1(BaseService):
    def register_handlers(self) -> None:
        self.app.register_handler(Model1_1CrudCommand, self.crud)
        self.app.register_handler(Model1_2CrudCommand, self.crud)


class Service2(BaseService):
    def register_handlers(self) -> None:
        self.app.register_handler(Model2_1CrudCommand, self.crud)
        self.app.register_handler(Model2_2CrudCommand, self.crud)
