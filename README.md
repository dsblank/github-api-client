# github-rest-api

A Pythonic interface to GitHub's REST API with typed models, automatic authentication, and rate limit handling.

## Installation

```bash
pip install github-rest-api
```

## Quick Start

```python
from github_rest_api import GitHub

gh = GitHub()  # Auto-detects token from environment or gh CLI
repo = gh.repo("comet-ml/opik")

# List issues (returns typed Issue objects)
for issue in repo.issues.list():
    print(f"#{issue.number}: {issue.title}")
    print(f"  Created: {issue.created_at}")  # datetime object
    print(f"  Labels: {[l.name for l in issue.labels]}")
```

## Authentication

The client automatically detects authentication tokens in this order:

1. **Explicit token** - Pass directly to the constructor
2. **Environment variables** - `GH_TOKEN` or `GITHUB_TOKEN`
3. **gh CLI command** - Runs `gh auth token` (works with secure credential stores)
4. **gh CLI hosts.yml** - Reads `~/.config/gh/hosts.yml`

```python
# Auto-detect (recommended)
gh = GitHub()

# Explicit token
gh = GitHub(token="ghp_xxxxxxxxxxxx")

# No authentication
gh = GitHub(token=None)
```

### Using with gh CLI

If you have the [GitHub CLI](https://cli.github.com/) installed:

```bash
gh auth login
```

The client will automatically use your credentials.

## Typed Models

All API responses return typed objects with attribute access and methods:

```python
repo = gh.repo("owner/repo")

# Issues
issue = repo.issues.get(123)
issue.title           # str
issue.body            # str | None
issue.state           # "open" or "closed"
issue.created_at      # datetime
issue.user.login      # str
issue.labels          # list[Label]
issue.is_open         # bool property

# Methods on objects
issue.close()
issue.reopen()
issue.add_comment("Thanks for reporting!")
issue.add_labels("bug", "priority:high")
issue.lock(reason="resolved")

# Pull Requests
pr = repo.pulls.get(456)
pr.title              # str
pr.head_ref           # str (branch name)
pr.base_ref           # str
pr.merged             # bool
pr.mergeable          # bool | None
pr.additions          # int
pr.deletions          # int

# Methods on PR objects
pr.approve()
pr.approve(body="LGTM!")
pr.request_changes("Please fix the tests")
pr.comment("Looking into this")
pr.merge(merge_method="squash")
pr.request_reviewers(reviewers=["alice", "bob"])

# Repository
info = repo.get()
info.stars            # int (alias for stargazers_count)
info.forks            # int
info.language         # str | None
info.default_branch   # str
```

## Repository Interface

The `repo()` method provides a convenient interface without repeating owner/repo:

```python
repo = gh.repo("owner/repo")
# or
repo = gh.repo("owner", "repo")

# Issues
repo.issues.list(state="open", labels="bug")
repo.issues.get(123)
repo.issues.create(title="Bug", body="Description", labels=["bug"])

# Pull Requests
repo.pulls.list(state="open")
repo.pulls.get(456)
repo.pulls.create(title="Feature", head="feature-branch", base="main")

# Repository info
repo.get()
repo.branches()
repo.contributors()
repo.languages()
repo.tags()

# Convenience shortcuts
repo.star()
repo.unstar()
repo.is_starred()
repo.fork()
repo.fork(organization="my-org")
repo.subscribe()    # watch
repo.unsubscribe()  # unwatch
```

## Search API

Search across all of GitHub:

```python
# Search issues and PRs
for item in gh.search.issues("bug label:critical repo:owner/repo"):
    print(item["title"])

# Search with filters
gh.search.issues("is:issue is:open author:username")
gh.search.issues("is:pr is:merged repo:owner/repo")

# Search repositories
for repo in gh.search.repositories("machine learning stars:>1000 language:python"):
    print(repo["full_name"], repo["stargazers_count"])

# Search code
for result in gh.search.code("def authenticate repo:owner/repo"):
    print(result["path"])

# Search users
for user in gh.search.users("location:tokyo followers:>100"):
    print(user["login"])

# Search commits
for commit in gh.search.commits("fix bug repo:owner/repo"):
    print(commit["sha"], commit["commit"]["message"])
```

## Rate Limit Handling

### Automatic Retry

Enable automatic retry on rate limits:

```python
gh = GitHub(auto_retry=True, max_retries=3)

# Will automatically wait and retry when rate limited
for issue in repo.issues.list():
    process(issue)
```

### Check Rate Limit Status

```python
status = gh.rate_limit()
print(f"Core: {status['resources']['core']['remaining']}/{status['resources']['core']['limit']}")
print(f"Search: {status['resources']['search']['remaining']}/{status['resources']['search']['limit']}")
```

## Async Usage

All operations are available in async form:

```python
import asyncio
from github_rest_api import AsyncGitHub

async def main():
    async with AsyncGitHub(auto_retry=True) as gh:
        repo = gh.repo("owner/repo")

        # Async iteration
        async for issue in repo.issues.list():
            print(issue.title)

        # Async operations
        pr = await repo.pulls.get(123)
        await pr.approve()

asyncio.run(main())
```

## Error Handling

```python
from github_rest_api import (
    GitHub,
    GitHubError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

gh = GitHub()
repo = gh.repo("owner/repo")

try:
    issue = repo.issues.get(99999)
except NotFoundError:
    print("Issue not found")
except AuthenticationError:
    print("Invalid or missing token")
except RateLimitError as e:
    print(f"Rate limited. Resets at: {e.reset_at}")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except GitHubError as e:
    print(f"API error [{e.status_code}]: {e.message}")
```

## Complete Example

```python
from github_rest_api import GitHub

# Initialize with auto-retry
gh = GitHub(auto_retry=True)
repo = gh.repo("comet-ml/opik")

# Get repository info
info = repo.get()
print(f"{info.full_name}: {info.stars} stars, {info.language}")

# List open issues with a specific label
for issue in repo.issues.list(state="open", labels="bug"):
    print(f"#{issue.number}: {issue.title}")
    print(f"  By: {issue.user.login} on {issue.created_at:%Y-%m-%d}")

    # Add a comment
    issue.add_comment("Looking into this!")

# List open PRs
for pr in repo.pulls.list(state="open"):
    print(f"PR #{pr.number}: {pr.title}")
    print(f"  {pr.head_ref} -> {pr.base_ref}")
    print(f"  +{pr.additions} -{pr.deletions}")

# Search for related issues across GitHub
for issue in gh.search.issues("opik bug is:open"):
    print(f"{issue['repository_url']}: {issue['title']}")

# Star the repo
repo.star()
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## License

MIT
