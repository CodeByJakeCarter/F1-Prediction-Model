from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "release.sh"


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    shutil.copy2(SCRIPT, repo / "release.sh")

    (repo / "pyproject.toml").write_text(
        '[project]\nname = "demo"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (repo / "CHANGELOG.md").write_text(
        "# Changelog\n\n<!-- towncrier release notes start -->\n",
        encoding="utf-8",
    )
    (repo / "changelog.d").mkdir()
    (repo / "changelog.d" / "README.md").write_text("rules\n", encoding="utf-8")

    (repo / "pyproject.toml").write_text(
        (
            '[project]\n'
            'name = "demo"\n'
            'version = "0.1.0"\n\n'
            "[tool.towncrier]\n"
            'directory = "changelog.d"\n'
            'filename = "CHANGELOG.md"\n'
            'start_string = "<!-- towncrier release notes start -->\\n"\n'
            'title_format = "## {version} ({project_date})"\n'
            'underlines = ["", "", ""]\n\n'
            "[[tool.towncrier.type]]\n"
            'directory = "added"\n'
            'name = "Added"\n'
            "showcontent = true\n"
        ),
        encoding="utf-8",
    )
    (repo / "changelog.d" / "100.added.md").write_text("Initial note.\n", encoding="utf-8")

    _run(["git", "init"], cwd=repo)
    _run(["git", "config", "user.email", "test@example.com"], cwd=repo)
    _run(["git", "config", "user.name", "Test User"], cwd=repo)
    _run(["git", "add", "."], cwd=repo)
    _run(["git", "commit", "-m", "init"], cwd=repo)
    return repo


def test_release_dry_run_does_not_mutate_repo(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    before_pyproject = (repo / "pyproject.toml").read_text(encoding="utf-8")
    before_changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")

    result = _run(
        ["bash", "release.sh", "--version", "0.1.1", "--dry-run"],
        cwd=repo,
        env={"RELEASE_TEST_CMD": "true"},
    )

    assert result.returncode == 0, result.stderr
    assert "dry-run: would create git tag v0.1.1" in result.stdout
    assert (repo / "pyproject.toml").read_text(encoding="utf-8") == before_pyproject
    assert (repo / "CHANGELOG.md").read_text(encoding="utf-8") == before_changelog
    assert (repo / "changelog.d" / "100.added.md").exists()

    tags = _run(["git", "tag"], cwd=repo)
    assert "v0.1.1" not in tags.stdout


def test_release_fails_on_dirty_tree_with_deterministic_code(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")

    result = _run(
        ["bash", "release.sh", "--version", "0.1.1", "--dry-run"],
        cwd=repo,
        env={"RELEASE_TEST_CMD": "true"},
    )

    assert result.returncode == 3
    assert "working tree must be clean" in result.stderr


def test_release_fails_when_tests_fail_with_deterministic_code(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    result = _run(
        ["bash", "release.sh", "--version", "0.1.1", "--dry-run"],
        cwd=repo,
        env={"RELEASE_TEST_CMD": "false"},
    )

    assert result.returncode == 4
    assert "preflight tests failed" in result.stderr


def test_release_requires_confirmation_for_non_dry_run(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    result = _run(
        ["bash", "release.sh", "--version", "0.1.1"],
        cwd=repo,
        env={"RELEASE_TEST_CMD": "true"},
    )

    assert result.returncode == 5
    assert "requires --yes" in result.stderr
