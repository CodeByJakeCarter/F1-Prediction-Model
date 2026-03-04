from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "release.sh"
VENV_BIN = ROOT / ".venv" / "bin"


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env["PATH"] = f"{VENV_BIN}:{merged_env.get('PATH', '')}"
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
            "showcontent = true\n\n"
            "[[tool.towncrier.type]]\n"
            'directory = "fixed"\n'
            'name = "Fixed"\n'
            "showcontent = true\n"
        ),
        encoding="utf-8",
    )
    (repo / "CHANGELOG.md").write_text(
        "# Changelog\n\n<!-- towncrier release notes start -->\n",
        encoding="utf-8",
    )
    (repo / "changelog.d").mkdir()
    (repo / "changelog.d" / "README.md").write_text("rules\n", encoding="utf-8")
    (repo / "changelog.d" / "200.added.md").write_text("Add endpoint docs.\n", encoding="utf-8")
    (repo / "changelog.d" / "150.fixed.md").write_text("Fix release typo.\n", encoding="utf-8")

    _run(["git", "init"], cwd=repo)
    _run(["git", "config", "user.email", "test@example.com"], cwd=repo)
    _run(["git", "config", "user.name", "Test User"], cwd=repo)
    _run(["git", "add", "."], cwd=repo)
    _run(["git", "commit", "-m", "init"], cwd=repo)
    return repo


def test_release_compiles_fragments_bumps_version_and_tags(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    result = _run(
        ["bash", "release.sh", "--version", "0.1.1", "--yes"],
        cwd=repo,
        env={"RELEASE_TEST_CMD": "true"},
    )

    assert result.returncode == 0, f"{result.stdout}\n{result.stderr}"
    assert "Release 0.1.1 completed." in result.stdout

    pyproject = (repo / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.1.1"' in pyproject

    changelog = (repo / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## 0.1.1 (" in changelog
    assert "Add endpoint docs." in changelog
    assert "Fix release typo." in changelog

    fragments = sorted(p.name for p in (repo / "changelog.d").glob("*.md"))
    assert fragments == ["README.md"]

    tags = _run(["git", "tag"], cwd=repo)
    assert "v0.1.1" in tags.stdout
