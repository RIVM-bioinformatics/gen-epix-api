from typing import Callable
from uuid import UUID

from pydantic import BaseModel, Field

from gen_epix.casedb.domain.enum import CaseRight, CaseRightSet
from gen_epix.casedb.domain.model.case.case import CaseRights, CaseSetRights
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

    def get_combinations_with_any_rights(self) -> dict[UUID, set[UUID]]:
        """
        Get the dict[case_type_id, set[data_collection_ids]] combinations for which
        there is any access or share right. The sets are guaranteed to be non-empty.
        """
        retval: dict[UUID, set[UUID]] = {}
        for case_type_id, data in self.case_type_access_abacs.items():
            data_collection_ids = {x for x, y in data.items() if y.has_any_rights()}
            if data_collection_ids:
                retval[case_type_id] = data_collection_ids
        for case_type_id, data in self.case_type_share_abacs.items():
            data_collection_ids = {x for x, y in data.items() if y.has_any_rights()}
            if not data_collection_ids:
                continue
            if case_type_id in retval:
                # Merge with existing data collection IDs
                data_collection_ids = retval[case_type_id].union(data_collection_ids)
            else:
                retval[case_type_id] = data_collection_ids
        return retval

    def get_case_types_with_any_rights(self) -> set[UUID]:
        """
        Get the set[case_type_id] for which there is any access or share right in at
        least one of the data collections.
        """
        retval = set()
        for case_type_id, data in self.case_type_access_abacs.items():
            has_right = any(x.has_any_rights() for x in data.values())
            if has_right:
                retval.add(case_type_id)
        for case_type_id, data in self.case_type_share_abacs.items():
            has_right = any(x.has_any_rights() for x in data.values())
            if has_right:
                retval.add(case_type_id)
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
        has_right_function = self._get_has_right_function(right)
        for case_type_id, data in self.case_type_access_abacs.items():
            data_collection_ids = {x for x, y in data.items() if has_right_function(y)}
            if data_collection_ids:
                retval[case_type_id] = data_collection_ids
        return retval

    def get_case_types_with_access_right(self, right: CaseRight) -> set[UUID]:
        """
        Get the set[case_type_id] for which there is the given right in at least one of
        the data collections.
        """
        retval = set()
        has_right_function = self._get_has_right_function(right)
        for case_type_id, data in self.case_type_access_abacs.items():
            has_right = any(has_right_function(x) for x in data.values())
            if has_right:
                retval.add(case_type_id)
        return retval

    def get_case_type_cols_with_any_rights(self) -> set[UUID]:
        """
        Get the set[case_type_col_id] for which there is any read or write access in at
        least one of the data collections.
        """
        retval = set()
        for case_type_id, data in self.case_type_access_abacs.items():
            for data_collection_id, access_abac in data.items():
                retval.update(access_abac.read_case_type_col_ids)
                retval.update(access_abac.write_case_type_col_ids)
        return retval

    def get_data_collections_with_any_rights(self) -> set[UUID]:
        data_collection_ids = set()
        for data in self.case_type_access_abacs.values():
            for data_collection_id, access_abac in data.items():
                if access_abac.has_any_rights():
                    data_collection_ids.add(data_collection_id)
        for data in self.case_type_share_abacs.values():
            for data_collection_id, share_abac in data.items():
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

    # def is_share_allowed(
    #     self,
    #     case_type_id: UUID,
    #     right: enum.CaseAbacRight,
    #     data_collection_ids: set[UUID],
    #     require_private: bool = False,
    #     from_data_collection_ids: set[UUID] | None = None,
    # ) -> bool:
    #     """
    #     Determine if the user has the right to add or remove cases or case sets in the
    #     given data collections.

    #     If require_private is True, exactly one of the data collections must be
    #     private: this represents the situation where the case or case set is created or
    #     deleted, while at same time being added or removed from to/from all the other
    #     data collections.

    #     Alternatively, if require_private is False, a set of from_data_collection_ids
    #     may be provided that the case or case set already is in, and for which there
    #     may be additional share rights.
    #     """
    #     # Parse input
    #     if right not in enum.CaseAbacRightSet.SHARE.value:
    #         raise ValueError(f"Right {right.value} is not an add or remove right.")
    #     has_right_function = self._get_has_right_function(right)
    #     get_from_data_collections_function = (
    #         self._get_from_data_collections_for_right_function(right)
    #     )
    #     if require_private and from_data_collection_ids is not None:
    #         raise ValueError(
    #             "from_data_collection_ids must be None if require_private is True"
    #         )
    #     elif not require_private and from_data_collection_ids is None:
    #         # Make from_data_collection_ids an empty set for easier processing
    #         from_data_collection_ids = set()
    #     # Determine if the operation is allowed
    #     access_data = CaseAbac.case_type_access_abacs.get(case_type_id, {})
    #     share_data = CaseAbac.case_type_share_abacs.get(case_type_id, {})
    #     n_private = 0
    #     for data_collection_id in data_collection_ids:
    #         if data_collection_id not in access_data:
    #             # No direct access to this data collection -> check share rights
    #             if data_collection_id not in share_data:
    #                 # No share rights either
    #                 return False
    #             # Check direct share rights from the provided data collections
    #             if all(
    #                 get_from_data_collections_function(x).isdisjoint(
    #                     data_collection_ids
    #                 )
    #                 for x in share_data[data_collection_id]
    #             ):
    #                 # No share rights from the provided data collections
    #                 return False
    #             # TODO: Check indirect share rights from the provided data collections
    #             # by checking if there is a path from the provided data collections to
    #             # this data collection through the share rights
    #         if access_data[data_collection_id].is_private:
    #             # This data collection is private
    #             n_private += 1
    #         if not has_right_function(access_data[data_collection_id]):
    #             # No access to this data collection
    #             return False
    #     if n_private != 1:
    #         # There must be exactly one private data collection
    #         return False
    #     # All checks passed
    #     return True

    def is_allowed(
        self,
        case_type_id: UUID,
        right: CaseRight,
        is_create_or_delete: bool = False,
        created_in_data_collection_id: UUID | None = None,
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

        # Parse input
        if current_data_collection_ids is None:
            current_data_collection_ids = set()
        if tgt_data_collection_ids is None:
            tgt_data_collection_ids = set()

        # Get rights for the case type
        access_abac = self.case_type_access_abacs.get(case_type_id, {})
        share_abac = self.case_type_share_abacs.get(case_type_id, {})
        if access_abac is None and share_abac is None:
            # No rights to this case type
            return False

        # Handle each right
        has_right_function = self._get_has_right_function(right)
        if right in CaseRightSet.ADD.value:
            # Check if the case or case set can be added to all the target data collections
            if is_create_or_delete:
                # Check if the case or case set can be created
                if created_in_data_collection_id is None:
                    raise exc.InvalidArgumentsError(
                        f"created_in_data_collection_id must be provided for right {right.value} if is_create_or_delete=True"
                    )
                if created_in_data_collection_id not in access_abac:
                    # No access to this data collection
                    return False
                if not access_abac[created_in_data_collection_id].is_private:
                    # created_in_data_collection_id is not a private data collection
                    return False
                if current_data_collection_ids:
                    raise exc.InvalidArgumentsError(
                        f"current_data_collection_ids must be empty for right {right.value} if is_create_or_delete=True"
                    )
            # Check for each of the remaining target data collections if the user has
            # the right to add cases or case sets to it
            remaining_data_collection_ids = (
                set()
                if tgt_data_collection_ids is None
                else set(tgt_data_collection_ids)
            )
            remaining_data_collection_ids.discard(
                created_in_data_collection_id  # type:ignore[arg-type]
            )
            if current_data_collection_ids:
                remaining_data_collection_ids = (
                    remaining_data_collection_ids - current_data_collection_ids
                )
            current_data_collection_ids.add(
                created_in_data_collection_id  # type:ignore[arg-type]
            )
            get_share_from_data_collections_function = (
                self._get_get_share_from_data_collections_function(right)
            )
            for data_collection_id in remaining_data_collection_ids:
                if data_collection_id not in access_abac:
                    # No access to this data collection
                    return False
                if access_abac[data_collection_id].is_private:
                    # Private data collection different from the created in data collection
                    return False
                if not has_right_function(access_abac[data_collection_id]):
                    # No access right in this data collection -> check share rights
                    if (
                        share_abac is None
                        or data_collection_id not in share_abac
                        or not current_data_collection_ids.intersection(
                            get_share_from_data_collections_function(
                                share_abac[data_collection_id]
                            )
                        )
                    ):
                        # No direct share rights either
                        # TODO: Check indirect share rights from the provided data collections
                        return False
        elif right in CaseRightSet.REMOVE.value:
            # Check if the case or case set can be deleted from all the target data collections
            if is_create_or_delete:
                # Check if the case or case set can be deleted
                if created_in_data_collection_id is None:
                    raise exc.InvalidArgumentsError(
                        f"created_in_data_collection_id must be provided for right {right.value} if is_create_or_delete=True"
                    )
                if created_in_data_collection_id not in access_abac:
                    # No access to this data collection
                    return False
                if not access_abac[created_in_data_collection_id].is_private:
                    # created_in_data_collection_id is not a private data collection
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
            remaining_data_collection_ids.discard(
                created_in_data_collection_id  # type:ignore[arg-type]
            )
            get_share_from_data_collections_function = (
                self._get_get_share_from_data_collections_function(right)
            )
            for data_collection_id in remaining_data_collection_ids:
                if data_collection_id not in access_abac:
                    # No access to this data collection
                    return False
                if access_abac[data_collection_id].is_private:
                    # Private data collection different from the created in data collection
                    return False
                if not has_right_function(access_abac[data_collection_id]):
                    # No access right in this data collection -> check share rights
                    if (
                        share_abac is None
                        or data_collection_id not in share_abac
                        or not current_data_collection_ids.intersection(
                            get_share_from_data_collections_function(
                                share_abac[data_collection_id]
                            )
                        )
                    ):
                        # No direct share rights either
                        # TODO: Check indirect share rights from the provided data collections
                        return False
        elif right in CaseRightSet.CONTENT.value:
            # Check if the case or case set can be read or written from any of the current data collections
            if is_create_or_delete:
                raise exc.InvalidArgumentsError(
                    f"is_create_or_delete must be False for right {right.value}"
                )
            if tgt_data_collection_ids:
                raise exc.InvalidArgumentsError(
                    f"tgt_data_collection_ids must be empty for right {right.value}"
                )
            has_right_function = self._get_has_right_function(right)
            for data_collection_id in current_data_collection_ids:
                if data_collection_id in access_abac and has_right_function(
                    access_abac[data_collection_id]
                ):
                    # Access right in this data collection
                    return True
        else:
            raise exc.InvalidArgumentsError(f"Right {right.value} is invalid")
        # All checks passed
        return True

    def get_case_rights(
        self,
        case_id: UUID,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: frozenset[UUID],
    ) -> CaseRights:
        case_rights: CaseRights = (
            self._get_case_or_set_rights(  # type:ignore[assignment]
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
        data_collection_ids: frozenset[UUID],
    ) -> CaseSetRights:
        case_set_rights: CaseSetRights = (
            self._get_case_or_set_rights(  # type:ignore[assignment]
                case_set_id,
                True,
                case_type_id,
                created_in_data_collection_id,
                data_collection_ids,
            )
        )
        return case_set_rights

    def _get_case_or_set_rights(
        self,
        case_or_set_id: UUID,
        is_case_set: bool,
        case_type_id: UUID,
        created_in_data_collection_id: UUID,
        data_collection_ids: frozenset[UUID],
    ) -> CaseRights | CaseSetRights:
        # Parse input
        shared_in_data_collection_ids = data_collection_ids - {
            created_in_data_collection_id
        }
        if self.is_full_access:
            if is_case_set:
                return CaseSetRights(
                    case_set_id=case_or_set_id,
                    case_type_id=case_type_id,
                    created_in_data_collection_id=created_in_data_collection_id,
                    data_collection_ids=data_collection_ids,  # type:ignore[arg-type]
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
                data_collection_ids=data_collection_ids,  # type:ignore[arg-type]
                is_full_access=True,
                add_data_collection_ids=set(),
                remove_data_collection_ids=set(),
                read_case_type_col_ids=set(),
                write_case_type_col_ids=set(),
                can_delete=True,
                shared_in_data_collection_ids=shared_in_data_collection_ids,
            )

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
        # Data collections that the case/set is not yet in but is allowed to be added to
        add_data_collection_ids = (
            {
                x
                for x, y in access.items()
                if (y.add_case_set if is_case_set else y.add_case)
                and x not in data_collection_ids
            }
            if is_own_private
            else set()
        )
        # Data collections that the case/set is in and is allowed to be removed from
        remove_data_collection_ids = (
            {
                x
                for x, y in access.items()
                if (y.remove_case_set if is_case_set else y.remove_case)
                and x in data_collection_ids
            }
            if is_own_private
            else set()
        )

        # Read/write rights
        if is_case_set:
            # Whether the case set can be read/written
            read_case_set = any(x.read_case_set for x in access.values())
            write_case_set = any(x.write_case_set for x in access.values())
        else:
            # Case type cols that can be read/written
            read_case_type_col_ids = set.union(
                *[x.read_case_type_col_ids for x in access.values()]
            )
            write_case_type_col_ids = set.union(
                *[x.write_case_type_col_ids for x in access.values()]
            )

        # Determine any other share rights
        share: dict[UUID, CaseTypeShareAbac] = self.case_type_share_abacs.get(
            case_type_id, {}
        )
        for to_data_collection_id, case_type_share_abac in share.items():
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

        can_delete = self.is_full_access or set(data_collection_ids).issubset(
            set(remove_data_collection_ids)
        )

        # Create the rights object
        if is_case_set:
            return CaseSetRights(
                case_set_id=case_or_set_id,
                case_type_id=case_type_id,
                created_in_data_collection_id=created_in_data_collection_id,
                data_collection_ids=data_collection_ids,  # type:ignore[arg-type]
                is_full_access=self.is_full_access,
                add_data_collection_ids=add_data_collection_ids,
                remove_data_collection_ids=remove_data_collection_ids,
                read_case_set=read_case_set,
                write_case_set=write_case_set,
                can_delete=can_delete,
                shared_in_data_collection_ids=shared_in_data_collection_ids,
            )
        return CaseRights(
            case_id=case_or_set_id,
            case_type_id=case_type_id,
            created_in_data_collection_id=created_in_data_collection_id,
            data_collection_ids=data_collection_ids,  # type:ignore[arg-type]
            is_full_access=self.is_full_access,
            add_data_collection_ids=add_data_collection_ids,
            remove_data_collection_ids=remove_data_collection_ids,
            read_case_type_col_ids=read_case_type_col_ids,
            write_case_type_col_ids=write_case_type_col_ids,
            can_delete=can_delete,
            shared_in_data_collection_ids=shared_in_data_collection_ids,
        )

    @staticmethod
    def _get_has_right_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeAccessAbac | CaseTypeShareAbac], bool]:
        if right == CaseRight.ADD_CASE:
            has_right_function = lambda x: x.add_case
        elif right == CaseRight.REMOVE_CASE:
            has_right_function = lambda x: x.remove_case
        elif right == CaseRight.READ_CASE:
            has_right_function = lambda x: len(x.read_case_type_col_ids) > 0
        elif right == CaseRight.WRITE_CASE:
            has_right_function = lambda x: len(x.write_case_type_col_ids) > 0
        elif right == CaseRight.ADD_CASE_SET:
            has_right_function = lambda x: x.add_case_set
        elif right == CaseRight.REMOVE_CASE_SET:
            has_right_function = lambda x: x.remove_case_set
        elif right == CaseRight.READ_CASE_SET:
            has_right_function = lambda x: x.read_case_set
        elif right == CaseRight.WRITE_CASE_SET:
            has_right_function = lambda x: x.write_case_set
        else:
            raise NotImplementedError(f"Right {right.value} not implemented")
        return has_right_function

    @staticmethod
    def _get_get_share_from_data_collections_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeShareAbac], set[UUID]]:
        if right == CaseRight.ADD_CASE:
            get_share_from_data_collections_function = (
                lambda x: x.add_case_from_data_collection_ids
            )
        elif right == CaseRight.REMOVE_CASE:
            get_share_from_data_collections_function = (
                lambda x: x.remove_case_from_data_collection_ids
            )
        elif right == CaseRight.ADD_CASE_SET:
            get_share_from_data_collections_function = (
                lambda x: x.add_case_set_from_data_collection_ids
            )
        elif right == CaseRight.REMOVE_CASE_SET:
            get_share_from_data_collections_function = (
                lambda x: x.remove_case_set_from_data_collection_ids
            )
        else:
            raise NotImplementedError(f"Right {right.value} not implemented")
        return get_share_from_data_collections_function

    @staticmethod
    def _get_from_data_collections_for_right_function(
        right: CaseRight,
    ) -> Callable[[CaseTypeShareAbac], set[UUID]]:
        if right == CaseRight.ADD_CASE:
            get_from_data_collections_function = (
                lambda x: x.add_case_from_data_collection_ids
            )
        elif right == CaseRight.REMOVE_CASE:
            get_from_data_collections_function = (
                lambda x: x.remove_case_from_data_collection_ids
            )
        elif right == CaseRight.ADD_CASE_SET:
            get_from_data_collections_function = (
                lambda x: x.add_case_set_from_data_collection_ids
            )
        elif right == CaseRight.REMOVE_CASE_SET:
            get_from_data_collections_function = (
                lambda x: x.remove_case_set_from_data_collection_ids
            )
        else:
            raise NotImplementedError(f"Right {right.value} not implemented")
        return get_from_data_collections_function
