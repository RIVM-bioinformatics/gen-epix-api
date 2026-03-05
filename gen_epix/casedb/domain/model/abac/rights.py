from collections.abc import Callable
from uuid import UUID

from pydantic import BaseModel, Field

from gen_epix.casedb.domain.enum import CaseRight, CaseRightSet
from gen_epix.casedb.domain.model.case.non_persistable import (CaseRights,
                                                               CaseSetRights)
from gen_epix.fastapp import exc


class CaseTypeAccessAbac(BaseModel):
    case_type_id: UUID = Field(description="The ID of the case type")
    data_collection_id: UUID = Field(description="The ID of the data collection")
    is_private: bool = Field(
        description="Whether the data collection is private, limited to the case types in the case type set. When true, add/remove case and add/remove case set are considered (i) as the right to create/delete a case or case set in this data collection (setting case.created_in_data_collection to this data collection) and (ii) as the right to share the case or case set further in other data collections. Deleting a case or case set is only allowed when it can or has been removed from all other data collections as well."
    )
    add_case: bool = Field(
        description="Whether cases may be added, limited to the case type and data collection"
    )
    remove_case: bool = Field(
        description="Whether cases may be removed, limited to the case type and data collection"
    )
    add_case_set: bool = Field(
        description="Whether case sets may be added, limited to the case type and data collection"
    )
    remove_case_set: bool = Field(
        description="Whether case sets may be removed, limited to the case type and data collection"
    )
    read_case_type_col_ids: set[UUID] = Field(
        description="The IDs of the case type columns for which values can be read, limited to the case type and data collection"
    )
    write_case_type_col_ids: set[UUID] = Field(
        description="The IDs of the case type columns for which values can be updated, limited to the case types in the case type set"
    )
    read_case_set: bool = Field(
        description="Whether case set be read, limited to the case type and data collection"
    )
    write_case_set: bool = Field(
        description="Whether case set be updated, limited to the case type and data collection"
    )

    def has_any_rights(self) -> bool:
        """
        Determine if at least one of the rights is set.
        """
        return (
            self.add_case
            or self.remove_case
            or self.add_case_set
            or self.remove_case_set
            or len(self.read_case_type_col_ids) > 0
            or len(self.write_case_type_col_ids) > 0
            or self.read_case_set
            or self.write_case_set
        )


class CaseTypeShareAbac(BaseModel):
    case_type_id: UUID = Field(description="The ID of the case type")
    data_collection_id: UUID = Field(description="The ID of the data collection")
    add_case_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which cases may be added to this data collection, limited to the case type"
    )
    remove_case_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which cases may be removed from this data collection, limited to the case type"
    )
    add_case_set_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which case sets may be added to this data collection, limited to the case type"
    )
    remove_case_set_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which case sets may be removed from this data collection, limited to the case type"
    )

    def has_any_rights(self) -> bool:
        """
        Determine if at least one of the rights is set.
        """
        return (
            len(self.add_case_from_data_collection_ids) > 0
            or len(self.remove_case_from_data_collection_ids) > 0
            or len(self.add_case_set_from_data_collection_ids) > 0
            or len(self.remove_case_set_from_data_collection_ids) > 0
        )


class CaseAbac(BaseModel):
    is_full_access: bool = Field(
        description="Whether the user has full access, i.e. is not limited by any ABAC policies. If so, the other fields are empty and are to be ignored."
    )
    case_type_access_abacs: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = Field(
        description="The case type data collection ABACs for the user, keyed by case type set ID and then data collection ID"
    )
    case_type_share_abacs: dict[UUID, dict[UUID, CaseTypeShareAbac]] = Field(
        description="The case type share ABACs for the user, keyed by case type set ID and then data collection ID"
    )

    def get_case_rights(
        self,
        case_id: UUID,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights:
        """
        Get the CaseRights for the given case.

        Arguments:
            case_id: The ID of the case.
            case_type_id: The ID of the case type that the case belongs to.
            created_in_data_collection_id: The ID of the data collection where the case was created.
            data_collection_ids: The IDs of the data collections in which the case is currently shared.
        """
        case_rights: CaseRights = (
            self._get_case_or_set_rights(  # type: ignore[assignment]
                case_id,
                False,
                case_type_id,
                created_in_data_collection_id,
                data_collection_ids,
            )
        )
        return case_rights

    def get_case_set_rights(
        self,
        case_set_id: UUID,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseSetRights:
        """
        Get the CaseSetRights for the given case set.

        Arguments:
            case_set_id: The ID of the case set.
            case_type_id: The ID of the case type that the case set belongs to.
            created_in_data_collection_id: The ID of the data collection where the case set was created.
            data_collection_ids: The IDs of the data collections in which the case set is currently shared.
        """
        case_set_rights: CaseSetRights = (
            self._get_case_or_set_rights(  # type: ignore[assignment]
                case_set_id,
                True,
                case_type_id,
                created_in_data_collection_id,
                data_collection_ids,
            )
        )
        return case_set_rights

    def get_combinations_with_any_rights(self) -> dict[UUID, set[UUID]]:
        """
        Get the dict[case_type_id, set[data_collection_ids]] combinations for which
        there is any access or share right. The sets are guaranteed to be non-empty.
        """
        retval: dict[UUID, set[UUID]] = {}
        for (
            case_type_id,
            data_collection_access_abac_map,
        ) in self.case_type_access_abacs.items():
            data_collection_ids = {
                x
                for x, y in data_collection_access_abac_map.items()
                if y.has_any_rights()
            }
            if data_collection_ids:
                retval[case_type_id] = data_collection_ids
        for (
            case_type_id,
            data_collection_share_abac_map,
        ) in self.case_type_share_abacs.items():
            data_collection_ids = {
                x
                for x, y in data_collection_share_abac_map.items()
                if y.has_any_rights()
            }
            if not data_collection_ids:
                continue
            if case_type_id in retval:
                # Merge with existing data collection IDs
                retval[case_type_id].update(data_collection_ids)
            else:
                retval[case_type_id] = data_collection_ids
        return retval

    def get_combinations_with_access_right(
        self,
        right: CaseRight,
    ) -> dict[UUID, set[UUID]]:
        """
        Get the dict[case_type_id, set[data_collection_ids]] combinations for which
        there is the given right. The sets are guaranteed to be non-empty.
        """
        retval = {}
        has_right_fn = self._get_has_right_function(right)
        for case_type_id, data in self.case_type_access_abacs.items():
            data_collection_ids = {x for x, y in data.items() if has_right_fn(y)}
            if data_collection_ids:
                retval[case_type_id] = data_collection_ids
        return retval

    def get_case_types_with_any_rights(self) -> set[UUID]:
        """
        Get the set[case_type_id] for which there is any access or share right in at
        least one of the data collections.
        """
        retval = set()
        for (
            case_type_id,
            data_collection_access_abac_map,
        ) in self.case_type_access_abacs.items():
            has_right = any(
                x.has_any_rights() for x in data_collection_access_abac_map.values()
            )
            if has_right:
                retval.add(case_type_id)
        for (
            case_type_id,
            data_collection_share_abac_map,
        ) in self.case_type_share_abacs.items():
            has_right = any(
                x.has_any_rights() for x in data_collection_share_abac_map.values()
            )
            if has_right:
                retval.add(case_type_id)
        return retval

    def get_case_types_with_access_right(self, right: CaseRight) -> set[UUID]:
        """
        Get the set[case_type_id] for which there is the given right in at least one of
        the data collections.
        """
        retval = set()
        has_right_fn = self._get_has_right_function(right)
        for case_type_id, data in self.case_type_access_abacs.items():
            has_right = any(has_right_fn(x) for x in data.values())
            if has_right:
                retval.add(case_type_id)
        return retval

    def get_case_type_cols_with_any_rights(
        self, case_type_id: UUID | None = None
    ) -> set[UUID]:
        """
        Get the set[case_type_col_id] for which there is any read or write access in at
        least one of the data collections. Optionally limited to the given case type.
        """
        retval: set[UUID] = set()
        if case_type_id is not None:
            if case_type_id not in self.case_type_access_abacs:
                return retval
            data = self.case_type_access_abacs[case_type_id]
            for access_abac in data.values():
                retval.update(access_abac.read_case_type_col_ids)
                retval.update(access_abac.write_case_type_col_ids)
        for case_type_id, data in self.case_type_access_abacs.items():
            for access_abac in data.values():
                retval.update(access_abac.read_case_type_col_ids)
                retval.update(access_abac.write_case_type_col_ids)
        return retval

    def get_case_type_cols_with_access_rights(
        self, right: CaseRight, case_type_id: UUID | None = None
    ) -> set[UUID]:
        """
        Get the set[case_type_col_id] for which there is any read or write access in at
        least one of the data collections. Optionally limited to the given case type.
        """
        retval: set[UUID] = set()
        if case_type_id is not None:
            if case_type_id not in self.case_type_access_abacs:
                return retval
            data = self.case_type_access_abacs[case_type_id]
            retval = self._update_access_rights(right, retval, data)
            return retval
        for case_type_id, data in self.case_type_access_abacs.items():
            retval = self._update_access_rights(right, retval, data)
        return retval

    def get_data_collections_with_any_rights(self) -> set[UUID]:
        """
        Get the set[data_collection_id] for which there is any access or share right.
        """
        data_collection_ids: set[UUID] = set()
        # Check access case rights
        for data_collection_access_abac_map in self.case_type_access_abacs.values():
            for (
                data_collection_id,
                access_abac,
            ) in data_collection_access_abac_map.items():
                if access_abac.has_any_rights():
                    data_collection_ids.add(data_collection_id)
        # Check share case rights
        for data_collection_share_abac_map in self.case_type_share_abacs.values():
            for (
                data_collection_id,
                share_abac,
            ) in data_collection_share_abac_map.items():
                if not share_abac.has_any_rights():
                    continue
                data_collection_ids.add(data_collection_id)
                data_collection_ids.update(share_abac.add_case_from_data_collection_ids)
                data_collection_ids.update(
                    share_abac.remove_case_from_data_collection_ids
                )
                data_collection_ids.update(
                    share_abac.add_case_set_from_data_collection_ids
                )
                data_collection_ids.update(
                    share_abac.remove_case_set_from_data_collection_ids
                )
        return data_collection_ids

    def get_data_collections_with_access_right_for_case_type_col(
        self, case_type_col_id: UUID, right: CaseRight
    ) -> set[UUID]:
        """
        Get the set[data_collection_id] for which there is the given right on the
        given case_type_col.
        """
        if right == CaseRight.READ_CASE:
            return {
                data_collection_id
                for access_by_data_collection in self.case_type_access_abacs.values()
                for data_collection_id, access_abac in access_by_data_collection.items()
                if case_type_col_id in access_abac.read_case_type_col_ids
            }
        elif right == CaseRight.WRITE_CASE:
            return {
                data_collection_id
                for access_by_data_collection in self.case_type_access_abacs.values()
                for data_collection_id, access_abac in access_by_data_collection.items()
                if case_type_col_id in access_abac.write_case_type_col_ids
            }
        else:
            raise exc.InvalidArgumentsError(
                f"Right {right.value} is invalid for case_type_col access"
            )

    def get_removable_data_collections_ids(
        self,
        is_case_set: bool,
        data_collection_ids: set[UUID],
        access: dict[UUID, CaseTypeAccessAbac],
        is_own_private: bool,
    ) -> set[UUID]:
        """
        Get the IDs of the data collections from which the case or case set can be
        removed.
        """
        remove_data_collection_ids: set[UUID] = (
            {
                x
                for x, y in access.items()
                if (y.remove_case_set if is_case_set else y.remove_case)
                and x in data_collection_ids
            }
            if is_own_private
            else set()
        )

        return remove_data_collection_ids

    def get_addable_data_collections_ids(
        self,
        is_case_set: bool,
        data_collection_ids: set[UUID],
        access: dict[UUID, CaseTypeAccessAbac],
        is_own_private: bool,
    ) -> set[UUID]:
        """
        Get the IDs of the data collections to which the case or case set can be
        added.
        """
        add_data_collection_ids: set[UUID] = (
            {
                x
                for x, y in access.items()
                if (y.add_case_set if is_case_set else y.add_case)
                and x not in data_collection_ids
            }
            if is_own_private
            else set()
        )

        return add_data_collection_ids

    def is_allowed(
        self,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        right: CaseRight,
        is_create_or_delete: bool = False,
        current_data_collection_ids: set[UUID] | None = None,
        tgt_data_collection_ids: set[UUID] | None = None,
    ) -> bool:
        """
        Determine if the given right is allowed for the given case type and data
        collections. This covers the following rights:
        - ADD_CASE/SET: create a case or case set and/or add it to all the given data
          collections
        - REMOVE_CASE/SET: delete a case or case set and/or remove it from all the
          given data collections
        - READ/WRITE_CASE/SET: read a case or case set from at least one of the given
          data collections
        """
        # Special case: full access
        if self.is_full_access:
            return True

        current_data_collection_ids = current_data_collection_ids or set()
        tgt_data_collection_ids = tgt_data_collection_ids or set()

        # Get rights for the case type
        access_abac = self.case_type_access_abacs.get(case_type_id, {})
        share_abac = self.case_type_share_abacs.get(case_type_id, {})

        if access_abac is None and share_abac is None:
            return False

        # Handle each right
        if right in CaseRightSet.ADD.value:
            return self._is_add_allowed(
                right,
                access_abac,
                share_abac,
                is_create_or_delete,
                created_in_data_collection_id,
                current_data_collection_ids,
                tgt_data_collection_ids,
            )
        if right in CaseRightSet.REMOVE.value:
            return self._is_remove_allowed(
                right,
                access_abac,
                share_abac,
                is_create_or_delete,
                created_in_data_collection_id,
                current_data_collection_ids,
                tgt_data_collection_ids,
            )
        if right in CaseRightSet.CONTENT.value:
            return self.is_content_allowed(
                right,
                access_abac,
                is_create_or_delete,
                current_data_collection_ids,
                tgt_data_collection_ids,
            )
        raise exc.InvalidArgumentsError(f"Right {right.value} is invalid")

    def is_content_allowed(
        self,
        right: CaseRight,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        is_create_or_delete: bool,
        current_data_collection_ids: set[UUID],
        tgt_data_collection_ids: set[UUID],
    ) -> bool:
        """
        Determine if the case or case set content can be accessed from at least one of
        the current data collections.
        """
        if is_create_or_delete:
            raise exc.InvalidArgumentsError(
                f"is_create_or_delete must be False for right {right.value}"
            )
        if tgt_data_collection_ids:
            raise exc.InvalidArgumentsError(
                f"tgt_data_collection_ids must be empty for right {right.value}"
            )

        has_right_fn = self._get_has_right_function(right)
        for data_collection_id in current_data_collection_ids:
            if data_collection_id in access_abac and has_right_fn(
                access_abac[data_collection_id]
            ):
                # Access right in this data collection
                return True
        return False

    def _update_access_rights(
        self, right: CaseRight, retval: set[UUID], data: dict[UUID, CaseTypeAccessAbac]
    ) -> set[UUID]:
        """Helper to update the set of case type column IDs based on the given right."""
        for access_abac in data.values():
            if right == CaseRight.READ_CASE:
                retval.update(access_abac.read_case_type_col_ids)
            elif right == CaseRight.WRITE_CASE:
                retval.update(access_abac.write_case_type_col_ids)
            else:
                raise exc.InvalidArgumentsError(
                    f"Right {right.value} is invalid for case_type_col access"
                )
        return retval

    def _validate_private_creation_or_deletion(
        self,
        right: CaseRight,
        created_in_data_collection_id: UUID,
        access_abac: dict[UUID, CaseTypeAccessAbac],
    ) -> bool:
        """
        Validate that the creation or deletion in a private data collection is
        allowed.
        """
        if created_in_data_collection_id is None:
            raise exc.InvalidArgumentsError(
                f"created_in_data_collection_id must be provided for right {right.value}"
            )

        if created_in_data_collection_id not in access_abac:
            return False

        if not access_abac[created_in_data_collection_id].is_private:
            return False

        return True

    def _check_access_or_share(
        self,
        right: CaseRight,
        data_collection_id: UUID,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        share_abac: dict[UUID, CaseTypeShareAbac],
        current_data_collection_ids: set[UUID],
    ) -> bool:
        """
        Check if there is either access or share right for the given data collection.
        """
        has_right_fn = self._get_has_right_function(right)
        get_share_from_data_collections_fn = (
            self._get_get_share_from_data_collections_function(right)
        )
        if data_collection_id not in access_abac:
            # No access to this data collection
            return False
        if access_abac[data_collection_id].is_private:
            # Private data collection different from the created in data collection
            return False
        if not has_right_fn(access_abac[data_collection_id]):
            # No access right in this data collection -> check share rights
            if (
                share_abac is None
                or data_collection_id not in share_abac
                or not current_data_collection_ids.intersection(
                    get_share_from_data_collections_fn(share_abac[data_collection_id])
                )
            ):
                # No direct share rights either
                # TODO: Check indirect share rights from the provided data collections
                return False
        return True

    def _is_add_allowed(
        self,
        right: CaseRight,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        share_abac: dict[UUID, CaseTypeShareAbac],
        is_create_or_delete: bool,
        created_in_data_collection_id: UUID,
        current_data_collection_ids: set[UUID],
        tgt_data_collection_ids: set[UUID],
    ) -> bool:
        """
        Determine if the case or case set can be added to all the target data collections
        """
        # Check if the case or case set can be added to all the target data collections
        if is_create_or_delete:
            if not self._validate_private_creation_or_deletion(
                right, created_in_data_collection_id, access_abac
            ):
                return False
            if current_data_collection_ids:
                raise exc.InvalidArgumentsError(
                    f"current_data_collection_ids must be empty for right {right.value} if is_create_or_delete=True"
                )
        remaining_data_collection_ids = (
            set() if tgt_data_collection_ids is None else set(tgt_data_collection_ids)
        )
        remaining_data_collection_ids.discard(created_in_data_collection_id)
        if current_data_collection_ids:
            remaining_data_collection_ids = (
                remaining_data_collection_ids - current_data_collection_ids
            )
        current_data_collection_ids.add(created_in_data_collection_id)

        for data_collection_id in remaining_data_collection_ids:
            if not self._check_access_or_share(
                right,
                data_collection_id,
                access_abac,
                share_abac,
                current_data_collection_ids,
            ):
                return False
        return True

    def _is_remove_allowed(
        self,
        right: CaseRight,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        share_abac: dict[UUID, CaseTypeShareAbac],
        is_create_or_delete: bool,
        created_in_data_collection_id: UUID,
        current_data_collection_ids: set[UUID],
        tgt_data_collection_ids: set[UUID],
    ) -> bool:
        # Check if the case or case set can be deleted from all the target data collections
        if is_create_or_delete:
            if not self._validate_private_creation_or_deletion(
                right, created_in_data_collection_id, access_abac
            ):
                return False
            if tgt_data_collection_ids:
                raise exc.InvalidArgumentsError(
                    f"tgt_data_collection_ids must be empty for right {right.value} if is_create_or_delete=True"
                )
            tgt_data_collection_ids = current_data_collection_ids
        if not tgt_data_collection_ids.issubset(current_data_collection_ids):
            raise exc.InvalidArgumentsError(
                f"tgt_data_collection_ids must be a subset of current_data_collection_ids for right {right.value}"
            )
        # Check for each of the remaining target data collections if the user has
        # the right to remove cases or case sets from it
        remaining_data_collection_ids = set(tgt_data_collection_ids)
        remaining_data_collection_ids.discard(created_in_data_collection_id)
        for data_collection_id in remaining_data_collection_ids:
            if not self._check_access_or_share(
                right,
                data_collection_id,
                access_abac,
                share_abac,
                current_data_collection_ids,
            ):
                return False
        return True

    def _get_case_or_set_rights_with_full_access(
        self,
        case_or_set_id: UUID,
        is_case_set: bool,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights | CaseSetRights:
        """
        Create a CaseRights or CaseSetRights object for the case/case set for a user
        with full access.
        """
        shared_in_data_collection_ids: set[UUID] = data_collection_ids - {
            created_in_data_collection_id
        }
        if is_case_set:
            return CaseSetRights(
                case_set_id=case_or_set_id,
                case_type_id=case_type_id,
                created_in_data_collection_id=created_in_data_collection_id,
                data_collection_ids=data_collection_ids,
                is_full_access=True,
                add_data_collection_ids=set(),
                remove_data_collection_ids=set(),
                read_case_set=True,
                write_case_set=True,
                can_delete=True,
                shared_in_data_collection_ids=shared_in_data_collection_ids,
            )
        return CaseRights(
            case_id=case_or_set_id,
            case_type_id=case_type_id,
            created_in_data_collection_id=created_in_data_collection_id,
            data_collection_ids=data_collection_ids,
            is_full_access=True,
            add_data_collection_ids=set(),
            remove_data_collection_ids=set(),
            read_case_type_col_ids=set(),
            write_case_type_col_ids=set(),
            can_delete=True,
            shared_in_data_collection_ids=shared_in_data_collection_ids,
        )

    def _get_case_or_set_rights_without_full_access(
        self,
        case_or_set_id: UUID,
        is_case_set: bool,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights | CaseSetRights:
        """
        Create a CaseRights or CaseSetRights object for the case/case set for a user
        under ABAC.
        """
        shared_in_data_collection_ids = data_collection_ids - {
            created_in_data_collection_id
        }
        # Determine case access: if the case/set created_in_data_collection_id is a
        # private data collection, the user is allowed add to/remove from the
        # listed data collections
        access: dict[UUID, CaseTypeAccessAbac] = self.case_type_access_abacs.get(
            case_type_id, {}
        )
        is_own_private = any(
            x.data_collection_id == created_in_data_collection_id and x.is_private
            for x in self.case_type_access_abacs.get(case_type_id, {}).values()
        )
        add_data_collection_ids = self.get_addable_data_collections_ids(
            is_case_set, data_collection_ids, access, is_own_private
        )
        remove_data_collection_ids = self.get_removable_data_collections_ids(
            is_case_set, data_collection_ids, access, is_own_private
        )

        # Determine case sharing: if the current data_collections that the case/set
        # is in match the from_data_collection_ids of a share right, the case/set can be
        # shared to and/or deleted from the to_data_collection_id
        share: dict[UUID, CaseTypeShareAbac] = self.case_type_share_abacs.get(
            case_type_id, {}
        )
        self._update_data_collections_with_share_rights(
            share,
            is_case_set,
            data_collection_ids,
            add_data_collection_ids,
            remove_data_collection_ids,
        )

        can_delete = set(data_collection_ids).issubset(set(remove_data_collection_ids))

        if is_case_set:
            # Read/write rights
            read_case_set = any(x.read_case_set for x in access.values())
            write_case_set = any(x.write_case_set for x in access.values())
            return CaseSetRights(
                case_set_id=case_or_set_id,
                case_type_id=case_type_id,
                created_in_data_collection_id=created_in_data_collection_id,
                data_collection_ids=data_collection_ids,
                is_full_access=self.is_full_access,
                add_data_collection_ids=add_data_collection_ids,
                remove_data_collection_ids=remove_data_collection_ids,
                read_case_set=read_case_set,
                write_case_set=write_case_set,
                can_delete=can_delete,
                shared_in_data_collection_ids=shared_in_data_collection_ids,
            )
        # Case type cols that can be read/written
        read_case_type_col_ids: set[UUID] = {
            col_id for x in access.values() for col_id in x.read_case_type_col_ids
        }
        write_case_type_col_ids: set[UUID] = {
            col_id for x in access.values() for col_id in x.write_case_type_col_ids
        }
        return CaseRights(
            case_id=case_or_set_id,
            case_type_id=case_type_id,
            created_in_data_collection_id=created_in_data_collection_id,
            data_collection_ids=data_collection_ids,
            is_full_access=self.is_full_access,
            add_data_collection_ids=add_data_collection_ids,
            remove_data_collection_ids=remove_data_collection_ids,
            read_case_type_col_ids=read_case_type_col_ids,
            write_case_type_col_ids=write_case_type_col_ids,
            can_delete=can_delete,
            shared_in_data_collection_ids=shared_in_data_collection_ids,
        )

    def _update_data_collections_with_share_rights(
        self,
        share: dict[UUID, CaseTypeShareAbac],
        is_case_set: bool,
        data_collection_ids: set[UUID],
        add_data_collection_ids: set[UUID],
        remove_data_collection_ids: set[UUID],
    ) -> None:
        """
        Update the add_data_collection_ids and remove_data_collection_ids based on
        the share rights. When a share right exists from a data collection in
        data_collection_ids to another data collection, the latter is added to
        add_data_collection_ids. Analogous for remove_data_collection_ids.
        """
        for to_data_collection_id, case_type_share_abac in share.items():
            # Update add_data_collection_ids
            add_from_data_collection_ids = (
                case_type_share_abac.add_case_set_from_data_collection_ids
                if is_case_set
                else case_type_share_abac.add_case_from_data_collection_ids
            )
            if (
                to_data_collection_id not in data_collection_ids
                and add_from_data_collection_ids.intersection(data_collection_ids)
            ):
                add_data_collection_ids.add(to_data_collection_id)
            # Update remove_data_collection_ids
            remove_from_data_collection_ids = (
                case_type_share_abac.remove_case_set_from_data_collection_ids
                if is_case_set
                else case_type_share_abac.remove_case_from_data_collection_ids
            )
            if (
                to_data_collection_id in data_collection_ids
                and remove_from_data_collection_ids.intersection(data_collection_ids)
            ):
                remove_data_collection_ids.add(to_data_collection_id)

    def _get_case_or_set_rights(
        self,
        case_or_set_id: UUID,
        is_case_set: bool,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights | CaseSetRights:
        """
        Create a CaseRights or CaseSetRights object for the case/case set with the
        given ID.

        Arguments:
            case_or_set_id: The ID of the case or case set.
            is_case_set: Whether the ID is for a case set.
            case_type_id: The ID of the case type that the case or case set belongs to.
            created_in_data_collection_id: The ID of the data collection where the case or case set was created.
            data_collection_ids: The IDs of the data collections in which the case or case set is currently shared.
        """
        # Parse input
        if self.is_full_access:
            return self._get_case_or_set_rights_with_full_access(
                case_or_set_id,
                is_case_set,
                case_type_id,
                created_in_data_collection_id,
                data_collection_ids,
            )

        return self._get_case_or_set_rights_without_full_access(
            case_or_set_id,
            is_case_set,
            case_type_id,
            created_in_data_collection_id,
            data_collection_ids,
        )

    @staticmethod
    def _get_has_right_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeAccessAbac | CaseTypeShareAbac], bool]:
        """
        Get a function that checks if the given right is present in a
        CaseTypeAccessAbac or CaseTypeShareAbac.
        """
        if right == CaseRight.ADD_CASE:
            has_right_fn = lambda x: x.add_case
        elif right == CaseRight.REMOVE_CASE:
            has_right_fn = lambda x: x.remove_case
        elif right == CaseRight.READ_CASE:
            has_right_fn = lambda x: len(x.read_case_type_col_ids) > 0
        elif right == CaseRight.WRITE_CASE:
            has_right_fn = lambda x: len(x.write_case_type_col_ids) > 0
        elif right == CaseRight.ADD_CASE_SET:
            has_right_fn = lambda x: x.add_case_set
        elif right == CaseRight.REMOVE_CASE_SET:
            has_right_fn = lambda x: x.remove_case_set
        elif right == CaseRight.READ_CASE_SET:
            has_right_fn = lambda x: x.read_case_set
        elif right == CaseRight.WRITE_CASE_SET:
            has_right_fn = lambda x: x.write_case_set
        else:
            raise NotImplementedError(f"Right {right.value} not implemented")
        return has_right_fn

    @staticmethod
    def _get_get_share_from_data_collections_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeShareAbac], set[UUID]]:
        """
        Get a function that retrieves the from_data_collection_ids for the given
        right from a CaseTypeShareAbac.
        """
        if right == CaseRight.ADD_CASE:
            get_share_from_data_collections_fn = (
                lambda x: x.add_case_from_data_collection_ids
            )
        elif right == CaseRight.REMOVE_CASE:
            get_share_from_data_collections_fn = (
                lambda x: x.remove_case_from_data_collection_ids
            )
        elif right == CaseRight.ADD_CASE_SET:
            get_share_from_data_collections_fn = (
                lambda x: x.add_case_set_from_data_collection_ids
            )
        elif right == CaseRight.REMOVE_CASE_SET:
            get_share_from_data_collections_fn = (
                lambda x: x.remove_case_set_from_data_collection_ids
            )
        else:
            raise NotImplementedError(f"Right {right.value} not implemented")
        return get_share_from_data_collections_fn

    @staticmethod
    def _get_from_data_collections_for_right_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeShareAbac], set[UUID]]:
        """
        Get a function that retrieves the from_data_collection_ids for the given
        right from a CaseTypeShareAbac.
        """
        if right == CaseRight.ADD_CASE:
            get_from_data_collections_fn = lambda x: x.add_case_from_data_collection_ids
        elif right == CaseRight.REMOVE_CASE:
            get_from_data_collections_fn = (
                lambda x: x.remove_case_from_data_collection_ids
            )
        elif right == CaseRight.ADD_CASE_SET:
            get_from_data_collections_fn = (
                lambda x: x.add_case_set_from_data_collection_ids
            )
        elif right == CaseRight.REMOVE_CASE_SET:
            get_from_data_collections_fn = (
                lambda x: x.remove_case_set_from_data_collection_ids
            )
        else:
            raise NotImplementedError(f"Right {right.value} not implemented")
        return get_from_data_collections_fn
