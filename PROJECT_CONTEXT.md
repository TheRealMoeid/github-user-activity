# Project Context: GitHub User Activity CLI

## Purpose

Build `github-activity <username>`, a Python CLI that retrieves recent public GitHub events and displays supported event types as concise, human-readable messages.

## Agreed decisions

- Python 3.13; `pip` and `venv`.
- Package `github_activity`, using a `src/` layout.
- `pyproject.toml` and `setuptools` packaging.
- Python standard library for runtime HTTP and JSON handling; no third-party runtime dependencies.
- `pytest` as a development dependency.
- Console script `github-activity` mapped to `github_activity.cli:main`.
- API endpoint: `https://api.github.com/users/<username>/events`.
- Supported events: `PushEvent`, `IssuesEvent`, `IssueCommentEvent`, `PullRequestEvent`, `WatchEvent`, `ForkEvent`, `CreateEvent`, and `DeleteEvent`.
- No authentication, persistence, caching, pagination, async requests, third-party HTTP clients, colors, GraphQL, or background jobs in v1.
- Tests must not require live GitHub API access.
- `REQUIREMENTS.md` is the full agreed specification.

## Architecture

- `src/github_activity/cli.py`: argument handling, orchestration, output, exit codes.
- `src/github_activity/github_api.py`: standard-library HTTP, JSON decoding, response validation, API/network errors.
- `src/github_activity/formatter.py`: pure event-to-message formatting; no network calls or terminal output.
- `tests/`: automated tests.

Flow: CLI arguments → CLI orchestration → API client → event data → formatter → terminal output.

## Current implementation status

**Foundation stage only.** This patch establishes package metadata, module placeholders, documentation, ignore rules, and a foundation test. API requests, event formatting, and complete CLI behavior are not implemented.

## Verification status

Tests have not been run in the user's local repository as part of this patch handoff. Do not describe the application as functional until later stages are implemented and verified.

## Known constraints

- The repository was reported as empty when inspected.
- `LICENSE` is intentionally omitted because no license choice has been confirmed for this repository.
- The console-script entry point is declared, but application behavior is not implemented at this stage.

## Next agreed task

After applying and verifying the foundation patch, implement the GitHub API client and isolated API tests. Keep that stage focused on API behavior and error handling; do not combine formatter or full CLI implementation into it.
