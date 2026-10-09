# Requirements: GitHub User Activity CLI

## 1. Project Overview

**Repository:** `github-user-activity`\
**Python package:** `github_activity`\
**CLI command:** `github-activity`\
**Python version:** Python 3.13\
**Status:** Requirements agreed; implementation not yet started.

Build a command-line application that accepts a GitHub username,
retrieves that user's recent public GitHub events through the GitHub
REST API, and displays supported activity in a readable terminal format.

The application is intended to satisfy the roadmap.sh GitHub User
Activity project while using a small, maintainable Python architecture.

## 2. Goals

-   Accept a GitHub username as a command-line argument.
-   Retrieve recent public activity from the GitHub REST API.
-   Convert supported event types into concise, human-readable messages.
-   Handle expected API, network, input, and response errors without
    exposing Python tracebacks for normal failures.
-   Keep the application simple, testable, and free of third-party
    runtime dependencies.
-   Provide automated tests that do not require a live GitHub
    connection.

## 3. Non-Goals for Version 1

The following are explicitly out of scope:

-   GitHub authentication or personal access tokens.
-   Database or persistent storage.
-   Caching.
-   Pagination or retrieval of a complete activity history.
-   Asynchronous HTTP requests.
-   Third-party HTTP clients or terminal UI frameworks.
-   Colored output or a complex terminal interface.
-   GitHub GraphQL API.
-   Background jobs or configuration files.

The application retrieves recent **public events** available through the
GitHub Events API. It must not claim to show a user's complete GitHub
history.

## 4. Technology and Packaging Requirements

-   Use Python 3.13.
-   Use `pip` and a Python `venv` virtual environment for development.
-   Use `pyproject.toml` for project metadata, build configuration,
    dependencies, and the console-script entry point.
-   Use `setuptools` as the build backend.
-   Use the Python standard library for HTTP requests and JSON decoding.
    Do not use third-party HTTP libraries such as `requests` or `httpx`.
-   Declare `pytest` as a development/test dependency, not a runtime
    dependency.
-   Install the CLI through the project's console-script entry point.
-   Use a `src/` package layout.

### Expected repository structure

``` text
github-user-activity/
├── src/
│   └── github_activity/
│       ├── __init__.py
│       ├── cli.py
│       ├── github_api.py
│       └── formatter.py
├── tests/
│   ├── test_cli.py
│   ├── test_github_api.py
│   └── test_formatter.py
├── README.md
├── REQUIREMENTS.md
├── PROJECT_CONTEXT.md
├── pyproject.toml
├── .gitignore
└── LICENSE
```

The `LICENSE` file should be included if an appropriate project license
is selected before publication.

## 5. Architecture and Responsibilities

### `cli.py`

Responsible for:

-   Reading and validating command-line arguments.
-   Calling the API layer.
-   Passing returned events to the formatter.
-   Printing activity and user-facing errors.
-   Returning the documented process exit codes.

It must not implement HTTP transport or contain the event-formatting
rules.

### `github_api.py`

Responsible for:

-   Constructing the GitHub API request.
-   Sending the HTTP request with the standard library.
-   Decoding and validating the JSON response structure.
-   Handling HTTP, network, and response errors.
-   Returning event data to the caller.

It must not format events for terminal display.

### `formatter.py`

Responsible for:

-   Converting supported event objects into readable activity messages.
-   Handling event-specific payload fields and actions.
-   Skipping unsupported event types safely.
-   Avoiding crashes when optional event details are missing or
    malformed.

It must not make network requests or print directly to the terminal. It
should return formatted messages to the caller.

### Dependency direction

The intended application flow is:

``` text
CLI arguments
    ↓
cli.py
    ↓
github_api.py
    ↓
GitHub REST API
    ↓
Event data
    ↓
formatter.py
    ↓
Human-readable terminal output
```

Keep the modules focused and avoid unnecessary abstractions.

## 6. Command-Line Interface

The installed command must be:

``` bash
github-activity <username>
```

The `pyproject.toml` console-script mapping must expose
`github-activity` and call `github_activity.cli:main`.

### Input behavior

-   Accept exactly one positional GitHub username.
-   If no username is supplied, print a concise usage message and exit
    with code `2`.
-   If extra positional arguments are supplied, print a concise usage
    message and exit with code `2`.
-   Do not make a network request when the CLI arguments are invalid.
-   Do not require the user to configure a GitHub token.

The application should rely on GitHub's API to determine whether the
account exists rather than attempting to maintain its own username
rules.

## 7. GitHub API Requirements

Request recent public events from:

``` text
GET https://api.github.com/users/<username>/events
```

Implementation requirements:

-   Use `urllib` or another appropriate Python standard-library HTTP
    facility.
-   Send an appropriate `Accept` header for the GitHub REST API.
-   Set a reasonable request timeout so the CLI cannot wait
    indefinitely.
-   Decode the response as JSON.
-   Validate that the top-level response is a list and that event
    entries are objects with the fields needed for safe processing.
-   Do not assume every event contains every optional payload field.
-   Do not print raw API responses to the user.
-   Do not retry requests automatically in version 1.
-   Do not implement pagination in version 1.

The unauthenticated API may impose rate limits. The application must
report rate-limit failures clearly and must not attempt to bypass them.

## 8. Supported Event Types

Version 1 must support the following eight event types.

  -----------------------------------------------------------------------
  Event type                          Required display behavior
  ----------------------------------- -----------------------------------
  `PushEvent`                         Report the number of commits pushed
                                      and the repository name.

  `IssuesEvent`                       Report the issue action, such as
                                      opened or closed, and the
                                      repository name.

  `IssueCommentEvent`                 Report that the user commented on
                                      an issue and identify the
                                      repository.

  `PullRequestEvent`                  Report the pull-request action,
                                      such as opened or closed, and the
                                      repository name.

  `WatchEvent`                        Report that the user starred the
                                      repository.

  `ForkEvent`                         Report that the user forked the
                                      repository.

  `CreateEvent`                       Report creation of a repository,
                                      branch, or tag when the event
                                      payload identifies the created
                                      object.

  `DeleteEvent`                       Report deletion of a branch or tag
                                      when the event payload identifies
                                      the deleted object.
  -----------------------------------------------------------------------

### Event formatting rules

-   Prefer concise, natural-language messages.
-   Include `owner/repository` when the event contains a usable
    repository name.
-   Use the event's action and payload fields when needed to describe
    the activity accurately.
-   Do not claim an action occurred if the payload does not provide
    enough information to support that claim.
-   Handle singular and plural commit counts correctly.
-   If an event is supported but lacks optional details, produce a safe,
    less-specific message where possible; otherwise skip that event.
-   Do not include sensitive or unnecessary raw payload data in output.

### Unsupported events

-   Skip event types outside the supported list.
-   Continue processing the remaining events.
-   Do not crash, display raw JSON, or invent a description for an
    unknown event type.

If the API returns events but none can be displayed because they are
unsupported or unusable, print a distinct, friendly message such as:

``` text
No supported recent activity to display for <username>.
```

## 9. Output Requirements

Keep terminal output plain and readable. Version 1 does not require
colors, tables, emojis, or a terminal UI framework.

For example:

``` text
GitHub activity for octocat:

- Pushed 3 commits to octocat/Hello-World
- Opened an issue in octocat/Hello-World
- Starred octocat/Spoon-Knife
- Forked octocat/example
```

The exact activity depends on the events returned by GitHub; the example
is illustrative and must not be hard-coded.

### Empty activity

If the API successfully returns an empty event list, print:

``` text
No recent public activity found for <username>.
```

An empty activity list is a successful API response, not an error.

## 10. Error Handling and Exit Codes

Normal application failures must be reported with concise, user-friendly
messages. Do not show a Python traceback for expected input, HTTP, or
network errors.

### Required cases

-   **User not found:** Report that the requested GitHub user could not
    be found.
-   **Rate limit:** Detect a rate-limit response when possible, using
    relevant response headers and/or the API error message. Report that
    the user should wait before retrying.
-   **Other forbidden response:** Do not automatically label every HTTP
    `403` as a rate limit; report a generic forbidden/API-access error
    when the response does not indicate rate limiting.
-   **Other HTTP errors:** Report a concise error appropriate to the
    status category.
-   **GitHub server errors (`5xx`):** Report that GitHub's server
    returned an error and suggest trying again later.
-   **Network failure or timeout:** Report that GitHub could not be
    reached.
-   **Invalid JSON or unexpected response structure:** Report that the
    API response could not be processed.
-   **Invalid CLI arguments:** Print usage guidance.

### Exit codes

  -----------------------------------------------------------------------
  Exit code                           Meaning
  ----------------------------------- -----------------------------------
  `0`                                 Successful execution, including a
                                      valid response with no activity.

  `1`                                 API, network, response-processing,
                                      or other runtime failure.

  `2`                                 Invalid command-line arguments.
  -----------------------------------------------------------------------

A missing user should exit with code `1`. A successful response
containing no supported events should also exit with code `0`.

## 11. Testing Requirements

Tests must not depend on GitHub being reachable or on live account
activity.

Use `pytest` and standard-library mocking facilities such as
`unittest.mock` to test API behavior deterministically.

### `test_github_api.py`

Cover at least:

-   Successful HTTP response and JSON decoding.
-   Correct request URL and relevant request headers.
-   User-not-found response.
-   Rate-limit response.
-   Forbidden response that is not identified as a rate limit.
-   Server error response.
-   Network failure and timeout.
-   Invalid JSON.
-   Unexpected top-level response structure.

### `test_formatter.py`

Cover at least:

-   All eight supported event types.
-   Different relevant event actions.
-   Commit-count singular/plural handling.
-   Missing optional payload fields.
-   Unknown/unsupported event types.
-   Malformed or unusable event entries.
-   Repository names and readable output.

### `test_cli.py`

Cover at least:

-   Missing username.
-   Extra positional arguments.
-   Successful activity display.
-   Empty activity response.
-   No supported events to display.
-   User-not-found error.
-   Rate-limit/API error.
-   Network or unexpected response failure.
-   Correct process exit codes.
-   No API request when arguments are invalid.

Tests should be isolated and should not require real network access.

## 12. Documentation Requirements

### `README.md`

Must explain:

-   Project purpose and features.
-   Python version requirement.
-   Setup and installation.
-   How to run the CLI.
-   Example output.
-   Supported event types.
-   Error behavior and limitations.
-   How to run tests.

### `PROJECT_CONTEXT.md`

Must be maintained as an AI handoff document containing:

-   Project purpose and agreed decisions.
-   Architecture and module responsibilities.
-   Current implementation status.
-   Tests run and their actual results.
-   Known issues and constraints.
-   Next agreed task.

Do not mark requirements as implemented or tests as passing without
verification. Keep agreed requirements separate from implementation
status.

## 13. Acceptance Criteria

Version 1 is complete when all of the following are true:

-   [ ] The project installs into a Python 3.13 virtual environment
    using `pip`.
-   [ ] The installed `github-activity <username>` command works.
-   [ ] The CLI validates its arguments and uses the documented exit
    codes.
-   [ ] The API client uses only the Python standard library for HTTP.
-   [ ] The API client handles HTTP, network, timeout, JSON, and
    response-structure errors.
-   [ ] Missing users, rate limits, other forbidden responses, and
    server errors are distinguished appropriately.
-   [ ] All eight supported event types have formatter coverage.
-   [ ] Unsupported events are skipped safely.
-   [ ] Empty activity and no-supported-activity cases have distinct
    messages.
-   [ ] Automated tests run without making live GitHub requests.
-   [ ] The full test suite passes.
-   [ ] `README.md` and `PROJECT_CONTEXT.md` accurately describe the
    completed implementation.
-   [ ] No out-of-scope feature has been added without an explicit
    decision.

## 14. Implementation Workflow

Follow this workflow:

1.  Review and finalize the requirements and project configuration plan.
2.  Establish the project foundation and package configuration.
3.  Implement the API client and its tests.
4.  Implement the event formatter and its tests.
5.  Integrate the CLI and test its behavior.
6.  Run the full test suite and manually verify the installed command.
7.  Update documentation to reflect the verified implementation state.

Implement one focused stage at a time. Keep changes small and testable,
and do not add new scope without agreeing on it first.
