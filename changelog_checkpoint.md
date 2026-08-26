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
- P6.3 Choice-Level Workspace Stock Controls: `CLOSED`; released and exact-SHA CI-passed, with delivery metadata retained in Git/GitHub.
- P6.4 Product Workspace Search Baseline: `CI_RECOVERY_AUDITED_READY`; the source release is clean and aligned, but its exact-SHA workflow ended in a zero-job startup failure. The approved CI-R1 recovery adds manual dispatch only and awaits Prompt 5.
- Online demo: not deployed.

## Last Accepted Functional Work

P6.4 adds controlled, URL-backed Product retrieval to the owned Workspace without adding filters, client-owned state, or unconfirmed facts:

- validated `q` state trims and collapses whitespace, permits at most 120 characters and eight tokens, rejects repeated or malformed input, and owns canonical Workspace return context;
- case-insensitive search requires every token to match at least one approved persisted field across Product name/description, confirmed Type/Tag names and aliases, exact choice Size/Color names and aliases, or confirmed material wording;
- every structured relation is Business-scoped, including the complete Size/Color choice boundary, and duplicate joins still produce one deterministically ordered Product;
- visible applied query, result count, Clear search, validation, catalog-empty, and search-no-result states remain native server-rendered behavior and preserve Edit and stock return context without HTMX or Alpine.

## Verification and Audit

- The focused P6.4 Workspace suite passed: 36 tests; the PostgreSQL-backed full regression suite passed: 379 tests.
- Source, untracked-file whitespace, documentation, and release-whitelist diff checks passed.
- Django system, migration dry-run, and unapplied-migration checks passed with no schema change.
- Integrity audit passed for Business-first querying, canonical and alias field coverage, confirmed-fact boundaries, whole-choice Business isolation, deliberate cross-Business corruption rejection, AND-across-token behavior, duplicate elimination, bounded query count, malformed-input recovery, canonical Edit/stock return context, native accessibility/mobile behavior, hosted compatibility, and approved Phase 6 scope.
- Owner/browser verification is advisory for P6.4 and has not been claimed as executed.

## Current Gate and Next Work

- Release gate: Prompt 5 must release CI-R1 and obtain successful CI on the new current-main recovery SHA. Because the original source SHA cannot be rerun after its zero-job startup failure, the owner explicitly approved that successful recovery-SHA CI may close P6.4; exact delivery metadata remains in Git/GitHub.
- Next functional slice after P6.4 closes: P6.5 V1 Product Workspace Filter Baseline; implementation requires explicit owner approval of the exact bounded filter set.

## Active Blockers and Decisions

- P6.4 is blocked only by the operational CI recovery gate; CI-R1 is locally audited and approved for release.
- P6.4 intentionally adds only native server-rendered search; filters, lifecycle keyword interpretation, fuzzy/morphology behavior, ranking, autocomplete, pagination, Workspace HTMX replacement, readiness, replies, and Dashboard behavior remain excluded.
- P6.5 remains `OWNER_DECISION_REQUIRED` before implementation for the exact bounded filter set; the roadmap recommends stored Lifecycle plus computed Availability only.
- Existing choices retain read-only quantity plus P5.6 controls; one-time initialization is not approval for ongoing direct set or arbitrary subsequent deltas.
- Direct stock set remains `OWNER_DECISION_REQUIRED`; stock-movement reason codes remain excluded unless separately approved.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Audited Release Set

- `.github/workflows/django.yml`
- `BUILD_PLAN.md`
- `DEVELOPMENT_NOTES.md`
- `changelog_checkpoint.md`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
