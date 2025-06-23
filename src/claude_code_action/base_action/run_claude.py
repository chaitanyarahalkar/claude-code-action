import os
import sys
import json
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any
import aiofiles


class ClaudeOptions:
    def __init__(
        self,
        allowed_tools: Optional[str] = None,
        disallowed_tools: Optional[str] = None,
        max_turns: Optional[str] = None,
        mcp_config: Optional[str] = None,
        system_prompt: Optional[str] = None,
        append_system_prompt: Optional[str] = None,
        claude_env: Optional[str] = None,
    ):
        self.allowed_tools = allowed_tools
        self.disallowed_tools = disallowed_tools
        self.max_turns = max_turns
        self.mcp_config = mcp_config
        self.system_prompt = system_prompt
        self.append_system_prompt = append_system_prompt
        self.claude_env = claude_env


class PreparedConfig:
    def __init__(self, claude_args: list[str], prompt_path: str, env: Dict[str, str]):
        self.claude_args = claude_args
        self.prompt_path = prompt_path
        self.env = env


def parse_custom_env_vars(claude_env: Optional[str]) -> Dict[str, str]:
    """Parse custom environment variables from YAML-like format."""
    if not claude_env or claude_env.strip() == "":
        return {}
    
    custom_env: Dict[str, str] = {}
    
    # Split by lines and parse each line as KEY: VALUE
    lines = claude_env.split("\n")
    
    for line in lines:
        trimmed_line = line.strip()
        if trimmed_line == "" or trimmed_line.startswith("#"):
            continue  # Skip empty lines and comments
        
        colon_index = trimmed_line.find(":")
        if colon_index == -1:
            continue  # Skip lines without colons
        
        key = trimmed_line[:colon_index].strip()
        value = trimmed_line[colon_index + 1:].strip()
        
        if key:
            custom_env[key] = value
    
    return custom_env


def prepare_run_config(prompt_path: str, options: ClaudeOptions) -> PreparedConfig:
    """Prepare the configuration for running Claude."""
    base_args = ["-p", "--verbose", "--output-format", "stream-json"]
    claude_args = base_args.copy()
    
    if options.allowed_tools:
        claude_args.extend(["--allowedTools", options.allowed_tools])
    if options.disallowed_tools:
        claude_args.extend(["--disallowedTools", options.disallowed_tools])
    if options.max_turns:
        try:
            max_turns_num = int(options.max_turns)
            if max_turns_num <= 0:
                raise ValueError()
            claude_args.extend(["--max-turns", options.max_turns])
        except ValueError:
            raise ValueError(f"maxTurns must be a positive number, got: {options.max_turns}")
    if options.mcp_config:
        claude_args.extend(["--mcp-config", options.mcp_config])
    if options.system_prompt:
        claude_args.extend(["--system-prompt", options.system_prompt])
    if options.append_system_prompt:
        claude_args.extend(["--append-system-prompt", options.append_system_prompt])
    
    # Parse custom environment variables
    custom_env = parse_custom_env_vars(options.claude_env)
    
    return PreparedConfig(claude_args, prompt_path, custom_env)


async def run_claude(prompt_path: str, options: Dict[str, Optional[str]]) -> None:
    """Run Claude with the specified configuration."""
    claude_options = ClaudeOptions(**{k: v for k, v in options.items() if v is not None})
    config = prepare_run_config(prompt_path, claude_options)
    
    # Set up paths
    runner_temp = os.environ.get("RUNNER_TEMP", "/tmp")
    execution_file = os.path.join(runner_temp, "claude-execution-output.json")
    
    # Log prompt file size
    try:
        prompt_size = Path(config.prompt_path).stat().st_size
        print(f"Prompt file size: {prompt_size} bytes")
    except Exception:
        print("Prompt file size: unknown bytes")
    
    # Log custom environment variables if any
    if config.env:
        env_keys = ", ".join(config.env.keys())
        print(f"Custom environment variables: {env_keys}")
    
    print(f"Running Claude with prompt from file: {config.prompt_path}")
    
    # Debug environment variables
    model = os.environ.get("ANTHROPIC_MODEL", "")
    use_bedrock = os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1"
    use_vertex = os.environ.get("CLAUDE_CODE_USE_VERTEX") == "1"
    
    print(f"Model: {model}")
    print(f"Use Bedrock: {use_bedrock}")
    print(f"Use Vertex: {use_vertex}")
    
    if use_bedrock:
        aws_region = os.environ.get("AWS_REGION", "")
        aws_access_key_set = "Yes" if os.environ.get("AWS_ACCESS_KEY_ID") else "No"
        aws_secret_key_set = "Yes" if os.environ.get("AWS_SECRET_ACCESS_KEY") else "No"
        aws_session_token_set = "Yes" if os.environ.get("AWS_SESSION_TOKEN") else "No"
        bedrock_base_url = os.environ.get("ANTHROPIC_BEDROCK_BASE_URL", "")
        
        print(f"AWS Region: {aws_region}")
        print(f"AWS Access Key set: {aws_access_key_set}")
        print(f"AWS Secret Key set: {aws_secret_key_set}")
        print(f"AWS Session Token set: {aws_session_token_set}")
        print(f"Bedrock Base URL: {bedrock_base_url}")
    
    print(f"Claude command: {' '.join(claude_cmd)}")
    
    # Prepare environment
    process_env = os.environ.copy()
    process_env.update(config.env)
    
    # Create the full claude command with prompt file input
    claude_cmd = ["claude"] + config.claude_args + [config.prompt_path]
    
    # Capture output
    output = ""
    
    try:
        # Claude process with direct file input
        claude_process = await asyncio.create_subprocess_exec(
            *claude_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=process_env
        )
        
        # Read output streaming
        async def read_output():
            nonlocal output
            if claude_process.stdout:
                async for line in claude_process.stdout:
                    text = line.decode()
                    
                    # Try to parse and pretty print JSON
                    lines = text.split("\n")
                    for i, line_text in enumerate(lines):
                        if line_text.strip():
                            try:
                                parsed = json.loads(line_text)
                                pretty_json = json.dumps(parsed, indent=2)
                                print(pretty_json)
                            except json.JSONDecodeError:
                                print(line_text, end="")
                        
                        if i < len(lines) - 1 or text.endswith("\n"):
                            print()
                    
                    output += text
        
        # Start reading output
        output_task = asyncio.create_task(read_output())
        
        # Wait for Claude to finish with timeout
        timeout_minutes = int(os.environ.get("INPUT_TIMEOUT_MINUTES", "10"))
        timeout_seconds = timeout_minutes * 60
        
        try:
            exit_code = await asyncio.wait_for(claude_process.wait(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            print(f"Claude process timed out after {timeout_seconds} seconds")
            claude_process.terminate()
            await asyncio.sleep(5)  # Give it time to terminate gracefully
            try:
                claude_process.kill()
            except ProcessLookupError:
                pass
            exit_code = 124  # Standard timeout exit code
        
        # Capture stderr for debugging
        if claude_process.stderr:
            stderr_output = await claude_process.stderr.read()
            if stderr_output:
                stderr_text = stderr_output.decode()
                print(f"Claude stderr: {stderr_text}")
                if exit_code != 0:
                    print(f"::error::Claude failed with exit code {exit_code}: {stderr_text}")
        
        # Wait for output reading to complete
        try:
            await asyncio.wait_for(output_task, timeout=5)
        except asyncio.TimeoutError:
            pass
        
        # Set conclusion based on exit code
        if exit_code == 0:
            try:
                # Process output and save execution metrics
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                    temp_file.write(output)
                    temp_file_path = temp_file.name
                
                # Use jq to process output into JSON array
                result = subprocess.run(
                    ["jq", "-s", ".", temp_file_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                async with aiofiles.open(execution_file, 'w') as f:
                    await f.write(result.stdout)
                
                print(f"Log saved to {execution_file}")
                os.unlink(temp_file_path)
                
            except Exception as e:
                print(f"::warning::Failed to process output for execution metrics: {e}")
            
            # Set GitHub Actions outputs
            if github_output := os.environ.get("GITHUB_OUTPUT"):
                with open(github_output, "a") as f:
                    f.write(f"conclusion=success\n")
                    f.write(f"execution_file={execution_file}\n")
            else:
                print(f"::set-output name=conclusion::success")
                print(f"::set-output name=execution_file::{execution_file}")
        else:
            # Set GitHub Actions outputs for failure
            if github_output := os.environ.get("GITHUB_OUTPUT"):
                with open(github_output, "a") as f:
                    f.write(f"conclusion=failure\n")
            else:
                print(f"::set-output name=conclusion::failure")
            
            # Still try to save execution file if we have output
            if output:
                try:
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                        temp_file.write(output)
                        temp_file_path = temp_file.name
                    
                    result = subprocess.run(
                        ["jq", "-s", ".", temp_file_path],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    async with aiofiles.open(execution_file, 'w') as f:
                        await f.write(result.stdout)
                    
                    # Set execution file output
                    if github_output := os.environ.get("GITHUB_OUTPUT"):
                        with open(github_output, "a") as f:
                            f.write(f"execution_file={execution_file}\n")
                    else:
                        print(f"::set-output name=execution_file::{execution_file}")
                    os.unlink(temp_file_path)
                    
                except Exception:
                    pass  # Ignore errors when processing output during failure
            
            sys.exit(exit_code)
            
    except Exception as e:
        print(f"::error::Failed to run Claude: {e}")
        # Set GitHub Actions outputs for failure
        if github_output := os.environ.get("GITHUB_OUTPUT"):
            with open(github_output, "a") as f:
                f.write(f"conclusion=failure\n")
        else:
            print(f"::set-output name=conclusion::failure")
        sys.exit(1)