"""GitHub API resource handlers."""

from github_rest_api.resources.repos import ReposResource, AsyncReposResource
from github_rest_api.resources.issues import IssuesResource, AsyncIssuesResource
from github_rest_api.resources.pulls import PullsResource, AsyncPullsResource
from github_rest_api.resources.users import UsersResource, AsyncUsersResource

__all__ = [
    "ReposResource",
    "AsyncReposResource",
    "IssuesResource",
    "AsyncIssuesResource",
    "PullsResource",
    "AsyncPullsResource",
    "UsersResource",
    "AsyncUsersResource",
]
