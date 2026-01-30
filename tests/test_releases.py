"""Tests for releases API."""

import tempfile
from pathlib import Path

from github_api_client import GitHub
from pytest_httpx import HTTPXMock


class TestReleases:
    """Tests for release operations."""

    def test_list_releases(self, httpx_mock: HTTPXMock):
        """List releases returns results."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases?per_page=30&page=1",
            json=[
                {"id": 1, "tag_name": "v1.0.0", "name": "Version 1.0.0"},
                {"id": 2, "tag_name": "v0.9.0", "name": "Version 0.9.0"},
            ],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases?per_page=30&page=2",
            json=[],
        )

        with GitHub(token="test-token") as gh:
            releases = list(gh.releases.list("owner", "repo"))
            assert len(releases) == 2
            assert releases[0]["tag_name"] == "v1.0.0"
            assert releases[1]["tag_name"] == "v0.9.0"

    def test_get_release(self, httpx_mock: HTTPXMock):
        """Get release by ID."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/123",
            json={"id": 123, "tag_name": "v1.0.0", "name": "Version 1.0.0"},
        )

        with GitHub(token="test-token") as gh:
            release = gh.releases.get("owner", "repo", 123)
            assert release["id"] == 123
            assert release["tag_name"] == "v1.0.0"

    def test_get_latest_release(self, httpx_mock: HTTPXMock):
        """Get latest release."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/latest",
            json={"id": 123, "tag_name": "v1.0.0", "name": "Version 1.0.0"},
        )

        with GitHub(token="test-token") as gh:
            release = gh.releases.get_latest("owner", "repo")
            assert release["tag_name"] == "v1.0.0"

    def test_get_release_by_tag(self, httpx_mock: HTTPXMock):
        """Get release by tag name."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/tags/v1.0.0",
            json={"id": 123, "tag_name": "v1.0.0", "name": "Version 1.0.0"},
        )

        with GitHub(token="test-token") as gh:
            release = gh.releases.get_by_tag("owner", "repo", "v1.0.0")
            assert release["tag_name"] == "v1.0.0"

    def test_create_release(self, httpx_mock: HTTPXMock):
        """Create a release."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases",
            method="POST",
            json={
                "id": 123,
                "tag_name": "v1.0.0",
                "name": "Version 1.0.0",
                "body": "Release notes",
            },
        )

        with GitHub(token="test-token") as gh:
            release = gh.releases.create(
                "owner",
                "repo",
                tag_name="v1.0.0",
                name="Version 1.0.0",
                body="Release notes",
            )
            assert release["id"] == 123
            assert release["tag_name"] == "v1.0.0"

    def test_delete_release(self, httpx_mock: HTTPXMock):
        """Delete a release."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/123",
            method="DELETE",
            status_code=204,
        )

        with GitHub(token="test-token") as gh:
            gh.releases.delete("owner", "repo", 123)

    def test_list_assets(self, httpx_mock: HTTPXMock):
        """List release assets."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/123/assets?per_page=30&page=1",
            json=[
                {"id": 1, "name": "package.tar.gz", "size": 1024},
                {"id": 2, "name": "package.whl", "size": 2048},
            ],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/123/assets?per_page=30&page=2",
            json=[],
        )

        with GitHub(token="test-token") as gh:
            assets = list(gh.releases.list_assets("owner", "repo", 123))
            assert len(assets) == 2
            assert assets[0]["name"] == "package.tar.gz"

    def test_upload_asset(self, httpx_mock: HTTPXMock):
        """Upload a release asset."""
        httpx_mock.add_response(
            url="https://uploads.github.com/repos/owner/repo/releases/123/assets?name=test.txt",
            method="POST",
            json={"id": 456, "name": "test.txt", "size": 13},
        )

        with GitHub(token="test-token") as gh:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write("test content")
                f.flush()
                temp_path = f.name

            try:
                asset = gh.releases.upload_asset("owner", "repo", 123, temp_path, name="test.txt")
                assert asset["id"] == 456
                assert asset["name"] == "test.txt"
            finally:
                Path(temp_path).unlink()

    def test_delete_asset(self, httpx_mock: HTTPXMock):
        """Delete a release asset."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/assets/456",
            method="DELETE",
            status_code=204,
        )

        with GitHub(token="test-token") as gh:
            gh.releases.delete_asset("owner", "repo", 456)


class TestRepoReleases:
    """Tests for repository-bound release operations."""

    def test_repo_releases_list(self, httpx_mock: HTTPXMock):
        """List releases via repo interface."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases?per_page=30&page=1",
            json=[{"id": 1, "tag_name": "v1.0.0"}],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases?per_page=30&page=2",
            json=[],
        )

        with GitHub(token="test-token") as gh:
            repo = gh.repo("owner/repo")
            releases = list(repo.releases.list())
            assert len(releases) == 1
            assert releases[0]["tag_name"] == "v1.0.0"

    def test_repo_releases_create(self, httpx_mock: HTTPXMock):
        """Create release via repo interface."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases",
            method="POST",
            json={"id": 123, "tag_name": "v1.0.0"},
        )

        with GitHub(token="test-token") as gh:
            repo = gh.repo("owner/repo")
            release = repo.releases.create(tag_name="v1.0.0")
            assert release["tag_name"] == "v1.0.0"

    def test_repo_releases_get_latest(self, httpx_mock: HTTPXMock):
        """Get latest release via repo interface."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/releases/latest",
            json={"id": 123, "tag_name": "v1.0.0"},
        )

        with GitHub(token="test-token") as gh:
            repo = gh.repo("owner/repo")
            release = repo.releases.get_latest()
            assert release["tag_name"] == "v1.0.0"
