# Project Context: GitHub User Activity CLI

## 1. Project Overview

**Repository:** https://github.com/TheRealMoeid/github-user-activity

**Project:** A command-line application that retrieves and summarizes a GitHub user's recent public activity.

**Language:** Python 3.13+

**Package name:** `github_activity`

**Planned CLI command:** `github-activity <username>`

**Package and dependency management:** `pip`, virtual environment (`.venv`), and `pyproject.toml` using setuptools.

**Current development stage:** Stage 4 — CLI Integration (implemented and verified).

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
3. If the list has 20 or more entries and no reliable count is available, do not report a count. Stage 5 changed this from skipping the event: the formatter now reports `Pushed to <branch> in <repository>` (branch taken from a `refs/heads/` ref) or plain `Pushed to <repository>`, because GitHub's Events API no longer includes `size` or `commits` in push payloads.

Pull-request rules:

- A closed pull request is described as merged only when the payload explicitly establishes `merged is True`.
- Other recognized and unknown actions must not produce unsupported claims.

**Stage 3 verification reported by the user (superseded by the Stage 4 total below):**

```text
58 passed in 0.46s
```

The reported full suite included:

- 37 formatter tests.
- 20 API client tests.
- 1 foundation test.

The user ran `python -m pytest -v` on Windows using Python 3.13.16 and pytest 9.1.1.

This confirms the reported local test result. The repository's current commit, push state, and complete working-tree state must be checked independently before declaring the stage committed or published. When the remote repository was inspected, Stage 3 was pushed as `origin/stage-3-event-formatter` (commit `a07dfc1`) and had not been merged into the default branch.

### Stage 4: CLI Integration — Implemented and Verified

Implementation file: `src/github_activity/cli.py`

Test file: `tests/test_cli.py`

`main(argv=None) -> int` parses arguments with `argparse`, calls `github_api.fetch_user_events`, passes the result to `formatter.format_events`, prints the output, and returns the exit code. The module imports `github_api` and `formatter` as modules so tests can replace `github_api.fetch_user_events` without network access.

Agreed Stage 4 decisions:

- `argparse` handles argument parsing. `main` catches the `SystemExit` it raises and returns the code, so `main` always returns an integer. `--help` returns 0.
- The username is stripped. A blank username is rejected as invalid input (usage message, exit code 2) before any request is made.
- The activity header and list and both "no activity" messages go to stdout. Usage and errors go to stderr, and errors are prefixed with `Error:`.
- The original API result distinguishes the two empty cases: an empty list gives "No recent public activity found for <username>."; a non-empty list with no formatted messages gives "No supported recent activity to display for <username>."
- Only `GitHubAPIError` is caught. Unexpected exceptions are intentionally not hidden.
- The CLI words the user-not-found message (it includes the username) and the invalid-response message (generic, to avoid exposing internals). Other API errors reuse the message carried by the exception, because those messages already meet the requirements.

Known limitation: fully CLI-owned error messages would require `GitHubHTTPError` to expose the HTTP status code so the CLI could tell 5xx errors from other HTTP errors. That change to `github_api.py` was deliberately left out of Stage 4 and could be a separate future stage.

Reported verification:

- `python -m pytest -v`: 74 passed in 0.56s (Python 3.13.16, pytest 9.1.1, Windows), including 16 CLI tests.
- `git diff --check`: clean.
- Manual checks with the installed command: an existing user with activity (exit code 0), a nonexistent username (error message, exit code 1), no username (usage, exit code 2), and extra arguments (usage message).
- Not verified manually: live rate-limit, forbidden, 5xx, network-failure, and invalid-response cases. These are covered by mocked tests only.

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

Branches seen on the remote: `phase-1/project-foundation` (default branch), `phase-2/api-client`, and `stage-3-event-formatter`. Their history is linear: foundation, API client, a documentation update, then Stage 3 (`a07dfc1`).

The user creates the `stage-4-cli-integration` branch from `stage-3-event-formatter`. The Stage 4 patch was applied locally on that branch; whether it has been committed or pushed must be confirmed with `git status` and `git log`.

Planned finish: when Stage 4 and its documentation are complete, the user creates a `main` branch and merges the entire project into it. The user controls all commits, pushes, and merges.

During the Stage 4 verification, the only untracked files reported besides the Stage 4 files were `stage-3-event-formatter.patch` and `stage-4-cli-integration.patch`. Patch files are development artifacts and ordinarily should not be committed. Preserve untracked files unless the user authorizes changes.

This status is historical and may have changed. Check `git status`, recent commits, and the remote before making further recommendations.

---

## 10. Known Incomplete Work and Verification Gaps

- Stage 4 passed the user's reported full test suite (74 tests) and manual checks, but its commit and push state must be confirmed.
- Live rate-limit, forbidden, server-error, network-failure, and invalid-response behavior has been verified only with mocked tests.
- API client tests are mocked; they do not establish that every live GitHub request will succeed.
- The merge into `main` has not been done.
- No `LICENSE` file exists in the repository yet, while `README.md` links to it as "if present". Choose a license before publication or remove the link.
- The formatter's generic wording for unknown issue actions (for example "Issue activity on issue #1 in <repository>") reads awkwardly in real output. It is accurate and within the agreed requirements; any wording change would be a separate stage.
- Fully CLI-owned error messages would need a status code on `GitHubHTTPError`; not done (see Stage 4).
- Do not describe the project as published or merged until the user confirms it.

---

## 11. Instructions for Continuing in a New Chat

Start by confirming the project state from the repository and `REQUIREMENTS.md`.

All four planned stages are implemented. Confirm with `git status` and `git log` that Stage 4 and the documentation update are committed, then help the user create `main` and merge the project, following the user's workflow (the user runs all Git commands).

Do not add features without agreeing on scope first. Follow-ups the user may raise: the license decision, clearer formatter wording for unknown issue actions, and the `GitHubHTTPError` status-code change.

Preserve the user's patch-first workflow, avoid unnecessary scope, and clearly distinguish verified facts from assumptions.
