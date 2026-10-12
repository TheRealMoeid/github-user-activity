# Requirements: GitHub User Activity CLI

## 1. Project Overview

**Repository:** `github-user-activity`  
**Python package:** `github_activity`  
**CLI command:** `github-activity`  
**Python version:** Python 3.13+  
**Status:** Requirements agreed; implementation stages 1 to 6 are complete.

Build a command-line application that accepts a GitHub username, retrieves that user's recent public GitHub events through the GitHub REST API, and displays supported activity in a readable terminal format.

The application is intended to satisfy the roadmap.sh GitHub User Activity project while using a small, maintainable Python architecture.

### Implementation status as of the Stage 6 verification

- Project foundation: implemented.
- GitHub API client: implemented.
- Event formatter: implemented.
- CLI integration: implemented.
- Push-event fallback (Stage 5) and repeated-line collapsing (Stage 6): implemented.
- Full automated test suite: 95 tests passed in the user's reported local run.
- Installed command: checked manually for existing users, a nonexistent user, a missing username, and extra arguments.

These statuses describe reported implementation progress and do not change the requirements or acceptance criteria below.

## 2. Goals

- Accept a GitHub username as a command-line argument.
- Retrieve recent public activity from the GitHub REST API.
- Convert supported event types into concise, human-readable messages.
- Handle expected API, network, input, and response errors without exposing Python tracebacks for normal failures.
- Keep the application simple, testable, and free of third-party runtime dependencies.
- Provide automated tests that do not require a live GitHub connection.

## 3. Non-Goals for Version 1

The following are explicitly out of scope:

- GitHub authentication or personal access tokens.
- Database or persistent storage.
- Caching.
- Pagination or retrieval of a complete activity history.
- Asynchronous HTTP requests.
- Third-party HTTP clients or terminal UI frameworks.
- Colored output or a complex terminal interface.
- GitHub GraphQL API.
- Background jobs or configuration files.

The application retrieves recent **public events** available through the GitHub Events API. It must not claim to show a user's complete GitHub history.

## 4. Technology and Packaging Requirements

- Use Python 3.13 or later.
- Use `pip` and a Python `venv` virtual environment for development.
- Use `pyproject.toml` for project metadata, build configuration, dependencies, and the console-script entry point.
- Use `setuptools` as the build backend.
- Use the Python standard library for HTTP requests and JSON decoding. Do not use third-party HTTP libraries such as `requests` or `httpx`.
- Declare `pytest` as a development/test dependency, not a runtime dependency.
- Install the CLI through the project's console-script entry point.
- Use a `src/` package layout.

### Expected repository structure

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

The `LICENSE` file should be included if an appropriate project license is selected before publication. The structure above is intended; actual implementation status must be verified separately.

## 5. Architecture and Responsibilities

### `cli.py`

Responsible for:

- Reading and validating command-line arguments.
- Calling the API layer.
- Passing returned events to the formatter.
- Printing activity and user-facing errors.
- Returning the documented process exit codes.

It must not implement HTTP transport or contain the event-formatting rules.

### `github_api.py`

Responsible for:

- Constructing the GitHub API request.
- Sending the HTTP request with the standard library.
- Decoding and validating the JSON response structure.
- Handling HTTP, network, and response errors.

It must not format events for terminal display or parse CLI arguments.

### `formatter.py`

Responsible for:

- Formatting the eight supported event types into concise messages.
- Applying the agreed action-specific wording and generic fallbacks.
- Including useful issue/PR numbers and branch/tag names when available.
- Handling missing, malformed, and optional event fields safely.
- Skipping unsupported or unusable events without stopping later events.

The formatter must not perform HTTP requests, print to the terminal, or determine process exit codes.

The agreed public formatter interface is:

```python
format_events(events) -> list[str]
```

A returned empty list means there are no displayable messages. The CLI must use the original API result to distinguish an empty API response from a response containing events that are all unsupported or unusable.

## 6. GitHub API Requirements

Request recent public activity from:

```text
GET https://api.github.com/users/<username>/events
```

The request must use the standard-library `urllib` APIs and a timeout of 10 seconds.

Required headers:

```text
Accept: application/vnd.github+json
X-GitHub-Api-Version: 2022-11-28
User-Agent: github-user-activity
```

Do not add retries, authentication, pagination, caching, or other out-of-scope network behavior.

### Response validation

- The top-level JSON value must be a list.
- Each event must have the structure required by the API client contract.
- Invalid JSON and unexpected response structures must be reported as API-response errors.
- An empty list is a successful API response, not a failure.
- Tests must mock network access and must not depend on live GitHub responses.

## 7. Supported Event Types

Support exactly these eight event types:

1. `PushEvent`
2. `IssuesEvent`
3. `IssueCommentEvent`
4. `PullRequestEvent`
5. `WatchEvent`
6. `ForkEvent`
7. `CreateEvent`
8. `DeleteEvent`

Other event types must be skipped. The formatter must not print raw JSON or invent descriptions for unsupported events.

### `PushEvent`

- Format a valid, non-negative integer `payload.size` as the commit count when available.
- If `size` is missing or invalid, use the length of a valid `payload.commits` list only when it contains fewer than 20 entries.
- A commits list containing 20 or more entries may be truncated, so it is not a reliable count.
- Current GitHub Events API payloads can omit both `size` and `commits`. When no reliable count is available, do not skip the event and do not invent a count. Report the push without one: `Pushed to <branch> in <repository>` when `payload.ref` is `refs/heads/<branch>` with a non-empty branch name, otherwise `Pushed to <repository>`.
- Use singular `commit` for a count of one and plural `commits` otherwise.
- Do not invent a commit count.

### `IssuesEvent`

- Recognize `opened`, `closed`, and `reopened`.
- Include a valid positive issue number when available.
- For an unknown or missing action, use generic issue-activity wording only when the event and repository still reliably identify the activity.
- Use less-specific wording if the action is known but the issue number is unavailable.

### `IssueCommentEvent`

- For `created`, report that a comment was added to the issue.
- For other, missing, or unknown actions, use generic issue-comment activity wording where reliable.
- Do not include comment bodies in default output.
- Include a valid positive issue number when available.

### `PullRequestEvent`

- Recognize relevant actions such as `opened`, `closed`, and `reopened`.
- Include a valid positive pull-request number when available.
- Report a pull request as merged only when the payload explicitly establishes that it was merged.
- Use generic pull-request activity wording for unknown actions when the activity remains reliably identifiable.

### `WatchEvent`

- Format the event as a repository-star action.
- Require a usable repository name.

### `ForkEvent`

- Format the event as a repository-fork action.
- Identify the source repository; do not substitute the destination fork's name for the source.

### `CreateEvent`

Support creation of:

- Repositories.
- Branches.
- Tags.

For branch and tag creation, require a recognized `ref_type` and a usable reference name. If the created object cannot be identified reliably, skip the event.

### `DeleteEvent`

Support deletion of:

- Branches.
- Tags.

Require a recognized object type and usable reference name for a specific deletion message. Repository deletion is not part of the supported behavior.

### General formatter behavior

- Do not claim an action occurred if the payload does not provide enough information to support that claim.
- Handle singular and plural commit counts correctly.
- If an event is supported but lacks optional details, produce a safe, less-specific message where possible; otherwise skip that event.
- Do not include sensitive or unnecessary raw payload data in output.
- Continue processing remaining events after an unsupported or malformed event.

## 8. Output Requirements

Keep terminal output plain and readable. Version 1 does not require colors, tables, emojis, or a terminal UI framework.

Illustrative output:

```text
GitHub activity for octocat:

- Pushed 3 commits to octocat/Hello-World
- Opened issue #42 in octocat/Hello-World
- Starred octocat/Spoon-Knife
- Forked octocat/example
```

The exact activity depends on events returned by GitHub; the example is illustrative and must not be hard-coded.

The CLI merges runs of identical consecutive activity lines into one line with an ` (N times)` suffix, for example `- Pushed to main in octocat/Hello-World (3 times)`. Only adjacent duplicates are merged, so the order of GitHub's feed is preserved, and counts inside messages are never summed.

### Empty activity

If the API successfully returns an empty event list, print:

```text
No recent public activity found for <username>.
```

An empty activity list is a successful API response, not an error.

If events exist but none can be displayed, print:

```text
No supported recent activity to display for <username>.
```

These two outcomes must remain distinct.

## 9. Error Handling and Exit Codes

Normal application failures must be reported with concise, user-friendly messages. Do not show a Python traceback for expected input, HTTP, or network errors.

Required cases:

- **User not found:** Report that the requested GitHub user could not be found.
- **Rate limit:** Detect a rate-limit response when possible, using relevant response headers and/or the API error message. Report that the user should wait before retrying.
- **Other forbidden response:** Do not automatically label every HTTP `403` as a rate limit.
- **Other HTTP errors:** Report a concise error appropriate to the status category.
- **GitHub server errors (`5xx`):** Report that GitHub's server returned an error and suggest trying again later.
- **Network failure or timeout:** Report that GitHub could not be reached.
- **Invalid JSON or unexpected response structure:** Report that the API response could not be processed.
- **Invalid CLI arguments:** Print usage guidance.

### Exit codes

| Exit code | Meaning |
|---|---|
| `0` | Successful execution, including no activity or no supported events |
| `1` | API, network, response-processing, or other runtime failure |
| `2` | Invalid command-line arguments |

A missing user should exit with code `1`. A successful response containing no supported events should exit with code `0`.

## 10. Testing Requirements

Tests must not depend on GitHub being reachable or on live account activity.

Use `pytest` and standard-library mocking facilities such as `unittest.mock` to test API behavior deterministically.

### `test_github_api.py`

Cover at least:

- Successful HTTP response and JSON decoding.
- Correct request URL and relevant request headers.
- User-not-found response.
- Rate-limit response.
- Forbidden response that is not identified as a rate limit.
- Server error response.
- Network failure and timeout.
- Invalid JSON.
- Unexpected top-level response structure.

### `test_formatter.py`

Cover at least:

- All eight supported event types.
- Different relevant event actions.
- Commit-count singular/plural handling.
- Missing optional payload fields.
- Unknown and unsupported event types.
- Malformed or unusable event entries.
- Repository names and readable output.
- Safe fallback messages.
- Reliable push-count handling.
- Processing later events when earlier events are unusable.

### `test_cli.py`

Cover at least:

- Missing username.
- Extra positional arguments.
- Successful activity display.
- Empty activity response.
- No supported events to display.
- User-not-found error.
- Rate-limit/API error.
- Network or unexpected response failure.
- Correct process exit codes.
- No API request when arguments are invalid.

Tests should be isolated and must not require real network access.

## 11. Documentation Requirements

### `README.md`

Must explain:

- Project purpose and features.
- Python version requirement.
- Setup and installation.
- How to run the CLI.
- Example output.
- Supported event types.
- Error behavior and limitations.
- How to run tests.
- Current implementation status.

### `PROJECT_CONTEXT.md`

Must be maintained as an AI handoff document containing:

- Project purpose and agreed decisions.
- Architecture and module responsibilities.
- Current implementation status.
- Tests run and their actual results.
- Known issues and constraints.
- Next agreed task.

Do not mark requirements as implemented or tests as passing without verification. Keep agreed requirements separate from implementation status.

## 12. Acceptance Criteria

Version 1 is complete when all of the following are true:

- [x] The project installs into a Python 3.13+ virtual environment using `pip`.
- [x] The installed `github-activity <username>` command works.
- [x] The CLI validates arguments and uses the documented exit codes.
- [x] The API client uses only the Python standard library for HTTP.
- [x] The API client handles HTTP, network, timeout, JSON, and response-structure errors.
- [x] Missing users, rate limits, other forbidden responses, and server errors are distinguished appropriately.
- [x] All eight supported event types have formatter coverage.
- [x] Unsupported events are skipped safely.
- [x] Empty activity and no-supported-activity cases have distinct messages.
- [x] Automated tests run without making live GitHub requests.
- [x] The full test suite passes.
- [x] `README.md` and `PROJECT_CONTEXT.md` accurately describe the completed implementation.
- [x] No out-of-scope feature has been added without an explicit decision.

## 13. Implementation Workflow

1. Finalize requirements and project configuration.
2. Establish the project foundation and package configuration.
3. Implement the API client and its tests.
4. Implement the event formatter and its tests.
5. Integrate the CLI and test its behavior.
6. Run the full test suite and manually verify the installed command.
7. Update documentation to reflect the verified implementation state.

Implement one focused stage at a time. Keep changes small and testable, and do not add new scope without agreeing on it first.
