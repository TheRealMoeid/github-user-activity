# GitHub User Activity CLI

A Python command-line application that retrieves a GitHub user's recent public activity and formats supported events into concise, human-readable messages.

**Repository:** https://github.com/TheRealMoeid/github-user-activity

## Status

**Current stage: Stage 4 — CLI Integration (implemented and verified)**

- **Stage 1 — Project Foundation:** Completed.
- **Stage 2 — GitHub API Client:** Implemented and tested.
- **Stage 3 — Event Formatter:** Implemented and tested.
- **Stage 4 — CLI Integration:** Implemented; all 74 tests in the full suite passed in the user's local environment, and the installed command was checked manually.

All three modules have automated tests that do not use the network. The installed `github-activity` command was run against the live GitHub API for an existing user, a nonexistent user, a missing username, and extra arguments, and the exit codes for success, user not found, and missing username were confirmed. Rate-limit, forbidden, server-error, network-failure, and invalid-response handling is covered by mocked tests only.

## Features

- Retrieves recent public GitHub events through the GitHub REST API.
- Uses Python's standard library for HTTP requests and JSON processing.
- Formats eight supported event types into readable messages.
- Provides a `github-activity <username>` command with plain output, concise error messages, and documented exit codes.
- Handles incomplete event payloads without inventing activity details.
- Skips unsupported or unusable events without stopping the remaining activity from being processed.
- Includes automated tests that do not require a live GitHub connection.

## Requirements

- Python 3.13 or later.
- `pip`.
- A Python virtual environment.
- Git for repository development.

Runtime HTTP and JSON handling use the Python standard library. `pytest` is a development and testing dependency, not a runtime dependency.

## Development setup

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### macOS / Linux

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Usage

After installing the project (see Development setup), run:

```bash
github-activity <username>
```

Example output:

```text
GitHub activity for octocat:

- Pushed 3 commits to octocat/Hello-World
- Opened issue #42 in octocat/Hello-World
- Starred octocat/Spoon-Knife
- Forked octocat/example
```

Actual output depends on the public events returned by GitHub.

## Error behavior and exit codes

Activity and the "no activity" messages are printed to stdout. Usage and error messages are printed to stderr, and expected failures never show a Python traceback.

| Situation | Output | Exit code |
|---|---|---|
| Activity displayed | Header and activity list | 0 |
| Empty API response | `No recent public activity found for <username>.` | 0 |
| Events returned, none supported | `No supported recent activity to display for <username>.` | 0 |
| Missing, extra, or blank argument | Usage message | 2 |
| User not found | `Error: GitHub user '<username>' was not found.` | 1 |
| Rate limit | Error asking you to wait before retrying | 1 |
| Other forbidden response | Error stating that GitHub denied access | 1 |
| GitHub server error | Error suggesting you try again later | 1 |
| Network failure or timeout | Error stating that GitHub could not be reached | 1 |
| Invalid or unexpected API response | Error stating that the response could not be processed | 1 |

## Supported event types

The formatter supports these eight event types:

| Event type | Example activity |
|---|---|
| `PushEvent` | Pushed 3 commits to a repository, or Pushed to a branch when GitHub provides no commit count |
| `IssuesEvent` | Opened issue #42 |
| `IssueCommentEvent` | Commented on issue #42 |
| `PullRequestEvent` | Opened or merged pull request #12 |
| `WatchEvent` | Starred a repository |
| `ForkEvent` | Forked a repository |
| `CreateEvent` | Created a branch, tag, or repository |
| `DeleteEvent` | Deleted a branch or tag |

Unknown actions use generic wording only when the event remains reliably identifiable. Events that cannot be described safely are skipped.

## Run tests

Activate the virtual environment, then run:

```powershell
python -m pytest -v
```

To run only the formatter or CLI tests:

```powershell
python -m pytest tests/test_formatter.py -v
python -m pytest tests/test_cli.py -v
```

**Latest reported verification:** 74 tests passed in 0.56 seconds (Python 3.13.16, pytest 9.1.1, Windows). This result was reported by the user from the local development environment; it is not a claim of an independent rerun against the current remote branch.

Automated tests must not require live GitHub API requests.

## Limitations

Version 1 is intended to show recent public events exposed by GitHub's Events API, not a user's complete GitHub history.

The following features are out of scope:

- GitHub authentication or personal access tokens.
- Pagination or complete activity-history retrieval.
- Caching or persistent storage.
- Asynchronous HTTP requests.
- Third-party HTTP clients such as `requests` or `httpx`.
- GitHub GraphQL API.
- Colored output or terminal UI frameworks.
- Background jobs or configuration files.

## Project documentation

- [REQUIREMENTS.md](REQUIREMENTS.md) — Agreed functional and technical requirements.
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) — Architecture, development status, decisions, and AI handoff instructions.
- [LICENSE](LICENSE) — Project license, if present.
