"""Types for prompt creation."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union


@dataclass 
class CommonFields:
    """Common fields for prompt context."""
    repository: str
    claude_comment_id: str
    trigger_phrase: str
    trigger_username: Optional[str] = None
    custom_instructions: Optional[str] = None
    allowed_tools: Optional[str] = None
    disallowed_tools: Optional[str] = None
    direct_prompt: Optional[str] = None
    claude_branch: Optional[str] = None


@dataclass
class IssueCommentEventData:
    """Issue comment event data."""
    event_name: str = "issue_comment"
    comment_id: str = ""
    is_pr: bool = False
    pr_number: Optional[str] = None
    issue_number: Optional[str] = None
    comment_body: str = ""
    claude_branch: Optional[str] = None
    base_branch: Optional[str] = None


@dataclass
class PullRequestReviewEventData:
    """Pull request review event data."""
    event_name: str = "pull_request_review"
    is_pr: bool = True
    pr_number: str = ""
    comment_body: str = ""
    claude_branch: Optional[str] = None
    base_branch: Optional[str] = None


@dataclass
class PullRequestReviewCommentEventData:
    """Pull request review comment event data."""
    event_name: str = "pull_request_review_comment"
    is_pr: bool = True
    pr_number: str = ""
    comment_id: Optional[str] = None
    comment_body: str = ""
    claude_branch: Optional[str] = None
    base_branch: Optional[str] = None


@dataclass
class IssuesEventData:
    """Issues event data."""
    event_name: str = "issues"
    event_action: str = ""
    is_pr: bool = False
    issue_number: str = ""
    base_branch: str = ""
    claude_branch: str = ""
    assignee_trigger: Optional[str] = None


@dataclass
class PullRequestEventData:
    """Pull request event data."""
    event_name: str = "pull_request"
    event_action: Optional[str] = None
    is_pr: bool = True
    pr_number: str = ""
    claude_branch: Optional[str] = None
    base_branch: Optional[str] = None


EventData = Union[
    IssueCommentEventData,
    PullRequestReviewEventData, 
    PullRequestReviewCommentEventData,
    IssuesEventData,
    PullRequestEventData
]


@dataclass
class PreparedContext:
    """Prepared context for prompt generation."""
    repository: str
    claude_comment_id: str
    trigger_phrase: str
    trigger_username: Optional[str] = None
    custom_instructions: Optional[str] = None
    allowed_tools: Optional[str] = None
    disallowed_tools: Optional[str] = None
    direct_prompt: Optional[str] = None
    claude_branch: Optional[str] = None
    event_data: Optional[EventData] = None