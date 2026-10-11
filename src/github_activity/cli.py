"""Command-line entry point for the GitHub activity application."""
from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from github_activity import formatter, github_api

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_USAGE = 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github-activity",
        description="Show a GitHub user's recent public activity.",
    )
    parser.add_argument("username", help="GitHub username to look up")
    return parser


def _error_message(error: github_api.GitHubAPIError, username: str) -> str:
    """Return the user-facing message for an expected API failure.

    The CLI words the messages that need CLI context (the username) or that
    must not expose internal details. Other API errors already carry a concise
    user-facing message, so it is reused instead of duplicated here.
    """
    if isinstance(error, github_api.UserNotFoundError):
        return f"GitHub user '{username}' was not found."
    if isinstance(error, github_api.InvalidResponseError):
        return "The response from GitHub could not be processed."
    return str(error)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line application and return the process exit code."""
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
        username = args.username.strip()
        if not username:
            parser.error("username must not be blank")
    except SystemExit as exit_request:
        # argparse reports usage problems (and --help) by exiting. Return the
        # code instead so main() always returns an exit status.
        code = exit_request.code
        return code if isinstance(code, int) else EXIT_USAGE

    try:
        events = github_api.fetch_user_events(username)
    except github_api.GitHubAPIError as error:
        print(f"Error: {_error_message(error, username)}", file=sys.stderr)
        return EXIT_FAILURE

    if not events:
        print(f"No recent public activity found for {username}.")
        return EXIT_SUCCESS

    messages = formatter.format_events(events)
    if not messages:
        print(f"No supported recent activity to display for {username}.")
        return EXIT_SUCCESS

    print(f"GitHub activity for {username}:")
    print()
    for message in messages:
        print(f"- {message}")
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
