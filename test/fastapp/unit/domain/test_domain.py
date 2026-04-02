from enum import Enum
from unittest import TestCase
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


class BaseDomainTestCase(TestCase):
    def setUp(self) -> None:
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
class TestStaticUtilities(TestCase):
    def test_get_service_name_variants(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        name_from_str: str = Domain.get_service_name("SVC")
        name_from_enum: str = Domain.get_service_name(ServiceType.SVC1)
        # Verify
        self.assertEqual(name_from_str, "SVC")
        self.assertEqual(name_from_enum, "SVC1")
        with self.assertRaises(exc.DomainException):
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
        self.assertEqual(cmd_name, "XCmd")
        self.assertEqual(model_name, "XModel")
        self.assertTrue(
            any(x.permission_type == PermissionType.EXECUTE for x in permissions)
        )


@pytest.mark.scenario_ids("TC-SEC-28-02")
class TestRegistrationAndLookups(BaseDomainTestCase):
    def test_properties_and_basic_sets(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        # Verify
        self.assertEqual(self.domain.name, "TEST")
        self.assertEqual(self.domain.description, "desc")
        self.assertIn(self.svc1, self.domain.service_types)
        self.assertIn(self.svc2, self.domain.service_types)
        # service_names mapping not populated by Domain; ensure property works
        self.assertIsInstance(self.domain.service_names, frozenset)
        self.assertEqual(len(self.domain.entities), 2)
        self.assertEqual(len(self.domain.models), 2)
        self.assertIn(CrudA, self.domain.crud_commands)
        self.assertIn(CrudB, self.domain.crud_commands)
        self.assertIn(DummyNonCrud, self.domain.commands)
        self.assertIn("CrudA", self.domain.command_names)
        self.assertIn("CrudB", self.domain.command_names)
        self.assertIn("DummyNonCrud", self.domain.command_names)
        self.assertGreaterEqual(len(self.domain.permissions), 1)

    def test_get_commands_include_crud_toggle(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        no_crud = self.domain.get_commands(include_crud=False)
        all_cmds = self.domain.get_commands(include_crud=True)
        no_crud_no_frozen = self.domain.get_commands(include_crud=False, frozen=False)
        all_cmds_no_frozen = self.domain.get_commands(include_crud=True, frozen=False)
        # Verify
        self.assertIn(DummyNonCrud, no_crud)
        self.assertNotIn(CrudA, no_crud)
        self.assertNotIn(CrudB, no_crud)
        self.assertIn(CrudA, all_cmds)
        self.assertIn(CrudB, all_cmds)
        self.assertIn(DummyNonCrud, all_cmds)
        self.assertIsInstance(no_crud, frozenset)
        self.assertIsInstance(all_cmds, frozenset)
        self.assertIsInstance(no_crud_no_frozen, set)
        self.assertIsInstance(all_cmds_no_frozen, set)

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
        self.assertEqual(svc_for_ent_a, self.svc1)
        self.assertEqual(svc_for_ent_b, self.svc2)
        self.assertIn(self.entity_a, ents_svc1)  # type: ignore[arg-type]
        self.assertIn(self.entity_b, ents_svc2)  # type: ignore[arg-type]
        self.assertEqual(svc_for_model_a, self.svc1)
        self.assertEqual(svc_for_model_b, self.svc2)
        self.assertIn(ModelA, models_svc1)
        self.assertIn(ModelB, models_svc2)

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
        self.assertEqual(svc_for_cmd_crud_a, self.svc1)
        self.assertEqual(svc_for_cmd_non_crud, self.svc1)
        self.assertIn(CrudA, cmds_svc1)
        self.assertIn(DummyNonCrud, cmds_svc1)
        self.assertIn(CrudB, cmds_svc2)
        self.assertIn(CrudA, crud_cmds_svc1)
        self.assertIn(CrudB, crud_cmds_svc2)
        self.assertIs(cmd_by_name, CrudA)
        self.assertTrue(perms_svc1.issubset(perms_domain))
        self.assertTrue(set(perms_for_model_a).issubset(perms_svc1))
        self.assertTrue(
            any(x.permission_type == PermissionType.READ for x in perms_for_cmd_a_all)
        )
        self.assertEqual(
            {x.permission_type for x in perms_for_cmd_a_read}, {PermissionType.READ}
        )
        # Verify base-class filtering results
        self.assertIn(CrudA, cmds_svc1_cmd_base)
        self.assertIn(DummyNonCrud, cmds_svc1_cmd_base)
        self.assertIn(CrudA, cmds_svc1_crud_base)
        self.assertNotIn(DummyNonCrud, cmds_svc1_crud_base)
        self.assertEqual(cmds_svc2_crud_base, frozenset({CrudB}))
        self.assertEqual(crud_cmds_svc1_base, frozenset({CrudA}))
        self.assertIn(CrudB, crud_cmds_svc2_base_nf)
        self.assertNotIn(CrudA, crud_cmds_svc2_base_nf)

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
        self.assertEqual(entity_for_model_a, self.entity_a)
        self.assertEqual(model_for_entity_a, ModelA)
        self.assertEqual(entity_for_crud_a, self.entity_a)
        self.assertEqual(crud_for_entity_a, CrudA)
        self.assertEqual(crud_for_model_a, CrudA)
        self.assertEqual(model_for_crud_a, ModelA)

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
        self.assertEqual(svc_for_perm_read, self.svc1)
        self.assertEqual(model_for_perm_read, ModelA)
        self.assertEqual(entity_for_perm_read, self.entity_a)
        self.assertIs(cmd_for_perm_read, CrudA)
        self.assertIs(cmd_for_perm_exec, DummyNonCrud)
        self.assertEqual(perm_by_tuple_class, perm_read)
        self.assertEqual(perm_by_tuple_name, perm_read)

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
        self.assertEqual(perm_crud.permission_type, PermissionType.UPDATE)
        self.assertEqual(perm_non_crud.permission_type, PermissionType.EXECUTE)

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
        self.assertEqual(links_same_service, {})
        self.assertIn(1, links_diff_service)
        self.assertIn(1, links_url_match)
        self.assertEqual(links_url_invert, {})

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
        self.assertEqual(
            all_ents, [self.entity_b, self.entity_a]
        )  # registration order B then A
        self.assertEqual(rev_ents, [self.entity_a, self.entity_b])
        self.assertEqual(ents_svc1, [self.entity_a])
        self.assertEqual(ents_not_svc1, [self.entity_b])
        self.assertEqual(ents_url_a, [self.entity_a])
        self.assertEqual(models_all, [ModelB, ModelA])
        self.assertEqual(models_svc2, [ModelB])

    def test_model_excluded_permissions_none_when_full_crud(self) -> None:
        # Create input
        # Set up mocks
        # Execute
        excluded = self.domain.get_model_excluded_permissions()
        # Verify
        self.assertEqual(excluded, {})

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
        with self.assertRaises(exc.DomainException):
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
        with self.assertRaises(exc.InitializationServiceError):
            self.domain.register_entity(broken_entity, service_type=ServiceType.SVC3)

        dup_entity = Entity(persistable=True)
        with self.assertRaises(exc.DomainException):
            self.domain.register_entity(
                dup_entity, service_type=ServiceType.SVC3, model_class=ModelA
            )

    def test_register_command_error_paths(self) -> None:
        # Create input
        # Set up mocks
        # 1) Crud without MODEL_CLASS
        with self.assertRaises(exc.DomainException):
            self.domain.register_command(BadCrudNoModel, service_type=self.svc1)

        # Change NAME to assert a already registered with different name
        with self.assertRaises(exc.DomainException):
            BadCrudNoModel.NAME = "BadCrudNoModelWrong"  # type: ignore[assignment]
            self.domain.register_command(BadCrudNoModel, service_type=self.svc1)

        # Change MODEL_CLASS to assert a subclass of Crud with no MODEL_CLASS
        with self.assertRaises(exc.DomainException):
            BadCrudNoModel.NAME = None  # Restore
            BadCrudNoModel.MODEL_CLASS = None
            self.domain.register_command(BadCrudNoModel, service_type=self.svc1)

        # With not registered Crud class with no MODEL_CLASS
        with self.assertRaises(exc.DomainException):
            BadCrudNoModel2.MODEL_CLASS = None
            self.domain.register_command(BadCrudNoModel2, service_type=self.svc1)

        # 2) Crud with MODEL_CLASS but model ENTITY missing
        class TmpModel(Model):
            NAME = None
            ENTITY = None

        BadCrudNoEntity.MODEL_CLASS = TmpModel
        with self.assertRaises(exc.DomainException):
            self.domain.register_command(BadCrudNoEntity, service_type=self.svc1)
        # 3) Crud with non-persistable entity
        non_persist_entity = Entity(persistable=False)
        NonPersistModel.ENTITY = non_persist_entity

        class NonPersistCrud(CrudCommand):
            NAME = None
            MODEL_CLASS: type[Model] | None = NonPersistModel  # type: ignore[assignment, misc]
            PERMISSION_TYPE_SET = PermissionTypeSet.CRUD

        with self.assertRaises(exc.DomainException):
            self.domain.register_command(NonPersistCrud, service_type=self.svc1)
        # 4) Re-register existing command with different service type
        with self.assertRaises(exc.DomainException):
            self.domain.register_command(CrudA, service_type=self.svc2)
        # 5) Re-register existing CrudA after changing MODEL_CLASS
        CrudA.MODEL_CLASS = ModelB
        with self.assertRaises(exc.DomainException):
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
        with self.assertRaises(exc.DomainException):
            self.domain.get_service_type_for_entity(unk_entity, verify=True)
        with self.assertRaises(exc.DomainException):
            self.domain.get_entities_for_service_type(ServiceType.SVC3, verify=True)
        with self.assertRaises(exc.DomainException):
            self.domain.get_service_type_for_model(UnkModel, verify=True)
        with self.assertRaises(exc.DomainException):
            self.domain.get_models_for_service_type(ServiceType.SVC3)
        with self.assertRaises(exc.DomainException):
            self.domain.get_service_type_for_command(UnkCmd)
        with self.assertRaises(exc.DomainException):
            self.domain.get_commands_for_service_type(ServiceType.SVC3)
        with self.assertRaises(exc.DomainException):
            self.domain.get_crud_commands_for_service_type(ServiceType.SVC3)
        with self.assertRaises(exc.DomainException):
            self.domain.get_command_for_name("UnknownCmd")
        with self.assertRaises(exc.DomainException):
            self.domain.get_permissions_for_service_type(ServiceType.SVC3)
        with self.assertRaises(exc.DomainException):
            self.domain.get_service_type_for_permission(unk_perm)
        with self.assertRaises(exc.DomainException):
            self.domain.get_entity_for_model(UnkModel)
        with self.assertRaises(exc.DomainException):
            self.domain.get_model_for_entity(unk_entity)
        with self.assertRaises(exc.DomainException):
            self.domain.get_entity_for_crud_command(CrudCommand)
        with self.assertRaises(exc.DomainException):
            self.domain.get_crud_command_for_entity(unk_entity)
        with self.assertRaises(exc.DomainException):
            self.domain.get_entity_for_permission(unk_perm)
        with self.assertRaises(exc.DomainException):
            self.domain.get_permissions_for_entity(unk_entity)
        with self.assertRaises(exc.DomainException):
            self.domain.get_crud_command_for_model(UnkModel)
        with self.assertRaises(exc.DomainException):
            self.domain.get_model_for_crud_command(CrudCommand)
        with self.assertRaises(exc.DomainException):
            self.domain.get_model_for_permission(unk_perm)
        with self.assertRaises(exc.DomainException):
            self.domain.get_permissions_for_model(UnkModel)
        with self.assertRaises(exc.DomainException):
            self.domain.get_permissions_for_command(UnkCmd)
        with self.assertRaises(exc.DomainException):
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
        self.assertIsInstance(perms_frozen, frozenset)
        self.assertIsInstance(perms_mutable, set)
        self.assertEqual(
            {x.permission_type for x in perms_model_filtered}, {PermissionType.READ}
        )
