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
- P5.2 Business-Scoped Inventory Adjustment Ledger Baseline: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.3 Atomic Inventory Increment/Decrement Service: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.4 ProductBundle Stock Boundary Enforcement: released, owner-reviewed, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.5 Authenticated Stock Mutation Route: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.6 HTMX Stock Response and Controls: released, owner/browser-tested, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.6A One-Save Initial Stock Capture: locally implemented, integrity-audited, and PostgreSQL-verified; required owner/browser test pending.
- Gate 3: not passed; P5.6A owner acceptance/release and Phase 5 transition/regression readiness remain.
- Online demo: not deployed.

## Last Accepted Functional Work

P5.6A removes the save-before-stock implementation gap while retaining one stock-write boundary:

- an unsaved choice exposes non-negative Starting stock during the normal Product create/edit submission, while persisted quantities remain read-only and continue to use P5.6 `-1`/`+1` controls;
- ProductBundle validates first, persists each new choice at zero, and passes a positive start plus server-derived Business and actor to the centralized inventory mutation boundary inside the same outer transaction;
- initialization re-locks the exact Business-scoped choice, requires zero quantity and no adjustment history, and records one immutable `0 -> N` fact; zero creates no fact because no transition occurred;
- invalid input and no-write helper interactions preserve seller input, and any later ProductBundle persistence failure rolls back Product, choice, quantity, tags, materials, and adjustment facts together.

## Verification and Audit

- Django system and migration dry-run checks passed with no schema changes.
- The focused P5.6A service/form/ProductBundle/create-edit/concurrency suite passed: 104 tests; the complete inventory suite passed: 46 tests.
- The PostgreSQL-backed full regression suite passed: 335 tests; the audit hardening rollback checks passed: 2 tests.
- Source and documentation diff checks passed.
- Integrity audit passed for Business-scoped vocabulary and choice identity, authenticated actor ownership, row locking, one-time initialization preconditions, immutable adjustment truth, full ProductBundle rollback, lifecycle/availability separation, P5.6 control preservation, no-write helper behavior, hosted compatibility, and approved scope.
- Required owner/browser testing has not yet been reported for P5.6A.

## Current Gate and Next Work

- Current gate: complete the required P5.6A owner/browser scenario; after owner PASS, proceed to Prompt 5 release and exact-SHA CI. Gate 3 remains open.
- Next functional slice after P5.6A release closure: P5.7 Inventory Transition and Regression Readiness.

## Active Blockers and Decisions

- P5.6A has no known technical blocker; required owner/browser acceptance is the only open release prerequisite.
- Existing choices retain read-only quantity plus P5.6 controls; one-time initialization is not approval for ongoing direct set or arbitrary subsequent deltas.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `BUILD_PLAN.md`
- `catalog/forms.py`
- `catalog/product_bundles.py`
- `catalog/tests.py`
- `catalog/views.py`
- `changelog_checkpoint.md`
- `inventory/mutations.py`
- `inventory/tests.py`
- `templates/catalog/_choice_section.html`
- Proposed commit: `feat: add one-save initial stock`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
