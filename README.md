# GitHub User Activity CLI

A command-line application planned to retrieve a GitHub user's recent public events and display supported activity in readable terminal output.

## Status

**Foundation stage only.** Package structure and development configuration are established by this patch. API retrieval, event formatting, and functional CLI behavior remain unimplemented.

## Requirements

- Python 3.13+
- `pip`

Runtime HTTP and JSON handling will use the Python standard library. `pytest` is for development and testing only.

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

Once the API client, formatter, and CLI integration are implemented:

```bash
github-activity <username>
```

Example output (illustrative only):

```text
GitHub activity for octocat:

- Pushed 3 commits to octocat/Hello-World
- Opened an issue in octocat/Hello-World
- Starred octocat/Spoon-Knife
```

## Planned event support

`PushEvent`, `IssuesEvent`, `IssueCommentEvent`, `PullRequestEvent`, `WatchEvent`, `ForkEvent`, `CreateEvent`, and `DeleteEvent`.

## Run tests

```bash
python -m pytest -v
```

Automated tests must not require a live GitHub connection.

## Limitations

The completed tool will show only recent public events exposed by GitHub's Events API, not a user's complete history. Authentication, caching, pagination, asynchronous requests, third-party HTTP clients, and persistent storage are out of scope for version 1.

See [REQUIREMENTS.md](REQUIREMENTS.md) for the full specification and [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) for implementation status.
