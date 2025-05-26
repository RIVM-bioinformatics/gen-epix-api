from gen_epix.fastapp import PermissionTypeSet
from gen_epix.seqdb.domain import model

EXCLUDED_PERMISSIONS: dict = {
    model.User: PermissionTypeSet.CU,
    model.UserInvitation: PermissionTypeSet.CU,
}
