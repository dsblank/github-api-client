"""Tests for rate limit handling."""

import time
import pytest
from pytest_httpx import HTTPXMock
from unittest.mock import patch

from github_rest_api import GitHub, RateLimitError


class TestRateLimitHandling:
    """Tests for rate limit detection and handling."""

    def test_rate_limit_error_raised(self, httpx_mock: HTTPXMock):
        """RateLimitError is raised on 429."""
        httpx_mock.add_response(
            url="https://api.github.com/user",
            status_code=429,
            json={"message": "API rate limit exceeded"},
            headers={"X-RateLimit-Reset": "1234567890"},
        )

        with GitHub(token="test") as gh:
            with pytest.raises(RateLimitError) as exc_info:
                gh.users.get_authenticated()
            assert exc_info.value.status_code == 429
            assert exc_info.value.reset_at == 1234567890

    def test_rate_limit_error_on_403_with_message(self, httpx_mock: HTTPXMock):
        """RateLimitError is raised on 403 with rate limit message."""
        httpx_mock.add_response(
            url="https://api.github.com/user",
            status_code=403,
            json={"message": "API rate limit exceeded"},
            headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1234567890"},
        )

        with GitHub(token="test") as gh:
            with pytest.raises(RateLimitError):
                gh.users.get_authenticated()

    def test_auto_retry_on_rate_limit(self, httpx_mock: HTTPXMock):
        """Auto retry waits and retries on rate limit."""
        # First request: rate limited
        httpx_mock.add_response(
            url="https://api.github.com/user",
            status_code=429,
            json={"message": "API rate limit exceeded"},
            headers={"Retry-After": "1"},
        )
        # Second request: success
        httpx_mock.add_response(
            url="https://api.github.com/user",
            json={"login": "octocat", "id": 1},
        )

        with patch("time.sleep") as mock_sleep:
            with GitHub(token="test", auto_retry=True) as gh:
                result = gh.users.get_authenticated()
                assert result["login"] == "octocat"
                mock_sleep.assert_called_once_with(1.0)

    def test_auto_retry_respects_max_retries(self, httpx_mock: HTTPXMock):
        """Auto retry stops after max_retries."""
        # All requests return rate limit
        for _ in range(4):
            httpx_mock.add_response(
                url="https://api.github.com/user",
                status_code=429,
                json={"message": "API rate limit exceeded"},
                headers={"Retry-After": "1"},
            )

        with patch("time.sleep"):
            with GitHub(token="test", auto_retry=True, max_retries=3) as gh:
                with pytest.raises(RateLimitError):
                    gh.users.get_authenticated()

    def test_auto_retry_uses_x_ratelimit_reset(self, httpx_mock: HTTPXMock):
        """Auto retry uses X-RateLimit-Reset header."""
        future_time = int(time.time()) + 5

        httpx_mock.add_response(
            url="https://api.github.com/user",
            status_code=429,
            json={"message": "API rate limit exceeded"},
            headers={"X-RateLimit-Reset": str(future_time)},
        )
        httpx_mock.add_response(
            url="https://api.github.com/user",
            json={"login": "octocat", "id": 1},
        )

        with patch("time.sleep") as mock_sleep:
            with GitHub(token="test", auto_retry=True) as gh:
                result = gh.users.get_authenticated()
                assert result["login"] == "octocat"
                # Should sleep for approximately 5 seconds
                call_args = mock_sleep.call_args[0][0]
                assert 4 <= call_args <= 6

    def test_no_retry_when_disabled(self, httpx_mock: HTTPXMock):
        """No retry when auto_retry is False."""
        httpx_mock.add_response(
            url="https://api.github.com/user",
            status_code=429,
            json={"message": "API rate limit exceeded"},
            headers={"Retry-After": "1"},
        )

        with GitHub(token="test", auto_retry=False) as gh:
            with pytest.raises(RateLimitError):
                gh.users.get_authenticated()

    def test_rate_limit_status(self, httpx_mock: HTTPXMock):
        """Can check rate limit status."""
        httpx_mock.add_response(
            url="https://api.github.com/rate_limit",
            json={
                "resources": {
                    "core": {
                        "limit": 5000,
                        "remaining": 4999,
                        "reset": 1234567890,
                    },
                    "search": {
                        "limit": 30,
                        "remaining": 29,
                        "reset": 1234567890,
                    },
                },
            },
        )

        with GitHub(token="test") as gh:
            status = gh.rate_limit()
            assert status["resources"]["core"]["limit"] == 5000
            assert status["resources"]["core"]["remaining"] == 4999

    def test_auto_retry_in_pagination(self, httpx_mock: HTTPXMock):
        """Auto retry works during pagination."""
        # Page 1: success
        httpx_mock.add_response(
            url="https://api.github.com/users/octocat/repos?type=owner&sort=full_name&direction=asc&per_page=30&page=1",
            json=[{"id": 1, "name": "repo1"}],
        )
        # Page 2: rate limited then success
        httpx_mock.add_response(
            url="https://api.github.com/users/octocat/repos?type=owner&sort=full_name&direction=asc&per_page=30&page=2",
            status_code=429,
            json={"message": "API rate limit exceeded"},
            headers={"Retry-After": "1"},
        )
        httpx_mock.add_response(
            url="https://api.github.com/users/octocat/repos?type=owner&sort=full_name&direction=asc&per_page=30&page=2",
            json=[{"id": 2, "name": "repo2"}],
        )
        # Page 3: empty
        httpx_mock.add_response(
            url="https://api.github.com/users/octocat/repos?type=owner&sort=full_name&direction=asc&per_page=30&page=3",
            json=[],
        )

        with patch("time.sleep"):
            with GitHub(token="test", auto_retry=True) as gh:
                repos = list(gh.repos.list_for_user("octocat"))
                assert len(repos) == 2
