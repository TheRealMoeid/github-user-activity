# Project Context: GitHub User Activity CLI

## 1. Project Overview

**Repository:** https://github.com/TheRealMoeid/github-user-activity

**Project:** A command-line application that retrieves and summarizes a GitHub user's recent public activity.

**Language:** Python 3.13+

**Package name:** `github_activity`

**Planned CLI command:** `github-activity <username>`

**Package and dependency management:** `pip`, virtual environment (`.venv`), and `pyproject.toml` using setuptools.

**Current development stage:** Stage 3 — Event Formatter.

**Requirements source of truth:** `REQUIREMENTS.md`

Always consult `REQUIREMENTS.md` before proposing implementation changes. If another document conflicts with it, identify the conflict rather than silently changing the agreed requirements.

### Important verification rule

Distinguish between:

- Requirements that have been agreed upon.
- Code that has been implemented.
- Tests that have actually been run.
- Behavior that has been manually verified.
- Changes that have been committed or pushed.

Do not infer that a stage is committed or pushed merely because its tests pass.

---

## 2. Development Status

The project is being developed in separate, reviewable stages.

### Stage 1: Project Foundation — Completed

The foundation includes the initial Python project structure, package configuration, console-script configuration, and foundation tests.

The user previously reported that the foundation stage was completed and pushed.

### Stage 2: GitHub API Client — Implemented

Implementation file: `src/github_activity/github_api.py`

Test file: `tests/test_github_api.py`

The API client retrieves recent public GitHub events and handles HTTP, network, timeout, and response-validation errors.

The implementation uses the Python standard library and does not introduce a third-party HTTP client.

Previously reported verification:

- API client tests: 18 passed.
- Full test suite after Stage 2: 21 passed.
- `git diff --check`: clean.

These are historical results from the Stage 2 implementation, not the current total.

### Stage 3: Event Formatter — Implemented and Tested

Implementation file: `src/github_activity/formatter.py`

Test file: `tests/test_formatter.py`

The formatter converts supported event dictionaries into concise activity messages. It uses event-specific formatting functions and a small dispatcher.

The agreed implementation rules include:

- Support exactly the eight event types specified in `REQUIREMENTS.md`.
- Include issue/PR numbers and branch/tag names when useful and available.
- Use generic wording for unknown or missing actions only when the activity remains reliably identifiable.
- Skip malformed, unsupported, or insufficiently descriptive events.
- Continue formatting later events after an unusable event.
- Do not print raw API payloads.
- Keep formatting independent of HTTP requests and terminal printing.

Push-event count rules:

1. Prefer a valid, non-negative integer `payload.size`.
2. Otherwise, use the length of a valid commits list only when it contains fewer than 20 entries.
3. If the list has 20 or more entries and no reliable count is available, skip the event rather than risk reporting a truncated count.

Pull-request rules:

- A closed pull request is described as merged only when the payload explicitly establishes `merged is True`.
- Other recognized and unknown actions must not produce unsupported claims.

**Latest verification reported by the user:**

```text
58 passed in 0.46s
```

The reported full suite included:

- 37 formatter tests.
- 20 API client tests.
- 1 foundation test.

The user ran `python -m pytest -v` on Windows using Python 3.13.16 and pytest 9.1.1.

This confirms the reported local test result. The repository's current commit, push state, and complete working-tree state must be checked independently before declaring the stage committed or published.

### Stage 4: CLI Integration — Pending

The CLI has not yet been completed and integrated with the API client and formatter.

The next stage should:

1. Inspect `src/github_activity/cli.py` and the existing package configuration.
2. Confirm the intended command-line interface and exit codes against `REQUIREMENTS.md`.
3. Connect argument parsing, the API client, and the formatter.
4. Distinguish an empty API response from a response containing no displayable supported events.
5. Display concise user-facing errors for expected failures.
6. Add focused CLI tests.
7. Verify the installed console command and full test suite.

Do not begin implementation until the Stage 3 changes and documentation have been reviewed and the user has approved the next implementation step.

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

Unsupported event types must be skipped without inventing descriptions.

### Formatter contract

The public formatter function is:

```python
format_events(events) -> list[str]
```

Its responsibilities are to transform a list of event objects into displayable messages and skip events that cannot be described reliably.

It must not perform network requests, print to the terminal, or decide CLI exit codes.

An empty returned list can mean either that the API returned no events or that none of the returned events could be formatted. The CLI must distinguish these situations using the original API result.

---

## 5. CLI Contract

The planned command is:

```text
github-activity <username>
```

The agreed exit codes are:

| Outcome | Exit code |
|---|---:|
| Successful execution, including no activity or no supported events | `0` |
| API, network, or runtime failure | `1` |
| Invalid, missing, or extra CLI arguments | `2` |

The agreed no-activity messages are:

- Empty API response: `No recent public activity found for <username>.`
- Events exist, but none can be displayed as supported activity: `No supported recent activity to display for <username>.`

These are CLI responsibilities and must not be implemented inside the formatter.

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

The intended error mapping is:

- HTTP `404` → `UserNotFoundError`
- HTTP `429` → `RateLimitError`
- HTTP `403` → `RateLimitError` when the response headers or message indicate rate limiting; otherwise `ForbiddenError`
- HTTP `5xx` and other HTTP errors → `GitHubHTTPError`
- URL, network, timeout, and operating-system errors → `GitHubNetworkError`
- Invalid JSON or malformed event structures → `InvalidResponseError`

An empty username raises `ValueError` before a request is made.

The client validates the response structure and event repository information. When changing this module, inspect the actual implementation and tests rather than relying exclusively on this summary.

---

## 7. Planned Project Structure

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

Confirm the actual repository structure before making changes. This is the intended structure, not a guarantee that every listed file has been implemented.

---

## 8. Required Development Workflow

The user prefers a patch-first, reviewable workflow.

For each issue or implementation stage:

1. Inspect the relevant documentation, source code, and tests.
2. Explain the current state and identify the root problem or design decision.
3. Present viable approaches, including pros, cons, affected files, risks, and compatibility with the existing architecture where relevant.
4. Recommend one approach and explain why.
5. Wait for the user's decision or approval before implementing.
6. After approval, prepare a focused `.patch` file and the necessary tests.
7. Explain the expected result and provide the exact commands to check and apply the patch.
8. Let the user apply the patch, run tests, and share the results.
9. Review the reported output and inspect remaining issues before recommending a commit.

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

The user applies patches and controls commits, pushes, and merges. Do not directly modify the working branch, commit, push, or merge on the user's behalf. Generate patches for the user to apply.

Work on one issue or stage at a time. Do not combine unrelated fixes or silently expand scope.

When a stage is completed and verified, update the relevant project context and handoff documentation to reflect the actual state.

---

## 9. Current Git State and Untracked Files

The most recently reported working-tree state was on branch `stage-3-event-formatter`.

Reported modified files:

- `PROJECT_CONTEXT.md`
- `REQUIREMENTS.md`
- `src/github_activity/formatter.py`

Reported untracked files:

- `PHASE_1_VERIFICATION.md`
- `stage-3-event-formatter.patch`
- `tests/test_formatter.py`

The user reported that the full test suite passed with 58 tests.

This status is historical and may have changed. Check `git status`, recent commits, and the actual remote branch before making further recommendations.

Preserve untracked files unless their purpose is understood and the user authorizes changes. Do not delete, overwrite, stage, or include unrelated files in a patch without reviewing their purpose.

The patch file is a development artifact and ordinarily should remain outside the committed application source unless the user explicitly wants it tracked.

---

## 10. Known Incomplete Work and Verification Gaps

- Stage 3 has passed the user's reported full test suite, but its final commit and remote state must be confirmed.
- CLI integration and `tests/test_cli.py` remain pending.
- The installed `github-activity <username>` command has not been confirmed through a complete end-to-end manual test.
- API client tests are mocked; they do not establish that every live GitHub request will succeed.
- Documentation should reflect only implemented and verified behavior.
- Do not describe the entire project as complete merely because the current test suite passes.

---

## 11. Instructions for Continuing in a New Chat

Start by confirming the project state from the repository and `REQUIREMENTS.md`.

The immediate priority is to finish reviewing Stage 3, ensure that the documentation accurately reflects its implementation and test results, and confirm the Git state before recommending a commit.

After Stage 3 is finalized, discuss Stage 4 — CLI integration — before generating any implementation patch.

Preserve the user's patch-first workflow, avoid unnecessary scope, and clearly distinguish verified facts from assumptions.
