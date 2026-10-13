"""Fetch and validate recent public GitHub events using the standard library."""
from __future__ import annotations

import json
from http.client import HTTPException, IncompleteRead
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

API_BASE_URL = "https://api.github.com"
REQUEST_TIMEOUT = 10


class GitHubAPIError(Exception):
    """Base class for expected API client failures."""


class UserNotFoundError(GitHubAPIError):
    """Requested GitHub user does not exist."""


class RateLimitError(GitHubAPIError):
    """GitHub API rate limit has been reached."""


class ForbiddenError(GitHubAPIError):
    """GitHub forbids the request for a non-rate-limit reason."""


class GitHubHTTPError(GitHubAPIError):
    """Other unsuccessful HTTP response."""


class GitHubNetworkError(GitHubAPIError):
    """Network failure or timeout while contacting GitHub."""


class InvalidResponseError(GitHubAPIError):
    """Invalid JSON or unexpected API response structure."""


def _error_message(error: HTTPError) -> str:
    try:
        payload = json.loads(error.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, OSError):
        return ""
    return payload.get("message", "") if isinstance(payload, dict) and isinstance(payload.get("message"), str) else ""


def _is_rate_limited(headers: Any, message: str) -> bool:
    remaining = headers.get("X-RateLimit-Remaining") if headers else None
    return remaining == "0" or "rate limit exceeded" in message.lower() or "secondary rate limit" in message.lower()


def fetch_user_events(username: str) -> list[dict[str, Any]]:
    """Return validated recent public events for ``username``.

    Raises a specific ``GitHubAPIError`` subclass for expected failures.
    """
    if not isinstance(username, str) or not username.strip():
        raise ValueError("username must be a non-empty string")

    url = f"{API_BASE_URL}/users/{quote(username.strip(), safe='')}/events"
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "github-user-activity",
    }, method="GET")

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            try:
                payload = json.loads(response.read().decode("utf-8"))
            except IncompleteRead as exc:
                raise InvalidResponseError("GitHub returned an incomplete response.") from exc
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InvalidResponseError("GitHub returned invalid JSON.") from exc
    except HTTPError as exc:
        message = _error_message(exc)
        if exc.code == 404:
            raise UserNotFoundError("GitHub user was not found.") from exc
        if exc.code == 429:
            raise RateLimitError("GitHub API rate limit exceeded; wait before retrying.") from exc
        if exc.code == 403:
            if _is_rate_limited(exc.headers, message):
                raise RateLimitError("GitHub API rate limit exceeded; wait before retrying.") from exc
            raise ForbiddenError("GitHub denied access to the API request.") from exc
        if 500 <= exc.code <= 599:
            raise GitHubHTTPError(f"GitHub server returned HTTP {exc.code}; try again later.") from exc
        raise GitHubHTTPError(f"GitHub API returned HTTP {exc.code}.") from exc
    except (URLError, TimeoutError, OSError, HTTPException) as exc:
        raise GitHubNetworkError("Could not reach GitHub; check your connection and try again.") from exc

    if not isinstance(payload, list):
        raise InvalidResponseError("GitHub returned an unexpected response structure.")
    for index, event in enumerate(payload):
        if not isinstance(event, dict):
            raise InvalidResponseError(f"Invalid event at position {index}.")
        if not isinstance(event.get("type"), str) or not isinstance(event.get("repo"), dict):
            raise InvalidResponseError(f"Event at position {index} is missing required fields.")
        if not isinstance(event["repo"].get("name"), str):
            raise InvalidResponseError(f"Event at position {index} has an invalid repository.")
    return payload
