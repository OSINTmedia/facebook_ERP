# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-08-27

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
- P6.5 V1 Product Workspace Filter Baseline: `AUDITED_READY`; implementation, local integrity verification, and required owner/browser acceptance passed; Prompt 5 release and exact-SHA CI remain.
- Online demo: not deployed.

## Last Accepted Functional Work

P6.5 adds the owner-approved bounded filter set to the owned Product Workspace without adding filter sprawl or client-owned truth:

- single-select stored Lifecycle (`Active`/`Draft`) and computed Availability (`Available`/`Sold out`) filters compose with `q` through canonical server-owned URL state;
- Availability is derived from active positive choice stock, excludes drafts from Sold out, and constrains the complete Product/choice/size/color relation to the active Business;
- visible active filters, result counts, Clear search, Clear filters, Clear all, validation, and distinct catalog/search/filter/combined empty states remain native server-rendered behavior;
- Type, Tag, material, size, color, readiness, low-stock, multi-select, sorting, pagination, HTMX filter state, and Alpine query state remain excluded.

## Verification and Audit

- The focused P6.5 Workspace suite passed: 49 tests; the focused inventory regression suite passed: 53 tests; the PostgreSQL-backed full regression suite passed: 392 tests.
- Source, whitespace, scope-whitelist, documentation, and no-drift checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit passed for the approved filter scope, Business-first querying, complete choice-relation isolation, lifecycle/availability separation, search composition, canonical/clear URL behavior, invalid-input recovery, bounded query growth, distinct empty states, native accessibility/mobile structure, and hosted compatibility.
- Required P6.5 owner/browser verification passed by owner report.

## Current Gate and Next Work

- Current gate: Prompt 5 exact release, remote alignment, and exact-SHA CI for P6.5.
- Next functional slice after P6.5 closes: P6.6 HTMX Workspace Truth Refresh and State Coherence.

## Active Blockers and Decisions

- P6.5 has no pre-release blocker; implementation approval fixed the exact set as stored Lifecycle plus computed Availability.
- P6.5 intentionally remains native server-rendered filtering; Type/Tag and other filter expansion, fuzzy/morphology behavior, ranking, autocomplete, pagination, Workspace HTMX replacement, readiness, replies, and Dashboard behavior remain excluded.
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
