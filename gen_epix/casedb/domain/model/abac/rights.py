"""Compute effective case and case-set rights from resolved ABAC records.

Access records grant rights within collections where an item is present. Share
records grant add or remove rights on a target collection when the item is present
in at least one configured source collection.
"""

from collections.abc import Callable
from uuid import UUID

from pydantic import BaseModel, Field

from gen_epix.casedb.domain.enum import CaseRight, CaseRightSet
from gen_epix.casedb.domain.model.case.non_persistable import CaseRights, CaseSetRights
from gen_epix.fastapp import exc


class CaseTypeAccessAbac(BaseModel):
    """Represents effective access rights for one case type and data collection."""

    case_type_id: UUID = Field(description="The ID of the CaseType")
    data_collection_id: UUID = Field(description="The ID of the data collection")
    is_private: bool = Field(
        description="Whether the data collection is private, limited to the CaseTypes in the CaseTypeSet. When true, add/remove case and add/remove case set are considered (i) as the right to create/delete a case or case set in this data collection (setting case.created_in_data_collection to this data collection) and (ii) as the right to share the case or case set further in other data collections. Deleting a case or case set is only allowed when it can or has been removed from all other data collections as well."
    )
    add_case: bool = Field(
        description="Whether cases may be added, limited to the CaseType and data collection"
    )
    remove_case: bool = Field(
        description="Whether cases may be removed, limited to the CaseType and data collection"
    )
    add_case_set: bool = Field(
        description="Whether case sets may be added, limited to the CaseType and data collection"
    )
    remove_case_set: bool = Field(
        description="Whether case sets may be removed, limited to the CaseType and data collection"
    )
    read_col_ids: set[UUID] = Field(
        description="The IDs of the columns for which values can be read, limited to the CaseType and data collection"
    )
    write_col_ids: set[UUID] = Field(
        description="The IDs of the columns for which values can be updated, limited to the CaseTypes in the CaseTypeSet"
    )
    read_case_set: bool = Field(
        description="Whether case set be read, limited to the CaseType and data collection"
    )
    write_case_set: bool = Field(
        description="Whether case set be updated, limited to the CaseType and data collection"
    )

    def has_any_rights(self) -> bool:
        """Return whether at least one access right is granted."""
        return (
            self.add_case
            or self.remove_case
            or self.add_case_set
            or self.remove_case_set
            or len(self.read_col_ids) > 0
            or len(self.write_col_ids) > 0
            or self.read_case_set
            or self.write_case_set
        )


class CaseTypeShareAbac(BaseModel):
    """Represents source-dependent share rights into one target collection."""

    case_type_id: UUID = Field(description="The ID of the CaseType")
    data_collection_id: UUID = Field(description="The ID of the data collection")
    add_case_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which cases may be added to this data collection, limited to the CaseType"
    )
    remove_case_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which cases may be removed from this data collection, limited to the CaseType"
    )
    add_case_set_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which case sets may be added to this data collection, limited to the CaseType"
    )
    remove_case_set_from_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which case sets may be removed from this data collection, limited to the CaseType"
    )

    def has_any_rights(self) -> bool:
        """Return whether at least one source collection grants a share right."""
        return (
            len(self.add_case_from_data_collection_ids) > 0
            or len(self.remove_case_from_data_collection_ids) > 0
            or len(self.add_case_set_from_data_collection_ids) > 0
            or len(self.remove_case_set_from_data_collection_ids) > 0
        )


class CaseAbac(BaseModel):
    """Represents a user's effective case ABAC rights grouped by case type."""

    is_full_access: bool = Field(
        description="Whether the user has full access, i.e. is not limited by any ABAC policies. If so, the other fields are empty and are to be ignored."
    )
    case_type_access_abacs: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = Field(
        description="The CaseTypeAccessAbac objects for the user, keyed by CaseTypeSet ID and then data collection ID"
    )
    case_type_share_abacs: dict[UUID, dict[UUID, CaseTypeShareAbac]] = Field(
        description="The CaseTypeShareAbac objects for the user, keyed by CaseTypeSet ID and then data collection ID"
    )

    def get_case_rights(
        self,
        case_id: UUID,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: set[UUID],
    ) -> CaseRights:
        """Return effective rights for a case in its current collections.

        Args:
            case_id: The ID of the case.
            case_type_id: The ID of the CaseType that the case belongs to.
            created_in_data_collection_id: The collection where the case was
                created.
            data_collection_ids: Collections containing the case, including its
                creation collection.

        Returns:
            Rights aggregated from applicable access and source-to-target share
            records.
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
        """Return effective rights for a case set in its current collections.

        Args:
            case_set_id: The ID of the case set.
            case_type_id: The ID of the CaseType that the case set belongs to.
            created_in_data_collection_id: The collection where the case set was
                created.
            data_collection_ids: Collections containing the case set, including its
                creation collection.

        Returns:
            Rights aggregated from applicable access and source-to-target share
            records.
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
        """Return case-type and target-collection pairs with any effective right.

        The returned collection sets are non-empty and include targets with an
        access or source-dependent share right.
        """
        case_type_data_collections_map: dict[UUID, set[UUID]] = {}
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
                case_type_data_collections_map[case_type_id] = data_collection_ids
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
            if case_type_id in case_type_data_collections_map:
                # Merge with existing data collection IDs
                case_type_data_collections_map[case_type_id].update(data_collection_ids)
            else:
                case_type_data_collections_map[case_type_id] = data_collection_ids
        return case_type_data_collections_map

    def get_combinations_with_access_right(
        self,
        right: CaseRight,
    ) -> dict[UUID, set[UUID]]:
        """Return case-type and collection pairs granting an access right.

        The returned collection sets are non-empty. Share rights are not considered.
        """
        retval = {}
        has_right_fn = self._get_has_right_function(right)
        for case_type_id, data in self.case_type_access_abacs.items():
            data_collection_ids = {x for x, y in data.items() if has_right_fn(y)}
            if data_collection_ids:
                retval[case_type_id] = data_collection_ids
        return retval

    def get_case_types_with_any_rights(self) -> set[UUID]:
        """Return case types with any access or share right in any collection."""
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
        """Return case types granting an access right in at least one collection."""
        retval = set()
        has_right_fn = self._get_has_right_function(right)
        for case_type_id, data in self.case_type_access_abacs.items():
            has_right = any(has_right_fn(x) for x in data.values())
            if has_right:
                retval.add(case_type_id)
        return retval

    def get_cols_with_any_rights(self, case_type_id: UUID | None = None) -> set[UUID]:
        """Return columns with read or write access in any collection.

        Results can be limited to one case type. Share rights do not grant column
        access and are not considered.
        """
        col_ids: set[UUID] = set()
        if case_type_id is not None:
            if case_type_id not in self.case_type_access_abacs:
                return col_ids
            data = self.case_type_access_abacs[case_type_id]
            for access_abac in data.values():
                col_ids.update(access_abac.read_col_ids)
                col_ids.update(access_abac.write_col_ids)
            return col_ids
        for ct_id, data in self.case_type_access_abacs.items():
            for access_abac in data.values():
                col_ids.update(access_abac.read_col_ids)
                col_ids.update(access_abac.write_col_ids)
        return col_ids

    def get_cols_with_access_rights(
        self, right: CaseRight, case_type_id: UUID | None = None
    ) -> set[UUID]:
        """Return columns granting the requested read or write access right.

        Results can be limited to one case type and are unioned across its access
        collections.
        """
        col_ids: set[UUID] = set()
        if case_type_id is not None:
            if case_type_id not in self.case_type_access_abacs:
                return col_ids
            data = self.case_type_access_abacs[case_type_id]
            col_ids = self._update_access_rights(right, col_ids, data)
            return col_ids
        for case_type_id, data in self.case_type_access_abacs.items():
            col_ids = self._update_access_rights(right, col_ids, data)
        return col_ids

    def get_data_collections_with_any_rights(self) -> set[UUID]:
        """Return all collections participating in any access or share right.

        For share rights, both target collections and configured source collections
        are returned.
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

    def get_data_collections_with_access_right_for_col(
        self, col_id: UUID, right: CaseRight
    ) -> set[UUID]:
        """Return collections granting a read or write right on a column.

        Args:
            col_id: Column whose access collections are requested.
            right: ``READ_CASE`` or ``WRITE_CASE``.

        Returns:
            Data collection IDs granting the requested column right across all case
            types.

        Raises:
            InvalidArgumentsError: If ``right`` is not a case read or write right.
        """
        if right == CaseRight.READ_CASE:
            return {
                data_collection_id
                for access_by_data_collection in self.case_type_access_abacs.values()
                for data_collection_id, access_abac in access_by_data_collection.items()
                if col_id in access_abac.read_col_ids
            }
        elif right == CaseRight.WRITE_CASE:
            return {
                data_collection_id
                for access_by_data_collection in self.case_type_access_abacs.values()
                for data_collection_id, access_abac in access_by_data_collection.items()
                if col_id in access_abac.write_col_ids
            }
        else:
            raise exc.InvalidArgumentsError(
                "a9f6e99f", f"Right {right.value} is invalid for Col access"
            )

    def get_removable_data_collections_ids(
        self,
        is_case_set: bool,
        data_collection_ids: set[UUID],
        access: dict[UUID, CaseTypeAccessAbac],
        is_own_private: bool,
    ) -> set[UUID]:
        """Return current collections removable through private-owner access.

        Direct access contributes removal rights only when the item was created in a
        private collection controlled by the user. Share rights are added separately.
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
        """Return absent collections addable through private-owner access.

        Direct access contributes add rights only when the item was created in a
        private collection controlled by the user. Share rights are added separately.
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
        """Return whether a right is allowed for the requested collection change.

        Add and remove operations must be allowed for every applicable target.
        Content access succeeds when at least one current collection grants it. A
        create or delete additionally requires access to the private creation
        collection. Full access bypasses these checks.

        Args:
            case_type_id: Case type to which the item belongs.
            created_in_data_collection_id: Collection where the item was created.
            right: Case or case-set operation to authorize.
            is_create_or_delete: Whether the operation creates or deletes the item,
            rather than only changing sharing or accessing content.
            current_data_collection_ids: Collections currently containing the item.
            tgt_data_collection_ids: Collections to add to or remove from.

        Returns:
            Whether the requested operation is authorized.

        Raises:
            InvalidArgumentsError: If the right is unsupported or its collection
            arguments are inconsistent with the requested operation.
            NotImplementedError: If a recognized right has no access/share mapping.
        """
        # Special case: full access
        if self.is_full_access:
            return True

        current_data_collection_ids = current_data_collection_ids or set()
        tgt_data_collection_ids = tgt_data_collection_ids or set()

        # Get rights for the CaseType
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
        raise exc.InvalidArgumentsError("c5677e5d", f"Right {right.value} is invalid")

    def is_content_allowed(
        self,
        right: CaseRight,
        access_abac: dict[UUID, CaseTypeAccessAbac],
        is_create_or_delete: bool,
        current_data_collection_ids: set[UUID],
        tgt_data_collection_ids: set[UUID],
    ) -> bool:
        """Return whether any current collection grants the content right.

        Args:
            right: Read or write right to test.
            access_abac: Effective access records keyed by collection ID.
            is_create_or_delete: Must be ``False`` for content access.
            current_data_collection_ids: Collections currently containing the item.
            tgt_data_collection_ids: Must be empty for content access.

        Returns:
            Whether at least one current collection grants the right.

        Raises:
            InvalidArgumentsError: If content access is combined with create/delete
                mode or target collections.
            NotImplementedError: If ``right`` has no access mapping.
        """
        if is_create_or_delete:
            raise exc.InvalidArgumentsError(
                "0b4675c7", f"is_create_or_delete must be False for right {right.value}"
            )
        if tgt_data_collection_ids:
            raise exc.InvalidArgumentsError(
                "19f50bc8",
                f"tgt_data_collection_ids must be empty for right {right.value}",
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
        """Add columns granting the requested access right to a set in place.

        Args:
            right: ``READ_CASE`` or ``WRITE_CASE``.
            retval: Set to mutate with matching column IDs.
            data: Access records to aggregate.

        Returns:
            The same mutated ``retval`` set.

        Raises:
            InvalidArgumentsError: If ``right`` is not a case read or write right.
        """
        for access_abac in data.values():
            if right == CaseRight.READ_CASE:
                retval.update(access_abac.read_col_ids)
            elif right == CaseRight.WRITE_CASE:
                retval.update(access_abac.write_col_ids)
            else:
                raise exc.InvalidArgumentsError(
                    "96a14ce1", f"Right {right.value} is invalid for Col access"
                )
        return retval

    def _validate_private_creation_or_deletion(
        self,
        right: CaseRight,
        created_in_data_collection_id: UUID,
        access_abac: dict[UUID, CaseTypeAccessAbac],
    ) -> bool:
        """Return whether creation or deletion uses an accessible private collection.

        Args:
            right: Create or delete right being evaluated.
            created_in_data_collection_id: Collection where the item is created.
            access_abac: Effective access records keyed by collection ID.

        Returns:
            ``True`` for an accessible private creation collection; ``False`` when
            access is absent or the collection is not private.

        Raises:
            InvalidArgumentsError: If the creation collection is not provided.
        """
        if created_in_data_collection_id is None:
            raise exc.InvalidArgumentsError(
                "04dbd654",
                f"created_in_data_collection_id must be provided for right {right.value}",
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
        """Return whether a target grants direct access or source-based sharing."""
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
        """Return whether an item can be added to every applicable target.

        The creation collection and collections already containing the item are
        excluded from target checks. Source matching uses a local set augmented with
        the creation collection and does not mutate caller-owned sets.

        Args:
            right: Case or case-set add right to evaluate.
            access_abac: Effective access records keyed by target collection ID.
            share_abac: Effective share records keyed by target collection ID.
            is_create_or_delete: Whether this add creates the item.
            created_in_data_collection_id: Collection where the item is created.
            current_data_collection_ids: Collections currently containing the item.
            tgt_data_collection_ids: Requested target collections.

        Returns:
            Whether every applicable target grants direct access or a share right
            from a current source collection.

        Raises:
            InvalidArgumentsError: If creation has no creation collection or is
                supplied with current collections.
            NotImplementedError: If ``right`` has no access or share mapping.
        """
        # Check if the case or case set can be added to all the target data collections
        if is_create_or_delete:
            if not self._validate_private_creation_or_deletion(
                right, created_in_data_collection_id, access_abac
            ):
                return False
            if current_data_collection_ids:
                raise exc.InvalidArgumentsError(
                    "72f9de30",
                    f"current_data_collection_ids must be empty for right {right.value} if is_create_or_delete=True",
                )
        remaining_data_collection_ids = (
            set() if tgt_data_collection_ids is None else set(tgt_data_collection_ids)
        )
        remaining_data_collection_ids.discard(created_in_data_collection_id)
        if current_data_collection_ids:
            remaining_data_collection_ids = (
                remaining_data_collection_ids - current_data_collection_ids
            )
        # Use a local copy to avoid mutating the caller's set
        effective_current = set(current_data_collection_ids)
        effective_current.add(created_in_data_collection_id)

        for data_collection_id in remaining_data_collection_ids:
            if not self._check_access_or_share(
                right,
                data_collection_id,
                access_abac,
                share_abac,
                effective_current,
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
        """Return whether an item can be removed from every applicable target.

        Deletion evaluates every current collection as a target after validating the
        private creation collection. The creation collection itself is excluded from
        share checks.

        Args:
            right: Case or case-set remove right to evaluate.
            access_abac: Effective access records keyed by target collection ID.
            share_abac: Effective share records keyed by target collection ID.
            is_create_or_delete: Whether this remove deletes the item.
            created_in_data_collection_id: Collection where the item was created.
            current_data_collection_ids: Collections currently containing the item.
            tgt_data_collection_ids: Requested collections to remove from.

        Returns:
            Whether every applicable target grants direct access or a share right
            from a current source collection.

        Raises:
            InvalidArgumentsError: If deletion has no creation collection, includes
                explicit targets, or a target is not a current collection.
            NotImplementedError: If ``right`` has no access or share mapping.
        """
        # Check if the case or case set can be deleted from all the target data collections
        if is_create_or_delete:
            if not self._validate_private_creation_or_deletion(
                right, created_in_data_collection_id, access_abac
            ):
                return False
            if tgt_data_collection_ids:
                raise exc.InvalidArgumentsError(
                    "25eccb30",
                    f"tgt_data_collection_ids must be empty for right {right.value} if is_create_or_delete=True",
                )
            tgt_data_collection_ids = current_data_collection_ids
        if not tgt_data_collection_ids.issubset(current_data_collection_ids):
            raise exc.InvalidArgumentsError(
                "cec81d55",
                f"tgt_data_collection_ids must be a subset of current_data_collection_ids for right {right.value}",
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
        """Create case or case-set rights for a user with full access.

        Full access grants deletion and all content rights; empty column and sharing
        sets act as unrestricted sentinels rather than denials.
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
            read_col_ids=set(),
            write_col_ids=set(),
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
        """Create case or case-set rights from effective ABAC records.

        Read and write rights are unioned only across collections containing the
        item. Add and remove rights combine private-owner access with source-matched
        share records, and deletion requires removal from every current collection.
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
            # Read/write rights - only in data collections where the case set
            # is actually present
            read_case_set = any(
                x.read_case_set
                for dc_id, x in access.items()
                if dc_id in data_collection_ids
            )
            write_case_set = any(
                x.write_case_set
                for dc_id, x in access.items()
                if dc_id in data_collection_ids
            )
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
        # Cols that can be read/written - only in data collections where the case
        # is actually present
        read_col_ids: set[UUID] = {
            col_id
            for dc_id, x in access.items()
            if dc_id in data_collection_ids
            for col_id in x.read_col_ids
        }
        write_col_ids: set[UUID] = {
            col_id
            for dc_id, x in access.items()
            if dc_id in data_collection_ids
            for col_id in x.write_col_ids
        }
        return CaseRights(
            case_id=case_or_set_id,
            case_type_id=case_type_id,
            created_in_data_collection_id=created_in_data_collection_id,
            data_collection_ids=data_collection_ids,
            is_full_access=self.is_full_access,
            add_data_collection_ids=add_data_collection_ids,
            remove_data_collection_ids=remove_data_collection_ids,
            read_col_ids=read_col_ids,
            write_col_ids=write_col_ids,
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
        """Update addable and removable collection sets in place from share rights.

        A target is addable when absent and at least one configured add source is
        current. It is removable when present and at least one configured remove
        source is current. Both result sets are mutated; inputs are not removed.
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
        """Create effective rights for a case or case set.

        Args:
            case_or_set_id: The ID of the case or case set.
            is_case_set: Whether the ID is for a case set.
            case_type_id: The ID of the CaseType that the case or case set belongs to.
            created_in_data_collection_id: The collection where the item was created.
            data_collection_ids: Collections currently containing the item.

        Returns:
            Full-access or ABAC-limited rights for the requested item kind.
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
        """Return a predicate for an access right.

        Args:
            right: Right whose access attribute should be tested.

        Returns:
            Predicate accepting an effective ABAC record.

        Raises:
            NotImplementedError: If ``right`` has no access mapping.
        """
        if right == CaseRight.ADD_CASE:
            has_right_fn = lambda x: x.add_case
        elif right == CaseRight.REMOVE_CASE:
            has_right_fn = lambda x: x.remove_case
        elif right == CaseRight.READ_CASE:
            has_right_fn = lambda x: len(x.read_col_ids) > 0
        elif right == CaseRight.WRITE_CASE:
            has_right_fn = lambda x: len(x.write_col_ids) > 0
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
        """Return an accessor for source collections granting a share right.

        Args:
            right: Add or remove right whose source collections are requested.

        Returns:
            Accessor accepting a share record and returning its source IDs.

        Raises:
            NotImplementedError: If ``right`` has no share-source mapping.
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
        """Return an accessor for source collections granting a share right.

        Args:
            right: Add or remove right whose source collections are requested.

        Returns:
            Accessor accepting a share record and returning its source IDs.

        Raises:
            NotImplementedError: If ``right`` has no share-source mapping.
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
