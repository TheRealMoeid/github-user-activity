"""Tests for the repository's initial packaging and structure."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_declares_python_version_and_console_script() -> None:
    with (ROOT / "pyproject.toml").open("rb") as config_file:
        config = tomllib.load(config_file)

    assert config["project"]["requires-python"] == ">=3.13"
    assert config["project"]["dependencies"] == []
    assert config["project"]["scripts"]["github-activity"] == (
        "github_activity.cli:main"
    )
    assert any(
        dependency.startswith("pytest")
        for dependency in config["project"]["optional-dependencies"]["dev"]
    )


def test_src_package_has_expected_modules() -> None:
    package = ROOT / "src" / "github_activity"
    for module in ("__init__.py", "cli.py", "github_api.py", "formatter.py"):
        assert (package / module).is_file()


def test_project_documentation_files_exist() -> None:
    for filename in ("README.md", "REQUIREMENTS.md", "PROJECT_CONTEXT.md"):
        assert (ROOT / filename).is_file()
