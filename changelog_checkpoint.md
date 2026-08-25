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
- P6.1 Product Workspace Route and Query Baseline: `AUDITED_READY`; Prompt 5 release and exact-SHA CI are pending.
- Online demo: not deployed.

## Last Accepted Functional Work

P6.1 establishes the authenticated seller Product Workspace read and URL-state foundation without pulling forward rich cards, stock interaction, search, filters, or later-phase behavior:

- the existing `/products/` route resolves one active Business and reads only its Products through a dedicated deterministic name-then-id query boundary;
- generated Add/Edit workflow links carry a canonical `/products/` return URL and discard every query key until its owning search/filter slice approves it;
- a reusable server-rendered results partial preserves the current simple Product identity/lifecycle rows, distinct Business-policy states, and one useful empty-catalog recovery action;
- small responsive layout rules keep result content and page actions wrapping without introducing HTMX, Alpine, schema, dependency, or state-truth changes.

## Verification and Audit

- The focused P6.1 suite passed: 8 tests; existing Product list/create/edit regressions passed: 63 tests; the catalog suite passed: 260 tests; the PostgreSQL-backed full regression suite passed: 350 tests.
- Source, untracked-file whitespace, documentation, and release-whitelist diff checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit passed for authentication, Business-first isolation, no-write GET behavior, multiple-Business policy, deterministic ordering, canonical return context, distinct empty states, thin view/read responsibilities, hosted compatibility, and approved Phase 6 scope.
- Owner/browser verification is advisory for P6.1 and has not been claimed as executed.

## Current Gate and Next Work

- Current gate: P6.1 is locally accepted and `AUDITED_READY`; Prompt 5 must release the exact audited set and verify relevant exact-SHA CI before the slice can close.
- Next functional slice after P6.1 closes: P6.2 Compact Product Card and Availability Baseline.

## Active Blockers and Decisions

- P6.1 has no known technical or owner-decision blocker; only the Prompt 5 operational release gate remains.
- P6.1 intentionally carries no search/filter state yet and does not display choices, computed availability, stock controls, readiness, replies, or Dashboard behavior.
- Existing choices retain read-only quantity plus P5.6 controls; one-time initialization is not approval for ongoing direct set or arbitrary subsequent deltas.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `BUILD_PLAN.md`
- `catalog/test_workspace.py`
- `catalog/views.py`
- `catalog/workspace.py`
- `changelog_checkpoint.md`
- `static/css/app.css`
- `templates/catalog/_product_results.html`
- `templates/catalog/product_list.html`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
