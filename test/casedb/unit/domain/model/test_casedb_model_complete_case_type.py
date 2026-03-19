from uuid import uuid4

import pytest

from gen_epix.casedb.domain import enum, model


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestModelCompleteCaseType:
    def test_dim_col_order(self) -> None:
        case_type_id = uuid4()

        ref_dims: list[model.RefDim] = [
            model.RefDim(
                id=uuid4(), code="dim1", label="dim1", dim_type=enum.DimType.TEXT
            ),
            model.RefDim(
                id=uuid4(), code="dim2", label="dim2", dim_type=enum.DimType.TEXT
            ),
            model.RefDim(
                id=uuid4(), code="dim3", label="dim3", dim_type=enum.DimType.TEXT
            ),
        ]

        dims: list[model.Dim] = [
            model.Dim(
                id=uuid4(),
                ref_dim_id=ref_dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="D",
                rank=1,
                occurrence=2,
            ),
            model.Dim(
                id=uuid4(),
                ref_dim_id=ref_dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="C",
                rank=2,
                occurrence=1,
            ),
            model.Dim(
                id=uuid4(),
                ref_dim_id=ref_dims[2].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="B",
                rank=2,
                occurrence=0,
            ),
            model.Dim(
                id=uuid4(),
                ref_dim_id=ref_dims[1].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="A",
                rank=1,
                occurrence=0,
            ),
        ]
        ordered_dim_ids = [dims[x].id for x in [3, 2, 1, 0]]

        cols: list[model.Col] = [
            model.Col(
                id=uuid4(),
                ref_col_id=uuid4(),
                dim_id=dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="D.B",
                rank=2,
            ),
            model.Col(
                id=uuid4(),
                ref_col_id=uuid4(),
                dim_id=dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="D.A",
                rank=1,
            ),
            model.Col(
                id=uuid4(),
                ref_col_id=uuid4(),
                dim_id=dims[1].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="C.A",
                rank=1,
            ),
            model.Col(
                id=uuid4(),
                ref_col_id=uuid4(),
                dim_id=dims[2].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="B.A",
                rank=1,
            ),
            model.Col(
                id=uuid4(),
                ref_col_id=uuid4(),
                dim_id=dims[3].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="A.A",
                rank=1,
            ),
        ]
        ordered_col_ids = [cols[x].id for x in [4, 3, 2, 1, 0]]

        complete_case_type = model.CompleteCaseType(
            user_id=uuid4(),
            name="test",
            etiologies={},
            etiological_agents={},
            ref_dims={},
            ref_cols={},
            dims={x.id: x for x in dims if x.id is not None},
            cols={x.id: x for x in cols if x.id is not None},
            protocols={},
            tree_algorithms={},
            case_type_access_abacs={},
            case_type_share_abacs={},
            create_max_n_cases=1000,
            read_max_n_cases=1000,
            read_max_tree_size=1000,
            update_max_n_cases=1000,
            delete_max_n_cases=1000,
            case_date_dim_id=None,
            ordered_dim_ids=[x.id for x in dims if x.id is not None],
        )

        assert ordered_dim_ids == complete_case_type.ordered_dim_ids
        assert ordered_col_ids == complete_case_type.ordered_col_ids
