#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/release.sh --version X.Y.Z [--dry-run] [--yes]

Options:
  --version X.Y.Z   Required target version.
  --dry-run         Preview actions; do not mutate files, fragments, or tags.
  --yes             Required for non-dry-run releases.
EOF
}

exit_with() {
  local code="$1"
  local message="$2"
  echo "error: ${message}" >&2
  exit "${code}"
}

TARGET_VERSION=""
DRY_RUN=0
CONFIRM=0

while (($# > 0)); do
  case "$1" in
    --version)
      TARGET_VERSION="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --yes)
      CONFIRM=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit_with 2 "unknown argument '$1'"
      ;;
  esac
done

if [[ -z "${TARGET_VERSION}" ]]; then
  usage
  exit_with 2 "--version is required"
fi

if [[ "${DRY_RUN}" -eq 0 && "${CONFIRM}" -ne 1 ]]; then
  exit_with 5 "non-dry-run release requires --yes"
fi

if ! command -v git >/dev/null 2>&1; then
  exit_with 2 "git is required"
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  exit_with 3 "working tree must be clean before release"
fi

TEST_CMD="${RELEASE_TEST_CMD:-./.venv/bin/python -m pytest -q}"
if ! bash -lc "${TEST_CMD}"; then
  exit_with 4 "preflight tests failed"
fi

if [[ "${DRY_RUN}" -eq 1 ]]; then
  echo "dry-run: would bump pyproject.toml version to ${TARGET_VERSION}"
  echo "dry-run: would compile fragments from changelog.d into CHANGELOG.md"
  echo "dry-run: would clear processed fragments"
  echo "dry-run: would create git tag v${TARGET_VERSION}"
  if command -v towncrier >/dev/null 2>&1; then
    towncrier build --draft --version "${TARGET_VERSION}" || true
  fi
  exit 0
fi

if [[ ! -f pyproject.toml ]]; then
  exit_with 2 "pyproject.toml not found"
fi

if ! command -v towncrier >/dev/null 2>&1; then
  exit_with 2 "towncrier is required for release build"
fi

python - <<PY
from pathlib import Path
import re

target = "${TARGET_VERSION}"
path = Path("pyproject.toml")
text = path.read_text(encoding="utf-8")
updated, n = re.subn(
    r'(?m)^version\\s*=\\s*"[0-9]+\\.[0-9]+\\.[0-9]+"\\s*$',
    f'version = "{target}"',
    text,
    count=1,
)
if n != 1:
    raise SystemExit("Unable to update project version in pyproject.toml")
path.write_text(updated, encoding="utf-8")
PY

towncrier build --yes --version "${TARGET_VERSION}"

if git rev-parse "v${TARGET_VERSION}" >/dev/null 2>&1; then
  exit_with 6 "tag v${TARGET_VERSION} already exists"
fi

git add pyproject.toml CHANGELOG.md changelog.d
git commit -m "chore(release): ${TARGET_VERSION}"
git tag "v${TARGET_VERSION}"

echo "Release ${TARGET_VERSION} completed."
