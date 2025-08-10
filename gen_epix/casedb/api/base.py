import gen_epix.casedb.domain.model as model
from gen_epix.fastapp import PermissionTypeSet

EXCLUDED_PERMISSIONS: dict = {
    model.CaseSet: PermissionTypeSet.C,
}
