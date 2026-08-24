# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-08-24

## Current State

- Phase 1 Django/PostgreSQL Foundation and CI: `PASSED`.
- Phase 2 User and Business Ownership: `PASSED`.
- Phase 3 Catalog Core: `PASSED`.
- Phase 4 Semantic Recognition and Choice Model: `PASSED`.
- Phase 5 Inventory and Computed Availability: `IN_PROGRESS`.
- P5.1 Pure Product Availability Service Baseline: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.2 Business-Scoped Inventory Adjustment Ledger Baseline: locally implemented, integrity-audited, and `AUDITED_READY` pending Prompt 5 release.
- Gate 3: not passed; transaction-safe stock mutation and ledger creation through one service remain later Phase 5 work.
- Online demo: not deployed.

## Last Accepted Functional Work

P5.2 establishes the inventory adjustment fact boundary:

- each immutable record belongs to one Business, exact ProductChoice row, and authenticated Business owner;
- before/after quantities, nonzero delta, and creation timestamp preserve the transition fact;
- model validation rejects cross-Business choices and actors;
- PostgreSQL constraints reject negative quantities, zero deltas, and inconsistent transition arithmetic;
- protected references and application-level update/delete guards preserve history;
- creating an adjustment record does not change ProductChoice quantity;
- no mutation/concurrency service, Product-bundle integration, direct set, reason code, route, HTMX/UI, total, or availability change was added.

## Verification and Audit

- Django system and migration dry-run checks passed; the initial inventory migration was exercised on the PostgreSQL test database while the local development database remained unchanged.
- The focused inventory availability/ledger suite passed: 14 tests.
- The directly related Product choice and bundle regression suite passed: 36 tests.
- The PostgreSQL-backed full regression suite passed: 292 tests.
- Source and documentation diff checks passed.
- Integrity audit passed for Business isolation, exact-choice identity, actor ownership, append-only behavior, numeric/database integrity, choice-level stock truth, no-write behavior, hosted compatibility, and approved scope.
- Owner/browser testing is not required for this backend-only slice.

## Current Gate and Next Work

- Current gate: Prompt 5 release of audited P5.2; Gate 3 remains open because stock mutation and adjustment creation are not yet centralized atomically.
- After successful release: return to Prompt 2 to select the next smallest Phase 5 functional slice; a transaction-safe increment/decrement inventory service is the current candidate and still requires analysis and approval.

## Active Blockers and Decisions

- P5.2 has no technical or owner-acceptance blocker.
- Existing Product-bundle quantity writes are not centralized or ledgered by P5.2; this is remaining Phase 5 work, not a P5.2 defect.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `inventory/models.py`
- `inventory/migrations/__init__.py`
- `inventory/migrations/0001_initial.py`
- `inventory/tests.py`
- `BUILD_PLAN.md`
- `DEVELOPMENT_NOTES.md`
- `README.md`
- `changelog_checkpoint.md`
- Proposed commit: `feat: add inventory adjustment ledger`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
