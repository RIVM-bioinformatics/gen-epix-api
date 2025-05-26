import datetime
import logging
import os
import re
import shutil
from enum import Enum
from test.test_client.endpoint_test_client import EndpointTestClient, EndpointVersion
from test.test_client.enum import RepositoryType, TestType
from test.test_client.util import get_test_name, get_test_output_dir, set_log_level
from time import sleep
from typing import Any, Hashable, Type, TypeVar
from uuid import UUID

from gen_epix.fastapp import Command, CrudOperation, Model, User
from util.cfg import BaseAppCfg
from util.env import BaseAppEnv

BASE_MODEL_TYPE = TypeVar("T", bound=Model)


class ServiceTestClient:
    TEST_CLIENTS: dict[Hashable, Any] = {}

    MODEL_KEY_MAP: dict[Type[Model], Hashable] = {}

    def __init__(
        self,
        app_env: BaseAppEnv,
        app_cfg: BaseAppCfg,
        test_type: TestType = TestType.UNDEFINED,
        test_name: str | None = None,
        test_dir: str | None = None,
        repository_type: Hashable | None = RepositoryType.DICT,
        load_target: str | None = None,
        roles: set | Enum | None = None,
        role_hierarchy: dict[Hashable, set] | None = None,
        user_class: Type[User] = User,
        verbose: bool = False,
        log_level: int = logging.ERROR,
        **kwargs: dict,
    ):
        # Set provided parameters
        self.app_cfg = app_cfg
        self.app_env = app_env
        self.test_type = test_type
        self.test_name: str = test_name or get_test_name(test_type)
        self.test_dir: str = test_dir or get_test_output_dir(self.test_name)
        self.repository_type = (
            RepositoryType(repository_type.value)
            if isinstance(repository_type, Enum)
            else repository_type
        )
        self.load_target = load_target
        self.roles: set = set() if roles is None else roles
        self.role_hierarchy: dict[Hashable, set] = (
            {} if role_hierarchy is None else role_hierarchy
        )
        self.user_class = user_class
        self.log_level = log_level
        self.verbose = verbose

        # Set log level
        ServiceTestClient._set_log_level(app_cfg, log_level)

        # Set additional parameters
        self.app = self.app_env.app
        self.cfg = self.app_cfg.cfg
        self.services = self.app_env.services
        self.repositories = self.app_env.repositories
        self.db: dict[Hashable, Model] = {}
        self.props: dict = {}
        self.use_endpoints: bool = kwargs.get("use_endpoints", False)
        self.endpoint_test_client: EndpointTestClient | None = kwargs.get(
            "endpoint_test_client"
        )
        self.app_last_handled_exception: dict | None = kwargs.get(
            "app_last_handled_exception"
        )
        if self.use_endpoints:
            if not self.endpoint_test_client:
                raise ValueError(
                    "Endpoint test client not provided while use_endpoints=True"
                )
            if not self.app_last_handled_exception:
                raise ValueError(
                    "App last handled exception not provided while use_endpoints=True"
                )

    def generate_id(self) -> UUID:
        return self.app.generate_id()

    def handle(
        self,
        cmd: Command,
        return_response: bool = False,
        endpoint_version: EndpointVersion = EndpointVersion.V1,
        use_endpoint: bool | None = None,
        **kwargs: dict,
    ) -> Any:
        use_endpoint = use_endpoint if use_endpoint is not None else self.use_endpoints
        if use_endpoint:
            previous_exception_id = self.app_last_handled_exception["id"]
            retval, response = self.endpoint_test_client.handle(
                cmd,
                return_response=True,
                endpoint_version=endpoint_version,
                **kwargs,
            )

            # Check if an exception was raised before generating the HTTP response, and
            # if so, raise it
            exception_id = self.app_last_handled_exception["id"]
            if exception_id != previous_exception_id:
                exception = self.app_last_handled_exception["exception"]
                raise exception

            if return_response:
                return retval, response
            return retval

        else:
            return self.app.handle(cmd)

    def _update_object_properties(
        self,
        obj: Model,
        props: dict[str, Any | None],
        set_dummy_link: dict[str, bool] | bool = False,
        exclude_none: bool = True,
    ) -> None:
        """
        Helper function for update methods. All the (field_name, value) pairs in props
        are set as attributes of obj. If the field_name is a relationship field, the value
        is set as the id of the linked object. If set_dummy_link is provided for a
        relationship field and no real linked obj is provided, a dummy id is put instead.
        If exclude_none is True, fields or link fields with value None are not set.
        """
        # Parse input
        model_class = obj.__class__
        id_field_name = model_class.ENTITY.id_field_name
        link_map: dict[str, tuple[str, Type[Model]]] = {
            x.relationship_field_name: (x.link_field_name, x.link_model_class)
            for x in model_class.ENTITY.links.values()
        }
        default_set_dummy_link = False
        if isinstance(set_dummy_link, bool):
            default_set_dummy_link = set_dummy_link
            set_dummy_link = {}

        # Set value fields and any links
        for field_name, value in props.items():
            if field_name in link_map:
                field_name, link_model_class = link_map[field_name]
                if not value:
                    if set_dummy_link.get(field_name, default_set_dummy_link):
                        value = self.generate_id()
                    else:
                        value = None
                else:
                    if set_dummy_link.get(field_name, default_set_dummy_link):
                        raise ValueError(
                            f"{model_class.__name__} given and set dummy link True"
                        )
                    value = getattr(
                        self._get_obj(link_model_class, value), id_field_name
                    )
            if exclude_none and value is None:
                continue
            setattr(obj, field_name, value)

    def update_object(
        self,
        user: str | User,
        model_class: Type[Model],
        obj: Model | str,
        props: dict[str, Any | None],
        set_dummy_link: dict[str, bool] | bool = False,
        exclude_none: bool = True,
    ) -> Model:
        user: self.user_class = self._get_obj(self.user_class, user)
        obj: Model = self._get_obj(model_class, obj, copy=True)
        self._update_object_properties(
            obj, props, set_dummy_link, exclude_none=exclude_none
        )
        sleep(0.000000001)
        updated_obj = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user,
                operation=CrudOperation.UPDATE_ONE,
                objs=obj,
            )
        )
        ServiceTestClient._verify_updated_obj(obj, updated_obj, user.id)
        return self._set_obj(updated_obj, update=True)

    def delete_object(
        self,
        user: str | User,
        model_class: Type[Model],
        obj: Model | str | tuple[UUID, UUID],
        retry_obj: tuple[UUID, UUID] | None = None,
    ) -> list[UUID] | UUID:
        user: self.user_class = self._get_obj(self.user_class, user)
        obj: Model = self._get_obj(model_class, obj, copy=True)

        if not obj and retry_obj:
            obj = self._get_obj(model_class, retry_obj, copy=True)

        deleted_obj_id = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user,
                operation=CrudOperation.DELETE_ONE,
                obj_ids=obj.id,
            )
        )
        # verify if deleted
        # is_existing_obj = self.app.handle(
        #     self.app.domain.get_crud_command_for_model(model_class)(
        #         user=user,
        #         operation=CrudOperation.EXISTS_ONE,
        #         obj_ids=deleted_obj_id,
        #     )
        # )
        # if is_existing_obj:
        #     raise ValueError(f"Object {deleted_obj_id} not deleted")
        return self._delete_obj(model_class, deleted_obj_id)

    def read_all(
        self,
        user: str | User,
        model_class: Type[BASE_MODEL_TYPE],
        cascade: bool = False,
    ) -> list[BASE_MODEL_TYPE]:
        user_obj: self.user_class = self._get_obj(self.user_class, user)
        return self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user_obj,
                operation=CrudOperation.READ_ALL,
                props={"cascade_read": cascade},
            ),
            use_endpoint=False,
        )

    def read_some(
        self,
        user: str | User,
        model_class: Type[Model],
        obj_ids: list[UUID] | set[UUID],
        cascade: bool = False,
    ) -> Model:
        user: self.user_class = self._get_obj(self.user_class, user)
        # objs = self.read_all(user, model_class, cascade=cascade)
        # return [x for x in objs if x.id in obj_ids]
        return self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user,
                operation=CrudOperation.READ_SOME,
                obj_ids=obj_ids,
                props={"cascade_read": cascade},
            ),
            use_endpoint=False,
        )

    def read_some_by_property(
        self,
        user: str | User,
        model_class: Type[Model],
        name: str,
        value: Any,
        cascade: bool = False,
    ) -> Model:
        objs = self.read_all(user, model_class, cascade=cascade)
        return [x for x in objs if getattr(x, name) == value]

    def read_one_by_property(
        self,
        user: str | User,
        model_class: Type[Model],
        name: str,
        value: Any,
        cascade: bool = False,
    ) -> Model:
        objs = self.read_some_by_property(
            user, model_class, name, value, cascade=cascade
        )
        if len(objs) == 0:
            raise ValueError(f"{model_class} with {name}='{value}' not found")
        if len(objs) > 1:
            raise ValueError(f"Multiple {model_class} with {name}='{value}' found")
        return objs[0]

    def verify_read_all(
        self,
        user: str | User,
        model_class: Type[Model],
        expected_ids: set[UUID] | list[Model],
    ) -> None:
        user_obj: self.user_class = self._get_obj(self.user_class, user)
        objs = self.handle(
            self.app.domain.get_crud_command_for_model(model_class)(
                user=user_obj, operation=CrudOperation.READ_ALL
            )
        )
        actual_ids = {x.id for x in objs}
        if not isinstance(expected_ids, set):
            expected_ids = {x.id for x in expected_ids if x.id is not None}
        if actual_ids != expected_ids:
            extra_ids = actual_ids - expected_ids
            missing_ids = expected_ids - actual_ids
            extra_names = [
                self._get_key_for_obj(self._get_obj(model_class, x)) for x in extra_ids
            ]
            missing_names = [
                self._get_key_for_obj(self._get_obj(model_class, x))
                for x in missing_ids
            ]
            raise ValueError(
                f"Difference in read all. Extra: {extra_names}. Missing: {missing_names}. User: {user_obj.name}. Model: {model_class}"
            )

    def _get_key_for_obj(self, obj: Model) -> Any:
        key_fields = self.MODEL_KEY_MAP[obj.__class__]
        if isinstance(key_fields, str):
            return getattr(obj, key_fields)
        return tuple(getattr(obj, x) for x in key_fields)

    @staticmethod
    def _init_repositories(
        repository_cfg: dict,
        services: set[Hashable],
        repository_type: RepositoryType,
        load_target: str,
        test_dir: str,
    ) -> None:
        for service_type in services:
            service_type_str = (
                str(service_type.value)
                if isinstance(service_type, Enum)
                else str(service_type)
            )
            curr_cfg = repository_cfg[service_type_str]
            if not curr_cfg:
                # No repository
                continue
            match repository_type:
                case RepositoryType.DICT:
                    curr_cfg["file"] = re.sub(
                        r"\.[A-Za-z]+\.pkl\.gz",
                        f".{load_target.lower()}.pkl.gz",
                        curr_cfg["file"],
                        flags=re.IGNORECASE,
                    )
                case RepositoryType.SA_SQLITE:
                    # Copy sqlite files to test output directory
                    source_file = re.sub(
                        r"\.[A-Za-z]+\.sqlite",
                        f".{load_target.lower()}.sqlite",
                        curr_cfg["file"],
                        flags=re.IGNORECASE,
                    )
                    if not os.path.isfile(source_file):
                        continue
                    target_file = os.path.join(test_dir, os.path.basename(source_file))
                    curr_cfg["file"] = target_file
                    shutil.copyfile(source_file, target_file)
                case RepositoryType.SA_SQL:
                    # Nothing to do
                    pass
                case _:
                    raise NotImplementedError(
                        f"repository_type {repository_type} not implemented"
                    )

    def _get_obj_key(
        self,
        table: dict,
        model_class: Type[Model],
        obj: str | UUID | Model | list[str | UUID | Model] | tuple[UUID, UUID],
        on_missing: str,
    ) -> tuple[UUID, UUID] | UUID:
        key_fields = self.MODEL_KEY_MAP[model_class]
        if not isinstance(key_fields, tuple):
            key_fields = (key_fields,) if len(key_fields) > 1 else key_fields
        if isinstance(obj, str) or isinstance(obj, datetime.datetime):
            key = (obj,)
        elif isinstance(obj, UUID):
            key = [x for x, y in table.items() if y.id == obj]
            if key:
                key = key[0]
            elif on_missing == "raise":
                raise ValueError(f"{model_class.__name__} {obj} not found")
            elif on_missing == "return_none":
                return None
            else:
                raise NotImplementedError()
        elif isinstance(obj, Model):
            key = tuple(getattr(obj, x) for x in key_fields)
        elif isinstance(obj, tuple):
            key = obj
        else:
            raise ValueError(f"Invalid object: {obj}")
        key = key if len(key) > 1 else key[0]
        return key

    def _get_obj(
        self,
        model_class: Type[Model],
        obj: str | UUID | Model | list[str | UUID | Model] | tuple[UUID, UUID],
        copy: bool = False,
        on_missing: str = "raise",
    ) -> BASE_MODEL_TYPE | list[BASE_MODEL_TYPE]:
        if isinstance(obj, list):
            return [self._get_obj(model_class, x) for x in obj]
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key = self._get_obj_key(table, model_class, obj, on_missing)
        if key not in table:
            if on_missing == "raise":
                raise ValueError(f"{model_class.__name__} {obj} not found")
            elif on_missing == "return_none":
                return None
            else:
                raise NotImplementedError()
        return table[key] if not copy else table[key].model_copy()

    def _set_obj(self, obj: Model, update: bool = False) -> Model:
        # print(f"{.__class__.__name__} {obj} created")
        model_class = type(obj)
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key_fields = self.MODEL_KEY_MAP[model_class]
        if not isinstance(key_fields, tuple):
            key_fields = (key_fields,) if len(key_fields) > 1 else key_fields
        model_name = model_class.__name__
        key = tuple(getattr(obj, x) for x in key_fields)
        key = key if len(key) > 1 else key[0]
        if key in table:
            if update:
                table[key] = obj
            else:
                raise ValueError(f"{model_name} {obj} already exists")
        table[key] = obj
        return obj

    def _delete_obj(self, model_class: Type[Model], obj_id: UUID) -> Model:
        if model_class not in self.db:
            self.db[model_class] = {}
        table = self.db[model_class]
        key = [x for x, y in table.items() if y.id == obj_id]
        if key:
            key = key[0]
        else:
            raise ValueError(f"{model_class} {obj_id} not found")
        if key not in table:
            raise ValueError(f"{model_class} {obj_id} not found")
        obj = table[key]
        del table[key]
        return obj

    def _update_object_properties(
        self,
        obj: Model,
        props: dict[str, Any | None],
        set_dummy_link: dict[str, bool] | bool = False,
        exclude_none: bool = True,
    ) -> None:
        """
        Helper function for update methods. All the (field_name, value) pairs in props
        are set as attributes of obj. If the field_name is a relationship field, the value
        is set as the id of the linked object. If set_dummy_link is provided for a
        relationship field and no real linked obj is provided, a dummy id is put instead.
        If exclude_none is True, fields or link fields with value None are not set.
        """
        # Parse input
        model_class = obj.__class__
        id_field_name = model_class.ENTITY.id_field_name
        link_map: dict[str, tuple[str, Type[Model]]] = {
            x.relationship_field_name: (x.link_field_name, x.link_model_class)
            for x in model_class.ENTITY.links.values()
        }
        default_set_dummy_link = False
        if isinstance(set_dummy_link, bool):
            default_set_dummy_link = set_dummy_link
            set_dummy_link = {}

        # Set value fields and any links
        for field_name, value in props.items():
            if field_name in link_map:
                field_name, link_model_class = link_map[field_name]
                if not value:
                    if set_dummy_link.get(field_name, default_set_dummy_link):
                        value = self.generate_id()
                    else:
                        value = None
                else:
                    if set_dummy_link.get(field_name, default_set_dummy_link):
                        raise ValueError(
                            f"{model_class.__name__} given and set dummy link True"
                        )
                    value = getattr(
                        self._get_obj(link_model_class, value), id_field_name
                    )
            if exclude_none and value is None:
                continue
            setattr(obj, field_name, value)

    @staticmethod
    def _set_log_level(app_cfg: BaseAppCfg, log_level: int) -> None:
        set_log_level(app_cfg.app_name.lower(), log_level)

    @staticmethod
    def _verify_updated_obj(in_obj, out_obj, user_id, **kwargs: dict) -> None:
        # TODO: verifying modified_by and modified_at is no longer possible here as the
        # persistence metadata no longer exists in the object. This should instead
        # be tested through unit tests on the repository in question.
        # verify_modified = kwargs.get("verify_modified", True)
        # if verify_modified and out_obj._modified_by != user_id:
        #     raise ValueError(f"_modified_by not updated: {out_obj._modified_by}")
        # if verify_modified and out_obj._modified_at <= in_obj._modified_at:
        #     raise ValueError(f"modified_at not updated: {out_obj._modified_at}")
        # if (
        #     out_obj.model_copy(
        #         update={
        #             "_modified_by": in_obj._modified_by,
        #             "_modified_at": in_obj._modified_at,
        #         }
        #     )
        #     != in_obj
        # ):
        #     raise ValueError(f"Object not updated: {in_obj}, {out_obj}")
        if out_obj != in_obj:
            raise ValueError(f"Object not updated: {in_obj}, {out_obj}")
