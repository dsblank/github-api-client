"""Tests for typed models."""

import pytest
from datetime import datetime, timezone

from github_rest_api.models import (
    Issue,
    PullRequest,
    Repository,
    User,
    Comment,
    Label,
    Milestone,
    Branch,
    _parse_datetime,
)


class TestParseDatetime:
    """Tests for datetime parsing."""

    def test_parse_iso_format_with_z(self):
        """Parses ISO 8601 format with Z suffix."""
        result = _parse_datetime("2024-01-15T10:30:00Z")
        assert result == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    def test_parse_iso_format_with_offset(self):
        """Parses ISO 8601 format with timezone offset."""
        result = _parse_datetime("2024-01-15T10:30:00+00:00")
        assert result == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)

    def test_parse_none(self):
        """Returns None for None input."""
        assert _parse_datetime(None) is None


class TestUser:
    """Tests for User model."""

    def test_from_dict_minimal(self):
        """Creates User from minimal data."""
        data = {
            "login": "octocat",
            "id": 1,
            "avatar_url": "https://github.com/images/octocat.png",
            "html_url": "https://github.com/octocat",
            "type": "User",
        }
        user = User.from_dict(data)
        assert user.login == "octocat"
        assert user.id == 1
        assert user.type == "User"

    def test_from_dict_full(self):
        """Creates User from full data."""
        data = {
            "login": "octocat",
            "id": 1,
            "avatar_url": "https://github.com/images/octocat.png",
            "html_url": "https://github.com/octocat",
            "type": "User",
            "name": "The Octocat",
            "email": "octocat@github.com",
            "bio": "A cat",
            "company": "GitHub",
            "location": "San Francisco",
            "followers": 100,
            "following": 50,
            "created_at": "2020-01-01T00:00:00Z",
        }
        user = User.from_dict(data)
        assert user.name == "The Octocat"
        assert user.email == "octocat@github.com"
        assert user.followers == 100
        assert user.created_at == datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


class TestLabel:
    """Tests for Label model."""

    def test_from_dict(self):
        """Creates Label from data."""
        data = {
            "id": 1,
            "name": "bug",
            "color": "fc2929",
            "description": "Something isn't working",
            "default": False,
        }
        label = Label.from_dict(data)
        assert label.id == 1
        assert label.name == "bug"
        assert label.color == "fc2929"
        assert label.description == "Something isn't working"


class TestMilestone:
    """Tests for Milestone model."""

    def test_from_dict(self):
        """Creates Milestone from data."""
        data = {
            "id": 1,
            "number": 1,
            "title": "v1.0",
            "description": "First release",
            "state": "open",
            "open_issues": 5,
            "closed_issues": 10,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T00:00:00Z",
            "due_on": "2024-02-01T00:00:00Z",
            "closed_at": None,
        }
        milestone = Milestone.from_dict(data)
        assert milestone.title == "v1.0"
        assert milestone.state == "open"
        assert milestone.open_issues == 5
        assert milestone.due_on == datetime(2024, 2, 1, 0, 0, 0, tzinfo=timezone.utc)


class TestIssue:
    """Tests for Issue model."""

    @pytest.fixture
    def issue_data(self):
        """Sample issue data."""
        return {
            "id": 1,
            "number": 42,
            "title": "Bug report",
            "body": "Something is broken",
            "state": "open",
            "locked": False,
            "user": {
                "login": "octocat",
                "id": 1,
                "avatar_url": "https://github.com/images/octocat.png",
                "html_url": "https://github.com/octocat",
                "type": "User",
            },
            "assignee": None,
            "assignees": [],
            "labels": [
                {"id": 1, "name": "bug", "color": "fc2929"},
            ],
            "milestone": None,
            "html_url": "https://github.com/owner/repo/issues/42",
            "comments": 5,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-16T12:00:00Z",
            "closed_at": None,
            "closed_by": None,
        }

    def test_from_dict(self, issue_data):
        """Creates Issue from data."""
        issue = Issue.from_dict(issue_data)
        assert issue.id == 1
        assert issue.number == 42
        assert issue.title == "Bug report"
        assert issue.body == "Something is broken"
        assert issue.state == "open"
        assert issue.user.login == "octocat"
        assert len(issue.labels) == 1
        assert issue.labels[0].name == "bug"
        assert issue.comments == 5

    def test_datetime_parsing(self, issue_data):
        """Parses datetime fields correctly."""
        issue = Issue.from_dict(issue_data)
        assert issue.created_at == datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert issue.updated_at == datetime(2024, 1, 16, 12, 0, 0, tzinfo=timezone.utc)
        assert issue.closed_at is None

    def test_is_open_property(self, issue_data):
        """is_open property works correctly."""
        issue = Issue.from_dict(issue_data)
        assert issue.is_open is True
        assert issue.is_closed is False

        issue_data["state"] = "closed"
        issue = Issue.from_dict(issue_data)
        assert issue.is_open is False
        assert issue.is_closed is True

    def test_raw_data_preserved(self, issue_data):
        """Raw data is preserved in _raw attribute."""
        issue = Issue.from_dict(issue_data)
        assert issue._raw == issue_data


class TestPullRequest:
    """Tests for PullRequest model."""

    @pytest.fixture
    def pr_data(self):
        """Sample pull request data."""
        return {
            "id": 1,
            "number": 123,
            "title": "Add feature",
            "body": "This PR adds a new feature",
            "state": "open",
            "locked": False,
            "draft": False,
            "merged": False,
            "mergeable": True,
            "user": {
                "login": "octocat",
                "id": 1,
                "avatar_url": "https://github.com/images/octocat.png",
                "html_url": "https://github.com/octocat",
                "type": "User",
            },
            "assignee": None,
            "assignees": [],
            "labels": [],
            "milestone": None,
            "html_url": "https://github.com/owner/repo/pull/123",
            "head": {
                "ref": "feature-branch",
                "sha": "abc123",
            },
            "base": {
                "ref": "main",
                "sha": "def456",
            },
            "comments": 2,
            "commits": 3,
            "additions": 100,
            "deletions": 50,
            "changed_files": 5,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-16T12:00:00Z",
            "closed_at": None,
            "merged_at": None,
            "merged_by": None,
        }

    def test_from_dict(self, pr_data):
        """Creates PullRequest from data."""
        pr = PullRequest.from_dict(pr_data)
        assert pr.id == 1
        assert pr.number == 123
        assert pr.title == "Add feature"
        assert pr.head_ref == "feature-branch"
        assert pr.base_ref == "main"
        assert pr.additions == 100
        assert pr.deletions == 50
        assert pr.changed_files == 5

    def test_is_merged_property(self, pr_data):
        """is_merged property works correctly."""
        pr = PullRequest.from_dict(pr_data)
        assert pr.is_merged is False

        pr_data["merged"] = True
        pr = PullRequest.from_dict(pr_data)
        assert pr.is_merged is True


class TestRepository:
    """Tests for Repository model."""

    @pytest.fixture
    def repo_data(self):
        """Sample repository data."""
        return {
            "id": 1,
            "name": "hello-world",
            "full_name": "octocat/hello-world",
            "owner": {
                "login": "octocat",
                "id": 1,
                "avatar_url": "https://github.com/images/octocat.png",
                "html_url": "https://github.com/octocat",
                "type": "User",
            },
            "private": False,
            "description": "A hello world repository",
            "fork": False,
            "html_url": "https://github.com/octocat/hello-world",
            "clone_url": "https://github.com/octocat/hello-world.git",
            "ssh_url": "git@github.com:octocat/hello-world.git",
            "homepage": "https://example.com",
            "language": "Python",
            "forks_count": 10,
            "stargazers_count": 100,
            "watchers_count": 100,
            "open_issues_count": 5,
            "default_branch": "main",
            "archived": False,
            "disabled": False,
            "pushed_at": "2024-01-15T10:30:00Z",
            "created_at": "2020-01-01T00:00:00Z",
            "updated_at": "2024-01-16T12:00:00Z",
        }

    def test_from_dict(self, repo_data):
        """Creates Repository from data."""
        repo = Repository.from_dict(repo_data)
        assert repo.id == 1
        assert repo.name == "hello-world"
        assert repo.full_name == "octocat/hello-world"
        assert repo.owner.login == "octocat"
        assert repo.language == "Python"
        assert repo.stargazers_count == 100

    def test_stars_alias(self, repo_data):
        """stars property is alias for stargazers_count."""
        repo = Repository.from_dict(repo_data)
        assert repo.stars == repo.stargazers_count == 100

    def test_forks_alias(self, repo_data):
        """forks property is alias for forks_count."""
        repo = Repository.from_dict(repo_data)
        assert repo.forks == repo.forks_count == 10


class TestBranch:
    """Tests for Branch model."""

    def test_from_dict(self):
        """Creates Branch from data."""
        data = {
            "name": "main",
            "protected": True,
            "commit": {
                "sha": "abc123",
            },
        }
        branch = Branch.from_dict(data)
        assert branch.name == "main"
        assert branch.protected is True
        assert branch.sha == "abc123"


class TestComment:
    """Tests for Comment model."""

    def test_from_dict(self):
        """Creates Comment from data."""
        data = {
            "id": 1,
            "body": "Great work!",
            "user": {
                "login": "octocat",
                "id": 1,
                "avatar_url": "https://github.com/images/octocat.png",
                "html_url": "https://github.com/octocat",
                "type": "User",
            },
            "html_url": "https://github.com/owner/repo/issues/1#issuecomment-1",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
        }
        comment = Comment.from_dict(data)
        assert comment.id == 1
        assert comment.body == "Great work!"
        assert comment.user.login == "octocat"
