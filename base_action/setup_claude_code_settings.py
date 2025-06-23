import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any


def get_claude_config_home_dir() -> str:
    """
    Get Claude's config directory using XDG path when available.
    Priority order:
    1. XDG_CONFIG_HOME/claude (XDG Base Directory spec)
    2. ~/.claude (legacy fallback)
    """
    if xdg_config_home := os.environ.get("XDG_CONFIG_HOME"):
        return os.path.join(xdg_config_home, "claude")
    
    return os.path.join(os.path.expanduser("~"), ".claude")


async def setup_claude_code_settings() -> None:
    """Set up Claude Code settings configuration."""
    config_dir = Path(get_claude_config_home_dir())
    settings_path = config_dir / "settings.json"
    
    print(f"Setting up Claude settings at: {settings_path}")
    
    # Ensure config directory exists
    print("Creating config directory...")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    settings: Dict[str, Any] = {}
    
    try:
        if settings_path.exists() and settings_path.stat().st_size > 0:
            with open(settings_path, 'r') as f:
                existing_content = f.read().strip()
                if existing_content:
                    settings = json.loads(existing_content)
                    print(f"Found existing settings:\n{json.dumps(settings, indent=2)}")
                else:
                    print("Settings file exists but is empty")
        else:
            print("No existing settings file found, creating new one")
    except (FileNotFoundError, json.JSONDecodeError):
        print("No existing settings file found, creating new one")
    
    settings["enableAllProjectMcpServers"] = True
    print("Updated settings with enableAllProjectMcpServers: true")
    
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    
    print("Settings saved successfully")