from uuid import UUID

from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.omop.base import BaseOmopService


class PersonValidator:

    def __init__(
        self,
        omop_service: BaseOmopService,
        user_id: UUID,
    ):
        self.omop_service = omop_service
        self.user_id = user_id
        # TODO: initialise members

        self._init_metadata()

    def validate_and_transform(
        self, cmd: command.UploadPersonsCommand, retval: model.PersonBatchUploadResult
    ) -> model.PersonBatchUploadResult:
        """
        Validate and transform the content of the persons in batch upload command.
        Where applicable, individual values are transformed from synonymous values to
        standard values, and combinations of values are transformed based on defined
        relations.

        The method adds resulting ValidatedPersonForUpload to the upload result,
        including any data issues found during validation and transformation.
        """
        data_issues_list = self._get_data_issues(cmd, retval)
        self.transform_individual_values(cmd, data_issues_list)
        self.transform_value_pairs(cmd, data_issues_list)

        return retval

    def _get_data_issues(
        self,
        cmd: command.UploadPersonsCommand,
        retval: model.PersonBatchUploadResult,
    ) -> list[list[model.PersonDataIssue] | None]:
        """
        Get references to data_issues for all persons, as a convenience for easily
        updating these in-place.
        """
        # Get and data_issues_list references
        data_issues_list: list[list[model.PersonDataIssue] | None] = [
            None if x is None else x.data_issues for x in retval.persons
        ]

        return data_issues_list

    def transform_individual_values(
        self,
        cmd: command.UploadPersonsCommand,
        data_issues_list: list[list[model.PersonDataIssue] | None],
    ) -> None:
        """Validate and transform individual values."""
        # TODO: implement
        pass

    def transform_value_pairs(
        self,
        cmd: command.UploadPersonsCommand,
        data_issues_list: list[list[model.PersonDataIssue] | None],
    ) -> None:
        """
        Validate and transform pairs of values.
        """
        # TODO: implement
        pass

    def _init_metadata(self) -> None:
        # TODO: implement
        pass
