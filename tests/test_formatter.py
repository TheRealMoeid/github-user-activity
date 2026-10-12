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
        ({"action": "mystery", "issue": {"number": 5}}, "Activity on issue #5 in octocat/Hello-World"),
        ({}, "Issue activity in octocat/Hello-World"),
    ],
)
def test_issue_actions_and_safe_generic_fallbacks(payload, expected):
    assert format_events([event("IssuesEvent", payload)]) == [expected]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"action": "edited", "issue": {"number": 7}}, "Comment activity on issue #7 in octocat/Hello-World"),
        ({}, "Issue comment activity in octocat/Hello-World"),
    ],
)
def test_comment_event_does_not_claim_new_comment_for_non_created_action(payload, expected):
    assert format_events([event("IssueCommentEvent", payload)]) == [expected]


def test_unknown_pull_request_action_uses_generic_message():
    item = event("PullRequestEvent", {"action": "synchronize", "pull_request": {"number": 12}})
    assert format_events([item]) == ["Activity on pull request #12 in octocat/Hello-World"]


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {"action": "ready_for_review", "pull_request": {"number": 12}},
            "Marked pull request #12 ready for review in octocat/Hello-World",
        ),
        (
            {"action": "ready_for_review"},
            "Marked a pull request ready for review in octocat/Hello-World",
        ),
        (
            {"action": "converted_to_draft", "pull_request": {"number": 12}},
            "Converted pull request #12 to draft in octocat/Hello-World",
        ),
        (
            {"action": "converted_to_draft"},
            "Converted a pull request to draft in octocat/Hello-World",
        ),
        (
            {"action": "reopened", "pull_request": {"number": 12}},
            "Reopened pull request #12 in octocat/Hello-World",
        ),
        ({}, "Pull request activity in octocat/Hello-World"),
    ],
)
def test_pull_request_draft_and_review_actions_and_generic_fallback(payload, expected):
    assert format_events([event("PullRequestEvent", payload)]) == [expected]


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


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        # Current GitHub payloads carry no size or commits, only the ref.
        ({"ref": "refs/heads/main"}, "Pushed to main in octocat/Hello-World"),
        ({"ref": "refs/heads/feature/login"}, "Pushed to feature/login in octocat/Hello-World"),
        ({"ref": "refs/heads/main", "head": "abc", "before": "def"}, "Pushed to main in octocat/Hello-World"),
        # An unreliable or malformed count falls back instead of skipping.
        ({"commits": [{"message": str(i)} for i in range(20)], "ref": "refs/heads/dev"}, "Pushed to dev in octocat/Hello-World"),
        ({"commits": "not a list", "ref": "refs/heads/dev"}, "Pushed to dev in octocat/Hello-World"),
        ({"size": "three", "ref": "refs/heads/dev"}, "Pushed to dev in octocat/Hello-World"),
        ({"size": True, "ref": "refs/heads/dev"}, "Pushed to dev in octocat/Hello-World"),
        ({"size": -1, "ref": "refs/heads/dev"}, "Pushed to dev in octocat/Hello-World"),
        # Unusable refs give the plain repository-level message.
        ({}, "Pushed to octocat/Hello-World"),
        ({"ref": "refs/tags/v1.0"}, "Pushed to octocat/Hello-World"),
        ({"ref": "refs/heads/"}, "Pushed to octocat/Hello-World"),
        ({"ref": "refs/heads/   "}, "Pushed to octocat/Hello-World"),
        ({"ref": 12}, "Pushed to octocat/Hello-World"),
    ],
)
def test_push_event_without_reliable_count_uses_branch_or_generic_fallback(payload, expected):
    assert format_events([event("PushEvent", payload)]) == [expected]


def test_push_event_count_wins_over_ref_when_available():
    item = event("PushEvent", {"size": 2, "ref": "refs/heads/main"})
    assert format_events([item]) == ["Pushed 2 commits to octocat/Hello-World"]


def test_push_event_without_usable_repository_is_still_skipped():
    item = {"type": "PushEvent", "repo": {"name": " "}, "payload": {"ref": "refs/heads/main"}}
    assert format_events([item]) == []


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
        event("CreateEvent", {"ref_type": "branch"}),
        event("WatchEvent"),
    ]
    assert format_events(items) == ["Starred octocat/Hello-World"]


def test_non_list_input_returns_empty_list():
    assert format_events(None) == []
    assert format_events({"type": "WatchEvent"}) == []


def test_boolean_issue_number_is_not_treated_as_integer():
    item = event("IssuesEvent", {"action": "opened", "issue": {"number": True}})
    assert format_events([item]) == ["Opened an issue in octocat/Hello-World"]
