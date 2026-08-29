from enum import Enum
from uuid import UUID

import pytest

from gen_epix.fastapp import OnException, exc
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation, PermissionType, PermissionTypeSet
from gen_epix.fastapp.model import Command, CrudCommand, Model, Permission


class ServiceType(Enum):
    SVC1 = "SVC1"
    SVC2 = "SVC2"
    SVC3 = "SVC3"


class ModelA(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]
    a_to_b: UUID | None = None


class ModelB(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]


class ModelC(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]
    to_c: UUID | None = None


class NonPersistModel(Model):
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]


class DummyNonCrud(Command):
    NAME = None
    PERMISSION_TYPE_SET = PermissionTypeSet.E


class CrudA(CrudCommand):
    NAME = None
    MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
    PERMISSION_TYPE_SET = PermissionTypeSet.CRUD


class CrudB(CrudCommand):
    NAME = None
    MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
    PERMISSION_TYPE_SET = PermissionTypeSet.CRUD


class BadCrudNoModel(CrudCommand):
    NAME = None
    MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
    PERMISSION_TYPE_SET = PermissionTypeSet.CRUD


class BadCrudNoModel2(CrudCommand):
    NAME = None
    MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
    PERMISSION_TYPE_SET = PermissionTypeSet.CRUD


class BadCrudNoEntity(CrudCommand):
    NAME = None
    MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
    PERMISSION_TYPE_SET = PermissionTypeSet.CRUD


class ModelD(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]
    to_c: UUID | None = None


class ModelE(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]
    to_c: UUID | None = None


class ModelF(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]
    to_c: UUID | None = None


class ModelX(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]
    to_y: UUID | None = None


class ModelY(Model):
    id: UUID
    NAME = None
    ENTITY: Entity | None = None  # type: ignore[misc]
    to_x: UUID | None = None


class CrudX(CrudCommand):
    NAME = None
    MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
    PERMISSION_TYPE_SET = PermissionTypeSet.CRUD


class CrudY(CrudCommand):
    NAME = None
    MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
    PERMISSION_TYPE_SET = PermissionTypeSet.CRUD


class BaseDomainTestCase:
    def setup_method(self) -> None:
        # Domain under test
        self.domain = Domain(name="TEST", description="desc")

        # Service types
        self.svc1 = ServiceType.SVC1
        self.svc2 = ServiceType.SVC2

        # Entities (use real Pydantic models, id is UUID by default)
        self.entity_b = Entity(
            id=UUID("00000000-0000-0000-0000-00000000000b"),
            persistable=True,
            url_name="b",
            database_name="db_b",
            schema_name="schema_b",
            links={},
        )
        self.entity_a = Entity(
            id=UUID("00000000-0000-0000-0000-00000000000a"),
            persistable=True,
            url_name="a",
            database_name="db_a",
            schema_name="schema_a",
            links={1: ("a_to_b", ModelB, None)},  # type: ignore[dict-item]
        )

        # Model linkage
        ModelB.ENTITY = self.entity_b
        ModelA.ENTITY = self.entity_a

        # Links: A -> B (already provided via constructor tuples)
        # self.entity_a.links[1] = Link(link_model_class=ModelB, name="a_to_b")

        # Crud commands model binding
        CrudB.MODEL_CLASS = ModelB
        CrudA.MODEL_CLASS = ModelA

        # Register in order: B first, then A (due to A->B link)
        self.domain.register_command(CrudB, service_type=self.svc2)
        self.domain.register_command(CrudA, service_type=self.svc1)
        self.domain.register_command(DummyNonCrud, service_type=self.svc1)


@pytest.mark.scenario_ids("TC-SEC-28-02")
class TestStaticUtilities:
    def test_get_service_name_variants(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        name_from_str: str = Domain.get_service_name("SVC")
        name_from_enum: str = Domain.get_service_name(ServiceType.SVC1)
        # Verify
        assert name_from_str == "SVC"
        assert name_from_enum == "SVC1"
        with pytest.raises(exc.DomainException):
            Domain.get_service_name(None)

    def test_get_command_and_model_name_and_permissions(self) -> None:
        # Create input
        class XCmd(Command):
            NAME = None
            PERMISSION_TYPE_SET = PermissionTypeSet.E

        class XModel(Model):
            NAME = None
            ENTITY = None

        # Set up mocks
        # Execute
        cmd_name: str = Domain.get_command_name(XCmd)
        model_name: str = Domain.get_model_name(XModel)
        permissions = Domain.get_command_permissions(XCmd)
        # Verify
        assert cmd_name == "XCmd"
        assert model_name == "XModel"
        assert any(x.permission_type == PermissionType.EXECUTE for x in permissions)


@pytest.mark.scenario_ids("TC-SEC-28-02")
class TestRegistrationAndLookups(BaseDomainTestCase):
    def test_properties_and_basic_sets(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        # Verify
        assert self.domain.name == "TEST"
        assert self.domain.description == "desc"
        assert self.svc1 in self.domain.service_types
        assert self.svc2 in self.domain.service_types
        # service_names mapping not populated by Domain; ensure property works
        assert isinstance(self.domain.service_names, frozenset)
        assert len(self.domain.entities) == 2
        assert len(self.domain.models) == 2
        assert CrudA in self.domain.crud_commands
        assert CrudB in self.domain.crud_commands
        assert DummyNonCrud in self.domain.commands
        assert "CrudA" in self.domain.command_names
        assert "CrudB" in self.domain.command_names
        assert "DummyNonCrud" in self.domain.command_names
        assert len(self.domain.permissions) >= 1

    def test_get_commands_include_crud_toggle(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        no_crud = self.domain.get_commands(include_crud=False)
        all_cmds = self.domain.get_commands(include_crud=True)
        no_crud_no_frozen = self.domain.get_commands(include_crud=False, frozen=False)
        all_cmds_no_frozen = self.domain.get_commands(include_crud=True, frozen=False)
        # Verify
        assert DummyNonCrud in no_crud
        assert CrudA not in no_crud
        assert CrudB not in no_crud
        assert CrudA in all_cmds
        assert CrudB in all_cmds
        assert DummyNonCrud in all_cmds
        assert isinstance(no_crud, frozenset)
        assert isinstance(all_cmds, frozenset)
        assert isinstance(no_crud_no_frozen, set)
        assert isinstance(all_cmds_no_frozen, set)

    def test_service_type_entity_and_model_mappings(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        svc_for_ent_a = self.domain.get_service_type_for_entity(
            self.entity_a, verify=True
        )
        svc_for_ent_b = self.domain.get_service_type_for_entity(
            self.entity_b, verify=True
        )
        ents_svc1 = self.domain.get_entities_for_service_type(self.svc1, frozen=True)
        ents_svc2 = self.domain.get_entities_for_service_type(self.svc2, frozen=False)
        svc_for_model_a = self.domain.get_service_type_for_model(ModelA, verify=True)
        svc_for_model_b = self.domain.get_service_type_for_model(ModelB, verify=True)
        models_svc1 = self.domain.get_models_for_service_type(self.svc1, frozen=True)
        models_svc2 = self.domain.get_models_for_service_type(self.svc2, frozen=False)
        # Verify
        assert svc_for_ent_a == self.svc1
        assert svc_for_ent_b == self.svc2
        assert self.entity_a in ents_svc1  # type: ignore[arg-type]
        assert self.entity_b in ents_svc2  # type: ignore[arg-type]
        assert svc_for_model_a == self.svc1
        assert svc_for_model_b == self.svc2
        assert ModelA in models_svc1
        assert ModelB in models_svc2

    def test_command_and_permission_mappings(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        svc_for_cmd_crud_a = self.domain.get_service_type_for_command(CrudA)
        svc_for_cmd_non_crud = self.domain.get_service_type_for_command(DummyNonCrud)
        cmds_svc1 = self.domain.get_commands_for_service_type(self.svc1, frozen=True)
        cmds_svc2 = self.domain.get_commands_for_service_type(self.svc2, frozen=False)
        crud_cmds_svc1 = self.domain.get_crud_commands_for_service_type(
            self.svc1, frozen=True
        )
        crud_cmds_svc2 = self.domain.get_crud_commands_for_service_type(
            self.svc2, frozen=False
        )
        cmd_by_name = self.domain.get_command_for_name("CrudA")
        perms_svc1 = self.domain.get_permissions_for_service_type(
            self.svc1, frozen=True
        )
        perms_domain = self.domain.get_permissions_for_domain(frozen=False)
        perms_for_model_a = self.domain.get_permissions_for_model(ModelA, frozen=False)
        perms_for_cmd_a_all = self.domain.get_permissions_for_command(
            CrudA, frozen=True
        )
        perms_for_cmd_a_read = self.domain.get_permissions_for_command(
            CrudA, frozen=False, permission_type_set=PermissionTypeSet.R
        )
        # Base-class filtering coverage
        cmds_svc1_cmd_base = self.domain.get_commands_for_service_type(
            self.svc1, frozen=True, base_class=Command
        )
        cmds_svc1_crud_base = self.domain.get_commands_for_service_type(
            self.svc1, frozen=False, base_class=CrudCommand
        )
        cmds_svc2_crud_base = self.domain.get_commands_for_service_type(
            self.svc2, frozen=True, base_class=CrudCommand
        )
        crud_cmds_svc1_base = self.domain.get_crud_commands_for_service_type(
            self.svc1, frozen=True, base_class=CrudCommand
        )
        crud_cmds_svc2_base_nf = self.domain.get_crud_commands_for_service_type(
            self.svc2, frozen=False, base_class=CrudCommand
        )

        # Verify
        assert svc_for_cmd_crud_a == self.svc1
        assert svc_for_cmd_non_crud == self.svc1
        assert CrudA in cmds_svc1
        assert DummyNonCrud in cmds_svc1
        assert CrudB in cmds_svc2
        assert CrudA in crud_cmds_svc1
        assert CrudB in crud_cmds_svc2
        assert cmd_by_name is CrudA
        assert perms_svc1.issubset(perms_domain)
        assert set(perms_for_model_a).issubset(perms_svc1)
        assert any(
            x.permission_type == PermissionType.READ for x in perms_for_cmd_a_all
        )
        assert {x.permission_type for x in perms_for_cmd_a_read} == {
            PermissionType.READ
        }
        # Verify base-class filtering results
        assert CrudA in cmds_svc1_cmd_base
        assert DummyNonCrud in cmds_svc1_cmd_base
        assert CrudA in cmds_svc1_crud_base
        assert DummyNonCrud not in cmds_svc1_crud_base
        assert cmds_svc2_crud_base == frozenset({CrudB})
        assert crud_cmds_svc1_base == frozenset({CrudA})
        assert CrudB in crud_cmds_svc2_base_nf
        assert CrudA not in crud_cmds_svc2_base_nf

    def test_model_entity_crud_command_cross_mappings(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        entity_for_model_a = self.domain.get_entity_for_model(ModelA)
        model_for_entity_a = self.domain.get_model_for_entity(self.entity_a)
        entity_for_crud_a = self.domain.get_entity_for_crud_command(CrudA)
        crud_for_entity_a = self.domain.get_crud_command_for_entity(self.entity_a)
        crud_for_model_a = self.domain.get_crud_command_for_model(ModelA)
        model_for_crud_a = self.domain.get_model_for_crud_command(CrudA)
        # Verify
        assert entity_for_model_a == self.entity_a
        assert model_for_entity_a == ModelA
        assert entity_for_crud_a == self.entity_a
        assert crud_for_entity_a == CrudA
        assert crud_for_model_a == CrudA
        assert model_for_crud_a == ModelA

    def test_permission_lookups(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        all_perms = self.domain.get_permissions_for_command(CrudA)
        perm_read = next(
            x for x in all_perms if x.permission_type == PermissionType.READ
        )
        perm_exec = next(iter(self.domain.get_permissions_for_command(DummyNonCrud)))
        svc_for_perm_read = self.domain.get_service_type_for_permission(perm_read)
        model_for_perm_read = self.domain.get_model_for_permission(perm_read)
        # Derive entity via model instead of get_entity_for_permission (not populated by Domain)
        entity_for_perm_read = self.domain.get_entity_for_model(model_for_perm_read)
        cmd_for_perm_read = self.domain.get_command_for_permission(perm_read)
        cmd_for_perm_exec = self.domain.get_command_for_permission(perm_exec)
        perm_by_tuple_class = self.domain.get_permission(CrudA, PermissionType.READ)
        perm_by_tuple_name = self.domain.get_permission("CrudA", PermissionType.READ)
        # Verify
        assert svc_for_perm_read == self.svc1
        assert model_for_perm_read == ModelA
        assert entity_for_perm_read == self.entity_a
        assert cmd_for_perm_read is CrudA
        assert cmd_for_perm_exec is DummyNonCrud
        assert perm_by_tuple_class == perm_read
        assert perm_by_tuple_name == perm_read

    def test_get_permission_for_command_instance(self) -> None:
        # Create input
        crud_instance: CrudCommand = CrudA.model_construct()
        setattr(crud_instance, "operation", CrudOperation.UPDATE_ONE)
        non_crud_instance: Command = DummyNonCrud.model_construct()
        # Set up mocks
        # Execute
        perm_crud = self.domain.get_permission_for_command_instance(crud_instance)
        perm_non_crud = self.domain.get_permission_for_command_instance(
            non_crud_instance
        )
        # Verify
        assert perm_crud.permission_type == PermissionType.UPDATE
        assert perm_non_crud.permission_type == PermissionType.EXECUTE

    def test_model_links_and_filters(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        # Filter by matching remote service with invert=False (should exclude)
        links_same_service = self.domain.get_model_links(
            ModelA, as_tuple=False, service_type=self.svc1, invert=False
        )
        # Filter by different service with invert=True (should include)
        links_diff_service = self.domain.get_model_links(
            ModelA, as_tuple=True, service_type=self.svc1, invert=True
        )
        # Filter by url_name
        links_url_match = self.domain.get_model_links(
            ModelA, as_tuple=False, url_name="b", invert=False
        )
        links_url_invert = self.domain.get_model_links(
            ModelA, as_tuple=False, url_name="b", invert=True
        )
        # Verify
        assert links_same_service == {}
        assert 1 in links_diff_service
        assert 1 in links_url_match
        assert links_url_invert == {}

    def test_dag_sorted_entities_and_models_filters(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        all_ents = self.domain.get_dag_sorted_entities()
        rev_ents = self.domain.get_dag_sorted_entities(reverse=True)
        ents_svc1 = self.domain.get_dag_sorted_entities(service_type=self.svc1)
        ents_not_svc1 = self.domain.get_dag_sorted_entities(
            service_type=self.svc1, invert=True
        )
        ents_url_a = self.domain.get_dag_sorted_entities(url_name="a")
        models_all = self.domain.get_dag_sorted_models()
        models_svc2 = self.domain.get_dag_sorted_models(service_type=self.svc2)
        # Verify
        assert all_ents == [self.entity_b, self.entity_a]  # registration order B then A
        assert rev_ents == [self.entity_a, self.entity_b]
        assert ents_svc1 == [self.entity_a]
        assert ents_not_svc1 == [self.entity_b]
        assert ents_url_a == [self.entity_a]
        assert models_all == [ModelB, ModelA]
        assert models_svc2 == [ModelB]

    def test_model_excluded_permissions_none_when_full_crud(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        excluded = self.domain.get_model_excluded_permissions()
        # Verify
        assert excluded == {}

    def test_register_service_type_and_entity_cycle_handling(self) -> None:
        # Create input
        self.domain.register_service_type(ServiceType.SVC3)
        # New entity with link to unknown model (ModelC is unregistered in the domain)
        entity_c = Entity(
            persistable=True,
            links={1: ("to_c", ModelC, None)},  # type: ignore[dict-item]
        )
        entity_e = Entity(
            persistable=True,
            links={1: ("to_c", ModelE, None)},  # type: ignore[dict-item]
        )
        # Set up mocks
        # Execute + Verify on_cycle default (raise): model_class must differ from link target
        with pytest.raises(exc.DomainException):
            self.domain.register_entity(
                entity_c, service_type=ServiceType.SVC3, model_class=ModelD
            )

        # IGNORE branch
        self.domain.register_entity(
            entity_e,
            service_type=ServiceType.SVC3,
            model_class=ModelF,
            on_cycle=OnException.IGNORE,
        )

        class BrokenEntity(Entity):
            @property
            def model_class(self):  # type: ignore[no-untyped-def]
                return None

            def __hash__(self) -> int:
                return hash(self.id)

        broken_entity = BrokenEntity(persistable=True)
        with pytest.raises(exc.InitializationServiceError):
            self.domain.register_entity(broken_entity, service_type=ServiceType.SVC3)

        dup_entity = Entity(persistable=True)
        with pytest.raises(exc.DomainException):
            self.domain.register_entity(
                dup_entity, service_type=ServiceType.SVC3, model_class=ModelA
            )

    def test_register_command_error_paths(self) -> None:
        # Create input
        # Set up mocks
        # 1) Crud without MODEL_CLASS
        with pytest.raises(exc.DomainException):
            self.domain.register_command(BadCrudNoModel, service_type=self.svc1)

        # Change NAME to assert a already registered with different name
        with pytest.raises(exc.DomainException):
            BadCrudNoModel.NAME = "BadCrudNoModelWrong"  # type: ignore[assignment]
            self.domain.register_command(BadCrudNoModel, service_type=self.svc1)

        # Change MODEL_CLASS to assert a subclass of Crud with no MODEL_CLASS
        with pytest.raises(exc.DomainException):
            BadCrudNoModel.NAME = None  # Restore
            BadCrudNoModel.MODEL_CLASS = None
            self.domain.register_command(BadCrudNoModel, service_type=self.svc1)

        # With not registered Crud class with no MODEL_CLASS
        with pytest.raises(exc.DomainException):
            BadCrudNoModel2.MODEL_CLASS = None
            self.domain.register_command(BadCrudNoModel2, service_type=self.svc1)

        # 2) Crud with MODEL_CLASS but model ENTITY missing
        class TmpModel(Model):
            NAME = None
            ENTITY = None

        BadCrudNoEntity.MODEL_CLASS = TmpModel
        with pytest.raises(exc.DomainException):
            self.domain.register_command(BadCrudNoEntity, service_type=self.svc1)
        # 3) Crud with non-persistable entity
        non_persist_entity = Entity(persistable=False)
        NonPersistModel.ENTITY = non_persist_entity

        class NonPersistCrud(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = NonPersistModel  # type: ignore[assignment, misc]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        with pytest.raises(exc.DomainException):
            self.domain.register_command(NonPersistCrud, service_type=self.svc1)
        # 4) Re-register existing command with different service type
        with pytest.raises(exc.DomainException):
            self.domain.register_command(CrudA, service_type=self.svc2)
        # 5) Re-register existing CrudA after changing MODEL_CLASS
        CrudA.MODEL_CLASS = ModelB
        with pytest.raises(exc.DomainException):
            self.domain.register_command(CrudA, service_type=self.svc1)
        # Restore for other tests (defensive)
        CrudA.MODEL_CLASS = ModelA

    def test_errors_for_unknown_items(self) -> None:
        # Create input
        unk_entity = Entity()

        class UnkModel(Model):
            NAME = None
            ENTITY = None

        class UnkCmd(Command):
            NAME = None
            PERMISSION_TYPE_SET = PermissionTypeSet.E

        unk_perm = Permission(
            command_name="Unknown", permission_type=PermissionType.READ
        )
        # Set up mocks
        # Execute + Verify
        with pytest.raises(exc.DomainException):
            self.domain.get_service_type_for_entity(unk_entity, verify=True)
        with pytest.raises(exc.DomainException):
            self.domain.get_entities_for_service_type(ServiceType.SVC3, verify=True)
        with pytest.raises(exc.DomainException):
            self.domain.get_service_type_for_model(UnkModel, verify=True)
        with pytest.raises(exc.DomainException):
            self.domain.get_models_for_service_type(ServiceType.SVC3)
        with pytest.raises(exc.DomainException):
            self.domain.get_service_type_for_command(UnkCmd)
        with pytest.raises(exc.DomainException):
            self.domain.get_commands_for_service_type(ServiceType.SVC3)
        with pytest.raises(exc.DomainException):
            self.domain.get_crud_commands_for_service_type(ServiceType.SVC3)
        with pytest.raises(exc.DomainException):
            self.domain.get_command_for_name("UnknownCmd")
        with pytest.raises(exc.DomainException):
            self.domain.get_permissions_for_service_type(ServiceType.SVC3)
        with pytest.raises(exc.DomainException):
            self.domain.get_service_type_for_permission(unk_perm)
        with pytest.raises(exc.DomainException):
            self.domain.get_entity_for_model(UnkModel)
        with pytest.raises(exc.DomainException):
            self.domain.get_model_for_entity(unk_entity)
        with pytest.raises(exc.DomainException):
            self.domain.get_entity_for_crud_command(CrudCommand)
        with pytest.raises(exc.DomainException):
            self.domain.get_crud_command_for_entity(unk_entity)
        with pytest.raises(exc.DomainException):
            self.domain.get_entity_for_permission(unk_perm)
        with pytest.raises(exc.DomainException):
            self.domain.get_permissions_for_entity(unk_entity)
        with pytest.raises(exc.DomainException):
            self.domain.get_crud_command_for_model(UnkModel)
        with pytest.raises(exc.DomainException):
            self.domain.get_model_for_crud_command(CrudCommand)
        with pytest.raises(exc.DomainException):
            self.domain.get_model_for_permission(unk_perm)
        with pytest.raises(exc.DomainException):
            self.domain.get_permissions_for_model(UnkModel)
        with pytest.raises(exc.DomainException):
            self.domain.get_permissions_for_command(UnkCmd)
        with pytest.raises(exc.DomainException):
            self.domain.get_permission(UnkCmd, PermissionType.READ)

    def test_get_permissions_filtered_and_frozen_flags(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        perms_frozen = self.domain.get_permissions_for_command(CrudA, frozen=True)
        perms_mutable = self.domain.get_permissions_for_command(CrudA, frozen=False)
        perms_model_filtered = self.domain.get_permissions_for_model(
            ModelA, frozen=False, permission_type_set=PermissionTypeSet.R
        )
        # Verify
        assert isinstance(perms_frozen, frozenset)
        assert isinstance(perms_mutable, set)
        assert {x.permission_type for x in perms_model_filtered} == {
            PermissionType.READ
        }

    def test_get_service_types(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        service_types = self.domain.get_service_types()
        # Verify
        assert isinstance(service_types, set)
        assert self.svc1 in service_types
        assert self.svc2 in service_types
        assert len(service_types) == 2

    def test_register_service_type_idempotency(self) -> None:
        # Create input
        # Set up mocks
        # Execute - calling register twice with same service type
        svc3 = ServiceType.SVC3
        result1 = self.domain.register_service_type(svc3)
        result2 = self.domain.register_service_type(svc3)
        # Verify - idempotent: calling twice should return same type
        assert result1 == svc3
        assert result2 == svc3
        assert svc3 in self.domain.service_types

    def test_get_dag_sorted_service_types(self) -> None:
        # Create input
        # Set up mocks
        # Execute - get DAG sorted service types (basic coverage)
        sorted_types = self.domain.get_dag_sorted_service_types(reverse=False)
        sorted_types_rev = self.domain.get_dag_sorted_service_types(reverse=True)
        # Verify
        assert isinstance(sorted_types, list)
        assert isinstance(sorted_types_rev, list)
        # With A->B link, B should come before A in default order,
        # so svc2 (B) before svc1 (A)
        assert len(sorted_types) == 2
        assert sorted_types[0] == self.svc2
        assert sorted_types[1] == self.svc1
        # Reversed order
        assert sorted_types_rev[0] == self.svc1
        assert sorted_types_rev[1] == self.svc2


@pytest.mark.scenario_ids("TC-SEC-28-02")
class TestDAGAndCycleBehavior:
    """Test topological sorting behavior with on_cycle parameter."""

    def setup_method(self) -> None:
        # Domain under test
        self.domain = Domain(name="TEST_DAG", description="desc")
        self.svc_main = ServiceType.SVC1

        # Entities - linear dependency A -> B (no cycle)
        self.entity_b_dag = Entity(
            id=UUID("00000000-0000-0000-0000-000000000051"),
            persistable=True,
            url_name="b_dag",
            database_name="db_b_dag",
            schema_name="schema_b_dag",
            links={},
        )
        self.entity_a_dag = Entity(
            id=UUID("00000000-0000-0000-0000-000000000050"),
            persistable=True,
            url_name="a_dag",
            database_name="db_a_dag",
            schema_name="schema_a_dag",
            links={1: ("a_to_b", ModelB, None)},  # type: ignore[dict-item]
        )

        # Set up model linkage
        ModelB.ENTITY = self.entity_b_dag
        ModelA.ENTITY = self.entity_a_dag

        # Set up CRUD commands
        CrudB.MODEL_CLASS = ModelB
        CrudA.MODEL_CLASS = ModelA

        # Register: B first, then A (due to A->B link)
        self.domain.register_command(CrudB, service_type=self.svc_main)
        self.domain.register_command(CrudA, service_type=self.svc_main)

    def test_get_dag_sorted_entities_respects_reverse(self) -> None:
        # Create input
        # Set up mocks
        # Execute - get entities in topological order
        sorted_forward = self.domain.get_dag_sorted_entities(reverse=False)
        sorted_backward = self.domain.get_dag_sorted_entities(reverse=True)

        # Verify - with A->B link, B should come first in forward order
        assert sorted_forward == [self.entity_b_dag, self.entity_a_dag]
        assert sorted_backward == [self.entity_a_dag, self.entity_b_dag]

    def test_get_dag_sorted_entities_on_cycle_parameter_accepted(self) -> None:
        # Create input
        # Set up mocks
        # Execute - verify on_cycle parameter is accepted and doesn't error
        # (no actual cycle in this setup, so both should work)
        result_raise = self.domain.get_dag_sorted_entities(on_cycle=OnException.RAISE)
        result_ignore = self.domain.get_dag_sorted_entities(on_cycle=OnException.IGNORE)

        # Verify - both return valid results with no cycles
        assert result_raise == [self.entity_b_dag, self.entity_a_dag]
        assert result_ignore == [self.entity_b_dag, self.entity_a_dag]


@pytest.mark.scenario_ids("TC-SEC-28-02")
class TestServiceTypeDagSorting:
    def test_get_dag_sorted_service_types_handles_non_contiguous_service_blocks(
        self,
    ) -> None:
        class RootS2(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]

        class MidS1(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]
            to_s2: UUID | None = None

        class MidS3(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]
            to_s2: UUID | None = None

        class LeafS1(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]
            to_s3: UUID | None = None

        class CrudRootS2(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        class CrudMidS1(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        class CrudMidS3(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        class CrudLeafS1(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        domain = Domain(name="SERVICE_DAG_NON_CONTIGUOUS")

        root_s2_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000a1"),
            persistable=True,
            links={},
        )
        mid_s1_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000a2"),
            persistable=True,
            links={1: ("to_s2", RootS2, None)},  # type: ignore[dict-item]
        )
        mid_s3_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000a3"),
            persistable=True,
            links={1: ("to_s2", RootS2, None)},  # type: ignore[dict-item]
        )
        leaf_s1_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000a4"),
            persistable=True,
            links={1: ("to_s3", MidS3, None)},  # type: ignore[dict-item]
        )

        RootS2.ENTITY = root_s2_entity
        MidS1.ENTITY = mid_s1_entity
        MidS3.ENTITY = mid_s3_entity
        LeafS1.ENTITY = leaf_s1_entity
        CrudRootS2.MODEL_CLASS = RootS2
        CrudMidS1.MODEL_CLASS = MidS1
        CrudMidS3.MODEL_CLASS = MidS3
        CrudLeafS1.MODEL_CLASS = LeafS1

        domain.register_command(CrudRootS2, service_type=ServiceType.SVC2)
        domain.register_command(CrudMidS1, service_type=ServiceType.SVC1)
        domain.register_command(CrudMidS3, service_type=ServiceType.SVC3)
        domain.register_command(CrudLeafS1, service_type=ServiceType.SVC1)

        sorted_types = domain.get_dag_sorted_service_types(on_cycle=OnException.RAISE)
        assert sorted_types == [ServiceType.SVC2, ServiceType.SVC3, ServiceType.SVC1]

    def test_get_dag_sorted_service_types_raises_on_real_service_cycle(self) -> None:
        class AnchorS1(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]

        class AnchorS2(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]

        class DepS1OnS2(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]
            to_s2: UUID | None = None

        class DepS2OnS1(Model):
            id: UUID
            NAME = None
            ENTITY: Entity | None = None  # type: ignore[misc]
            to_s1: UUID | None = None

        class CrudAnchorS1(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        class CrudAnchorS2(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        class CrudDepS1OnS2(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        class CrudDepS2OnS1(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = None  # type: ignore[misc,assignment]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        domain = Domain(name="SERVICE_DAG_CYCLE")

        anchor_s1_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000b1"),
            persistable=True,
            links={},
        )
        anchor_s2_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000b2"),
            persistable=True,
            links={},
        )
        dep_s1_on_s2_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000b3"),
            persistable=True,
            links={1: ("to_s2", AnchorS2, None)},  # type: ignore[dict-item]
        )
        dep_s2_on_s1_entity = Entity(
            id=UUID("00000000-0000-0000-0000-0000000000b4"),
            persistable=True,
            links={1: ("to_s1", AnchorS1, None)},  # type: ignore[dict-item]
        )

        AnchorS1.ENTITY = anchor_s1_entity
        AnchorS2.ENTITY = anchor_s2_entity
        DepS1OnS2.ENTITY = dep_s1_on_s2_entity
        DepS2OnS1.ENTITY = dep_s2_on_s1_entity
        CrudAnchorS1.MODEL_CLASS = AnchorS1
        CrudAnchorS2.MODEL_CLASS = AnchorS2
        CrudDepS1OnS2.MODEL_CLASS = DepS1OnS2
        CrudDepS2OnS1.MODEL_CLASS = DepS2OnS1

        domain.register_command(CrudAnchorS1, service_type=ServiceType.SVC1)
        domain.register_command(CrudAnchorS2, service_type=ServiceType.SVC2)
        domain.register_command(CrudDepS1OnS2, service_type=ServiceType.SVC1)
        domain.register_command(CrudDepS2OnS1, service_type=ServiceType.SVC2)

        with pytest.raises(exc.DomainException) as context:
            domain.get_dag_sorted_service_types(on_cycle=OnException.RAISE)
        assert context.value.args[0] == "f8b2c94d"


@pytest.mark.scenario_ids("TC-SEC-28-02")
class TestCrudPermissionTypeMapCompleteness(BaseDomainTestCase):
    def test_delete_all_has_permission_type_map_entry(self) -> None:
        """
        LSP-3650 regression: DELETE_ALL is wired into the generated
        DELETE /v1/{entity} endpoint, so a command with this operation is
        dispatched through the PDP permission check. Domain.CRUD_PERMISSION_
        TYPE_MAP lacked an entry for it, causing a KeyError instead of the
        expected DELETE permission check.
        """
        crud_instance: CrudCommand = CrudA.model_construct()
        setattr(crud_instance, "operation", CrudOperation.DELETE_ALL)

        perm = self.domain.get_permission_for_command_instance(crud_instance)

        assert perm.permission_type == PermissionType.DELETE

    def test_permission_type_map_covers_all_generated_endpoint_operations(
        self,
    ) -> None:
        """
        Every CrudOperation that the generic CRUD endpoint generator actually
        wires up to a REST endpoint must have a Domain.CRUD_PERMISSION_TYPE_MAP
        entry, since a real request for that endpoint dispatches a command
        with that operation through the PDP permission check. This is the
        broader invariant behind the DELETE_ALL regression above: it also
        catches the same class of omission for any operation added to
        endpoint generation in the future without a matching map entry.
        """
        from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator

        generated_operations = set(
            CrudEndpointGenerator.CRUD_OPERATION_TO_ENDPOINT_TYPE.keys()
        )
        mapped_operations = set(Domain.CRUD_PERMISSION_TYPE_MAP.keys())

        assert generated_operations.issubset(mapped_operations)
