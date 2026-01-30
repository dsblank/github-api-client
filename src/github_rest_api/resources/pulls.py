"""Pull requests resource handlers."""

from __future__ import annotations

from typing import Any, Iterator, AsyncIterator

from github_rest_api.resources.base import Resource, AsyncResource


class PullsResource(Resource):
    """Synchronous pull request operations."""

    def get(self, owner: str, repo: str, pull_number: int) -> dict[str, Any]:
        """Get a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.

        Returns:
            Pull request data.
        """
        return self._request("GET", f"/repos/{owner}/{repo}/pulls/{pull_number}")

    def list(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        head: str | None = None,
        base: str | None = None,
    ) -> Iterator[dict[str, Any]]:
        """List pull requests for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.
            state: State filter (open, closed, all).
            sort: Sort field (created, updated, popularity, long-running).
            direction: Sort direction (asc, desc).
            head: Filter by head user/org and branch (format: "user:branch").
            base: Filter by base branch name.

        Yields:
            Pull request data dictionaries.
        """
        params: dict[str, Any] = {
            "state": state,
            "sort": sort,
            "direction": direction,
        }
        if head:
            params["head"] = head
        if base:
            params["base"] = base
        yield from self._paginate("GET", f"/repos/{owner}/{repo}/pulls", params=params)

    def create(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str | None = None,
        draft: bool = False,
        maintainer_can_modify: bool = True,
    ) -> dict[str, Any]:
        """Create a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            title: Pull request title.
            head: Branch containing changes (format: "user:branch" for cross-repo).
            base: Branch to merge into.
            body: Pull request body.
            draft: Create as draft PR.
            maintainer_can_modify: Allow maintainer edits.

        Returns:
            Created pull request data.
        """
        data: dict[str, Any] = {
            "title": title,
            "head": head,
            "base": base,
            "draft": draft,
            "maintainer_can_modify": maintainer_can_modify,
        }
        if body:
            data["body"] = body
        return self._request("POST", f"/repos/{owner}/{repo}/pulls", json=data)

    def update(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.
            **kwargs: Fields to update (title, body, state, base).

        Returns:
            Updated pull request data.
        """
        return self._request(
            "PATCH", f"/repos/{owner}/{repo}/pulls/{pull_number}", json=kwargs
        )

    def close(self, owner: str, repo: str, pull_number: int) -> dict[str, Any]:
        """Close a pull request without merging.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.

        Returns:
            Updated pull request data.
        """
        return self.update(owner, repo, pull_number, state="closed")

    def merge(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        commit_title: str | None = None,
        commit_message: str | None = None,
        merge_method: str = "merge",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Merge a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.
            commit_title: Title for the merge commit.
            commit_message: Message for the merge commit.
            merge_method: Merge method (merge, squash, rebase).
            sha: SHA that head must match to allow merge.

        Returns:
            Merge result data.
        """
        data: dict[str, Any] = {"merge_method": merge_method}
        if commit_title:
            data["commit_title"] = commit_title
        if commit_message:
            data["commit_message"] = commit_message
        if sha:
            data["sha"] = sha
        return self._request(
            "PUT", f"/repos/{owner}/{repo}/pulls/{pull_number}/merge", json=data
        )

    def is_merged(self, owner: str, repo: str, pull_number: int) -> bool:
        """Check if a pull request has been merged.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.

        Returns:
            True if merged, False otherwise.
        """
        try:
            self._request("GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/merge")
            return True
        except Exception:
            return False

    def list_commits(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> Iterator[dict[str, Any]]:
        """List commits on a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.

        Yields:
            Commit data dictionaries.
        """
        yield from self._paginate(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/commits"
        )

    def list_files(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> Iterator[dict[str, Any]]:
        """List files changed in a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.

        Yields:
            File data dictionaries.
        """
        yield from self._paginate(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/files"
        )

    def list_reviews(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> Iterator[dict[str, Any]]:
        """List reviews on a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.

        Yields:
            Review data dictionaries.
        """
        yield from self._paginate(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        )

    def create_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str | None = None,
        event: str = "COMMENT",
        comments: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a review on a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.
            body: Review body.
            event: Review event (APPROVE, REQUEST_CHANGES, COMMENT).
            comments: List of review comments.

        Returns:
            Created review data.
        """
        data: dict[str, Any] = {"event": event}
        if body:
            data["body"] = body
        if comments:
            data["comments"] = comments
        return self._request(
            "POST", f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews", json=data
        )

    def request_reviewers(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        reviewers: list[str] | None = None,
        team_reviewers: list[str] | None = None,
    ) -> dict[str, Any]:
        """Request reviewers for a pull request.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pull_number: Pull request number.
            reviewers: List of usernames to request.
            team_reviewers: List of team slugs to request.

        Returns:
            Updated pull request data.
        """
        data: dict[str, Any] = {}
        if reviewers:
            data["reviewers"] = reviewers
        if team_reviewers:
            data["team_reviewers"] = team_reviewers
        return self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers",
            json=data,
        )


class AsyncPullsResource(AsyncResource):
    """Asynchronous pull request operations."""

    async def get(self, owner: str, repo: str, pull_number: int) -> dict[str, Any]:
        """Get a pull request."""
        return await self._request("GET", f"/repos/{owner}/{repo}/pulls/{pull_number}")

    async def list(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        head: str | None = None,
        base: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """List pull requests for a repository."""
        params: dict[str, Any] = {
            "state": state,
            "sort": sort,
            "direction": direction,
        }
        if head:
            params["head"] = head
        if base:
            params["base"] = base
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/pulls", params=params
        ):
            yield item

    async def create(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str | None = None,
        draft: bool = False,
        maintainer_can_modify: bool = True,
    ) -> dict[str, Any]:
        """Create a pull request."""
        data: dict[str, Any] = {
            "title": title,
            "head": head,
            "base": base,
            "draft": draft,
            "maintainer_can_modify": maintainer_can_modify,
        }
        if body:
            data["body"] = body
        return await self._request("POST", f"/repos/{owner}/{repo}/pulls", json=data)

    async def update(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Update a pull request."""
        return await self._request(
            "PATCH", f"/repos/{owner}/{repo}/pulls/{pull_number}", json=kwargs
        )

    async def close(self, owner: str, repo: str, pull_number: int) -> dict[str, Any]:
        """Close a pull request without merging."""
        return await self.update(owner, repo, pull_number, state="closed")

    async def merge(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        commit_title: str | None = None,
        commit_message: str | None = None,
        merge_method: str = "merge",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Merge a pull request."""
        data: dict[str, Any] = {"merge_method": merge_method}
        if commit_title:
            data["commit_title"] = commit_title
        if commit_message:
            data["commit_message"] = commit_message
        if sha:
            data["sha"] = sha
        return await self._request(
            "PUT", f"/repos/{owner}/{repo}/pulls/{pull_number}/merge", json=data
        )

    async def is_merged(self, owner: str, repo: str, pull_number: int) -> bool:
        """Check if a pull request has been merged."""
        try:
            await self._request(
                "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/merge"
            )
            return True
        except Exception:
            return False

    async def list_commits(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> AsyncIterator[dict[str, Any]]:
        """List commits on a pull request."""
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/commits"
        ):
            yield item

    async def list_files(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> AsyncIterator[dict[str, Any]]:
        """List files changed in a pull request."""
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/files"
        ):
            yield item

    async def list_reviews(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> AsyncIterator[dict[str, Any]]:
        """List reviews on a pull request."""
        async for item in self._paginate(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews"
        ):
            yield item

    async def create_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str | None = None,
        event: str = "COMMENT",
        comments: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a review on a pull request."""
        data: dict[str, Any] = {"event": event}
        if body:
            data["body"] = body
        if comments:
            data["comments"] = comments
        return await self._request(
            "POST", f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews", json=data
        )

    async def request_reviewers(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        reviewers: list[str] | None = None,
        team_reviewers: list[str] | None = None,
    ) -> dict[str, Any]:
        """Request reviewers for a pull request."""
        data: dict[str, Any] = {}
        if reviewers:
            data["reviewers"] = reviewers
        if team_reviewers:
            data["team_reviewers"] = team_reviewers
        return await self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers",
            json=data,
        )
