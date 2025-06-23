"""Permission validation logic."""

from typing import Dict, Any
from ..context import ParsedGitHubContext
from ..api.client import RestClient


class PermissionError(Exception):
    """Permission-related errors."""
    pass


async def check_write_permissions(rest_client: RestClient, context: ParsedGitHubContext) -> bool:
    """Check if the actor has write permissions to the repository."""
    try:
        # Check collaborator permissions
        endpoint = f"repos/{context.repository.owner}/{context.repository.repo}/collaborators/{context.actor}/permission"
        
        try:
            response = await rest_client.get(endpoint)
            permission = response.get("permission", "").lower()
            
            # Write permissions include: admin, maintain, write
            write_permissions = {"admin", "maintain", "write"}
            has_write = permission in write_permissions
            
            print(f"Actor {context.actor} has permission: {permission}")
            return has_write
            
        except Exception as e:
            # If we can't check permissions, assume they don't have write access
            print(f"Could not check permissions for {context.actor}: {e}")
            return False
            
    except Exception as e:
        print(f"Permission check failed: {e}")
        return False