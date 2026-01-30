"""A Pythonic interface to GitHub's REST API."""

from github_rest_api.auth import (
    get_token,
    get_token_from_env,
    get_token_from_gh_cli,
    get_token_from_hosts_file,
)
from github_rest_api.client import GitHub, AsyncGitHub
from github_rest_api.exceptions import (
    GitHubError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from github_rest_api.repo import Repo, AsyncRepo
from github_rest_api.models import (
    Issue,
    PullRequest,
    Repository,
    User,
    Comment,
    Label,
    Milestone,
    Branch,
)

__version__ = "0.1.0"
__all__ = [
    # Clients
    "GitHub",
    "AsyncGitHub",
    # Repository interface
    "Repo",
    "AsyncRepo",
    # Models
    "Issue",
    "PullRequest",
    "Repository",
    "User",
    "Comment",
    "Label",
    "Milestone",
    "Branch",
    # Exceptions
    "GitHubError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    # Auth helpers
    "get_token",
    "get_token_from_env",
    "get_token_from_gh_cli",
    "get_token_from_hosts_file",
]
