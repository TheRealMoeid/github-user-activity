# Project Context: GitHub User Activity CLI

## 1. Project Overview

**Repository:** https://github.com/TheRealMoeid/github-user-activity

**Project:** A command-line application that retrieves and summarizes a GitHub user's recent public activity.

**Language:** Python 3.13

**Package name:** `github_activity`

**CLI command:** `github-activity <username>`

**Package and dependency management:** `pip`, virtual environment (`.venv`), and `pyproject.toml` using setuptools.

**Current branch:** `phase-2/api-client`

**Latest confirmed local commit:** `08c2cd2` — `Implemented GitHub events API client`

The latest commit is confirmed locally. Do not assume that it has been pushed to the remote repository.

**Requirements source of truth:** `REQUIREMENTS.md`

Always consult `REQUIREMENTS.md` before proposing implementation changes. If another document conflicts with it, identify the conflict rather than silently changing the agreed requirements.

---

## 2. Development Status

The project is being developed in separate, reviewable stages.

### Stage 1: Project Foundation — Completed

Branch: `phase-1/project-foundation`

The user reported successfully pushing this branch to the remote repository.

The foundation includes the initial Python project structure, package configuration, and basic tests.

**Verification reported by the user:**
- 3 tests passed.

### Stage 2: GitHub API Client — Implemented and Committed Locally

Branch: `phase-2/api-client`

Latest confirmed commit: `08c2cd2`

Files included in that commit:

- `src/github_activity/github_api.py`
- `tests/test_github_api.py`

The API client retrieves recent public GitHub events and handles HTTP, network, timeout, and response-validation errors.

**Verification results reported before the commit:**
- `python -m pytest tests/test_github_api.py -v`: 18 passed.
- `python -m pytest -v`: 21 passed.
- `git diff --check`: clean.

These results establish that the reported tests passed at that point. They do not establish that every acceptance criterion or the complete installed CLI has been verified.

### Stage 3: Event Formatter — Next

The formatter has **not yet been implemented**.

The next task is to agree on the detailed formatting behavior for all eight supported event types, including missing fields, singular/plural wording, and events that cannot be displayed safely.

**Do not write formatter code yet.** First review the requirements, propose concrete formatting rules, explain important trade-offs, recommend an approach, and wait for the user's approval.

### Stage 4: CLI Integration — Later

The CLI has not yet been completed and integrated with the API client and formatter.

Do not start this stage until the formatter has been implemented, tested, and reviewed.

---

## 3. Agreed Technical Requirements

The application must:

- Retrieve events from `GET https://api.github.com/users/<username>/events`.
- Use Python's standard-library `urllib` for HTTP requests.
- Avoid third-party HTTP clients such as `requests` and `httpx`.
- Use a request timeout of 10 seconds.
- Send the following headers:
  - `Accept: application/vnd.github+json`
  - `X-GitHub-Api-Version: 2022-11-28`
  - `User-Agent: github-user-activity`
- Avoid retries, pagination, authentication tokens, databases, persistence, caching, asynchronous processing, and GraphQL.
- Keep API communication, event formatting, and CLI responsibilities separate.
- Use deterministic tests with mocked HTTP responses.
- Never require live GitHub API requests for automated tests.
- Avoid colored output, terminal UI frameworks, and unnecessary dependencies.
- Handle missing optional event fields safely.
- Never invent event actions or print raw API JSON as a substitute for formatted output.
- Skip unsupported events and events that cannot be formatted reliably.
- Keep the implementation focused on the agreed requirements; do not introduce additional features without approval.

---

## 4. Supported GitHub Event Types

The application supports these eight event types:

1. `PushEvent`
2. `IssuesEvent`
3. `IssueCommentEvent`
4. `PullRequestEvent`
5. `WatchEvent`
6. `ForkEvent`
7. `CreateEvent`
8. `DeleteEvent`

Other GitHub event types must not produce invented or misleading activity descriptions.

The detailed wording and field requirements for each supported type remain to be agreed during Stage 3.

---

## 5. CLI Contract

The eventual CLI should accept a GitHub username:

`github-activity <username>`

The agreed exit codes are:

| Outcome | Exit code |
|---|---:|
| Successful execution, including no activity or no supported events | `0` |
| API, network, or runtime failure | `1` |
| Invalid, missing, or extra CLI arguments | `2` |

The agreed no-activity messages are:

- Empty API response: `No recent public activity found for <username>.`
- Events exist, but none can be displayed as supported activity: `No supported recent activity to display for <username>.`

Keep these outcomes distinct. Do not treat an empty API response as an API failure.

The CLI should eventually be responsible for argument handling, calling the API client and formatter, displaying results and appropriate errors, and returning the correct exit code.

---

## 6. Current API Client Implementation

Implementation file: `src/github_activity/github_api.py`

Tests: `tests/test_github_api.py`

The API client currently defines these custom exceptions:

- `GitHubAPIError`
- `UserNotFoundError`
- `RateLimitError`
- `ForbiddenError`
- `GitHubHTTPError`
- `GitHubNetworkError`
- `InvalidResponseError`

The current intended error mapping is:

- HTTP `404` → `UserNotFoundError`
- HTTP `429` → `RateLimitError`
- HTTP `403` → `RateLimitError` when the response headers or message indicate rate limiting; otherwise `ForbiddenError`
- HTTP `5xx` and other HTTP errors → `GitHubHTTPError`
- URL, network, timeout, and operating-system errors → `GitHubNetworkError`
- Invalid JSON or malformed event structures → `InvalidResponseError`

An empty username raises `ValueError` before a request is made.

The client validates that:

- The top-level API response is a list.
- Each event is a dictionary with a string `type`.
- Each event has a dictionary `repo`.
- Each event has a string `repo.name`.

The test suite mocks `urllib` and covers successful requests, URL construction and encoding, headers and timeout, empty results, HTTP errors, rate limiting, network failures, timeouts, invalid JSON, malformed structures, and empty usernames.

When making future changes, inspect the actual current implementation and tests instead of relying exclusively on this summary.

---

## 7. Planned Project Structure

The intended structure is:

```text
github-user-activity/
├── src/
│   └── github_activity/
│       ├── __init__.py
│       ├── cli.py
│       ├── github_api.py
│       └── formatter.py
├── tests/
│   ├── test_project_foundation.py
│   ├── test_github_api.py
│   ├── test_formatter.py
│   └── test_cli.py
├── README.md
├── REQUIREMENTS.md
├── PROJECT_CONTEXT.md
├── pyproject.toml
├── .gitignore
└── LICENSE
```

This is the intended final structure, not a guarantee that every listed file already exists. Inspect the repository before relying on it.

---

## 8. Stage 3: Event Formatter Planning

The next assistant should begin by reviewing:

1. `REQUIREMENTS.md`
2. The current repository structure
3. `src/github_activity/github_api.py`
4. `tests/test_github_api.py`
5. Any relevant existing documentation

Then propose explicit formatting rules for each of the eight supported event types.

The proposal should address:

- What information each event type should display.
- How actions are represented, using actual event data.
- How push events report commit counts, including singular/plural grammar.
- Which fields are required and which are optional for display.
- How missing, null, or incorrectly typed optional values are handled.
- What makes an event unusable for formatting.
- How unsupported event types are skipped.
- How the formatter's output distinguishes an empty event list from a list with no displayable events.
- What the formatter returns to the CLI.
- Which unit tests will verify each rule.

The formatter should remain independent of HTTP requests and terminal printing. Its responsibility is to transform event data into displayable messages according to the approved rules.

Do not assume every event contains every field that might normally appear in a GitHub API response. The implementation and tests must account for incomplete payloads.

After proposing the rules, recommend an approach and explain meaningful trade-offs. **Wait for explicit user approval before generating implementation code or a patch.**

---

## 9. Required Development Workflow

The user prefers a patch-first, reviewable workflow.

Follow these steps for each issue or implementation stage:

1. Inspect the relevant documentation, source code, and tests.
2. Explain the current state and identify the root problem or design decision.
3. Present viable approaches, including pros, cons, affected files, risks, and compatibility with the existing architecture where relevant.
4. Recommend one approach and explain why.
5. Wait for the user's decision or approval before implementing.
6. After approval, prepare a focused `.patch` file and the necessary tests.
7. Explain the expected result and provide the exact commands to check and apply the patch.
8. Let the user apply the patch, run the tests, and share the results.
9. Review the reported output and inspect any remaining issues before recommending a commit.

Typical patch workflow:

```powershell
git status --short
git switch -c <new-branch-name>
git apply --check <patch-file>
git apply <patch-file>
python -m pytest -v
git diff --check
git diff
git status --short
```

Adapt the commands to the actual branch and patch filename. Do not blindly create a branch if it already exists; inspect the Git state first.

The user applies patches and controls commits, pushes, and merges. **Do not directly modify the working branch, commit, push, or merge on the user's behalf.** Generate patches for the user to apply.

Work on one issue or stage at a time. Do not combine unrelated fixes or silently expand scope.

When a stage is completed and verified, update the relevant project context and handoff documentation to reflect the actual state.

---

## 10. Current Git State and Untracked Files

The last reported working-tree status, after commit `08c2cd2`, was:

```text
?? PHASE_1_VERIFICATION.md
?? phase-1-project-foundation.patch
?? phase-2-api-client-429-rate-limit.patch
?? phase-2-api-client.patch
```

These are untracked files. Preserve them unless the user explicitly authorizes a change.

Do not stage, delete, overwrite, or include these files in unrelated patches without first checking their purpose and obtaining permission where necessary.

Before proposing Git commands, inspect the current branch, working-tree status, and recent commit history. The recorded state may have changed since this context was written.

---

## 11. Known Incomplete Work and Verification Gaps

- The event formatter has not been implemented.
- The CLI has not yet been fully integrated.
- The installed `github-activity <username>` command has not been confirmed through a complete end-to-end manual test.
- The API client tests are mocked; they do not establish that a live GitHub request will always succeed.
- The README and context documentation should ultimately reflect only features that are implemented and verified.
- Optional and malformed event fields need explicit formatter rules and test coverage.
- The current Git state and whether the latest API-client commit has been pushed must be rechecked.

Do not describe the entire project as complete merely because the current test suite passes.

---

## 12. Instructions for Continuing in a New Chat

Start by confirming the project state from the repository and `REQUIREMENTS.md`.

The immediate task is:

**Plan Stage 3 — the event formatter. No formatter implementation code yet.**

Review the agreed requirements and current API client, then propose concrete formatting rules for all eight supported event types. Explain the design decisions and recommend an approach. Wait for the user's approval before generating a patch or implementation.

Preserve the user's patch-first workflow, avoid unnecessary scope, and clearly distinguish verified facts from assumptions.
