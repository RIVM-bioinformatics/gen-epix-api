from uuid import UUID

from pydantic import BaseModel

import gen_epix.casedb.domain.model as model
from gen_epix.casedb.domain.model import Model
from gen_epix.fastapp import PermissionTypeSet

EXCLUDED_PERMISSIONS: dict = {
    model.User: PermissionTypeSet.CU,
    model.UserInvitation: PermissionTypeSet.CU,
    model.CaseSet: PermissionTypeSet.C,
}


class UpdateAssociationRequestBody(BaseModel):
    obj_ids1: list[UUID] | UUID | None = None
    obj_ids2: list[UUID] | UUID | None = None
    association_objs: list[Model] | None = None
