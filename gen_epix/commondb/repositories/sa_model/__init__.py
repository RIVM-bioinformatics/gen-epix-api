# pylint: disable=useless-import-alias
from gen_epix.commondb.domain import DOMAIN, enum, model
from gen_epix.commondb.repositories.sa_model.abac import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.commondb.repositories.sa_model.abac import (
    OrganizationAdminPolicyMixin as OrganizationAdminPolicyMixin,
)
from gen_epix.commondb.repositories.sa_model.base import (
    DB_METADATA_FIELDS as DB_METADATA_FIELDS,
)
from gen_epix.commondb.repositories.sa_model.base import (
    GENERATE_SERVICE_METADATA as GENERATE_SERVICE_METADATA,
)
from gen_epix.commondb.repositories.sa_model.base import (
    SERVICE_METADATA_FIELDS as SERVICE_METADATA_FIELDS,
)
from gen_epix.commondb.repositories.sa_model.base import (
    NoIdRowMetadataMixin as NoIdRowMetadataMixin,
)
from gen_epix.commondb.repositories.sa_model.base import (
    RowMetadataMixin as RowMetadataMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import Contact as Contact
from gen_epix.commondb.repositories.sa_model.organization import (
    ContactMixin as ContactMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollection as DataCollection,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionMixin as DataCollectionMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionSet as DataCollectionSet,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionSetMemberMixin as DataCollectionSetMemberMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    DataCollectionSetMixin as DataCollectionSetMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    ExternalIdentifier as ExternalIdentifier,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    ExternalIdentifierMixin as ExternalIdentifierMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    IdentifierIssuer as IdentifierIssuer,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    IdentifierIssuerMixin as IdentifierIssuerMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    Organization as Organization,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationIdentifierIssuerLink as OrganizationIdentifierIssuerLink,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationMixin as OrganizationMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationSet as OrganizationSet,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationSetMemberMixin as OrganizationSetMemberMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    OrganizationSetMixin as OrganizationSetMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import Site as Site
from gen_epix.commondb.repositories.sa_model.organization import SiteMixin as SiteMixin
from gen_epix.commondb.repositories.sa_model.organization import User as User
from gen_epix.commondb.repositories.sa_model.organization import (
    UserInvitation as UserInvitation,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    UserInvitationMixin as UserInvitationMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import UserMixin as UserMixin
from gen_epix.commondb.repositories.sa_model.system import Outage as Outage
from gen_epix.commondb.repositories.sa_model.system import OutageMixin as OutageMixin
from gen_epix.commondb.repositories.sa_model.util import create_field_metadata
from gen_epix.commondb.repositories.sa_model.util import (
    create_field_metadata as create_field_metadata,
)
from gen_epix.commondb.repositories.sa_model.util import (
    create_mapped_column as create_mapped_column,
)
from gen_epix.commondb.repositories.sa_model.util import (
    create_table_args as create_table_args,
)
from gen_epix.commondb.repositories.sa_model.util import (
    get_mixin_mapped_column as get_mixin_mapped_column,
)
from gen_epix.commondb.repositories.sa_model.util import (
    set_entity_repository_model_classes,
)
from gen_epix.commondb.repositories.sa_model.util import (
    set_entity_repository_model_classes as set_entity_repository_model_classes,
)

SA_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, dict[type[model.Model], type]] = {
    enum.ServiceType.ABAC: {
        model.OrganizationAdminPolicy: OrganizationAdminPolicy,
    },
    enum.ServiceType.ORGANIZATION: {
        model.Contact: Contact,
        model.DataCollection: DataCollection,
        model.DataCollectionSet: DataCollectionSet,
        model.DataCollectionSetMember: DataCollectionSetMember,
        model.Organization: Organization,
        model.OrganizationSet: OrganizationSet,
        model.OrganizationSetMember: OrganizationSetMember,
        model.Site: Site,
        model.User: User,
        model.UserInvitation: UserInvitation,
        model.IdentifierIssuer: IdentifierIssuer,
        model.OrganizationIdentifierIssuerLink: OrganizationIdentifierIssuerLink,
        model.ExternalIdentifier: ExternalIdentifier,
    },
    enum.ServiceType.SYSTEM: {
        model.Outage: Outage,
    },
}

FIELD_NAME_MAP: dict[type, dict[str, str]] = {}

set_entity_repository_model_classes(
    DOMAIN,
    SA_MODELS_BY_SERVICE_TYPE,
    RowMetadataMixin,
    field_name_map=FIELD_NAME_MAP,
)

SERVICE_METADATA_FIELDS, DB_METADATA_FIELDS, GENERATE_SERVICE_METADATA = (
    create_field_metadata(DOMAIN)
)
