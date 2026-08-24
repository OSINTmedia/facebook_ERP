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
- P5.6A One-Save Initial Stock Capture: owner-approved and planned as the next functional slice.
- Gate 3: not passed; P5.6A and Phase 5 transition/regression readiness remain.
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
- Owner/browser testing passed functionally. Owner noted that new Products and newly added choices must be saved at zero before stock controls appear; P5.6A owns the approved correction before Phase 5 audit/Gate 3 closure.

## Current Gate and Next Work

- Current gate: P5.6 is `CLOSED`; Gate 3 remains open.
- Next functional slice: P5.6A One-Save Initial Stock Capture; P5.7 Inventory Transition and Regression Readiness follows only after P5.6A closes.

## Active Blockers and Decisions

- P5.1 through P5.6 are closed with no technical or owner-acceptance blocker.
- P5.6A is owner-approved: unsaved choices may accept starting stock in the normal final Product save, while the server must persist choice identity first and record any positive start through the centralized inventory mutation boundary as one immutable fact.
- Existing choices retain read-only quantity plus P5.6 controls; P5.6A is not approval for ongoing direct set or arbitrary subsequent deltas.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- None; P5.6 is closed and P5.6A implementation has not started.

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
