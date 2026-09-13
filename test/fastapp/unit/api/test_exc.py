"""Unit tests for HTTP exception classes."""

from __future__ import annotations

from fastapi import status

from gen_epix.fastapp.api.exc import (
    BadRequest400HTTPException,
    Forbidden403HTTPException,
    MethodNotAllowed405HTTPException,
    ResourceConflict409HTTPException,
    ResourceNotFound404HTTPException,
    UnauthorizedUser401HTTPException,
)


class TestBadRequest400HTTPException:
    """Tests for BadRequest400HTTPException."""

    def test_creates_with_default_message(self) -> None:
        """Verify 400 exception creates with default message."""
        exc = BadRequest400HTTPException()
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert "Bad request" in exc.detail

    def test_creates_with_custom_message(self) -> None:
        """Verify 400 exception creates with custom message."""
        detail = "Invalid input format"
        exc = BadRequest400HTTPException(detail=detail)
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.detail == detail

    def test_creates_with_custom_headers(self) -> None:
        """Verify 400 exception accepts custom headers."""
        headers = {"X-Custom": "header"}
        exc = BadRequest400HTTPException(headers=headers)
        assert exc.headers == headers


class TestUnauthorizedUser401HTTPException:
    """Tests for UnauthorizedUser401HTTPException."""

    def test_creates_with_default_message(self) -> None:
        """Verify 401 exception creates with default message."""
        exc = UnauthorizedUser401HTTPException()
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Unauthorized" in exc.detail

    def test_creates_with_custom_message(self) -> None:
        """Verify 401 exception creates with custom message."""
        detail = "Invalid credentials"
        exc = UnauthorizedUser401HTTPException(detail=detail)
        assert exc.detail == detail

    def test_creates_with_custom_headers(self) -> None:
        """Verify 401 exception accepts custom headers."""
        headers = {"WWW-Authenticate": "Bearer"}
        exc = UnauthorizedUser401HTTPException(headers=headers)
        assert exc.headers == headers


class TestForbidden403HTTPException:
    """Tests for Forbidden403HTTPException."""

    def test_creates_with_default_message(self) -> None:
        """Verify 403 exception creates with default message."""
        exc = Forbidden403HTTPException()
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert "Forbidden" in exc.detail

    def test_creates_with_custom_message(self) -> None:
        """Verify 403 exception creates with custom message."""
        detail = "Access denied"
        exc = Forbidden403HTTPException(detail=detail)
        assert exc.detail == detail


class TestResourceNotFound404HTTPException:
    """Tests for ResourceNotFound404HTTPException."""

    def test_creates_with_default_message(self) -> None:
        """Verify 404 exception creates with default message."""
        exc = ResourceNotFound404HTTPException()
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc.detail

    def test_creates_with_custom_message(self) -> None:
        """Verify 404 exception creates with custom message."""
        detail = "User not found"
        exc = ResourceNotFound404HTTPException(detail=detail)
        assert exc.detail == detail


class TestMethodNotAllowed405HTTPException:
    """Tests for MethodNotAllowed405HTTPException."""

    def test_creates_with_default_message(self) -> None:
        """Verify 405 exception creates with default message."""
        exc = MethodNotAllowed405HTTPException()
        assert exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert "Method not allowed" in exc.detail

    def test_creates_with_custom_message(self) -> None:
        """Verify 405 exception creates with custom message."""
        detail = "POST not allowed on this endpoint"
        exc = MethodNotAllowed405HTTPException(detail=detail)
        assert exc.detail == detail


class TestResourceConflict409HTTPException:
    """Tests for ResourceConflict409HTTPException."""

    def test_creates_with_default_message(self) -> None:
        """Verify 409 exception creates with default message."""
        exc = ResourceConflict409HTTPException()
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert "Conflict" in exc.detail

    def test_creates_with_custom_message(self) -> None:
        """Verify 409 exception creates with custom message."""
        detail = "Resource already exists"
        exc = ResourceConflict409HTTPException(detail=detail)
        assert exc.detail == detail

    def test_all_exceptions_are_http_exceptions(self) -> None:
        """Verify all exceptions are proper HTTPException subclasses."""
        from fastapi import HTTPException

        exceptions = [
            BadRequest400HTTPException(),
            UnauthorizedUser401HTTPException(),
            Forbidden403HTTPException(),
            ResourceNotFound404HTTPException(),
            MethodNotAllowed405HTTPException(),
            ResourceConflict409HTTPException(),
        ]
        for exc in exceptions:
            assert isinstance(exc, HTTPException)
