"""A Pythonic interface to GitHub's REST API."""

from github_api_client.auth import (
    get_token,
    get_token_from_env,
    get_token_from_gh_cli,
    get_token_from_hosts_file,
)
from github_api_client.client import AsyncGitHub, GitHub
from github_api_client.exceptions import (
    AuthenticationError,
    GitHubError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from github_api_client.models import (
    Branch,
    Comment,
    Issue,
    Label,
    Milestone,
    PullRequest,
    Repository,
    User,
)
from github_api_client.repo import AsyncRepo, Repo

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
