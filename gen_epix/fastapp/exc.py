"""Exceptions used by the domain, service, and API layers."""

from collections.abc import Iterable
from typing import Any


class DomainException(Exception):
    """Base error that carries a stable application error code and message."""

    def __init__(self, code: str, message: str | None):
        """Initialize a DomainException instance."""
        self.code = code
        self.message = message


class DataException(DomainException):
    """Domain error associated with one or more data identifiers."""

    def __init__(self, code: str, message: str | None, ids: Iterable | None = None):
        """Initialize a DataException instance."""
        super().__init__(code, message)
        self.ids = ids


class InvalidArgumentsError(DataException):
    """Error for command arguments that fail validation."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize a InvalidArgumentsError instance."""
        super().__init__(code, message, ids=ids)


class IdsError(DataException):
    """Base error associated with supplied object identifiers."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize a IdsError instance."""
        super().__init__(code, message, ids=ids)


class InvalidIdsError(IdsError):
    """Error for malformed or unknown object identifiers."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize a InvalidIdsError instance."""
        super().__init__(code, message, ids=ids)


class DuplicateIdsError(IdsError):
    """Error for duplicate object identifiers in one operation."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize a DuplicateIdsError instance."""
        super().__init__(code, message, ids=ids)


class InvalidModelIdsError(IdsError):
    """Error for identifiers belonging to an unexpected model."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize a InvalidModelIdsError instance."""
        super().__init__(code, message, ids=ids)


class AlreadyExistingIdsError(IdsError):
    """Error for identifiers that already exist in persistent storage."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize a AlreadyExistingIdsError instance."""
        super().__init__(code, message, ids=ids)


class InvalidLinkIdsError(IdsError):
    """Error for identifiers that violate a model relationship."""

    def __init__(self, code: str, message: str, ids: Iterable | None = None):
        """Initialize a InvalidLinkIdsError instance."""
        super().__init__(code, message, ids=ids)


class LinkConstraintViolationError(IdsError):
    """Error for a relationship constraint violation between model instances."""

    def __init__(
        self,
        code: str,
        message: str,
        ids: Iterable | None = None,
        linked_ids: Iterable | None = None,
    ):
        """Initialize a LinkConstraintViolationError instance."""
        super().__init__(code, message, ids=ids)
        self.linked_ids = linked_ids


class UniqueConstraintViolationError(DataException):
    """Error for data that violates a unique constraint."""

    def __init__(
        self,
        code: str,
        message: str,
        ids: Iterable | None = None,
        duplicate_key_ids: Iterable | None = None,
    ):
        """Initialize a UniqueConstraintViolationError instance."""
        super().__init__(code, message, ids=ids)
        self.duplicate_key_ids = duplicate_key_ids


class NotNullConstraintViolationError(DataException):
    """Error for data that omits a required field."""

    def __init__(
        self,
        code: str,
        message: str,
        ids: Iterable | None = None,
        column_names: Iterable[str] | None = None,
    ):
        """Initialize a NotNullConstraintViolationError instance."""
        super().__init__(code, message, ids=ids)
        self.column_names = column_names


class NoResultsError(DataException):
    """Error for an operation that expected matching data but found none."""

    def __init__(self, code: str, message: str | None = None):
        # Message is optional
        """Initialize a NoResultsError instance."""
        super().__init__(code, message)


class ServiceException(DomainException):
    """Base service error with HTTP response properties."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        # Message is optional
        """Initialize a ServiceException instance."""
        super().__init__(code, message)
        if http_props is None:
            http_props = {}
        self._init_http_props(http_props, 500)

    def get_http_status_code(self) -> int:
        """Return http status code."""
        return int(self.http_props["status_code"])

    def get_http_other_props(self) -> dict[str, Any]:
        """Return http other props."""
        return {x: y for x, y in self.http_props.items() if x not in {"status_code"}}

    def _init_message(self, message: str | None, default_message: str) -> None:
        """Initialize message."""
        super().__init__(
            code=self.code, message=default_message if not message else message
        )

    def _init_http_props(
        self, http_props: dict[str, Any], http_status_code: int
    ) -> None:
        """Initialize http props."""
        self.http_props = {**http_props}
        self.http_props["status_code"] = self.http_props.get(
            "status_code", http_status_code
        )


class InitializationServiceError(ServiceException):
    """Error while initializing an application service."""

    pass


class RepositoryInitializationServiceError(InitializationServiceError):
    """Error while initializing a repository-backed service."""

    pass


class RepositoryServiceError(ServiceException):
    """Error representing a failure in a repository-backed service operation."""

    pass


class AuthException(ServiceException):
    """Base error for authentication and authorization failures."""

    pass


class FeatureDisabledServiceError(ServiceException):
    """HTTP 503 error for commands disabled by application configuration."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a FeatureDisabledServiceError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "System unavailable: Feature is disabled")
        self._init_http_props(http_props, 503)


class CredentialsAuthError(AuthException):
    """HTTP 401 error for credentials that cannot be validated."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a CredentialsAuthError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Could not validate credentials")
        self._init_http_props(http_props, 401)


class UnauthorizedAuthError(AuthException):
    """HTTP 403 error for credentials without the required authorization."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a UnauthorizedAuthError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Unauthorized: Invalid credentials")
        self._init_http_props(http_props, 403)


class UserNotFoundAuthError(AuthException):
    """HTTP 404 error for an identity with no application user."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a UserNotFoundAuthError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "User not found")
        self._init_http_props(http_props, 404)


class UserAlreadyExistsAuthError(AuthException):
    """HTTP 409 error for an identity that already has an application user."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a UserAlreadyExistsAuthError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "User already exists")
        self._init_http_props(http_props, 409)


class ConcurrentModificationError(ServiceException):
    """HTTP 409 error for a conflicting concurrent modification."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a ConcurrentModificationError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(
            message,
            "Concurrent modification detected",
        )
        self._init_http_props(http_props, 409)


class ServiceUnavailableError(ServiceException):
    """HTTP 503 error for a temporarily unavailable service."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a ServiceUnavailableError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Service unavailable")
        self._init_http_props(http_props, 503)


class RequestLimitExceededAuthError(AuthException):
    """HTTP 429 error for an authentication request that exceeds its limit."""

    def __init__(
        self,
        code: str,
        message: str | None = None,
        http_props: dict[str, Any] | None = None,
    ):
        """Initialize a RequestLimitExceededAuthError instance."""
        super().__init__(code, message, http_props)
        if http_props is None:
            http_props = {}
        self._init_message(message, "Request limit exceeded")
        self._init_http_props(http_props, 429)
