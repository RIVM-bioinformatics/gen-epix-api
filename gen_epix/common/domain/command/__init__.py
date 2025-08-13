from typing import Type

from gen_epix import fastapp
from gen_epix.common.domain import DOMAIN, enum
from gen_epix.common.domain.command.auth import (
    GetIdentityProvidersCommand as GetIdentityProvidersCommand,
)
from gen_epix.common.domain.command.base import Command as Command
from gen_epix.common.domain.command.base import CrudCommand as CrudCommand
from gen_epix.common.domain.command.base import (
    UpdateAssociationCommand as UpdateAssociationCommand,
)
from gen_epix.common.domain.command.organization import (
    ContactCrudCommand as ContactCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    DataCollectionCrudCommand as DataCollectionCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    DataCollectionSetCrudCommand as DataCollectionSetCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    DataCollectionSetDataCollectionUpdateAssociationCommand as DataCollectionSetDataCollectionUpdateAssociationCommand,
)
from gen_epix.common.domain.command.organization import (
    DataCollectionSetMemberCrudCommand as DataCollectionSetMemberCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    IdentifierIssuerCrudCommand as IdentifierIssuerCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    InviteUserCommand as InviteUserCommand,
)
from gen_epix.common.domain.command.organization import (
    OrganizationCrudCommand as OrganizationCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    OrganizationSetCrudCommand as OrganizationSetCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    OrganizationSetMemberCrudCommand as OrganizationSetMemberCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    OrganizationSetOrganizationUpdateAssociationCommand as OrganizationSetOrganizationUpdateAssociationCommand,
)
from gen_epix.common.domain.command.organization import (
    RegisterInvitedUserCommand as RegisterInvitedUserCommand,
)
from gen_epix.common.domain.command.organization import (
    RetrieveOrganizationContactCommand as RetrieveOrganizationContactCommand,
)
from gen_epix.common.domain.command.organization import (
    SiteCrudCommand as SiteCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    UpdateUserCommand as UpdateUserCommand,
)
from gen_epix.common.domain.command.organization import (
    UpdateUserOwnOrganizationCommand as UpdateUserOwnOrganizationCommand,
)
from gen_epix.common.domain.command.organization import (
    UserCrudCommand as UserCrudCommand,
)
from gen_epix.common.domain.command.organization import (
    UserInvitationCrudCommand as UserInvitationCrudCommand,
)
from gen_epix.common.domain.command.rbac import (
    RetrieveOwnPermissionsCommand as RetrieveOwnPermissionsCommand,
)
from gen_epix.common.domain.command.system import OutageCrudCommand as OutageCrudCommand
from gen_epix.common.domain.command.system import (
    RetrieveOutagesCommand as RetrieveOutagesCommand,
)

COMMANDS_BY_SERVICE: dict[enum.ServiceType, list[Type[fastapp.Command]]] = {
    enum.ServiceType.AUTH: [
        GetIdentityProvidersCommand,
    ],
    enum.ServiceType.ORGANIZATION: [
        ContactCrudCommand,
        DataCollectionCrudCommand,
        DataCollectionSetCrudCommand,
        DataCollectionSetDataCollectionUpdateAssociationCommand,
        DataCollectionSetMemberCrudCommand,
        IdentifierIssuerCrudCommand,
        InviteUserCommand,
        OrganizationCrudCommand,
        OrganizationSetCrudCommand,
        OrganizationSetMemberCrudCommand,
        OrganizationSetOrganizationUpdateAssociationCommand,
        RegisterInvitedUserCommand,
        RetrieveOrganizationContactCommand,
        SiteCrudCommand,
        UpdateUserCommand,
        UpdateUserOwnOrganizationCommand,
        UserCrudCommand,
        UserInvitationCrudCommand,
    ],
    enum.ServiceType.RBAC: [
        RetrieveOwnPermissionsCommand,
    ],
    enum.ServiceType.SYSTEM: [
        OutageCrudCommand,
        RetrieveOutagesCommand,
    ],
}

for service_type, command_classes in COMMANDS_BY_SERVICE.items():
    for command_class in command_classes:
        DOMAIN.register_command(command_class, service_type=service_type)
