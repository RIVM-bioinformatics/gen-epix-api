from enum import Enum

from gen_epix.commondb.domain import enum


def get_role_set_map(role_map: dict[Enum, Enum]) -> dict[Enum, set[Enum]]:
    reverse_role_map = {y: x for x, y in role_map.items()}
    role_set_map: dict[Enum, set[Enum]] = {}
    for role_set in enum.RoleSet:
        role_set_map[role_set] = {reverse_role_map[x] for x in role_set.value}
    return role_set_map


# def map_permission_tuples(
#     permission_tuples: set[tuple[type[Command], PermissionTypeSet]],
#     role_map: dict[Enum, Enum],
# ) -> set[tuple[type[Command], PermissionTypeSet]]:
