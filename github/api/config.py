"""GitHub API configuration."""

import os

# GitHub API configuration
GITHUB_SERVER_URL = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
GITHUB_API_URL = os.environ.get("GITHUB_API_URL", "https://api.github.com")
GITHUB_GRAPHQL_URL = os.environ.get("GITHUB_GRAPHQL_URL", "https://api.github.com/graphql")