import gen_epix.common.domain.model as common_model
from gen_epix.fastapp import PermissionTypeSet

EXCLUDED_PERMISSIONS: dict = {
    common_model.User: PermissionTypeSet.CU,
    common_model.UserInvitation: PermissionTypeSet.CU,
}
