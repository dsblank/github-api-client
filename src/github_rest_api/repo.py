"""Repository-bound interface for GitHub API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator, AsyncIterator

from github_rest_api.models import (
    Issue,
    PullRequest,
    Comment,
    Label,
    Repository,
    Branch,
    User,
)

if TYPE_CHECKING:
    from github_rest_api.client import GitHub, AsyncGitHub


class RepoIssues:
    """Issue operations bound to a specific repository."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo
        self._client = repo._client

    def get(self, issue_number: int) -> Issue:
        """Get an issue by number."""
        data = self._client.issues.get(self._repo.owner, self._repo.name, issue_number)
        return Issue.from_dict(data, self._repo)

    def list(
        self,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        labels: str | None = None,
        assignee: str | None = None,
        creator: str | None = None,
        mentioned: str | None = None,
        milestone: str | int | None = None,
        since: str | None = None,
    ) -> Iterator[Issue]:
        """List issues (excludes pull requests)."""
        for data in self._client.issues.list(
            self._repo.owner,
            self._repo.name,
            state=state,
            sort=sort,
            direction=direction,
            labels=labels,
            assignee=assignee,
            creator=creator,
            mentioned=mentioned,
            milestone=milestone,
            since=since,
        ):
            yield Issue.from_dict(data, self._repo)

    def create(
        self,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: int | None = None,
    ) -> Issue:
        """Create an issue."""
        data = self._client.issues.create(
            self._repo.owner,
            self._repo.name,
            title=title,
            body=body,
            labels=labels,
            assignees=assignees,
            milestone=milestone,
        )
        return Issue.from_dict(data, self._repo)

    def update(self, issue_number: int, **kwargs: Any) -> Issue:
        """Update an issue."""
        data = self._client.issues.update(
            self._repo.owner, self._repo.name, issue_number, **kwargs
        )
        return Issue.from_dict(data, self._repo)

    def close(self, issue_number: int) -> Issue:
        """Close an issue."""
        data = self._client.issues.close(self._repo.owner, self._repo.name, issue_number)
        return Issue.from_dict(data, self._repo)

    def reopen(self, issue_number: int) -> Issue:
        """Reopen an issue."""
        data = self._client.issues.reopen(self._repo.owner, self._repo.name, issue_number)
        return Issue.from_dict(data, self._repo)

    def lock(self, issue_number: int, lock_reason: str | None = None) -> None:
        """Lock an issue."""
        self._client.issues.lock(
            self._repo.owner, self._repo.name, issue_number, lock_reason
        )

    def unlock(self, issue_number: int) -> None:
        """Unlock an issue."""
        self._client.issues.unlock(self._repo.owner, self._repo.name, issue_number)

    def list_comments(self, issue_number: int) -> Iterator[Comment]:
        """List comments on an issue."""
        for data in self._client.issues.list_comments(
            self._repo.owner, self._repo.name, issue_number
        ):
            yield Comment.from_dict(data, self._repo)

    def create_comment(self, issue_number: int, body: str) -> Comment:
        """Create a comment on an issue."""
        data = self._client.issues.create_comment(
            self._repo.owner, self._repo.name, issue_number, body
        )
        return Comment.from_dict(data, self._repo)

    def add_labels(self, issue_number: int, labels: list[str]) -> list[Label]:
        """Add labels to an issue."""
        data = self._client.issues.add_labels(
            self._repo.owner, self._repo.name, issue_number, labels
        )
        return [Label.from_dict(l) for l in data]

    def remove_label(self, issue_number: int, label: str) -> None:
        """Remove a label from an issue."""
        self._client.issues.remove_label(
            self._repo.owner, self._repo.name, issue_number, label
        )


class RepoPulls:
    """Pull request operations bound to a specific repository."""

    def __init__(self, repo: Repo) -> None:
        self._repo = repo
        self._client = repo._client

    def get(self, pull_number: int) -> PullRequest:
        """Get a pull request by number."""
        data = self._client.pulls.get(self._repo.owner, self._repo.name, pull_number)
        return PullRequest.from_dict(data, self._repo)

    def list(
        self,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        head: str | None = None,
        base: str | None = None,
    ) -> Iterator[PullRequest]:
        """List pull requests."""
        for data in self._client.pulls.list(
            self._repo.owner,
            self._repo.name,
            state=state,
            sort=sort,
            direction=direction,
            head=head,
            base=base,
        ):
            yield PullRequest.from_dict(data, self._repo)

    def create(
        self,
        title: str,
        head: str,
        base: str,
        body: str | None = None,
        draft: bool = False,
        maintainer_can_modify: bool = True,
    ) -> PullRequest:
        """Create a pull request."""
        data = self._client.pulls.create(
            self._repo.owner,
            self._repo.name,
            title=title,
            head=head,
            base=base,
            body=body,
            draft=draft,
            maintainer_can_modify=maintainer_can_modify,
        )
        return PullRequest.from_dict(data, self._repo)

    def update(self, pull_number: int, **kwargs: Any) -> PullRequest:
        """Update a pull request."""
        data = self._client.pulls.update(
            self._repo.owner, self._repo.name, pull_number, **kwargs
        )
        return PullRequest.from_dict(data, self._repo)

    def close(self, pull_number: int) -> PullRequest:
        """Close a pull request without merging."""
        data = self._client.pulls.close(self._repo.owner, self._repo.name, pull_number)
        return PullRequest.from_dict(data, self._repo)

    def merge(
        self,
        pull_number: int,
        commit_title: str | None = None,
        commit_message: str | None = None,
        merge_method: str = "merge",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Merge a pull request."""
        return self._client.pulls.merge(
            self._repo.owner,
            self._repo.name,
            pull_number,
            commit_title=commit_title,
            commit_message=commit_message,
            merge_method=merge_method,
            sha=sha,
        )

    def is_merged(self, pull_number: int) -> bool:
        """Check if a pull request has been merged."""
        return self._client.pulls.is_merged(self._repo.owner, self._repo.name, pull_number)

    def list_commits(self, pull_number: int) -> Iterator[dict[str, Any]]:
        """List commits on a pull request."""
        return self._client.pulls.list_commits(
            self._repo.owner, self._repo.name, pull_number
        )

    def list_files(self, pull_number: int) -> Iterator[dict[str, Any]]:
        """List files changed in a pull request."""
        return self._client.pulls.list_files(
            self._repo.owner, self._repo.name, pull_number
        )

    def list_reviews(self, pull_number: int) -> Iterator[dict[str, Any]]:
        """List reviews on a pull request."""
        return self._client.pulls.list_reviews(
            self._repo.owner, self._repo.name, pull_number
        )

    def create_review(
        self,
        pull_number: int,
        body: str | None = None,
        event: str = "COMMENT",
        comments: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a review on a pull request."""
        return self._client.pulls.create_review(
            self._repo.owner,
            self._repo.name,
            pull_number,
            body=body,
            event=event,
            comments=comments,
        )

    def request_reviewers(
        self,
        pull_number: int,
        reviewers: list[str] | None = None,
        team_reviewers: list[str] | None = None,
    ) -> PullRequest:
        """Request reviewers for a pull request."""
        data = self._client.pulls.request_reviewers(
            self._repo.owner,
            self._repo.name,
            pull_number,
            reviewers=reviewers,
            team_reviewers=team_reviewers,
        )
        return PullRequest.from_dict(data, self._repo)


class Repo:
    """A GitHub repository with bound owner/repo context.

    Usage:
        >>> gh = GitHub()
        >>> repo = gh.repo("comet-ml", "opik")
        >>> # or: repo = gh.repo("comet-ml/opik")
        >>>
        >>> # List issues (returns Issue objects)
        >>> for issue in repo.issues.list():
        ...     print(issue.title)
        ...     issue.close()  # methods on the object
        >>>
        >>> # Get repo info
        >>> info = repo.get()
        >>> print(info.stars, info.language)
        >>>
        >>> # Convenience methods
        >>> repo.star()
        >>> repo.fork()
    """

    def __init__(self, client: GitHub, owner: str, name: str) -> None:
        self._client = client
        self.owner = owner
        self.name = name
        self.full_name = f"{owner}/{name}"

        # Bound resource handlers
        self.issues = RepoIssues(self)
        self.pulls = RepoPulls(self)

    def get(self) -> Repository:
        """Get repository details."""
        data = self._client.repos.get(self.owner, self.name)
        return Repository.from_dict(data, self._client)

    def update(self, **kwargs: Any) -> Repository:
        """Update repository settings."""
        data = self._client.repos.update(self.owner, self.name, **kwargs)
        return Repository.from_dict(data, self._client)

    def delete(self) -> None:
        """Delete this repository."""
        self._client.repos.delete(self.owner, self.name)

    def contributors(self, anon: bool = False) -> Iterator[User]:
        """List repository contributors."""
        for data in self._client.repos.list_contributors(self.owner, self.name, anon=anon):
            yield User.from_dict(data)

    def languages(self) -> dict[str, int]:
        """List languages used in this repository."""
        return self._client.repos.list_languages(self.owner, self.name)

    def tags(self) -> Iterator[dict[str, Any]]:
        """List repository tags."""
        return self._client.repos.list_tags(self.owner, self.name)

    def branches(self, protected: bool | None = None) -> Iterator[Branch]:
        """List repository branches."""
        for data in self._client.repos.list_branches(self.owner, self.name, protected=protected):
            yield Branch.from_dict(data)

    # Convenience shortcuts
    def star(self) -> None:
        """Star this repository."""
        self._client.request("PUT", f"/user/starred/{self.full_name}")

    def unstar(self) -> None:
        """Unstar this repository."""
        self._client.request("DELETE", f"/user/starred/{self.full_name}")

    def is_starred(self) -> bool:
        """Check if this repository is starred by the authenticated user."""
        try:
            self._client.request("GET", f"/user/starred/{self.full_name}")
            return True
        except Exception:
            return False

    def fork(self, organization: str | None = None) -> Repository:
        """Fork this repository.

        Args:
            organization: Optional organization to fork to.

        Returns:
            The forked repository.
        """
        data: dict[str, Any] = {}
        if organization:
            data["organization"] = organization
        result = self._client.request(
            "POST", f"/repos/{self.full_name}/forks", json=data if data else None
        )
        return Repository.from_dict(result, self._client)

    def subscribe(self) -> None:
        """Watch/subscribe to this repository."""
        self._client.request(
            "PUT",
            f"/repos/{self.full_name}/subscription",
            json={"subscribed": True},
        )

    def unsubscribe(self) -> None:
        """Unwatch/unsubscribe from this repository."""
        self._client.request("DELETE", f"/repos/{self.full_name}/subscription")

    def __repr__(self) -> str:
        return f"Repo({self.full_name!r})"


# Async versions


class AsyncRepoIssues:
    """Async issue operations bound to a specific repository."""

    def __init__(self, repo: AsyncRepo) -> None:
        self._repo = repo
        self._client = repo._client

    async def get(self, issue_number: int) -> Issue:
        """Get an issue by number."""
        data = await self._client.issues.get(
            self._repo.owner, self._repo.name, issue_number
        )
        return Issue.from_dict(data, self._repo)

    async def list(
        self,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        labels: str | None = None,
        assignee: str | None = None,
        creator: str | None = None,
        mentioned: str | None = None,
        milestone: str | int | None = None,
        since: str | None = None,
    ) -> AsyncIterator[Issue]:
        """List issues (excludes pull requests)."""
        async for data in self._client.issues.list(
            self._repo.owner,
            self._repo.name,
            state=state,
            sort=sort,
            direction=direction,
            labels=labels,
            assignee=assignee,
            creator=creator,
            mentioned=mentioned,
            milestone=milestone,
            since=since,
        ):
            yield Issue.from_dict(data, self._repo)

    async def create(
        self,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
        milestone: int | None = None,
    ) -> Issue:
        """Create an issue."""
        data = await self._client.issues.create(
            self._repo.owner,
            self._repo.name,
            title=title,
            body=body,
            labels=labels,
            assignees=assignees,
            milestone=milestone,
        )
        return Issue.from_dict(data, self._repo)

    async def update(self, issue_number: int, **kwargs: Any) -> Issue:
        """Update an issue."""
        data = await self._client.issues.update(
            self._repo.owner, self._repo.name, issue_number, **kwargs
        )
        return Issue.from_dict(data, self._repo)

    async def close(self, issue_number: int) -> Issue:
        """Close an issue."""
        data = await self._client.issues.close(
            self._repo.owner, self._repo.name, issue_number
        )
        return Issue.from_dict(data, self._repo)

    async def reopen(self, issue_number: int) -> Issue:
        """Reopen an issue."""
        data = await self._client.issues.reopen(
            self._repo.owner, self._repo.name, issue_number
        )
        return Issue.from_dict(data, self._repo)

    async def lock(self, issue_number: int, lock_reason: str | None = None) -> None:
        """Lock an issue."""
        await self._client.issues.lock(
            self._repo.owner, self._repo.name, issue_number, lock_reason
        )

    async def unlock(self, issue_number: int) -> None:
        """Unlock an issue."""
        await self._client.issues.unlock(
            self._repo.owner, self._repo.name, issue_number
        )

    async def list_comments(self, issue_number: int) -> AsyncIterator[Comment]:
        """List comments on an issue."""
        async for data in self._client.issues.list_comments(
            self._repo.owner, self._repo.name, issue_number
        ):
            yield Comment.from_dict(data, self._repo)

    async def create_comment(self, issue_number: int, body: str) -> Comment:
        """Create a comment on an issue."""
        data = await self._client.issues.create_comment(
            self._repo.owner, self._repo.name, issue_number, body
        )
        return Comment.from_dict(data, self._repo)

    async def add_labels(
        self, issue_number: int, labels: list[str]
    ) -> list[Label]:
        """Add labels to an issue."""
        data = await self._client.issues.add_labels(
            self._repo.owner, self._repo.name, issue_number, labels
        )
        return [Label.from_dict(l) for l in data]

    async def remove_label(self, issue_number: int, label: str) -> None:
        """Remove a label from an issue."""
        await self._client.issues.remove_label(
            self._repo.owner, self._repo.name, issue_number, label
        )


class AsyncRepoPulls:
    """Async pull request operations bound to a specific repository."""

    def __init__(self, repo: AsyncRepo) -> None:
        self._repo = repo
        self._client = repo._client

    async def get(self, pull_number: int) -> PullRequest:
        """Get a pull request by number."""
        data = await self._client.pulls.get(
            self._repo.owner, self._repo.name, pull_number
        )
        return PullRequest.from_dict(data, self._repo)

    async def list(
        self,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        head: str | None = None,
        base: str | None = None,
    ) -> AsyncIterator[PullRequest]:
        """List pull requests."""
        async for data in self._client.pulls.list(
            self._repo.owner,
            self._repo.name,
            state=state,
            sort=sort,
            direction=direction,
            head=head,
            base=base,
        ):
            yield PullRequest.from_dict(data, self._repo)

    async def create(
        self,
        title: str,
        head: str,
        base: str,
        body: str | None = None,
        draft: bool = False,
        maintainer_can_modify: bool = True,
    ) -> PullRequest:
        """Create a pull request."""
        data = await self._client.pulls.create(
            self._repo.owner,
            self._repo.name,
            title=title,
            head=head,
            base=base,
            body=body,
            draft=draft,
            maintainer_can_modify=maintainer_can_modify,
        )
        return PullRequest.from_dict(data, self._repo)

    async def update(self, pull_number: int, **kwargs: Any) -> PullRequest:
        """Update a pull request."""
        data = await self._client.pulls.update(
            self._repo.owner, self._repo.name, pull_number, **kwargs
        )
        return PullRequest.from_dict(data, self._repo)

    async def close(self, pull_number: int) -> PullRequest:
        """Close a pull request without merging."""
        data = await self._client.pulls.close(
            self._repo.owner, self._repo.name, pull_number
        )
        return PullRequest.from_dict(data, self._repo)

    async def merge(
        self,
        pull_number: int,
        commit_title: str | None = None,
        commit_message: str | None = None,
        merge_method: str = "merge",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Merge a pull request."""
        return await self._client.pulls.merge(
            self._repo.owner,
            self._repo.name,
            pull_number,
            commit_title=commit_title,
            commit_message=commit_message,
            merge_method=merge_method,
            sha=sha,
        )

    async def is_merged(self, pull_number: int) -> bool:
        """Check if a pull request has been merged."""
        return await self._client.pulls.is_merged(
            self._repo.owner, self._repo.name, pull_number
        )

    async def list_commits(self, pull_number: int) -> AsyncIterator[dict[str, Any]]:
        """List commits on a pull request."""
        async for item in self._client.pulls.list_commits(
            self._repo.owner, self._repo.name, pull_number
        ):
            yield item

    async def list_files(self, pull_number: int) -> AsyncIterator[dict[str, Any]]:
        """List files changed in a pull request."""
        async for item in self._client.pulls.list_files(
            self._repo.owner, self._repo.name, pull_number
        ):
            yield item

    async def list_reviews(self, pull_number: int) -> AsyncIterator[dict[str, Any]]:
        """List reviews on a pull request."""
        async for item in self._client.pulls.list_reviews(
            self._repo.owner, self._repo.name, pull_number
        ):
            yield item

    async def create_review(
        self,
        pull_number: int,
        body: str | None = None,
        event: str = "COMMENT",
        comments: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a review on a pull request."""
        return await self._client.pulls.create_review(
            self._repo.owner,
            self._repo.name,
            pull_number,
            body=body,
            event=event,
            comments=comments,
        )

    async def request_reviewers(
        self,
        pull_number: int,
        reviewers: list[str] | None = None,
        team_reviewers: list[str] | None = None,
    ) -> PullRequest:
        """Request reviewers for a pull request."""
        data = await self._client.pulls.request_reviewers(
            self._repo.owner,
            self._repo.name,
            pull_number,
            reviewers=reviewers,
            team_reviewers=team_reviewers,
        )
        return PullRequest.from_dict(data, self._repo)


class AsyncRepo:
    """An async GitHub repository with bound owner/repo context.

    Usage:
        >>> async with AsyncGitHub() as gh:
        ...     repo = gh.repo("comet-ml", "opik")
        ...     async for issue in repo.issues.list():
        ...         print(issue.title)
    """

    def __init__(self, client: AsyncGitHub, owner: str, name: str) -> None:
        self._client = client
        self.owner = owner
        self.name = name
        self.full_name = f"{owner}/{name}"

        # Bound resource handlers
        self.issues = AsyncRepoIssues(self)
        self.pulls = AsyncRepoPulls(self)

    async def get(self) -> Repository:
        """Get repository details."""
        data = await self._client.repos.get(self.owner, self.name)
        return Repository.from_dict(data, self._client)

    async def update(self, **kwargs: Any) -> Repository:
        """Update repository settings."""
        data = await self._client.repos.update(self.owner, self.name, **kwargs)
        return Repository.from_dict(data, self._client)

    async def delete(self) -> None:
        """Delete this repository."""
        await self._client.repos.delete(self.owner, self.name)

    async def contributors(self, anon: bool = False) -> AsyncIterator[User]:
        """List repository contributors."""
        async for data in self._client.repos.list_contributors(
            self.owner, self.name, anon=anon
        ):
            yield User.from_dict(data)

    async def languages(self) -> dict[str, int]:
        """List languages used in this repository."""
        return await self._client.repos.list_languages(self.owner, self.name)

    async def tags(self) -> AsyncIterator[dict[str, Any]]:
        """List repository tags."""
        async for item in self._client.repos.list_tags(self.owner, self.name):
            yield item

    async def branches(
        self, protected: bool | None = None
    ) -> AsyncIterator[Branch]:
        """List repository branches."""
        async for data in self._client.repos.list_branches(
            self.owner, self.name, protected=protected
        ):
            yield Branch.from_dict(data)

    # Convenience shortcuts
    async def star(self) -> None:
        """Star this repository."""
        await self._client.request("PUT", f"/user/starred/{self.full_name}")

    async def unstar(self) -> None:
        """Unstar this repository."""
        await self._client.request("DELETE", f"/user/starred/{self.full_name}")

    async def is_starred(self) -> bool:
        """Check if this repository is starred by the authenticated user."""
        try:
            await self._client.request("GET", f"/user/starred/{self.full_name}")
            return True
        except Exception:
            return False

    async def fork(self, organization: str | None = None) -> Repository:
        """Fork this repository."""
        data: dict[str, Any] = {}
        if organization:
            data["organization"] = organization
        result = await self._client.request(
            "POST", f"/repos/{self.full_name}/forks", json=data if data else None
        )
        return Repository.from_dict(result, self._client)

    async def subscribe(self) -> None:
        """Watch/subscribe to this repository."""
        await self._client.request(
            "PUT",
            f"/repos/{self.full_name}/subscription",
            json={"subscribed": True},
        )

    async def unsubscribe(self) -> None:
        """Unwatch/unsubscribe from this repository."""
        await self._client.request("DELETE", f"/repos/{self.full_name}/subscription")

    def __repr__(self) -> str:
        return f"AsyncRepo({self.full_name!r})"
