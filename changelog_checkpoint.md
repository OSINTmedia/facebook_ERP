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
- P5.6 HTMX Stock Response and Controls: locally implemented, integrity-audited, and owner/browser-tested with a documented save-before-stock UX limitation; ready for release.
- Gate 3: not passed; a separately approved quantity-management UX correction and Phase 5 transition/regression readiness remain later work.
- Online demo: not deployed.

## Last Accepted Functional Work

P5.6 provides the first seller-visible stock controls without creating another stock-write boundary:

- only persisted, Business-scoped choice rows on Product edit render compact `+1`/`-1` controls; the ProductBundle quantity input remains read-only and unsaved rows have no control;
- controls submit only the existing CSRF-protected P5.5 route with exact deltas, so actor, Business, row lock, quantity transition, and immutable adjustment fact remain server-owned;
- an HTMX response replaces only the affected choice-control region with current server quantity plus success or error feedback; the UI claims no optimistic stock state;
- native submission safely follows the same route and return context, while loading disables both controls for the affected choice.

## Verification and Audit

- Django system and migration dry-run checks passed with no schema changes.
- The focused P5.6 HTMX/control checks passed; route plus Product create/edit regression passed: 70 tests; the complete inventory suite passed: 38 tests.
- The PostgreSQL-backed full regression suite passed: 321 tests.
- Source and documentation diff checks passed.
- Integrity audit passed for authentication, CSRF, POST-only mutation, Business isolation, exact-choice identity, read-only ProductBundle stock input, server-derived actor ownership, safe return paths, atomic stock/ledger truth, HTMX server truth, accessibility feedback, mobile control density, hosted compatibility, and approved scope.
- Owner/browser testing passed functionally. Owner noted that new Products and newly added choices must be saved at zero before stock controls appear; this inconvenient two-step quantity workflow requires a separately approved correction before Phase 5 audit/Gate 3 closure.

## Current Gate and Next Work

- Current gate: P5.6 is locally accepted and awaiting Prompt 5 release, clean alignment, and exact-SHA CI; Gate 3 remains open.
- Next functional work after P5.6 release: use Prompt 2 to define the smallest quantity-management UX correction; P5.7 Inventory Transition and Regression Readiness follows only after that correction closes.

## Active Blockers and Decisions

- P5.1 through P5.5 have no technical or owner-acceptance blocker. P5.6 has no technical or owner-test blocker; only the Prompt 5 release/CI gate remains open.
- Owner approved compact controls beside persisted Product-edit choices only; the read-only field and separate inventory mutation boundary remain mandatory.
- Required UX follow-up: reduce the new-Product/new-choice save-before-stock friction without allowing an unsaved row to bypass persisted choice identity, the centralized mutation service, or the immutable adjustment ledger.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `BUILD_PLAN.md`
- `DEVELOPMENT_NOTES.md`
- `APP_EXPERIENCE_PLAN.md`
- `README.md`
- `catalog/tests.py`
- `changelog_checkpoint.md`
- `inventory/views.py`
- `inventory/tests.py`
- `static/css/app.css`
- `templates/catalog/_choice_section.html`
- `templates/inventory/_choice_stock_controls.html`
- Proposed commit: `feat: add htmx stock controls`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
