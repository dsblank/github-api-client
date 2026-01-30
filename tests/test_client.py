"""Tests for the GitHub client."""

import pytest
from pytest_httpx import HTTPXMock

from github_rest_api import GitHub, AsyncGitHub
from github_rest_api.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)


class TestGitHub:
    """Tests for synchronous GitHub client."""

    def test_init_without_token(self):
        """Client can be created without a token."""
        gh = GitHub()
        assert gh._client is not None
        gh.close()

    def test_init_with_token(self):
        """Client includes auth header when token provided."""
        gh = GitHub(token="test-token")
        assert gh._client.headers["Authorization"] == "Bearer test-token"
        gh.close()

    def test_context_manager(self):
        """Client works as context manager."""
        with GitHub() as gh:
            assert gh._client is not None

    def test_get_repo(self, httpx_mock: HTTPXMock):
        """Can fetch a repository."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/octocat/Hello-World",
            json={"id": 1, "name": "Hello-World", "full_name": "octocat/Hello-World"},
        )

        with GitHub() as gh:
            repo = gh.repos.get("octocat", "Hello-World")
            assert repo["name"] == "Hello-World"

    def test_authentication_error(self, httpx_mock: HTTPXMock):
        """Raises AuthenticationError on 401."""
        httpx_mock.add_response(
            url="https://api.github.com/user",
            status_code=401,
            json={"message": "Bad credentials"},
        )

        with GitHub(token="bad-token") as gh:
            with pytest.raises(AuthenticationError) as exc_info:
                gh.users.get_authenticated()
            assert exc_info.value.status_code == 401

    def test_not_found_error(self, httpx_mock: HTTPXMock):
        """Raises NotFoundError on 404."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/nonexistent/repo",
            status_code=404,
            json={"message": "Not Found"},
        )

        with GitHub() as gh:
            with pytest.raises(NotFoundError) as exc_info:
                gh.repos.get("nonexistent", "repo")
            assert exc_info.value.status_code == 404

    def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        """Raises RateLimitError on 403 rate limit."""
        httpx_mock.add_response(
            url="https://api.github.com/users/octocat",
            status_code=403,
            json={"message": "API rate limit exceeded"},
            headers={"X-RateLimit-Reset": "1234567890"},
        )

        with GitHub() as gh:
            with pytest.raises(RateLimitError) as exc_info:
                gh.users.get("octocat")
            assert exc_info.value.reset_at == 1234567890

    def test_pagination(self, httpx_mock: HTTPXMock):
        """Pagination iterates through all pages."""
        base_params = "type=owner&sort=full_name&direction=asc&per_page=30"
        httpx_mock.add_response(
            url=f"https://api.github.com/users/octocat/repos?{base_params}&page=1",
            json=[{"id": 1}, {"id": 2}],
        )
        httpx_mock.add_response(
            url=f"https://api.github.com/users/octocat/repos?{base_params}&page=2",
            json=[{"id": 3}],
        )
        httpx_mock.add_response(
            url=f"https://api.github.com/users/octocat/repos?{base_params}&page=3",
            json=[],
        )

        with GitHub() as gh:
            repos = list(gh.repos.list_for_user("octocat"))
            assert len(repos) == 3


class TestAsyncGitHub:
    """Tests for asynchronous GitHub client."""

    @pytest.mark.asyncio
    async def test_init_without_token(self):
        """Async client can be created without a token."""
        gh = AsyncGitHub()
        assert gh._client is not None
        await gh.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Async client works as context manager."""
        async with AsyncGitHub() as gh:
            assert gh._client is not None

    @pytest.mark.asyncio
    async def test_get_repo(self, httpx_mock: HTTPXMock):
        """Async client can fetch a repository."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/octocat/Hello-World",
            json={"id": 1, "name": "Hello-World"},
        )

        async with AsyncGitHub() as gh:
            repo = await gh.repos.get("octocat", "Hello-World")
            assert repo["name"] == "Hello-World"
