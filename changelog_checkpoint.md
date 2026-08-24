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
- P5.1 Pure Product Availability Service Baseline: locally implemented, integrity-audited, and `AUDITED_READY` pending Prompt 5 release.
- Gate 3: not passed; centralized stock mutation and a complete adjustment audit trail remain later Phase 5 work.
- Online demo: not deployed.

## Last Accepted Functional Work

P5.1 establishes the first Phase 5 backend boundary:

- a dedicated `inventory` app owns a side-effect-free Product availability service;
- availability is computed, never stored;
- an active Product is available only when it has at least one active, positive-quantity choice owned by the active Business;
- draft Products and Products with no choices, zero-only choices, or inactive-only choices are unavailable;
- Business/Product mismatches are rejected before computation;
- no quantity mutation, ledger, stock UI, readiness, buyer-reply behavior, model, or migration was added.

## Verification and Audit

- Django system, migration dry-run, and migration-state checks passed; no migration was generated.
- The focused availability service suite passed: 6 tests.
- The directly related Product choice and bundle regression suite passed: 36 tests.
- The PostgreSQL-backed full regression suite passed: 284 tests.
- Source and documentation diff checks passed.
- Integrity audit passed for Business isolation, computed-versus-stored truth, lifecycle separation, choice-level quantity truth, no-write behavior, hosted compatibility, and approved scope.
- Owner/browser testing is not required for this backend-only slice.
- The released Phase 4 state remains owner-accepted with UX notes and exact-SHA CI-passed; Git/GitHub remain delivery-metadata authority.

## Current Gate and Next Work

- Current gate: Prompt 5 release of audited P5.1; Gate 3 remains open after P5.1 because stock mutations and their complete audit trail are not yet centralized.
- After successful release: return to Prompt 2 to select the next smallest Phase 5 functional slice; the inventory adjustment-ledger baseline is the current candidate and still requires analysis and approval.

## Active Blockers and Decisions

- P5.1 has no technical or owner-acceptance blocker.
- Existing Product-bundle quantity writes are not centralized or ledgered by P5.1; this is remaining Phase 5 work, not a P5.1 defect.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `config/settings/base.py`
- `inventory/__init__.py`
- `inventory/apps.py`
- `inventory/availability.py`
- `inventory/tests.py`
- `BUILD_PLAN.md`
- `README.md`
- `changelog_checkpoint.md`
- Proposed commit: `feat: add product availability service`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
