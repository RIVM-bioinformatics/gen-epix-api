from test.util.mock_compat import Mock, patch
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.model.abac.rights import CaseTypeAccessAbac
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.services.case.base import BaseCaseService
from gen_epix.casedb.services.case.retrieve_complete_case_type import (
    case_service_retrieve_complete_case_type,
)
from gen_epix.commondb.domain.enum import Role
from gen_epix.commondb.domain.model.organization import User
from gen_epix.fastapp import BaseUnitOfWork, CrudOperation

CASE_TYPE_ID = UUID("550e8400-e29b-41d4-a716-446655440001")
DISEASE_ID = UUID("550e8400-e29b-41d4-a716-446655440002")
OTHER_DISEASE_ID = UUID("550e8400-e29b-41d4-a716-446655440003")
AGENT_ID = UUID("550e8400-e29b-41d4-a716-446655440004")
OTHER_AGENT_ID = UUID("550e8400-e29b-41d4-a716-446655440005")
ETIOLOGY_ID = UUID("550e8400-e29b-41d4-a716-446655440006")
OTHER_ETIOLOGY_ID = UUID("550e8400-e29b-41d4-a716-446655440007")
REF_DIM_ID = UUID("550e8400-e29b-41d4-a716-446655440008")
DIM_ID = UUID("550e8400-e29b-41d4-a716-446655440009")
REF_COL_ID = UUID("550e8400-e29b-41d4-a716-446655440010")
COL_ID = UUID("550e8400-e29b-41d4-a716-446655440011")
DATA_COLLECTION_ID = UUID("550e8400-e29b-41d4-a716-446655440012")
OTHER_DATA_COLLECTION_ID = UUID("550e8400-e29b-41d4-a716-446655440013")


class TestRetrieveCompleteCaseType:
    def setup_method(self) -> None:
        self.user = User(
            id=UUID("550e8400-e29b-41d4-a716-446655440014"),
            key="test@example.com",
            email="test@example.com",
            roles={Role.ORG_USER.value},
            organization_id=UUID("550e8400-e29b-41d4-a716-446655440015"),
            is_active=True,
        )
        self.case_type = model.CaseType(
            id=CASE_TYPE_ID,
            name="Test case type",
            disease_id=DISEASE_ID,
        )
        self.etiological_agent = model.EtiologicalAgent(
            id=AGENT_ID, name="Relevant agent", type="virus"
        )
        self.other_etiological_agent = model.EtiologicalAgent(
            id=OTHER_AGENT_ID, name="Other agent", type="bacterium"
        )
        self.etiology = model.Etiology(
            id=ETIOLOGY_ID,
            disease_id=DISEASE_ID,
            etiological_agent_id=AGENT_ID,
            etiological_agent=None,
        )
        self.other_etiology = model.Etiology(
            id=OTHER_ETIOLOGY_ID,
            disease_id=OTHER_DISEASE_ID,
            etiological_agent_id=OTHER_AGENT_ID,
            etiological_agent=None,
        )
        self.ref_dim = model.RefDim(
            id=REF_DIM_ID,
            dim_type=enum.DimType.TIME,
            code="Case date",
            label="Case date",
        )
        self.dim = model.Dim(
            id=DIM_ID,
            case_type_id=CASE_TYPE_ID,
            ref_dim_id=REF_DIM_ID,
            code="Case date",
            rank=1,
            is_case_date_dim=True,
        )
        self.ref_col = model.RefCol(
            id=REF_COL_ID,
            ref_dim_id=REF_DIM_ID,
            code="date",
            col_type=enum.ColType.TIME_DAY,
        )
        self.col = model.Col(
            id=COL_ID,
            case_type_id=CASE_TYPE_ID,
            dim_id=DIM_ID,
            ref_col_id=REF_COL_ID,
            code="Case date.date",
            rank=1,
            tree_algorithm_codes={enum.TreeAlgorithmType.NJ},
        )
        self.used_tree_algorithm = model.TreeAlgorithm(
            id=UUID("550e8400-e29b-41d4-a716-446655440016"),
            tree_algorithm_class_id=UUID("550e8400-e29b-41d4-a716-446655440017"),
            seqdb_tree_algorithm_id=UUID("550e8400-e29b-41d4-a716-446655440018"),
            code=enum.TreeAlgorithmType.NJ,
            name="Neighbor joining",
            is_ultrametric=False,
        )
        self.unused_tree_algorithm = model.TreeAlgorithm(
            id=UUID("550e8400-e29b-41d4-a716-446655440019"),
            tree_algorithm_class_id=UUID("550e8400-e29b-41d4-a716-446655440020"),
            seqdb_tree_algorithm_id=UUID("550e8400-e29b-41d4-a716-446655440021"),
            code=enum.TreeAlgorithmType.UPGMA,
            name="UPGMA",
            is_ultrametric=True,
        )
        self.repository = Mock()
        self.uow = Mock(spec=BaseUnitOfWork)
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.repository.uow.return_value = self.uow
        self.repository.crud.side_effect = self.repository_crud
        self.service = Mock(spec=BaseCaseService)
        self.service.repository = self.repository
        self.service.app = Mock()
        self.service.app.handle.side_effect = self.app_handle

    def repository_crud(
        self,
        _uow: Any,
        _user_id: Any,
        entity: type,
        operation: CrudOperation,
        **kwargs: Any,
    ) -> Any:
        if entity is model.CaseType:
            return self.case_type
        if entity is model.Col and operation is CrudOperation.READ_ALL:
            return {COL_ID}
        if entity is model.Col:
            return [self.col]
        if entity is model.Dim:
            return [self.dim]
        if entity is model.RefCol:
            return [self.ref_col]
        if entity is model.RefDim:
            return [self.ref_dim]
        raise AssertionError(f"Unexpected repository CRUD: {entity}, {operation}")

    def app_handle(self, cmd: Any) -> Any:
        if isinstance(cmd, command.EtiologyCrudCommand):
            return [self.etiology, self.other_etiology]
        if isinstance(cmd, command.EtiologicalAgentCrudCommand):
            return [self.etiological_agent]
        if isinstance(cmd, command.TreeAlgorithmCrudCommand):
            return [self.used_tree_algorithm, self.unused_tree_algorithm]
        if isinstance(cmd, command.GeneticDistanceProtocolCrudCommand):
            return []
        if isinstance(cmd, command.DataCollectionCrudCommand):
            return [DATA_COLLECTION_ID, OTHER_DATA_COLLECTION_ID]
        raise AssertionError(f"Unexpected application command: {type(cmd)}")

    def create_command(
        self, user: User | None = None
    ) -> command.RetrieveCompleteCaseTypeCommand:
        return command.RetrieveCompleteCaseTypeCommand(
            user=user,
            case_type_id=CASE_TYPE_ID,
        )

    def create_access_abac(self) -> CaseTypeAccessAbac:
        return CaseTypeAccessAbac(
            case_type_id=CASE_TYPE_ID,
            data_collection_id=DATA_COLLECTION_ID,
            is_private=False,
            add_case=True,
            remove_case=False,
            add_case_set=False,
            remove_case_set=False,
            read_col_ids={COL_ID},
            write_col_ids=set(),
            read_case_set=True,
            write_case_set=False,
        )

    def retrieve(
        self, user: User | None, case_abac: model.CaseAbac
    ) -> model.CompleteCaseType:
        cmd = self.create_command(user)
        with patch.object(
            BaseCaseAbacPolicy,
            "get_case_abac_from_command",
            return_value=case_abac,
        ):
            return case_service_retrieve_complete_case_type(self.service, cmd)

    def test_non_full_access_characterizes_complete_case_type(self) -> None:
        access = self.create_access_abac()
        result = self.retrieve(
            self.user,
            model.CaseAbac(
                is_full_access=False,
                case_type_access_abacs={CASE_TYPE_ID: {DATA_COLLECTION_ID: access}},
                case_type_share_abacs={},
            ),
        )

        assert result.id == CASE_TYPE_ID
        assert result.user_id == self.user.id
        assert result.etiologies == {ETIOLOGY_ID: self.etiology}
        assert result.etiological_agents == {AGENT_ID: self.etiological_agent}
        assert result.tree_algorithms == {
            enum.TreeAlgorithmType.NJ: self.used_tree_algorithm
        }
        assert result.case_type_access_abacs == {DATA_COLLECTION_ID: access}
        assert result.case_type_share_abacs == {}
        assert result.case_date_dim_id == DIM_ID
        assert result.case_date_col_type_map == {enum.ColType.TIME_DAY: COL_ID}
        assert result.ordered_dim_ids == [DIM_ID]
        assert result.ordered_col_ids == [COL_ID]
        assert result.ordered_col_ids_by_dim == {DIM_ID: [COL_ID]}

    def test_full_access_characterizes_generated_access_and_exclusions(self) -> None:
        result = self.retrieve(
            self.user,
            model.CaseAbac(
                is_full_access=True,
                case_type_access_abacs={},
                case_type_share_abacs={},
            ),
        )

        expected_access = {
            data_collection_id: CaseTypeAccessAbac(
                case_type_id=CASE_TYPE_ID,
                data_collection_id=data_collection_id,
                is_private=True,
                add_case=True,
                remove_case=True,
                read_col_ids={COL_ID},
                write_col_ids={COL_ID},
                add_case_set=True,
                remove_case_set=True,
                read_case_set=True,
                write_case_set=True,
            )
            for data_collection_id in (DATA_COLLECTION_ID, OTHER_DATA_COLLECTION_ID)
        }
        assert result.case_type_access_abacs == expected_access
        assert result.etiologies == {ETIOLOGY_ID: self.etiology}
        assert result.tree_algorithms == {
            enum.TreeAlgorithmType.NJ: self.used_tree_algorithm
        }
        assert result.case_date_dim_id == DIM_ID
        assert OTHER_ETIOLOGY_ID not in result.etiologies
        assert enum.TreeAlgorithmType.UPGMA not in result.tree_algorithms
