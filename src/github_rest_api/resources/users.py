"""Users resource handlers."""

from __future__ import annotations

from typing import Any, Iterator, AsyncIterator

from github_rest_api.resources.base import Resource, AsyncResource


class UsersResource(Resource):
    """Synchronous user operations."""

    def get(self, username: str) -> dict[str, Any]:
        """Get a user by username.

        Args:
            username: The username.

        Returns:
            User data.
        """
        return self._request("GET", f"/users/{username}")

    def get_authenticated(self) -> dict[str, Any]:
        """Get the authenticated user.

        Returns:
            Authenticated user data.
        """
        return self._request("GET", "/user")

    def update_authenticated(self, **kwargs: Any) -> dict[str, Any]:
        """Update the authenticated user.

        Args:
            **kwargs: Fields to update (name, email, blog, company, location, bio).

        Returns:
            Updated user data.
        """
        return self._request("PATCH", "/user", json=kwargs)

    def list_followers(self, username: str) -> Iterator[dict[str, Any]]:
        """List followers of a user.

        Args:
            username: The username.

        Yields:
            User data dictionaries.
        """
        yield from self._paginate("GET", f"/users/{username}/followers")

    def list_following(self, username: str) -> Iterator[dict[str, Any]]:
        """List users that a user is following.

        Args:
            username: The username.

        Yields:
            User data dictionaries.
        """
        yield from self._paginate("GET", f"/users/{username}/following")

    def is_following(self, username: str, target: str) -> bool:
        """Check if a user follows another user.

        Args:
            username: The username.
            target: The target username.

        Returns:
            True if following, False otherwise.
        """
        try:
            self._request("GET", f"/users/{username}/following/{target}")
            return True
        except Exception:
            return False

    def follow(self, username: str) -> None:
        """Follow a user (as authenticated user).

        Args:
            username: The username to follow.
        """
        self._request("PUT", f"/user/following/{username}")

    def unfollow(self, username: str) -> None:
        """Unfollow a user (as authenticated user).

        Args:
            username: The username to unfollow.
        """
        self._request("DELETE", f"/user/following/{username}")

    def list_emails(self) -> list[dict[str, Any]]:
        """List email addresses for the authenticated user.

        Returns:
            List of email data dictionaries.
        """
        return self._request("GET", "/user/emails")

    def add_emails(self, emails: list[str]) -> list[dict[str, Any]]:
        """Add email addresses to the authenticated user.

        Args:
            emails: List of email addresses to add.

        Returns:
            List of added email data dictionaries.
        """
        return self._request("POST", "/user/emails", json={"emails": emails})

    def delete_emails(self, emails: list[str]) -> None:
        """Delete email addresses from the authenticated user.

        Args:
            emails: List of email addresses to delete.
        """
        self._request("DELETE", "/user/emails", json={"emails": emails})

    def list_ssh_keys(self, username: str) -> Iterator[dict[str, Any]]:
        """List public SSH keys for a user.

        Args:
            username: The username.

        Yields:
            SSH key data dictionaries.
        """
        yield from self._paginate("GET", f"/users/{username}/keys")

    def list_gpg_keys(self, username: str) -> Iterator[dict[str, Any]]:
        """List GPG keys for a user.

        Args:
            username: The username.

        Yields:
            GPG key data dictionaries.
        """
        yield from self._paginate("GET", f"/users/{username}/gpg_keys")


class AsyncUsersResource(AsyncResource):
    """Asynchronous user operations."""

    async def get(self, username: str) -> dict[str, Any]:
        """Get a user by username."""
        return await self._request("GET", f"/users/{username}")

    async def get_authenticated(self) -> dict[str, Any]:
        """Get the authenticated user."""
        return await self._request("GET", "/user")

    async def update_authenticated(self, **kwargs: Any) -> dict[str, Any]:
        """Update the authenticated user."""
        return await self._request("PATCH", "/user", json=kwargs)

    async def list_followers(self, username: str) -> AsyncIterator[dict[str, Any]]:
        """List followers of a user."""
        async for item in self._paginate("GET", f"/users/{username}/followers"):
            yield item

    async def list_following(self, username: str) -> AsyncIterator[dict[str, Any]]:
        """List users that a user is following."""
        async for item in self._paginate("GET", f"/users/{username}/following"):
            yield item

    async def is_following(self, username: str, target: str) -> bool:
        """Check if a user follows another user."""
        try:
            await self._request("GET", f"/users/{username}/following/{target}")
            return True
        except Exception:
            return False

    async def follow(self, username: str) -> None:
        """Follow a user (as authenticated user)."""
        await self._request("PUT", f"/user/following/{username}")

    async def unfollow(self, username: str) -> None:
        """Unfollow a user (as authenticated user)."""
        await self._request("DELETE", f"/user/following/{username}")

    async def list_emails(self) -> list[dict[str, Any]]:
        """List email addresses for the authenticated user."""
        return await self._request("GET", "/user/emails")

    async def add_emails(self, emails: list[str]) -> list[dict[str, Any]]:
        """Add email addresses to the authenticated user."""
        return await self._request("POST", "/user/emails", json={"emails": emails})

    async def delete_emails(self, emails: list[str]) -> None:
        """Delete email addresses from the authenticated user."""
        await self._request("DELETE", "/user/emails", json={"emails": emails})

    async def list_ssh_keys(self, username: str) -> AsyncIterator[dict[str, Any]]:
        """List public SSH keys for a user."""
        async for item in self._paginate("GET", f"/users/{username}/keys"):
            yield item

    async def list_gpg_keys(self, username: str) -> AsyncIterator[dict[str, Any]]:
        """List GPG keys for a user."""
        async for item in self._paginate("GET", f"/users/{username}/gpg_keys"):
            yield item
