from uuid import uuid4

from gen_epix.casedb.domain.model.case import CaseTypeDim, CompleteCaseType


class TestCaseTypeColOrder:
    def test_case_type_col_order_derivation(self) -> None:
        col1, col2, col3, col4 = (uuid4() for _ in range(4))

        dims: list[CaseTypeDim] = [
            CaseTypeDim(
                id=uuid4(), dim_id=uuid4(), case_type_id=uuid4(), code="A", rank=1
            ),
            CaseTypeDim(
                id=uuid4(), dim_id=uuid4(), case_type_id=uuid4(), code="B", rank=2
            ),
            CaseTypeDim(
                id=uuid4(), dim_id=uuid4(), case_type_id=uuid4(), code="C", rank=3
            ),
        ]

        complete_case_type = CompleteCaseType(
            name="test",
            etiologies={},
            etiological_agents={},
            dims={},
            cols={},
            case_type_dims={x.id: x for x in dims if x.id is not None},
            case_type_cols={},
            ordered_case_type_col_ids=[col4, col3, col2, col1],
            genetic_distance_protocols={},
            tree_algorithms={},
            case_type_access_abacs={},
            case_type_share_abacs={},
            create_max_n_cases=1000,
            read_max_n_cases=1000,
            read_max_tree_size=1000,
            update_max_n_cases=1000,
            delete_max_n_cases=1000,
            stats_geo_case_type_dim_id=None,
            stats_time_case_type_dim_id=None,
            ordered_case_type_dim_ids=[x.id for x in dims if x.id is not None],
        )

        # TODO: Fix model validator of CompleteCaseType @model_validator(mode="after")

        assert complete_case_type.ordered_case_type_col_ids == [col1, col2, col3, col4]
