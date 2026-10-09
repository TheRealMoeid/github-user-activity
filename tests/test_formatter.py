"""Tests for deterministic formatting of GitHub activity events."""

import pytest

from github_activity.formatter import format_events


def event(event_type, payload=None, repository="octocat/Hello-World"):
    return {
        "type": event_type,
        "repo": {"name": repository},
        "payload": {} if payload is None else payload,
    }


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        (
            event("PushEvent", {"size": 1}),
            "Pushed 1 commit to octocat/Hello-World",
        ),
        (
            event("PushEvent", {"size": 3}),
            "Pushed 3 commits to octocat/Hello-World",
        ),
        (
            event("IssuesEvent", {"action": "opened", "issue": {"number": 42}}),
            "Opened issue #42 in octocat/Hello-World",
        ),
        (
            event("IssuesEvent", {"action": "closed"}),
            "Closed an issue in octocat/Hello-World",
        ),
        (
            event("IssueCommentEvent", {"action": "created", "issue": {"number": 42}}),
            "Commented on issue #42 in octocat/Hello-World",
        ),
        (
            event("PullRequestEvent", {"action": "opened", "pull_request": {"number": 12}}),
            "Opened pull request #12 in octocat/Hello-World",
        ),
        (
            event("PullRequestEvent", {"action": "closed", "pull_request": {"number": 12, "merged": True}}),
            "Merged pull request #12 in octocat/Hello-World",
        ),
        (
            event("WatchEvent"),
            "Starred octocat/Hello-World",
        ),
        (
            event("ForkEvent"),
            "Forked octocat/Hello-World",
        ),
        (
            event("CreateEvent", {"ref_type": "branch", "ref": "feature/login"}),
            "Created branch feature/login in octocat/Hello-World",
        ),
        (
            event("CreateEvent", {"ref_type": "tag", "ref": "v1.0"}),
            "Created tag v1.0 in octocat/Hello-World",
        ),
        (
            event("CreateEvent", {"ref_type": "repository"}, "octocat/new-project"),
            "Created repository octocat/new-project",
        ),
        (
            event("DeleteEvent", {"ref_type": "tag", "ref": "v1.0"}),
            "Deleted tag v1.0 in octocat/Hello-World",
        ),
    ],
)
def test_formats_supported_events(item, expected):
    assert format_events([item]) == [expected]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"action": "reopened", "issue": {"number": 5}}, "Reopened issue #5 in octocat/Hello-World"),
        ({"action": "mystery", "issue": {"number": 5}}, "Issue activity on issue #5 in octocat/Hello-World"),
        ({}, "Issue activity in octocat/Hello-World"),
    ],
)
def test_issue_actions_and_safe_generic_fallbacks(payload, expected):
    assert format_events([event("IssuesEvent", payload)]) == [expected]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"action": "edited", "issue": {"number": 7}}, "Issue comment activity on issue #7 in octocat/Hello-World"),
        ({}, "Issue comment activity in octocat/Hello-World"),
    ],
)
def test_comment_event_does_not_claim_new_comment_for_non_created_action(payload, expected):
    assert format_events([event("IssueCommentEvent", payload)]) == [expected]


def test_unknown_pull_request_action_uses_generic_message():
    item = event("PullRequestEvent", {"action": "synchronize", "pull_request": {"number": 12}})
    assert format_events([item]) == ["Pull request activity on #12 in octocat/Hello-World"]


def test_closed_pull_request_is_not_called_merged_without_merged_flag():
    item = event("PullRequestEvent", {"action": "closed", "pull_request": {"number": 12}})
    assert format_events([item]) == ["Closed pull request #12 in octocat/Hello-World"]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"size": 0}, "Pushed 0 commits to octocat/Hello-World"),
        ({"commits": [{"message": "one"}]}, "Pushed 1 commit to octocat/Hello-World"),
        ({"commits": [{"message": str(i)} for i in range(19)]}, "Pushed 19 commits to octocat/Hello-World"),
    ],
)
def test_push_event_uses_size_or_complete_short_commit_list(payload, expected):
    assert format_events([event("PushEvent", payload)]) == [expected]


def test_push_event_skips_when_commit_count_is_not_reliable():
    assert format_events([event("PushEvent", {"commits": [{"message": str(i)} for i in range(20)]})]) == []
    assert format_events([event("PushEvent", {"commits": "not a list"})]) == []


@pytest.mark.parametrize(
    "item",
    [
        None,
        "not an event",
        {},
        {"type": "WatchEvent", "repo": {"name": "   "}},
        {"type": "WatchEvent", "repo": {"name": 12}},
        {"type": "WatchEvent", "repo": None},
        event("CreateEvent", {"ref_type": "branch"}),
        event("DeleteEvent", {"ref_type": "repository", "ref": "repo"}),
        event("CreateEvent", {"ref_type": "unknown", "ref": "x"}),
    ],
)
def test_malformed_or_unusable_events_are_skipped(item):
    assert format_events([item]) == []


def test_unsupported_events_are_skipped_without_affecting_supported_events():
    items = [
        event("PublicEvent"),
        event("WatchEvent"),
        event("GollumEvent"),
        event("ForkEvent"),
    ]
    assert format_events(items) == [
        "Starred octocat/Hello-World",
        "Forked octocat/Hello-World",
    ]


def test_malformed_event_does_not_stop_later_events_from_being_formatted():
    items = [
        None,
        event("PushEvent", {"size": "three"}),
        event("WatchEvent"),
    ]
    assert format_events(items) == ["Starred octocat/Hello-World"]


def test_non_list_input_returns_empty_list():
    assert format_events(None) == []
    assert format_events({"type": "WatchEvent"}) == []


def test_boolean_issue_number_is_not_treated_as_integer():
    item = event("IssuesEvent", {"action": "opened", "issue": {"number": True}})
    assert format_events([item]) == ["Opened an issue in octocat/Hello-World"]
