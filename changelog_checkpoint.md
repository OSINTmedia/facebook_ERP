# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-09-01

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
- P6.6 HTMX Workspace Truth Refresh and State Coherence: `CLOSED`; released and exact-SHA CI-passed, with delivery metadata retained in Git/GitHub.
- P6.7 Phase 6 Workspace UX, Navigation, Accessibility, and Regression Gate: `IN_PROGRESS`.
- P6.7a Workspace First-Viewport and Mobile-Density Repair: `AUDITED_READY`; implementation, integrity audit, focused verification, full PostgreSQL regression, and required owner/browser acceptance passed; Prompt 5 release and exact-SHA CI remain.
- Online demo: not deployed.

## Last Accepted Functional Work

P6.7a repairs the Workspace hierarchy and responsive presentation without changing server-owned Product or inventory behavior:

- daily Add Product, search/filter, Product cards, and exact-choice stock work appear before secondary vocabulary settings;
- valid active filters remain collapsed while their canonical server-owned state and clear actions stay visible; invalid filters open with field errors;
- Lifecycle and computed Availability precede the secondary description excerpt on each card;
- responsive card, choice, and stock-control styling improves compactness, wrapping, and approximately 44-pixel action targets at mobile width.

## Verification and Audit

- The focused Workspace and inventory route/HTMX suite passed 74 tests; the PostgreSQL-backed full regression suite passed 402 tests.
- Source, template, responsive-style, whitespace, scope-whitelist, documentation, and no-drift checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit found no change to Business-scoped reads or mutations, exact-choice identity, canonical URL state, Phase 5 inventory ownership, lifecycle/availability separation, HTMX server truth, native fallback, dependencies, schema, or hosted compatibility.
- Required P6.7a desktop and approximately 390px mobile owner/browser verification passed by owner report; this is bounded slice acceptance, not a broader WCAG or cross-browser certification.

## Current Gate and Next Work

- Current gate: Prompt 5 release, remote alignment, and exact-SHA CI for P6.7a.
- Next functional work after P6.7a closes: contract the remaining P6.7 navigation, accessibility, and Phase 6 regression gate as the next smallest slice before Phase 7.

## Active Blockers and Decisions

- P6.7a has no pre-release blocker.
- P6.7a changes only Workspace hierarchy and responsive presentation. Backend query/mutation behavior, live search/filter navigation, optimistic state, Dashboard synchronization, polling, readiness, replies, direct set, bulk mutation, and lifecycle mutation remain excluded.
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
