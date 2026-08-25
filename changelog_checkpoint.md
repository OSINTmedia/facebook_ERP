# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-08-25

## Current State

- Phase 1 Django/PostgreSQL Foundation and CI: `PASSED`.
- Phase 2 User and Business Ownership: `PASSED`.
- Phase 3 Catalog Core: `PASSED`.
- Phase 4 Semantic Recognition and Choice Model: `PASSED`.
- Phase 5 Inventory and Computed Availability: `IN_PROGRESS`.
- P5.1 Pure Product Availability Service Baseline: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.2 Business-Scoped Inventory Adjustment Ledger Baseline: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.3 Atomic Inventory Increment/Decrement Service: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.4 ProductBundle Stock Boundary Enforcement: released, owner-reviewed, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.5 Authenticated Stock Mutation Route: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.6 HTMX Stock Response and Controls: released, owner/browser-tested, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.6A One-Save Initial Stock Capture: released, owner/browser-tested, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.7 Inventory Transition and Regression Readiness: released, integrity-audited, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.8 Inventory Boundary Hardening: locally accepted and release-ready; commit, push, exact-SHA CI, and the Phase 5/Gate 3 post-CI transition remain pending.
- Gate 3: not passed; P5.8 release and exact-SHA CI are the remaining operational gate before the Phase 5 transition.
- Online demo: not deployed.

## Last Accepted Functional Work

P5.8 closes the two integrity gaps found by the Phase 5 code-first audit without adding inventory policy or UI behavior:

- ledger bulk creation validates the complete batch's Business/choice/actor scope before any insert, while conflict-ignore and conflict-update modes are rejected so facts cannot be hidden or rewritten;
- one-time initialization and ongoing `+1` mutation validate the configured database quantity range before writing;
- storage overflow now returns the existing controlled `ValidationError` path, preserving current server quantity and creating no adjustment fact.

## Verification and Audit

- The P5.8 inventory suite passed: 52 tests; the PostgreSQL-backed full regression suite passed: 342 tests.
- Source and documentation diff checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit passed for batch-level Business isolation, ledger conflict-mode immutability, configured quantity-range enforcement, rollback/no-write behavior, HTMX error recovery, existing stock/lifecycle/availability boundaries, hosted compatibility, and approved scope.
- P5.8 is backend hardening with no new owner/browser interaction; the previously accepted P5.6A/P5.7 workflow remains unchanged.

## Current Gate and Next Work

- Current gate: release the locally accepted P5.8 set through Prompt 5 and require successful exact-SHA CI; Gate 3 remains not passed before that evidence.
- Next functional slice: none before release; after successful P5.8 CI, Prompt 5 must complete the Phase 5/Gate 3 governance transition, then routine planning may begin for Phase 6.

## Active Blockers and Decisions

- P5.8 has no known local technical blocker; release, exact-SHA CI, and the allowed post-CI Phase 5/Gate 3 transition remain pending.
- Existing choices retain read-only quantity plus P5.6 controls; one-time initialization is not approval for ongoing direct set or arbitrary subsequent deltas.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `inventory/models.py`
- `inventory/mutations.py`
- `inventory/tests.py`
- `BUILD_PLAN.md`
- `DEVELOPMENT_NOTES.md`
- `changelog_checkpoint.md`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
