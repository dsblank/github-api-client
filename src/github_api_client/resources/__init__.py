"""GitHub API resource handlers."""

from github_api_client.resources.issues import AsyncIssuesResource, IssuesResource
from github_api_client.resources.pulls import AsyncPullsResource, PullsResource
from github_api_client.resources.releases import AsyncReleasesResource, ReleasesResource
from github_api_client.resources.repos import AsyncReposResource, ReposResource
from github_api_client.resources.users import AsyncUsersResource, UsersResource

__all__ = [
    "ReposResource",
    "AsyncReposResource",
    "IssuesResource",
    "AsyncIssuesResource",
    "PullsResource",
    "AsyncPullsResource",
    "ReleasesResource",
    "AsyncReleasesResource",
    "UsersResource",
    "AsyncUsersResource",
]
