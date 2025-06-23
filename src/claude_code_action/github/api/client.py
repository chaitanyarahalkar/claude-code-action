"""GitHub API client wrapper."""

import aiohttp
from typing import Dict, Any, Optional
from dataclasses import dataclass
from .config import GITHUB_API_URL, GITHUB_GRAPHQL_URL


@dataclass
class RestClient:
    """REST API client."""
    session: aiohttp.ClientSession
    token: str
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET request."""
        url = f"{GITHUB_API_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with self.session.get(url, headers=headers, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """POST request."""
        url = f"{GITHUB_API_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with self.session.post(url, headers=headers, json=json_data, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """PATCH request."""
        url = f"{GITHUB_API_URL}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        async with self.session.patch(url, headers=headers, json=json_data, **kwargs) as response:
            response.raise_for_status()
            return await response.json()


@dataclass
class GraphQLClient:
    """GraphQL API client."""
    session: aiohttp.ClientSession
    token: str
    
    async def query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        async with self.session.post(GITHUB_GRAPHQL_URL, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.json()


@dataclass
class OctokitWrapper:
    """Octokit-like wrapper for GitHub API clients."""
    rest: RestClient
    graphql: GraphQLClient
    session: aiohttp.ClientSession
    
    async def close(self):
        """Close the session."""
        await self.session.close()


def create_octokit(token: str) -> OctokitWrapper:
    """Create Octokit-like client wrapper."""
    session = aiohttp.ClientSession()
    
    return OctokitWrapper(
        rest=RestClient(session=session, token=token),
        graphql=GraphQLClient(session=session, token=token),
        session=session
    )