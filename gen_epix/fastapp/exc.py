"""Utilities for the fastapp exc module."""

from collections.abc import Iterable
from typing import Any


class DomainException(Exception):
    """Provide the domain exception framework abstraction."""

    def __init__(self, code: str, message: str | None):
        """Initialize the instance."""
        self.code = code
        self.message = message


class DataException(DomainException):
    """Provide the data exception framework abstraction."""

    def __init__(self, code: str, message: str | None, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message)
        self.ids = ids


class InvalidArgumentsError(DataException):
    """Provide the invalid arguments error framework abstraction."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)


class IdsError(DataException):
    """Provide the ids error framework abstraction."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)


class InvalidIdsError(IdsError):
    """Provide the invalid ids error framework abstraction."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)


class DuplicateIdsError(IdsError):
    """Provide the duplicate ids error framework abstraction."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)


class InvalidModelIdsError(IdsError):
    """Provide the invalid model ids error framework abstraction."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)


class AlreadyExistingIdsError(IdsError):
    """Provide the already existing ids error framework abstraction."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)


class InvalidLinkIdsError(IdsError):
    """Provide the invalid link ids error framework abstraction."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)


class LinkConstraintViolationError(IdsError):
    """Provide the link constraint violation error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str,
        ids: Iterable | None = None,
        linked_ids: Iterable | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)
        self.linked_ids = linked_ids


class UniqueConstraintViolationError(DataException):
    """Provide the unique constraint violation error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str,
        ids: Iterable | None = None,
        duplicate_key_ids: Iterable | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)
        self.duplicate_key_ids = duplicate_key_ids


class NotNullConstraintViolationError(DataException):
    """Provide the not null constraint violation error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str,
        ids: Iterable | None = None,
        column_names: Iterable[str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, ids=ids)
        self.column_names = column_names


class NoResultsError(DataException):
    """Provide the no results error framework abstraction."""

    def __init__(self, code: str, message: str | None = None):
        # Message is optional
        """Initialize the instance."""
        super().__init__(code, message)


class ServiceException(DomainException):
    """Provide the service exception framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        # Message is optional
        """Initialize the instance."""
        super().__init__(code, message)
        if http_props is None:
            http_props = {}
        self._init_http_props(http_props, 500)

    def get_http_status_code(self) -> int:
        """Perform the get http status code operation."""
        return int(self.http_props["status_code"])

    def get_http_other_props(self) -> dict[str, Any]:
        """Perform the get http other props operation."""
        return {x: y for x, y in self.http_props.items() if x not in {"status_code"}}

    def _init_message(self, message: str | None, default_message: str) -> None:
        """Perform the  init message operation."""
        super().__init__(
            code=self.code, message=default_message if not message else message
        )

    def _init_http_props(
        self, http_props: dict[str, Any], http_status_code: int
    ) -> None:
        """Perform the  init http props operation."""
        self.http_props = {**http_props}
        self.http_props["status_code"] = self.http_props.get(
            "status_code", http_status_code
        )


class InitializationServiceError(ServiceException):
    """Provide the initialization service error framework abstraction."""

    pass


class RepositoryInitializationServiceError(InitializationServiceError):
    """Provide the repository initialization service error framework abstraction."""

    pass


class RepositoryServiceError(ServiceException):
    """Provide the repository service error framework abstraction."""

    pass


class AuthException(ServiceException):
    """Provide the auth exception framework abstraction."""

    pass


class FeatureDisabledServiceError(ServiceException):
    """Provide the feature disabled service error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "System unavailable: Feature is disabled")
        self._init_http_props(http_props, 503)


class CredentialsAuthError(AuthException):
    """Provide the credentials auth error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Could not validate credentials")
        self._init_http_props(http_props, 401)


class UnauthorizedAuthError(AuthException):
    """Provide the unauthorized auth error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Unauthorized: Invalid credentials")
        self._init_http_props(http_props, 403)


class UserNotFoundAuthError(AuthException):
    """Provide the user not found auth error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "User not found")
        self._init_http_props(http_props, 404)


class UserAlreadyExistsAuthError(AuthException):
    """Provide the user already exists auth error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "User already exists")
        self._init_http_props(http_props, 409)


class ConcurrentModificationError(ServiceException):
    """Provide the concurrent modification error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(
            message,
            "Concurrent modification detected",
        )
        self._init_http_props(http_props, 409)


class ServiceUnavailableError(ServiceException):
    """Provide the service unavailable error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Service unavailable")
        self._init_http_props(http_props, 503)


class RequestLimitExceededAuthError(AuthException):
    """Provide the request limit exceeded auth error framework abstraction."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Request limit exceeded")
        self._init_http_props(http_props, 429)
