#!/usr/bin/env python3

import os
import sys
from typing import Dict, Any

from claude_code_action.base_action.prepare_prompt import prepare_prompt
from claude_code_action.base_action.run_claude import run_claude
from claude_code_action.base_action.setup_claude_code_settings import setup_claude_code_settings
from claude_code_action.base_action.validate_env import validate_environment_variables


async def run() -> None:
    """Main entry point for the base action."""
    try:
        validate_environment_variables()
        
        await setup_claude_code_settings()
        
        prompt_config = await prepare_prompt({
            "prompt": os.environ.get("INPUT_PROMPT", ""),
            "prompt_file": os.environ.get("INPUT_PROMPT_FILE", ""),
        })
        
        await run_claude(prompt_config["path"], {
            "allowed_tools": os.environ.get("INPUT_ALLOWED_TOOLS"),
            "disallowed_tools": os.environ.get("INPUT_DISALLOWED_TOOLS"),
            "max_turns": os.environ.get("INPUT_MAX_TURNS"),
            "mcp_config": os.environ.get("INPUT_MCP_CONFIG"),
            "system_prompt": os.environ.get("INPUT_SYSTEM_PROMPT"),
            "append_system_prompt": os.environ.get("INPUT_APPEND_SYSTEM_PROMPT"),
            "claude_env": os.environ.get("INPUT_CLAUDE_ENV"),
        })
        
    except Exception as error:
        print(f"::error::Action failed with error: {error}")
        # Set GitHub Actions outputs for failure
        if github_output := os.environ.get("GITHUB_OUTPUT"):
            with open(github_output, "a") as f:
                f.write(f"conclusion=failure\n")
        else:
            print(f"::set-output name=conclusion::failure")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())