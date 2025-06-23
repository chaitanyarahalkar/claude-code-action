import os
from typing import List


def validate_environment_variables() -> None:
    """
    Validates the environment variables required for running Claude Code
    based on the selected provider (Anthropic API, AWS Bedrock, or Google Vertex AI)
    """
    use_bedrock = os.environ.get("CLAUDE_CODE_USE_BEDROCK") == "1"
    use_vertex = os.environ.get("CLAUDE_CODE_USE_VERTEX") == "1"
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    errors: List[str] = []
    
    if use_bedrock and use_vertex:
        errors.append(
            "Cannot use both Bedrock and Vertex AI simultaneously. Please set only one provider."
        )
    
    if not use_bedrock and not use_vertex:
        if not anthropic_api_key:
            errors.append(
                "ANTHROPIC_API_KEY is required when using direct Anthropic API."
            )
    elif use_bedrock:
        required_bedrock_vars = {
            "AWS_REGION": os.environ.get("AWS_REGION"),
            "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        }
        
        for key, value in required_bedrock_vars.items():
            if not value:
                errors.append(f"{key} is required when using AWS Bedrock.")
    
    elif use_vertex:
        required_vertex_vars = {
            "ANTHROPIC_VERTEX_PROJECT_ID": os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID"),
            "CLOUD_ML_REGION": os.environ.get("CLOUD_ML_REGION"),
        }
        
        for key, value in required_vertex_vars.items():
            if not value:
                errors.append(f"{key} is required when using Google Vertex AI.")
    
    if errors:
        error_message = "Environment variable validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise RuntimeError(error_message)