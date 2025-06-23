"""MCP server installation and configuration."""

from typing import List, Optional


async def prepare_mcp_config(
    github_token: str,
    owner: str,
    repo: str,
    branch: str,
    additional_mcp_config: str,
    claude_comment_id: str,
    allowed_tools: List[str],
) -> str:
    """Prepare MCP configuration."""
    # Placeholder implementation
    # The full implementation would:
    # - Install GitHub MCP server
    # - Configure with repository details
    # - Merge additional MCP config
    # - Return JSON configuration string
    
    # Create valid MCP configuration with required mcpServers field
    base_config = {
        "mcpServers": {}
    }
    
    # If additional MCP config is provided, merge it
    if additional_mcp_config and additional_mcp_config.strip():
        try:
            import json
            additional_config = json.loads(additional_mcp_config)
            if isinstance(additional_config, dict) and "mcpServers" in additional_config:
                base_config["mcpServers"].update(additional_config["mcpServers"])
        except json.JSONDecodeError:
            # Invalid JSON, ignore additional config
            pass
    
    import json
    return json.dumps(base_config)