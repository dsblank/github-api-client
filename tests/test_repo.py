"""Tests for repository-bound interface."""

import pytest
from github_api_client import Branch, GitHub, Issue, PullRequest, Repository, User
from pytest_httpx import HTTPXMock


class TestRepoInterface:
    """Tests for the Repo interface."""

    def test_repo_from_two_args(self):
        """Create repo from owner and name."""
        with GitHub(token=None) as gh:
            repo = gh.repo("owner", "repo")
            assert repo.owner == "owner"
            assert repo.name == "repo"
            assert repo.full_name == "owner/repo"

    def test_repo_from_full_name(self):
        """Create repo from full name."""
        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            assert repo.owner == "owner"
            assert repo.name == "repo"

    def test_repo_invalid_format(self):
        """Raises error for invalid format."""
        with GitHub(token=None) as gh:
            with pytest.raises(ValueError, match="Must provide repo name"):
                gh.repo("owner")

    def test_repo_repr(self):
        """Repo has useful repr."""
        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            assert repr(repo) == "Repo('owner/repo')"


class TestRepoGet:
    """Tests for getting repository info."""

    def test_get_returns_repository(self, httpx_mock: HTTPXMock):
        """repo.get() returns Repository object."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo",
            json={
                "id": 1,
                "name": "repo",
                "full_name": "owner/repo",
                "owner": {
                    "login": "owner",
                    "id": 1,
                    "avatar_url": "",
                    "html_url": "",
                    "type": "User",
                },
                "html_url": "https://github.com/owner/repo",
                "clone_url": "https://github.com/owner/repo.git",
                "ssh_url": "git@github.com:owner/repo.git",
                "stargazers_count": 100,
                "forks_count": 10,
                "watchers_count": 100,
                "open_issues_count": 5,
                "default_branch": "main",
                "language": "Python",
            },
        )

        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            info = repo.get()
            assert isinstance(info, Repository)
            assert info.name == "repo"
            assert info.stars == 100
            assert info.language == "Python"


class TestRepoIssues:
    """Tests for repo.issues operations."""

    @pytest.fixture
    def issue_response(self):
        """Sample issue response data."""
        return {
            "id": 1,
            "number": 42,
            "title": "Test issue",
            "body": "Body text",
            "state": "open",
            "locked": False,
            "user": {
                "login": "octocat",
                "id": 1,
                "avatar_url": "",
                "html_url": "",
                "type": "User",
            },
            "assignee": None,
            "assignees": [],
            "labels": [{"id": 1, "name": "bug", "color": "fc2929"}],
            "milestone": None,
            "html_url": "https://github.com/owner/repo/issues/42",
            "comments": 0,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "closed_at": None,
            "closed_by": None,
        }

    def test_issues_get_returns_issue(self, httpx_mock: HTTPXMock, issue_response):
        """repo.issues.get() returns Issue object."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            json=issue_response,
        )

        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.get(42)
            assert isinstance(issue, Issue)
            assert issue.number == 42
            assert issue.title == "Test issue"
            assert issue.user.login == "octocat"

    def test_issues_list_returns_issues(self, httpx_mock: HTTPXMock, issue_response):
        """repo.issues.list() returns Issue objects."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=open&sort=created&direction=desc&per_page=30&page=1",
            json=[issue_response],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues?state=open&sort=created&direction=desc&per_page=30&page=2",
            json=[],
        )

        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            issues = list(repo.issues.list())
            assert len(issues) == 1
            assert isinstance(issues[0], Issue)

    def test_issues_create_returns_issue(self, httpx_mock: HTTPXMock, issue_response):
        """repo.issues.create() returns Issue object."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues",
            json=issue_response,
            method="POST",
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.create(title="Test issue", body="Body text")
            assert isinstance(issue, Issue)
            assert issue.title == "Test issue"


class TestRepoPulls:
    """Tests for repo.pulls operations."""

    @pytest.fixture
    def pr_response(self):
        """Sample PR response data."""
        return {
            "id": 1,
            "number": 123,
            "title": "Add feature",
            "body": "Description",
            "state": "open",
            "locked": False,
            "draft": False,
            "merged": False,
            "mergeable": True,
            "user": {
                "login": "octocat",
                "id": 1,
                "avatar_url": "",
                "html_url": "",
                "type": "User",
            },
            "assignee": None,
            "assignees": [],
            "labels": [],
            "milestone": None,
            "html_url": "https://github.com/owner/repo/pull/123",
            "head": {"ref": "feature", "sha": "abc123"},
            "base": {"ref": "main", "sha": "def456"},
            "comments": 0,
            "commits": 1,
            "additions": 10,
            "deletions": 5,
            "changed_files": 2,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "closed_at": None,
            "merged_at": None,
            "merged_by": None,
        }

    def test_pulls_get_returns_pullrequest(self, httpx_mock: HTTPXMock, pr_response):
        """repo.pulls.get() returns PullRequest object."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_response,
        )

        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            assert isinstance(pr, PullRequest)
            assert pr.number == 123
            assert pr.head_ref == "feature"
            assert pr.base_ref == "main"

    def test_pulls_list_returns_pullrequests(self, httpx_mock: HTTPXMock, pr_response):
        """repo.pulls.list() returns PullRequest objects."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls?state=open&sort=created&direction=desc&per_page=30&page=1",
            json=[pr_response],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls?state=open&sort=created&direction=desc&per_page=30&page=2",
            json=[],
        )

        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            prs = list(repo.pulls.list())
            assert len(prs) == 1
            assert isinstance(prs[0], PullRequest)


class TestRepoBranches:
    """Tests for repo.branches()."""

    def test_branches_returns_branch_objects(self, httpx_mock: HTTPXMock):
        """repo.branches() returns Branch objects."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/branches?per_page=30&page=1",
            json=[
                {"name": "main", "protected": True, "commit": {"sha": "abc123"}},
                {"name": "develop", "protected": False, "commit": {"sha": "def456"}},
            ],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/branches?per_page=30&page=2",
            json=[],
        )

        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            branches = list(repo.branches())
            assert len(branches) == 2
            assert isinstance(branches[0], Branch)
            assert branches[0].name == "main"
            assert branches[0].protected is True


class TestRepoContributors:
    """Tests for repo.contributors()."""

    def test_contributors_returns_user_objects(self, httpx_mock: HTTPXMock):
        """repo.contributors() returns User objects."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/contributors?anon=false&per_page=30&page=1",
            json=[
                {
                    "login": "octocat",
                    "id": 1,
                    "avatar_url": "",
                    "html_url": "",
                    "type": "User",
                    "contributions": 100,
                },
            ],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/contributors?anon=false&per_page=30&page=2",
            json=[],
        )

        with GitHub(token=None) as gh:
            repo = gh.repo("owner/repo")
            contributors = list(repo.contributors())
            assert len(contributors) == 1
            assert isinstance(contributors[0], User)
            assert contributors[0].login == "octocat"


class TestRepoConvenienceMethods:
    """Tests for repo convenience methods."""

    def test_star(self, httpx_mock: HTTPXMock):
        """repo.star() stars the repository."""
        httpx_mock.add_response(
            url="https://api.github.com/user/starred/owner/repo",
            method="PUT",
            status_code=204,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            repo.star()  # Should not raise

    def test_unstar(self, httpx_mock: HTTPXMock):
        """repo.unstar() unstars the repository."""
        httpx_mock.add_response(
            url="https://api.github.com/user/starred/owner/repo",
            method="DELETE",
            status_code=204,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            repo.unstar()  # Should not raise

    def test_is_starred_true(self, httpx_mock: HTTPXMock):
        """repo.is_starred() returns True when starred."""
        httpx_mock.add_response(
            url="https://api.github.com/user/starred/owner/repo",
            method="GET",
            status_code=204,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            assert repo.is_starred() is True

    def test_is_starred_false(self, httpx_mock: HTTPXMock):
        """repo.is_starred() returns False when not starred."""
        httpx_mock.add_response(
            url="https://api.github.com/user/starred/owner/repo",
            method="GET",
            status_code=404,
            json={"message": "Not Found"},
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            assert repo.is_starred() is False

    def test_fork(self, httpx_mock: HTTPXMock):
        """repo.fork() forks the repository."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/forks",
            method="POST",
            json={
                "id": 2,
                "name": "repo",
                "full_name": "myuser/repo",
                "html_url": "https://github.com/myuser/repo",
                "clone_url": "https://github.com/myuser/repo.git",
                "ssh_url": "git@github.com:myuser/repo.git",
                "fork": True,
                "stargazers_count": 0,
                "forks_count": 0,
                "watchers_count": 0,
                "open_issues_count": 0,
                "default_branch": "main",
            },
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            forked = repo.fork()
            assert isinstance(forked, Repository)
            assert forked.full_name == "myuser/repo"
            assert forked.fork is True

    def test_subscribe(self, httpx_mock: HTTPXMock):
        """repo.subscribe() watches the repository."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/subscription",
            method="PUT",
            json={"subscribed": True},
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            repo.subscribe()  # Should not raise

    def test_unsubscribe(self, httpx_mock: HTTPXMock):
        """repo.unsubscribe() unwatches the repository."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/subscription",
            method="DELETE",
            status_code=204,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            repo.unsubscribe()  # Should not raise
