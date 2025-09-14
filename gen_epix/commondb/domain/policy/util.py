from enum import Enum

from gen_epix.commondb.domain import enum


def get_role_set_map(role_map: dict[Enum, Enum]) -> dict[Enum, set[Enum]]:
    role_set_map: dict[Enum, set[Enum]] = {}
    for role_set in enum.RoleSet:
        role_set_map[role_set] = {role_map[x] for x in role_set.value}
    return role_set_map
