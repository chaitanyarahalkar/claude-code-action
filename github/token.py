"""GitHub token management with OIDC support."""

import os
import time
import json
from typing import Optional
import aiohttp
import asyncio


class TokenError(Exception):
    """Token-related errors."""
    pass


async def setup_github_token() -> str:
    """Setup GitHub token using OIDC or provided token."""
    override_token = os.environ.get("OVERRIDE_GITHUB_TOKEN")
    if override_token:
        return override_token
    
    # Try OIDC token exchange
    try:
        return await get_oidc_token()
    except Exception as e:
        raise TokenError(f"Failed to get GitHub token: {e}")


async def get_oidc_token(max_retries: int = 5) -> str:
    """Get OIDC token with retry logic."""
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL")
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN")
    
    if not request_url or not request_token:
        raise TokenError("OIDC token request URL or token not available")
    
    for attempt in range(max_retries):
        try:
            # Request ID token
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {request_token}"}
                params = {"audience": "github"}
                
                async with session.get(request_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        raise TokenError(f"Failed to get ID token: {response.status}")
                    
                    data = await response.json()
                    id_token = data.get("value")
                    
                    if not id_token:
                        raise TokenError("No ID token in response")
                
                # Exchange ID token for installation access token
                github_api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
                token_url = f"{github_api_url}/app/installations/{os.environ.get('GITHUB_INSTALLATION_ID')}/access_tokens"
                
                headers = {
                    "Authorization": f"Bearer {id_token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"
                }
                
                async with session.post(token_url, headers=headers) as response:
                    if response.status == 201:
                        data = await response.json()
                        access_token = data.get("token")
                        if access_token:
                            # Set output for token revocation
                            if github_output := os.environ.get("GITHUB_OUTPUT"):
                                with open(github_output, "a") as f:
                                    f.write(f"GITHUB_TOKEN={access_token}\n")
                            return access_token
                    
                    raise TokenError(f"Failed to get access token: {response.status}")
        
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            # Exponential backoff
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
    
    raise TokenError("Max retries exceeded")