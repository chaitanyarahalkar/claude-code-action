"""Main prompt creation functionality."""

import os
import aiofiles
from typing import List, Dict, Any, Optional
from ..github.context import ParsedGitHubContext
from ..github.data.fetcher import FetchDataResult
from .types import PreparedContext, EventData, CommonFields


BASE_ALLOWED_TOOLS = [
    "Edit",
    "MultiEdit", 
    "Glob",
    "Grep",
    "LS", 
    "Read",
    "Write",
    "mcp__github_file_ops__commit_files",
    "mcp__github_file_ops__delete_files", 
    "mcp__github_file_ops__update_claude_comment",
]

DISALLOWED_TOOLS = ["WebSearch", "WebFetch"]


def build_allowed_tools_string(custom_allowed_tools: Optional[List[str]] = None) -> str:
    """Build allowed tools string."""
    base_tools = BASE_ALLOWED_TOOLS.copy()
    
    all_allowed_tools = ",".join(base_tools)
    if custom_allowed_tools:
        all_allowed_tools = f"{all_allowed_tools},{','.join(custom_allowed_tools)}"
    
    return all_allowed_tools


def build_disallowed_tools_string(
    custom_disallowed_tools: Optional[List[str]] = None,
    allowed_tools: Optional[List[str]] = None,
) -> str:
    """Build disallowed tools string."""
    disallowed_tools = DISALLOWED_TOOLS.copy()
    
    # If user has explicitly allowed some hardcoded disallowed tools, remove them
    if allowed_tools:
        disallowed_tools = [
            tool for tool in disallowed_tools 
            if tool not in allowed_tools
        ]
    
    all_disallowed_tools = ",".join(disallowed_tools)
    if custom_disallowed_tools:
        if all_disallowed_tools:
            all_disallowed_tools = f"{all_disallowed_tools},{','.join(custom_disallowed_tools)}"
        else:
            all_disallowed_tools = ",".join(custom_disallowed_tools)
    
    return all_disallowed_tools


def prepare_context(
    context: ParsedGitHubContext,
    claude_comment_id: str,
    base_branch: Optional[str] = None,
    claude_branch: Optional[str] = None,
) -> PreparedContext:
    """Prepare context for prompt generation."""
    # This is a simplified version - would need full implementation
    # based on the TypeScript version's complex logic
    
    common_fields = CommonFields(
        repository=context.repository.full_name,
        claude_comment_id=claude_comment_id,
        trigger_phrase=context.inputs.trigger_phrase,
        trigger_username=context.actor,
        custom_instructions=context.inputs.custom_instructions if context.inputs.custom_instructions else None,
        allowed_tools=",".join(context.inputs.allowed_tools) if context.inputs.allowed_tools else None,
        disallowed_tools=",".join(context.inputs.disallowed_tools) if context.inputs.disallowed_tools else None,
        direct_prompt=context.inputs.direct_prompt if context.inputs.direct_prompt else None,
        claude_branch=claude_branch,
    )
    
    # Convert common fields to PreparedContext
    return PreparedContext(
        repository=common_fields.repository,
        claude_comment_id=common_fields.claude_comment_id,
        trigger_phrase=common_fields.trigger_phrase,
        trigger_username=common_fields.trigger_username,
        custom_instructions=common_fields.custom_instructions,
        allowed_tools=common_fields.allowed_tools,
        disallowed_tools=common_fields.disallowed_tools,
        direct_prompt=common_fields.direct_prompt,
        claude_branch=common_fields.claude_branch,
        # event_data would be populated based on event type
    )


def generate_prompt(context: PreparedContext, github_data: FetchDataResult) -> str:
    """Generate the prompt content."""
    # This would contain the complex prompt generation logic
    # from the TypeScript version - simplified for now
    
    prompt_content = f"""You are Claude, an AI assistant designed to help with GitHub issues and pull requests.

Repository: {context.repository}
Comment ID: {context.claude_comment_id}
Trigger Phrase: {context.trigger_phrase}
"""
    
    if context.custom_instructions:
        prompt_content += f"\n\nCUSTOM INSTRUCTIONS:\n{context.custom_instructions}"
    
    return prompt_content


async def create_prompt(
    claude_comment_id: int,
    base_branch: Optional[str],
    claude_branch: Optional[str], 
    github_data: FetchDataResult,
    context: ParsedGitHubContext,
) -> None:
    """Create the prompt file."""
    try:
        prepared_context = prepare_context(
            context,
            str(claude_comment_id),
            base_branch,
            claude_branch,
        )
        
        # Create the prompts directory
        runner_temp = os.environ.get("RUNNER_TEMP", "/tmp")
        prompts_dir = f"{runner_temp}/claude-prompts"
        os.makedirs(prompts_dir, exist_ok=True)
        
        # Generate the prompt
        prompt_content = generate_prompt(prepared_context, github_data)
        
        # Log the final prompt
        print("===== FINAL PROMPT =====")
        print(prompt_content)
        print("=======================")
        
        # Write the prompt file
        prompt_file = f"{prompts_dir}/claude-prompt.txt"
        async with aiofiles.open(prompt_file, 'w') as f:
            await f.write(prompt_content)
        
        # Set allowed tools environment variables
        all_allowed_tools = build_allowed_tools_string(context.inputs.allowed_tools)
        all_disallowed_tools = build_disallowed_tools_string(
            context.inputs.disallowed_tools,
            context.inputs.allowed_tools,
        )
        
        # Export environment variables
        if github_env := os.environ.get("GITHUB_ENV"):
            async with aiofiles.open(github_env, 'a') as f:
                await f.write(f"ALLOWED_TOOLS={all_allowed_tools}\n")
                await f.write(f"DISALLOWED_TOOLS={all_disallowed_tools}\n")
        else:
            os.environ["ALLOWED_TOOLS"] = all_allowed_tools
            os.environ["DISALLOWED_TOOLS"] = all_disallowed_tools
            
    except Exception as error:
        print(f"::error::Create prompt failed with error: {error}")
        raise