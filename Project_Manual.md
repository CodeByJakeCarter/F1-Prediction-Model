# F1 Oracle — Mega Development Workbook (v1–v7)

---
# State Map (Capability Index)

This index summarizes the **capability states** the system progresses through.
Each state corresponds to a proven system capability verified by gate tests.

| State | Version | Capability |
|------|--------|-----------|
| S1 | v1 | Project boots with stable test harness |
| S2 | v1 | Core persistence layer usable |
| S3 | v1 | One-season ingestion deterministic |
| S4 | v1 | Baseline predictions available |
| S5 | v1 | Simulation + leak-free backtesting |
| S7 | v2 | Multi-season ingestion reliable |
| S10 | v3 | Credible prediction evaluation |
| S12 | v4 | Operational service (tasks + CI) |
| S13 | v5 | Decision engine (scenarios + attribution) |
| S14 | v6 | Backend ready for UI integration |
| S15 | v6 | Web UI usable by operator |
| S16 | v7 | Reproducible ML training + registry |



This is a **single, executable workbook**. Each **leaf node** is intended to be **one commit-sized change**.
No code is included here — only instructions.

## Canonical verify command
```
./.venv/bin/python -m pytest -q
```

## Frontend verify guidance (v6+)
For the separate UI repository, use a lightweight check appropriate to your setup:
- Manual smoke: open the UI in a browser and confirm pages render and API calls succeed.
- If you add a JS test runner later, run it here (keep the command documented in the UI repo RUNBOOK).


## Constraints and non-goals

- No live race prediction mode (this remains historical + simulated analysis).
- No real network calls in tests (use mocks/fixtures).
- No background schedulers beyond the simple task runner introduced in v4.

**Version-scoped constraints**
- UI work begins in **v6** (before that: backend only).
- Machine-learning work begins in **v7** (before that: stats-first).


## Layer taxonomy
- Frontend: UI repo code (views/components/router/state), contract tests.
- API: routing, request/response schemas, HTTP errors.
- Service: business rules, orchestration of repositories, deterministic error mapping.
- Repository: database queries and persistence operations.
- Model: ORM entities + constraints.
- Migration: schema evolution and migration tests.
- Provider: external API adapter, pagination, rate-limits, parsing.
- Ingestion: normalization + persistence pipelines + orchestration.
- Model/Prediction: feature extraction, scoring, probability conversion.
- Evaluation: backtesting, metrics, calibration.
- Ops: tasks, artifacts, CI, logging/metrics.

## Global decisions (encode once, then follow)
### Determinism rules
- All randomness must be explicitly controlled (seeded) and tested for reproducibility.
- Ordering must be stable (explicit sorts; deterministic tie-break rules).
- Ingestion must be idempotent (upsert strategy) or season-scoped deterministic reload (clear-and-reload), per the persistence decision below.

### Persistence strategy decision
- Reference tables (Driver, Constructor, Circuit): **upsert by natural key** (e.g., driver_ref).
- Season-scoped fact tables (Race, Result, Lap, PitStop, QualifyingResult): **clear-and-reload per season** by default for determinism (optimize later).

### Fixture strategy
- Maintain small, hand-auditable synthetic fixtures:
  - `fixture_min_season`: 1 season, 2 races, 3 drivers, 2 constructors.
  - `fixture_edge_cases`: DNF/missing position, tie scores, missing optional fields.
  - `fixture_sprint_era`: a minimal sprint-shaped payload used only to verify policy.
- Maintain mocked provider payloads per endpoint family (drivers/constructors/races/results/etc.).

### Artifact strategy
- All long workflows (ingestion/backtest/sim/task runs) write JSON artifacts under `artifacts/`.
- Artifact naming must be deterministic (stable run_id under fixed ‘now’ fixture).
- Artifacts have versioned schemas; tests validate required fields and ordering.

## Version gates (must be satisfiable)
### v1 Gate
- One full season ingests into a clean DB using mocks/fixtures.
- Predictions endpoint returns schema-valid deterministic output.
- Championship simulation returns probabilities summing to 1.
- Backtesting prevents leakage (test enforces).

### v2 Gate
- Multi-season ingestion completes across an enumerated season list (mocked).
- Deterministic reload produces identical DB state across reruns.
- Data-quality audits report and categorize issues deterministically.

### v3 Gate
- Backtesting produces a metrics artifact with log loss + Brier score.
- Calibration bucket summary exists and is stable on fixed fixtures.

### v4 Gate
- Ingestion and backtests run as non-blocking tasks with status lifecycle.
- Task artifacts are stored and discoverable via API.
- CI runs tests + migration smoke checks successfully.

### v5 Gate
- Scenario runs (baseline vs counterfactual) produce deterministic artifacts.
- Attribution output is stable, ordered, and includes caveats.

### v6 Gate
- UI can authenticate (single-owner) and call protected endpoints.
- Operator can start ingestion/backtests/scenarios and inspect tasks/artifacts.

### v7 Gate
- Training dataset artifacts are deterministic and leak-free.
- Training runs are reproducible under fixed seeds.
- ML models are only selectable after evaluation gates pass.

### v5 Gate
- Scenario engine runs baseline + counterfactual deterministically.
- Scenario artifacts are schema-valid and stable across reruns.
- Attribution output is stable, ordered, and includes caveats.

### v6 Gate
- UI can authenticate (single-owner token) and call protected endpoints.
- UI can start ingestion/backtest tasks and view task details + artifacts.
- UI can view predictions, scenarios, and attribution outputs without developer tooling.

### v7 Gate
- Training dataset artifacts are deterministic and leak-free.
- Training runs are reproducible under controlled seeds and identical inputs.
- Model registry records provenance and metrics; ML is not promoted without evaluation gates.


---
# Current State Tracker

Update this block manually as you work through the workbook.

- Current state: 1.2.1.10
- Next target state: 1.3.1.1
- Last completed step: 1.2.1.10
- Current version focus: v1


---
# Design Principles

These principles guide decisions when the workbook doesn’t specify an exact choice.

1. **Determinism over cleverness**: explicit ordering, explicit seeds, explicit policies.
2. **Artifacts over logs**: logs help, artifacts prove.
3. **Contracts over convenience**: schemas and error shapes are stable interfaces.
4. **Tests before optimization**: correctness first, speed second.
5. **Provider isolation**: external schema never leaks past normalization.
6. **Small steps**: each leaf is one safe, reviewable change.
7. **No hidden global state**: configuration is explicit and testable.


---
# Debugging Command Toolbox

These are common commands you’ll use while executing the workbook.

## Python / backend
- Run all tests:
```
./.venv/bin/python -m pytest -q
```
- Run a focused subset:
```
./.venv/bin/python -m pytest -q -k ingestion
./.venv/bin/python -m pytest -q tests/integration
./.venv/bin/python -m pytest -q --maxfail=1
```
- Show collected tests (sanity):
```
./.venv/bin/python -m pytest -q --collect-only
```

## Artifacts
- List artifacts:
```
ls -R artifacts | head
```
- Pretty-print JSON (if jq installed):
```
jq . artifacts/<path-to-file>.json
```

## Git hygiene (before gates/releases)
- Check status:
```
git status
```
- View recent commits:
```
git log --oneline -n 20
```


---
# Data Contracts (Stable Interfaces)

These contracts define what must remain stable for clients (including the UI) and for reproducible workflows.

## API Error Contract
- Errors include:
  - `code` (machine readable)
  - `message` (human readable)
  - optional `details` (structured)

Invariants:
- Error shapes are consistent across endpoints.
- Auth errors return 401 with the same error shape.

## Ingestion Contract
Input:
- season (or season range in v2+)
- endpoint selection (v4+)
- deterministic reload policy (season-scoped facts)

Output (artifact + API task metadata):
- counts per family (created/updated/skipped/warned/error)
- warnings/errors with stable codes
- deterministic artifact paths

Invariants:
- For identical mocked inputs, reruns produce identical DB state and report totals.

## Prediction Contract
Input:
- `race_id` or `(season, round)`

Output:
- list of drivers with probabilities and any summary fields

Invariants:
- probabilities in [0,1]
- sum(probabilities) = 1 (within tolerance)
- ordering is deterministic

## Scenario Contract (v5)
Input:
- target race selector
- list of perturbations (typed, versioned)
- execution settings

Output:
- baseline results
- scenario results
- deltas

Invariants:
- baseline must match normal prediction path for the same inputs
- delta computation is deterministic and stable

## Task Contract (v4+)
Task lifecycle:
- queued → running → succeeded/failed

Task fields:
- status, timestamps, type, parameters summary
- artifact pointers

Invariants:
- starting a task is non-blocking
- task detail always exposes artifact pointers when present

## Artifact Contract
- All artifacts are JSON with versioned schemas.
- Artifact naming is deterministic under fixed ‘now’ in tests.
- Artifacts are discoverable via API (metadata endpoints), not raw filesystem access.


---
# Provider Stability Strategy

The external provider (Jolpica/Ergast-compatible) is treated as **unstable input**.

Rules:

- All provider-specific parsing lives in the **Provider** layer.
- No provider payload structure leaks past the **Normalization** layer.
- Normalization converts provider records into internal schemas with explicit policies for:
  - missing fields
  - unexpected enum values
  - paging limits
  - data anomalies (DNF/NC etc.)
- Provider changes are handled by updating adapters/normalizers and their tests **without** changing domain services or API contracts unless absolutely required.


---
# Failure Playbook

This section lists common failure modes, likely causes, and deterministic debug steps.

## Ingestion failures
**Symptoms**
- Missing rows (e.g., drivers/races/results not fully populated)
- Per-season counts drift across reruns
- Reports show warnings/errors unexpectedly

**Likely causes**
- Pagination collector not applied to an endpoint
- Provider envelope changes (MRData structure)
- Normalizer policy mismatch (missing fields or parsing differences)
- Orchestrator order violates dependencies (e.g., races before circuits)

**Deterministic debug steps**
1. Inspect the ingestion report artifact for missing family counts and errors.
2. Re-run the failing endpoint adapter tests with mocked payloads.
3. Compare normalized output ordering for stability (explicit sorts).
4. Validate clear-and-reload boundaries (season-scoped facts cleared correctly).

## Prediction failures
**Symptoms**
- Probabilities don’t sum to 1
- NaNs/Infs appear
- Output ordering changes between runs

**Likely causes**
- Feature extraction includes future data or nondeterministic ordering
- Tie-break policy not applied consistently
- Probability conversion not guarded against degenerate scores

**Deterministic debug steps**
1. Run the smallest failing fixture and print (or artifact) intermediate features.
2. Re-run probability conversion unit tests and invariants checks.
3. Verify tie-break ordering and stable sorts are applied at the final step.

## Backtesting / metrics failures
**Symptoms**
- Leakage test fails
- Metrics artifacts missing fields or unstable ordering

**Likely causes**
- Data split boundary incorrect (race N sees race N or N+1)
- Metrics aggregation iterates over dicts/sets without sorting

**Deterministic debug steps**
1. Inspect the backtest artifact inputs: what races were included for each prediction.
2. Add an assertion in the harness enforcing strict chronological constraints.
3. Ensure all metric collections are explicitly ordered before writing artifacts.

## Task/ops failures (v4+)
**Symptoms**
- Tasks never leave “running”
- Artifacts not discoverable from task detail
- UI cannot start jobs (401/403)

**Likely causes**
- Task lifecycle transitions not persisted
- Artifact bundling path mismatch
- Auth middleware not whitelisting /health and OpenAPI
- Missing Authorization header in UI client wrapper

**Deterministic debug steps**
1. Confirm task status transitions in DB via repository/service tests.
2. Verify artifact paths via deterministic path naming tests.
3. Re-run API auth tests for protected vs public endpoints.


---
# Recovery Procedure (When Things Go Sideways)

Use this to restore a known-good state quickly.

1. Confirm your current state tracker (above) is accurate.
2. Ensure the working tree is clean or your changes are committed/stashed:
   - `git status`
3. Recreate local environment if needed (v0 steps).
4. Reset database to a clean state (test DB or dev DB):
   - Drop and recreate (method depends on your DB choice)
   - Re-run migrations to head
5. Re-run the gate tests for your current state (or the most recent completed state).
6. Re-run deterministic ingestion on fixtures if your state requires it.
7. Inspect artifacts generated by ingestion/backtest/scenario runs for root cause.

Rule of thumb: If you can’t prove you’re at the intended state, roll back to the previous state and re-advance.


---
# Future Extensions (Parking Lot)

These are intentionally **not** part of v1–v7 unless explicitly promoted into a version.
Capture ideas here without polluting the executable plan.

- Live race updates and near-real-time predictions
- Weather integration using real forecasts (beyond proxy perturbations)
- Tyre/strategy modelling with richer pitstop + stint representations
- Circuit clustering / similarity metrics
- Telemetry-derived pace proxies (if data becomes available)
- Multi-tenant hosting / team collaboration
- Public SaaS hardening (billing, user management, audit logs)




---


---

# Version 0 — IDE + Environment Setup (Repo Operating System)
Goal: Make the repo immediately workable on a fresh machine, create and populate tracking docs using standard tools, and expose project history clearly to repo visitors.

## 0.1 Local environment and IDE setup

#### 0.1.1.1 — Create .python-version (or equivalent)

**Why this step exists**  
Pins the intended Python version so contributors and CI match behavior.

**Layer**  
Ops

**Files likely touched**  
.python-version

**Tests to add/update**  
None (doc-only). Verify file exists and matches your chosen version.

**Verify**
```
git status
```


#### 0.1.1.2 — Document environment bootstrap in RUNBOOK

**Why this step exists**  
Ensures a fresh machine can set up venv and run tests deterministically.

**Layer**  
Docs

**Files likely touched**  
RUNBOOK.md

**Tests to add/update**  
Doc check: RUNBOOK includes steps to create venv and run pytest.

**Verify**
```
git status
```


#### 0.1.2.1 — Add VS Code workspace recommendations

**Why this step exists**  
Captures editor settings and extension recommendations without forcing tooling.

**Layer**  
Ops

**Files likely touched**  
.vscode/extensions.json, .vscode/settings.json

**Tests to add/update**  
None (doc-only). Verify settings files load in VS Code.

**Verify**
```
git status
```


#### 0.1.2.2 — Add debug/run configurations for API and pytest

**Why this step exists**  
Lets you run FastAPI and pytest from the IDE without memorizing commands.

**Layer**  
Ops

**Files likely touched**  
.vscode/launch.json

**Tests to add/update**  
Manual verify: configurations appear and launch successfully.

**Verify**
```
git status
```


#### 0.1.3.1 — Add local env template (.env.example)

**Why this step exists**  
Standardizes required environment variables without committing secrets.

**Layer**  
Ops

**Files likely touched**  
.env.example

**Tests to add/update**  
None. Verify template documents required vars clearly.

**Verify**
```
git status
```


#### 0.1.3.2 — Add deterministic test env guidance

**Why this step exists**  
Prevents tests from accidentally hitting non-test databases or live services.

**Layer**  
Docs

**Files likely touched**  
RUNBOOK.md

**Tests to add/update**  
Doc check: RUNBOOK states ‘no live HTTP in tests’ and test DB rules.

**Verify**
```
git status
```


## 0.2 Tracking docs (standard tools) and project history visibility

#### 0.2.1.1 — Create README.md skeleton (visitor-first)

**Why this step exists**  
Gives repo visitors a fast understanding: what it is, current state, how to run.

**Layer**  
Docs

**Files likely touched**  
README.md

**Tests to add/update**  
None (doc-only). Verify headings exist and links are valid.

**Verify**
```
git status
```


#### 0.2.1.2 — Add ‘State Map’ link to README

**Why this step exists**  
Makes capability progression visible to visitors and future you.

**Layer**  
Docs

**Files likely touched**  
README.md

**Tests to add/update**  
None (doc-only). Verify README links to State Map section/file.

**Verify**
```
git status
```


#### 0.2.2.1 — Create CHANGELOG.md with initial entries

**Why this step exists**  
Establishes human-readable project history that stays clean over time.

**Layer**  
Docs

**Files likely touched**  
CHANGELOG.md

**Tests to add/update**  
None (doc-only). Verify format is consistent and version headings exist.

**Verify**
```
git status
```


#### 0.2.2.2 — Create changelog fragment directory and rules

**Why this step exists**  
Enables clean-slate releases by collecting small fragments between releases.

**Layer**  
Docs

**Files likely touched**  
changelog.d/ + docs/changelog.md

**Tests to add/update**  
None (doc-only). Verify directory exists and rules documented.

**Verify**
```
git status
```


#### 0.2.3.1 — Create decisions log (ADRs-lite) structure

**Why this step exists**  
Records why key decisions were made so outsiders can follow the history logically.

**Layer**  
Docs

**Files likely touched**  
spec/decisions.md or docs/adr/

**Tests to add/update**  
None (doc-only). Verify an initial decision entry exists.

**Verify**
```
git status
```


#### 0.2.3.2 — Add CONTRIBUTING.md (solo-friendly)

**Why this step exists**  
Even for solo projects, explains conventions and how changes are tracked.

**Layer**  
Docs

**Files likely touched**  
CONTRIBUTING.md

**Tests to add/update**  
None (doc-only). Verify references to changelog fragments and decisions log.

**Verify**
```
git status
```


#### 0.2.4.1 — Add release tagging policy to README

**Why this step exists**  
Makes releases and history discoverable: tags correspond to version milestones.

**Layer**  
Docs

**Files likely touched**  
README.md

**Tests to add/update**  
None (doc-only). Verify README references tags + changelog.

**Verify**
```
git status
```


## 0.3 Manual release script (clean-slate changelog)

#### 0.3.1.1 — Add scripts/release.sh skeleton (manual release driver)

**Why this step exists**  
Creates a repeatable, auditable release process you can run locally.

**Layer**  
Ops

**Files likely touched**  
scripts/release.sh, tests/unit/ops/

**Tests to add/update**  
Tests: script has a dry-run mode test that validates it doesn’t mutate without confirmation.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 0.3.1.2 — Add release script: preflight checks

**Why this step exists**  
Prevents releasing from a dirty tree or failing tests.

**Layer**  
Ops

**Files likely touched**  
scripts/release.sh, tests/unit/ops/

**Tests to add/update**  
Tests: simulate dirty tree and failing tests; script exits with deterministic error codes.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 0.3.1.3 — Add release script: compile changelog fragments into CHANGELOG.md

**Why this step exists**  
Automates release notes generation and resets fragments to a clean slate.

**Layer**  
Ops

**Files likely touched**  
scripts/release.sh, changelog.d/, tests/integration/ops/

**Tests to add/update**  
Tests: with sample fragments, generated changelog section is deterministic and fragments are cleared.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 0.3.1.4 — Add release script: bump version (single source of truth)

**Why this step exists**  
Ensures version metadata and changelog stay in sync.

**Layer**  
Ops

**Files likely touched**  
pyproject.toml (or version file), scripts/release.sh, tests/unit/ops/

**Tests to add/update**  
Tests: version bump is deterministic and only touches expected files.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 0.3.1.5 — Add release script: create git tag

**Why this step exists**  
Makes project history visible via tags aligned to versions.

**Layer**  
Ops

**Files likely touched**  
scripts/release.sh, tests/unit/ops/

**Tests to add/update**  
Tests: dry-run shows intended tag; real run requires explicit confirmation flag.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 0.3.2.1 — Document release process in RUNBOOK

**Why this step exists**  
Ensures you can execute releases consistently months later.

**Layer**  
Docs

**Files likely touched**  
RUNBOOK.md

**Tests to add/update**  
Doc check: RUNBOOK includes release steps + rollback guidance.

**Verify**
```
git status
```



---
### STATE S0 — Development environment + project history are legible (v0 complete)

**Capabilities unlocked**
- Fresh machine setup is documented and repeatable
- VS Code workspace settings and run configs exist
- Tracking docs exist and are populated (README, CHANGELOG, decisions log)
- Manual release script exists for clean-slate changelog releases
- Repo visitors can see project evolution via changelog + tags + decisions

**Invariants (must remain true going forward)**
- Docs reflect reality (no aspirational setup steps)
- Changelog entries are built from fragments and reset on release
- Key decisions are recorded in the decisions log
- Releases are tagged and discoverable from the repo

**Exit gate (must be proven by tests/commands)**
- Follow RUNBOOK on a clean machine profile and reach a green test run
- Run release script in dry-run mode successfully
- Verify README clearly links to State Map, CHANGELOG, and decisions log

**Artifacts produced**
- None

# Version 1 — Deterministic MVP

Goal: Boot service, persist core entities, ingest one full season deterministically, return baseline predictions, and simulate championship probabilities.

---

## 1.1 Repository scaffolding and docs

#### 1.1.1.1 — Create docs/ and spec/ structure

**Why this step exists**  
Stabilizes long-lived documentation locations and prevents later churn.

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.1.1.2 — Add RUNBOOK.md (setup/run/test/ingest)

**Why this step exists**  
Makes daily commands discoverable and repeatable.

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.1.1.3 — Add ARCHITECTURE_NOTES.md (living)

**Why this step exists**  
Records boundaries and assumptions without rewriting the workbook.

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.1.1.4 — Add CODE_STYLE.md

**Why this step exists**  
Prevents style drift across modules and tests.

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.1.1.5 — Add ERROR_HANDLING.md

**Why this step exists**  
Defines domain vs HTTP error mapping consistently.

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.1.1.6 — Add spec/requirements.yml

**Why this step exists**  
Turns goals into verifiable requirements.

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.1.1.7 — Add spec/decisions.md

**Why this step exists**  
Locks hard boundaries like data source and determinism rules.

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.1.1.8 — Record v1 scope decisions

**Why this step exists**  
Freezes v1 non-goals and acceptance target (one season).

**Layer**  
Docs

**Files likely touched**  
docs/, spec/

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 1.2 Test harness foundations

#### 1.2.1.1 — Create tests/ layout (unit/integration)

**Why this step exists**  
Ensures test discovery is consistent and scalable.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a trivial smoke test that always runs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.2 — Add pytest configuration

**Why this step exists**  
Stabilizes discovery rules and avoids implicit defaults changing.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test asserting intended collection behavior.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.3 — Add DB engine fixture

**Why this step exists**  
Enables isolated DB integration tests.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add an integration test that creates and disposes the engine.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.4 — Add DB session fixture

**Why this step exists**  
Standardizes open/rollback/close behavior in tests.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test that forces an error and asserts rollback.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.5 — Add factories for core entities (part 1)

**Why this step exists**  
Speeds up later tests by centralizing object creation patterns.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test creating Driver/Constructor using factories.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.6 — Add factories for core entities (part 2)

**Why this step exists**  
Completes fixture toolkit for season/race/results.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test building a minimal season with one race and results.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.7 — Add HTTP client test helper

**Why this step exists**  
Reduces repeated boilerplate in endpoint tests.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test calling health endpoint via helper.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.8 — Add deterministic ‘now’ fixture

**Why this step exists**  
Prevents time-based flakiness in reports and artifacts.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test showing fixed timestamps across runs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.9 — Add artifact temp directory fixture

**Why this step exists**  
Prevents tests writing artifacts to random places.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test that writes an artifact under a temp artifacts root.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.2.1.10 — Add snapshot-style assertion helper (tolerant)

**Why this step exists**  
Enables comparing deterministic JSON artifacts without brittle exact matches.

**Layer**  
Tests

**Files likely touched**  
tests/, conftest, fixtures

**Tests to add/update**  
Add a test comparing two artifacts with stable ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 1.3 API skeleton

#### 1.3.1.1 — Create FastAPI app factory

**Why this step exists**  
Keeps app wiring testable and avoids import side effects.

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add a test that imports and instantiates the app.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.3.1.2 — Mount /api/v1 router

**Why this step exists**  
Establishes stable versioning for all endpoints.

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add a routing test asserting /api/v1 is mounted.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.3.1.3 — Add /api/v1/health endpoint

**Why this step exists**  
Provides a minimal endpoint to verify app boot and client wiring.

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add endpoint test asserting 200 and status payload.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.3.1.4 — Add standard validation error shape

**Why this step exists**  
Makes client errors consistent and testable.

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add a test triggering validation error and asserting response schema.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.3.1.5 — Add standard not-found error shape

**Why this step exists**  
Standardizes 404 responses across API.

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add a test for unknown route asserting error shape.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.3.1.6 — Add OpenAPI metadata

**Why this step exists**  
Makes API self-describing and stable for reviewers.

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add a test that OpenAPI schema includes title/version.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.3.1.7 — Add API dependency wiring boundary

**Why this step exists**  
Creates a single place to build dependencies (db session, services).

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add a test that dependencies can be constructed in isolation.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.3.1.8 — Add API pagination schema (foundation)

**Why this step exists**  
Prepares list endpoints to scale later without breaking clients.

**Layer**  
API

**Files likely touched**  
src/api/, tests/api/

**Tests to add/update**  
Add schema tests for pagination response shape.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 1.4 Configuration + DB baseline

#### 1.4.1.1 — Add settings object

**Why this step exists**  
Centralizes config (DB URL, env, artifacts path).

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add tests that settings load defaults deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.4.1.2 — Add test env override mechanism

**Why this step exists**  
Ensures tests never target dev/prod DB.

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add tests that test settings point to isolated DB URL.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.4.1.3 — Add config validation rules

**Why this step exists**  
Fails fast on invalid configuration.

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add tests for invalid settings producing clear errors.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.4.1.4 — Create DB engine module

**Why this step exists**  
Creates canonical place to build engines and sessions.

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add a test that engine creation uses settings.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.4.1.5 — Create session factory helper

**Why this step exists**  
Standardizes session lifecycle for repo/service.

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add tests for commit/rollback behavior.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.4.1.6 — Initialize migrations baseline

**Why this step exists**  
Tracks schema changes from day one.

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add migration smoke test: upgrade to head on empty DB.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.4.1.7 — Add migration test helper (upgrade)

**Why this step exists**  
Catches broken revisions early.

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add tests that upgrade completes cleanly.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.4.1.8 — Add migration test helper (downgrade)

**Why this step exists**  
Prevents irreversible or broken downgrades (where supported).

**Layer**  
DB + Migration

**Files likely touched**  
src/db/, migrations/, tests/db/

**Tests to add/update**  
Add tests that downgrade completes cleanly.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S1 — Project boots with stable test harness

**Capabilities unlocked**
- Project documentation skeleton exists
- Pytest runs in a stable, configured layout
- FastAPI app can be instantiated via app factory
- API version router mounted and health endpoint responds
- DB engine/session helpers exist and migrations baseline is runnable

**Invariants (must remain true going forward)**
- Repository remains runnable and testable after each step
- No real network calls in tests
- Config has a test override so tests never hit dev/prod DB
- Error response shapes are consistent (validation + not-found)

**Exit gate (must be proven by tests/commands)**
- Run the full test suite successfully
- Hit /api/v1/health in tests and assert 200 + expected payload
- Migration smoke test upgrades an empty DB to head

**Artifacts produced**
- None


## 1.5 Core domain entities (Driver, Constructor, Season, Race, Result)

### 1.5.1 Driver

#### 1.5.1.1.1 — Define Driver ORM model

**Why this step exists**  
Introduces the Driver entity and locks invariants needed by ingestion.

**Layer**  
Model

**Files likely touched**  
src/models/driver*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid Driver creates; missing required fields fail.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.1.2 — Add Driver identity uniqueness constraint

**Why this step exists**  
Prevents duplicate logical records by enforcing unique identity (driver_ref).

**Layer**  
Model

**Files likely touched**  
src/models/driver*, tests/integration/db/

**Tests to add/update**  
Integration test: inserting duplicates fails deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.2.1 — Create migration for Driver table

**Why this step exists**  
Persists schema for the entity with constraints matching the model.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: after upgrade, table exists and columns match expectations.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.2.2 — Add indexes for Driver identity lookups

**Why this step exists**  
Ensures ingestion and lookups remain fast and predictable as data grows.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Schema test: expected indexes exist.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.3.1 — Add Driver repository: create/get

**Why this step exists**  
Centralizes DB access and query logic in one boundary.

**Layer**  
Repository

**Files likely touched**  
src/repositories/driver*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create + get-by-id; missing returns None.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.3.2 — Add Driver repository: list ordering

**Why this step exists**  
Stabilizes list behavior for later API and ingestion audits.

**Layer**  
Repository

**Files likely touched**  
src/repositories/driver*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: list order deterministic; limit/offset works.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.4.1 — Add Driver service: create behavior

**Why this step exists**  
Moves business rules and error mapping out of API and into the service layer.

**Layer**  
Service

**Files likely touched**  
src/services/driver*, tests/unit/services/

**Tests to add/update**  
Service tests: happy-path create works; invalid input mapped to expected error.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.4.2 — Add Driver service: duplicate handling

**Why this step exists**  
Ensures duplicates are handled deterministically and consistently.

**Layer**  
Service

**Files likely touched**  
src/services/driver*, tests/unit/services/

**Tests to add/update**  
Service tests: duplicate create yields expected error result.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.5.1 — Add Driver API read schema

**Why this step exists**  
Creates stable API representation decoupled from ORM details.

**Layer**  
API

**Files likely touched**  
src/schemas/driver*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: serialization includes expected fields and types.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.1.5.2 — Add Driver API create schema

**Why this step exists**  
Defines validated inputs for create operations (even if endpoints come later).

**Layer**  
API

**Files likely touched**  
src/schemas/driver*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: invalid inputs fail; valid inputs pass.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.5.2 Constructor

#### 1.5.2.1.1 — Define Constructor ORM model

**Why this step exists**  
Introduces the Constructor entity and locks invariants needed by ingestion.

**Layer**  
Model

**Files likely touched**  
src/models/constructor*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid Constructor creates; missing required fields fail.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.1.2 — Add Constructor identity uniqueness constraint

**Why this step exists**  
Prevents duplicate logical records by enforcing unique identity (constructor_ref).

**Layer**  
Model

**Files likely touched**  
src/models/constructor*, tests/integration/db/

**Tests to add/update**  
Integration test: inserting duplicates fails deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.2.1 — Create migration for Constructor table

**Why this step exists**  
Persists schema for the entity with constraints matching the model.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: after upgrade, table exists and columns match expectations.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.2.2 — Add indexes for Constructor identity lookups

**Why this step exists**  
Ensures ingestion and lookups remain fast and predictable as data grows.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Schema test: expected indexes exist.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.3.1 — Add Constructor repository: create/get

**Why this step exists**  
Centralizes DB access and query logic in one boundary.

**Layer**  
Repository

**Files likely touched**  
src/repositories/constructor*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create + get-by-id; missing returns None.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.3.2 — Add Constructor repository: list ordering

**Why this step exists**  
Stabilizes list behavior for later API and ingestion audits.

**Layer**  
Repository

**Files likely touched**  
src/repositories/constructor*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: list order deterministic; limit/offset works.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.4.1 — Add Constructor service: create behavior

**Why this step exists**  
Moves business rules and error mapping out of API and into the service layer.

**Layer**  
Service

**Files likely touched**  
src/services/constructor*, tests/unit/services/

**Tests to add/update**  
Service tests: happy-path create works; invalid input mapped to expected error.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.4.2 — Add Constructor service: duplicate handling

**Why this step exists**  
Ensures duplicates are handled deterministically and consistently.

**Layer**  
Service

**Files likely touched**  
src/services/constructor*, tests/unit/services/

**Tests to add/update**  
Service tests: duplicate create yields expected error result.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.5.1 — Add Constructor API read schema

**Why this step exists**  
Creates stable API representation decoupled from ORM details.

**Layer**  
API

**Files likely touched**  
src/schemas/constructor*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: serialization includes expected fields and types.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.2.5.2 — Add Constructor API create schema

**Why this step exists**  
Defines validated inputs for create operations (even if endpoints come later).

**Layer**  
API

**Files likely touched**  
src/schemas/constructor*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: invalid inputs fail; valid inputs pass.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.5.3 Season

#### 1.5.3.1.1 — Define Season ORM model

**Why this step exists**  
Introduces the Season entity and locks invariants needed by ingestion.

**Layer**  
Model

**Files likely touched**  
src/models/season*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid Season creates; missing required fields fail.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.1.2 — Add Season identity uniqueness constraint

**Why this step exists**  
Prevents duplicate logical records by enforcing unique identity (year).

**Layer**  
Model

**Files likely touched**  
src/models/season*, tests/integration/db/

**Tests to add/update**  
Integration test: inserting duplicates fails deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.2.1 — Create migration for Season table

**Why this step exists**  
Persists schema for the entity with constraints matching the model.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: after upgrade, table exists and columns match expectations.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.2.2 — Add indexes for Season identity lookups

**Why this step exists**  
Ensures ingestion and lookups remain fast and predictable as data grows.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Schema test: expected indexes exist.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.3.1 — Add Season repository: create/get

**Why this step exists**  
Centralizes DB access and query logic in one boundary.

**Layer**  
Repository

**Files likely touched**  
src/repositories/season*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create + get-by-id; missing returns None.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.3.2 — Add Season repository: list ordering

**Why this step exists**  
Stabilizes list behavior for later API and ingestion audits.

**Layer**  
Repository

**Files likely touched**  
src/repositories/season*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: list order deterministic; limit/offset works.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.4.1 — Add Season service: create behavior

**Why this step exists**  
Moves business rules and error mapping out of API and into the service layer.

**Layer**  
Service

**Files likely touched**  
src/services/season*, tests/unit/services/

**Tests to add/update**  
Service tests: happy-path create works; invalid input mapped to expected error.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.4.2 — Add Season service: duplicate handling

**Why this step exists**  
Ensures duplicates are handled deterministically and consistently.

**Layer**  
Service

**Files likely touched**  
src/services/season*, tests/unit/services/

**Tests to add/update**  
Service tests: duplicate create yields expected error result.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.5.1 — Add Season API read schema

**Why this step exists**  
Creates stable API representation decoupled from ORM details.

**Layer**  
API

**Files likely touched**  
src/schemas/season*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: serialization includes expected fields and types.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.3.5.2 — Add Season API create schema

**Why this step exists**  
Defines validated inputs for create operations (even if endpoints come later).

**Layer**  
API

**Files likely touched**  
src/schemas/season*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: invalid inputs fail; valid inputs pass.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.5.4 Race

#### 1.5.4.1.1 — Define Race ORM model

**Why this step exists**  
Introduces the Race entity and locks invariants needed by ingestion.

**Layer**  
Model

**Files likely touched**  
src/models/race*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid Race creates; missing required fields fail.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.1.2 — Add Race identity uniqueness constraint

**Why this step exists**  
Prevents duplicate logical records by enforcing unique identity ((season_id, round)).

**Layer**  
Model

**Files likely touched**  
src/models/race*, tests/integration/db/

**Tests to add/update**  
Integration test: inserting duplicates fails deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.2.1 — Create migration for Race table

**Why this step exists**  
Persists schema for the entity with constraints matching the model.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: after upgrade, table exists and columns match expectations.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.2.2 — Add indexes for Race identity lookups

**Why this step exists**  
Ensures ingestion and lookups remain fast and predictable as data grows.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Schema test: expected indexes exist.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.3.1 — Add Race repository: create/get

**Why this step exists**  
Centralizes DB access and query logic in one boundary.

**Layer**  
Repository

**Files likely touched**  
src/repositories/race*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create + get-by-id; missing returns None.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.3.2 — Add Race repository: list ordering

**Why this step exists**  
Stabilizes list behavior for later API and ingestion audits.

**Layer**  
Repository

**Files likely touched**  
src/repositories/race*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: list order deterministic; limit/offset works.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.4.1 — Add Race service: create behavior

**Why this step exists**  
Moves business rules and error mapping out of API and into the service layer.

**Layer**  
Service

**Files likely touched**  
src/services/race*, tests/unit/services/

**Tests to add/update**  
Service tests: happy-path create works; invalid input mapped to expected error.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.4.2 — Add Race service: duplicate handling

**Why this step exists**  
Ensures duplicates are handled deterministically and consistently.

**Layer**  
Service

**Files likely touched**  
src/services/race*, tests/unit/services/

**Tests to add/update**  
Service tests: duplicate create yields expected error result.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.5.1 — Add Race API read schema

**Why this step exists**  
Creates stable API representation decoupled from ORM details.

**Layer**  
API

**Files likely touched**  
src/schemas/race*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: serialization includes expected fields and types.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.4.5.2 — Add Race API create schema

**Why this step exists**  
Defines validated inputs for create operations (even if endpoints come later).

**Layer**  
API

**Files likely touched**  
src/schemas/race*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: invalid inputs fail; valid inputs pass.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.5.5 Result

#### 1.5.5.1.1 — Define Result ORM model

**Why this step exists**  
Introduces the Result entity and locks invariants needed by ingestion.

**Layer**  
Model

**Files likely touched**  
src/models/result*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid Result creates; missing required fields fail.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.1.2 — Add Result identity uniqueness constraint

**Why this step exists**  
Prevents duplicate logical records by enforcing unique identity ((race_id, driver_id)).

**Layer**  
Model

**Files likely touched**  
src/models/result*, tests/integration/db/

**Tests to add/update**  
Integration test: inserting duplicates fails deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.2.1 — Create migration for Result table

**Why this step exists**  
Persists schema for the entity with constraints matching the model.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: after upgrade, table exists and columns match expectations.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.2.2 — Add indexes for Result identity lookups

**Why this step exists**  
Ensures ingestion and lookups remain fast and predictable as data grows.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Schema test: expected indexes exist.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.3.1 — Add Result repository: create/get

**Why this step exists**  
Centralizes DB access and query logic in one boundary.

**Layer**  
Repository

**Files likely touched**  
src/repositories/result*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create + get-by-id; missing returns None.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.3.2 — Add Result repository: list ordering

**Why this step exists**  
Stabilizes list behavior for later API and ingestion audits.

**Layer**  
Repository

**Files likely touched**  
src/repositories/result*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: list order deterministic; limit/offset works.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.4.1 — Add Result service: create behavior

**Why this step exists**  
Moves business rules and error mapping out of API and into the service layer.

**Layer**  
Service

**Files likely touched**  
src/services/result*, tests/unit/services/

**Tests to add/update**  
Service tests: happy-path create works; invalid input mapped to expected error.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.4.2 — Add Result service: duplicate handling

**Why this step exists**  
Ensures duplicates are handled deterministically and consistently.

**Layer**  
Service

**Files likely touched**  
src/services/result*, tests/unit/services/

**Tests to add/update**  
Service tests: duplicate create yields expected error result.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.5.1 — Add Result API read schema

**Why this step exists**  
Creates stable API representation decoupled from ORM details.

**Layer**  
API

**Files likely touched**  
src/schemas/result*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: serialization includes expected fields and types.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.5.5.5.2 — Add Result API create schema

**Why this step exists**  
Defines validated inputs for create operations (even if endpoints come later).

**Layer**  
API

**Files likely touched**  
src/schemas/result*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: invalid inputs fail; valid inputs pass.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S2 — Core persistence layer is usable

**Capabilities unlocked**
- Core entities exist (Driver, Constructor, Season, Race, Result)
- Migrations create core tables with constraints and indexes
- Repositories support create/get/list with deterministic ordering
- Services enforce duplicate handling deterministically
- Schemas exist for read/create inputs

**Invariants (must remain true going forward)**
- Core identity fields are enforced as uniqueness constraints
- Repository list order is deterministic (explicit ordering)
- Service duplicate handling is deterministic and tested
- Migrations always have a smoke test

**Exit gate (must be proven by tests/commands)**
- Integration tests can persist and retrieve each core entity
- Duplicate identity insertion fails deterministically (service-level behavior)
- Upgrade-to-head migration test passes

**Artifacts produced**
- None


## 1.6 Provider adapters (Jolpica/Ergast-compatible)

#### 1.6.1.1 — Add provider config (base URL, format)

**Why this step exists**  
Centralizes base URL and response format expectations.

**Layer**  
Provider

**Files likely touched**  
src/provider/, tests/unit/provider/

**Tests to add/update**  
Tests: URL composition and JSON format selection are deterministic.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.6.1.2 — Add HTTP request wrapper (timeouts/retries)

**Why this step exists**  
Standardizes network behavior and failure classification.

**Layer**  
Provider

**Files likely touched**  
src/provider/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked 200 ok; mocked timeout becomes classified error; mocked non-200 handled.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.6.1.3 — Add rate-limit handling policy

**Why this step exists**  
Defines how 429/throttle is handled predictably.

**Layer**  
Provider

**Files likely touched**  
src/provider/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked rate-limit triggers backoff path and is recorded in report.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.6.1.4 — Add response envelope parser/validator (MRData)

**Why this step exists**  
Ensures the Ergast-style envelope is present before normalization.

**Layer**  
Provider

**Files likely touched**  
src/provider/, tests/unit/provider/

**Tests to add/update**  
Tests: invalid envelope yields parse error; valid envelope passes.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.6.1.5 — Add pagination collector (generic)

**Why this step exists**  
Many endpoints page; a generic collector avoids duplication.

**Layer**  
Provider

**Files likely touched**  
src/provider/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked multi-page responses collected in deterministic order.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 1.7 Ingestion pipelines (one season core)

### 1.7.1 drivers ingestion

#### 1.7.1.1.1 — Add adapter: fetch drivers

**Why this step exists**  
Creates a single responsibility function that fetches drivers records from the provider.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload returns expected raw record count; invalid envelope classified.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.1.1.2 — Add normalizer: drivers → Driver inputs

**Why this step exists**  
Separates external payload format from internal service inputs and applies deterministic parsing rules.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping test from raw record to normalized inputs; missing fields handled by policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.1.1.3 — Add persistence step: upsert drivers

**Why this step exists**  
Writes normalized records via service layer using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: running persistence twice yields identical DB state (counts + key fields).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.1.1.4 — Add per-family report counters

**Why this step exists**  
Tracks created/updated/skipped/warned counts per ingestion family for auditing.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed inputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.7.2 constructors ingestion

#### 1.7.2.1.1 — Add adapter: fetch constructors

**Why this step exists**  
Creates a single responsibility function that fetches constructors records from the provider.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload returns expected raw record count; invalid envelope classified.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.2.1.2 — Add normalizer: constructors → Constructor inputs

**Why this step exists**  
Separates external payload format from internal service inputs and applies deterministic parsing rules.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping test from raw record to normalized inputs; missing fields handled by policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.2.1.3 — Add persistence step: upsert constructors

**Why this step exists**  
Writes normalized records via service layer using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: running persistence twice yields identical DB state (counts + key fields).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.2.1.4 — Add per-family report counters

**Why this step exists**  
Tracks created/updated/skipped/warned counts per ingestion family for auditing.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed inputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.7.3 seasons ingestion

#### 1.7.3.1.1 — Add adapter: fetch seasons

**Why this step exists**  
Creates a single responsibility function that fetches seasons records from the provider.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload returns expected raw record count; invalid envelope classified.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.3.1.2 — Add normalizer: seasons → Season inputs

**Why this step exists**  
Separates external payload format from internal service inputs and applies deterministic parsing rules.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping test from raw record to normalized inputs; missing fields handled by policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.3.1.3 — Add persistence step: upsert seasons

**Why this step exists**  
Writes normalized records via service layer using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: running persistence twice yields identical DB state (counts + key fields).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.3.1.4 — Add per-family report counters

**Why this step exists**  
Tracks created/updated/skipped/warned counts per ingestion family for auditing.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed inputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.7.4 races ingestion

#### 1.7.4.1.1 — Add adapter: fetch races

**Why this step exists**  
Creates a single responsibility function that fetches races records from the provider.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload returns expected raw record count; invalid envelope classified.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.4.1.2 — Add normalizer: races → Race inputs

**Why this step exists**  
Separates external payload format from internal service inputs and applies deterministic parsing rules.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping test from raw record to normalized inputs; missing fields handled by policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.4.1.3 — Add persistence step: upsert races

**Why this step exists**  
Writes normalized records via service layer using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: running persistence twice yields identical DB state (counts + key fields).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.4.1.4 — Add per-family report counters

**Why this step exists**  
Tracks created/updated/skipped/warned counts per ingestion family for auditing.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed inputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 1.7.5 results ingestion

#### 1.7.5.1.1 — Add adapter: fetch results

**Why this step exists**  
Creates a single responsibility function that fetches results records from the provider.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload returns expected raw record count; invalid envelope classified.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.5.1.2 — Add normalizer: results → Result inputs

**Why this step exists**  
Separates external payload format from internal service inputs and applies deterministic parsing rules.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping test from raw record to normalized inputs; missing fields handled by policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.5.1.3 — Add persistence step: upsert results

**Why this step exists**  
Writes normalized records via service layer using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: running persistence twice yields identical DB state (counts + key fields).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.5.1.4 — Add per-family report counters

**Why this step exists**  
Tracks created/updated/skipped/warned counts per ingestion family for auditing.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed inputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.6.1 — Define ingestion config object (season, mode, artifacts path)

**Why this step exists**  
Establishes how ingestion is configured and where artifacts are written.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/config/, tests/unit/ingestion/

**Tests to add/update**  
Tests: defaults deterministic; config is serializable; invalid values rejected.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.6.2 — Define ingestion report schema (versioned)

**Why this step exists**  
Freezes report shape so automation and debugging are stable over time.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report contains required fields; stable ordering; schema version recorded.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.6.3 — Add one-season ingestion orchestrator

**Why this step exists**  
Defines ingestion order for a season and ensures dependencies are met.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/orchestrate/, tests/integration/ingestion/

**Tests to add/update**  
Integration test: ingest fixture_min_season and verify DB counts for each table.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.6.4 — Add season-scoped deterministic reload

**Why this step exists**  
Implements clear-and-reload for season-scoped fact tables to guarantee determinism.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/orchestrate/, tests/integration/ingestion/

**Tests to add/update**  
Tests: run ingestion twice and assert identical DB state snapshots.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.7.6.5 — Write ingestion artifact (JSON report)

**Why this step exists**  
Produces a stable artifact for debugging and auditing without relying on logs.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/artifacts/, tests/integration/artifacts/

**Tests to add/update**  
Tests: artifact is written to deterministic path and matches schema.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S3 — One-season ingestion is deterministic

**Capabilities unlocked**
- Provider wrapper exists with parsing, classification, pagination handling
- Adapters + normalizers + persistence steps exist for drivers/constructors/seasons/races/results
- One-season orchestration runs in a defined order
- Season-scoped deterministic reload is implemented
- Ingestion report is written as a JSON artifact

**Invariants (must remain true going forward)**
- Ingestion can be rerun to produce identical DB state for the same inputs
- Normalization rules are deterministic (stable parsing, stable ordering)
- Reports are versioned and stable (ordering, required fields)
- Fact tables follow the clear-and-reload per season strategy (until explicitly optimized)

**Exit gate (must be proven by tests/commands)**
- Run one-season ingest on fixture_min_season and assert expected row counts
- Rerun ingest and assert identical DB snapshot (counts + key fields)
- Validate ingestion report artifact schema and deterministic path naming

**Artifacts produced**
- artifacts/ingestion/<run_id>/report.json


## 1.8 Prediction baseline + API surface

#### 1.8.1.1 — Define prediction request schema

**Why this step exists**  
Freezes what inputs predictions accept (race_id or season+round).

**Layer**  
API

**Files likely touched**  
src/schemas/prediction*, tests/unit/schemas/

**Tests to add/update**  
Tests: validation rejects invalid inputs and accepts valid inputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.1.2 — Define prediction response schema

**Why this step exists**  
Freezes output shape so clients/tests exist before model sophistication.

**Layer**  
API

**Files likely touched**  
src/schemas/prediction*, tests/unit/schemas/

**Tests to add/update**  
Tests: probabilities exist; types correct; values within bounds.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.2.1 — Add predictions endpoint scaffold

**Why this step exists**  
Creates endpoint routing and wiring without committing to model internals.

**Layer**  
API

**Files likely touched**  
src/api/routes/, tests/api/

**Tests to add/update**  
Endpoint tests: returns 200 for a known race in fixture DB.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.2.2 — Return deterministic placeholder predictions

**Why this step exists**  
Enables end-to-end tests while baseline model is built.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/, tests/api/

**Tests to add/update**  
Tests: repeated calls produce identical outputs for same input.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.3.1 — Add dataset extraction (past results only)

**Why this step exists**  
Defines exactly what historical rows are used to compute signals for a race.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/data/, tests/unit/prediction/

**Tests to add/update**  
Tests: synthetic DB returns correct subset in correct order; no future data included.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.3.2 — Add feature: rolling points form

**Why this step exists**  
Adds an explainable driver form signal based on recent points.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: synthetic results produce expected rolling values deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.3.3 — Add feature: constructor strength proxy

**Why this step exists**  
Adds an explainable team strength signal.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: synthetic results produce expected team strength deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.4.1 — Combine features into driver scores

**Why this step exists**  
Produces one score per driver as input to probability conversion.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/scoring/, tests/unit/prediction/

**Tests to add/update**  
Tests: expected ranking on a hand-constructed fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.4.2 — Convert scores to probabilities (invariants)

**Why this step exists**  
Transforms scores into valid probabilities usable for simulation.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/probabilities/, tests/unit/prediction/

**Tests to add/update**  
Tests: sum to 1 within tolerance; all in [0,1].

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.4.3 — Add tie-break determinism policy

**Why this step exists**  
Prevents equal-score instability across runs.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/scoring/, tests/unit/prediction/

**Tests to add/update**  
Tests: equal-score fixture yields stable ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.8.5.1 — Wire baseline model into predictions endpoint

**Why this step exists**  
Replaces placeholder output with baseline outputs while keeping schema stable.

**Layer**  
API

**Files likely touched**  
src/api/routes/, tests/api/

**Tests to add/update**  
Update endpoint tests to validate real model invariants.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S4 — Baseline predictions are available and schema-stable

**Capabilities unlocked**
- Prediction request/response schemas are defined
- Predictions endpoint exists and returns deterministic outputs
- Baseline features + scoring + probability conversion implemented
- Tie-break determinism is defined and tested

**Invariants (must remain true going forward)**
- Probabilities always sum to 1 within tolerance
- Outputs are deterministic for identical inputs and DB state
- Feature extraction uses only past data for the target race
- Schema remains stable for clients and the future UI

**Exit gate (must be proven by tests/commands)**
- Call predictions endpoint twice for same input and compare outputs
- Assert probability distribution invariants (sum-to-1, bounds)
- Assert tie-score ordering is deterministic

**Artifacts produced**
- None


## 1.9 Backtesting + simulation (leak-free)

#### 1.9.1.1 — Define backtesting split rules (no leakage)

**Why this step exists**  
Locks rule: predicting race N may only use data from races < N.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/backtest/, tests/unit/eval/

**Tests to add/update**  
Tests: intentional future-data fixture fails leakage check.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.9.1.2 — Add backtesting harness entrypoint

**Why this step exists**  
Creates repeatable chronological evaluation runner.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/backtest/, tests/integration/eval/

**Tests to add/update**  
Tests: harness runs over fixture_min_season and returns structured outputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.9.2.1 — Define simulation contract (championship probabilities)

**Why this step exists**  
Freezes output shape and reproducibility requirements for simulator.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/sim/, tests/unit/eval/

**Tests to add/update**  
Tests: same inputs produce identical outputs.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.9.2.2 — Implement Monte Carlo championship simulation

**Why this step exists**  
Simulates season outcomes using race probability distributions.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/sim/, tests/integration/eval/

**Tests to add/update**  
Tests: title probabilities sum to 1; determinism under fixed seed policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.9.2.3 — Add simulation guardrails (max iterations)

**Why this step exists**  
Prevents accidental huge compute during dev/tests.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/sim/, tests/unit/eval/

**Tests to add/update**  
Tests: invalid iteration counts rejected deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.9.3.1 — Write backtest artifact (JSON)

**Why this step exists**  
Produces a stable artifact for evaluation runs.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/artifacts/, tests/integration/artifacts/

**Tests to add/update**  
Tests: artifact written to deterministic path and matches schema.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S5 — Simulation + backtesting are proven leak-free (v1 complete)

**Capabilities unlocked**
- Backtesting harness runs chronologically
- Leakage checks enforce past-only usage
- Monte Carlo championship simulation produces title probabilities
- Backtest artifact writing exists

**Invariants (must remain true going forward)**
- Backtesting never uses future data (enforced by tests)
- Simulation outputs remain probability-valid and deterministic
- Artifacts remain schema-versioned and deterministic

**Exit gate (must be proven by tests/commands)**
- v1 gate tests all pass (ingest, predict, simulate, no-leakage)
- Backtest run produces a valid artifact schema

**Artifacts produced**
- artifacts/backtest/<run_id>/backtest.json


## 1.10 v1 Gate — Definition of done checks

#### 1.10.1.1 — Add v1 gate test: one-season ingest succeeds

**Why this step exists**  
Makes the v1 ingestion capability executable proof.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Integration test that runs ingestion over fixture_min_season and asserts DB state + report schema.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.10.1.2 — Add v1 gate test: predictions endpoint deterministic

**Why this step exists**  
Proves predictions are stable and schema-valid for a fixed input.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
API test calling predictions twice and comparing responses.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.10.1.3 — Add v1 gate test: simulation probabilities valid

**Why this step exists**  
Proves simulation outputs are well-formed and stable.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Integration test asserting probabilities sum to 1 and are deterministic.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 1.10.1.4 — Add v1 gate test: no leakage enforced

**Why this step exists**  
Proves backtesting isolation rules are active and tested.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Test that fails on intentional leakage attempt.

**Verify**
```
./.venv/bin/python -m pytest -q
```


# Version 2 — Full Historical Coverage

Goal: Ingest **all seasons** deterministically, handle pagination and edge cases, and produce robust reports/audits.

---

## 2.1 Season enumeration + multi-season orchestration

#### 2.1.1.1 — Add season enumeration via provider

**Why this step exists**  
Discovers available seasons using the provider and ensures deterministic ordering.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked seasons payload yields sorted list deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.1.1.2 — Add season range selection (start/end)

**Why this step exists**  
Allows partial multi-season runs while keeping the contract explicit.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/config/, tests/unit/ingestion/

**Tests to add/update**  
Tests: selecting a range yields correct list.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.1.2.1 — Add multi-season orchestrator

**Why this step exists**  
Runs one-season ingestion repeatedly across a season list.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/orchestrate/, tests/integration/ingestion/

**Tests to add/update**  
Integration test: ingest two seasons using fixtures and assert stable state.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.1.2.2 — Add resumable checkpoints per season

**Why this step exists**  
Allows resuming after failure without redoing completed seasons.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/orchestrate/, tests/integration/ingestion/

**Tests to add/update**  
Tests: simulate failure at season K; resume completes; final state matches fresh run.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.1.3.1 — Add per-season artifact bundle

**Why this step exists**  
Stores per-season reports under deterministic paths for debugging.

**Layer**  
Ops

**Files likely touched**  
artifacts/, tests/integration/artifacts/

**Tests to add/update**  
Tests: artifact directory structure deterministic; files exist.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.1.3.2 — Add global multi-season summary artifact

**Why this step exists**  
Summarizes totals across seasons for auditing and automation.

**Layer**  
Ops

**Files likely touched**  
artifacts/, tests/integration/artifacts/

**Tests to add/update**  
Tests: global totals match sum of per-season totals deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 2.2 Data quality, audits, and edge cases

#### 2.2.1.1 — Add audit: row counts per season (core tables)

**Why this step exists**  
Catches partial ingests and anomalies quickly.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/audit/, tests/unit/ingestion/

**Tests to add/update**  
Tests: audit output deterministic on fixture seasons.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.2.1.2 — Add audit: referential integrity checks

**Why this step exists**  
Ensures results link to existing drivers/constructors/races.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/audit/, tests/unit/ingestion/

**Tests to add/update**  
Tests: invalid reference fixture produces deterministic failures.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.2.2.1 — Add policy: DNF/NC and missing positions

**Why this step exists**  
Handles historical anomalies without breaking ingestion determinism.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: DNF/missing position fixtures normalize consistently.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.2.2.2 — Add policy: sprint-era data handling (minimal)

**Why this step exists**  
Prevents sprint-era shapes from corrupting race results (policy first).

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/policy/, tests/unit/ingestion/

**Tests to add/update**  
Tests: sprint fixture does not violate invariants; policy deterministic.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 2.3 Provider pagination and throughput policy

#### 2.3.1.1 — Extend pagination collector to all endpoint adapters

**Why this step exists**  
Ensures all paged endpoints return complete datasets deterministically.

**Layer**  
Provider

**Files likely touched**  
src/provider/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked multi-page responses fully collected for at least two endpoints.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.3.1.2 — Add per-endpoint page size policy

**Why this step exists**  
Keeps request sequence stable and minimizes calls within limits.

**Layer**  
Provider

**Files likely touched**  
src/provider/, tests/unit/provider/

**Tests to add/update**  
Tests: page size applied consistently; deterministic request ordering under mocks.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.3.2.1 — Add courteous delay enforcement in multi-season loops

**Why this step exists**  
Protects the API service and reduces throttle risk.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/orchestrate/, tests/unit/ingestion/

**Tests to add/update**  
Tests: delay invoked per policy using time mocks.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S7 — Multi-season ingestion is reliable (v2 complete)

**Capabilities unlocked**
- Season enumeration and range selection exist
- Multi-season orchestrator runs across season lists
- Resumable checkpoints work across failures
- Global summary artifacts and audits exist

**Invariants (must remain true going forward)**
- Multi-season runs are deterministic for identical mocked inputs
- Artifacts are written under deterministic paths
- Audits remain deterministic and schema-stable

**Exit gate (must be proven by tests/commands)**
- v2 gate tests pass: multi-season reruns match DB snapshots
- Audit and summary artifacts validate against schema and stable totals

**Artifacts produced**
- artifacts/ingestion/<run_id>/summary.json
- artifacts/ingestion/<run_id>/audits.json


## 2.4 v2 Gate — Definition of done checks

#### 2.4.1.1 — Add v2 gate test: multi-season ingest deterministic

**Why this step exists**  
Proves multi-season runs complete and reruns match state.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Integration test ingesting two fixture seasons twice and comparing DB snapshots.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 2.4.1.2 — Add v2 gate test: audits produced and stable

**Why this step exists**  
Proves audits and summary artifacts exist and are deterministic.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Test asserting audit artifact schemas and stable totals.

**Verify**
```
./.venv/bin/python -m pytest -q
```


# Version 3 — Credible Predictions (Evaluation + Calibration)

Goal: Add richer explainable features, formal metrics, and calibration summaries; produce stable evaluation artifacts.

---

## 3.1 Extended entities for enriched data (Circuit, Qualifying, Laps, PitStops, Standings)

### 3.1.1 Circuit

#### 3.1.1.1.1 — Define Circuit ORM model

**Why this step exists**  
Adds Circuit persistence so enriched ingestion can store it reliably.

**Layer**  
Model

**Files likely touched**  
src/models/circuit*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid create; required fields; identity constraints.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.1.2.1 — Create migration for Circuit table

**Why this step exists**  
Persists schema for enriched data.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: table exists after upgrade; FKs as expected.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.1.3.1 — Add Circuit repository basics

**Why this step exists**  
Centralizes DB queries and upserts for enriched entities.

**Layer**  
Repository

**Files likely touched**  
src/repositories/circuit*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create/get/list behavior; deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.1.4.1 — Add Circuit service basics

**Why this step exists**  
Provides a consistent business boundary and error mapping.

**Layer**  
Service

**Files likely touched**  
src/services/circuit*, tests/unit/services/

**Tests to add/update**  
Service tests: happy path; duplicate policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.1.2 QualifyingResult

#### 3.1.2.1.1 — Define QualifyingResult ORM model

**Why this step exists**  
Adds QualifyingResult persistence so enriched ingestion can store it reliably.

**Layer**  
Model

**Files likely touched**  
src/models/qualifyingresult*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid create; required fields; identity constraints.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.2.2.1 — Create migration for QualifyingResult table

**Why this step exists**  
Persists schema for enriched data.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: table exists after upgrade; FKs as expected.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.2.3.1 — Add QualifyingResult repository basics

**Why this step exists**  
Centralizes DB queries and upserts for enriched entities.

**Layer**  
Repository

**Files likely touched**  
src/repositories/qualifyingresult*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create/get/list behavior; deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.2.4.1 — Add QualifyingResult service basics

**Why this step exists**  
Provides a consistent business boundary and error mapping.

**Layer**  
Service

**Files likely touched**  
src/services/qualifyingresult*, tests/unit/services/

**Tests to add/update**  
Service tests: happy path; duplicate policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.1.3 Lap

#### 3.1.3.1.1 — Define Lap ORM model

**Why this step exists**  
Adds Lap persistence so enriched ingestion can store it reliably.

**Layer**  
Model

**Files likely touched**  
src/models/lap*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid create; required fields; identity constraints.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.3.2.1 — Create migration for Lap table

**Why this step exists**  
Persists schema for enriched data.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: table exists after upgrade; FKs as expected.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.3.3.1 — Add Lap repository basics

**Why this step exists**  
Centralizes DB queries and upserts for enriched entities.

**Layer**  
Repository

**Files likely touched**  
src/repositories/lap*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create/get/list behavior; deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.3.4.1 — Add Lap service basics

**Why this step exists**  
Provides a consistent business boundary and error mapping.

**Layer**  
Service

**Files likely touched**  
src/services/lap*, tests/unit/services/

**Tests to add/update**  
Service tests: happy path; duplicate policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.1.4 PitStop

#### 3.1.4.1.1 — Define PitStop ORM model

**Why this step exists**  
Adds PitStop persistence so enriched ingestion can store it reliably.

**Layer**  
Model

**Files likely touched**  
src/models/pitstop*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid create; required fields; identity constraints.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.4.2.1 — Create migration for PitStop table

**Why this step exists**  
Persists schema for enriched data.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: table exists after upgrade; FKs as expected.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.4.3.1 — Add PitStop repository basics

**Why this step exists**  
Centralizes DB queries and upserts for enriched entities.

**Layer**  
Repository

**Files likely touched**  
src/repositories/pitstop*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create/get/list behavior; deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.4.4.1 — Add PitStop service basics

**Why this step exists**  
Provides a consistent business boundary and error mapping.

**Layer**  
Service

**Files likely touched**  
src/services/pitstop*, tests/unit/services/

**Tests to add/update**  
Service tests: happy path; duplicate policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.1.5 DriverStanding

#### 3.1.5.1.1 — Define DriverStanding ORM model

**Why this step exists**  
Adds DriverStanding persistence so enriched ingestion can store it reliably.

**Layer**  
Model

**Files likely touched**  
src/models/driverstanding*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid create; required fields; identity constraints.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.5.2.1 — Create migration for DriverStanding table

**Why this step exists**  
Persists schema for enriched data.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: table exists after upgrade; FKs as expected.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.5.3.1 — Add DriverStanding repository basics

**Why this step exists**  
Centralizes DB queries and upserts for enriched entities.

**Layer**  
Repository

**Files likely touched**  
src/repositories/driverstanding*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create/get/list behavior; deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.5.4.1 — Add DriverStanding service basics

**Why this step exists**  
Provides a consistent business boundary and error mapping.

**Layer**  
Service

**Files likely touched**  
src/services/driverstanding*, tests/unit/services/

**Tests to add/update**  
Service tests: happy path; duplicate policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.1.6 ConstructorStanding

#### 3.1.6.1.1 — Define ConstructorStanding ORM model

**Why this step exists**  
Adds ConstructorStanding persistence so enriched ingestion can store it reliably.

**Layer**  
Model

**Files likely touched**  
src/models/constructorstanding*, tests/unit/models/

**Tests to add/update**  
Unit tests: valid create; required fields; identity constraints.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.6.2.1 — Create migration for ConstructorStanding table

**Why this step exists**  
Persists schema for enriched data.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: table exists after upgrade; FKs as expected.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.6.3.1 — Add ConstructorStanding repository basics

**Why this step exists**  
Centralizes DB queries and upserts for enriched entities.

**Layer**  
Repository

**Files likely touched**  
src/repositories/constructorstanding*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create/get/list behavior; deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.1.6.4.1 — Add ConstructorStanding service basics

**Why this step exists**  
Provides a consistent business boundary and error mapping.

**Layer**  
Service

**Files likely touched**  
src/services/constructorstanding*, tests/unit/services/

**Tests to add/update**  
Service tests: happy path; duplicate policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 3.2 Enriched ingestion endpoints and pipelines

### 3.2.1 circuits ingestion

#### 3.2.1.1.1 — Add adapter: fetch circuits

**Why this step exists**  
Adds provider adapter for circuits endpoint family.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload parses to raw records; pagination handled if applicable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.1.1.2 — Add normalizer: circuits → Circuit inputs

**Why this step exists**  
Creates deterministic mapping from provider payload to internal inputs and applies missing-field policy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping tests for required fields; deterministic parsing of optional fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.1.1.3 — Add persistence: upsert circuits records

**Why this step exists**  
Writes normalized enriched records using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: rerun persistence yields stable DB counts and key fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.1.1.4 — Add report counters for circuits

**Why this step exists**  
Makes enriched ingestion auditable.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed input.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.2.2 qualifying ingestion

#### 3.2.2.1.1 — Add adapter: fetch qualifying

**Why this step exists**  
Adds provider adapter for qualifying endpoint family.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload parses to raw records; pagination handled if applicable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.2.1.2 — Add normalizer: qualifying → QualifyingResult inputs

**Why this step exists**  
Creates deterministic mapping from provider payload to internal inputs and applies missing-field policy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping tests for required fields; deterministic parsing of optional fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.2.1.3 — Add persistence: upsert qualifying records

**Why this step exists**  
Writes normalized enriched records using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: rerun persistence yields stable DB counts and key fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.2.1.4 — Add report counters for qualifying

**Why this step exists**  
Makes enriched ingestion auditable.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed input.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.2.3 driverStandings ingestion

#### 3.2.3.1.1 — Add adapter: fetch driverStandings

**Why this step exists**  
Adds provider adapter for driverStandings endpoint family.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload parses to raw records; pagination handled if applicable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.3.1.2 — Add normalizer: driverStandings → DriverStanding inputs

**Why this step exists**  
Creates deterministic mapping from provider payload to internal inputs and applies missing-field policy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping tests for required fields; deterministic parsing of optional fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.3.1.3 — Add persistence: upsert driverStandings records

**Why this step exists**  
Writes normalized enriched records using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: rerun persistence yields stable DB counts and key fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.3.1.4 — Add report counters for driverStandings

**Why this step exists**  
Makes enriched ingestion auditable.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed input.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.2.4 constructorStandings ingestion

#### 3.2.4.1.1 — Add adapter: fetch constructorStandings

**Why this step exists**  
Adds provider adapter for constructorStandings endpoint family.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload parses to raw records; pagination handled if applicable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.4.1.2 — Add normalizer: constructorStandings → ConstructorStanding inputs

**Why this step exists**  
Creates deterministic mapping from provider payload to internal inputs and applies missing-field policy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping tests for required fields; deterministic parsing of optional fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.4.1.3 — Add persistence: upsert constructorStandings records

**Why this step exists**  
Writes normalized enriched records using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: rerun persistence yields stable DB counts and key fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.4.1.4 — Add report counters for constructorStandings

**Why this step exists**  
Makes enriched ingestion auditable.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed input.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.2.5 laps ingestion

#### 3.2.5.1.1 — Add adapter: fetch laps

**Why this step exists**  
Adds provider adapter for laps endpoint family.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload parses to raw records; pagination handled if applicable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.5.1.2 — Add normalizer: laps → Lap inputs

**Why this step exists**  
Creates deterministic mapping from provider payload to internal inputs and applies missing-field policy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping tests for required fields; deterministic parsing of optional fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.5.1.3 — Add persistence: upsert laps records

**Why this step exists**  
Writes normalized enriched records using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: rerun persistence yields stable DB counts and key fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.5.1.4 — Add report counters for laps

**Why this step exists**  
Makes enriched ingestion auditable.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed input.

**Verify**
```
./.venv/bin/python -m pytest -q
```


### 3.2.6 pitstops ingestion

#### 3.2.6.1.1 — Add adapter: fetch pitstops

**Why this step exists**  
Adds provider adapter for pitstops endpoint family.

**Layer**  
Provider

**Files likely touched**  
src/provider/endpoints/, tests/unit/provider/

**Tests to add/update**  
Tests: mocked payload parses to raw records; pagination handled if applicable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.6.1.2 — Add normalizer: pitstops → PitStop inputs

**Why this step exists**  
Creates deterministic mapping from provider payload to internal inputs and applies missing-field policy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/normalize/, tests/unit/ingestion/

**Tests to add/update**  
Tests: mapping tests for required fields; deterministic parsing of optional fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.6.1.3 — Add persistence: upsert pitstops records

**Why this step exists**  
Writes normalized enriched records using the persistence strategy.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/persist/, tests/integration/ingestion/

**Tests to add/update**  
Tests: rerun persistence yields stable DB counts and key fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.2.6.1.4 — Add report counters for pitstops

**Why this step exists**  
Makes enriched ingestion auditable.

**Layer**  
Ingestion

**Files likely touched**  
src/ingestion/report/, tests/unit/ingestion/

**Tests to add/update**  
Tests: report counters deterministic for fixed input.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 3.3 Feature engineering expansion

#### 3.3.1.1 — Add feature: finishing position trend

**Why this step exists**  
Adds robust driver form signal beyond points.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: synthetic fixture yields expected trend values deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.3.1.2 — Add feature: constructor reliability proxy

**Why this step exists**  
Adds stability signal using DNFs/finishes.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: fixture yields expected reliability values deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.3.1.3 — Add feature: qualifying performance signal

**Why this step exists**  
Uses qualifying results as an explainable predictor for race outcomes.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: fixture with qualifying changes feature values deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.3.1.4 — Add feature: pitstop tendency proxy

**Why this step exists**  
Uses pitstop frequency/duration as strategy/reliability proxy.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: synthetic pitstop fixture yields expected feature values.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.3.1.5 — Add feature: circuit familiarity placeholder

**Why this step exists**  
Adds circuit-level representation with explicit fallback rules.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: circuit encoding deterministic; missing circuit handled by policy.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.3.2.1 — Add feature registry (stable ordering)

**Why this step exists**  
Makes model inputs auditable and comparable across runs.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/features/, tests/unit/prediction/

**Tests to add/update**  
Tests: registry lists expected features in stable order.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 3.4 Evaluation metrics and calibration

#### 3.4.1.1 — Add metric: log loss

**Why this step exists**  
Measures probabilistic accuracy in a standard way.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/metrics/, tests/unit/eval/

**Tests to add/update**  
Tests: compute on tiny hand-checkable fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.4.1.2 — Add metric: Brier score

**Why this step exists**  
Measures calibration-friendly probabilistic error.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/metrics/, tests/unit/eval/

**Tests to add/update**  
Tests: compute on tiny hand-checkable fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.4.1.3 — Add metrics report schema + artifact writer

**Why this step exists**  
Freezes evaluation artifact shape and makes results reviewable.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/artifacts/, tests/integration/artifacts/

**Tests to add/update**  
Tests: artifact schema validated; deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.4.2.1 — Add calibration sanity checks (finite outputs)

**Why this step exists**  
Prevents broken probability math from shipping.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/calibration/, tests/unit/eval/

**Tests to add/update**  
Tests: invalid inputs produce clear failure; outputs always finite.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.4.2.2 — Add calibration bucket summary

**Why this step exists**  
Summarizes predicted vs observed frequencies in bins for diagnosis.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/calibration/, tests/unit/eval/

**Tests to add/update**  
Tests: bin assignment deterministic; summary stable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.4.2.3 — Add calibration regression test on fixed fixture

**Why this step exists**  
Locks calibration behavior so refactors don’t silently degrade outputs.

**Layer**  
Tests

**Files likely touched**  
tests/fixtures/, tests/gates/

**Tests to add/update**  
Tests: compare bucket summary to expected within tolerance.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 3.5 v3 Gate — Definition of done checks

#### 3.5.1.1 — Add v3 gate: metrics artifact produced

**Why this step exists**  
Proves evaluation produces stable metrics output.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Integration test that runs backtest on fixture and asserts artifact schema + stable fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 3.5.1.2 — Add v3 gate: calibration summary stable

**Why this step exists**  
Proves calibration bucket summary exists and is stable.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Test comparing calibration summary against expected fixture output.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S10 — Credible prediction evaluation exists (v3 complete)

**Capabilities unlocked**
- Enriched entities and ingestion pipelines exist (circuits/qualifying/laps/pitstops/standings)
- Expanded feature set exists and is registry-tracked
- Metrics (log loss, Brier) and evaluation artifacts exist
- Calibration summaries and regression checks exist

**Invariants (must remain true going forward)**
- Evaluation outputs are deterministic on fixed fixtures
- Calibration summaries remain stable within tolerance
- Feature registry ordering is stable and tested

**Exit gate (must be proven by tests/commands)**
- v3 gate tests pass: metrics artifact produced and schema-valid
- Calibration bucket summary matches expected fixture outputs (tolerance)

**Artifacts produced**
- artifacts/metrics/<run_id>/metrics.json
- artifacts/metrics/<run_id>/calibration.json


# Version 4 — Operational Platform (Tasks, Observability, CI)

Goal: Make the system run like a service: non-blocking task execution, observability, and CI gates.

---

## 4.1 Task execution model

#### 4.1.1.1 — Add Task ORM model (status, timestamps, artifacts)

**Why this step exists**  
Introduces a durable representation of long-running jobs (ingest/backtest).

**Layer**  
Model

**Files likely touched**  
src/models/task*, tests/unit/models/

**Tests to add/update**  
Tests: create task row; validate status transitions.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.1.1.2 — Add migration for Task table

**Why this step exists**  
Persists task tracking in the database.

**Layer**  
Migration

**Files likely touched**  
migrations/, tests/migrations/

**Tests to add/update**  
Migration test: task table exists and columns match expectations.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.1.2.1 — Add Task repository

**Why this step exists**  
Centralizes task persistence and retrieval.

**Layer**  
Repository

**Files likely touched**  
src/repositories/task*, tests/unit/repositories/

**Tests to add/update**  
Repo tests: create/get/list; deterministic ordering by created time/id.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.1.2.2 — Add Task service

**Why this step exists**  
Defines lifecycle operations for tasks (queued→running→done/failed).

**Layer**  
Service

**Files likely touched**  
src/services/task*, tests/unit/services/

**Tests to add/update**  
Service tests: lifecycle transitions and error mapping deterministic.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.1.3.1 — Add ingestion task runner wrapper

**Why this step exists**  
Runs ingestion as a task without blocking API calls.

**Layer**  
Ops

**Files likely touched**  
src/ops/tasks/, tests/integration/ops/

**Tests to add/update**  
Tests: task transitions on success/failure; artifacts recorded.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.1.3.2 — Add backtest task runner wrapper

**Why this step exists**  
Runs backtests as tasks and records metrics artifacts.

**Layer**  
Ops

**Files likely touched**  
src/ops/tasks/, tests/integration/ops/

**Tests to add/update**  
Tests: metrics artifact path recorded; stable completion states.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.1.4.1 — Add endpoint selection for ingestion tasks

**Why this step exists**  
Allows running core-only vs enriched endpoint families for ingestion.

**Layer**  
Ops

**Files likely touched**  
src/ops/tasks/, tests/integration/ops/

**Tests to add/update**  
Tests: runner respects selection; report records selected families.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 4.2 Operational API endpoints

#### 4.2.1.1 — Add /api/v1/tasks list endpoint

**Why this step exists**  
Exposes job history for operational visibility.

**Layer**  
API

**Files likely touched**  
src/api/routes/tasks*, tests/api/

**Tests to add/update**  
API tests: list returns ordered tasks; pagination works.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.2.1.2 — Add /api/v1/tasks/{id} detail endpoint

**Why this step exists**  
Allows inspecting a job and its artifacts.

**Layer**  
API

**Files likely touched**  
src/api/routes/tasks*, tests/api/

**Tests to add/update**  
API tests: existing returns 200; missing returns 404 with standard error shape.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.2.2.1 — Add /api/v1/ingest start endpoint

**Why this step exists**  
Starts ingestion as a non-blocking task and returns a task id.

**Layer**  
API

**Files likely touched**  
src/api/routes/ingest*, tests/api/

**Tests to add/update**  
API tests: starts task; does not block; task stored.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.2.2.2 — Add /api/v1/backtest start endpoint

**Why this step exists**  
Starts backtest as a non-blocking task and returns a task id.

**Layer**  
API

**Files likely touched**  
src/api/routes/backtest*, tests/api/

**Tests to add/update**  
API tests: starts task; parameters validated; task stored.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 4.3 Observability and artifacts hygiene

#### 4.3.1.1 — Add structured logging fields (request_id, task_id)

**Why this step exists**  
Makes logs correlatable across API requests and background jobs.

**Layer**  
Ops

**Files likely touched**  
src/ops/logging*, tests/unit/ops/

**Tests to add/update**  
Tests: log records include expected keys for a sample request/task.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.3.1.2 — Add minimal runtime info endpoint (/api/v1/metrics)

**Why this step exists**  
Provides basic operational insight (build/version, uptime, last task status).

**Layer**  
API

**Files likely touched**  
src/api/routes/metrics*, tests/api/

**Tests to add/update**  
API tests: endpoint returns expected keys and types.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.3.2.1 — Add artifact directory policy + cleanup rules

**Why this step exists**  
Prevents artifact sprawl and keeps storage predictable.

**Layer**  
Ops

**Files likely touched**  
src/ops/artifacts*, tests/unit/ops/

**Tests to add/update**  
Tests: deterministic artifact paths; cleanup policy enforceable in dry-run.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.3.2.2 — Add artifact bundling for enriched ingestion runs

**Why this step exists**  
Stores per-endpoint/per-season reports in predictable structure.

**Layer**  
Ops

**Files likely touched**  
src/ops/artifacts*, tests/integration/ops/

**Tests to add/update**  
Tests: bundling yields deterministic directory tree and references stored on Task.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 4.4 Continuous integration gates

#### 4.4.1.1 — Add CI workflow: run tests on push

**Why this step exists**  
Ensures regressions are caught immediately in a clean environment.

**Layer**  
Ops

**Files likely touched**  
.github/workflows/, tests/

**Tests to add/update**  
Verify by running the same pytest command in CI.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.4.1.2 — Add CI workflow: migrations smoke check

**Why this step exists**  
Prevents broken migrations from being merged.

**Layer**  
Ops

**Files likely touched**  
.github/workflows/, tests/migrations/

**Tests to add/update**  
CI runs upgrade-to-head smoke test.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.4.2.1 — Add CI artifact upload for test reports (optional)

**Why this step exists**  
Preserves debugging context for failing CI runs.

**Layer**  
Ops

**Files likely touched**  
.github/workflows/

**Tests to add/update**  
Verify CI produces and uploads a small report artifact.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 4.5 v4 Gate — Definition of done checks

#### 4.5.1.1 — Add v4 gate: ingestion runs as task

**Why this step exists**  
Proves ingestion can be started via API and completes as a task with artifacts.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Integration test starting ingestion task and polling stored status to completion (mocked).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 4.5.1.2 — Add v4 gate: backtest runs as task

**Why this step exists**  
Proves backtest runs as task and writes metrics artifact.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Integration test starting backtest task and asserting artifact schema.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S12 — Operational service behavior proven (v4 complete)

**Capabilities unlocked**
- Task model tracks ingestion/backtest jobs with lifecycle
- Operational endpoints start jobs and expose status and artifacts
- Structured logs include request_id/task_id correlation
- CI gates run tests + migration smoke checks

**Invariants (must remain true going forward)**
- API starts tasks non-blockingly (returns task id promptly)
- Task lifecycle is consistent and durable (queued→running→done/failed)
- Artifacts are discoverable from tasks and stored deterministically
- CI remains green for main branch

**Exit gate (must be proven by tests/commands)**
- v4 gate tests pass: ingestion and backtest run as tasks and produce artifacts
- Tasks list/detail endpoints show artifact pointers
- CI workflow runs pytest and migration smoke checks

**Artifacts produced**
- artifacts/tasks/<task_id>/... (bundled reports)


#### 4.5.1.3 — Add v4 gate: tasks endpoints expose artifacts

**Why this step exists**  
Proves operational endpoints surface task status and artifact pointers.

**Layer**  
Tests

**Files likely touched**  
tests/gates/, tests/api/

**Tests to add/update**  
API tests: list/detail include artifact references and stable fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---

# Version 5 — Decision Engine (Scenarios + Attribution)
Goal: Turn predictions into a decision-support tool by enabling counterfactual scenarios, comparisons, and explainable factor attribution. Keep everything deterministic and artifact-driven.

## 5.1 Scenario contract and data model

#### 5.1.1.1 — Define scenario request schema

**Why this step exists**  
Freezes inputs for a scenario run (target race, perturbations, simulation settings).

**Layer**  
API

**Files likely touched**  
src/schemas/scenario*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: invalid perturbations rejected; valid accepted.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.1.1.2 — Define scenario response schema

**Why this step exists**  
Freezes output shape for scenario results (baseline vs scenario, deltas).

**Layer**  
API

**Files likely touched**  
src/schemas/scenario*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: delta fields exist; probability invariants enforced.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.1.2.1 — Define perturbation types (versioned)

**Why this step exists**  
Creates a controlled vocabulary for scenario changes (qualifying shift, strength multiplier, weather proxy).

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/scenario*, tests/unit/prediction/

**Tests to add/update**  
Tests: perturbations serialize deterministically; ordering stable.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.1.2.2 — Add scenario config validation rules

**Why this step exists**  
Prevents nonsense scenarios (negative multipliers, invalid bounds) from producing misleading output.

**Layer**  
Service

**Files likely touched**  
src/services/scenario*, tests/unit/services/

**Tests to add/update**  
Tests: validation errors are deterministic and have stable error codes.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.1.3.1 — Add ScenarioRun artifact schema

**Why this step exists**  
Defines the artifact written for scenario runs (inputs, outputs, metadata).

**Layer**  
Ops

**Files likely touched**  
src/ops/artifacts*, tests/integration/artifacts/

**Tests to add/update**  
Tests: artifact schema required fields + stable ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 5.2 Baseline vs counterfactual execution

#### 5.2.1.1 — Add scenario runner skeleton

**Why this step exists**  
Creates the orchestration boundary for running baseline + counterfactual in one call.

**Layer**  
Service

**Files likely touched**  
src/services/scenario*, tests/unit/services/

**Tests to add/update**  
Unit test: runner returns structured empty output for stubbed model.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.2.1.2 — Implement baseline capture (no perturbations)

**Why this step exists**  
Ensures the scenario engine always records baseline outputs for comparison.

**Layer**  
Service

**Files likely touched**  
src/services/scenario*, tests/integration/scenario/

**Tests to add/update**  
Tests: baseline equals normal prediction outputs on fixture race.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.2.2.1 — Implement perturbation: qualifying position shift

**Why this step exists**  
Allows counterfactual adjustment based on qualifying (using v3 qualifying ingestion when present, fallback policy when absent).

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/scenario/perturbations*, tests/unit/prediction/

**Tests to add/update**  
Tests: fixture with qualifying shifts feature and changes output deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.2.2.2 — Implement perturbation: constructor strength multiplier

**Why this step exists**  
Enables scenario changes to team strength assumptions without retraining models.

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/scenario/perturbations*, tests/unit/prediction/

**Tests to add/update**  
Tests: applying multiplier changes outputs in expected direction deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.2.2.3 — Implement perturbation: weather proxy toggle (policy only)

**Why this step exists**  
Introduces a placeholder weather effect as a controlled perturbation type (explicitly labeled as proxy).

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/scenario/perturbations*, tests/unit/prediction/

**Tests to add/update**  
Tests: toggle yields deterministic difference; proxy clearly recorded in artifact.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.2.3.1 — Add scenario delta computation

**Why this step exists**  
Computes baseline vs scenario diffs (probability deltas, expected points deltas).

**Layer**  
Service

**Files likely touched**  
src/services/scenario*, tests/unit/services/

**Tests to add/update**  
Tests: delta math correct and deterministic on a small fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.2.4.1 — Write scenario artifact

**Why this step exists**  
Persists scenario runs for later inspection and UI consumption.

**Layer**  
Ops

**Files likely touched**  
src/ops/artifacts*, tests/integration/artifacts/

**Tests to add/update**  
Integration test: artifact path deterministic; schema valid; stable ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 5.3 Attribution and explanations

#### 5.3.1.1 — Define attribution output schema

**Why this step exists**  
Freezes what ‘explanation’ means (feature contributions, signed deltas, caveats).

**Layer**  
API

**Files likely touched**  
src/schemas/attribution*, tests/unit/schemas/

**Tests to add/update**  
Schema tests: contributions list stable ordering; includes caveat field.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.3.1.2 — Implement attribution: feature ablation deltas (baseline)

**Why this step exists**  
Explains predictions by re-running with features removed/neutralized and measuring deltas (deterministic).

**Layer**  
Model/Prediction

**Files likely touched**  
src/prediction/attribution*, tests/unit/prediction/

**Tests to add/update**  
Tests: ablation runner deterministic; contributions sum approximately to overall delta (within tolerance).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.3.2.1 — Add attribution caveats policy

**Why this step exists**  
Ensures explanations are labeled and don’t overclaim (especially for proxy perturbations).

**Layer**  
Service

**Files likely touched**  
src/services/attribution*, tests/unit/services/

**Tests to add/update**  
Tests: caveats included for proxy perturbations and for low-data cases.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.3.3.1 — Add /api/v1/scenario endpoint

**Why this step exists**  
Exposes scenario runs as an API capability for the UI.

**Layer**  
API

**Files likely touched**  
src/api/routes/scenario*, tests/api/

**Tests to add/update**  
API tests: endpoint returns schema-valid response; deterministic output on fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.3.3.2 — Add /api/v1/attribution endpoint

**Why this step exists**  
Exposes attribution/explanation output for a prediction (or scenario).

**Layer**  
API

**Files likely touched**  
src/api/routes/attribution*, tests/api/

**Tests to add/update**  
API tests: endpoint returns stable ordered contributions; deterministic on fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 5.4 v5 Gate — Definition of done checks

#### 5.4.1.1 — Add v5 gate: scenario run produces artifact

**Why this step exists**  
Proves scenario engine runs baseline+counterfactual and writes schema-valid artifact.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Gate test: run scenario on fixture race; validate artifact schema and deterministic path.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.4.1.2 — Add v5 gate: scenario deltas deterministic

**Why this step exists**  
Proves scenario outputs are reproducible on fixed fixtures.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Gate test: run same scenario twice; compare outputs and artifacts.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 5.4.1.3 — Add v5 gate: attribution output stable

**Why this step exists**  
Proves explanation output exists, ordered stably, and includes caveats.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Gate test: attribution endpoint output matches expected fixture (tolerance).

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S13 — Decision engine available (v5 complete)

**Capabilities unlocked**
- Scenario API exists and returns baseline vs counterfactual comparisons
- Scenario artifacts are written deterministically
- Attribution/explanation output exists with caveats

**Invariants (must remain true going forward)**
- Scenario outputs are deterministic for identical inputs and DB state
- Attribution output ordering is stable and caveats are present where needed
- All probability invariants remain enforced (sum-to-1, bounds)

**Exit gate (must be proven by tests/commands)**
- v5 gate tests pass (scenario artifact, deterministic deltas, attribution stability)

**Artifacts produced**
- artifacts/scenarios/<run_id>/scenario.json
- artifacts/scenarios/<run_id>/attribution.json


---

# Version 6 — Web UI (Single-Owner, No Programming Required)
Goal: Provide a website UI in a **separate repository** that lets a non-programmer operator run ingestion/backtests/scenarios and view results. Auth is **single-owner** (no multi-user).

## 6.1 Backend UI contract and single-owner auth

#### 6.1.1.1 — Define UI-facing API contract doc

**Why this step exists**  
Locks the minimal endpoints + response shapes the UI relies on, reducing churn.

**Layer**  
Docs

**Files likely touched**  
docs/ui_contract.md, tests/gates/

**Tests to add/update**  
Doc-sanity test: referenced endpoints exist; OpenAPI includes them.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 6.1.2.1 — Add AUTH_TOKEN setting (single-owner)

**Why this step exists**  
Introduces a single secret token used to protect operational endpoints.

**Layer**  
DB + API

**Files likely touched**  
src/settings*, tests/unit/

**Tests to add/update**  
Tests: settings require token in non-dev modes; deterministic default behavior in tests.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 6.1.2.2 — Add auth middleware (Bearer token)

**Why this step exists**  
Enforces Authorization header checks uniformly across protected routes.

**Layer**  
API

**Files likely touched**  
src/api/middleware*, tests/api/

**Tests to add/update**  
API tests: missing/invalid token returns 401 with standard error shape.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 6.1.2.3 — Whitelist public endpoints (health + OpenAPI)

**Why this step exists**  
Keeps basic diagnostics accessible while securing operations.

**Layer**  
API

**Files likely touched**  
src/api/middleware*, tests/api/

**Tests to add/update**  
API tests: /health accessible without token; /tasks requires token.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 6.1.3.1 — Add CORS configuration (dev)

**Why this step exists**  
Allows the separate frontend repo to call the API during development.

**Layer**  
API

**Files likely touched**  
src/api/app*, tests/api/

**Tests to add/update**  
API tests: CORS headers present for configured origins in dev/test config.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 6.1.4.1 — Add UI-ready error codes and messages (stabilize)

**Why this step exists**  
Ensures the UI can display clear errors without parsing ad-hoc text.

**Layer**  
API

**Files likely touched**  
src/api/errors*, tests/api/

**Tests to add/update**  
API tests: errors include code + message consistently.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 6.1.5.1 — Add artifacts listing endpoint

**Why this step exists**  
Allows the UI to discover available artifacts for a task/run (without direct filesystem access).

**Layer**  
API

**Files likely touched**  
src/api/routes/artifacts*, tests/api/

**Tests to add/update**  
API tests: listing returns deterministic ordering and stable metadata fields.

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S14 — UI integration contract stable (backend ready for UI)

**Capabilities unlocked**
- Single-owner auth protects operational endpoints
- CORS configured for dev UI
- Artifacts can be listed via API
- UI-facing contract documented

**Invariants (must remain true going forward)**
- All mutating/operational endpoints require Authorization header
- Error response shapes remain stable and machine-readable (code + message)
- Artifacts are exposed only via controlled metadata endpoints

**Exit gate (must be proven by tests/commands)**
- Auth tests pass (401/200 as expected)
- CORS headers verified for dev origin
- Artifacts list endpoint returns deterministic output on fixtures

**Artifacts produced**
- None

## 6.2 Frontend repository bootstrap (separate repo)

#### 6.2.1.1 — Create frontend repo scaffold (vanilla)

**Why this step exists**  
Starts a separate repo for the UI with a minimal, predictable file layout.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: index.html, src/, assets/

**Tests to add/update**  
None (frontend repo). Add a simple lint-free check: load index.html locally.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.2.1.2 — Add UI runbook (dev server options)

**Why this step exists**  
Documents how to run the UI locally without framework tooling assumptions.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: RUNBOOK.md

**Tests to add/update**  
None (doc-only).

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.2.2.1 — Add API client module (fetch wrapper)

**Why this step exists**  
Centralizes API calls, headers, base URL, and error handling in one place.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/api/client.js, tests/

**Tests to add/update**  
Frontend tests: mocked fetch returns expected parsed payload + error handling behavior.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.2.2.2 — Add auth token storage policy (single-owner)

**Why this step exists**  
Defines where the token lives (dev env file / localStorage) and how it is applied.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/state/auth.js, src/views/login.js

**Tests to add/update**  
Frontend tests: Authorization header attached; missing token prompts login view.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.2.3.1 — Add minimal router (hash-based)

**Why this step exists**  
Provides multi-page navigation without a framework (migration-friendly).

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/router/*

**Tests to add/update**  
Frontend tests: route changes render correct view modules.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.2.3.2 — Add shared UI components (status badge, table)

**Why this step exists**  
Creates reusable display primitives to avoid duplication across pages.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/components/*

**Tests to add/update**  
Frontend tests: components render expected DOM structure for sample inputs.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


## 6.3 UI pages for core operations

#### 6.3.1.1 — Add Dashboard page (system status)

**Why this step exists**  
Gives a non-dev operator a home screen: API reachable, last task, version info.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/dashboard.js

**Tests to add/update**  
Frontend tests: dashboard renders status values from mocked API.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.3.2.1 — Add Tasks page (list + filter)

**Why this step exists**  
Lets operator see job history and status at a glance.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/tasks.js

**Tests to add/update**  
Frontend tests: tasks list sorted deterministically; filters update view.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.3.2.2 — Add Task detail page (status + artifacts)

**Why this step exists**  
Lets operator inspect a single task, view logs pointers and artifact metadata.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/task_detail.js

**Tests to add/update**  
Frontend tests: detail renders artifacts list from mocked API.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.3.3.1 — Add Ingest page (start job)

**Why this step exists**  
Lets operator start ingestion with season range and endpoint selection.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/ingest.js

**Tests to add/update**  
Frontend tests: form validates inputs; submits start request; navigates to task detail.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.3.4.1 — Add Backtest page (start job + view metrics)

**Why this step exists**  
Lets operator run backtests and view summary metrics artifacts.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/backtest.js

**Tests to add/update**  
Frontend tests: start request; metrics view renders from mocked artifact metadata.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.3.5.1 — Add Predictions page (select race, view probabilities)

**Why this step exists**  
Lets operator query predictions without any programming knowledge.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/predictions.js

**Tests to add/update**  
Frontend tests: selection drives API call; probability table renders deterministically.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.3.6.1 — Add Scenario page (v5) baseline vs counterfactual compare

**Why this step exists**  
Lets operator run scenario comparisons and see deltas clearly.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/scenario.js

**Tests to add/update**  
Frontend tests: scenario results render; delta formatting stable.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.3.7.1 — Add Attribution page (v5) explanation view

**Why this step exists**  
Lets operator see ‘why’ a prediction/scenario changed.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/attribution.js

**Tests to add/update**  
Frontend tests: contributions list renders in stable order with caveats.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


## 6.4 UX hardening and migration-readiness

#### 6.4.1.1 — Add global loading + error handling UI

**Why this step exists**  
Prevents confusing blank screens and standardizes user feedback.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/components/*, src/state/*

**Tests to add/update**  
Frontend tests: loading and error states render for mocked failures.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.4.1.2 — Add artifact viewer (JSON pretty + download link)

**Why this step exists**  
Allows operator to inspect artifacts without shell access.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/artifact_viewer.js

**Tests to add/update**  
Frontend tests: viewer renders JSON with stable formatting; handles large artifacts gracefully.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.4.2.1 — Add UI contract test suite (mock server)

**Why this step exists**  
Locks the frontend assumptions against the API contract, easing future framework migration.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: tests/contract/*

**Tests to add/update**  
Frontend tests: contract tests run against mocked responses matching OpenAPI shapes.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.4.3.1 — Document migration plan to framework UI

**Why this step exists**  
Explicitly documents how to move to React/Svelte later without changing the backend contract.

**Layer**  
Docs

**Files likely touched**  
ui-repo: docs/migration_to_framework.md

**Tests to add/update**  
None (doc-only).

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 6.5 v6 Gate — Definition of done checks

#### 6.5.1.1 — Add v6 gate: UI can authenticate and call API

**Why this step exists**  
Proves a non-dev operator can log in (token) and reach protected endpoints.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: tests/gates/*

**Tests to add/update**  
Manual checklist + frontend test: authenticated API call succeeds; unauthenticated fails.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.5.1.2 — Add v6 gate: operator can start ingest/backtest and view task

**Why this step exists**  
Proves end-to-end UI workflows are usable.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: tests/gates/*

**Tests to add/update**  
Frontend test: start job → navigate to task detail → list artifacts (mocked).

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 6.5.1.3 — Add v6 gate: scenario + attribution pages function (v5)

**Why this step exists**  
Proves decision engine features are accessible to UI.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: tests/gates/*

**Tests to add/update**  
Frontend test: scenario + attribution render stable outputs from mocks.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```



---
### STATE S15 — Web UI usable by non-developer operator (v6 complete)

**Capabilities unlocked**
- Separate frontend repo exists and runs locally
- Operator can authenticate (single-owner)
- Operator can start ingestion/backtests and inspect tasks/artifacts
- Operator can view predictions, scenarios, and attribution explanations

**Invariants (must remain true going forward)**
- Frontend remains framework-migration-ready (router/components/state modular)
- Backend remains framework-agnostic and versioned
- Auth remains single-owner; no multi-user features creep in

**Exit gate (must be proven by tests/commands)**
- v6 gate checks pass (auth, workflows, scenario/attribution access)

**Artifacts produced**
- None


---

# Version 7 — Reproducible Training + Model Registry (Machine Learning Optionality)
Goal: Introduce machine-learning models **only** with strict reproducibility, evaluation gates, and model registry. The system must remain deterministic and backtest-driven.

## 7.1 Training contract and dataset artifacts

#### 7.1.1.1 — Define training dataset schema (versioned)

**Why this step exists**  
Freezes the structure of training examples derived from historical data.

**Layer**  
Evaluation

**Files likely touched**  
src/train/schema*, tests/unit/train/

**Tests to add/update**  
Schema tests: required fields + ordering; schema version recorded.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.1.1.2 — Add training dataset builder (extractor)

**Why this step exists**  
Creates deterministic extraction of features/labels from DB for training.

**Layer**  
Evaluation

**Files likely touched**  
src/train/build*, tests/integration/train/

**Tests to add/update**  
Tests: fixture dataset extracted deterministically (stable ordering, no leakage).

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.1.2.1 — Write training dataset artifact

**Why this step exists**  
Persists training data as an artifact for reproducibility and auditing.

**Layer**  
Ops

**Files likely touched**  
artifacts/train/<run_id>/dataset.jsonl, tests/integration/artifacts/

**Tests to add/update**  
Tests: artifact path deterministic; schema valid; stable row ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.1.3.1 — Add label definition doc (what is being predicted)

**Why this step exists**  
Prevents silent label drift (e.g., win vs podium vs points).

**Layer**  
Docs

**Files likely touched**  
docs/labels.md, tests/gates/

**Tests to add/update**  
Doc-sanity test: label version referenced by training code is present.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 7.2 Model registry and reproducibility controls

#### 7.2.1.1 — Define ModelSpec schema

**Why this step exists**  
Freezes how a model is described: algorithm, hyperparameters, feature set, training data version.

**Layer**  
Ops

**Files likely touched**  
src/model_registry/spec*, tests/unit/registry/

**Tests to add/update**  
Schema tests: ModelSpec serializes deterministically; stable ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.2.1.2 — Add model registry storage (DB or filesystem index)

**Why this step exists**  
Creates a durable registry of trained models and metadata.

**Layer**  
Ops

**Files likely touched**  
src/model_registry/store*, tests/integration/registry/

**Tests to add/update**  
Tests: create/list/get registry entries deterministic ordering.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.2.2.1 — Add training run ID and provenance fields

**Why this step exists**  
Ensures every model points to dataset artifact, code version, and config.

**Layer**  
Ops

**Files likely touched**  
src/model_registry/*, tests/unit/registry/

**Tests to add/update**  
Tests: provenance fields present and deterministic under fixed ‘now’.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.2.3.1 — Add RNG control policy for training

**Why this step exists**  
Centralizes seeding and makes training deterministic for identical inputs.

**Layer**  
Evaluation

**Files likely touched**  
src/train/repro*, tests/integration/train/

**Tests to add/update**  
Tests: training with fixed seed yields identical model hash/metrics on tiny fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 7.3 Baseline ML model introduction (guarded)

#### 7.3.1.1 — Implement first ML model: logistic baseline (or equivalent)

**Why this step exists**  
Introduces a simple learnable model that can be compared to the stats baseline.

**Layer**  
Model/Prediction

**Files likely touched**  
src/ml/models/logistic*, tests/unit/ml/

**Tests to add/update**  
Tests: model trains on tiny dataset; produces deterministic predictions.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.3.1.2 — Add ML prediction adapter behind feature flag

**Why this step exists**  
Allows selecting baseline stats model vs ML model without breaking API schema.

**Layer**  
Service

**Files likely touched**  
src/services/prediction*, tests/unit/services/

**Tests to add/update**  
Tests: selecting model changes internal path but preserves output schema.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.3.2.1 — Add ML evaluation pipeline (backtest integration)

**Why this step exists**  
Evaluates ML models using the same backtesting harness and metrics artifacts.

**Layer**  
Evaluation

**Files likely touched**  
src/eval/backtest*, src/ml/*, tests/integration/eval/

**Tests to add/update**  
Tests: ML backtest produces metrics artifact schema-valid and deterministic on fixture.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.3.3.1 — Add model selection policy (default stays non-ML until proven)

**Why this step exists**  
Prevents unproven models from becoming default without gates passing.

**Layer**  
Service

**Files likely touched**  
src/services/model_select*, tests/unit/services/

**Tests to add/update**  
Tests: default selection remains baseline unless registry marks model as approved.

**Verify**
```
./.venv/bin/python -m pytest -q
```


## 7.4 Training as tasks + UI integration

#### 7.4.1.1 — Add training task runner

**Why this step exists**  
Runs training as a tracked task with artifacts and registry update.

**Layer**  
Ops

**Files likely touched**  
src/ops/tasks/train*, tests/integration/ops/

**Tests to add/update**  
Tests: task transitions; dataset + model artifacts recorded.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.4.1.2 — Add /api/v1/train start endpoint

**Why this step exists**  
Allows starting a training run via API (for UI use).

**Layer**  
API

**Files likely touched**  
src/api/routes/train*, tests/api/

**Tests to add/update**  
API tests: protected endpoint starts task; validates parameters.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.4.2.1 — Add UI page: Train model (v7)

**Why this step exists**  
Lets operator start training and view model registry entries without programming knowledge.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/train.js, tests/

**Tests to add/update**  
Frontend tests: form validates; starts task; renders registry list from mocks.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


#### 7.4.2.2 — Add UI page: Model registry browser

**Why this step exists**  
Allows selecting a model and viewing provenance/metrics artifacts.

**Layer**  
Frontend

**Files likely touched**  
ui-repo: src/views/models.js, tests/

**Tests to add/update**  
Frontend tests: registry list/detail render stable outputs from mocks.

**Verify**
```
Frontend (manual): open the UI in a browser and smoke-check navigation + API calls
```


## 7.5 v7 Gate — Definition of done checks

#### 7.5.1.1 — Add v7 gate: dataset artifact deterministic

**Why this step exists**  
Proves training dataset extraction is stable and leak-free.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Gate test: build dataset twice; compare artifact hashes/rows deterministically.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.5.1.2 — Add v7 gate: training reproducible

**Why this step exists**  
Proves training run with fixed seed produces identical model artifact and metrics on fixture.

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Gate test: run training twice; compare model signature + metrics within tolerance.

**Verify**
```
./.venv/bin/python -m pytest -q
```


#### 7.5.1.3 — Add v7 gate: ML model beats baseline on fixture (tiny)

**Why this step exists**  
Prevents shipping ML that is worse than baseline (even on a small controlled fixture).

**Layer**  
Tests

**Files likely touched**  
tests/gates/

**Tests to add/update**  
Gate test: compare metrics; require non-worse threshold (documented).

**Verify**
```
./.venv/bin/python -m pytest -q
```



---
### STATE S16 — Reproducible training + model registry available (v7 complete)

**Capabilities unlocked**
- Training datasets are built and stored as artifacts
- Model registry stores provenance and metrics
- ML model can be trained and evaluated via tasks
- UI can start training and browse models

**Invariants (must remain true going forward)**
- Training is deterministic under controlled seeds and identical inputs
- Model selection never breaks API schema
- Backtesting remains leak-free and is the only acceptance gate for models

**Exit gate (must be proven by tests/commands)**
- v7 gate tests pass (dataset determinism, training reproducibility, baseline comparison)

**Artifacts produced**
- artifacts/train/<run_id>/dataset.jsonl
- artifacts/train/<run_id>/model.json (or equivalent)
- artifacts/metrics/<run_id>/metrics.json
