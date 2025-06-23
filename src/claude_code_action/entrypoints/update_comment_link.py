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

        # Create the updated comment body
        github_server_url = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
        job_link = f"{github_server_url}/{repository}/actions/runs/{github_run_id}"
        
        # Determine status and create appropriate message
        if not prepare_success:
            comment_body = f"❌ **Failed to prepare Claude request**\n\n"
            if prepare_error:
                comment_body += f"Error: {prepare_error}\n\n"
            comment_body += f"[View run details]({job_link})"
        elif claude_success:
            comment_body = f"✅ **Request completed successfully**\n\n"
            if claude_branch:
                comment_body += f"Branch: `{claude_branch}`\n\n"
            if output_file:
                comment_body += f"Changes have been made to your codebase.\n\n"
            comment_body += f"[View run details]({job_link})"
        else:
            comment_body = f"❌ **Request failed**\n\n"
            if claude_branch:
                comment_body += f"Branch: `{claude_branch}`\n\n"
            comment_body += f"[View run details]({job_link})"

        # Update the comment
        endpoint = f"repos/{repository}/issues/comments/{claude_comment_id}"
        await octokit.rest.patch(endpoint, {"body": comment_body})

        print("Comment updated successfully")
        
        # Clean up the session
        await octokit.close()

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