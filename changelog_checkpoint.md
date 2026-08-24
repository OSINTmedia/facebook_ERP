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
- P5.4 ProductBundle Stock Boundary Enforcement: locally implemented, audited, and ready for the release/owner-test gate; exact delivery metadata remains in Git/GitHub.
- Gate 3: not passed; stock routes/UI and the remaining Phase 5 acceptance work remain later Phase 5 work.
- Online demo: not deployed.

## Last Accepted Functional Work

P5.3 establishes the first centralized stock mutation boundary:

- an authenticated Business owner can apply exactly one `+1` or `-1` delta to an owned ProductChoice;
- the current choice row is locked before quantity evaluation, and quantity plus immutable adjustment fact commit in one transaction;
- invalid deltas, underflow, unsaved inputs, cross-Business choices, and non-owner actors produce no stock or ledger write;
- the service returns the locked choice, adjustment, and freshly computed Product availability without changing lifecycle or `is_active` state;
- PostgreSQL-backed concurrency coverage proves two competing decrements cannot produce a lost update or duplicate transition fact.

P5.2 establishes the inventory adjustment fact boundary:

- each immutable record belongs to one Business, exact ProductChoice row, and authenticated Business owner;
- before/after quantities, nonzero delta, and creation timestamp preserve the transition fact;
- model validation rejects cross-Business choices and actors;
- PostgreSQL constraints reject negative quantities, zero deltas, and inconsistent transition arithmetic;
- protected references and application-level update/delete guards preserve history;
- creating an adjustment record does not change ProductChoice quantity;
- no mutation/concurrency service, Product-bundle integration, direct set, reason code, route, HTMX/UI, total, or availability change was added.

P5.4 establishes the ProductBundle stock boundary:

- new ProductChoice rows always start at quantity zero and create no inventory adjustment;
- existing choice quantities are preserved even when stale or forged form values are submitted;
- persisted choices cannot be deleted through ProductBundle, while deactivation remains available;
- unsaved extra rows can be discarded, and the quantity field is visibly read-only;
- ProductBundle owns choice identity, activation, and Business/Product validation, while stock mutation remains centralized in the inventory service.

## Verification and Audit

- Django system and migration dry-run checks passed; the initial inventory migration was exercised on the PostgreSQL test database while the local development database remained unchanged.
- The focused inventory availability/ledger/mutation suite passed: 24 tests.
- The directly related Product choice and bundle regression suite passed: 84 tests.
- Previous P5.3 release evidence included a 2-test migration-order reproducer and a 302-test PostgreSQL-backed full regression suite.
- P5.4 full local verification passed: Django system check, migration dry-run, focused 84-test suite, inventory 24-test suite, and full PostgreSQL-backed regression suite (305 tests).
- Source and documentation diff checks passed.
- Integrity audit passed for Business isolation, exact-choice identity, actor ownership, append-only behavior, numeric/database integrity, choice-level stock truth, no-write behavior, hosted compatibility, and approved scope.
- Owner/browser testing is required for this visible choice-form boundary and is pending the owner report.

## Current Gate and Next Work

- Current gate: Phase 5 functional continuation; P5.4 is audited and awaiting owner/browser confirmation, release, and exact-SHA CI; Gate 3 remains open because stock route/HTMX behavior and transition/regression readiness are not complete.
- Next functional slice: P5.5 Authenticated Stock Mutation Route after P5.4 release closure; after P5.7, run the Phase 5 audit and Gate 3 transition workflow.

## Active Blockers and Decisions

- P5.2 and P5.3 have no technical or owner-acceptance blocker.
- P5.4 has no technical blocker; the required owner/browser test and Prompt 5 release/CI gate remain open.
- ProductBundle no longer accepts quantity writes as part of product editing; stock mutation remains a later authenticated route concern over the P5.3 service.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `BUILD_PLAN.md`
- `changelog_checkpoint.md`
- `DEVELOPMENT_NOTES.md`
- `APP_EXPERIENCE_PLAN.md`
- `README.md`
- `catalog/forms.py`
- `catalog/product_bundles.py`
- `catalog/tests.py`
- `templates/catalog/_choice_section.html`
- Proposed commit: `feat: enforce product bundle stock boundary`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
