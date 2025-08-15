from test.fastapp import enum
from test.fastapp.model import DOMAIN, Model1_1, Model1_2, Model2_1, Model2_2
from typing import ClassVar, Type

from gen_epix import fastapp
from gen_epix.fastapp.model import CrudCommand


class Model1_1CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model1_1


class Model1_2CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model1_2


class Model2_1CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model2_1


class Model2_2CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model2_2


COMMANDS_BY_SERVICE: dict[enum.ServiceType, list[Type[fastapp.Command]]] = {
    enum.ServiceType.SERVICE1: [
        Model1_1CrudCommand,
        Model1_2CrudCommand,
    ],
    enum.ServiceType.SERVICE2: [
        Model2_1CrudCommand,
        Model2_2CrudCommand,
    ],
}

for service_type, command_classes in COMMANDS_BY_SERVICE.items():
    for command_class in command_classes:
        DOMAIN.register_command(command_class, service_type=service_type)
