"""GitHub data formatting functionality."""

from typing import Dict, Any, List, Optional


def format_context(context_data: Dict[str, Any], is_pr: bool) -> str:
    """Format context data."""
    # Placeholder implementation
    return "Formatted context data"


def format_comments(comments: List[Dict[str, Any]], image_url_map: Optional[Dict[str, str]]) -> str:
    """Format comments data."""
    # Placeholder implementation
    return "Formatted comments"


def format_review_comments(review_data: List[Dict[str, Any]], image_url_map: Optional[Dict[str, str]]) -> str:
    """Format review comments data."""
    # Placeholder implementation
    return "Formatted review comments"


def format_changed_files_with_sha(changed_files: List[Dict[str, Any]]) -> str:
    """Format changed files data."""
    # Placeholder implementation
    return "Formatted changed files"


def format_body(body: str, image_url_map: Optional[Dict[str, str]]) -> str:
    """Format body content."""
    # Placeholder implementation
    return body