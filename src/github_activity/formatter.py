"""Format supported GitHub events as concise, human-readable messages.

This module is deliberately pure: it does not perform network requests or
write to the terminal.
"""
from __future__ import annotations

from typing import Any


def _repository_name(event: dict[str, Any]) -> str | None:
    """Return a non-empty repository name when the event provides one."""
    repository = event.get("repo")
    if not isinstance(repository, dict):
        return None

    name = repository.get("name")
    if not isinstance(name, str):
        return None

    name = name.strip()
    return name or None


def _payload(event: dict[str, Any]) -> dict[str, Any]:
    """Return the event payload, treating malformed payloads as unavailable."""
    payload = event.get("payload")
    return payload if isinstance(payload, dict) else {}


def _positive_issue_number(payload: dict[str, Any], key: str) -> int | None:
    """Return a valid positive issue/PR number, excluding booleans."""
    item = payload.get(key)
    if not isinstance(item, dict):
        return None

    number = item.get("number")
    if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
        return None
    return number


def _format_push_event(event: dict[str, Any], repository: str) -> str | None:
    payload = _payload(event)
    size = payload.get("size")

    if isinstance(size, int) and not isinstance(size, bool) and size >= 0:
        count = size
    else:
        commits = payload.get("commits")
        # GitHub can truncate the commits array at 20 entries. Do not claim
        # that its length is the total when it reaches that limit.
        if not isinstance(commits, list) or len(commits) >= 20:
            return None
        count = len(commits)

    noun = "commit" if count == 1 else "commits"
    return f"Pushed {count} {noun} to {repository}"


def _format_issues_event(event: dict[str, Any], repository: str) -> str:
    payload = _payload(event)
    action = payload.get("action")
    number = _positive_issue_number(payload, "issue")
    suffix = f" issue #{number}" if number is not None else " an issue"

    actions = {
        "opened": "Opened",
        "closed": "Closed",
        "reopened": "Reopened",
    }
    if isinstance(action, str) and action in actions:
        return f"{actions[action]}{suffix} in {repository}"

    if number is not None:
        return f"Issue activity on issue #{number} in {repository}"
    return f"Issue activity in {repository}"


def _format_issue_comment_event(event: dict[str, Any], repository: str) -> str:
    payload = _payload(event)
    number = _positive_issue_number(payload, "issue")
    target = f"issue #{number}" if number is not None else "an issue"
    action = payload.get("action")

    if action == "created":
        return f"Commented on {target} in {repository}"
    return (
        f"Issue comment activity on {target} in {repository}"
        if number is not None
        else f"Issue comment activity in {repository}"
    )


def _format_pull_request_event(event: dict[str, Any], repository: str) -> str:
    payload = _payload(event)
    action = payload.get("action")
    number = _positive_issue_number(payload, "pull_request")
    suffix = f" pull request #{number}" if number is not None else " a pull request"

    if action == "closed":
        pull_request = payload.get("pull_request")
        if isinstance(pull_request, dict) and pull_request.get("merged") is True:
            return f"Merged{suffix} in {repository}"
        return f"Closed{suffix} in {repository}"

    actions = {
        "opened": "Opened",
        "reopened": "Reopened",
        "ready_for_review": "Marked{suffix} ready for review",
        "converted_to_draft": "Converted{suffix} to draft",
    }
    if isinstance(action, str) and action in actions:
        if action == "ready_for_review":
            return f"Marked{suffix} ready for review in {repository}"
        if action == "converted_to_draft":
            return f"Converted{suffix} to draft in {repository}"
        return f"{actions[action]}{suffix} in {repository}"

    if number is not None:
        return f"Pull request activity on #{number} in {repository}"
    return f"Pull request activity in {repository}"


def _format_watch_event(event: dict[str, Any], repository: str) -> str:
    return f"Starred {repository}"


def _format_fork_event(event: dict[str, Any], repository: str) -> str:
    return f"Forked {repository}"


def _format_create_event(event: dict[str, Any], repository: str) -> str | None:
    payload = _payload(event)
    ref_type = payload.get("ref_type")

    if ref_type == "repository":
        return f"Created repository {repository}"

    if ref_type in {"branch", "tag"}:
        ref = payload.get("ref")
        if not isinstance(ref, str) or not ref.strip():
            return None
        return f"Created {ref_type} {ref.strip()} in {repository}"

    return None


def _format_delete_event(event: dict[str, Any], repository: str) -> str | None:
    payload = _payload(event)
    ref_type = payload.get("ref_type")
    ref = payload.get("ref")

    if ref_type not in {"branch", "tag"}:
        return None
    if not isinstance(ref, str) or not ref.strip():
        return None

    return f"Deleted {ref_type} {ref.strip()} in {repository}"


def _format_event(event: Any) -> str | None:
    """Format one event, returning None when it cannot be described safely."""
    if not isinstance(event, dict):
        return None

    event_type = event.get("type")
    if not isinstance(event_type, str):
        return None

    repository = _repository_name(event)
    if repository is None:
        return None

    if event_type == "PushEvent":
        return _format_push_event(event, repository)
    if event_type == "IssuesEvent":
        return _format_issues_event(event, repository)
    if event_type == "IssueCommentEvent":
        return _format_issue_comment_event(event, repository)
    if event_type == "PullRequestEvent":
        return _format_pull_request_event(event, repository)
    if event_type == "WatchEvent":
        return _format_watch_event(event, repository)
    if event_type == "ForkEvent":
        return _format_fork_event(event, repository)
    if event_type == "CreateEvent":
        return _format_create_event(event, repository)
    if event_type == "DeleteEvent":
        return _format_delete_event(event, repository)
    return None


def format_events(events: Any) -> list[str]:
    """Format supported events, skipping entries that cannot be described.

    The caller is responsible for distinguishing an empty API response from
    a non-empty response whose events were all skipped.
    """
    if not isinstance(events, list):
        return []

    messages: list[str] = []
    for event in events:
        message = _format_event(event)
        if message is not None:
            messages.append(message)
    return messages
