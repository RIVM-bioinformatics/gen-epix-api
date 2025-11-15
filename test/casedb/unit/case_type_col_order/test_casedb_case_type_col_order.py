from uuid import uuid4

from gen_epix.casedb.domain.model.case import CaseTypeDim, CompleteCaseType


def test_case_type_col_order_derivation() -> None:
    col1, col2, col3, col4 = (uuid4() for _ in range(4))

    dims: list[CaseTypeDim] = [
        CaseTypeDim(
            id=uuid4(), dim_id=uuid4(), rank=1, case_type_col_order=[col1, col2]
        ),
        CaseTypeDim(id=uuid4(), dim_id=uuid4(), rank=2, case_type_col_order=[col3]),
        CaseTypeDim(id=uuid4(), dim_id=uuid4(), rank=3, case_type_col_order=[col4]),
    ]

    complete_case_type = CompleteCaseType(
        name="test",
        etiologies={},
        etiological_agents={},
        dims={},
        cols={},
        case_type_dims=dims,
        case_type_cols={},
        case_type_col_order=[col4, col3, col2, col1],
        genetic_distance_protocols={},
        tree_algorithms={},
        case_type_access_abacs={},
        case_type_share_abacs={},
    )

    assert complete_case_type.case_type_col_order == [col1, col2, col3, col4]
