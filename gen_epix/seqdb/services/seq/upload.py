from collections import defaultdict
from typing import Any
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.domain.enum import (
    IdentifierType,
    OnExistsUploadAction,
    UploadStatus,
)
from gen_epix.commondb.domain.model import UploadResult
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_number import EqualsNumberFilter
from gen_epix.filter.string_set import StringSetFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def seq_service_upload_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> model.SampleBatchUploadResult:
    """
    Upload a batch of samples along with their associated data.
    The data are uploaded as a single atomic unit of work, so that
    either all data are successfully uploaded or none are.

    Args:
        self: The SeqService instance
        cmd: Command containing the sample batch and upload options

    Returns:
        SampleBatchUploadResult containing the results of the upload operation
    """
    # Step 1: Check user rights
    _check_user_rights(self, cmd)

    # Step 2: Initialize the upload result
    retval = _initialize_upload_result(cmd)

    # Step 3: Check existence of samples and associated data
    # (May return early with errors in upload_result)
    success = _verify_batch(self, cmd, retval)
    if not success:  # Early return due to errors
        return retval

    # Step 4: Look up, complete and verify reference data links
    # (May return early with errors in upload_result)
    success = _retrieve_and_verify_reference_data(self, cmd, retval)
    if not success:  # Early return due to errors
        return retval

    # Step 5: Create or update the data
    _create_or_update_data(self, cmd, {}, retval)

    # Step 6: Return the upload result
    return retval


def _check_user_rights(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
) -> None:
    """
    Check if the user has the necessary rights to upload samples.

    Step 1: Check user rights
    1.1 Get user roles
    1.2 If user has any of the roles in the GE_APP_ADMIN role set, they are authorized.
    1.3 If user does not have any of the roles in the GE_APP_ADMIN role set, ABAC must be applied through the substeps below. The substeps below cannot yet be implemented since the ABAC policies are not yet available, so placeholders are added that must be included in the generated code.
    1.3.1 [PLACEHOLDER] Retrieve ABAC rights from cmd._policies.
    1.3.2 [PLACEHOLDER] For each sample in the batch, verify user has WRITE access to sample.created_in_data_collection_id
    1.3.3 [PLACEHOLDER] Error if the user is not authorized
    1.3.4 Consider the user authorized in any case for now, until ABAC can be implemented
    """
    # 1.1 Get user roles
    user_roles = cmd.user.roles if cmd.user else set()

    # 1.2 If user has any of the roles in the GE_APP_ADMIN role set, they are authorized
    if user_roles & enum.RoleSet.GE_APP_ADMIN.value:
        return  # User is authorized

    # 1.3 If user does not have any of the roles in the GE_APP_ADMIN role set, ABAC must be applied
    # 1.3.1 [PLACEHOLDER] Retrieve ABAC rights from cmd._policies
    # TODO: Implement ABAC rights retrieval when policies are available

    # 1.3.2 [PLACEHOLDER] For each sample in the batch, verify user has WRITE access to sample.created_in_data_collection_id
    for sample in cmd.sample_batch.samples:
        # TODO: Implement ABAC authorization check for WRITE access to data collection
        data_collection_id = sample.created_in_data_collection_id
        # Placeholder: Check if user has WRITE access to this data collection
        # user_has_write_access = check_abac_write_access(abac_rights, data_collection_id)
        pass

    # 1.3.3 [PLACEHOLDER] Error if the user is not authorized
    # TODO: Implement authorization error when ABAC is available
    # if not user_is_authorized:
    #     raise PermissionError(f"User {cmd.user.email if cmd.user else 'anonymous'} lacks required permissions to upload samples")

    # 1.3.4 Consider the user authorized in any case for now, until ABAC can be implemented
    # TODO: Remove this when ABAC authorization is fully implemented
    return  # User is considered authorized for now


def _initialize_upload_result(
    cmd: command.UploadSamplesCommand,
) -> model.SampleBatchUploadResult:
    """
    Initialize the upload result that will be the return value.

    Step 2: Initialize the upload result (SampleBatchUploadResult)
    2.1 For each sample in cmd.sample_batch.samples:
    2.1.1 For all associated data types (read_sets, seqs, allele_profiles, etc.):
    2.1.1.1 Create UploadResult for each instance with status PENDING
    2.1.1.1 Set the ID of the existing instance if available
    2.1.2 Create SampleUploadResult
    2.2 Create SampleBatchUploadResult
    """
    # Placeholder: create basic result structure
    sample_results = []
    base_upload_result = UploadResult(
        status=UploadStatus.PENDING,
    )

    def _create_sub_result(obj: Any | None) -> UploadResult | None:
        if obj is None:
            return None
        return UploadResult(
            id=getattr(obj, "id", None),
            status=UploadStatus.PENDING,
        )

    def _create_sub_results(objs: list | None) -> list[UploadResult] | None:
        if objs is None:
            return None
        return [
            UploadResult(
                id=getattr(x, "id", None),
                status=UploadStatus.PENDING,
            )
            for x in objs
        ]

    for sample in cmd.sample_batch.samples:
        sample_result = model.SampleUploadResult(
            status=UploadStatus.SKIPPED,
            sample=_create_sub_result(sample.props),
            external_ids=_create_sub_results(sample.external_ids),
            read_sets=_create_sub_results(sample.read_sets),
            seqs=_create_sub_results(sample.seqs),
            seq_taxonomies=_create_sub_results(sample.seq_taxonomies),
            seq_classifications=_create_sub_results(sample.seq_classifications),
            locus_profiles=_create_sub_results(sample.locus_profiles),
            allele_profiles=_create_sub_results(sample.allele_profiles),
            snp_profiles=_create_sub_results(sample.snp_profiles),
            mlva_profiles=_create_sub_results(sample.mlva_profiles),
            kmer_profiles=_create_sub_results(sample.kmer_profiles),
            seq_distances=_create_sub_results(sample.seq_distances),
            pcr_measurements=_create_sub_results(sample.pcr_measurements),
            ast_measurements=_create_sub_results(sample.ast_measurements),
        )
        sample_results.append(sample_result)

    return model.SampleBatchUploadResult(
        batch_id=cmd.sample_batch.id,
        status=UploadStatus.SKIPPED,
        samples=sample_results,
    )


def _verify_batch(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
) -> bool:
    """
    Check existence of samples and associated data.
    """
    success = True
    # Handle transaction
    with self.repository.uow() as uow:
        # Verify existence of samples by ID
        success &= _verify_batch_sample_existence(self, cmd, retval, uow)
        # Verify existence and consistency of external IDs
        success &= _verify_batch_external_ids(self, cmd, retval)
        # Verify existence and consistency of associated data as needed
        success &= _verify_batch_associated_data(self, cmd, retval, uow)
    return success


def _retrieve_and_verify_reference_data(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    upload_result: model.SampleBatchUploadResult,
) -> bool:
    """
    Look up, complete and verify reference data links.

    Step 4: Look up, complete and verify reference data links
    4.1 Sequence reads: currently nothing to do
    4.2 Sequences: currently nothing to do
    4.3 Allele profiles
    4.3.1 Retrieve unique locus set data
    4.3.1.1 Go over all sample_batch.samples and all allele profiles in them
    4.3.1.1.1 Extract all unique locus set IDs and codes. Map code to ID if both are provided. Error if a code maps to more than one ID. Adjust SampleBatchUploadResult return value accordingly and return.
    4.3.1.1.2 Retrieve all unique locus sets by both ID and code. Verify that those retrieved by code and that also had an ID provided, indeed actually have that ID. Error if not.
    4.3.2 Retrieve unique locus code map data
    4.3.2.1 Go over all sample_batch.samples and all allele profiles in them
    4.3.2.1.1 Extract all unique locus code maps IDs and codes.
    4.3.2.1.2 Retrieve all unique locus code maps by both ID and code. Verify that those retrieved by code and that also had an ID provided, indeed actually have that ID. Error if not. Adjust SampleBatchUploadResult return value accordingly and return.
    4.3.3 Verify and convert allele profile representation
    4.3.3.1 Initialise a unique map (dict) of allele ID to locus ID
    4.3.3.2 Go over all sample_batch.samples and all allele profiles in them
    4.3.3.2.1 If the allele profile is stored in the locus_allele_id_map field, i.e. explicitly contains (locus code map, locus code) or ID:
    4.3.3.2.1.1 Fill in the locus ID based on the locus code map retrieved in 4.3.1.1.1.
    4.3.3.2.1.2 Verify that those alleles for which both locus ID and code were provided, that the code indeed corresponds to the stored locus ID. Error if not. Adjust SampleBatchUploadResult return value accordingly and return.
    4.3.3.2.1.3 Convert the locus_allele_id_map allele profile representation to the allele_ids representation whereby the list of allele IDs is stored in the same order as the locus IDs in the locus set.
    4.3.3.2.2 If the allele profile is stored in the allele_profile, and depending on the allele_profile_format, convert it to the allele_ids representation
    4.3.3.2.3 Gover over all the allele IDs, and corresponding locus IDs via the locus set, in the allele_ids field
    4.3.3.2.3.1 If the allele ID already exists as key in the map of 4.3.3.1: check if the locus ID (i.e. the value) is the same. Error if not. Adjust SampleBatchUploadResult return value accordingly and return.
    4.3.3.2.3.2 If the allele ID does not exist as key, add it with the locus ID as value
    4.3.4 Retrieve unique allele data and verify locus IDs
    4.3.4.1 Retrieve any existing alleles for the unique allele IDs in the map of 4.3.3.1. Use the repository.crud method with READ_ALL operation and an UuidSetMemberFilter on the unique allele IDs.
    4.3.4.2 Verify that the retrieved alleles correspond to the same locus ID as in the map. Error if not. Adjust SampleBatchUploadResult return value accordingly and return.
    4.3.4.3 Create a subset of the map of 4.3.3.1 containing only the (allele ID, locus ID) pairs that are not yet persisted, i.e. that are new and should be provided as part of the sample_batch.
    4.3.4.4 Loop over all sample_batch.alleles
    4.3.4.4.1 Fill in locus ID if (locus code map, locus code) was provided
    4.3.4.4.2 Verify the locus Id against the map of 3.1.3.1. Error if not identical. Adjust SampleBatchUploadResult return value accordingly and return.
    4.3.4.4.3 If the allele is not yet persisted, flag it as such.
    4.3.4.4.4 Verify that all the alleles that are new and as such to be persisted in the map of 4.3.4.3 are indeed present in sample_batch.alleles. Error if not. Adjust SampleBatchUploadResult return value accordingly and return.
    """
    # TODO: Implement reference data lookup and verification
    # Return True since all operations were successful for now
    return True


def _create_or_update_data(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    reference_data: dict[str, Any],
    upload_result: model.SampleBatchUploadResult,
) -> None:
    """
    Create or update the sample data within a single unit of work.

    Step 5: Create or update the data
    5.1 Begin single Unit of Work encompassing all remaining steps
    5.2 Add new reference data
    5.2.1 Upload all the new sample_batch.alleles flagged in 3.1.4.4.3 using repository.crud with operation=CREATE_SOME
    5.3 Add sample data - loop over each sample in cmd.sample_batch.samples
    5.3.1 If new: create the sample and fill in the resulting sample_id in any associated data.
    5.3.2 If existing: update the sample
    5.3.2.1 If on_exists=UPDATE, update the props dict. For any of the new props that have value None, delete the key.
    5.3.2.2 If on_exists=SKIP, do not make any changes.
    5.3.3  Adjust the corresponding SampleUploadResult.sample_result correspondingly, including its status.
    5.3.4 Create any external identifiers that did not exist yet. Adjust the corresponding SampleUploadResult.external_ids_results correspondingly, including its status.
    5.3.5 Go over each type of associated data (read sets, seqs, allele profiles, ...).
    5.3.5.1 If new: create the instance and fill in the instance's id
    5.3.5.2 If existing:
    5.3.5.2.1 If on_exists=UPDATE, update the provided fields that are updatable through an upload action - these are the following:
    5.3.5.2.1.1 ReadSet: fwd_uri, rev_uri, fwd_file_id, rev_file_id, file_format, file_compression, sequencing_run_code
    5.3.5.2.1.2 Seq: uri, file_id, file_format, file_compression, read_set_id if existing value is None, read_set2_id if existing value is None, assembly_protocol_id if existing value is None, file_hash if existing value is None, contigs if existing value is empty list
    5.3.5.2.1.3 AlleleProfile: allele_profile, allele_profile_format, seq_id if existing value is None
    5.3.5.2.1.4 Error if a non-updatable field is different between existing and new value.
    5.3.5.2.2 If on_exists=SKIP, do not make any changes.
    5.3.5.3 Adjust the corresponding SampleUploadResult.external_ids_results correspondingly, including its status. If Error, roll back and stop here.
    5.4 Update profile distances. This is a placeholder step, to be added and described as such.
    """
    # TODO: Implement data creation and update within UoW
    # Update upload_result as operations proceed
    pass


def _verify_batch_sample_existence(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check sample existence when ID is given"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True
    sample_ids = list({x.id for x in samples if x.id is not None})
    has_existing_samples = False
    if sample_ids:
        # Some sample IDs are given, check existence
        # Check existence of given sample IDs
        samples_exist: list[bool] = self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            model.Sample,
            None,
            sample_ids,
            CrudOperation.EXISTS_SOME,
        )
        existing_sample_ids = {x for x, y in zip(sample_ids, samples_exist) if y}
        for sample, sample_result in zip(samples, sample_results):
            sample_id = sample.id
            if sample_id is None:
                # Sample ID not given, cannot exist
                continue
            if sample_id not in existing_sample_ids:
                # Sample ID is given but does not exist
                success = False
                sample_result.add_error("a8b4c2e9", f"ID does not exist")
                continue
            # Sample exists
            has_existing_samples = True
    if has_existing_samples and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "d3f5b6a1", "One or more samples already exist and on_exists=ERROR."
        )
    return success


def _verify_batch_external_ids(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
) -> bool:
    """Retrieve and verify identifier issuers in external IDs"""
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Retrieve and verify identifier issuers in external IDs provided by ID
    identifier_issuer_ids = list(
        {
            y.identifier_issuer_id
            for x in samples
            for y in x.external_ids or []
            if y.identifier_issuer_id is not None
        }
    )
    identifier_issuer_by_id_map: dict[UUID, model.IdentifierIssuer] = {}
    identifier_issuers: list[model.IdentifierIssuer] = []
    if identifier_issuer_ids:
        identifier_issuers = self.crud(  # type:ignore[assignment]
            command.IdentifierIssuerCrudCommand(
                user=cmd.user,
                obj_ids=list(identifier_issuer_ids),
                operation=CrudOperation.READ_SOME,
            )
        )
        identifier_issuer_by_id_map = {  # type: ignore[misc]
            x.id: x for x in identifier_issuers if x.id is not None
        }
        for sample, sample_result in zip(samples, sample_results):
            for external_id, external_id_result in zip(
                sample.external_ids or [], sample_result.external_ids or []
            ):
                identifier_issuer_id = external_id.identifier_issuer_id
                if identifier_issuer_id is None:
                    continue
                if identifier_issuer_id not in identifier_issuer_by_id_map:
                    success = False
                    external_id_result.add_error(
                        "c4d5e6f7",
                        f"Identifier issuer with ID {identifier_issuer_id} does not exist",
                    )

    # Retrieve and verify identifier issuers in external IDs provided by code
    identifier_issuer_codes = list(
        {
            y.identifier_issuer_code
            for x in samples
            for y in x.external_ids or []
            if y.identifier_issuer_code is not None
        }
    )
    identifier_issuer_by_code_map: dict[str, model.IdentifierIssuer] = {}
    if identifier_issuer_codes:
        identifier_issuers = self.crud(  # type:ignore[assignment]
            command.IdentifierIssuerCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ALL,
                query_filter=StringSetFilter(
                    key="code", members=frozenset(identifier_issuer_codes)
                ),
            )
        )
        identifier_issuer_by_code_map = {x.code: x for x in identifier_issuers}
        for sample, sample_result in zip(samples, sample_results):
            for i, (external_id, external_id_result) in enumerate(
                zip(
                    sample.external_ids or [],
                    sample_result.external_ids or [],
                )
            ):
                identifier_issuer_code = external_id.identifier_issuer_code
                if identifier_issuer_code is None:
                    continue
                if identifier_issuer_code not in identifier_issuer_by_code_map:
                    success = False
                    external_id_result.add_error(
                        "d6e7f8a9",
                        f"Identifier issuer with code {identifier_issuer_code} does not exist",
                    )
                    continue
                identifier_issuer = identifier_issuer_by_code_map[
                    identifier_issuer_code
                ]
                if external_id.identifier_issuer_id is not None:
                    if external_id.identifier_issuer_id != identifier_issuer.id:
                        success = False
                        external_id_result.add_error(
                            "e7f8a9b0",
                            f"Identifier issuer code {identifier_issuer_code} with ID {identifier_issuer.id} does not match provided ID {external_id.identifier_issuer_id}",
                        )
                else:
                    # Add identifier issuer ID, must be as a new instance since external_ids are frozen
                    if sample.external_ids is not None:
                        sample.external_ids[i] = external_id.model_copy(
                            update={"identifier_issuer_id": identifier_issuer.id}
                        )
                # Add to ID map as well
                if identifier_issuer.id is not None:
                    identifier_issuer_by_id_map[identifier_issuer.id] = identifier_issuer  # type: ignore[misc]

    # Retrieve and verify external IDs
    external_identifiers = list(
        {y.external_id for x in samples for y in x.external_ids or []}
    )
    if external_identifiers:
        # Get all SAMPLE external identifiers matching the provided external
        # identifiers and identifier issuers, but not their combination
        # This leaves the possibility that the same external identifier for a
        # different identifier issuer is retrieved: this is addressed after
        # retrieval, allowing a straightforward filter here
        existing_external_ids: list[model.ExternalIdentifier] = (
            self.crud(  # type:ignore[assignment]
                command.ExternalIdentifierCrudCommand(
                    user=cmd.user,
                    operation=CrudOperation.READ_ALL,
                    query_filter=CompositeFilter(
                        operator=LogicalOperator.AND,
                        filters=[
                            EqualsNumberFilter(
                                key="identifier_type",
                                value=IdentifierType.SAMPLE.value,
                            ),
                            UuidSetFilter(
                                key="identifier_issuer_id",
                                members=frozenset(identifier_issuer_by_id_map.keys()),
                            ),
                            StringSetFilter(
                                key="identifier",
                                members=frozenset(external_identifiers),
                            ),
                        ],
                    ),
                )
            )
        )
        existing_external_id_map: dict[tuple[UUID, str], model.ExternalIdentifier] = {
            (x.identifier_issuer_id, x.external_id): x for x in existing_external_ids
        }
        has_existing_samples = False
        for sample, sample_result in zip(samples, sample_results):
            for external_id, external_id_result in zip(
                sample.external_ids or [], sample_result.external_ids or []
            ):
                if external_id_result.status in [
                    UploadStatus.SKIPPED,
                    UploadStatus.FAILED,
                ]:
                    # Already skipped or failed, no need to check existence
                    continue
                key: tuple[UUID, str] = (external_id.identifier_issuer_id, external_id.external_id)  # type: ignore[assignment]
                if key in existing_external_id_map:
                    has_existing_samples = True
                    existing_external_id = existing_external_id_map[key]
                    # Cross-validate with sample ID if given
                    if sample.id is not None:
                        if existing_external_id.internal_id != sample.id:
                            success = False
                            external_id_result.add_error(
                                "f8a9b0c1",
                                f"External identifier {external_id.external_id} refers to sample ID {existing_external_id.internal_id}, which does not match provided sample ID {sample.id}",
                            )
                        # External ID already exists, nothing to upload
                        external_id_result.id = existing_external_id.id
                        external_id_result.status = UploadStatus.SKIPPED
                    else:
                        # Fill in sample ID
                        sample.id = existing_external_id.internal_id
        if has_existing_samples and cmd.on_exists == OnExistsUploadAction.ERROR:
            success = False
            retval.add_error(
                "a1c7d9f3",
                "One or more samples already exist and on_exists=ERROR",
            )

    return success


def _verify_batch_associated_data(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Check associated data existence and consistency"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Prepare some data
    rev_map = {
        y: x for x, y in model.SampleForUpload.FOR_UPLOAD_MODEL_CLASS_MAP.items()
    }
    model_class_map: dict[str, type[model.Model]] = {
        y: rev_map[x]
        for x, y in model.SampleForUpload.MODEL_RESULT_FIELD_NAME_MAP.items()
    }

    # Verify each associated data type for each sample
    has_existing_data = False
    for field_name, model_class in model_class_map.items():
        # Collect all IDs for this associated data type and determine existence
        obj_ids: list[UUID] = list(
            {
                y.id
                for x in samples
                for y in getattr(x, field_name) or []
                if y.id is not None
            }
        )
        if not obj_ids:
            # No associated data IDs to check
            continue
        objs_exist: list[bool] = self.repository.crud(  # type:ignore[assignment]
            uow,
            user_id,
            model_class,
            None,
            obj_ids,
            CrudOperation.EXISTS_SOME,
        )
        existing_obj_ids = {x for x, y in zip(obj_ids, objs_exist) if y}
        # Get (id, sample_id) for all existing ids
        existing_obj_sample_id_map: dict[UUID, UUID] = {}
        if existing_obj_ids:
            result_iter = self.repository.read_fields(
                uow,
                user_id,
                model_class,
                ["id", "sample_id"],
                filter=UuidSetFilter(key="id", members=frozenset(existing_obj_ids)),
            )
            existing_obj_sample_id_map = {x[0]: x[1] for x in result_iter}
        # Verify existence of associated data instances
        for i, (sample, sample_result) in enumerate(zip(samples, sample_results)):
            for obj, obj_result in zip(
                getattr(sample, field_name) or [],
                getattr(sample_result, field_name) or [],
            ):
                if obj.id is None:
                    # Instance does not exist yet, assign sample ID if existing
                    obj.sample_id = sample.id
                    continue
                if obj.id not in existing_obj_ids:
                    success = False
                    obj_result.add_error(
                        "d4f5e6a7",
                        f"ID does not exist",
                    )
                # Existing instance
                has_existing_data = True
                existing_sample_id = existing_obj_sample_id_map[obj.id]
                if sample.id is None:
                    # Fill in sample ID
                    sample.id = existing_sample_id
                else:
                    if sample.id != existing_sample_id:
                        success = False
                        obj_result.add_error(
                            "e5f6a7b8",
                            f"Associated data ID {obj.id} refers to sample ID {existing_sample_id}, which does not match provided sample ID {sample.id}",
                        )
    if has_existing_data and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "c6e7f8a0",
            f"One or more {model_class.NAME} instances already exist and on_exists=ERROR",
        )

    # Associated data class specific verifications
    success &= _verify_batch_seqs(self, cmd, retval, uow)
    success &= _verify_batch_allele_profiles(self, cmd, retval, uow)

    return success


def _verify_batch_seqs(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify seq specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Get dict[(sample_id, seq_hash), [(read_set_id, read_set2_id, assembly_protocol_id, id)]
    sample_ids = list({sample.id for sample in samples if sample.id is not None})
    if not sample_ids:
        return success  # No samples with ID, nothing to verify
    result_iter = self.repository.read_fields(
        uow,
        user_id,
        model.Seq,
        [
            "sample_id",
            "seq_hash",
            "read_set_id",
            "read_set2_id",
            "assembly_protocol_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=frozenset(sample_ids)),
    )
    key_map: defaultdict[tuple[UUID, UUID], list[tuple]] = defaultdict(list)
    for x in result_iter:
        key_map[(x[0], x[1])].append((x[2], x[3], x[4], x[5]))

    # Verify each seq
    has_existing_seqs = False
    for sample, sample_result in zip(samples, sample_results):
        if sample.id is None:
            # Sample does not exist
            continue
        for seq, seq_result in zip(sample.seqs or [], sample_result.seqs or []):
            existing_seq_data = key_map.get((sample.id, seq.seq_hash))
            if existing_seq_data is None:
                # No existing seq with this hash for this sample
                continue
            # Compare existing seqs with this hash
            for (
                read_set_id,
                read_set2_id,
                assembly_protocol_id,
                seq_id,
            ) in existing_seq_data:
                if seq.assembly_protocol_id != assembly_protocol_id:
                    # Different assembly protocol, cannot give rise to an issue
                    continue
                if seq.read_set_id == read_set_id and seq.read_set2_id == read_set2_id:
                    # Same read sets -> skip since the seq is identical and there are
                    # no immutable parts
                    seq.id = seq_id
                    seq_result.add_warning(
                        "a2b3c4d5",
                        f"Seq with same hash ({seq.seq_hash}), read sets and assembly protocol already exists",
                    )
                    seq_result.status = UploadStatus.SKIPPED
                    has_existing_seqs = True
                    break
                if seq.read_set_id is None and seq.read_set2_id is None:
                    # New seq with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same reads sets
                    success = False
                    seq_result.add_error(
                        "f1e2d3c4",
                        f"Seq with same hash ({seq.seq_hash}) and assembly protocol already exists with ID {seq_id}, but new seq has no read sets no read sets are provided for the new seq to compare",
                    )

    # Finalise checks
    if has_existing_seqs and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "b4c5d6e7",
            "One or more seqs already exist and on_exists=ERROR",
        )
    return success


def _verify_batch_allele_profiles(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: fastapp.BaseUnitOfWork,
) -> bool:
    """Verify allele profile specific rules"""
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Get sample IDs
    sample_ids = list({sample.id for sample in samples if sample.id is not None})
    if not sample_ids:
        # No existing samples, nothing to verify
        return success

    # Retrieve and verify locus detection protocols provided by ID and/or code
    protocol_tuples = list(
        {
            (y.locus_detection_protocol_id, y.locus_detection_protocol_code)
            for x in samples
            for y in x.allele_profiles or []
        }
    )
    protocol_ids = {x[0] for x in protocol_tuples if x[0] is not None}
    protocol_codes = {x[1] for x in protocol_tuples if x[1] is not None}
    protocol_id_code_map: dict[UUID, str] = {}
    protocol_code_id_map: dict[str, UUID] = {}
    if protocol_ids or protocol_codes:
        # Retrieve locus detection protocols by ID and code
        result_iter = self.repository.read_fields(
            uow,
            user_id,
            model.LocusDetectionProtocol,
            ["id", "code"],
            filter=CompositeFilter(
                operator=LogicalOperator.OR,
                filters=[
                    UuidSetFilter(key="id", members=frozenset(protocol_ids)),
                    StringSetFilter(key="code", members=frozenset(protocol_codes)),
                ],
            ),
        )
        protocol_id_code_map = {x[0]: x[1] for x in result_iter}
        protocol_code_id_map = {y: x for x, y in protocol_id_code_map.items()}
        # Verify locus detection protocols in allele profiles
        for sample, sample_result in zip(samples, sample_results):
            for allele_profile, allele_profile_result in zip(
                sample.allele_profiles or [], sample_result.allele_profiles or []
            ):
                protocol_id = allele_profile.locus_detection_protocol_id
                protocol_code = allele_profile.locus_detection_protocol_code
                if protocol_id and protocol_id not in protocol_id_code_map:
                    success = False
                    allele_profile_result.add_error(
                        "b2c3d4e5",
                        f"Locus detection protocol with ID {protocol_id} does not exist",
                    )
                if protocol_code:
                    if protocol_code not in protocol_code_id_map:
                        success = False
                        allele_profile_result.add_error(
                            "d4e5f6a7",
                            f"Locus detection protocol with code {protocol_code} does not exist",
                        )
                    elif (
                        protocol_id
                        and protocol_code_id_map[protocol_code] != protocol_id
                    ):
                        success = False
                        allele_profile_result.add_error(
                            "e5f6a7b8",
                            f"Locus detection protocol code {protocol_code} with ID {protocol_code_id_map[protocol_code]} does not match provided ID {protocol_id}",
                        )
                    elif not protocol_id:
                        # Add locus detection protocol ID
                        allele_profile.locus_detection_protocol_id = (
                            protocol_code_id_map[protocol_code]
                        )

    # Retrieve and verify locus sets provided by ID and/or code
    locus_set_tuples = list(
        {
            (y.locus_set_id, y.locus_set_code)
            for x in samples
            for y in x.allele_profiles or []
        }
    )
    locus_set_ids = {x[0] for x in locus_set_tuples if x[0] is not None}
    locus_set_codes = {x[1] for x in locus_set_tuples if x[1] is not None}
    locus_set_id_code_map: dict[UUID, str] = {}
    locus_set_code_id_map: dict[str, UUID] = {}
    if locus_set_ids or locus_set_codes:
        # Retrieve locus sets by ID and code
        result_iter = self.repository.read_fields(
            uow,
            user_id,
            model.LocusSet,
            ["id", "code"],
            filter=CompositeFilter(
                operator=LogicalOperator.OR,
                filters=[
                    UuidSetFilter(key="id", members=frozenset(locus_set_ids)),
                    StringSetFilter(key="code", members=frozenset(locus_set_codes)),
                ],
            ),
        )
        locus_set_id_code_map = {x[0]: x[1] for x in result_iter}
        locus_set_code_id_map = {y: x for x, y in locus_set_id_code_map.items()}
        # Verify locus sets in allele profiles
        for sample, sample_result in zip(samples, sample_results):
            for allele_profile, allele_profile_result in zip(
                sample.allele_profiles or [], sample_result.allele_profiles or []
            ):
                locus_set_id = allele_profile.locus_set_id
                locus_set_code = allele_profile.locus_set_code
                if locus_set_id and locus_set_id not in locus_set_id_code_map:
                    success = False
                    allele_profile_result.add_error(
                        "f6a7b8c9",
                        f"Locus set with ID {locus_set_id} does not exist",
                    )
                if locus_set_code:
                    if locus_set_code not in locus_set_code_id_map:
                        success = False
                        allele_profile_result.add_error(
                            "a7b8c9d0",
                            f"Locus set with code {locus_set_code} does not exist",
                        )
                    elif (
                        locus_set_id
                        and locus_set_code_id_map[locus_set_code] != locus_set_id
                    ):
                        success = False
                        allele_profile_result.add_error(
                            "b8c9d0e1",
                            f"Locus set code {locus_set_code} with ID {locus_set_code_id_map[locus_set_code]} does not match provided ID {locus_set_id}",
                        )
                    elif not locus_set_id:
                        # Add locus set ID
                        allele_profile.locus_set_id = locus_set_code_id_map[
                            locus_set_code
                        ]

    # Get dict[(sample_id, allele_profile_hash), [(locus_detection_protocol_id, locus_set_id, seq_id,id)]
    result_iter = self.repository.read_fields(
        uow,
        user_id,
        model.AlleleProfile,
        [
            "sample_id",
            "allele_profile_hash",
            "locus_detection_protocol_id",
            "locus_set_id",
            "seq_id",
            "id",
        ],
        filter=UuidSetFilter(key="sample_id", members=frozenset(sample_ids)),
    )
    key_map: defaultdict[tuple[UUID, UUID], list[tuple]] = defaultdict(list)
    for x in result_iter:
        key_map[(x[0], x[1])].append((x[2], x[3], x[4], x[5]))

    # Verify each allele profile
    has_existing_allele_profiles = False
    for sample, sample_result in zip(samples, sample_results):
        if sample.id is None:
            # Sample does not exist
            continue
        for allele_profile, allele_profile_result in zip(
            sample.allele_profiles or [], sample_result.allele_profiles or []
        ):
            existing_allele_profile_data = key_map.get(
                (sample.id, allele_profile.allele_profile_hash)
            )
            if existing_allele_profile_data is None:
                # No existing allele profile with this hash for this sample
                continue
            # Compare existing allele profiles with this hash
            for (
                locus_detection_protocol_id,
                locus_set_id,
                seq_id,
                allele_profile_id,
            ) in existing_allele_profile_data:
                if (
                    allele_profile.locus_detection_protocol_id
                    != locus_detection_protocol_id
                ):
                    # Different locus detection protocol, cannot give rise to an issue
                    continue
                if allele_profile.locus_set_id != locus_set_id:
                    # Different locus set, cannot give rise to an issue
                    continue
                if allele_profile.seq_id == seq_id:
                    # Same seq -> skip since the allele profile is identical and there are
                    # no immutable parts
                    allele_profile.id = allele_profile_id
                    allele_profile_result.add_warning(
                        "c7d8e9f0",
                        f"Allele profile with same hash ({allele_profile.allele_profile_hash}), seq and assembly protocol already exists",
                    )
                    allele_profile_result.status = UploadStatus.SKIPPED
                    has_existing_allele_profiles = True
                    break
                if allele_profile.seq_id is None:
                    # New allele profile with same hash but unknown read sets -> error since
                    # cannot verify if indeed it was derived from the same seq
                    success = False
                    allele_profile_result.add_error(
                        "a8f3e7b2",
                        f"Allele profile with same hash ({allele_profile.allele_profile_hash}) and assembly protocol already exists with ID {allele_profile_id}, but new allele profile has no seq ID provided for the new allele profile to compare",
                    )

    # Finalise checks
    if has_existing_allele_profiles and cmd.on_exists == OnExistsUploadAction.ERROR:
        success = False
        retval.add_error(
            "d8a3b7f4",
            "One or more allele profiles already exist and on_exists=ERROR",
        )
    return success
