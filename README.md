# GitHub User Activity CLI

A Python command-line application that retrieves a GitHub user's recent public activity and formats supported events into concise, human-readable messages.

**Repository:** https://github.com/TheRealMoeid/github-user-activity

## Status

**Current stage: Stage 3 — Event Formatter**

- **Stage 1 — Project Foundation:** Completed.
- **Stage 2 — GitHub API Client:** Implemented and tested.
- **Stage 3 — Event Formatter:** Implemented; all 58 tests in the full suite passed in the user's local environment.
- **Stage 4 — CLI Integration:** Pending.

The formatter and API client have automated test coverage. The complete CLI workflow, including the installed console command, has not yet been verified end to end.

## Features

- Retrieves recent public GitHub events through the GitHub REST API.
- Uses Python's standard library for HTTP requests and JSON processing.
- Formats eight supported event types into readable messages.
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

## Intended usage

The planned command is:

```bash
github-activity <username>
```

**Note:** CLI integration is not yet complete. The command should not be considered end-to-end verified until Stage 4 is implemented and tested.

Illustrative output:

```text
GitHub activity for octocat:

- Pushed 3 commits to octocat/Hello-World
- Opened issue #42 in octocat/Hello-World
- Starred octocat/Spoon-Knife
- Forked octocat/example
```

Actual output depends on the public events returned by GitHub.

## Supported event types

The formatter supports these eight event types:

| Event type | Example activity |
|---|---|
| `PushEvent` | Pushed 3 commits to a repository |
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

To run only the formatter tests:

```powershell
python -m pytest tests/test_formatter.py -v
```

**Latest reported verification:** 58 tests passed in 0.46 seconds. This result was reported by the user from the local development environment; it is not a claim of an independent rerun against the current remote branch.

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
