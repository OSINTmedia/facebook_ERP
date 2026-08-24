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
- P5.5 Authenticated Stock Mutation Route: locally implemented, integrity-audited, and ready for the Prompt 5 release gate.
- Gate 3: not passed; HTMX stock controls and Phase 5 transition/regression readiness remain later work.
- Online demo: not deployed.

## Last Accepted Functional Work

P5.5 exposes the centralized stock boundary through one authenticated route:

- only CSRF-protected POST requests with exact `+1` or `-1` deltas can reach the mutation service;
- Business and actor come from the authenticated request, while the target choice is Business-scoped and cross-Business identity is not exposed;
- each accepted request produces one atomic quantity transition and immutable adjustment fact;
- invalid delta, underflow, unauthenticated, GET, CSRF, cross-Business, missing-Business, and unresolved multiple-Business paths produce no stock or ledger write;
- safe internal return context is preserved, external return URLs fall back to Products, and HTMX controls/responses remain P5.6 work.

## Verification and Audit

- Django system and migration dry-run checks passed with no schema changes.
- The focused P5.5 route/security suite passed: 11 tests; the complete inventory suite passed: 35 tests.
- The PostgreSQL-backed full regression suite passed: 316 tests.
- Source and documentation diff checks passed.
- Integrity audit passed for authentication, CSRF, POST-only mutation, Business isolation, exact-choice identity, server-derived actor ownership, safe return paths, atomic stock/ledger truth, hosted compatibility, and approved scope.
- Owner/browser testing is advisory for this route-only slice; no visible stock-control surface was added.

## Current Gate and Next Work

- Current gate: P5.5 is locally accepted and awaiting Prompt 5 commit, push, clean alignment, and exact-SHA CI; Gate 3 remains open.
- Next functional slice: P5.6 HTMX Stock Response and Controls after P5.5 release closure; after P5.7, run the Phase 5 audit and Gate 3 transition workflow.

## Active Blockers and Decisions

- P5.1 through P5.5 have no technical or owner-acceptance blocker; P5.5 has only the Prompt 5 release/CI gate open.
- The P5.5 route has no visible control consumer yet; P5.6 owns the approved server-rendered HTMX response/control surface.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `BUILD_PLAN.md`
- `changelog_checkpoint.md`
- `config/urls.py`
- `inventory/urls.py`
- `inventory/views.py`
- `inventory/tests.py`
- Proposed commit: `feat: add stock mutation route`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
