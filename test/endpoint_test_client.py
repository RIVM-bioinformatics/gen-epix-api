import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Type
from uuid import UUID

# import libraries
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from jose import jwt
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.casedb.api.auth import UserInvitationRequestBody
from gen_epix.casedb.domain import command, model
from gen_epix.fastapp import CrudOperation


class EndpointVersion(Enum):
    V1 = "v1"


class EndpointTestClient:

    ENDPOINT_VERSION_PREFIX_MAP = {EndpointVersion.V1: "/v1"}
    SECRET_KEY = str(uuid.uuid4())
    ENCRYPTION_ALGORITHM = "HS256"

    def __init__(self, fast_api: FastAPI, **kwargs: dict) -> None:
        self.fast_api = fast_api
        self.test_client = TestClient(fast_api, raise_server_exceptions=False)

    @staticmethod
    def _content_to_obj(
        response: Response, retval_class: Type, is_list: bool = False
    ) -> Any:
        if response.status_code not in (200, 201):
            return None
        decoded_obj = json.loads(response.content.decode(response.encoding or "utf-8"))
        if issubclass(retval_class, PydanticBaseModel):
            if is_list:
                return [retval_class(**x) for x in decoded_obj]
            else:
                return retval_class(**decoded_obj)
        elif issubclass(retval_class, UUID):
            if is_list:
                return [UUID(x) for x in decoded_obj]
            else:
                return UUID(decoded_obj)
        raise NotImplementedError(f"Unsupported return type: {retval_class}")

    def handle(
        self,
        cmd: command.Command,
        return_response: bool = False,
        endpoint_version: EndpointVersion = EndpointVersion.V1,
    ) -> Any:
        route_prefix = self.ENDPOINT_VERSION_PREFIX_MAP[endpoint_version]
        if cmd.user:
            headers = self.get_dummy_jwt_header(cmd.user.email)
        else:
            headers = None
        if type(cmd) is command.GetIdentityProvidersCommand:
            response = self.test_client.get(route_prefix + "/identity_providers")
            retval = self._content_to_obj(
                response, model.IdentityProvider, is_list=True
            )
        if type(cmd) is command.InviteUserCommand:
            request_body = UserInvitationRequestBody(
                email=cmd.email,
                roles=cmd.roles,
                organization_id=cmd.organization_id,
            )
            response = self.test_client.post(
                route_prefix + "/user_invitations",
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            retval = self._content_to_obj(response, model.UserInvitation)
        if type(cmd) is command.RegisterInvitedUserCommand:
            response = self.test_client.post(
                route_prefix + f"/user_registrations/{cmd.token}",
                headers=headers,
            )
            retval = self._content_to_obj(response, model.User)
        if isinstance(cmd, command.CrudCommand):
            model_class = cmd.MODEL_CLASS
            entity = model_class.ENTITY
            route = f"{route_prefix}/{entity.snake_case_plural_name}"
            if cmd.operation == CrudOperation.READ_ALL:
                response = self.test_client.get(route, headers=headers)
                retval = self._content_to_obj(response, model_class, is_list=True)
            elif cmd.operation == CrudOperation.READ_SOME:
                response = self.test_client.get(
                    f"{route}", headers=headers, ids=cmd.obj_ids
                )
                retval = self._content_to_obj(response, model_class, is_list=True)
            elif cmd.operation == CrudOperation.READ_ONE:
                response = self.test_client.get(
                    f"{route}/{cmd.obj_ids}", headers=headers
                )
                retval = self._content_to_obj(response, model_class)
            elif cmd.operation == CrudOperation.CREATE_ONE:
                response = self.test_client.post(
                    f"{route}",
                    json=json.loads(cmd.objs.model_dump_json()),
                    headers=headers,
                )
                retval = self._content_to_obj(response, model_class)
            elif cmd.operation == CrudOperation.UPDATE_ONE:
                response = self.test_client.put(
                    f"{route}/{cmd.obj_ids}",
                    json=json.loads(cmd.objs.model_dump_json()),
                    headers=headers,
                )
                retval = self._content_to_obj(response, model_class)
            elif cmd.operation in (CrudOperation.DELETE_ONE,):
                response = self.test_client.delete(
                    f"{route}/{cmd.obj_ids}", headers=headers
                )
                retval = None
            else:
                raise NotImplementedError(f"Unsupported operation: {cmd.operation}")
            # TODO: map response model to internal model, in case different
        if return_response:
            return retval, response
        return retval

    def get_dummy_jwt(
        self,
        email: str,
        iss: str | None = None,
        sub: str | None = None,
        aud: str | None = None,
        exp: int | None = None,
        expire_default_minutes: int = 15,
    ) -> str:
        claims = {
            "email": email,
            "iss": iss or f"https://{uuid.uuid4()}.org",
            "sub": sub or str(uuid.uuid4()),
            "aud": aud or str(uuid.uuid4()),
            "exp": exp or datetime.now() + timedelta(minutes=expire_default_minutes),
        }
        encoded_jwt = jwt.encode(
            claims, self.SECRET_KEY, algorithm=self.ENCRYPTION_ALGORITHM
        )
        return encoded_jwt

    def get_dummy_jwt_header(
        self,
        email: str,
        iss: str | None = None,
        sub: str | None = None,
        aud: str | None = None,
        exp: int | None = None,
        expire_default_minutes: int = 15,
    ) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.get_dummy_jwt(email, iss, sub, aud, exp, expire_default_minutes)}"
        }
