# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-08-26

## Current State

- Phase 1 Django/PostgreSQL Foundation and CI: `PASSED`.
- Phase 2 User and Business Ownership: `PASSED`.
- Phase 3 Catalog Core: `PASSED`.
- Phase 4 Semantic Recognition and Choice Model: `PASSED`.
- Phase 5 Inventory and Computed Availability: `PASSED`.
- P5.1 Pure Product Availability Service Baseline: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.2 Business-Scoped Inventory Adjustment Ledger Baseline: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.3 Atomic Inventory Increment/Decrement Service: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.4 ProductBundle Stock Boundary Enforcement: released, owner-reviewed, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.5 Authenticated Stock Mutation Route: released and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.6 HTMX Stock Response and Controls: released, owner/browser-tested, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.6A One-Save Initial Stock Capture: released, owner/browser-tested, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.7 Inventory Transition and Regression Readiness: released, integrity-audited, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- P5.8 Inventory Boundary Hardening: released, integrity-audited, and exact-SHA CI-passed; delivery metadata remains in Git/GitHub.
- Gate 3: `PASSED`; the Phase 5 audit and transition are complete.
- Phase 6 Operational Product Workspace: `IN_PROGRESS`.
- P6.1 Product Workspace Route and Query Baseline: `CLOSED`; released and exact-SHA CI-passed, with delivery metadata retained in Git/GitHub.
- P6.2 Compact Product Card and Availability Baseline: `CLOSED`; released and exact-SHA CI-passed, with delivery metadata retained in Git/GitHub.
- P6.3 Choice-Level Workspace Stock Controls: locally `AUDITED_READY`; operational closure is determined by the Prompt 5 Git/GitHub release evidence.
- Online demo: not deployed.

## Last Accepted Functional Work

P6.3 makes each active ProductChoice on an owned Workspace card directly actionable without adding a new mutation path or premature Workspace HTMX:

- each visible active choice has CSRF-protected native `-1` and `+1` controls labeled with exact Choice identity, canonical Size, and canonical Color;
- every accepted action reuses the released authenticated inventory route, locked delta service, and immutable adjustment ledger, while leaving lifecycle and choice activation unchanged;
- success and expected failure redirect to the canonical Workspace URL and re-render quantity, active total, and computed Availability from current server truth;
- inactive choices remain non-actionable, duplicate-looking rows remain distinct, and mobile controls retain safe tap targets without HTMX, Alpine, direct set, or optimistic state.

## Verification and Audit

- The focused P6.3 Workspace and inventory-route suite passed: 37 tests; the inventory suite passed: 53 tests; the catalog suite passed: 274 tests; the PostgreSQL-backed full regression suite passed: 365 tests.
- Source, untracked-file whitespace, documentation, and release-whitelist diff checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit passed for authenticated Business-scoped mutation reuse, exact duplicate-choice targeting, immutable ledger transitions, underflow/no-write recovery, lifecycle and activation preservation, full-page recomputation, CSRF propagation through isolated card rendering, native return context, mobile tap targets, hosted compatibility, and approved Phase 6 scope.
- Owner/browser verification is advisory for P6.3 and has not been claimed as executed.

## Current Gate and Next Work

- Release gate: P6.3 closes when Prompt 5 produces a clean aligned release and relevant exact-SHA CI success; the exact outcome is read from Git/GitHub rather than copied into this file.
- Next functional slice after P6.3 closes: P6.4 Product Workspace Search Baseline.

## Active Blockers and Decisions

- P6.3 has no known technical or owner-decision blocker; Prompt 5 owns its operational release outcome.
- P6.3 intentionally adds only native exact-choice `-1`/`+1` controls; search/filter state, Workspace HTMX replacement, readiness, replies, Dashboard behavior, direct set, and arbitrary deltas remain excluded.
- Existing choices retain read-only quantity plus P5.6 controls; one-time initialization is not approval for ongoing direct set or arbitrary subsequent deltas.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `BUILD_PLAN.md`
- `README.md`
- `catalog/test_workspace.py`
- `changelog_checkpoint.md`
- `static/css/app.css`
- `templates/catalog/_product_card.html`
- `templates/catalog/_product_results.html`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
