# Project Context: GitHub User Activity CLI

## 1. Project Overview

**Repository:** https://github.com/TheRealMoeid/github-user-activity

**Project:** A command-line application that retrieves and summarizes a GitHub user's recent public activity.

**Language:** Python 3.13+

**Package name:** `github_activity`

**Planned CLI command:** `github-activity <username>`

**Package and dependency management:** `pip`, virtual environment (`.venv`), and `pyproject.toml` using setuptools.

**Current development stage:** Stage 8 — API Client Hardening (implemented and verified). All eight stages are implemented and the project is licensed under the MIT License (`LICENSE`); the merge of `stage-8-api-hardening` into `main` remains.

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

Reported verification at the end of Stage 4 (the 74-test total is historical; see Stage 6 for the current total):

- `python -m pytest -v`: 74 passed in 0.56s (Python 3.13.16, pytest 9.1.1, Windows), including 16 CLI tests.
- `git diff --check`: clean.
- Manual checks with the installed command: an existing user with activity (exit code 0), a nonexistent username (error message, exit code 1), no username (usage, exit code 2), and extra arguments (usage message).
- Not verified manually: live rate-limit, forbidden, 5xx, network-failure, and invalid-response cases. These are covered by mocked tests only.

### Stage 5: Push Event Fallback — Implemented and Verified

Implementation file: `src/github_activity/formatter.py` (`_format_push_event`)

Test file: `tests/test_formatter.py`

Reason for the stage: a live check of `https://api.github.com/users/josebbk/events` returned 30 events, all `PushEvent`. Every payload contained only `repository_id`, `push_id`, `ref`, `head`, and `before`, with no `size` and no `commits`. Before this stage the formatter skipped all of them, so `github-activity josebbk` printed "No supported recent activity to display for josebbk." The mocked tests had not caught this because they used the older payload shape. The change is consistent with GitHub's changelog entry of 2025-08-08 announcing removal of commit summaries from Events API payloads.

Agreed decision (option A): keep `Pushed N commits to <repository>` whenever `size` or a complete short `commits` list gives a reliable count; otherwise report `Pushed to <branch> in <repository>` (branch taken from a `refs/heads/` ref) or plain `Pushed to <repository>`. A count is never invented. Pushes without a usable repository name are still skipped. Rejected: fetching the real count through the compare API (extra requests per push, outside the agreed network scope).

Reported verification:

- `python -m pytest -v`: 88 passed in 0.31s (Python 3.13.16, pytest 9.1.1, Windows).
- `git diff --check`: clean.
- Live check: `github-activity josebbk` now lists the pushes as `Pushed to main in josebbk/99ways-website`.
- Pushed as `origin/stage-5-push-fallback` (commit `4c087e3`).

Not verified: the live shape of `PullRequestEvent` payloads. The same changelog said pull-request payloads would be trimmed. If `merged` is absent, merged pull requests are reported as closed, which is safe but less informative.

### Stage 6: Collapse Repeated Activity Lines — Implemented and Verified

Implementation file: `src/github_activity/cli.py` (`_collapse_repeats`)

Test file: `tests/test_cli.py` (7 new tests)

Reason for the stage: with Stage 5 alone, a user with many pushes to the same branch produced dozens of identical lines.

Agreed decision (option 1): a private helper in `cli.py` merges runs of identical consecutive messages into one line with an ` (N times)` suffix. Only adjacent duplicates are merged, so the order of GitHub's feed is preserved. A single line has no suffix. Counts inside messages are never summed. `format_events` is unchanged and still returns one message per usable event. Rejected: a public helper in `formatter.py` and grouping push events inside `format_events`.

Reported verification:

- The user reported that all 95 tests passed. The pytest output for this run was not shared, so its timing and tool versions are not recorded here.
- Live check: `github-activity josebbk` prints a single `Pushed to main in josebbk/99ways-website (30 times)` line, and `github-activity TheRealMoeid` shows merged runs such as `(3 times)` while non-adjacent duplicates stay separate.
- Pushed as `origin/stage-6-collapse-repeats` (commit `8363eb1`).

### Stage 7: Formatter Cleanup — Implemented and Verified

Implementation file: `src/github_activity/formatter.py`

Test file: `tests/test_formatter.py`

Scope (agreed): remove dead code and fix redundant wording only. No new named issue actions were added.

- The pull-request formatter no longer carries unused placeholder strings in its `actions` mapping. `ready_for_review` and `converted_to_draft` are explicit branches, and the mapping holds only `opened` and `reopened`. Behavior is unchanged.
- Generic wording no longer repeats "issue": `Activity on issue #<n> in <repository>`, `Comment activity on issue #<n> in <repository>`, and `Activity on pull request #<n> in <repository>`. The versions without a number (`Issue activity in <repository>`, `Issue comment activity in <repository>`, `Pull request activity in <repository>`) are unchanged.
- Tests added for the `ready_for_review` and `converted_to_draft` branches (with and without a number), `reopened`, and the empty-payload fallback.
- Rejected: naming more issue actions such as `labeled` or `assigned`. The redundancy fix was chosen as the smaller change.

Reported verification:

- The user reported that all 101 tests passed. The pytest output for this run was not shared.
- Live check: `github-activity TheRealMoeid` shows lines such as `Activity on issue #4 in TheRealMoeid/github-user-activity (3 times)`.
- Pushed as `origin/stage-7-formatter-cleanup` (commit `31023c3`) and merged into `main` through pull request #5.

### Stage 8: API Client Hardening — Implemented and Verified

Implementation file: `src/github_activity/github_api.py`

Test file: `tests/test_github_api.py`

- A truncated response body (`http.client.IncompleteRead`) now raises `InvalidResponseError("GitHub returned an incomplete response.")` instead of escaping as a traceback. The CLI shows its generic "response could not be processed" message for it.
- Other `http.client.HTTPException` cases, such as `BadStatusLine`, are handled together with URL, timeout, and operating-system errors as `GitHubNetworkError`. `HTTPError` is still caught first, so the HTTP status classification is unchanged.
- New tests assert the exact message and exception class for 404, 429, a plain 403, 500, another 4xx (418), and a `URLError`, and cover `IncompleteRead`, `HTTPException`, and `BadStatusLine`.
- `*.patch` was added to `.gitignore`, so development patch files no longer appear as untracked.
- Rejected: a status code on `GitHubHTTPError` (an architecture change for messages that already meet the requirements) and a `python -m` entry point (not required).

Reported verification:

- `python -m pytest -v`: 110 passed in 0.58s (Python 3.13.16, pytest 9.1.1, Windows).
- Not verified live: the new paths only occur on broken or truncated connections, so they are covered by mocked tests only.
- Pushed as `origin/stage-8-api-hardening` (commit `39d2641`); not yet merged into `main` when this document was written.

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

The CLI also merges runs of identical consecutive activity lines into one line with an ` (N times)` suffix. This is a presentation step in `cli.py`; the formatter still returns one message per usable event.

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

`main` is the default branch on the remote. Its tip is `facd1f9`, the merge of pull request #5 (`stage-7-formatter-cleanup`), so it contains everything through Stage 7: foundation, API client, a documentation update, Stage 3 (`a07dfc1`), Stage 4 (`febe70f`), the Stage 4 documentation update (`d996cff`), Stage 5 (`4c087e3`), Stage 6 (`8363eb1`), the Stage 5 and 6 documentation update (`9ab33e3`), the MIT license (`11e7d62`), and Stage 7 (`31023c3`).

Other remote branches: `phase-1/project-foundation`, `phase-2/api-client`, `stage-3-event-formatter`, `stage-4-cli-integration`, `stage-5-push-fallback`, `stage-6-collapse-repeats`, `add-mit-license`, `stage-7-formatter-cleanup` (all merged into `main`), and `stage-8-api-hardening` (commit `39d2641`, not yet merged when this was written). The documentation update for Stages 7 and 8 is committed on `stage-8-api-hardening`. This was checked by inspecting the remote repository, not the user's local working tree.

The user controls all commits, pushes, and merges.

Patch files are development artifacts. Since Stage 8, `*.patch` is listed in `.gitignore`, so they no longer show as untracked. Preserve the user's local patch files unless the user authorizes changes.

This status is historical and may have changed. Check `git status`, recent commits, and the remote before making further recommendations.

---

## 10. Known Incomplete Work and Verification Gaps

- `stage-8-api-hardening` (including this documentation update) has to be merged into `main`.
- The live shape of `PullRequestEvent` payloads has not been checked (see Stage 5). Merged pull requests may be reported as closed if `merged` is missing.
- Live rate-limit, forbidden, server-error, network-failure, truncated-response, and invalid-response behavior has been verified only with mocked tests.
- API client tests are mocked; they do not establish that every live GitHub request will succeed. The Stage 5 push-payload problem showed that mocked payloads can drift from the live API.
- Fully CLI-owned error messages would need a status code on `GitHubHTTPError`; deliberately not done (see Stage 4 and Stage 8).
- Do not describe the project as published until the user confirms it.

---

## 11. Instructions for Continuing in a New Chat

Start by confirming the project state from the repository and `REQUIREMENTS.md`.

All eight stages are implemented, and the user reported 110 passing tests (Python 3.13.16, pytest 9.1.1, Windows) at the end of Stage 8. Confirm with `git status` and `git log` that `stage-8-api-hardening` and this documentation update are merged into `main`. After that, no required work remains.

Do not add features without agreeing on scope first. Optional follow-ups the user may raise: a live check of pull-request payloads and the `GitHubHTTPError` status-code change.

Preserve the user's patch-first workflow, avoid unnecessary scope, and clearly distinguish verified facts from assumptions.
