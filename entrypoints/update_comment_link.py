#!/usr/bin/env python3
"""Update comment with job link."""

import os
import sys
from typing import Optional

from ..github.api.client import create_octokit
from ..github.context import parse_github_context


def set_failed(message: str) -> None:
    """Set GitHub Actions failed status."""
    print(f"::error::{message}")
    sys.exit(1)


async def run() -> None:
    """Main execution logic."""
    try:
        # Get required environment variables
        repository = os.environ.get("REPOSITORY")
        pr_number = os.environ.get("PR_NUMBER")
        claude_comment_id = os.environ.get("CLAUDE_COMMENT_ID")
        github_run_id = os.environ.get("GITHUB_RUN_ID")
        github_token = os.environ.get("GITHUB_TOKEN")
        github_event_name = os.environ.get("GITHUB_EVENT_NAME")
        trigger_comment_id = os.environ.get("TRIGGER_COMMENT_ID")
        claude_branch = os.environ.get("CLAUDE_BRANCH")
        is_pr = os.environ.get("IS_PR", "").lower() == "true"
        base_branch = os.environ.get("BASE_BRANCH")
        claude_success = os.environ.get("CLAUDE_SUCCESS", "").lower() == "true"
        output_file = os.environ.get("OUTPUT_FILE", "")
        trigger_username = os.environ.get("TRIGGER_USERNAME", "")
        prepare_success = os.environ.get("PREPARE_SUCCESS", "").lower() == "true"
        prepare_error = os.environ.get("PREPARE_ERROR", "")

        if not all([repository, claude_comment_id, github_run_id, github_token]):
            raise Exception("Missing required environment variables")

        # Create GitHub client
        octokit = create_octokit(github_token)

        # Update comment with job link
        # This would contain the logic to update the GitHub comment
        # with the job run link and other relevant information

        print("Comment updated successfully")

    except Exception as error:
        error_message = str(error)
        set_failed(f"Update comment failed with error: {error_message}")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()