"""Typed models for GitHub API responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from github_rest_api.repo import Repo, AsyncRepo


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string to datetime object."""
    if value is None:
        return None
    # GitHub uses ISO 8601 format: 2024-01-15T10:30:00Z
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_user(data: dict[str, Any] | None) -> User | None:
    """Parse user data into User object."""
    if data is None:
        return None
    return User.from_dict(data)


@dataclass
class User:
    """A GitHub user."""

    login: str
    id: int
    avatar_url: str
    html_url: str
    type: str
    name: str | None = None
    email: str | None = None
    bio: str | None = None
    company: str | None = None
    location: str | None = None
    blog: str | None = None
    twitter_username: str | None = None
    public_repos: int | None = None
    public_gists: int | None = None
    followers: int | None = None
    following: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Create User from API response dict."""
        return cls(
            login=data["login"],
            id=data["id"],
            avatar_url=data.get("avatar_url", ""),
            html_url=data.get("html_url", ""),
            type=data.get("type", "User"),
            name=data.get("name"),
            email=data.get("email"),
            bio=data.get("bio"),
            company=data.get("company"),
            location=data.get("location"),
            blog=data.get("blog"),
            twitter_username=data.get("twitter_username"),
            public_repos=data.get("public_repos"),
            public_gists=data.get("public_gists"),
            followers=data.get("followers"),
            following=data.get("following"),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
            _raw=data,
        )


@dataclass
class Label:
    """A GitHub label."""

    id: int
    name: str
    color: str
    description: str | None = None
    default: bool = False

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Label:
        """Create Label from API response dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            color=data.get("color", ""),
            description=data.get("description"),
            default=data.get("default", False),
            _raw=data,
        )


@dataclass
class Milestone:
    """A GitHub milestone."""

    id: int
    number: int
    title: str
    description: str | None
    state: str
    open_issues: int
    closed_issues: int
    created_at: datetime | None
    updated_at: datetime | None
    due_on: datetime | None
    closed_at: datetime | None

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Milestone:
        """Create Milestone from API response dict."""
        return cls(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            description=data.get("description"),
            state=data.get("state", "open"),
            open_issues=data.get("open_issues", 0),
            closed_issues=data.get("closed_issues", 0),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
            due_on=_parse_datetime(data.get("due_on")),
            closed_at=_parse_datetime(data.get("closed_at")),
            _raw=data,
        )


@dataclass
class Comment:
    """A GitHub issue or PR comment."""

    id: int
    body: str
    user: User | None
    html_url: str
    created_at: datetime | None
    updated_at: datetime | None

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _repo: Repo | None = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any], repo: Repo | None = None) -> Comment:
        """Create Comment from API response dict."""
        return cls(
            id=data["id"],
            body=data.get("body", ""),
            user=_parse_user(data.get("user")),
            html_url=data.get("html_url", ""),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
            _raw=data,
            _repo=repo,
        )


@dataclass
class Issue:
    """A GitHub issue with convenience methods."""

    id: int
    number: int
    title: str
    body: str | None
    state: str
    locked: bool
    user: User | None
    assignee: User | None
    assignees: list[User]
    labels: list[Label]
    milestone: Milestone | None
    html_url: str
    comments: int
    created_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    closed_by: User | None

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _repo: Repo | None = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any], repo: Repo | None = None) -> Issue:
        """Create Issue from API response dict."""
        assignees = [User.from_dict(a) for a in data.get("assignees", [])]
        labels = [Label.from_dict(l) for l in data.get("labels", [])]
        milestone = None
        if data.get("milestone"):
            milestone = Milestone.from_dict(data["milestone"])

        return cls(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            state=data.get("state", "open"),
            locked=data.get("locked", False),
            user=_parse_user(data.get("user")),
            assignee=_parse_user(data.get("assignee")),
            assignees=assignees,
            labels=labels,
            milestone=milestone,
            html_url=data.get("html_url", ""),
            comments=data.get("comments", 0),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
            closed_at=_parse_datetime(data.get("closed_at")),
            closed_by=_parse_user(data.get("closed_by")),
            _raw=data,
            _repo=repo,
        )

    def close(self) -> Issue:
        """Close this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        data = self._repo._client.issues.update(
            self._repo.owner, self._repo.name, self.number, state="closed"
        )
        return Issue.from_dict(data, self._repo)

    def reopen(self) -> Issue:
        """Reopen this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        data = self._repo._client.issues.update(
            self._repo.owner, self._repo.name, self.number, state="open"
        )
        return Issue.from_dict(data, self._repo)

    def add_comment(self, body: str) -> Comment:
        """Add a comment to this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        data = self._repo._client.issues.create_comment(
            self._repo.owner, self._repo.name, self.number, body
        )
        return Comment.from_dict(data, self._repo)

    def add_labels(self, *labels: str) -> list[Label]:
        """Add labels to this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        data = self._repo._client.issues.add_labels(
            self._repo.owner, self._repo.name, self.number, list(labels)
        )
        return [Label.from_dict(l) for l in data]

    def remove_label(self, label: str) -> None:
        """Remove a label from this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        self._repo._client.issues.remove_label(
            self._repo.owner, self._repo.name, self.number, label
        )

    def lock(self, reason: str | None = None) -> None:
        """Lock this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        self._repo._client.issues.lock(
            self._repo.owner, self._repo.name, self.number, reason
        )

    def unlock(self) -> None:
        """Unlock this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        self._repo._client.issues.unlock(
            self._repo.owner, self._repo.name, self.number
        )

    def list_comments(self) -> Iterator[Comment]:
        """List comments on this issue."""
        if self._repo is None:
            raise RuntimeError("Issue not bound to a repository")
        for data in self._repo._client.issues.list_comments(
            self._repo.owner, self._repo.name, self.number
        ):
            yield Comment.from_dict(data, self._repo)

    @property
    def is_open(self) -> bool:
        """Check if issue is open."""
        return self.state == "open"

    @property
    def is_closed(self) -> bool:
        """Check if issue is closed."""
        return self.state == "closed"


@dataclass
class PullRequest:
    """A GitHub pull request with convenience methods."""

    id: int
    number: int
    title: str
    body: str | None
    state: str
    locked: bool
    draft: bool
    merged: bool
    mergeable: bool | None
    user: User | None
    assignee: User | None
    assignees: list[User]
    labels: list[Label]
    milestone: Milestone | None
    html_url: str
    head_ref: str
    head_sha: str
    base_ref: str
    base_sha: str
    comments: int
    commits: int
    additions: int
    deletions: int
    changed_files: int
    created_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    merged_at: datetime | None
    merged_by: User | None

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _repo: Repo | None = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any], repo: Repo | None = None) -> PullRequest:
        """Create PullRequest from API response dict."""
        assignees = [User.from_dict(a) for a in data.get("assignees", [])]
        labels = [Label.from_dict(l) for l in data.get("labels", [])]
        milestone = None
        if data.get("milestone"):
            milestone = Milestone.from_dict(data["milestone"])

        head = data.get("head", {})
        base = data.get("base", {})

        return cls(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            state=data.get("state", "open"),
            locked=data.get("locked", False),
            draft=data.get("draft", False),
            merged=data.get("merged", False),
            mergeable=data.get("mergeable"),
            user=_parse_user(data.get("user")),
            assignee=_parse_user(data.get("assignee")),
            assignees=assignees,
            labels=labels,
            milestone=milestone,
            html_url=data.get("html_url", ""),
            head_ref=head.get("ref", ""),
            head_sha=head.get("sha", ""),
            base_ref=base.get("ref", ""),
            base_sha=base.get("sha", ""),
            comments=data.get("comments", 0),
            commits=data.get("commits", 0),
            additions=data.get("additions", 0),
            deletions=data.get("deletions", 0),
            changed_files=data.get("changed_files", 0),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
            closed_at=_parse_datetime(data.get("closed_at")),
            merged_at=_parse_datetime(data.get("merged_at")),
            merged_by=_parse_user(data.get("merged_by")),
            _raw=data,
            _repo=repo,
        )

    def close(self) -> PullRequest:
        """Close this pull request without merging."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        data = self._repo._client.pulls.update(
            self._repo.owner, self._repo.name, self.number, state="closed"
        )
        return PullRequest.from_dict(data, self._repo)

    def merge(
        self,
        commit_title: str | None = None,
        commit_message: str | None = None,
        merge_method: str = "merge",
        sha: str | None = None,
    ) -> dict[str, Any]:
        """Merge this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        return self._repo._client.pulls.merge(
            self._repo.owner,
            self._repo.name,
            self.number,
            commit_title=commit_title,
            commit_message=commit_message,
            merge_method=merge_method,
            sha=sha,
        )

    def approve(self, body: str | None = None) -> dict[str, Any]:
        """Approve this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        return self._repo._client.pulls.create_review(
            self._repo.owner,
            self._repo.name,
            self.number,
            body=body,
            event="APPROVE",
        )

    def request_changes(self, body: str) -> dict[str, Any]:
        """Request changes on this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        return self._repo._client.pulls.create_review(
            self._repo.owner,
            self._repo.name,
            self.number,
            body=body,
            event="REQUEST_CHANGES",
        )

    def comment(self, body: str) -> dict[str, Any]:
        """Add a review comment to this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        return self._repo._client.pulls.create_review(
            self._repo.owner,
            self._repo.name,
            self.number,
            body=body,
            event="COMMENT",
        )

    def add_comment(self, body: str) -> Comment:
        """Add an issue comment to this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        data = self._repo._client.issues.create_comment(
            self._repo.owner, self._repo.name, self.number, body
        )
        return Comment.from_dict(data, self._repo)

    def request_reviewers(
        self,
        reviewers: list[str] | None = None,
        team_reviewers: list[str] | None = None,
    ) -> PullRequest:
        """Request reviewers for this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        data = self._repo._client.pulls.request_reviewers(
            self._repo.owner,
            self._repo.name,
            self.number,
            reviewers=reviewers,
            team_reviewers=team_reviewers,
        )
        return PullRequest.from_dict(data, self._repo)

    def list_commits(self) -> Iterator[dict[str, Any]]:
        """List commits on this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        return self._repo._client.pulls.list_commits(
            self._repo.owner, self._repo.name, self.number
        )

    def list_files(self) -> Iterator[dict[str, Any]]:
        """List files changed in this pull request."""
        if self._repo is None:
            raise RuntimeError("PullRequest not bound to a repository")
        return self._repo._client.pulls.list_files(
            self._repo.owner, self._repo.name, self.number
        )

    @property
    def is_open(self) -> bool:
        """Check if PR is open."""
        return self.state == "open"

    @property
    def is_closed(self) -> bool:
        """Check if PR is closed."""
        return self.state == "closed"

    @property
    def is_merged(self) -> bool:
        """Check if PR is merged."""
        return self.merged


@dataclass
class Repository:
    """A GitHub repository with convenience methods."""

    id: int
    name: str
    full_name: str
    html_url: str
    clone_url: str
    ssh_url: str
    forks_count: int
    stargazers_count: int
    watchers_count: int
    open_issues_count: int
    default_branch: str
    private: bool = False
    fork: bool = False
    archived: bool = False
    disabled: bool = False
    owner: User | None = None
    description: str | None = None
    homepage: str | None = None
    language: str | None = None
    pushed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)
    _client: Any = field(default=None, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any], client: Any = None) -> Repository:
        """Create Repository from API response dict."""
        return cls(
            id=data["id"],
            name=data["name"],
            full_name=data["full_name"],
            owner=_parse_user(data.get("owner")),
            private=data.get("private", False),
            description=data.get("description"),
            fork=data.get("fork", False),
            html_url=data.get("html_url", ""),
            clone_url=data.get("clone_url", ""),
            ssh_url=data.get("ssh_url", ""),
            homepage=data.get("homepage"),
            language=data.get("language"),
            forks_count=data.get("forks_count", 0),
            stargazers_count=data.get("stargazers_count", 0),
            watchers_count=data.get("watchers_count", 0),
            open_issues_count=data.get("open_issues_count", 0),
            default_branch=data.get("default_branch", "main"),
            archived=data.get("archived", False),
            disabled=data.get("disabled", False),
            pushed_at=_parse_datetime(data.get("pushed_at")),
            created_at=_parse_datetime(data.get("created_at")),
            updated_at=_parse_datetime(data.get("updated_at")),
            _raw=data,
            _client=client,
        )

    def star(self) -> None:
        """Star this repository."""
        if self._client is None:
            raise RuntimeError("Repository not bound to a client")
        self._client.request("PUT", f"/user/starred/{self.full_name}")

    def unstar(self) -> None:
        """Unstar this repository."""
        if self._client is None:
            raise RuntimeError("Repository not bound to a client")
        self._client.request("DELETE", f"/user/starred/{self.full_name}")

    def is_starred(self) -> bool:
        """Check if this repository is starred by the authenticated user."""
        if self._client is None:
            raise RuntimeError("Repository not bound to a client")
        try:
            self._client.request("GET", f"/user/starred/{self.full_name}")
            return True
        except Exception:
            return False

    def fork(self, organization: str | None = None) -> Repository:
        """Fork this repository."""
        if self._client is None:
            raise RuntimeError("Repository not bound to a client")
        data: dict[str, Any] = {}
        if organization:
            data["organization"] = organization
        result = self._client.request(
            "POST", f"/repos/{self.full_name}/forks", json=data if data else None
        )
        return Repository.from_dict(result, self._client)

    def subscribe(self) -> None:
        """Watch/subscribe to this repository."""
        if self._client is None:
            raise RuntimeError("Repository not bound to a client")
        self._client.request(
            "PUT",
            f"/repos/{self.full_name}/subscription",
            json={"subscribed": True},
        )

    def unsubscribe(self) -> None:
        """Unwatch/unsubscribe from this repository."""
        if self._client is None:
            raise RuntimeError("Repository not bound to a client")
        self._client.request("DELETE", f"/repos/{self.full_name}/subscription")

    @property
    def stars(self) -> int:
        """Alias for stargazers_count."""
        return self.stargazers_count

    @property
    def forks(self) -> int:
        """Alias for forks_count."""
        return self.forks_count


@dataclass
class Branch:
    """A GitHub branch."""

    name: str
    protected: bool
    sha: str

    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Branch:
        """Create Branch from API response dict."""
        commit = data.get("commit", {})
        return cls(
            name=data["name"],
            protected=data.get("protected", False),
            sha=commit.get("sha", ""),
            _raw=data,
        )


@dataclass
class SearchResult:
    """A search result container."""

    total_count: int
    incomplete_results: bool
    items: list[Any]

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], item_parser: Any = None
    ) -> SearchResult:
        """Create SearchResult from API response dict."""
        items = data.get("items", [])
        if item_parser:
            items = [item_parser(item) for item in items]
        return cls(
            total_count=data.get("total_count", 0),
            incomplete_results=data.get("incomplete_results", False),
            items=items,
        )
