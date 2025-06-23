"""Trigger validation logic."""

import re
from typing import Optional
from ..context import (
    ParsedGitHubContext, 
    is_issues_event, 
    is_issue_comment_event,
    is_pull_request_review_event,
    is_pull_request_review_comment_event,
    is_issues_assigned_event
)


async def check_trigger_action(context: ParsedGitHubContext) -> bool:
    """Check if the action should be triggered based on context."""
    
    # Handle direct prompt case
    if context.inputs.direct_prompt:
        return True
    
    # Handle issue assignment trigger
    if is_issues_assigned_event(context) and context.inputs.assignee_trigger:
        assignees = context.payload.get("issue", {}).get("assignees", [])
        for assignee in assignees:
            if assignee.get("login") == context.inputs.assignee_trigger.lstrip("@"):
                return True
        return False
    
    # Handle issue creation with trigger phrase in body
    if is_issues_event(context) and context.event_action == "opened":
        issue_body = context.payload.get("issue", {}).get("body", "")
        if issue_body and context.inputs.trigger_phrase in issue_body:
            return True
        return False
    
    # Handle comment-based triggers
    trigger_phrase = context.inputs.trigger_phrase
    
    if is_issue_comment_event(context):
        comment_body = context.payload.get("comment", {}).get("body", "")
        return trigger_phrase in comment_body
    
    elif is_pull_request_review_event(context):
        review_body = context.payload.get("review", {}).get("body", "")
        return review_body and trigger_phrase in review_body
    
    elif is_pull_request_review_comment_event(context):
        comment_body = context.payload.get("comment", {}).get("body", "")
        return trigger_phrase in comment_body
    
    return False


def extract_trigger_content(context: ParsedGitHubContext) -> Optional[str]:
    """Extract the content that contains the trigger phrase."""
    trigger_phrase = context.inputs.trigger_phrase
    
    if is_issue_comment_event(context):
        return context.payload.get("comment", {}).get("body", "")
    
    elif is_pull_request_review_event(context):
        return context.payload.get("review", {}).get("body", "")
    
    elif is_pull_request_review_comment_event(context):
        return context.payload.get("comment", {}).get("body", "")
    
    elif is_issues_event(context):
        return context.payload.get("issue", {}).get("body", "")
    
    return None