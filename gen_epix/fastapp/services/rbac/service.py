import abc
from enum import Enum
from typing import Any, Hashable, Type

from gen_epix.fastapp import (
    BaseService,
    EventTiming,
    Permission,
    PermissionType,
    PermissionTypeSet,
    exc,
)
from gen_epix.fastapp.model import Command, User
from gen_epix.fastapp.services.rbac.policy import RbacPolicy


class BaseRbacService(BaseService):
    """
    Abstract base class for a Role-Based Access Control (RBAC) service. Implement this
    class to provide RBAC functionality to the application. Most methods already have
    an implementation, but the following methods must be implemented by the subclass:
    - retrieve_user_roles: retrieve the roles of a user

    A role is defined as a hashable object such as a string or an Enum, which is
    registered with this service together with the associated Permissions. The service
    can subsequently register a policy for commands to which RBAC applies and which
    checks if the user has the required permission to execute the command through the
    role(s) they have been assigned.
    """

    SERVICE_TYPE = "RBAC"

    def __init__(self, *args: list, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._permissions_without_rbac: set[Permission] = set()
        self._permissions_by_role: dict[Hashable, set[Permission]] = {}
        self._roles_by_permission: dict[Permission, set[Hashable]] = {
            x: set() for x in self.app.domain.permissions
        }
        self._sub_roles_by_role: dict[Hashable, set[Hashable]] = {}

    @property
    def permissions_without_rbac(self) -> set[Permission]:
        return self._permissions_without_rbac

    @property
    def permissions_by_role(self) -> dict[Hashable, set[Permission]]:
        return self._permissions_by_role

    @property
    def roles_by_permission(self) -> dict[Permission, set[Hashable]]:
        return self._roles_by_permission

    def register_handlers(self) -> None:
        """
        No handlers to register in base implementation. Override as needed.
        """
        pass

    def register_permission_without_rbac(self, permission: Permission) -> None:
        """
        Register a permission that is not subject to RBAC. This can be used for
        permissions or commands that are not associated with a role, but are still used
        in the application.
        """
        roles = self._roles_by_permission[permission]
        if roles:
            roles_str = ", ".join([str(x) for x in roles])
            raise exc.ServiceException(
                f"Permission {permission} has some roles registered: {roles_str}"
            )
        self._permissions_without_rbac.add(permission)

    def unregister_permission_without_rbac(self, permission: Permission) -> None:
        """
        Unregister a permission that is not subject to RBAC. This can be used for
        permissions that are not associated with a role, but are still used in the
        application.
        """
        if permission not in self._permissions_without_rbac:
            raise exc.ServiceException(f"Permission {permission} is not registered")
        self._permissions_without_rbac.remove(permission)

    def register_role(
        self, role: Hashable, permissions: set[Permission], update_role: bool = True
    ) -> None:
        """
        Register a role with the associated permissions, or update an existing role's
        permissions. In case of dynamic roles, i.e. that can be changed at runtime, call
        register_role at runtime in when a role is updated or added. In case of multiple
        objs, a mechanism should be implemented to ensure that the role is
        (eventually) updated or added in all objs.
        """
        # Check if all permissions are registered
        invalid_permissions = permissions - self.app.domain.permissions
        if invalid_permissions:
            invalid_permissions_str = ", ".join([str(x) for x in invalid_permissions])
            raise exc.ServiceException(
                f"Permission(s) {invalid_permissions_str} are not registered"
            )
        # Add to permissions by role
        if role in self._permissions_by_role:
            if not update_role:
                raise exc.ServiceException(f"Role {role} is already registered")
            removed_permissions = self._permissions_by_role[role] - permissions
            for permission in removed_permissions:
                self._roles_by_permission[permission].remove(role)
            permissions = permissions - self._permissions_by_role[role]
        else:
            self._permissions_by_role[role] = permissions
        # Add to roles by permission
        for permission in permissions:
            self._roles_by_permission[permission].add(role)
        # Remove from role hierarchy so that it can be recalculated
        for sub_roles in self._sub_roles_by_role.values():
            if role in sub_roles:
                sub_roles.remove(role)
        self._sub_roles_by_role.pop(role, None)

    def register_roles(
        self,
        role_permissions: dict[
            Hashable, set[Permission | tuple[type[Command], PermissionType]]
        ],
        root_role: Hashable | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Register multiple roles with the associated permissions. This is a convenience
        method to register multiple roles at once. The permissions are given as a set of
        Permission objects or tuples of Command class and PermissionType. The root_role
        is optional and is used to check that the root role has all permissions. The
        keyword arguments are passed to the register_role method.
        """
        for role, permissions_or_tuples in role_permissions.items():
            permissions = {
                (
                    x
                    if isinstance(x, Permission)
                    else self.app.domain.get_permission(x[0], x[1])
                )
                for x in permissions_or_tuples
            }
            if root_role and role == root_role:
                all_permissions = self.app.domain.permissions
                missing_permissions = all_permissions - permissions
                if missing_permissions:
                    missing_permissions_str = ", ".join(
                        [str(x) for x in missing_permissions]
                    )
                    raise exc.InitializationServiceError(
                        f"Root role {root_role} is missing permissions: {missing_permissions_str}"
                    )
            self.register_role(role, permissions, **kwargs)

    def unregister_role(self, role: Hashable) -> None:
        """
        Unregister a role. In case of dynamic roles, i.e. that can be changed at
        runtime, call unregister_role at runtime in when a role is deleted. In case
        of multiple objs, a mechanism should be implemented to ensure that the
        role is (eventually) unregistered in all objs.

        Any RBAC policies for the corresponding permissions will be updated
        automatically.
        """
        if role not in self._permissions_by_role:
            raise exc.ServiceException(f"Role {role} is not registered")
        for permission in self._permissions_by_role[role]:
            self._roles_by_permission[permission].remove(role)
        del self._permissions_by_role[role]

    def verify_roles_exist_for_all_permission(self) -> None:
        """
        Verify that all permissions that are subject to RBAC have at least one role
        registered. This is useful to ensure that no such permission is forgotten to be
        associated with a role.
        """
        missing_permissions = self.app.domain.permissions - {
            x for x in self._roles_by_permission if not self._roles_by_permission[x]
        }
        if missing_permissions:
            missing_permissions_str = ", ".join([str(x) for x in missing_permissions])
            raise exc.ServiceException(
                f"No roles for permission(s) {missing_permissions_str}"
            )

    def get_rbac_permissions_for_command_class(
        self, command_class: Type[Command]
    ) -> set[Permission]:
        """
        Get the permissions for a command class that are subject to RBAC, i.e. which are
        registered to be subject to RBAC.
        """
        return (
            self.app.domain.get_permissions_for_command(command_class)
            - self._permissions_without_rbac
        )

    def get_command_classes_with_rbac(self) -> set[Type[Command]]:
        """
        Get all command classes that are subject to RBAC, i.e. for which at least one
        permission is registered to be subject to RBAC.
        """
        permissions = self.app.domain.permissions - self._permissions_without_rbac
        return {self.app.domain.get_command_for_permission(x) for x in permissions}

    def get_sub_roles(self, role: Hashable) -> set[Hashable]:
        """
        Get all sub roles of a role, i.e. all roles whose permissions are a subset of
        the role in question. The role hierarchy is calculated lazily.
        """
        if role not in self._sub_roles_by_role:
            self._sub_roles_by_role[role] = set()
            permissions = self._permissions_by_role[role]
            for other_role, other_permissions in self._permissions_by_role.items():
                if other_role == role:
                    continue
                if other_permissions < permissions:
                    self._sub_roles_by_role[role].add(other_role)
        return self._sub_roles_by_role[role]

    @abc.abstractmethod
    def retrieve_user_roles(self, user: User) -> set[Hashable]:
        """
        Implement this method to retrieve the roles of a user.
        """
        raise NotImplementedError

    def retrieve_user_is_non_rbac_authorized(self, cmd: Command) -> bool:
        """
        Overriding this method provides a mechanism for a user to exist but
        (currently) not being authorized to execute the command in question,
        regardless of whether the user has the required permission through their roles.
        This is one way to implement non role-based access control.
        """
        return True

    def retrieve_user_is_root(self, user: User) -> bool:
        """
        Overriding this method provides a mechanism for a root user to exist, which is
        always allowed to execute any command.
        """
        return False

    def retrieve_user_permissions(self, user: User) -> set[Permission]:
        """
        Retrieve all permissions that a user has.
        """
        return set.union(
            set(),
            *[self._permissions_by_role[x] for x in self.retrieve_user_roles(user)],
        )

    def retrieve_user_has_all_rbac_permissions(self, user: User) -> bool:
        """
        Retrieve whether a user has all permissions that are subject to RBAC.
        """
        return (
            len(
                self.app.domain.permissions
                - self.retrieve_user_permissions(user)
                - self._permissions_without_rbac
            )
            == 0
        )

    def retrieve_user_has_more_permissions(
        self, user: User, tgt_user_or_roles: User | set[Hashable]
    ) -> bool:
        """
        Retrieve whether a user has more permissions than a target user or a set of
        roles. This is useful for determining whether a user can perform an action on
        another user.
        """
        if isinstance(tgt_user_or_roles, User):
            permissions = self.retrieve_user_permissions(tgt_user_or_roles)
        else:
            permissions = set.union(
                set(),
                *[self._permissions_by_role[x] for x in tgt_user_or_roles],
            )
        return not self.retrieve_user_permissions(user).issubset(permissions)

    def register_rbac_policies(self, **kwargs: Any) -> None:
        """
        Register an RBAC policy for every command that is subject to RBAC. In case of
        dynamic roles, i.e. that can be changed at runtime, these policies remain
        up-to-date as long as the updates are submitted to this service.

        The default implementation of the policy functions can be overridden by passing
        them as keyword arguments. This is useful for testing or for adding additional
        functionality to the policy functions. The following functions can be overridden:
        - get_permission_for_command
        - get_permission_has_rbac
        - get_roles_by_permission
        - retrieve_user_roles
        - retrieve_user_is_non_rbac_authorized
        - retrieve_user_is_root
        """
        # Create arguments for the RBAC policy constructor
        policy_args = [
            "get_permission_for_command",
            "get_permission_has_rbac",
            "get_roles_by_permission",
            "retrieve_user_roles",
            "retrieve_user_is_non_rbac_authorized",
            "retrieve_user_is_root",
        ]
        for i, arg_name in enumerate(policy_args):
            # Get default function
            match arg_name:
                case "get_permission_for_command":
                    default_fun = (
                        lambda x: self.app.domain.get_permission_for_command_instance(x)
                    )
                case "get_permission_has_rbac":
                    default_fun = lambda x: x not in self._permissions_without_rbac
                case "get_roles_by_permission":
                    default_fun = lambda x: self._roles_by_permission[x]
                case "retrieve_user_roles":
                    default_fun = lambda x: self.retrieve_user_roles(x)
                case "retrieve_user_is_non_rbac_authorized":
                    default_fun = lambda x: self.retrieve_user_is_non_rbac_authorized(x)
                case "retrieve_user_is_root":
                    default_fun = lambda x: self.retrieve_user_is_root(x)
            # Override default function if provided as keyword argument
            policy_args[i] = kwargs.get(arg_name, default_fun)
        # Create a single RBAC policy with the provided functions
        rbac_policy = RbacPolicy(  # type: ignore
            *policy_args[0:-2],
            retrieve_user_is_non_rbac_authorized=policy_args[-2],
            retrieve_user_is_root=policy_args[-1],
        )
        # Register the RBAC policy for all command classes that are subject to RBAC
        for command_class in self.get_command_classes_with_rbac():
            self.app.register_policy(command_class, rbac_policy, EventTiming.BEFORE)

    @staticmethod
    def expand_hierarchical_role_permissions(
        role_hierarchy: dict[Hashable, set[Hashable]],
        role_permission_sets: dict[
            Hashable, set[tuple[type[Command], PermissionTypeSet]]
        ],
        verify_redundant_permissions: bool = True,
    ) -> dict[Hashable, set[tuple[type[Command], PermissionType]]]:
        """
        Add the permissions of all sub-roles in a role hierarchy to the current role.
        This is useful to describe all permissions only for the lowest roles in the
        hierarchy, avoiding code duplication and risk of inconsistencies.

        Permissions are given as a tuple[Command, PermissionTypeSet], so that this
        function can be called before the actual permissions are created by the domain.

        The role hierarchy is a dictionary where the keys are the roles and the values
        are all the roles that are below the key role in the hierarchy, i.e. not only
        the direct sub-roles.

        If verify_redundant_permissions is True, the function will raise an error if
        there are any redundant permissions in the role hierarchy, whereby a parent
        role has the same permission as one of its sub-roles. This can be help to
        ensure that the role hierarchy is indeed correctly defined.
        """

        def _get_permissions(
            role_permission_sets: set[tuple[type[Command], PermissionTypeSet]],
        ) -> set[tuple[type[Command], PermissionType]]:
            permissions = set()
            for command_class, permission_type_set in role_permission_sets:
                permissions.update(
                    {(command_class, x) for x in permission_type_set.value}
                )
            return permissions

        role_permissions_map = {}
        for role in role_hierarchy:
            role_permissions_map[role] = _get_permissions(
                role_permission_sets.get(role, set())
            )
            if verify_redundant_permissions:
                orig_role_permissions = role_permissions_map[role].copy()
            for sub_role in role_hierarchy.get(role, set()):
                # Add the permissions of the sub-role to the role
                sub_role_permissions = _get_permissions(
                    role_permission_sets.get(sub_role, set())
                )
                role_permissions_map[role].update(sub_role_permissions)
                if not verify_redundant_permissions:
                    continue
                # Check if any sub-role permissions are also in the role's unique
                # permissions
                redundant_permissions = sub_role_permissions.intersection(
                    orig_role_permissions
                )
                if not redundant_permissions:
                    continue
                # Some redundant permissions -> summarize them by command class and
                # raise an error
                command_classes = sorted(
                    {x[0] for x in redundant_permissions},
                    key=lambda x: x.__name__,
                )
                redundant_permission_sets = []
                for command_class in command_classes:
                    redundant_permission_sets.append(
                        PermissionTypeSet(
                            frozenset(
                                {
                                    x[1]
                                    for x in redundant_permissions
                                    if x[0] == command_class
                                }
                            )
                        )
                    )
                duplicate_permissions_str = ", ".join(
                    [
                        f"{x.__name__}.{y.name}"
                        for x, y in zip(command_classes, redundant_permission_sets)
                    ]
                )
                role_str = role.value if isinstance(role, Enum) else str(role)
                sub_role_str = (
                    sub_role.value if isinstance(sub_role, Enum) else str(sub_role)
                )
                raise exc.InitializationServiceError(
                    f"Duplicate permissions in role hierarchy for role {role_str} and sub-role {sub_role_str}: {duplicate_permissions_str}"
                )
        return role_permissions_map
