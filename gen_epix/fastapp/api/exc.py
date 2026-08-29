"""Utilities for the fastapp exc module."""

from fastapi import HTTPException, status


class BadRequest400HTTPException(HTTPException):
    """Provide the bad request400 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Bad request: The server cannot or will not process the request"
            " due to an apparent client error"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers
        )


class UnauthorizedUser401HTTPException(HTTPException):
    # User not logged in
    """Provide the unauthorized user401 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Unauthorized: The request has not been applied "
            "because it lacks valid credentials for the target resource"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers
        )


class Forbidden403HTTPException(HTTPException):
    # User does not have correct rights
    """Provide the forbidden403 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Forbidden: The server understood the request, "
            "but is refusing to authorize it"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers
        )


class ResourceNotFound404HTTPException(HTTPException):
    """Provide the resource not found404 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Resource not found: "
            "The requested resource could not be found but may be available in the future"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers
        )


class MethodNotAllowed405HTTPException(HTTPException):
    """Provide the method not allowed405 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Method not allowed: "
            "The request method is known by the server but has been disabled and cannot be used"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=detail,
            headers=headers,
        )


class ResourceConflict409HTTPException(HTTPException):
    """Provide the resource conflict409 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = "Conflict with current resource state",
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers
        )


class ForeignKeyConstraint409HTTPException(HTTPException):
    """Provide the foreign key constraint409 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = "Resource cannot be deleted due to dependent entities",
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers
        )


class UnprocessableEntity422HTTPException(HTTPException):
    """Provide the unprocessable entity422 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = "Invalid data: The request contains invalid data",
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
        )


class InternalServerError500HTTPException(HTTPException):
    """Provide the internal server error500 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Internal server error: "
            "The server has encountered a situation it doesn't know how to handle"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )


class NotImplemented501HTTPException(HTTPException):
    """Provide the not implemented501 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Not implemented: "
            "The server does not support the functionality required to fulfill the request"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=detail, headers=headers
        )


class ServiceUnavailableError503HTTPException(HTTPException):
    """Provide the service unavailable error503 h t t p exception framework abstraction."""

    def __init__(
        self,
        detail: str = (
            "Service unavailable: " "The server is not ready to handle the request"
        ),
        headers: dict[str, str] | None = None,
    ):
        """Initialize the instance."""
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers,
        )
