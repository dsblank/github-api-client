"""Tests for methods on Issue and PullRequest objects."""

import pytest
from github_api_client import Comment, GitHub, Issue, PullRequest
from pytest_httpx import HTTPXMock


class TestIssueMethods:
    """Tests for methods on Issue objects."""

    @pytest.fixture
    def issue_data(self):
        """Sample issue data."""
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
            "labels": [],
            "milestone": None,
            "html_url": "https://github.com/owner/repo/issues/42",
            "comments": 0,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "closed_at": None,
            "closed_by": None,
        }

    def test_issue_close(self, httpx_mock: HTTPXMock, issue_data):
        """issue.close() closes the issue."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            json=issue_data,
        )
        closed_data = {**issue_data, "state": "closed"}
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            method="PATCH",
            json=closed_data,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.get(42)
            closed_issue = issue.close()
            assert isinstance(closed_issue, Issue)
            assert closed_issue.state == "closed"

    def test_issue_reopen(self, httpx_mock: HTTPXMock, issue_data):
        """issue.reopen() reopens the issue."""
        issue_data["state"] = "closed"
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            json=issue_data,
        )
        reopened_data = {**issue_data, "state": "open"}
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            method="PATCH",
            json=reopened_data,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.get(42)
            reopened = issue.reopen()
            assert reopened.state == "open"

    def test_issue_add_comment(self, httpx_mock: HTTPXMock, issue_data):
        """issue.add_comment() adds a comment."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            json=issue_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42/comments",
            method="POST",
            json={
                "id": 1,
                "body": "Thanks!",
                "user": {
                    "login": "me",
                    "id": 2,
                    "avatar_url": "",
                    "html_url": "",
                    "type": "User",
                },
                "html_url": "https://github.com/owner/repo/issues/42#issuecomment-1",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            },
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.get(42)
            comment = issue.add_comment("Thanks!")
            assert isinstance(comment, Comment)
            assert comment.body == "Thanks!"

    def test_issue_add_labels(self, httpx_mock: HTTPXMock, issue_data):
        """issue.add_labels() adds labels."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            json=issue_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42/labels",
            method="POST",
            json=[
                {"id": 1, "name": "bug", "color": "fc2929"},
                {"id": 2, "name": "priority", "color": "0000ff"},
            ],
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.get(42)
            labels = issue.add_labels("bug", "priority")
            assert len(labels) == 2
            assert labels[0].name == "bug"

    def test_issue_lock(self, httpx_mock: HTTPXMock, issue_data):
        """issue.lock() locks the issue."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            json=issue_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42/lock",
            method="PUT",
            status_code=204,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.get(42)
            issue.lock(reason="resolved")  # Should not raise

    def test_issue_list_comments(self, httpx_mock: HTTPXMock, issue_data):
        """issue.list_comments() returns comments."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42",
            json=issue_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42/comments?per_page=30&page=1",
            json=[
                {
                    "id": 1,
                    "body": "First comment",
                    "user": {
                        "login": "user1",
                        "id": 1,
                        "avatar_url": "",
                        "html_url": "",
                        "type": "User",
                    },
                    "html_url": "",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                },
            ],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/42/comments?per_page=30&page=2",
            json=[],
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            issue = repo.issues.get(42)
            comments = list(issue.list_comments())
            assert len(comments) == 1
            assert isinstance(comments[0], Comment)

    def test_issue_not_bound_raises_error(self):
        """Methods raise error when issue not bound to repo."""
        issue = Issue.from_dict(
            {
                "id": 1,
                "number": 42,
                "title": "Test",
                "body": None,
                "state": "open",
                "locked": False,
                "user": None,
                "assignee": None,
                "assignees": [],
                "labels": [],
                "milestone": None,
                "html_url": "",
                "comments": 0,
                "created_at": None,
                "updated_at": None,
                "closed_at": None,
                "closed_by": None,
            }
        )

        with pytest.raises(RuntimeError, match="not bound"):
            issue.close()


class TestPullRequestMethods:
    """Tests for methods on PullRequest objects."""

    @pytest.fixture
    def pr_data(self):
        """Sample PR data."""
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

    def test_pr_approve(self, httpx_mock: HTTPXMock, pr_data):
        """pr.approve() approves the PR."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123/reviews",
            method="POST",
            json={"id": 1, "state": "APPROVED", "body": "LGTM!"},
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            result = pr.approve(body="LGTM!")
            assert result["state"] == "APPROVED"

    def test_pr_request_changes(self, httpx_mock: HTTPXMock, pr_data):
        """pr.request_changes() requests changes."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123/reviews",
            method="POST",
            json={"id": 1, "state": "CHANGES_REQUESTED", "body": "Please fix X"},
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            result = pr.request_changes("Please fix X")
            assert result["state"] == "CHANGES_REQUESTED"

    def test_pr_comment(self, httpx_mock: HTTPXMock, pr_data):
        """pr.comment() adds a review comment."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123/reviews",
            method="POST",
            json={"id": 1, "state": "COMMENTED", "body": "Looking good"},
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            result = pr.comment("Looking good")
            assert result["state"] == "COMMENTED"

    def test_pr_merge(self, httpx_mock: HTTPXMock, pr_data):
        """pr.merge() merges the PR."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123/merge",
            method="PUT",
            json={"sha": "abc123", "merged": True, "message": "Pull Request successfully merged"},
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            result = pr.merge(merge_method="squash")
            assert result["merged"] is True

    def test_pr_close(self, httpx_mock: HTTPXMock, pr_data):
        """pr.close() closes the PR."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        closed_data = {**pr_data, "state": "closed"}
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            method="PATCH",
            json=closed_data,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            closed_pr = pr.close()
            assert isinstance(closed_pr, PullRequest)
            assert closed_pr.state == "closed"

    def test_pr_request_reviewers(self, httpx_mock: HTTPXMock, pr_data):
        """pr.request_reviewers() requests reviewers."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123/requested_reviewers",
            method="POST",
            json=pr_data,
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            result = pr.request_reviewers(reviewers=["alice", "bob"])
            assert isinstance(result, PullRequest)

    def test_pr_add_comment(self, httpx_mock: HTTPXMock, pr_data):
        """pr.add_comment() adds an issue comment."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/issues/123/comments",
            method="POST",
            json={
                "id": 1,
                "body": "Comment on PR",
                "user": {
                    "login": "me",
                    "id": 2,
                    "avatar_url": "",
                    "html_url": "",
                    "type": "User",
                },
                "html_url": "",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            },
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            comment = pr.add_comment("Comment on PR")
            assert isinstance(comment, Comment)
            assert comment.body == "Comment on PR"

    def test_pr_list_files(self, httpx_mock: HTTPXMock, pr_data):
        """pr.list_files() returns changed files."""
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123",
            json=pr_data,
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123/files?per_page=30&page=1",
            json=[
                {"filename": "src/main.py", "additions": 10, "deletions": 5},
            ],
        )
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/pulls/123/files?per_page=30&page=2",
            json=[],
        )

        with GitHub(token="test") as gh:
            repo = gh.repo("owner/repo")
            pr = repo.pulls.get(123)
            files = list(pr.list_files())
            assert len(files) == 1
            assert files[0]["filename"] == "src/main.py"

    def test_pr_not_bound_raises_error(self):
        """Methods raise error when PR not bound to repo."""
        pr = PullRequest.from_dict(
            {
                "id": 1,
                "number": 123,
                "title": "Test",
                "body": None,
                "state": "open",
                "locked": False,
                "draft": False,
                "merged": False,
                "mergeable": None,
                "user": None,
                "assignee": None,
                "assignees": [],
                "labels": [],
                "milestone": None,
                "html_url": "",
                "head": {"ref": "", "sha": ""},
                "base": {"ref": "", "sha": ""},
                "comments": 0,
                "commits": 0,
                "additions": 0,
                "deletions": 0,
                "changed_files": 0,
                "created_at": None,
                "updated_at": None,
                "closed_at": None,
                "merged_at": None,
                "merged_by": None,
            }
        )

        with pytest.raises(RuntimeError, match="not bound"):
            pr.approve()
