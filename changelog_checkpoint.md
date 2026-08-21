# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: read-only evidence at `/home/giga/Desktop/OSINT/facebook_MVP/`
- Authority rule: exact branch, hash, remote, and CI metadata live in Git/GitHub, not this file
- Last updated: 2026-08-21

## Current State

- Phase 1 Django/PostgreSQL Foundation and CI: `PASSED`.
- Phase 2 User and Business Ownership: `PASSED`.
- Phase 3 Catalog Core: `PASSED`.
- Phase 4 Semantic Recognition and Choice Model: `IN_PROGRESS`.
- P4.1 through P4.9f, including P4.9d_expand and P4.9e_expand: released, remote-aligned, CI-passed, owner/browser-reviewed, and `PASSED`.
- Gate 3: not passed; inventory and computed availability remain later work.
- Online demo: not deployed.

## Last Accepted Functional Work

P4.9f adds explicit material confirmation to authenticated Product create/edit:

- recognition candidates remain transient and require a seller action;
- “Review as material” transfers a freshly recomputed candidate into copied, unsaved formset data;
- editable rows expose canonical material, optional percentage, original seller wording, and source;
- confirmation, correction, and removal save only through the atomic Product bundle;
- Business and Product ownership plus confirmed-only state are assigned and validated server-side;
- forged cross-Business material identities are rejected without mutation;
- validation errors preserve Product, choice, classification, and material input;
- no material alias model, automatic alias learning, measurement behavior, inventory, availability, readiness, buyer replies, or LLM truth was added;
- existing choice-level quantity and lifecycle boundaries are unchanged;
- no model or migration change was required.

## Verification and Audit

- Local and test Django system checks passed.
- Local and test migration dry-run checks reported no changes.
- Local and test migration-state checks passed.
- The 79-test focused P4.9f run passed after slice-local assertion/rendering repair; the affected material-form tests re-passed after final percentage-input hardening.
- The final PostgreSQL-backed full suite passed: 278 tests.
- `git diff --check` passed.
- Integrity result: `PASS` for scope, Business isolation, atomic recovery, candidate-versus-confirmed truth, accessibility baseline, HTMX server truth, hosted compatibility, and regression boundaries.
- The last released branch state is aligned with the actual remote and has successful exact-SHA CI; Git/GitHub remain the metadata authority.
- Owner/browser acceptance: `PASS WITH NOTES`; P4.9 is technically sound, while broader Product create/edit UX remains inconvenient and insufficiently assistant-like for a later UX-focused slice or phase.

## Current Gate and Next Work

- Current gate: P4.10 Phase 4 Audit and Transition.
- Next work: run the Phase 4 audit against the roadmap, clothing data spec, code, tests, Git alignment, and exact-SHA CI evidence before closing Phase 4.
- Do not begin inventory, availability, measurements, readiness, buyer replies, deployment, or broad UX redesign as part of P4.10.
- Routine successful delivery metadata remains in Git/GitHub.

## Active Blockers and Decisions

- P4.9 has no remaining technical or owner-acceptance blocker.
- UX note: the current Product create/edit surface is functionally accepted but not yet the desired smart assistant-style operational experience; treat this as later UX work, not a Phase 4 semantic-recognition blocker.
- Material confirmation placement and wording are resolved for P4.9f: compact editable rows follow recognition feedback.
- Material alias policy is resolved for P4.9f only: no alias persistence or automatic learning; any future material vocabulary/alias manager needs a separately approved slice.
- Unrelated later-phase owner decisions remain where recorded in controlling documents.

## Current Documentation Sync Release Set

- `BUILD_PLAN.md`
- `DEVELOPMENT_NOTES.md`
- `changelog_checkpoint.md`

Proposed commit: `docs: record p4.9 owner acceptance notes`

## Handoff Guardrails

- Preserve the Django modular monolith, PostgreSQL, Templates, HTMX server truth, Alpine local state, authenticated seller workflow, and Business isolation.
- Preserve observed text → candidate → confirmed fact separation.
- Preserve choice-level stock truth and keep lifecycle separate from computed availability.
- Do not stage, commit, push, change authentication/remotes, or modify frozen/private documents outside the approved release workflow.
- Never stage secrets, local databases, media, caches, dumps, logs, backups, or owner-private workflow artifacts.
