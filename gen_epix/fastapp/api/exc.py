"""HTTP exceptions returned by generated API routes."""

from fastapi import HTTPException, status


class BadRequest400HTTPException(HTTPException):
    """HTTP 400 error for requests the API cannot process."""

    def __init__(
        self,
        detail: str = (
            "Bad request: The server cannot or will not process the request"
            " due to an apparent client error"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 400 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers
        )


class UnauthorizedUser401HTTPException(HTTPException):
    # User not logged in
    """HTTP 401 error for requests without valid credentials."""

    def __init__(
        self,
        detail: str = (
            "Unauthorized: The request has not been applied "
            "because it lacks valid credentials for the target resource"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 401 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers
        )


class Forbidden403HTTPException(HTTPException):
    # User does not have correct rights
    """HTTP 403 error for requests the user is not authorized to make."""

    def __init__(
        self,
        detail: str = (
            "Forbidden: The server understood the request, "
            "but is refusing to authorize it"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 403 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers
        )


class ResourceNotFound404HTTPException(HTTPException):
    """HTTP 404 error for unavailable resources."""

    def __init__(
        self,
        detail: str = (
            "Resource not found: "
            "The requested resource could not be found but may be available in the future"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 404 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers
        )


class MethodNotAllowed405HTTPException(HTTPException):
    """HTTP 405 error for disabled request methods."""

    def __init__(
        self,
        detail: str = (
            "Method not allowed: "
            "The request method is known by the server but has been disabled and cannot be used"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 405 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=detail,
            headers=headers,
        )


class ResourceConflict409HTTPException(HTTPException):
    """HTTP 409 error for requests that conflict with resource state."""

    def __init__(
        self,
        detail: str = "Conflict with current resource state",
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 409 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers
        )


class ForeignKeyConstraint409HTTPException(HTTPException):
    """HTTP 409 error when deletion would violate a foreign-key relationship."""

    def __init__(
        self,
        detail: str = "Resource cannot be deleted due to dependent entities",
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 409 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers
        )


class UnprocessableEntity422HTTPException(HTTPException):
    """HTTP 422 error for syntactically valid requests with invalid data."""

    def __init__(
        self,
        detail: str = "Invalid data: The request contains invalid data",
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 422 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
        )


class InternalServerError500HTTPException(HTTPException):
    """HTTP 500 error for unexpected server failures."""

    def __init__(
        self,
        detail: str = (
            "Internal server error: "
            "The server has encountered a situation it doesn't know how to handle"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 500 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )


class NotImplemented501HTTPException(HTTPException):
    """HTTP 501 error for unsupported server functionality."""

    def __init__(
        self,
        detail: str = (
            "Not implemented: "
            "The server does not support the functionality required to fulfill the request"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 501 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=detail, headers=headers
        )


class ServiceUnavailableError503HTTPException(HTTPException):
    """HTTP 503 error for a service that cannot currently handle requests."""

    def __init__(
        self,
        detail: str = (
            "Service unavailable: " "The server is not ready to handle the request"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Construct an HTTP 503 exception with optional headers."""
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers,
        )
