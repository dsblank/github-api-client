"""Base resource class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from github_api_client.client import AsyncGitHub, GitHub


class Resource:
    """Base class for sync API resources."""

    def __init__(self, client: GitHub) -> None:
        self._client = client

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        return self._client.request(method, path, **kwargs)

    def _paginate(self, method: str, path: str, **kwargs: Any) -> Any:
        return self._client.paginate(method, path, **kwargs)


class AsyncResource:
    """Base class for async API resources."""

    def __init__(self, client: AsyncGitHub) -> None:
        self._client = client

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        return await self._client.request(method, path, **kwargs)

    def _paginate(self, method: str, path: str, **kwargs: Any) -> Any:
        return self._client.paginate(method, path, **kwargs)
