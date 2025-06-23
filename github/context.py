"""GitHub context parsing functionality."""

import os
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class EventName(str, Enum):
    """GitHub event names."""
    ISSUES = "issues"
    ISSUE_COMMENT = "issue_comment"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"
    PULL_REQUEST_REVIEW_COMMENT = "pull_request_review_comment"


@dataclass
class Repository:
    """Repository information."""
    owner: str
    repo: str
    full_name: str


@dataclass
class Inputs:
    """Action inputs."""
    trigger_phrase: str
    assignee_trigger: str
    allowed_tools: List[str]
    disallowed_tools: List[str]
    custom_instructions: str
    direct_prompt: str
    base_branch: Optional[str] = None


@dataclass
class ParsedGitHubContext:
    """Parsed GitHub context."""
    run_id: str
    event_name: str
    event_action: Optional[str]
    repository: Repository
    actor: str
    payload: Dict[str, Any]
    entity_number: int
    is_pr: bool
    inputs: Inputs


def parse_multiline_input(s: str) -> List[str]:
    """Parse multiline input string into list."""
    result = []
    for line in s.split('\n'):
        for tool in line.split(','):
            cleaned_tool = tool.split('#')[0].strip()
            if cleaned_tool:
                result.append(cleaned_tool)
    return result


def parse_github_context() -> ParsedGitHubContext:
    """Parse GitHub context from environment variables."""
    # Get GitHub context from environment
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not github_event_path:
        raise Exception("GITHUB_EVENT_PATH not found")
    
    with open(github_event_path, 'r') as f:
        payload = json.load(f)
    
    event_name = os.environ.get("GITHUB_EVENT_NAME")
    if not event_name:
        raise Exception("GITHUB_EVENT_NAME not found")
    
    repository_name = os.environ.get("GITHUB_REPOSITORY")
    if not repository_name:
        raise Exception("GITHUB_REPOSITORY not found")
    
    owner, repo = repository_name.split('/')
    
    common_fields = {
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "event_name": event_name,
        "event_action": payload.get("action"),
        "repository": Repository(
            owner=owner,
            repo=repo,
            full_name=repository_name
        ),
        "actor": os.environ.get("GITHUB_ACTOR", ""),
        "payload": payload,
        "inputs": Inputs(
            trigger_phrase=os.environ.get("TRIGGER_PHRASE", "@claude"),
            assignee_trigger=os.environ.get("ASSIGNEE_TRIGGER", ""),
            allowed_tools=parse_multiline_input(os.environ.get("ALLOWED_TOOLS", "")),
            disallowed_tools=parse_multiline_input(os.environ.get("DISALLOWED_TOOLS", "")),
            custom_instructions=os.environ.get("CUSTOM_INSTRUCTIONS", ""),
            direct_prompt=os.environ.get("DIRECT_PROMPT", ""),
            base_branch=os.environ.get("BASE_BRANCH")
        )
    }

    if event_name == EventName.ISSUES:
        return ParsedGitHubContext(
            **common_fields,
            entity_number=payload["issue"]["number"],
            is_pr=False
        )
    elif event_name == EventName.ISSUE_COMMENT:
        return ParsedGitHubContext(
            **common_fields,
            entity_number=payload["issue"]["number"],
            is_pr=bool(payload["issue"].get("pull_request"))
        )
    elif event_name == EventName.PULL_REQUEST:
        return ParsedGitHubContext(
            **common_fields,
            entity_number=payload["pull_request"]["number"],
            is_pr=True
        )
    elif event_name == EventName.PULL_REQUEST_REVIEW:
        return ParsedGitHubContext(
            **common_fields,
            entity_number=payload["pull_request"]["number"],
            is_pr=True
        )
    elif event_name == EventName.PULL_REQUEST_REVIEW_COMMENT:
        return ParsedGitHubContext(
            **common_fields,
            entity_number=payload["pull_request"]["number"],
            is_pr=True
        )
    else:
        raise Exception(f"Unsupported event type: {event_name}")


def is_issues_event(context: ParsedGitHubContext) -> bool:
    """Check if context is issues event."""
    return context.event_name == EventName.ISSUES


def is_issue_comment_event(context: ParsedGitHubContext) -> bool:
    """Check if context is issue comment event."""
    return context.event_name == EventName.ISSUE_COMMENT


def is_pull_request_event(context: ParsedGitHubContext) -> bool:
    """Check if context is pull request event."""
    return context.event_name == EventName.PULL_REQUEST


def is_pull_request_review_event(context: ParsedGitHubContext) -> bool:
    """Check if context is pull request review event."""
    return context.event_name == EventName.PULL_REQUEST_REVIEW


def is_pull_request_review_comment_event(context: ParsedGitHubContext) -> bool:
    """Check if context is pull request review comment event."""
    return context.event_name == EventName.PULL_REQUEST_REVIEW_COMMENT


def is_issues_assigned_event(context: ParsedGitHubContext) -> bool:
    """Check if context is issues assigned event."""
    return is_issues_event(context) and context.event_action == "assigned"