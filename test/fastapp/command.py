from test.fastapp.model import DOMAIN, Model1_1, Model1_2, Model2_1, Model2_2
from typing import ClassVar

from gen_epix.fastapp.model import CrudCommand


class Model1_1CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model1_1


class Model1_2CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model1_2


class Model2_1CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model2_1


class Model2_2CrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = Model2_2


DOMAIN.register_locals(locals())
