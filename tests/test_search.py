"""Tests for search API."""

from github_api_client import GitHub
from pytest_httpx import HTTPXMock


class TestSearch:
    """Tests for search operations."""

    def test_search_issues(self, httpx_mock: HTTPXMock):
        """Search issues returns results."""
        httpx_mock.add_response(
            url="https://api.github.com/search/issues?q=bug+label%3Acritical&order=desc&per_page=100&page=1",
            json={
                "total_count": 2,
                "incomplete_results": False,
                "items": [
                    {"id": 1, "number": 1, "title": "Critical bug 1"},
                    {"id": 2, "number": 2, "title": "Critical bug 2"},
                ],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.issues("bug label:critical"))
            assert len(results) == 2
            assert results[0]["title"] == "Critical bug 1"

    def test_search_issues_with_sort(self, httpx_mock: HTTPXMock):
        """Search issues with sort parameter."""
        httpx_mock.add_response(
            url="https://api.github.com/search/issues?q=bug&order=desc&sort=created&per_page=100&page=1",
            json={
                "total_count": 1,
                "incomplete_results": False,
                "items": [{"id": 1, "title": "Bug"}],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.issues("bug", sort="created"))
            assert len(results) == 1

    def test_search_repositories(self, httpx_mock: HTTPXMock):
        """Search repositories returns results."""
        httpx_mock.add_response(
            url="https://api.github.com/search/repositories?q=python+stars%3A%3E1000&order=desc&per_page=100&page=1",
            json={
                "total_count": 2,
                "incomplete_results": False,
                "items": [
                    {"id": 1, "full_name": "owner/repo1", "stargazers_count": 5000},
                    {"id": 2, "full_name": "owner/repo2", "stargazers_count": 3000},
                ],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.repositories("python stars:>1000"))
            assert len(results) == 2
            assert results[0]["stargazers_count"] == 5000

    def test_search_code(self, httpx_mock: HTTPXMock):
        """Search code returns results."""
        httpx_mock.add_response(
            url="https://api.github.com/search/code?q=addClass+repo%3Ajquery%2Fjquery&order=desc&per_page=100&page=1",
            json={
                "total_count": 1,
                "incomplete_results": False,
                "items": [
                    {"name": "jquery.js", "path": "src/jquery.js"},
                ],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.code("addClass repo:jquery/jquery"))
            assert len(results) == 1
            assert results[0]["path"] == "src/jquery.js"

    def test_search_users(self, httpx_mock: HTTPXMock):
        """Search users returns results."""
        httpx_mock.add_response(
            url="https://api.github.com/search/users?q=location%3Atokyo&order=desc&per_page=100&page=1",
            json={
                "total_count": 1,
                "incomplete_results": False,
                "items": [
                    {"id": 1, "login": "user1", "type": "User"},
                ],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.users("location:tokyo"))
            assert len(results) == 1
            assert results[0]["login"] == "user1"

    def test_search_commits(self, httpx_mock: HTTPXMock):
        """Search commits returns results."""
        httpx_mock.add_response(
            url="https://api.github.com/search/commits?q=fix+bug&order=desc&per_page=100&page=1",
            json={
                "total_count": 1,
                "incomplete_results": False,
                "items": [
                    {
                        "sha": "abc123",
                        "commit": {"message": "Fix bug in parser"},
                    },
                ],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.commits("fix bug"))
            assert len(results) == 1
            assert results[0]["sha"] == "abc123"

    def test_search_pagination(self, httpx_mock: HTTPXMock):
        """Search paginates through results."""
        # First page
        httpx_mock.add_response(
            url="https://api.github.com/search/issues?q=bug&order=desc&per_page=100&page=1",
            json={
                "total_count": 150,
                "incomplete_results": False,
                "items": [{"id": i, "title": f"Bug {i}"} for i in range(100)],
            },
        )
        # Second page
        httpx_mock.add_response(
            url="https://api.github.com/search/issues?q=bug&order=desc&per_page=100&page=2",
            json={
                "total_count": 150,
                "incomplete_results": False,
                "items": [{"id": i, "title": f"Bug {i}"} for i in range(100, 150)],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.issues("bug"))
            assert len(results) == 150

    def test_search_empty_results(self, httpx_mock: HTTPXMock):
        """Search handles empty results."""
        httpx_mock.add_response(
            url="https://api.github.com/search/issues?q=nonexistent&order=desc&per_page=100&page=1",
            json={
                "total_count": 0,
                "incomplete_results": False,
                "items": [],
            },
        )

        with GitHub(token=None) as gh:
            results = list(gh.search.issues("nonexistent"))
            assert len(results) == 0
