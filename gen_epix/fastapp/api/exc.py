from fastapi import HTTPException, status


class BadRequest400HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = (
            "Bad request: The server cannot or will not process the request"
            " due to an apparent client error"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers
        )


class UnauthorizedUser401HTTPException(HTTPException):
    # User not logged in
    def __init__(
        self,
        detail: str = (
            "Unauthorized: The request has not been applied "
            "because it lacks valid credentials for the target resource"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers
        )


class Forbidden403HTTPException(HTTPException):
    # User does not have correct rights
    def __init__(
        self,
        detail: str = (
            "Forbidden: The server understood the request, "
            "but is refusing to authorize it"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers
        )


class ResourceNotFound404HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = (
            "Resource not found: "
            "The requested resource could not be found but may be available in the future"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers
        )


class MethodNotAllowed405HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = (
            "Method not allowed: "
            "The request method is known by the server but has been disabled and cannot be used"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=detail,
            headers=headers,
        )


class ResourceAlreadyExists409HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = (
            "Resource already exists: "
            "The request could not be completed due to a conflict "
            "with the current state of the target resource"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers
        )


class UnprocessableEntity422HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = "Invalid data: The request contains invalid data",
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
        )


class InternalServerError500HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = (
            "Internal server error: "
            "The server has encountered a situation it doesn't know how to handle"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )


class NotImplemented501HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = (
            "Not implemented: "
            "The server does not support the functionality required to fulfill the request"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=detail, headers=headers
        )


class ServiceUnavailableError503HTTPException(HTTPException):
    def __init__(
        self,
        detail: str = (
            "Service unavailable: " "The server is not ready to handle the request"
        ),
        headers: dict[str, str] | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers,
        )
