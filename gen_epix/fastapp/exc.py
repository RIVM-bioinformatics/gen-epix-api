from typing import Any, Iterable


class DomainException(Exception):
    def __init__(self, message: str | None):
        self.message = message


class DataException(DomainException):
    def __init__(self, message: str | None, ids: Iterable | None = None):
        super().__init__(message)
        self.ids = ids


class InvalidArgumentsError(DataException):
    def __init__(self, message: str, ids: Iterable | None = None):
        super().__init__(message, ids=ids)


class IdsError(DataException):
    def __init__(self, message: str, ids: Iterable | None = None):
        super().__init__(message, ids=ids)


class InvalidIdsError(IdsError):
    def __init__(self, message: str, ids: Iterable | None = None):
        super().__init__(message, ids=ids)


class DuplicateIdsError(IdsError):
    def __init__(self, message: str, ids: Iterable | None = None):
        super().__init__(message, ids=ids)


class InvalidModelIdsError(IdsError):
    def __init__(self, message: str, ids: Iterable | None = None):
        super().__init__(message, ids=ids)


class AlreadyExistingIdsError(IdsError):
    def __init__(self, message: str, ids: Iterable | None = None):
        super().__init__(message, ids=ids)


class InvalidLinkIdsError(IdsError):
    def __init__(self, message: str, ids: Iterable | None = None):
        super().__init__(message, ids=ids)


class LinkConstraintViolationError(IdsError):
    def __init__(
        self,
        message: str,
        ids: Iterable | None = None,
        linked_ids: Iterable | None = None,
    ):
        super().__init__(message, ids=ids)
        self.linked_ids = linked_ids


class UniqueConstraintViolationError(DataException):
    def __init__(
        self,
        message: str,
        ids: Iterable | None = None,
        duplicate_key_ids: Iterable | None = None,
    ):
        super().__init__(message, ids=ids)
        self.duplicate_key_ids = duplicate_key_ids


class NotNullConstraintViolationError(DataException):
    def __init__(
        self,
        message: str,
        ids: Iterable | None = None,
        column_names: Iterable[str] | None = None,
    ):
        super().__init__(message, ids=ids)
        self.column_names = column_names


class NoResultsError(DataException):
    def __init__(self, message: str | None = None):
        # Message is optional
        super().__init__(message)


class ServiceException(DomainException):
    def __init__(
        self, message: str | None = None, http_props: dict[str, Any] | None = None
    ):
        # Message is optional
        super().__init__(message)
        if http_props is None:
            http_props = {}
        self._init_http_props(http_props, 401)

    def get_http_status_code(self) -> int:
        return int(self.http_props["status_code"])

    def get_http_other_props(self) -> dict[str, Any]:
        return {x: y for x, y in self.http_props.items() if x not in {"status_code"}}

    def _init_message(self, message: str | None, default_message: str) -> None:
        super().__init__(message=default_message if not message else message)

    def _init_http_props(
        self, http_props: dict[str, Any], http_status_code: int
    ) -> None:
        self.http_props = {**http_props}
        self.http_props["status_code"] = self.http_props.get(
            "status_code", http_status_code
        )


class InitializationServiceError(ServiceException):
    pass


class RepositoryInitializationServiceError(InitializationServiceError):
    pass


class RepositoryServiceError(ServiceException):
    pass


class AuthException(ServiceException):
    pass


class CredentialsAuthError(AuthException):
    def __init__(
        self, message: str | None = None, http_props: dict[str, Any] | None = None
    ):
        super().__init__(message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Could not validate credentials")
        self._init_http_props(http_props, 401)


class UnauthorizedAuthError(AuthException):
    def __init__(
        self, message: str | None = None, http_props: dict[str, Any] | None = None
    ):
        super().__init__(message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Unauthorized: Invalid credentials")
        self._init_http_props(http_props, 403)


class UserNotFoundAuthError(AuthException):
    def __init__(
        self, message: str | None = None, http_props: dict[str, Any] | None = None
    ):
        super().__init__(message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "User not found")
        self._init_http_props(http_props, 404)


class UserAlreadyExistsAuthError(AuthException):
    def __init__(
        self, message: str | None = None, http_props: dict[str, Any] | None = None
    ):
        super().__init__(message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "User already exists")
        self._init_http_props(http_props, 409)


class ServiceUnavailableError(ServiceException):
    def __init__(
        self, message: str | None = None, http_props: dict[str, Any] | None = None
    ):
        super().__init__(message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Service unavailable")
        self._init_http_props(http_props, 503)
