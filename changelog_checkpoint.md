# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-08-31

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
- P6.3 Choice-Level Workspace Stock Controls: `CLOSED`; released and exact-SHA CI-passed, with delivery metadata retained in Git/GitHub.
- P6.4 Product Workspace Search Baseline: `CLOSED`; the approved manual-dispatch recovery was released and exact-SHA CI-passed after the original source workflow's zero-job startup failure, with delivery metadata retained in Git/GitHub.
- P6.5 V1 Product Workspace Filter Baseline: `CLOSED`; released and exact-SHA CI-passed, with delivery metadata retained in Git/GitHub.
- P6.6 HTMX Workspace Truth Refresh and State Coherence: `AUDITED_READY`; implementation, audit hardening, local PostgreSQL verification, and required owner/browser acceptance passed; Prompt 5 release and exact-SHA CI remain.
- Online demo: not deployed.

## Last Accepted Functional Work

P6.6 progressively enhances exact-choice Workspace stock controls while preserving the released Phase 5 mutation boundary and native fallback:

- the existing stock POST accepts an explicit Workspace response scope only with one exact canonical local `q`/Lifecycle/Availability return state;
- accepted and expected-error HTMX responses re-run the shared Business-scoped Workspace read boundary and replace the complete results region so quantity, totals, computed Availability, result count, and filter membership stay coherent;
- loading/disabled behavior, accessible success/error feedback, focus recovery, and full-refresh transport recovery use minimal page JavaScript that never computes or owns Product or inventory truth;
- native POST/redirect remains functional, Product Edit keeps its existing choice-only HTMX response, and stale acted-choice feedback remains visible even when that choice no longer renders.

## Verification and Audit

- The combined focused Workspace and inventory suite passed 111 tests after audit hardening; the PostgreSQL-backed full regression suite passed 401 tests.
- Source, JavaScript syntax, whitespace, scope-whitelist, documentation, and no-drift checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit passed for Business-scoped mutation and response reads, exact-choice identity, canonical return-state validation, Phase 5 ledger/service reuse, lifecycle/availability separation, complete results-region truth, native fallback, bounded query growth, expected-error recovery, transport/focus hooks, and hosted compatibility.
- Required P6.6 owner/browser verification passed by owner report; functionality works, while the visual interface still needs later UI/UX improvement.

## Current Gate and Next Work

- Current gate: Prompt 5 release, remote alignment, and exact-SHA CI for P6.6.
- Next functional slice after P6.6 closes: P6.7 Phase 6 Workspace UX, Navigation, Accessibility, and Regression Gate.

## Active Blockers and Decisions

- P6.6 has no pre-release blocker. Functional behavior is accepted; visual UI/UX improvement remains later work and does not block this release.
- P6.6 changes only Workspace stock-response coherence. Live search/filter navigation, optimistic state, Dashboard synchronization, polling, readiness, replies, direct set, bulk mutation, and lifecycle mutation remain excluded.
- Existing choices retain read-only quantity plus P5.6 controls; one-time initialization is not approval for ongoing direct set or arbitrary subsequent deltas.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
