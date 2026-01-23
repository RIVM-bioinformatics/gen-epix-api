from uuid import uuid4

from gen_epix.casedb.domain import enum, model
import pytest


@pytest.mark.scenario_ids("TC-SEC-29-01")
class TestModelCompleteCaseType:
    def test_case_type_dim_col_order(self) -> None:
        case_type_id = uuid4()

        dims: list[model.Dim] = [
            model.Dim(
                id=uuid4(), code="dim1", label="dim1", dim_type=enum.DimType.TEXT
            ),
            model.Dim(
                id=uuid4(), code="dim2", label="dim2", dim_type=enum.DimType.TEXT
            ),
            model.Dim(
                id=uuid4(), code="dim3", label="dim3", dim_type=enum.DimType.TEXT
            ),
        ]

        case_type_dims: list[model.CaseTypeDim] = [
            model.CaseTypeDim(
                id=uuid4(),
                dim_id=dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="D",
                rank=1,
                occurrence=2,
            ),
            model.CaseTypeDim(
                id=uuid4(),
                dim_id=dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="C",
                rank=2,
                occurrence=1,
            ),
            model.CaseTypeDim(
                id=uuid4(),
                dim_id=dims[2].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="B",
                rank=2,
                occurrence=0,
            ),
            model.CaseTypeDim(
                id=uuid4(),
                dim_id=dims[1].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="A",
                rank=1,
                occurrence=0,
            ),
        ]
        ordered_case_type_dim_ids = [case_type_dims[x].id for x in [3, 2, 1, 0]]

        case_type_cols: list[model.CaseTypeCol] = [
            model.CaseTypeCol(
                id=uuid4(),
                col_id=uuid4(),
                case_type_dim_id=case_type_dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="D.B",
                rank=2,
            ),
            model.CaseTypeCol(
                id=uuid4(),
                col_id=uuid4(),
                case_type_dim_id=case_type_dims[0].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="D.A",
                rank=1,
            ),
            model.CaseTypeCol(
                id=uuid4(),
                col_id=uuid4(),
                case_type_dim_id=case_type_dims[1].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="C.A",
                rank=1,
            ),
            model.CaseTypeCol(
                id=uuid4(),
                col_id=uuid4(),
                case_type_dim_id=case_type_dims[2].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="B.A",
                rank=1,
            ),
            model.CaseTypeCol(
                id=uuid4(),
                col_id=uuid4(),
                case_type_dim_id=case_type_dims[3].id,  # type: ignore[arg-type]
                case_type_id=case_type_id,
                code="A.A",
                rank=1,
            ),
        ]
        ordered_case_type_col_ids = [case_type_cols[x].id for x in [4, 3, 2, 1, 0]]

        complete_case_type = model.CompleteCaseType(
            name="test",
            etiologies={},
            etiological_agents={},
            dims={},
            cols={},
            case_type_dims={x.id: x for x in case_type_dims if x.id is not None},
            case_type_cols={x.id: x for x in case_type_cols if x.id is not None},
            genetic_distance_protocols={},
            tree_algorithms={},
            case_type_access_abacs={},
            case_type_share_abacs={},
            create_max_n_cases=1000,
            read_max_n_cases=1000,
            read_max_tree_size=1000,
            update_max_n_cases=1000,
            delete_max_n_cases=1000,
            case_date_case_type_dim_id=None,
            ordered_case_type_dim_ids=[
                x.id for x in case_type_dims if x.id is not None
            ],
        )

        assert ordered_case_type_dim_ids == complete_case_type.ordered_case_type_dim_ids
        assert ordered_case_type_col_ids == complete_case_type.ordered_case_type_col_ids
