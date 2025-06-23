"""Actor validation logic."""

from typing import Dict, Any
from ..context import ParsedGitHubContext
from ..api.client import RestClient


class ActorValidationError(Exception):
    """Actor validation errors."""
    pass


async def check_human_actor(rest_client: RestClient, context: ParsedGitHubContext) -> None:
    """Check if the actor is human (not a bot)."""
    try:
        # Get user information
        user_data = await rest_client.get(f"users/{context.actor}")
        
        # Check if user is a bot
        if user_data.get("type") == "Bot":
            raise ActorValidationError(f"Actor {context.actor} is a bot")
        
        print(f"Actor {context.actor} validated as human")
        
    except Exception as e:
        if isinstance(e, ActorValidationError):
            raise e
        raise ActorValidationError(f"Failed to validate actor {context.actor}: {e}")