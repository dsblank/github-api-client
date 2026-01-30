"""Repository resource handlers."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

from github_api_client.resources.base import AsyncResource, Resource


class ReposResource(Resource):
    """Synchronous repository operations."""

    def get(self, owner: str, repo: str) -> dict[str, Any]:
        """Get a repository.

        Args:
            owner: Repository owner (user or organization).
            repo: Repository name.

        Returns:
            Repository data.
        """
        return self._request("GET", f"/repos/{owner}/{repo}")

    def list_for_user(
        self,
        username: str,
        type: str = "owner",
        sort: str = "full_name",
        direction: str = "asc",
    ) -> Iterator[dict[str, Any]]:
        """List repositories for a user.

        Args:
            username: The username.
            type: Type filter (all, owner, member).
            sort: Sort field (created, updated, pushed, full_name).
            direction: Sort direction (asc, desc).

        Yields:
            Repository data dictionaries.
        """
        params = {"type": type, "sort": sort, "direction": direction}
        yield from self._paginate("GET", f"/users/{username}/repos", params=params)

    def list_for_org(
        self,
        org: str,
        type: str = "all",
        sort: str = "full_name",
        direction: str = "asc",
    ) -> Iterator[dict[str, Any]]:
        """List repositories for an organization.

        Args:
            org: Organization name.
            type: Type filter (all, public, private, forks, sources, member).
            sort: Sort field (created, updated, pushed, full_name).
            direction: Sort direction (asc, desc).

        Yields:
            Repository data dictionaries.
        """
        params = {"type": type, "sort": sort, "direction": direction}
        yield from self._paginate("GET", f"/orgs/{org}/repos", params=params)

    def list_for_authenticated_user(
        self,
        visibility: str = "all",
        affiliation: str = "owner,collaborator,organization_member",
        sort: str = "full_name",
        direction: str = "asc",
    ) -> Iterator[dict[str, Any]]:
        """List repositories for the authenticated user.

        Args:
            visibility: Visibility filter (all, public, private).
            affiliation: Comma-separated list of affiliations.
            sort: Sort field (created, updated, pushed, full_name).
            direction: Sort direction (asc, desc).

        Yields:
            Repository data dictionaries.
        """
        params = {
            "visibility": visibility,
            "affiliation": affiliation,
            "sort": sort,
            "direction": direction,
        }
        yield from self._paginate("GET", "/user/repos", params=params)

    def create(
        self,
        name: str,
        description: str | None = None,
        private: bool = False,
        auto_init: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a repository for the authenticated user.

        Args:
            name: Repository name.
            description: Repository description.
            private: Whether the repository is private.
            auto_init: Initialize with a README.
            **kwargs: Additional repository options.

        Returns:
            Created repository data.
        """
        data = {
            "name": name,
            "private": private,
            "auto_init": auto_init,
            **kwargs,
        }
        if description:
            data["description"] = description
        return self._request("POST", "/user/repos", json=data)

    def create_for_org(
        self,
        org: str,
        name: str,
        description: str | None = None,
        private: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a repository in an organization.

        Args:
            org: Organization name.
            name: Repository name.
            description: Repository description.
            private: Whether the repository is private.
            **kwargs: Additional repository options.

        Returns:
            Created repository data.
        """
        data = {"name": name, "private": private, **kwargs}
        if description:
            data["description"] = description
        return self._request("POST", f"/orgs/{org}/repos", json=data)

    def update(
        self,
        owner: str,
        repo: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            **kwargs: Fields to update (name, description, private, etc.).

        Returns:
            Updated repository data.
        """
        return self._request("PATCH", f"/repos/{owner}/{repo}", json=kwargs)

    def delete(self, owner: str, repo: str) -> None:
        """Delete a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
        """
        self._request("DELETE", f"/repos/{owner}/{repo}")

    def list_contributors(
        self,
        owner: str,
        repo: str,
        anon: bool = False,
    ) -> Iterator[dict[str, Any]]:
        """List repository contributors.

        Args:
            owner: Repository owner.
            repo: Repository name.
            anon: Include anonymous contributors.

        Yields:
            Contributor data dictionaries.
        """
        params = {"anon": str(anon).lower()}
        yield from self._paginate("GET", f"/repos/{owner}/{repo}/contributors", params=params)

    def list_languages(self, owner: str, repo: str) -> dict[str, int]:
        """List languages used in a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Dictionary mapping language names to byte counts.
        """
        return self._request("GET", f"/repos/{owner}/{repo}/languages")

    def list_tags(self, owner: str, repo: str) -> Iterator[dict[str, Any]]:
        """List repository tags.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Yields:
            Tag data dictionaries.
        """
        yield from self._paginate("GET", f"/repos/{owner}/{repo}/tags")

    def list_branches(
        self,
        owner: str,
        repo: str,
        protected: bool | None = None,
    ) -> Iterator[dict[str, Any]]:
        """List repository branches.

        Args:
            owner: Repository owner.
            repo: Repository name.
            protected: Filter by protected status.

        Yields:
            Branch data dictionaries.
        """
        params: dict[str, Any] = {}
        if protected is not None:
            params["protected"] = str(protected).lower()
        yield from self._paginate("GET", f"/repos/{owner}/{repo}/branches", params=params)


class AsyncReposResource(AsyncResource):
    """Asynchronous repository operations."""

    async def get(self, owner: str, repo: str) -> dict[str, Any]:
        """Get a repository."""
        return await self._request("GET", f"/repos/{owner}/{repo}")

    async def list_for_user(
        self,
        username: str,
        type: str = "owner",
        sort: str = "full_name",
        direction: str = "asc",
    ) -> AsyncIterator[dict[str, Any]]:
        """List repositories for a user."""
        params = {"type": type, "sort": sort, "direction": direction}
        async for item in self._paginate("GET", f"/users/{username}/repos", params=params):
            yield item

    async def list_for_org(
        self,
        org: str,
        type: str = "all",
        sort: str = "full_name",
        direction: str = "asc",
    ) -> AsyncIterator[dict[str, Any]]:
        """List repositories for an organization."""
        params = {"type": type, "sort": sort, "direction": direction}
        async for item in self._paginate("GET", f"/orgs/{org}/repos", params=params):
            yield item

    async def list_for_authenticated_user(
        self,
        visibility: str = "all",
        affiliation: str = "owner,collaborator,organization_member",
        sort: str = "full_name",
        direction: str = "asc",
    ) -> AsyncIterator[dict[str, Any]]:
        """List repositories for the authenticated user."""
        params = {
            "visibility": visibility,
            "affiliation": affiliation,
            "sort": sort,
            "direction": direction,
        }
        async for item in self._paginate("GET", "/user/repos", params=params):
            yield item

    async def create(
        self,
        name: str,
        description: str | None = None,
        private: bool = False,
        auto_init: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a repository for the authenticated user."""
        data = {
            "name": name,
            "private": private,
            "auto_init": auto_init,
            **kwargs,
        }
        if description:
            data["description"] = description
        return await self._request("POST", "/user/repos", json=data)

    async def create_for_org(
        self,
        org: str,
        name: str,
        description: str | None = None,
        private: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a repository in an organization."""
        data = {"name": name, "private": private, **kwargs}
        if description:
            data["description"] = description
        return await self._request("POST", f"/orgs/{org}/repos", json=data)

    async def update(
        self,
        owner: str,
        repo: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a repository."""
        return await self._request("PATCH", f"/repos/{owner}/{repo}", json=kwargs)

    async def delete(self, owner: str, repo: str) -> None:
        """Delete a repository."""
        await self._request("DELETE", f"/repos/{owner}/{repo}")

    async def list_contributors(
        self,
        owner: str,
        repo: str,
        anon: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """List repository contributors."""
        params = {"anon": str(anon).lower()}
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/contributors", params=params
        ):
            yield item

    async def list_languages(self, owner: str, repo: str) -> dict[str, int]:
        """List languages used in a repository."""
        return await self._request("GET", f"/repos/{owner}/{repo}/languages")

    async def list_tags(self, owner: str, repo: str) -> AsyncIterator[dict[str, Any]]:
        """List repository tags."""
        async for item in self._paginate("GET", f"/repos/{owner}/{repo}/tags"):
            yield item

    async def list_branches(
        self,
        owner: str,
        repo: str,
        protected: bool | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """List repository branches."""
        params: dict[str, Any] = {}
        if protected is not None:
            params["protected"] = str(protected).lower()
        async for item in self._paginate("GET", f"/repos/{owner}/{repo}/branches", params=params):
            yield item
