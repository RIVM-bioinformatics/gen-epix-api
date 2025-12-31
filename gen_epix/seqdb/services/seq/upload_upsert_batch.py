from uuid import UUID

from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def _upsert_batch_refdata(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Upsert reference data as part of creating or updating the sample data.
    """
    user_id = cmd.user.id if cmd.user else None
    success = True

    # Add any new alleles
    alleles = cmd.sample_batch.alleles
    if alleles:
        created_alleles = self.repository.crud(
            uow,
            user_id,
            model.Allele,
            alleles,
            None,
            operation=CrudOperation.CREATE_SOME,
        )
    return success


def _upsert_batch_create_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Upsert sample data as part of creating or updating the sample data.


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
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples

    # Determine which samples need to be created
    to_create_sample_result_pairs = [
        (x, y)
        for x, y in zip(samples, sample_results)
        if x.id is None and y.status == UploadStatus.PENDING
    ]
    if not to_create_sample_result_pairs:
        return True

    # Create samples
    _upload_create_objects(
        self,
        uow,
        user_id,
        model.Sample,
        to_create_sample_result_pairs,  # type:ignore[arg-type]
    )

    return True


def _upsert_batch_update_samples(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Update existing sample data as part of updating the sample data.
    This function only updates samples that already exist; it does not create new samples.
    It updates the props dictionary of each sample based on the provided updates,
    and adjusts the corresponding SampleUploadResult accordingly.
    """
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = True

    # Determine which samples need to be updated
    to_update_sample_result_pairs = [
        (x, y)
        for x, y in zip(samples, sample_results)
        if x.id is not None and y.status == UploadStatus.PENDING
    ]
    if not to_update_sample_result_pairs:
        return success

    return _upload_update_objects(
        self,
        uow,
        user_id,
        model.Sample,
        model.STORED_MODEL_FIELD_PROPS[model.Sample],
        to_update_sample_result_pairs,  # type:ignore[arg-type]
    )

    return success


def _upsert_batch_create_associated_data(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Create associated data as part of creating or updating the sample data.
    """
    user_id = cmd.user.id if cmd.user else None
    samples = cmd.sample_batch.samples
    sample_results = retval.samples
    success = False

    # Prepare some data
    rev_map = {
        y: x for x, y in model.SampleForUpload.FOR_UPLOAD_MODEL_CLASS_MAP.items()
    }
    model_class_map: dict[str, type[model.Model]] = {
        y: rev_map[x]
        for x, y in model.SampleForUpload.MODEL_DATA_FIELD_NAME_MAP.items()
    }

    # Create each associated data type for each sample
    for field_name, model_class in model_class_map.items():
        # Determine which objects need to be created
        to_create_obj_result_pairs = []
        for sample, sample_result in zip(samples, sample_results):
            objs: list[model.Model] | None = getattr(sample, field_name)
            obj_results: list[UploadResult] | None = getattr(sample_result, field_name)
            for obj, obj_result in zip(objs or [], obj_results or []):
                if obj.id is None and obj_result.status == UploadStatus.PENDING:
                    to_create_obj_result_pairs.append((obj, obj_result))
        if not to_create_obj_result_pairs:
            continue

        # Create the objects
        _upload_create_objects(
            self,
            uow,
            user_id,
            model_class,
            to_create_obj_result_pairs,
        )

    success = True
    return success


def _upsert_batch_update_associated_data(
    self: BaseSeqService,
    cmd: command.UploadSamplesCommand,
    retval: model.SampleBatchUploadResult,
    uow: BaseUnitOfWork,
) -> bool:
    """
    Update associated data as part of creating or updating the sample data.
    """
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
        for x, y in model.SampleForUpload.MODEL_DATA_FIELD_NAME_MAP.items()
    }

    # Update each associated data type for each sample
    for field_name, model_class in model_class_map.items():
        # Determine which objects need to be updated
        to_update_obj_result_pairs = []
        for sample, sample_result in zip(samples, sample_results):
            objs: list[model.Model] | None = getattr(sample, field_name)
            obj_results: list[UploadResult] | None = getattr(sample_result, field_name)
            for obj, obj_result in zip(objs or [], obj_results or []):
                if obj.id is not None and obj_result.status == UploadStatus.PENDING:
                    to_update_obj_result_pairs.append((obj, obj_result))
        if not to_update_obj_result_pairs:
            continue

        success &= _upload_update_objects(
            self,
            uow,
            user_id,
            model_class,
            model.STORED_MODEL_FIELD_PROPS[model_class],
            to_update_obj_result_pairs,
        )
    return success


def _upload_create_objects(
    self: BaseSeqService,
    uow: BaseUnitOfWork,
    user_id: UUID | None,
    model_class: type[model.Model],
    to_create_obj_result_pairs: list[tuple[model.Model, UploadResult]],
) -> bool:
    """
    Create new objects and update the corresponding UploadResults.
    ️"""
    # Create objects
    to_create_objs = [x for x, _ in to_create_obj_result_pairs]
    to_create_obj_results = [x for _, x in to_create_obj_result_pairs]
    created_obj_ids: list[UUID] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user_id,
        model_class,
        to_create_objs,
        None,
        operation=CrudOperation.CREATE_SOME,
        return_id=True,
    )

    # Assign object ID and status to results
    for created_obj_id, obj_result in zip(created_obj_ids, to_create_obj_results):
        obj_result.id = created_obj_id
        obj_result.status = UploadStatus.CREATED

    return True


def _upload_update_objects(
    self: BaseSeqService,
    uow: BaseUnitOfWork,
    user_id: UUID | None,
    model_class: type[model.Model],
    stored_model_field_props: dict[str, model.ModelFieldProps],
    to_update_obj_result_pairs: list[tuple[model.Model, UploadResult]],
) -> bool:
    """
    Update existing objects and update the corresponding UploadResults.
    """

    success = True
    # Retrieve existing objects
    obj_ids = [x.id for x, _ in to_update_obj_result_pairs]
    existing_objs: list[model.Model] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user_id,
        model_class,
        None,
        obj_ids,
        operation=CrudOperation.READ_SOME,
    )

    # Determine which samples actually need to be updated instead of having identical data
    to_update_objs: list[model.Model] = []
    to_update_obj_results: list[model.UploadResult] = []
    for (obj, obj_result), existing_obj in zip(
        to_update_obj_result_pairs, existing_objs
    ):
        # Only check props for updates, other fields are not updatable
        is_updated = False
        for field_name, field_props in stored_model_field_props.items():
            existing_value = getattr(existing_obj, field_name)
            # Field if the field, with its existing value, is (still) mutable
            if not field_props.is_mutable_value(existing_value):
                success = False
                obj_result.status = UploadStatus.FAILED
                obj_result.add_error(
                    "d3c9f6b1",
                    f"Field {field_name} with existing value {existing_value} may not be updated.",
                )
                continue
            # Update the existing object's field if the new value is different
            new_value = getattr(obj, field_name)
            if existing_value is None:
                # Existing value is None: set new value if not None
                if new_value:
                    is_updated = True
                    setattr(existing_obj, field_name, new_value)
            elif field_props.is_dict:
                # Field content is a dict: update keys individually
                is_updated |= _upload_update_objects_dict_value(
                    existing_value, new_value
                )
            elif field_props.is_list:
                is_updated |= _upload_update_objects_list_value(
                    existing_value, new_value
                )
            else:
                # Field content is a single value: compare directly
                if new_value != existing_value:
                    is_updated = True
                    setattr(existing_obj, field_name, new_value)
        # Determine whether to update, i.e. if any values are indeed different, or otherwise skip
        if not is_updated:
            obj_result.status = UploadStatus.SKIPPED
            obj_result.add_info("f7a8b2d4", "Content is identical")
        else:
            to_update_objs.append(obj)
            to_update_obj_results.append(obj_result)

    # Stop if there were errors
    if not success:
        return success

    # Update the objects whose data are different
    if not to_update_objs:
        return success
    updated_obj_ids: list[UUID] = self.repository.crud(  # type:ignore[assignment]
        uow,
        user_id,
        model_class,
        to_update_objs,
        None,
        operation=CrudOperation.UPDATE_SOME,
        return_id=True,
    )

    # Assign object ID and status to results
    for updated_obj_id, obj_result in zip(updated_obj_ids, to_update_obj_results):
        obj_result.id = updated_obj_id
        obj_result.status = UploadStatus.UPDATED

    return success


def _upload_update_objects_dict_value(content: dict, updates: dict | None) -> bool:
    """
    Update a dictionary in place with new values and return whether any updates were
    made.

    An update is made if:
    - A key from updates does not exist in content and its value is not
        None, add it to content.
    - A key from updates exists in content:
        - If the new value is None: the key is then also removed from content.
        - If the new value is different from the existing value.
    """
    is_updated = False
    if updates is None:
        return is_updated
    for key, value in updates.items():
        if key not in content:
            if value is not None:
                # New key with not None value, update it
                is_updated = True
                content[key] = value
        else:
            orig_value = content.get(key)
            if value is None:
                # New value is None, remove the key
                if orig_value is not None:
                    is_updated = True
                del content[key]
            elif orig_value != value:
                # New value is different, update it
                is_updated = True
                content[key] = value
            else:
                # New value is the same, do nothing
                pass
    return is_updated


def _upload_update_objects_list_value(
    existing_value: list, new_value: list | None
) -> bool:
    """
    Update a list in place with new values and return whether any updates were made.

    An update is made if:
    - The new value is None and the existing list is not empty: clear the existing
      list.
    - The new value is a list and is different from the existing list: replace the
      existing list.
    """
    is_updated = False
    if new_value is None:
        if existing_value:
            # Existing list is not empty, clear it
            is_updated = True
            existing_value.clear()
    else:
        # Replace existing list with new list if different
        if new_value != existing_value:
            is_updated = True
            min_len = min(len(existing_value), len(new_value))
            max_len = max(len(existing_value), len(new_value))
            for i in range(min_len):
                existing_value[i] = new_value[i]
            if len(new_value) > len(existing_value):
                # New value has more items, extend the existing list
                existing_value.extend(new_value[min_len:max_len])
    return is_updated
