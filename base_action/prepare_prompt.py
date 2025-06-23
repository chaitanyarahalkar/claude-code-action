import os
import aiofiles
from pathlib import Path
from typing import Dict, Any, TypedDict


class PreparePromptInput(TypedDict):
    prompt: str
    prompt_file: str


class PreparePromptConfig(TypedDict):
    type: str  # "file" or "inline"
    path: str


async def validate_and_prepare_prompt(input_data: PreparePromptInput) -> PreparePromptConfig:
    """Validate inputs and prepare prompt configuration."""
    # Validate inputs
    if not input_data["prompt"] and not input_data["prompt_file"]:
        raise ValueError(
            "Neither 'prompt' nor 'prompt_file' was provided. At least one is required."
        )
    
    if input_data["prompt"] and input_data["prompt_file"]:
        raise ValueError(
            "Both 'prompt' and 'prompt_file' were provided. Please specify only one."
        )
    
    # Handle prompt file
    if input_data["prompt_file"]:
        prompt_path = Path(input_data["prompt_file"])
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file '{input_data['prompt_file']}' does not exist.")
        
        # Validate that the file is not empty
        if prompt_path.stat().st_size == 0:
            raise ValueError("Prompt file is empty. Please provide a non-empty prompt.")
        
        return {
            "type": "file",
            "path": str(prompt_path),
        }
    
    # Handle inline prompt
    if not input_data["prompt"] or input_data["prompt"].strip() == "":
        raise ValueError("Prompt is empty. Please provide a non-empty prompt.")
    
    inline_path = "/tmp/claude-action/prompt.txt"
    return {
        "type": "inline",
        "path": inline_path,
    }


async def create_temporary_prompt_file(prompt: str, prompt_path: str) -> None:
    """Create a temporary prompt file."""
    # Create the directory path
    dir_path = Path(prompt_path).parent
    dir_path.mkdir(parents=True, exist_ok=True)
    
    async with aiofiles.open(prompt_path, 'w') as f:
        await f.write(prompt)


async def prepare_prompt(input_data: PreparePromptInput) -> PreparePromptConfig:
    """Prepare prompt configuration and create temporary file if needed."""
    config = await validate_and_prepare_prompt(input_data)
    
    if config["type"] == "inline":
        await create_temporary_prompt_file(input_data["prompt"], config["path"])
    
    return config