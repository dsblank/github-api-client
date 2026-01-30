"""Authentication helpers for GitHub API.

Token resolution order:
1. Explicit token passed to client
2. GH_TOKEN or GITHUB_TOKEN environment variable
3. gh CLI auth token (via `gh auth token` command)
4. gh CLI hosts.yml file (plain text fallback)
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

# Optional YAML support for reading hosts.yml directly
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def get_token_from_env() -> str | None:
    """Get token from environment variables.

    Checks GH_TOKEN first (used by gh CLI), then GITHUB_TOKEN.

    Returns:
        Token string or None if not found.
    """
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def get_token_from_gh_cli(hostname: str = "github.com") -> str | None:
    """Get token from gh CLI using `gh auth token`.

    This is the recommended way to get the token as it works with
    both secure credential stores and plain text storage.

    Args:
        hostname: GitHub hostname (default: github.com).

    Returns:
        Token string or None if gh CLI is not available or not authenticated.
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "token", "--hostname", hostname],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        pass
    return None


def get_token_from_hosts_file(hostname: str = "github.com") -> str | None:
    """Get token from gh CLI's hosts.yml file.

    This only works if gh was configured with --insecure-storage
    or if no system credential store was available.

    Args:
        hostname: GitHub hostname (default: github.com).

    Returns:
        Token string or None if file doesn't exist or token not found.
    """
    if not HAS_YAML:
        return None

    # Check config directory locations
    config_dir = os.environ.get("GH_CONFIG_DIR")
    if not config_dir:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        config_dir = str(Path(xdg_config) / "gh")

    hosts_file = Path(config_dir) / "hosts.yml"
    if not hosts_file.exists():
        return None

    try:
        with open(hosts_file) as f:
            hosts: dict[str, Any] = yaml.safe_load(f) or {}
            host_config = hosts.get(hostname, {})
            return host_config.get("oauth_token")
    except (OSError, yaml.YAMLError):
        return None


def get_token(hostname: str = "github.com") -> str | None:
    """Get GitHub token using all available methods.

    Tries in order:
    1. Environment variables (GH_TOKEN, GITHUB_TOKEN)
    2. gh CLI command (`gh auth token`)
    3. gh CLI hosts.yml file

    Args:
        hostname: GitHub hostname (default: github.com).

    Returns:
        Token string or None if no token found.
    """
    # Try environment variables first
    token = get_token_from_env()
    if token:
        return token

    # Try gh CLI command
    token = get_token_from_gh_cli(hostname)
    if token:
        return token

    # Fall back to hosts.yml file
    return get_token_from_hosts_file(hostname)
