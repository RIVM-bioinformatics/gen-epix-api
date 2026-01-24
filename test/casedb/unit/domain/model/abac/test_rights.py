from unittest import TestCase
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain.enum import CaseRight, CaseRightSet
from gen_epix.casedb.domain.model.abac.rights import (
    CaseAbac,
    CaseTypeAccessAbac,
    CaseTypeShareAbac,
)
from gen_epix.fastapp import exc


class BaseCaseAbacTestCase(TestCase):
    """Base test case with common fixtures for ABAC rights."""

    def setUp(self) -> None:
        # IDs
        self.case_type_id_1: UUID = UUID("11111111-1111-1111-1111-111111111111")
        self.case_type_id_2: UUID = UUID("22222222-2222-2222-2222-222222222222")
        self.dc1: UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1")
        self.dc2: UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2")
        self.dc3: UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3")
        self.dc4: UUID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4")
        self.col1: UUID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1")
        self.col2: UUID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2")
        self.col3: UUID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3")

    def make_access(
        self,
        data_collection_id: UUID,
        *,
        is_private: bool = False,
        add_case: bool = False,
        remove_case: bool = False,
        add_case_set: bool = False,
        remove_case_set: bool = False,
        read_cols: set[UUID] | None = None,
        write_cols: set[UUID] | None = None,
        read_case_set: bool = False,
        write_case_set: bool = False,
    ) -> CaseTypeAccessAbac:
        return CaseTypeAccessAbac(
            case_type_id=self.case_type_id_1,
            data_collection_id=data_collection_id,
            is_private=is_private,
            add_case=add_case,
            remove_case=remove_case,
            add_case_set=add_case_set,
            remove_case_set=remove_case_set,
            read_case_type_col_ids=read_cols or set(),
            write_case_type_col_ids=write_cols or set(),
            read_case_set=read_case_set,
            write_case_set=write_case_set,
        )

    def make_share(
        self,
        to_data_collection_id: UUID,
        *,
        add_from: set[UUID] | None = None,
        remove_from: set[UUID] | None = None,
        add_set_from: set[UUID] | None = None,
        remove_set_from: set[UUID] | None = None,
    ) -> CaseTypeShareAbac:
        return CaseTypeShareAbac(
            case_type_id=self.case_type_id_1,
            data_collection_id=to_data_collection_id,
            add_case_from_data_collection_ids=add_from or set(),
            remove_case_from_data_collection_ids=remove_from or set(),
            add_case_set_from_data_collection_ids=add_set_from or set(),
            remove_case_set_from_data_collection_ids=remove_set_from or set(),
        )


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestCaseTypeAccessAbac(BaseCaseAbacTestCase):
    def test_has_any_rights_false(self) -> None:
        access: CaseTypeAccessAbac = self.make_access(
            self.dc1,
            is_private=False,
            add_case=False,
            remove_case=False,
            add_case_set=False,
            remove_case_set=False,
            read_cols=set(),
            write_cols=set(),
            read_case_set=False,
            write_case_set=False,
        )
        self.assertFalse(access.has_any_rights())

    def test_has_any_rights_true_by_flag(self) -> None:
        access: CaseTypeAccessAbac = self.make_access(self.dc1, add_case=True)
        self.assertTrue(access.has_any_rights())

    def test_has_any_rights_true_by_cols(self) -> None:
        access: CaseTypeAccessAbac = self.make_access(self.dc1, read_cols={self.col1})
        self.assertTrue(access.has_any_rights())


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestCaseTypeShareAbac(BaseCaseAbacTestCase):
    def test_has_any_rights_false(self) -> None:
        share: CaseTypeShareAbac = self.make_share(self.dc1)
        self.assertFalse(share.has_any_rights())

    def test_has_any_rights_true_by_add(self) -> None:
        share: CaseTypeShareAbac = self.make_share(self.dc2, add_from={self.dc1})
        self.assertTrue(share.has_any_rights())

    def test_has_any_rights_true_by_remove_set(self) -> None:
        share: CaseTypeShareAbac = self.make_share(self.dc3, remove_set_from={self.dc1})
        self.assertTrue(share.has_any_rights())


@pytest.mark.scenario_ids("TC-RBAC-01-02", "TC-SEC-29-01")
class TestCaseAbac(BaseCaseAbacTestCase):
    def test_get_combinations_with_any_rights(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1),
                self.dc2: self.make_access(self.dc2, add_case=True),
            }
        }
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_1: {
                self.dc3: self.make_share(self.dc3, add_from={self.dc2}),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        combos = abac.get_combinations_with_any_rights()
        self.assertIn(self.case_type_id_1, combos)
        self.assertEqual(combos[self.case_type_id_1], {self.dc2, self.dc3})

    def test_get_case_types_with_any_rights(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1),
            },
            self.case_type_id_2: {
                self.dc2: CaseTypeAccessAbac(
                    case_type_id=self.case_type_id_2,
                    data_collection_id=self.dc2,
                    is_private=False,
                    add_case=True,
                    remove_case=False,
                    add_case_set=False,
                    remove_case_set=False,
                    read_case_type_col_ids=set(),
                    write_case_type_col_ids=set(),
                    read_case_set=False,
                    write_case_set=False,
                ),
            },
        }
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {}
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        case_types = abac.get_case_types_with_any_rights()
        self.assertEqual(case_types, {self.case_type_id_2})

    def test_get_combinations_with_access_right(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1}),
                self.dc2: self.make_access(self.dc2, add_case=True),
                self.dc3: self.make_access(self.dc3, write_cols={self.col2}),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        add_combos = abac.get_combinations_with_access_right(CaseRight.ADD_CASE)
        self.assertEqual(add_combos[self.case_type_id_1], {self.dc2})
        read_combos = abac.get_combinations_with_access_right(CaseRight.READ_CASE)
        self.assertEqual(read_combos[self.case_type_id_1], {self.dc1})
        write_combos = abac.get_combinations_with_access_right(CaseRight.WRITE_CASE)
        self.assertEqual(write_combos[self.case_type_id_1], {self.dc3})

    def test_get_case_types_with_access_right(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1),
            },
            self.case_type_id_2: {
                self.dc2: CaseTypeAccessAbac(
                    case_type_id=self.case_type_id_2,
                    data_collection_id=self.dc2,
                    is_private=False,
                    add_case=False,
                    remove_case=False,
                    add_case_set=False,
                    remove_case_set=False,
                    read_case_type_col_ids={self.col1},
                    write_case_type_col_ids=set(),
                    read_case_set=False,
                    write_case_set=False,
                )
            },
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        case_types = abac.get_case_types_with_access_right(CaseRight.READ_CASE)
        self.assertEqual(case_types, {self.case_type_id_2})

    def test_get_case_type_cols_with_any_rights_unfiltered(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(
                    self.dc1, read_cols={self.col1}, write_cols={self.col2}
                ),
            },
            self.case_type_id_2: {
                self.dc2: CaseTypeAccessAbac(
                    case_type_id=self.case_type_id_2,
                    data_collection_id=self.dc2,
                    is_private=False,
                    add_case=False,
                    remove_case=False,
                    add_case_set=False,
                    remove_case_set=False,
                    read_case_type_col_ids={self.col3},
                    write_case_type_col_ids=set(),
                    read_case_set=False,
                    write_case_set=False,
                )
            },
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        cols = abac.get_case_type_cols_with_any_rights()
        self.assertEqual(cols, {self.col1, self.col2, self.col3})

    def test_get_case_type_cols_with_any_rights_filtered_includes_all(self) -> None:
        # Due to implementation, filtered path still aggregates all case types.
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1})
            },
            self.case_type_id_2: {
                self.dc2: CaseTypeAccessAbac(
                    case_type_id=self.case_type_id_2,
                    data_collection_id=self.dc2,
                    is_private=False,
                    add_case=False,
                    remove_case=False,
                    add_case_set=False,
                    remove_case_set=False,
                    read_case_type_col_ids={self.col2},
                    write_case_type_col_ids=set(),
                    read_case_set=False,
                    write_case_set=False,
                )
            },
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        cols = abac.get_case_type_cols_with_any_rights(self.case_type_id_1)
        self.assertEqual(cols, {self.col1, self.col2})

    def test_get_case_type_cols_with_access_rights_read_filtered(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1}),
                self.dc2: self.make_access(self.dc2, write_cols={self.col2}),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        cols_read = abac.get_case_type_cols_with_access_rights(
            CaseRight.READ_CASE, case_type_id=self.case_type_id_1
        )
        self.assertEqual(cols_read, {self.col1})
        cols_write = abac.get_case_type_cols_with_access_rights(
            CaseRight.WRITE_CASE, case_type_id=self.case_type_id_1
        )
        self.assertEqual(cols_write, {self.col2})
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.get_case_type_cols_with_access_rights(
                CaseRight.ADD_CASE, case_type_id=self.case_type_id_1
            )

    def test_get_data_collections_with_any_rights(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, add_case=True),
                self.dc2: self.make_access(self.dc2),
            }
        }
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_1: {
                self.dc3: self.make_share(
                    self.dc3, add_from={self.dc1}, remove_from={self.dc2}
                ),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        dcs = abac.get_data_collections_with_any_rights()
        self.assertEqual(dcs, {self.dc1, self.dc2, self.dc3})

    def test_get_data_collections_with_access_right_for_case_type_col(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1}),
                self.dc2: self.make_access(self.dc2, write_cols={self.col1}),
            },
            self.case_type_id_2: {
                self.dc3: CaseTypeAccessAbac(
                    case_type_id=self.case_type_id_2,
                    data_collection_id=self.dc3,
                    is_private=False,
                    add_case=False,
                    remove_case=False,
                    add_case_set=False,
                    remove_case_set=False,
                    read_case_type_col_ids={self.col1},
                    write_case_type_col_ids=set(),
                    read_case_set=False,
                    write_case_set=False,
                )
            },
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        read_dcs = abac.get_data_collections_with_access_right_for_case_type_col(
            self.col1, CaseRight.READ_CASE
        )
        self.assertEqual(read_dcs, {self.dc1, self.dc3})
        write_dcs = abac.get_data_collections_with_access_right_for_case_type_col(
            self.col1, CaseRight.WRITE_CASE
        )
        self.assertEqual(write_dcs, {self.dc2})
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.get_data_collections_with_access_right_for_case_type_col(
                self.col1, CaseRight.ADD_CASE
            )

    def test_is_allowed_full_access(self) -> None:
        abac: CaseAbac = CaseAbac(
            is_full_access=True, case_type_access_abacs={}, case_type_share_abacs={}
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.ADD_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
            current_data_collection_ids={self.dc1},
            tgt_data_collection_ids={self.dc2},
        )
        self.assertTrue(allowed)

    def test_is_allowed_add_create_missing_created_in_raises(self) -> None:
        abac: CaseAbac = CaseAbac(
            is_full_access=False, case_type_access_abacs={}, case_type_share_abacs={}
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.ADD_CASE,
                is_create_or_delete=True,
                created_in_data_collection_id=None,
            )

    def test_is_allowed_add_create_not_in_access_returns_false(self) -> None:
        abac: CaseAbac = CaseAbac(
            is_full_access=False, case_type_access_abacs={}, case_type_share_abacs={}
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.ADD_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
        )
        self.assertFalse(allowed)

    def test_is_allowed_add_create_not_private_returns_false(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=False)
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.ADD_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
        )
        self.assertFalse(allowed)

    def test_is_allowed_add_create_current_non_empty_raises(self) -> None:
        access_map = {
            self.case_type_id_1: {self.dc1: self.make_access(self.dc1, is_private=True)}
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.ADD_CASE,
                is_create_or_delete=True,
                created_in_data_collection_id=self.dc1,
                current_data_collection_ids={self.dc1},
            )

        # set is_create_or_delete to False to other path
        self.assertFalse(
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.ADD_CASE,
                is_create_or_delete=False,
                created_in_data_collection_id=self.dc1,
                current_data_collection_ids={self.dc1},
                tgt_data_collection_ids={
                    self.dc3
                },  # Add tgt to not get a no-operation add
            )
        )

    def test_is_allowed_add_remaining_target_no_access_no_share_false(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=True),
                self.dc2: self.make_access(self.dc2, is_private=False),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.ADD_CASE,
            is_create_or_delete=False,
            created_in_data_collection_id=self.dc1,
            tgt_data_collection_ids={self.dc2},
        )
        self.assertFalse(allowed)

    def test_is_allowed_add_with_share_true(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=True),
                self.dc2: self.make_access(self.dc2, is_private=False),
            }
        }
        share_map = {
            self.case_type_id_1: {
                self.dc2: self.make_share(self.dc2, add_from={self.dc1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.ADD_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
            tgt_data_collection_ids={self.dc2},
        )
        self.assertTrue(allowed)

    def test_is_allowed_add_to_private_target_false(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=True),
                self.dc2: self.make_access(self.dc2, is_private=True),
            }
        }
        share_map = {
            self.case_type_id_1: {
                self.dc2: self.make_share(self.dc2, add_from={self.dc1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.ADD_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
            tgt_data_collection_ids={self.dc2},
        )
        self.assertFalse(allowed)

    def test_is_allowed_remove_delete_missing_created_in_raises(self) -> None:
        abac: CaseAbac = CaseAbac(
            is_full_access=False, case_type_access_abacs={}, case_type_share_abacs={}
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.REMOVE_CASE,
                is_create_or_delete=True,
                created_in_data_collection_id=None,
            )

    def test_is_allowed_remove_delete_not_in_access_false(self) -> None:
        abac: CaseAbac = CaseAbac(
            is_full_access=False, case_type_access_abacs={}, case_type_share_abacs={}
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.REMOVE_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
        )
        self.assertFalse(allowed)

    def test_is_allowed_remove_delete_not_private_false(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=False)
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.REMOVE_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
        )
        self.assertFalse(allowed)

    def test_is_allowed_remove_delete_tgt_not_empty_raises(self) -> None:
        access_map = {
            self.case_type_id_1: {self.dc1: self.make_access(self.dc1, is_private=True)}
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.REMOVE_CASE,
                is_create_or_delete=True,
                created_in_data_collection_id=self.dc1,
                tgt_data_collection_ids={self.dc2},
            )

    def test_is_allowed_remove_tgt_not_subset_raises(self) -> None:
        access_map = {
            self.case_type_id_1: {self.dc1: self.make_access(self.dc1, is_private=True)}
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.REMOVE_CASE,
                is_create_or_delete=False,
                created_in_data_collection_id=self.dc1,
                current_data_collection_ids={self.dc1},
                tgt_data_collection_ids={self.dc2},
            )

    def test_is_allowed_remove_with_share_true(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=True),
                self.dc2: self.make_access(self.dc2, is_private=False),
            }
        }
        share_map = {
            self.case_type_id_1: {
                self.dc2: self.make_share(self.dc2, remove_from={self.dc1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.REMOVE_CASE,
            is_create_or_delete=False,
            created_in_data_collection_id=self.dc1,
            current_data_collection_ids={self.dc1, self.dc2},
            tgt_data_collection_ids={self.dc2},
        )
        self.assertTrue(allowed)

    def test_is_allowed_content_is_create_or_delete_true_raises(self) -> None:
        access_map = {self.case_type_id_1: {self.dc1: self.make_access(self.dc1)}}
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.READ_CASE,
                is_create_or_delete=True,
                current_data_collection_ids={self.dc1},
            )

    def test_is_allowed_content_tgt_not_empty_raises(self) -> None:
        access_map = {self.case_type_id_1: {self.dc1: self.make_access(self.dc1)}}
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=CaseRight.WRITE_CASE,
                tgt_data_collection_ids={self.dc1},
                current_data_collection_ids={self.dc1},
            )

    def test_is_allowed_content_read_true(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.READ_CASE,
            is_create_or_delete=False,
            current_data_collection_ids={self.dc1},
        )
        self.assertTrue(allowed)

    def test_is_allowed_content_read_false(self) -> None:
        """
        This test expects is_allowed to return False bfecause the access map does not grant any read rights
        (no read_cols specified) for the given data collection. Therefore, CaseAbac.is_allowed should deny
        READ_CASE access for the provided current_data_collection_ids.
        """
        access_map = {self.case_type_id_1: {self.dc1: self.make_access(self.dc1)}}
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.READ_CASE,
            is_create_or_delete=False,
            current_data_collection_ids={self.dc1},
        )
        self.assertFalse(allowed)

    def test_is_allowed_invalid_right_raises(self) -> None:
        access_map = {self.case_type_id_1: {self.dc1: self.make_access(self.dc1)}}
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.is_allowed(
                case_type_id=self.case_type_id_1,
                right=next(iter(CaseRightSet.CONTENT.value)),  # type: ignore[arg-type]
                is_create_or_delete=False,
                tgt_data_collection_ids={self.dc1},
            )

    def test_get_case_rights_non_full_access(self) -> None:
        # Access: created_in is private; remove rights on dc1, dc2; add rights on dc3; share add to dc4 from dc2
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(
                    self.dc1,
                    is_private=True,
                    remove_case=True,
                    read_cols={self.col1},
                    write_cols={self.col3},
                ),
                self.dc2: self.make_access(
                    self.dc2, remove_case=True, read_cols={self.col2}
                ),
                self.dc3: self.make_access(self.dc3, add_case=True),
            }
        }
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_1: {
                self.dc4: self.make_share(self.dc4, add_from={self.dc2})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        case_id: UUID = uuid4()
        rights = abac.get_case_rights(
            case_id=case_id,
            case_type_id=self.case_type_id_1,
            created_in_data_collection_id=self.dc1,
            data_collection_ids=frozenset({self.dc1, self.dc2}),
        )
        self.assertFalse(rights.is_full_access)
        self.assertEqual(rights.case_id, case_id)
        self.assertEqual(rights.add_data_collection_ids, {self.dc3, self.dc4})
        self.assertEqual(rights.remove_data_collection_ids, {self.dc1, self.dc2})
        self.assertEqual(rights.read_case_type_col_ids, {self.col1, self.col2})
        self.assertEqual(rights.write_case_type_col_ids, {self.col3})
        self.assertTrue(rights.can_delete)
        self.assertEqual(rights.shared_in_data_collection_ids, {self.dc2})

    def test_get_case_set_rights_non_full_access(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(
                    self.dc1, is_private=True, remove_case_set=True, read_case_set=True
                ),
                self.dc2: self.make_access(
                    self.dc2, remove_case_set=True, write_case_set=True
                ),
                self.dc3: self.make_access(self.dc3, add_case_set=True),
            }
        }
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_1: {
                self.dc4: self.make_share(self.dc4, add_set_from={self.dc2})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        case_set_id: UUID = uuid4()
        rights = abac.get_case_set_rights(
            case_set_id=case_set_id,
            case_type_id=self.case_type_id_1,
            created_in_data_collection_id=self.dc1,
            data_collection_ids=frozenset({self.dc1, self.dc2}),
        )
        self.assertFalse(rights.is_full_access)
        self.assertEqual(rights.case_set_id, case_set_id)
        self.assertEqual(rights.add_data_collection_ids, {self.dc3, self.dc4})
        self.assertEqual(rights.remove_data_collection_ids, {self.dc1, self.dc2})
        self.assertTrue(rights.read_case_set)
        self.assertTrue(rights.write_case_set)
        self.assertTrue(rights.can_delete)
        self.assertEqual(rights.shared_in_data_collection_ids, {self.dc2})

    def test_get_case_rights_full_access(self) -> None:
        abac: CaseAbac = CaseAbac(
            is_full_access=True, case_type_access_abacs={}, case_type_share_abacs={}
        )
        case_id: UUID = uuid4()
        rights = abac.get_case_rights(
            case_id=case_id,
            case_type_id=self.case_type_id_1,
            created_in_data_collection_id=self.dc1,
            data_collection_ids=frozenset({self.dc1, self.dc2}),
        )
        self.assertTrue(rights.is_full_access)
        self.assertEqual(rights.add_data_collection_ids, set())
        self.assertEqual(rights.remove_data_collection_ids, set())
        self.assertTrue(rights.can_delete)
        self.assertEqual(rights.read_case_type_col_ids, set())
        self.assertEqual(rights.write_case_type_col_ids, set())
        self.assertEqual(rights.shared_in_data_collection_ids, {self.dc2})

    def test_get_case_set_rights_full_access(self) -> None:
        abac: CaseAbac = CaseAbac(
            is_full_access=True, case_type_access_abacs={}, case_type_share_abacs={}
        )
        case_set_id: UUID = uuid4()
        rights = abac.get_case_set_rights(
            case_set_id=case_set_id,
            case_type_id=self.case_type_id_1,
            created_in_data_collection_id=self.dc1,
            data_collection_ids=frozenset({self.dc1, self.dc2}),
        )
        self.assertTrue(rights.is_full_access)
        self.assertEqual(rights.add_data_collection_ids, set())
        self.assertEqual(rights.remove_data_collection_ids, set())
        self.assertTrue(rights.can_delete)
        self.assertTrue(rights.read_case_set)
        self.assertTrue(rights.write_case_set)
        self.assertEqual(rights.shared_in_data_collection_ids, {self.dc2})

    def test_get_combinations_with_any_rights_share_only(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {}
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_1: {
                self.dc3: self.make_share(self.dc3, add_from={self.dc1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        combos = abac.get_combinations_with_any_rights()
        self.assertEqual(combos, {self.case_type_id_1: {self.dc3}})

    def test_get_case_types_with_any_rights_share_only(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {}
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_2: {
                self.dc4: self.make_share(self.dc4, remove_from={self.dc1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        case_types = abac.get_case_types_with_any_rights()
        self.assertEqual(case_types, {self.case_type_id_2})

    def test_get_case_type_cols_with_any_rights_filtered_missing_case_type_returns_empty(
        self,
    ) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        cols = abac.get_case_type_cols_with_any_rights(self.case_type_id_2)
        self.assertEqual(cols, set())

    def test_get_case_type_cols_with_access_rights_unfiltered_invalid_right_raises(
        self,
    ) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1}),
                self.dc2: self.make_access(self.dc2, write_cols={self.col2}),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        with self.assertRaises(exc.InvalidArgumentsError):
            abac.get_case_type_cols_with_access_rights(CaseRight.ADD_CASE)

    def test_get_case_type_cols_with_access_rights_unfiltered(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, read_cols={self.col1}),
                self.dc2: self.make_access(self.dc2, write_cols={self.col2}),
            },
            self.case_type_id_2: {
                self.dc3: self.make_access(self.dc3, read_cols={self.col3}),
            },
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        self.assertEqual(
            abac.get_case_type_cols_with_access_rights(CaseRight.READ_CASE),
            {self.col1, self.col3},
        )
        self.assertEqual(
            abac.get_case_type_cols_with_access_rights(CaseRight.WRITE_CASE),
            {self.col2},
        )

    def test_get_data_collections_with_any_rights_share_no_rights_ignored(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {self.dc1: self.make_access(self.dc1, add_case=True)}
        }
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_1: {
                self.dc4: self.make_share(self.dc4)
            }  # no rights -> ignored
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        dcs = abac.get_data_collections_with_any_rights()
        self.assertEqual(dcs, {self.dc1})

    def test_is_allowed_add_direct_access_true(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=True),
                self.dc2: self.make_access(self.dc2, is_private=False, add_case=True),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.ADD_CASE,
            is_create_or_delete=True,
            created_in_data_collection_id=self.dc1,
            tgt_data_collection_ids={self.dc2},
        )
        self.assertTrue(allowed)

    def test_is_allowed_remove_direct_access_true(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=True),
                self.dc2: self.make_access(
                    self.dc2, is_private=False, remove_case=True
                ),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.REMOVE_CASE,
            is_create_or_delete=False,
            created_in_data_collection_id=self.dc1,
            current_data_collection_ids={self.dc1, self.dc2},
            tgt_data_collection_ids={self.dc2},
        )
        self.assertTrue(allowed)

    def test_is_allowed_content_write_true(self) -> None:
        access_map = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, write_cols={self.col1})
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        allowed = abac.is_allowed(
            case_type_id=self.case_type_id_1,
            right=CaseRight.WRITE_CASE,
            is_create_or_delete=False,
            current_data_collection_ids={self.dc1},
        )
        self.assertTrue(allowed)

    def test_get_case_rights_not_own_private_share_only_can_delete_false(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(self.dc1, is_private=False),
                self.dc2: self.make_access(self.dc2, is_private=False),
            }
        }
        share_map: dict[UUID, dict[UUID, CaseTypeShareAbac]] = {
            self.case_type_id_1: {
                self.dc3: self.make_share(self.dc3, add_from={self.dc1}),
                self.dc2: self.make_share(self.dc2, remove_from={self.dc1}),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs=share_map,
        )
        case_id: UUID = uuid4()
        rights = abac.get_case_rights(
            case_id=case_id,
            case_type_id=self.case_type_id_1,
            created_in_data_collection_id=self.dc1,
            data_collection_ids=frozenset({self.dc1, self.dc2}),
        )
        self.assertEqual(rights.add_data_collection_ids, {self.dc3})
        self.assertEqual(rights.remove_data_collection_ids, {self.dc2})
        self.assertFalse(rights.can_delete)

    def test_get_case_set_rights_can_delete_false(self) -> None:
        access_map: dict[UUID, dict[UUID, CaseTypeAccessAbac]] = {
            self.case_type_id_1: {
                self.dc1: self.make_access(
                    self.dc1, is_private=True, remove_case_set=True
                ),
                self.dc2: self.make_access(
                    self.dc2, is_private=False, remove_case_set=False
                ),
            }
        }
        abac: CaseAbac = CaseAbac(
            is_full_access=False,
            case_type_access_abacs=access_map,
            case_type_share_abacs={},
        )
        case_set_id: UUID = uuid4()
        rights = abac.get_case_set_rights(
            case_set_id=case_set_id,
            case_type_id=self.case_type_id_1,
            created_in_data_collection_id=self.dc1,
            data_collection_ids=frozenset({self.dc1, self.dc2}),
        )
        self.assertEqual(rights.remove_data_collection_ids, {self.dc1})
        self.assertFalse(rights.can_delete)


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestHelperFunctions(BaseCaseAbacTestCase):
    def test_get_has_right_function_branches(self) -> None:
        access: CaseTypeAccessAbac = self.make_access(
            self.dc1,
            add_case=True,
            remove_case=True,
            add_case_set=True,
            remove_case_set=True,
            read_cols={self.col1},
            write_cols={self.col2},
            read_case_set=True,
            write_case_set=True,
        )
        # ADD_CASE
        self.assertTrue(CaseAbac._get_has_right_function(CaseRight.ADD_CASE)(access))
        # REMOVE_CASE
        self.assertTrue(CaseAbac._get_has_right_function(CaseRight.REMOVE_CASE)(access))
        # READ_CASE
        self.assertTrue(CaseAbac._get_has_right_function(CaseRight.READ_CASE)(access))
        # WRITE_CASE
        self.assertTrue(CaseAbac._get_has_right_function(CaseRight.WRITE_CASE)(access))
        # ADD_CASE_SET
        self.assertTrue(
            CaseAbac._get_has_right_function(CaseRight.ADD_CASE_SET)(access)
        )
        # REMOVE_CASE_SET
        self.assertTrue(
            CaseAbac._get_has_right_function(CaseRight.REMOVE_CASE_SET)(access)
        )
        # READ_CASE_SET
        self.assertTrue(
            CaseAbac._get_has_right_function(CaseRight.READ_CASE_SET)(access)
        )
        # WRITE_CASE_SET
        self.assertTrue(
            CaseAbac._get_has_right_function(CaseRight.WRITE_CASE_SET)(access)
        )
        # Negative checks for read/write case
        access_empty: CaseTypeAccessAbac = self.make_access(self.dc2)
        self.assertFalse(
            CaseAbac._get_has_right_function(CaseRight.READ_CASE)(access_empty)
        )
        self.assertFalse(
            CaseAbac._get_has_right_function(CaseRight.WRITE_CASE)(access_empty)
        )

    def test_get_get_share_from_data_collections_function_branches(self) -> None:
        share: CaseTypeShareAbac = self.make_share(
            self.dc1,
            add_from={self.dc2},
            remove_from={self.dc3},
            add_set_from={self.dc4},
            remove_set_from={self.dc1},
        )
        self.assertEqual(
            CaseAbac._get_get_share_from_data_collections_function(CaseRight.ADD_CASE)(
                share
            ),
            {self.dc2},
        )
        self.assertEqual(
            CaseAbac._get_get_share_from_data_collections_function(
                CaseRight.REMOVE_CASE
            )(share),
            {self.dc3},
        )
        self.assertEqual(
            CaseAbac._get_get_share_from_data_collections_function(
                CaseRight.ADD_CASE_SET
            )(share),
            {self.dc4},
        )
        self.assertEqual(
            CaseAbac._get_get_share_from_data_collections_function(
                CaseRight.REMOVE_CASE_SET
            )(share),
            {self.dc1},
        )

    def test_get_from_data_collections_for_right_function_branches(self) -> None:
        share: CaseTypeShareAbac = self.make_share(
            self.dc2,
            add_from={self.dc1},
            remove_from={self.dc2},
            add_set_from={self.dc3},
            remove_set_from={self.dc4},
        )
        self.assertEqual(
            CaseAbac._get_from_data_collections_for_right_function(CaseRight.ADD_CASE)(
                share
            ),
            {self.dc1},
        )
        self.assertEqual(
            CaseAbac._get_from_data_collections_for_right_function(
                CaseRight.REMOVE_CASE
            )(share),
            {self.dc2},
        )
        self.assertEqual(
            CaseAbac._get_from_data_collections_for_right_function(
                CaseRight.ADD_CASE_SET
            )(share),
            {self.dc3},
        )
        self.assertEqual(
            CaseAbac._get_from_data_collections_for_right_function(
                CaseRight.REMOVE_CASE_SET
            )(share),
            {self.dc4},
        )
