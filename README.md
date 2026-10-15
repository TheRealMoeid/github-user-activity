# GitHub User Activity CLI

A small command line tool that shows a GitHub user's recent public activity in the terminal. It uses only the Python standard library, so there is nothing to install besides the project itself.

This project is based on the [GitHub User Activity](https://roadmap.sh/projects/github-user-activity) challenge from roadmap.sh.

## Features

- Fetches recent public events from the GitHub REST API
- Turns eight event types into short, readable lines
- Merges repeated consecutive lines into one line with a count
- Reports errors in plain language, never as a Python traceback
- Uses clear exit codes, so it works in scripts
- Needs no third party runtime packages and no GitHub token

## Requirements

Python 3.13 or newer.

## Installation

Windows PowerShell:

```powershell
git clone https://github.com/TheRealMoeid/github-user-activity.git
cd github-user-activity
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

macOS or Linux:

```bash
git clone https://github.com/TheRealMoeid/github-user-activity.git
cd github-user-activity
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The `[dev]` part also installs pytest. Leave it out if you only want to run the tool.

## Usage

```bash
github-activity <username>
```

Example:

```text
$ github-activity octocat
GitHub activity for octocat:

- Pushed to main in octocat/Hello-World (3 times)
- Opened issue #42 in octocat/Hello-World
- Starred octocat/Spoon-Knife
- Forked octocat/example
```

The output depends on what GitHub returns for that user at that moment. Identical lines that appear next to each other are merged, and lines that are separated by other activity stay separate, so the order of the feed is kept.

## Supported events

| Event | Example line |
|---|---|
| Push | `Pushed to main in octocat/Hello-World` |
| Issue | `Opened issue #42 in octocat/Hello-World` |
| Issue comment | `Commented on issue #42 in octocat/Hello-World` |
| Pull request | `Merged pull request #12 in octocat/Hello-World` |
| Star | `Starred octocat/Spoon-Knife` |
| Fork | `Forked octocat/example` |
| Create | `Created branch feature/login in octocat/Hello-World` |
| Delete | `Deleted tag v1.0 in octocat/Hello-World` |

Some notes on the wording:

- GitHub's Events API no longer includes commit counts in push events, so a push is shown as `Pushed to <branch> in <repository>`. A count such as `Pushed 3 commits to ...` only appears when the data contains a reliable one.
- A closed pull request is only called merged when GitHub says so explicitly. Otherwise it is shown as closed.
- Unknown actions get generic wording such as `Activity on issue #7`, and events that cannot be described safely are skipped.

## Errors and exit codes

Results go to stdout. Usage and error messages go to stderr.

| Situation | Exit code |
|---|---|
| Activity shown | 0 |
| No public activity found | 0 |
| Events found, but none supported | 0 |
| User not found, rate limit, access denied, server error, network failure, unreadable response | 1 |
| Missing, extra, or blank username | 2 |

Example messages:

```text
Error: GitHub user 'someone' was not found.
Error: GitHub API rate limit exceeded; wait before retrying.
Error: Could not reach GitHub; check your connection and try again.
```

## Project layout

```text
src/github_activity/
    cli.py          argument parsing, printing, exit codes
    github_api.py   the HTTP request, response checks, API errors
    formatter.py    turns events into readable lines
tests/              pytest tests, no network needed
```

Each module has one job. The CLI never builds requests, the API client never prints, and the formatter does neither.

## Running the tests

```bash
python -m pytest -v
```

All tests use mocked responses, so they run without an internet connection.

## Limitations

- It shows only the recent public events GitHub provides, not a full history
- No authentication, so the unauthenticated rate limit applies
- No pagination, caching, or colored output

## License

MIT, see [LICENSE](LICENSE).