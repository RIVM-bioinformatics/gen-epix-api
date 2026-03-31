# pylint: disable=useless-import-alias
from gen_epix import fastapp
from gen_epix.commondb.domain import enum as common_enum
from gen_epix.commondb.domain import model as common_model
from gen_epix.commondb.domain.model import (
    SORTED_MODELS_BY_SERVICE_TYPE as _COMMON_SORTED_MODELS_BY_SERVICE_TYPE,
)
from gen_epix.commondb.domain.model import BaseIdentifier as BaseIdentifier
from gen_epix.commondb.domain.model import Contact as Contact
from gen_epix.commondb.domain.model import DataCollection as DataCollection
from gen_epix.commondb.domain.model import DataCollectionSet as DataCollectionSet
from gen_epix.commondb.domain.model import (
    DataCollectionSetMember as DataCollectionSetMember,
)
from gen_epix.commondb.domain.model import IdentifierForUpload as IdentifierForUpload
from gen_epix.commondb.domain.model import IdentifierIssuer as IdentifierIssuer
from gen_epix.commondb.domain.model import Model as Model
from gen_epix.commondb.domain.model import Organization as Organization
from gen_epix.commondb.domain.model import (
    OrganizationAdminPolicy as OrganizationAdminPolicy,
)
from gen_epix.commondb.domain.model import (
    OrganizationIdentifierIssuerLink as OrganizationIdentifierIssuerLink,
)
from gen_epix.commondb.domain.model import OrganizationSet as OrganizationSet
from gen_epix.commondb.domain.model import (
    OrganizationSetMember as OrganizationSetMember,
)
from gen_epix.commondb.domain.model import Outage as Outage
from gen_epix.commondb.domain.model import Site as Site
from gen_epix.commondb.domain.model import UploadResult as UploadResult
from gen_epix.commondb.domain.model import User as User
from gen_epix.commondb.domain.model import UserInvitation as UserInvitation
from gen_epix.commondb.domain.model import (
    UserInvitationConstraints as UserInvitationConstraints,
)
from gen_epix.commondb.domain.model import UserNameEmail as UserNameEmail
from gen_epix.commondb.domain.util import complete_stored_model_field_props
from gen_epix.fastapp.model import ModelFieldProps
from gen_epix.fastapp.services.auth import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth import IDPUser as IDPUser
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.file import File as File
from gen_epix.seqdb.domain.model.seq import Allele as Allele
from gen_epix.seqdb.domain.model.seq import AlleleForUpload as AlleleForUpload
from gen_epix.seqdb.domain.model.seq import AstMeasurement as AstMeasurement
from gen_epix.seqdb.domain.model.seq import AstPrediction as AstPrediction
from gen_epix.seqdb.domain.model.seq import BaseSeq as BaseSeq
from gen_epix.seqdb.domain.model.seq import (
    CalculateSeqDistancesResult as CalculateSeqDistancesResult,
)
from gen_epix.seqdb.domain.model.seq import CodeMixin as CodeMixin
from gen_epix.seqdb.domain.model.seq import ContentMixin as ContentMixin
from gen_epix.seqdb.domain.model.seq import Contig as Contig
from gen_epix.seqdb.domain.model.seq import Locus as Locus
from gen_epix.seqdb.domain.model.seq import LocusCodeMap as LocusCodeMap
from gen_epix.seqdb.domain.model.seq import LocusSet as LocusSet
from gen_epix.seqdb.domain.model.seq import PcrMeasurement as PcrMeasurement
from gen_epix.seqdb.domain.model.seq import PhylogeneticTree as PhylogeneticTree
from gen_epix.seqdb.domain.model.seq import Protocol as Protocol
from gen_epix.seqdb.domain.model.seq import ProtocolSet as ProtocolSet
from gen_epix.seqdb.domain.model.seq import ProtocolSetMember as ProtocolSetMember
from gen_epix.seqdb.domain.model.seq import QualityMixin as QualityMixin
from gen_epix.seqdb.domain.model.seq import ReadSet as ReadSet
from gen_epix.seqdb.domain.model.seq import ReadSetForUpload as ReadSetForUpload
from gen_epix.seqdb.domain.model.seq import ReadSetIdentifier as ReadSetIdentifier
from gen_epix.seqdb.domain.model.seq import RefAllele as RefAllele
from gen_epix.seqdb.domain.model.seq import Sample as Sample
from gen_epix.seqdb.domain.model.seq import SampleBatchForUpload as SampleBatchForUpload
from gen_epix.seqdb.domain.model.seq import (
    SampleBatchUploadResult as SampleBatchUploadResult,
)
from gen_epix.seqdb.domain.model.seq import (
    SampleDataCollectionLink as SampleDataCollectionLink,
)
from gen_epix.seqdb.domain.model.seq import SampleDataIssue as SampleDataIssue
from gen_epix.seqdb.domain.model.seq import SampleForUpload as SampleForUpload
from gen_epix.seqdb.domain.model.seq import SampleIdentifier as SampleIdentifier
from gen_epix.seqdb.domain.model.seq import SampleUploadResult as SampleUploadResult
from gen_epix.seqdb.domain.model.seq import Seq as Seq
from gen_epix.seqdb.domain.model.seq import SeqClassification as SeqClassification
from gen_epix.seqdb.domain.model.seq import (
    SeqClassificationForUpload as SeqClassificationForUpload,
)
from gen_epix.seqdb.domain.model.seq import SeqDistance as SeqDistance
from gen_epix.seqdb.domain.model.seq import SeqForUpload as SeqForUpload
from gen_epix.seqdb.domain.model.seq import SeqIdentifier as SeqIdentifier
from gen_epix.seqdb.domain.model.seq import SeqProfile as SeqProfile
from gen_epix.seqdb.domain.model.seq import SeqProfileForUpload as SeqProfileForUpload
from gen_epix.seqdb.domain.model.seq import SeqProfileIdentifier as SeqProfileIdentifier
from gen_epix.seqdb.domain.model.seq import SeqTaxonomy as SeqTaxonomy
from gen_epix.seqdb.domain.model.seq import Taxon as Taxon
from gen_epix.seqdb.domain.model.seq import TaxonSet as TaxonSet
from gen_epix.seqdb.domain.model.seq import TaxonSetMember as TaxonSetMember
from gen_epix.seqdb.domain.model.seq import TreeAlgorithm as TreeAlgorithm
from gen_epix.seqdb.domain.model.seq import TreeAlgorithmClass as TreeAlgorithmClass
from gen_epix.seqdb.domain.model.seq.category import SeqCategory as SeqCategory
from gen_epix.seqdb.domain.model.seq.category import SeqCategorySet as SeqCategorySet
from gen_epix.seqdb.domain.model.seq.ref_seq import RefSeq as RefSeq
from gen_epix.util import add_parent_class_docs

# List up model classes per service and sorted according to links topology
SORTED_MODELS_BY_SERVICE_TYPE: dict[enum.ServiceType, list[type[fastapp.Model]]] = (
    {  # pyright: ignore[reportAssignmentType]
        # Common models
        enum.ServiceType.AUTH: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.AUTH]
        ),
        enum.ServiceType.SYSTEM: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.SYSTEM]
        ),
        enum.ServiceType.RBAC: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.RBAC]
        ),
        enum.ServiceType.ORGANIZATION: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.ORGANIZATION]
        ),
        # Specific models
        enum.ServiceType.ABAC: list(
            _COMMON_SORTED_MODELS_BY_SERVICE_TYPE[common_enum.ServiceType.ABAC]
        ),
        enum.ServiceType.FILE: [File],
        enum.ServiceType.SEQ: [
            Taxon,
            TaxonSet,
            TaxonSetMember,
            Locus,
            LocusSet,
            LocusCodeMap,
            BaseSeq,
            RefSeq,
            RefAllele,
            TreeAlgorithmClass,
            TreeAlgorithm,
            SeqCategorySet,
            SeqCategory,
            Protocol,
            ProtocolSet,
            ProtocolSetMember,
            Sample,
            SampleDataCollectionLink,
            SampleIdentifier,
            ReadSet,
            ReadSetIdentifier,
            Seq,
            SeqIdentifier,
            Allele,
            SeqProfile,
            SeqProfileIdentifier,
            AstMeasurement,
            AstPrediction,
            PcrMeasurement,
            SeqClassification,
            SeqClassificationForUpload,
            SeqDistance,
            SeqTaxonomy,
            PhylogeneticTree,
            ReadSetForUpload,
            SeqForUpload,
            AlleleForUpload,
            SeqProfileForUpload,
            SampleForUpload,
            SampleBatchForUpload,
            SampleUploadResult,
            CalculateSeqDistancesResult,
            SampleBatchUploadResult,
        ],
    }
)

SORTED_SERVICE_TYPES = tuple(SORTED_MODELS_BY_SERVICE_TYPE.keys())

COMMON_MODEL_MAP: dict[type[fastapp.Model], type[fastapp.Model]] = {
    common_model.User: User,
    common_model.UserInvitation: UserInvitation,
    common_model.UserInvitationConstraints: UserInvitationConstraints,
    common_model.OrganizationAdminPolicy: OrganizationAdminPolicy,
}

# Additional field properties for models that have already been stored (persisted)
STORED_MODEL_FIELD_PROPS: dict[type[fastapp.Model], dict[str, ModelFieldProps]] = {
    Sample: {"props": ModelFieldProps(is_mutable_always=True, is_sub_field_dict=True)},
    ReadSet: {
        "fwd_uri": ModelFieldProps(is_mutable_always=True),
        "rev_uri": ModelFieldProps(is_mutable_always=True),
        "fwd_file_id": ModelFieldProps(is_mutable_always=True),
        "rev_file_id": ModelFieldProps(is_mutable_always=True),
        "file_format": ModelFieldProps(is_mutable_always=True),
        "file_compression": ModelFieldProps(is_mutable_always=True),
        "sequencing_run_code": ModelFieldProps(is_mutable_always=True),
    },
    Seq: {
        "uri": ModelFieldProps(is_mutable_always=True),
        "file_id": ModelFieldProps(is_mutable_always=True),
        "file_format": ModelFieldProps(is_mutable_always=True),
        "file_compression": ModelFieldProps(is_mutable_always=True),
        "read_set_id": ModelFieldProps(is_mutable_if_empty=True),
    },
}
complete_stored_model_field_props(
    STORED_MODEL_FIELD_PROPS, SORTED_MODELS_BY_SERVICE_TYPE
)
add_parent_class_docs(
    set.union(
        *[
            set(y)
            for x, y in SORTED_MODELS_BY_SERVICE_TYPE.items()
            if x
            not in {
                enum.ServiceType.AUTH,
                enum.ServiceType.SYSTEM,
                enum.ServiceType.RBAC,
                enum.ServiceType.ORGANIZATION,
            }
        ]
    ),
    exclude=(Model,),
)
