# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-09-02

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
- P6.7a Workspace First-Viewport and Mobile-Density Repair: `CLOSED`; released and exact-SHA CI-passed after implementation, integrity audit, focused verification, full PostgreSQL regression, and required owner/browser acceptance, with delivery metadata retained in Git/GitHub.
- P6.7b Canonical Workspace Return-Path Hardening: `CLOSED`; implementation, integrity audit, required owner/browser return-path verification, release, and exact-SHA CI passed, with delivery metadata retained in Git/GitHub.
- P6.7c Workspace Accessibility and Recovery Hardening: `CLOSED`; released and exact-SHA CI-passed after local audit and required owner/browser verification, with delivery metadata retained in Git/GitHub.
- Online demo: not deployed.

## Last Accepted Functional Work

P6.7c hardens in-flight Workspace stock controls without changing Product, vocabulary, inventory, or computed truth:

- each acted choice's stock buttons are physically disabled as well as exposed as aria-disabled while a request is in flight;
- server-rendered quantity, availability, lifecycle, result membership, and feedback remain authoritative;
- accepted, expected-error, and transport-recovery paths restore the applicable controls and established focus behavior.

## Verification and Audit

- The focused Workspace-state, Product create/edit, ProductBundle, recognition/transfer, Business-isolation, and inventory-return regression set passed 152 tests; the PostgreSQL-backed full regression suite passed 405 tests. A fresh audit rerun of the canonical Workspace state and Product create/edit matrix passed 71 tests.
- Source, tests, whitespace, scope-whitelist, documentation, and no-drift checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit confirmed canonical Product Workspace parsing is isolated to Product Add/Edit while generic vocabulary recovery remains unchanged; it found no change to Business-scoped reads or mutations, atomic ProductBundle persistence, exact-choice identity, Phase 5 inventory ownership, lifecycle/availability separation, HTMX server truth, dependencies, schema, or hosted compatibility.
- Required P6.7b owner/browser verification passed by owner report for exact combined-state Cancel and save return paths.
- P6.7c focused Workspace/inventory regression and the PostgreSQL-backed full regression suite passed; Django system and migration checks, JavaScript syntax, whitespace, scope-whitelist, and no-drift checks passed. Required owner/browser verification passed, including the in-flight disabled-control recovery check.

## Current Gate and Next Work

- Current gate: P6.7d Phase 6 Integrated Regression and Owner Closure Gate.
- Next functional slice: P6.7d Phase 6 Integrated Regression and Owner Closure Gate.
- Controlled remaining order: P6.7d integrated regression and owner closure; a P6.7d defect requires the smallest separate recovery slice.

## Active Blockers and Decisions

- P6.7a through P6.7c are closed. P6.7d is not started and is the remaining Phase 6 closure gate.
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
