"""Create initial comment functionality."""

from typing import Dict, Any
from ...api.client import RestClient
from ...context import ParsedGitHubContext


async def create_initial_comment(rest_client: RestClient, context: ParsedGitHubContext) -> int:
    """Create initial tracking comment."""
    # Placeholder implementation
    # The full implementation would:
    # - Create a comment with spinner and initial message
    # - Handle both PR and issue comments
    # - Return the comment ID
    
    comment_body = "🔄 Working on your request..."
    
    if context.is_pr:
        endpoint = f"repos/{context.repository.owner}/{context.repository.repo}/issues/{context.entity_number}/comments"
    else:
        endpoint = f"repos/{context.repository.owner}/{context.repository.repo}/issues/{context.entity_number}/comments"
    
    response = await rest_client.post(endpoint, {"body": comment_body})
    return response["id"]