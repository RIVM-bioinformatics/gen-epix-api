# pylint: disable=wildcard-import, unused-wildcard-import

from __future__ import annotations

from gen_epix.seqdb.domain import DOMAIN, enum
from gen_epix.seqdb.repositories.sa_model.base import RowMetadataMixin
from gen_epix.seqdb.repositories.sa_model.organization import *
from util.util import set_entity_repository_model_classes

set_entity_repository_model_classes(
    DOMAIN, enum.ServiceType, RowMetadataMixin, "gen_epix.seqdb.repositories.sa_model"
)
