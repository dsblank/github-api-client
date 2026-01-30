"""GitHub API client implementations."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterator
from typing import Any

import httpx

from github_api_client.auth import get_token
from github_api_client.exceptions import (
    AuthenticationError,
    GitHubError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from github_api_client.repo import AsyncRepo, Repo
from github_api_client.resources.issues import AsyncIssuesResource, IssuesResource
from github_api_client.resources.pulls import AsyncPullsResource, PullsResource
from github_api_client.resources.releases import AsyncReleasesResource, ReleasesResource
from github_api_client.resources.repos import AsyncReposResource, ReposResource
from github_api_client.resources.search import AsyncSearchResource, SearchResource
from github_api_client.resources.users import AsyncUsersResource, UsersResource

BASE_URL = "https://api.github.com"
_UNSET = object()  # Sentinel to distinguish None from "not provided"


def _handle_error_response(response: httpx.Response) -> None:
    """Raise appropriate exception for error responses."""
    status_code = response.status_code
    try:
        data = response.json()
        message = data.get("message", response.text)
    except Exception:
        data = {}
        message = response.text

    if status_code == 401:
        raise AuthenticationError(message, status_code, data)
    elif status_code == 404:
        raise NotFoundError(message, status_code, data)
    elif status_code in (403, 429):
        reset_at = response.headers.get("X-RateLimit-Reset")
        raise RateLimitError(
            message,
            status_code,
            data,
            reset_at=int(reset_at) if reset_at else None,
        )
    elif status_code == 422:
        raise ValidationError(message, status_code, data)
    else:
        raise GitHubError(message, status_code, data)


def _is_rate_limit_error(response: httpx.Response) -> bool:
    """Check if response is a rate limit error."""
    if response.status_code not in (403, 429):
        return False
    # Check for rate limit specific indicators
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining == "0":
        return True
    try:
        data = response.json()
        message = data.get("message", "").lower()
        return "rate limit" in message or "abuse" in message
    except Exception:
        return response.status_code == 429


def _get_retry_after(response: httpx.Response) -> float:
    """Get seconds to wait before retrying."""
    # Check Retry-After header first
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return float(retry_after)
        except ValueError:
            pass

    # Fall back to X-RateLimit-Reset
    reset_at = response.headers.get("X-RateLimit-Reset")
    if reset_at:
        try:
            reset_time = int(reset_at)
            wait_time = reset_time - time.time()
            return max(wait_time, 1)  # At least 1 second
        except ValueError:
            pass

    # Default wait time
    return 60


class GitHub:
    """Synchronous GitHub API client.

    Usage:
        >>> gh = GitHub(token="ghp_...")
        >>> repo = gh.repos.get("owner", "repo")
        >>> issues = gh.issues.list("owner", "repo")

        # Auto-detect token from environment or gh CLI:
        >>> gh = GitHub()
        >>> repo = gh.repos.get("owner", "repo")

        # Auto-retry on rate limits:
        >>> gh = GitHub(auto_retry=True)
    """

    def __init__(
        self,
        token: str | None | object = _UNSET,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        auto_retry: bool = False,
        max_retries: int = 3,
    ) -> None:
        """Initialize the GitHub client.

        Args:
            token: Personal access token or fine-grained token.
                   If not provided, auto-detects from environment variables
                   (GH_TOKEN, GITHUB_TOKEN) or gh CLI authentication.
                   Pass None explicitly to disable authentication.
            base_url: API base URL (default: https://api.github.com).
            timeout: Request timeout in seconds.
            auto_retry: Automatically retry on rate limit errors.
            max_retries: Maximum number of retries for rate limits.
        """
        # Auto-detect token if not provided
        if token is _UNSET:
            token = get_token()

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.Client(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )
        self._auto_retry = auto_retry
        self._max_retries = max_retries

        # Initialize resource handlers
        self.repos = ReposResource(self)
        self.issues = IssuesResource(self)
        self.pulls = PullsResource(self)
        self.users = UsersResource(self)
        self.search = SearchResource(self)
        self.releases = ReleasesResource(self)

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Make an API request.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            **kwargs: Additional arguments passed to httpx.

        Returns:
            Parsed JSON response.

        Raises:
            GitHubError: On API errors.
        """
        retries = 0
        while True:
            response = self._client.request(method, path, **kwargs)

            if response.status_code >= 400:
                # Handle rate limiting with auto-retry
                if self._auto_retry and _is_rate_limit_error(response):
                    if retries < self._max_retries:
                        wait_time = _get_retry_after(response)
                        time.sleep(wait_time)
                        retries += 1
                        continue
                _handle_error_response(response)

            if response.status_code == 204:
                return None
            return response.json()

    def paginate(
        self,
        method: str,
        path: str,
        per_page: int = 30,
        **kwargs: Any,
    ) -> Iterator[Any]:
        """Iterate through paginated results.

        Args:
            method: HTTP method.
            path: API endpoint path.
            per_page: Results per page (max 100).
            **kwargs: Additional arguments passed to httpx.

        Yields:
            Individual items from paginated responses.
        """
        params = kwargs.pop("params", {})
        params["per_page"] = min(per_page, 100)
        page = 1

        while True:
            params["page"] = page
            retries = 0
            while True:
                response = self._client.request(method, path, params=params, **kwargs)

                if response.status_code >= 400:
                    if self._auto_retry and _is_rate_limit_error(response):
                        if retries < self._max_retries:
                            wait_time = _get_retry_after(response)
                            time.sleep(wait_time)
                            retries += 1
                            continue
                    _handle_error_response(response)
                break

            items = response.json()
            if not items:
                break

            yield from items
            page += 1

    def repo(self, owner: str, name: str | None = None) -> Repo:
        """Get a repository-bound interface.

        Args:
            owner: Repository owner, or full name as "owner/repo".
            name: Repository name (optional if owner contains full name).

        Returns:
            A Repo object with bound owner/repo context.

        Usage:
            >>> repo = gh.repo("comet-ml", "opik")
            >>> # or
            >>> repo = gh.repo("comet-ml/opik")
            >>> issues = list(repo.issues.list())
        """
        if name is None:
            if "/" not in owner:
                raise ValueError("Must provide repo name or use 'owner/repo' format")
            owner, name = owner.split("/", 1)
        return Repo(self, owner, name)

    def rate_limit(self) -> dict[str, Any]:
        """Get current rate limit status.

        Returns:
            Rate limit information including limits, remaining, and reset times.
        """
        return self.request("GET", "/rate_limit")

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> GitHub:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncGitHub:
    """Asynchronous GitHub API client.

    Usage:
        >>> async with AsyncGitHub(token="ghp_...") as gh:
        ...     repo = await gh.repos.get("owner", "repo")
        ...     issues = await gh.issues.list("owner", "repo")

        # Auto-detect token from environment or gh CLI:
        >>> async with AsyncGitHub() as gh:
        ...     repo = await gh.repos.get("owner", "repo")

        # Auto-retry on rate limits:
        >>> async with AsyncGitHub(auto_retry=True) as gh:
        ...     # Will automatically wait and retry on rate limits
    """

    def __init__(
        self,
        token: str | None | object = _UNSET,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        auto_retry: bool = False,
        max_retries: int = 3,
    ) -> None:
        """Initialize the async GitHub client.

        Args:
            token: Personal access token or fine-grained token.
                   If not provided, auto-detects from environment variables
                   (GH_TOKEN, GITHUB_TOKEN) or gh CLI authentication.
                   Pass None explicitly to disable authentication.
            base_url: API base URL (default: https://api.github.com).
            timeout: Request timeout in seconds.
            auto_retry: Automatically retry on rate limit errors.
            max_retries: Maximum number of retries for rate limits.
        """
        # Auto-detect token if not provided
        if token is _UNSET:
            token = get_token()

        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
        )
        self._auto_retry = auto_retry
        self._max_retries = max_retries

        # Initialize resource handlers
        self.repos = AsyncReposResource(self)
        self.issues = AsyncIssuesResource(self)
        self.pulls = AsyncPullsResource(self)
        self.users = AsyncUsersResource(self)
        self.search = AsyncSearchResource(self)
        self.releases = AsyncReleasesResource(self)

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        """Make an async API request.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            **kwargs: Additional arguments passed to httpx.

        Returns:
            Parsed JSON response.

        Raises:
            GitHubError: On API errors.
        """
        retries = 0
        while True:
            response = await self._client.request(method, path, **kwargs)

            if response.status_code >= 400:
                # Handle rate limiting with auto-retry
                if self._auto_retry and _is_rate_limit_error(response):
                    if retries < self._max_retries:
                        wait_time = _get_retry_after(response)
                        await asyncio.sleep(wait_time)
                        retries += 1
                        continue
                _handle_error_response(response)

            if response.status_code == 204:
                return None
            return response.json()

    async def paginate(
        self,
        method: str,
        path: str,
        per_page: int = 30,
        **kwargs: Any,
    ) -> Any:
        """Iterate through paginated results asynchronously.

        Args:
            method: HTTP method.
            path: API endpoint path.
            per_page: Results per page (max 100).
            **kwargs: Additional arguments passed to httpx.

        Yields:
            Individual items from paginated responses.
        """
        params = kwargs.pop("params", {})
        params["per_page"] = min(per_page, 100)
        page = 1

        while True:
            params["page"] = page
            retries = 0
            while True:
                response = await self._client.request(method, path, params=params, **kwargs)

                if response.status_code >= 400:
                    if self._auto_retry and _is_rate_limit_error(response):
                        if retries < self._max_retries:
                            wait_time = _get_retry_after(response)
                            await asyncio.sleep(wait_time)
                            retries += 1
                            continue
                    _handle_error_response(response)
                break

            items = response.json()
            if not items:
                break

            for item in items:
                yield item
            page += 1

    def repo(self, owner: str, name: str | None = None) -> AsyncRepo:
        """Get a repository-bound interface.

        Args:
            owner: Repository owner, or full name as "owner/repo".
            name: Repository name (optional if owner contains full name).

        Returns:
            An AsyncRepo object with bound owner/repo context.

        Usage:
            >>> repo = gh.repo("comet-ml", "opik")
            >>> # or
            >>> repo = gh.repo("comet-ml/opik")
            >>> async for issue in repo.issues.list():
            ...     print(issue["title"])
        """
        if name is None:
            if "/" not in owner:
                raise ValueError("Must provide repo name or use 'owner/repo' format")
            owner, name = owner.split("/", 1)
        return AsyncRepo(self, owner, name)

    async def rate_limit(self) -> dict[str, Any]:
        """Get current rate limit status.

        Returns:
            Rate limit information including limits, remaining, and reset times.
        """
        return await self.request("GET", "/rate_limit")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncGitHub:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
