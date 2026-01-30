"""GitHub API exceptions."""

from __future__ import annotations

from typing import Any


class GitHubError(Exception):
    """Base exception for GitHub API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(GitHubError):
    """Raised when authentication fails (401)."""


class NotFoundError(GitHubError):
    """Raised when a resource is not found (404)."""


class RateLimitError(GitHubError):
    """Raised when rate limit is exceeded (403/429)."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
        reset_at: int | None = None,
    ) -> None:
        super().__init__(message, status_code, response_data)
        self.reset_at = reset_at


class ValidationError(GitHubError):
    """Raised when request validation fails (422)."""
