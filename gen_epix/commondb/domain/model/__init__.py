# pylint: disable=useless-import-alias
import gen_epix.fastapp as fastapp
from gen_epix.commondb.domain import enum
from gen_epix.commondb.domain.model.abac import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.commondb.domain.model.base import Model as Model
from gen_epix.commondb.domain.model.organization import Contact as Contact
from gen_epix.commondb.domain.model.organization import DataCollection as DataCollection
from gen_epix.commondb.domain.model.organization import (
    DataCollectionSet as DataCollectionSet,
)
from gen_epix.commondb.domain.model.organization import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.domain.model.organization import (
    ExternalIdentifier as ExternalIdentifier,
)
from gen_epix.commondb.domain.model.organization import (
    ExternalIdentifierForUpload as ExternalIdentifierForUpload,
)
from gen_epix.commondb.domain.model.organization import (
    IdentifierIssuer as IdentifierIssuer,
)
from gen_epix.commondb.domain.model.organization import Organization as Organization
from gen_epix.commondb.domain.model.organization import (
    OrganizationIdentifierIssuerLink as OrganizationIdentifierIssuerLink,
)
from gen_epix.commondb.domain.model.organization import (
    OrganizationSet as OrganizationSet,
)
from gen_epix.commondb.domain.model.organization import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.domain.model.organization import Site as Site
from gen_epix.commondb.domain.model.organization import User as User
from gen_epix.commondb.domain.model.organization import UserInvitation as UserInvitation
from gen_epix.commondb.domain.model.organization import (
    UserInvitationConstraints as UserInvitationConstraints,
)
from gen_epix.commondb.domain.model.organization import UserNameEmail as UserNameEmail
from gen_epix.commondb.domain.model.system import Outage as Outage
from gen_epix.commondb.domain.model.system import PackageMetadata as PackageMetadata
from gen_epix.commondb.domain.model.upload import (
    BaseBatchForUpload as BaseBatchForUpload,
)
from gen_epix.commondb.domain.model.upload import (
    BaseBatchUploadResult as BaseBatchUploadResult,
)
from gen_epix.commondb.domain.model.upload import DataIssue as DataIssue
from gen_epix.commondb.domain.model.upload import IsNewIdMixin as IsNewIdMixin
from gen_epix.commondb.domain.model.upload import ParentForUpload as ParentForUpload
from gen_epix.commondb.domain.model.upload import (
    ParentUploadResult as ParentUploadResult,
)
from gen_epix.commondb.domain.model.upload import UploadResult as UploadResult
from gen_epix.commondb.domain.util import (
    complete_stored_model_field_props as complete_stored_model_field_props,
)
from gen_epix.fastapp.model import ModelFieldProps as ModelFieldProps
from gen_epix.fastapp.services.auth import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth import IDPUser as IDPUser

SORTED_MODELS_BY_SERVICE_TYPE: dict[
    enum.ServiceType, tuple[type[fastapp.Model], ...]
] = {
    enum.ServiceType.AUTH: (
        IdentityProvider,
        IDPUser,
    ),
    enum.ServiceType.SYSTEM: (Outage, PackageMetadata),
    enum.ServiceType.ORGANIZATION: (
        Organization,
        OrganizationSet,
        OrganizationSetMember,
        DataCollection,
        DataCollectionSet,
        DataCollectionSetMember,
        IdentifierIssuer,
        OrganizationIdentifierIssuerLink,
        ExternalIdentifier,
        Site,
        Contact,
        UserNameEmail,
        User,
        UserInvitation,
        UserInvitationConstraints,
    ),
    enum.ServiceType.RBAC: tuple(),
    enum.ServiceType.ABAC: (OrganizationAdminPolicy,),
}

SORTED_SERVICE_TYPES = tuple(SORTED_MODELS_BY_SERVICE_TYPE.keys())

COMMON_MODEL_MAP: dict[type[fastapp.Model], type[fastapp.Model]] = {}
