"""Update comment with branch information."""

from ...api.client import OctokitWrapper
from ...context import ParsedGitHubContext


async def update_tracking_comment(
    octokit: OctokitWrapper,
    context: ParsedGitHubContext,
    comment_id: int,
    claude_branch: str,
) -> None:
    """Update tracking comment with branch information."""
    # Placeholder implementation
    # The full implementation would update the comment
    # with branch link and status information
    
    comment_body = f"🔄 Working on your request...\n\nBranch: `{claude_branch}`"
    
    endpoint = f"repos/{context.repository.owner}/{context.repository.repo}/issues/comments/{comment_id}"
    await octokit.rest.patch(endpoint, {"body": comment_body})