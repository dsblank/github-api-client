"""Issues resource handlers."""

from __future__ import annotations

from typing import Any, Iterator, AsyncIterator

from github_rest_api.resources.base import Resource, AsyncResource


class IssuesResource(Resource):
    """Synchronous issue operations."""

    def get(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Get an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.

        Returns:
            Issue data.
        """
        return self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")

    def list(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        labels: str | None = None,
        assignee: str | None = None,
        creator: str | None = None,
        mentioned: str | None = None,
        milestone: str | int | None = None,
        since: str | None = None,
    ) -> Iterator[dict[str, Any]]:
        """List issues for a repository (excludes pull requests).

        Args:
            owner: Repository owner.
            repo: Repository name.
            state: State filter (open, closed, all).
            sort: Sort field (created, updated, comments).
            direction: Sort direction (asc, desc).
            labels: Comma-separated list of label names.
            assignee: Filter by assignee username, or "none" / "*".
            creator: Filter by issue creator username.
            mentioned: Filter by mentioned username.
            milestone: Filter by milestone number or "*" / "none".
            since: Only issues updated after this time (ISO 8601 format).

        Yields:
            Issue data dictionaries (pull requests are excluded).
        """
        params: dict[str, Any] = {
            "state": state,
            "sort": sort,
            "direction": direction,
        }
        if labels:
            params["labels"] = labels
        if assignee:
            params["assignee"] = assignee
        if creator:
            params["creator"] = creator
        if mentioned:
            params["mentioned"] = mentioned
        if milestone is not None:
            params["milestone"] = milestone
        if since:
            params["since"] = since
        for item in self._paginate("GET", f"/repos/{owner}/{repo}/issues", params=params):
            if "pull_request" not in item:
                yield item

    def create(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: int | None = None,
    ) -> dict[str, Any]:
        """Create an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            title: Issue title.
            body: Issue body.
            labels: List of label names.
            assignees: List of usernames to assign.
            milestone: Milestone number.

        Returns:
            Created issue data.
        """
        data: dict[str, Any] = {"title": title}
        if body:
            data["body"] = body
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone
        return self._request("POST", f"/repos/{owner}/{repo}/issues", json=data)

    def update(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.
            **kwargs: Fields to update (title, body, state, labels, etc.).

        Returns:
            Updated issue data.
        """
        return self._request(
            "PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json=kwargs
        )

    def close(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Close an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.

        Returns:
            Updated issue data.
        """
        return self.update(owner, repo, issue_number, state="closed")

    def reopen(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Reopen a closed issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.

        Returns:
            Updated issue data.
        """
        return self.update(owner, repo, issue_number, state="open")

    def lock(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        lock_reason: str | None = None,
    ) -> None:
        """Lock an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.
            lock_reason: Reason (off-topic, too heated, resolved, spam).
        """
        data = {}
        if lock_reason:
            data["lock_reason"] = lock_reason
        self._request(
            "PUT", f"/repos/{owner}/{repo}/issues/{issue_number}/lock", json=data
        )

    def unlock(self, owner: str, repo: str, issue_number: int) -> None:
        """Unlock an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.
        """
        self._request("DELETE", f"/repos/{owner}/{repo}/issues/{issue_number}/lock")

    def list_comments(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> Iterator[dict[str, Any]]:
        """List comments on an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.

        Yields:
            Comment data dictionaries.
        """
        yield from self._paginate(
            "GET", f"/repos/{owner}/{repo}/issues/{issue_number}/comments"
        )

    def create_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
    ) -> dict[str, Any]:
        """Create a comment on an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.
            body: Comment body.

        Returns:
            Created comment data.
        """
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": body},
        )

    def list_labels(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> Iterator[dict[str, Any]]:
        """List labels on an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.

        Yields:
            Label data dictionaries.
        """
        yield from self._paginate(
            "GET", f"/repos/{owner}/{repo}/issues/{issue_number}/labels"
        )

    def add_labels(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        labels: list[str],
    ) -> list[dict[str, Any]]:
        """Add labels to an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.
            labels: List of label names to add.

        Returns:
            List of all labels on the issue.
        """
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/labels",
            json={"labels": labels},
        )

    def remove_label(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        label: str,
    ) -> None:
        """Remove a label from an issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.
            label: Label name to remove.
        """
        self._request(
            "DELETE", f"/repos/{owner}/{repo}/issues/{issue_number}/labels/{label}"
        )


class AsyncIssuesResource(AsyncResource):
    """Asynchronous issue operations."""

    async def get(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Get an issue."""
        return await self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")

    async def list(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        labels: str | None = None,
        assignee: str | None = None,
        creator: str | None = None,
        mentioned: str | None = None,
        milestone: str | int | None = None,
        since: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """List issues for a repository (excludes pull requests)."""
        params: dict[str, Any] = {
            "state": state,
            "sort": sort,
            "direction": direction,
        }
        if labels:
            params["labels"] = labels
        if assignee:
            params["assignee"] = assignee
        if creator:
            params["creator"] = creator
        if mentioned:
            params["mentioned"] = mentioned
        if milestone is not None:
            params["milestone"] = milestone
        if since:
            params["since"] = since
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/issues", params=params
        ):
            if "pull_request" not in item:
                yield item

    async def create(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: int | None = None,
    ) -> dict[str, Any]:
        """Create an issue."""
        data: dict[str, Any] = {"title": title}
        if body:
            data["body"] = body
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone
        return await self._request("POST", f"/repos/{owner}/{repo}/issues", json=data)

    async def update(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update an issue."""
        return await self._request(
            "PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json=kwargs
        )

    async def close(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Close an issue."""
        return await self.update(owner, repo, issue_number, state="closed")

    async def reopen(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Reopen a closed issue."""
        return await self.update(owner, repo, issue_number, state="open")

    async def lock(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        lock_reason: str | None = None,
    ) -> None:
        """Lock an issue."""
        data = {}
        if lock_reason:
            data["lock_reason"] = lock_reason
        await self._request(
            "PUT", f"/repos/{owner}/{repo}/issues/{issue_number}/lock", json=data
        )

    async def unlock(self, owner: str, repo: str, issue_number: int) -> None:
        """Unlock an issue."""
        await self._request(
            "DELETE", f"/repos/{owner}/{repo}/issues/{issue_number}/lock"
        )

    async def list_comments(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> AsyncIterator[dict[str, Any]]:
        """List comments on an issue."""
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/issues/{issue_number}/comments"
        ):
            yield item

    async def create_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
    ) -> dict[str, Any]:
        """Create a comment on an issue."""
        return await self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            json={"body": body},
        )

    async def list_labels(
        self,
        owner: str,
        repo: str,
        issue_number: int,
    ) -> AsyncIterator[dict[str, Any]]:
        """List labels on an issue."""
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/issues/{issue_number}/labels"
        ):
            yield item

    async def add_labels(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        labels: list[str],
    ) -> list[dict[str, Any]]:
        """Add labels to an issue."""
        return await self._request(
            "POST",
            f"/repos/{owner}/{repo}/issues/{issue_number}/labels",
            json={"labels": labels},
        )

    async def remove_label(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        label: str,
    ) -> None:
        """Remove a label from an issue."""
        await self._request(
            "DELETE", f"/repos/{owner}/{repo}/issues/{issue_number}/labels/{label}"
        )
