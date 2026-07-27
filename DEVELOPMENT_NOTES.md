# Development Notes

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Update rule: update only for a meaningful decision, rejected alternative, trade-off, bug, workaround, or engineering lesson
- Read during context load: after APP_EXPERIENCE_PLAN.md
- Daily implementation log: no

## Purpose

This document records why meaningful product, architecture, workflow, and UX decisions were made.

It is not:

- a changelog;
- a phase tracker;
- a duplicate of BUILD_PLAN.md;
- a copy of frozen scope documents;
- a commit history.

## Initial Decisions

### 2026-07-27 - Rebuild from discovery evidence

Decision:
Build the portfolio project from zero instead of publishing or copying the unfinished prototype.

Reason:
The prototype validated behavior and exposed backend, documentation, and UI/UX risks, but it has no reliable Git history and contains prototype-era coupling.

### 2026-07-27 - Seller-first source of truth

Decision:
Build the private seller workflow before public buyer features.

Reason:
Public catalogs, assistants, and later automation cannot be trusted when seller-maintained price, stock, size, color, and availability are stale.

### 2026-07-27 - Honest Git history

Decision:
Git history continues honestly from the existing remote initial README commit, and the next commit will be the first substantive rebuild-planning commit.

Reason:
Do not fabricate, backdate, reconstruct fake implementation history from the earlier prototype, force push, or delete the existing public remote history.

### 2026-07-27 - Preserve existing remote history

Decision:
Use the existing public GitHub repository `https://github.com/OSINTmedia/facebook_ERP` and preserve its `main` branch initial README commit `dce852b`.

Reason:
The remote repository already exists and contains one initial commit. The first substantive rebuild commit should continue chronologically from that history instead of replacing it.

### 2026-07-27 - Repository hygiene before baseline commit

Decision:
Create a root `.gitignore` before the first substantive rebuild-planning commit.

Reason:
The repository must exclude secrets, local environments, Python cache, media uploads, backups, database dumps, logs, coverage output, and private local workflow notes before any baseline documentation commit is staged.

### 2026-07-27 - Modular monolith

Decision:
Use Django and PostgreSQL in a modular monolith.

Reason:
The project benefits from integrated auth, forms, migrations, transactions, testing, admin, and server-rendered workflows without premature microservices or API-first complexity.

### 2026-07-27 - Variant-level stock

Decision:
Stock truth belongs to product choices/variants.

Reason:
A clothing product may be available in one size/color and sold out in another.

### 2026-07-27 - Structured clothing data boundary

Decision:
Document clothing product attributes, category-specific measurements, variant data, and fit guidance in `docs/domain/CLOTHING_DATA_SPEC_V1.md` before freezing product scope.

Reason:
The active planning docs previously covered size, color, and quantity but did not define material, fit, garment measurements, category templates, or fit guidance. These need owner-approved boundaries before models or forms are built.

### 2026-07-27 - Computed availability

Decision:
Availability is computed from product lifecycle and active choice quantities.

Reason:
Lifecycle and sellability represent different system states.

### 2026-07-27 - Deterministic replies before LLM

Decision:
Seller-ready replies are generated from stored facts and computed state.

Reason:
An LLM must not invent or own price, stock, size, color, lifecycle, or availability truth.

### 2026-07-27 - UI/UX as architecture

Decision:
Navigation, return paths, first viewport, mobile density, feedback, and page responsibility are defined before screens accumulate features.

Reason:
The discovery prototype showed that late UI correction can become a large refactoring effort and may introduce regressions.

### 2026-07-27 - Micro-slice execution workflow

Decision:
Work proceeds through context load, next-step report, owner approval, implementation, verification, manual test, integrity audit, documentation sync, Git checkpoint, and commit/push approval.

Reason:
The workflow prevents context loss, scope creep, stale documentation, and unreviewable AI-generated diffs.
