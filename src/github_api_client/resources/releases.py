"""Releases resource handlers."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

from github_api_client.resources.base import AsyncResource, Resource


class ReleasesResource(Resource):
    """Synchronous release operations."""

    def list(self, owner: str, repo: str) -> Iterator[dict[str, Any]]:
        """List releases for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Yields:
            Release data dictionaries.
        """
        yield from self._paginate("GET", f"/repos/{owner}/{repo}/releases")

    def get(self, owner: str, repo: str, release_id: int) -> dict[str, Any]:
        """Get a release by ID.

        Args:
            owner: Repository owner.
            repo: Repository name.
            release_id: Release ID.

        Returns:
            Release data.
        """
        return self._request("GET", f"/repos/{owner}/{repo}/releases/{release_id}")

    def get_latest(self, owner: str, repo: str) -> dict[str, Any]:
        """Get the latest release.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Latest release data.
        """
        return self._request("GET", f"/repos/{owner}/{repo}/releases/latest")

    def get_by_tag(self, owner: str, repo: str, tag: str) -> dict[str, Any]:
        """Get a release by tag name.

        Args:
            owner: Repository owner.
            repo: Repository name.
            tag: Tag name.

        Returns:
            Release data.
        """
        return self._request("GET", f"/repos/{owner}/{repo}/releases/tags/{tag}")

    def create(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        name: str | None = None,
        body: str | None = None,
        draft: bool = False,
        prerelease: bool = False,
        target_commitish: str | None = None,
        generate_release_notes: bool = False,
    ) -> dict[str, Any]:
        """Create a release.

        Args:
            owner: Repository owner.
            repo: Repository name.
            tag_name: The name of the tag for this release.
            name: The name of the release.
            body: Text describing the release.
            draft: True to create a draft release.
            prerelease: True to mark as a prerelease.
            target_commitish: The commitish value for the tag (branch or SHA).
            generate_release_notes: Auto-generate release notes.

        Returns:
            Created release data.
        """
        data: dict[str, Any] = {
            "tag_name": tag_name,
            "draft": draft,
            "prerelease": prerelease,
            "generate_release_notes": generate_release_notes,
        }
        if name:
            data["name"] = name
        if body:
            data["body"] = body
        if target_commitish:
            data["target_commitish"] = target_commitish

        return self._request("POST", f"/repos/{owner}/{repo}/releases", json=data)

    def update(
        self,
        owner: str,
        repo: str,
        release_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a release.

        Args:
            owner: Repository owner.
            repo: Repository name.
            release_id: Release ID.
            **kwargs: Fields to update (tag_name, name, body, draft, prerelease).

        Returns:
            Updated release data.
        """
        return self._request("PATCH", f"/repos/{owner}/{repo}/releases/{release_id}", json=kwargs)

    def delete(self, owner: str, repo: str, release_id: int) -> None:
        """Delete a release.

        Args:
            owner: Repository owner.
            repo: Repository name.
            release_id: Release ID.
        """
        self._request("DELETE", f"/repos/{owner}/{repo}/releases/{release_id}")

    def list_assets(self, owner: str, repo: str, release_id: int) -> Iterator[dict[str, Any]]:
        """List assets for a release.

        Args:
            owner: Repository owner.
            repo: Repository name.
            release_id: Release ID.

        Yields:
            Asset data dictionaries.
        """
        yield from self._paginate("GET", f"/repos/{owner}/{repo}/releases/{release_id}/assets")

    def get_asset(self, owner: str, repo: str, asset_id: int) -> dict[str, Any]:
        """Get a release asset.

        Args:
            owner: Repository owner.
            repo: Repository name.
            asset_id: Asset ID.

        Returns:
            Asset data.
        """
        return self._request("GET", f"/repos/{owner}/{repo}/releases/assets/{asset_id}")

    def upload_asset(
        self,
        owner: str,
        repo: str,
        release_id: int,
        file_path: str | Path,
        name: str | None = None,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        """Upload a release asset.

        Args:
            owner: Repository owner.
            repo: Repository name.
            release_id: Release ID.
            file_path: Path to the file to upload.
            name: Name for the asset (defaults to filename).
            content_type: MIME type of the asset.

        Returns:
            Created asset data.
        """
        path = Path(file_path)
        asset_name = name or path.name

        with open(path, "rb") as f:
            content = f.read()

        # Upload URL uses uploads.github.com instead of api.github.com
        upload_url = f"https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets"

        response = self._client._client.post(
            upload_url,
            params={"name": asset_name},
            content=content,
            headers={"Content-Type": content_type},
        )

        if response.status_code >= 400:
            from github_api_client.client import _handle_error_response

            _handle_error_response(response)

        return response.json()

    def delete_asset(self, owner: str, repo: str, asset_id: int) -> None:
        """Delete a release asset.

        Args:
            owner: Repository owner.
            repo: Repository name.
            asset_id: Asset ID.
        """
        self._request("DELETE", f"/repos/{owner}/{repo}/releases/assets/{asset_id}")


class AsyncReleasesResource(AsyncResource):
    """Asynchronous release operations."""

    async def list(self, owner: str, repo: str) -> AsyncIterator[dict[str, Any]]:
        """List releases for a repository."""
        async for item in self._paginate("GET", f"/repos/{owner}/{repo}/releases"):
            yield item

    async def get(self, owner: str, repo: str, release_id: int) -> dict[str, Any]:
        """Get a release by ID."""
        return await self._request("GET", f"/repos/{owner}/{repo}/releases/{release_id}")

    async def get_latest(self, owner: str, repo: str) -> dict[str, Any]:
        """Get the latest release."""
        return await self._request("GET", f"/repos/{owner}/{repo}/releases/latest")

    async def get_by_tag(self, owner: str, repo: str, tag: str) -> dict[str, Any]:
        """Get a release by tag name."""
        return await self._request("GET", f"/repos/{owner}/{repo}/releases/tags/{tag}")

    async def create(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        name: str | None = None,
        body: str | None = None,
        draft: bool = False,
        prerelease: bool = False,
        target_commitish: str | None = None,
        generate_release_notes: bool = False,
    ) -> dict[str, Any]:
        """Create a release."""
        data: dict[str, Any] = {
            "tag_name": tag_name,
            "draft": draft,
            "prerelease": prerelease,
            "generate_release_notes": generate_release_notes,
        }
        if name:
            data["name"] = name
        if body:
            data["body"] = body
        if target_commitish:
            data["target_commitish"] = target_commitish

        return await self._request("POST", f"/repos/{owner}/{repo}/releases", json=data)

    async def update(
        self,
        owner: str,
        repo: str,
        release_id: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a release."""
        return await self._request(
            "PATCH", f"/repos/{owner}/{repo}/releases/{release_id}", json=kwargs
        )

    async def delete(self, owner: str, repo: str, release_id: int) -> None:
        """Delete a release."""
        await self._request("DELETE", f"/repos/{owner}/{repo}/releases/{release_id}")

    async def list_assets(
        self, owner: str, repo: str, release_id: int
    ) -> AsyncIterator[dict[str, Any]]:
        """List assets for a release."""
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/releases/{release_id}/assets"
        ):
            yield item

    async def get_asset(self, owner: str, repo: str, asset_id: int) -> dict[str, Any]:
        """Get a release asset."""
        return await self._request("GET", f"/repos/{owner}/{repo}/releases/assets/{asset_id}")

    async def upload_asset(
        self,
        owner: str,
        repo: str,
        release_id: int,
        file_path: str | Path,
        name: str | None = None,
        content_type: str = "application/octet-stream",
    ) -> dict[str, Any]:
        """Upload a release asset."""
        path = Path(file_path)
        asset_name = name or path.name

        with open(path, "rb") as f:
            content = f.read()

        upload_url = f"https://uploads.github.com/repos/{owner}/{repo}/releases/{release_id}/assets"

        response = await self._client._client.post(
            upload_url,
            params={"name": asset_name},
            content=content,
            headers={"Content-Type": content_type},
        )

        if response.status_code >= 400:
            from github_api_client.client import _handle_error_response

            _handle_error_response(response)

        return response.json()

    async def delete_asset(self, owner: str, repo: str, asset_id: int) -> None:
        """Delete a release asset."""
        await self._request("DELETE", f"/repos/{owner}/{repo}/releases/assets/{asset_id}")
