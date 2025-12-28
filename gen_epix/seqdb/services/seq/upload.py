from typing import Any

from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.commondb.domain.model import UploadResult
from gen_epix.seqdb.domain import command, enum, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService
from gen_epix.seqdb.services.seq.upload_verify_batch import (
    _verify_batch_associated_data,
    _verify_batch_external_ids,
    _verify_batch_sample_existence,
)


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
        success &= _verify_batch_external_ids(self, cmd, retval, uow)
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
