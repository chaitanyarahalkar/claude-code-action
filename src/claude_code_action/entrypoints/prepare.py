#!/usr/bin/env python3
"""
Prepare the Claude action by checking trigger conditions, verifying human actor,
and creating the initial tracking comment
"""

import os
import sys
from typing import Optional

from ..github.token import setup_github_token
from ..github.validation.trigger import check_trigger_action
from ..github.validation.actor import check_human_actor
from ..github.validation.permissions import check_write_permissions
from ..github.operations.comments.create_initial import create_initial_comment
from ..github.operations.branch import setup_branch
from ..github.operations.comments.update_with_branch import update_tracking_comment
from ..mcp.install_mcp_server import prepare_mcp_config
from ..create_prompt import create_prompt
from ..github.api.client import create_octokit
from ..github.data.fetcher import fetch_github_data
from ..github.context import parse_github_context


def set_output(name: str, value: str) -> None:
    """Set GitHub Actions output."""
    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with open(github_output, "a") as f:
            f.write(f"{name}={value}\n")
    else:
        # Fallback for older runners
        print(f"::set-output name={name}::{value}")


def set_failed(message: str) -> None:
    """Set GitHub Actions failed status."""
    print(f"::error::{message}")
    sys.exit(1)


def export_variable(name: str, value: str) -> None:
    """Export environment variable for GitHub Actions."""
    if github_env := os.environ.get("GITHUB_ENV"):
        with open(github_env, "a") as f:
            f.write(f"{name}={value}\n")
    else:
        os.environ[name] = value


async def run() -> None:
    """Main execution logic."""
    try:
        # Step 1: Setup GitHub token
        github_token = await setup_github_token()
        octokit = create_octokit(github_token)

        # Step 2: Parse GitHub context (once for all operations)
        context = parse_github_context()

        # Step 3: Check write permissions
        has_write_permissions = await check_write_permissions(
            octokit.rest, context
        )
        if not has_write_permissions:
            raise Exception(
                "Actor does not have write permissions to the repository"
            )

        # Step 4: Check trigger conditions
        contains_trigger = await check_trigger_action(context)

        if not contains_trigger:
            print("No trigger found, skipping remaining steps")
            set_output("contains_trigger", "false")
            return

        # Step 5: Check if actor is human
        await check_human_actor(octokit.rest, context)

        # Step 6: Create initial tracking comment
        comment_id = await create_initial_comment(octokit.rest, context)

        # Step 7: Fetch GitHub data (once for both branch setup and prompt creation)
        github_data = await fetch_github_data(
            octokits=octokit,
            repository=f"{context.repository.owner}/{context.repository.repo}",
            pr_number=str(context.entity_number),
            is_pr=context.is_pr,
            trigger_username=context.actor,
        )

        # Step 8: Setup branch
        branch_info = await setup_branch(octokit, github_data, context)

        # Set outputs for GitHub Actions
        set_output("claude_comment_id", str(comment_id))
        set_output("CLAUDE_BRANCH", branch_info.claude_branch or "")
        set_output("BASE_BRANCH", branch_info.base_branch)
        set_output("GITHUB_TOKEN", github_token)
        set_output("contains_trigger", "true")

        # Step 9: Update initial comment with branch link (only for issues that created a new branch)
        if branch_info.claude_branch:
            await update_tracking_comment(
                octokit, context, comment_id, branch_info.claude_branch
            )

        # Step 10: Create prompt file
        await create_prompt(
            comment_id,
            branch_info.base_branch,
            branch_info.claude_branch,
            github_data,
            context,
        )

        # Step 11: Get MCP configuration
        additional_mcp_config = os.environ.get("MCP_CONFIG", "")
        mcp_config = await prepare_mcp_config(
            github_token=github_token,
            owner=context.repository.owner,
            repo=context.repository.repo,
            branch=branch_info.current_branch,
            additional_mcp_config=additional_mcp_config,
            claude_comment_id=str(comment_id),
            allowed_tools=context.inputs.allowed_tools,
        )
        set_output("mcp_config", mcp_config)
        
        # Clean up the session
        await octokit.close()

    except Exception as error:
        error_message = str(error)
        set_failed(f"Prepare step failed with error: {error_message}")
        # Also output the clean error message for the action to capture
        set_output("prepare_error", error_message)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    import asyncio
    asyncio.run(run())


if __name__ == "__main__":
    main()