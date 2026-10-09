"""Deterministic tests for the GitHub REST API client."""

import json
from io import BytesIO
from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock, patch

import pytest

from github_activity import github_api


def make_response(payload, status=200):
    response = MagicMock()
    response.__enter__.return_value = response
    response.status = status
    response.read.return_value = json.dumps(payload).encode("utf-8")
    return response


def make_http_error(status, payload=None, headers=None):
    body = json.dumps(payload or {}).encode("utf-8")
    return HTTPError(
        "https://api.github.com/users/octocat/events",
        status,
        "error",
        headers or {},
        BytesIO(body),
    )


def valid_event():
    return {"type": "PushEvent", "repo": {"name": "octocat/Hello-World"}, "payload": {}}


def test_success_returns_decoded_events_and_builds_expected_request():
    response = make_response([valid_event()])
    with patch("github_activity.github_api.urlopen", return_value=response) as urlopen:
        result = github_api.fetch_user_events("octocat")

    assert result == [valid_event()]
    request = urlopen.call_args.args[0]
    assert request.full_url == "https://api.github.com/users/octocat/events"
    assert request.get_method() == "GET"
    assert request.get_header("Accept") == "application/vnd.github+json"
    assert request.get_header("X-github-api-version") == "2022-11-28"
    assert request.get_header("User-agent") == "github-user-activity"
    assert urlopen.call_args.kwargs["timeout"] == 10


def test_empty_list_is_valid():
    with patch("github_activity.github_api.urlopen", return_value=make_response([])):
        assert github_api.fetch_user_events("octocat") == []


def test_username_is_url_encoded():
    with patch("github_activity.github_api.urlopen", return_value=make_response([])) as urlopen:
        github_api.fetch_user_events("octa cot")
    assert urlopen.call_args.args[0].full_url.endswith("/users/octa%20cot/events")


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (make_http_error(404, {"message": "Not Found"}), github_api.UserNotFoundError),
        (make_http_error(403, {"message": "API rate limit exceeded"}), github_api.RateLimitError),
        (make_http_error(403, {"message": "Resource forbidden"}), github_api.ForbiddenError),
        (make_http_error(500, {"message": "Server Error"}), github_api.GitHubHTTPError),
        (make_http_error(429, {"message": "Too Many Requests"}), github_api.RateLimitError),
    ],
)
def test_http_errors_are_classified(error, expected):
    with patch("github_activity.github_api.urlopen", side_effect=error):
        with pytest.raises(expected):
            github_api.fetch_user_events("octocat")


def test_403_with_rate_limit_header_is_rate_limit():
    error = make_http_error(403, {"message": "Forbidden"}, {"X-RateLimit-Remaining": "0"})
    with patch("github_activity.github_api.urlopen", side_effect=error):
        with pytest.raises(github_api.RateLimitError):
            github_api.fetch_user_events("octocat")


@pytest.mark.parametrize("failure", [URLError("offline"), TimeoutError("timed out"), OSError("socket failure")])
def test_network_failures_are_classified(failure):
    with patch("github_activity.github_api.urlopen", side_effect=failure):
        with pytest.raises(github_api.GitHubNetworkError):
            github_api.fetch_user_events("octocat")


def test_invalid_json_is_rejected():
    response = make_response([])
    response.read.return_value = b"not json"
    with patch("github_activity.github_api.urlopen", return_value=response):
        with pytest.raises(github_api.InvalidResponseError):
            github_api.fetch_user_events("octocat")


@pytest.mark.parametrize("payload", [{"events": []}, ["not an object"], [{"repo": {"name": "x/y"}}], [{"type": "PushEvent", "repo": {}}]])
def test_unexpected_response_structures_are_rejected(payload):
    with patch("github_activity.github_api.urlopen", return_value=make_response(payload)):
        with pytest.raises(github_api.InvalidResponseError):
            github_api.fetch_user_events("octocat")


def test_empty_username_is_rejected_without_request():
    with patch("github_activity.github_api.urlopen") as urlopen:
        with pytest.raises(ValueError):
            github_api.fetch_user_events(" ")
    urlopen.assert_not_called()
