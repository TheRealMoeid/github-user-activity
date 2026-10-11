"""Deterministic tests for the command-line interface."""

import pytest

from github_activity import cli, github_api


@pytest.fixture
def fetch(monkeypatch):
    """Replace the API call with a recorder so no request is ever made."""

    class Fetch:
        def __init__(self):
            self.calls = []
            self.result = []
            self.error = None

        def __call__(self, username):
            self.calls.append(username)
            if self.error is not None:
                raise self.error
            return self.result

    fake = Fetch()
    monkeypatch.setattr(cli.github_api, "fetch_user_events", fake)
    return fake


def event(event_type, payload=None, repository="octocat/Hello-World"):
    return {
        "type": event_type,
        "repo": {"name": repository},
        "payload": {} if payload is None else payload,
    }


@pytest.mark.parametrize("argv", [[], ["octocat", "extra"], [" "], [""]])
def test_invalid_arguments_exit_2_without_api_request(fetch, capsys, argv):
    assert cli.main(argv) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "usage: github-activity" in captured.err
    assert fetch.calls == []


def test_help_exits_successfully_without_api_request(fetch, capsys):
    assert cli.main(["--help"]) == 0

    assert "usage: github-activity" in capsys.readouterr().out
    assert fetch.calls == []


def test_displays_formatted_activity(fetch, capsys):
    fetch.result = [
        event("PushEvent", {"size": 3}),
        event("PublicEvent"),
        event("WatchEvent", repository="octocat/Spoon-Knife"),
    ]

    assert cli.main(["octocat"]) == 0

    captured = capsys.readouterr()
    assert captured.out == (
        "GitHub activity for octocat:\n"
        "\n"
        "- Pushed 3 commits to octocat/Hello-World\n"
        "- Starred octocat/Spoon-Knife\n"
    )
    assert captured.err == ""
    assert fetch.calls == ["octocat"]


def test_username_is_stripped_before_request_and_display(fetch, capsys):
    fetch.result = [event("WatchEvent")]

    assert cli.main(["  octocat "]) == 0

    assert fetch.calls == ["octocat"]
    assert capsys.readouterr().out.startswith("GitHub activity for octocat:")


def test_empty_api_response_has_its_own_message(fetch, capsys):
    fetch.result = []

    assert cli.main(["octocat"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "No recent public activity found for octocat.\n"
    assert captured.err == ""


def test_events_without_supported_activity_have_their_own_message(fetch, capsys):
    fetch.result = [event("PublicEvent"), event("GollumEvent")]

    assert cli.main(["octocat"]) == 0

    captured = capsys.readouterr()
    assert captured.out == "No supported recent activity to display for octocat.\n"
    assert captured.err == ""


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (
            github_api.UserNotFoundError("GitHub user was not found."),
            "Error: GitHub user 'octocat' was not found.\n",
        ),
        (
            github_api.RateLimitError("GitHub API rate limit exceeded; wait before retrying."),
            "Error: GitHub API rate limit exceeded; wait before retrying.\n",
        ),
        (
            github_api.ForbiddenError("GitHub denied access to the API request."),
            "Error: GitHub denied access to the API request.\n",
        ),
        (
            github_api.GitHubHTTPError("GitHub server returned HTTP 503; try again later."),
            "Error: GitHub server returned HTTP 503; try again later.\n",
        ),
        (
            github_api.GitHubNetworkError("Could not reach GitHub; check your connection and try again."),
            "Error: Could not reach GitHub; check your connection and try again.\n",
        ),
        (
            github_api.InvalidResponseError("Invalid event at position 3."),
            "Error: The response from GitHub could not be processed.\n",
        ),
    ],
)
def test_api_errors_are_reported_on_stderr_with_exit_1(fetch, capsys, error, expected):
    fetch.error = error

    assert cli.main(["octocat"]) == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == expected


def test_unexpected_errors_are_not_hidden(fetch):
    fetch.error = RuntimeError("bug")

    with pytest.raises(RuntimeError):
        cli.main(["octocat"])
