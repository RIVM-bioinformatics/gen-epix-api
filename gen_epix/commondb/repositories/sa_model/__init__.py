from gen_epix.commondb.domain import DOMAIN, enum
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
    IdentifierIssuer as IdentifierIssuer,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    IdentifierIssuerMixin as IdentifierIssuerMixin,
)
from gen_epix.commondb.repositories.sa_model.organization import (
    Organization as Organization,
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

set_entity_repository_model_classes(
    DOMAIN,
    enum.ServiceType,
    RowMetadataMixin,
    "gen_epix.commondb.repositories.sa_model",
)

SERVICE_METADATA_FIELDS, DB_METADATA_FIELDS, GENERATE_SERVICE_METADATA = (
    create_field_metadata(DOMAIN)
)
