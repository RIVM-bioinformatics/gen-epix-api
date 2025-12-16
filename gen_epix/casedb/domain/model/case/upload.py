from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.casedb.domain.model.case.operational_data import Case
from gen_epix.casedb.domain.model.seqdb import ReadSet as ReadSet
from gen_epix.casedb.domain.model.seqdb import Seq as Seq
from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.organization import ExternalIdentifierForUpload
from gen_epix.fastapp.domain import Entity
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain.model import ReadSetForUpload as SeqdbReadSetForUpload
from gen_epix.seqdb.domain.model import SeqForUpload as SeqdbSeqForUpload


class ReadSetForUpload(SeqdbReadSetForUpload):
    """
    A single read set to be uploaded and associated with both an existing case in
    casedb and a potentially existing sample in seqdb. Equal to the corresponding
    seqdb model, with an additional case_type_col_id property.

    Description of the seqdb model:
    """

    __doc__ = f"{__doc__}{SeqdbReadSetForUpload.__doc__}"

    ENTITY: ClassVar = Entity(persistable=False)

    case_type_col_id: UUID = Field(
        description="The ID of the case type column with column type genetic reads that the read set is or will be associated with."
    )


class SeqForUpload(SeqdbSeqForUpload):
    """
    A single sequence to be uploaded and associated with both an existing case in
    casedb and a potentially existing sample in seqdb. The sample can be identified
    in seqdb either by its internal ID (sample_id) or by an external identifier
    (external_sample_id). The ID of created sequence is intended to be added to
    the corresponding case in casedb as the content of the given case type column.

    Description of the seqdb model:
    """

    __doc__ = f"{__doc__}{SeqdbSeqForUpload.__doc__}"

    ENTITY: ClassVar = Entity(persistable=False)

    case_type_col_id: UUID = Field(
        description="The ID of the case type column that the sequence is or will be associated with."
    )


class CaseForUpload(Case):
    """
    A case intended for upload, together with any relevant associated data.
    """

    ENTITY: ClassVar = Entity(persistable=False)
    NAME: ClassVar = "CaseForUpload"

    # Case level data
    external_ids: list[ExternalIdentifierForUpload] | None = Field(
        default=None,
        description="The external identifiers associated with the sample, if available.",
    )
    data_collection_ids: list[UUID] | None = Field(
        default=None,
        description="The data collection IDs that the sample should be put in. If None, this element is not taken into consideration during the upload.",
    )

    # Associated data
    has_content: bool = Field(
        default=False,
        description="Indicates whether the case has content to be uploaded, since content is a mandatory field and the distinction can otherwise not be made. If False, content must be empty.",
    )
    read_sets: list[ReadSetForUpload] | None = Field(
        default=None,
        description="The read sets to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different case type column.",
    )
    seqs: list[SeqForUpload] | None = Field(
        default=None,
        description="The sequences to be uploaded and associated with the case. If None, this element is not taken into consideration during the upload. Must each be for a different case type column.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        # Verify that external_ids contains no duplicates
        if self.external_ids is not None and len(self.external_ids) != len(
            set(self.external_ids)
        ):
            raise ValueError("external_ids must not contain duplicates.")
        # Verify that has_content is consistent with content
        if not self.has_content and self.content:
            raise ValueError(
                "has_content is False, but content is not empty. Content must be empty."
            )
        # Verify that read_sets contains no duplicate case_type_col_id
        if self.read_sets is not None:
            case_type_col_ids = [x.case_type_col_id for x in self.read_sets]
            if len(case_type_col_ids) != len(set(case_type_col_ids)):
                raise ValueError(
                    "read_sets must not contain duplicate case_type_col_id."
                )
        # Verify that seqs contains no duplicate case_type_col_id
        if self.seqs is not None:
            case_type_col_ids = [x.case_type_col_id for x in self.seqs]
            if len(case_type_col_ids) != len(set(case_type_col_ids)):
                raise ValueError("seqs must not contain duplicate case_type_col_id.")
        return self


class CasesForUpload(Model):
    """
    A number of unique cases intended for upload. The parameters specifying the
    upload operation are specified elsewhere.
    """

    ENTITY: ClassVar = Entity(persistable=False)

    cases: list[CaseForUpload] = Field(description="The cases to be uploaded.")

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        # Verify that cases contain no duplicate case_ids
        case_ids = [x.id for x in self.cases if x.id is not None]
        if len(case_ids) != len(set(case_ids)):
            raise ValueError("cases must not contain duplicate case IDs.")
        # Verify that cases contains no duplicate external_ids
        all_external_ids = []
        for case in self.cases:
            if case.external_ids is not None:
                all_external_ids.extend(case.external_ids)
        if len(all_external_ids) != len(set(all_external_ids)):
            raise ValueError("cases must not contain duplicate external_ids.")
        return self
