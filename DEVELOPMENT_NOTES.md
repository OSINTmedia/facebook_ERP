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
Git history continues honestly from the existing remote initial README commit. The first substantive rebuild-planning commit is `549db75 docs: add portfolio rebuild planning baseline`.

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

### 2026-07-28 - Django 5.2 dependency baseline

Decision:
Use Django 5.2 LTS on Python 3.13 with Psycopg 3, django-environ, django-htmx, pytest, and pytest-django as the initial dependency baseline.

Reason:
This gives the rebuild a stable Django/PostgreSQL foundation compatible with the planned backend-capable demo, server-rendered HTMX workflows, environment-based settings, and automated tests without introducing app code, frontend build tooling, or deployment-specific services before their approved slices.

### 2026-07-29 - Neutral Django project package

Decision:
Use `config` as the internal Django project package for the clean scaffold.

Reason:
This keeps the scaffold conventional and avoids treating the unresolved final public project/repository name as an implementation blocker. Product-facing naming remains owner-controlled and can evolve independently from the internal settings package.

### 2026-07-29 - Production settings fail fast without provider lock-in

Decision:
Keep non-database local settings placeholder-friendly, keep test settings explicit, and make production settings fail during Django startup unless `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and `DATABASE_URL` are provided. Production settings also reject `DJANGO_DEBUG=True`.

Reason:
The rebuild needs production-safe runtime boundaries before deployment work, but provider-specific configuration, real secrets, and hosting decisions remain deferred. Failing fast prevents accidental insecure startup while preserving the planned hosted Django/PostgreSQL demo path.

### 2026-07-29 - PostgreSQL-only configuration baseline

Decision:
Reject non-PostgreSQL `DATABASE_URL` values during settings import and keep the Django test database name explicit and separate from the development database.

Reason:
The portfolio app needs database behavior that matches the planned PostgreSQL demo before models and constraints are introduced. Keeping this as configuration-only avoids silently creating local database state while preventing SQLite drift.

### 2026-07-29 - Local DATABASE_URL fails fast

Decision:
Require `DATABASE_URL` for local and test settings instead of falling back to executable placeholder PostgreSQL credentials.

Reason:
A missing `.env` previously attempted to authenticate with example credentials and produced a misleading PostgreSQL password failure. Failing at settings import makes the environment contract explicit while preserving the PostgreSQL-only boundary.

### 2026-07-29 - Configuration approval is not runtime readiness

Decision:
A database configuration baseline is not considered fully operational until the application proves a direct PostgreSQL connection, migration access, test execution, local server startup, and HTTP response.

Incident summary:
The local `.env` was initially missing, executable example credentials caused misleading authentication attempts, and one run used system Django instead of the project virtual environment. A project-specific PostgreSQL role/database was then created manually, the ignored `.env` was aligned with those local credentials, and direct connection, migrations, tests, and local server verification passed.

Reason:
Infrastructure gates must use runtime evidence rather than configuration inspection alone. HTTP `200` alone also does not prove a shell is ready; templates, static CSS, `404` behavior, semantic structure, and phase-specific acceptance criteria must be verified separately.

### 2026-07-30 - Custom user baseline needs clean migration state

Decision:
Introduce the custom seller user model before Business or catalog schema, and do not silently rewrite the existing local development database after default Django auth/admin migrations were already applied.

Incident summary:
P2.1 added `accounts.User` as the custom email-based auth model. The existing local development database had already applied `admin.0001_initial` before the new `accounts.0001_initial` dependency existed, so Django reported `InconsistentMigrationHistory`. Local tests were also blocked because the configured PostgreSQL role could not create the test database.

Reason:
Django custom user models need to be established before dependent app migrations become part of the project baseline. The safe recovery path is an owner-approved PostgreSQL verification strategy, such as rebuilding the disposable local development database and enabling test database creation, rather than hiding the issue with SQLite or silently mutating local database state.

Resolution:
The owner approved and completed the local-only PostgreSQL unblock by rebuilding the disposable development database while it contained no seller or product data, preserving ignored `.env` credentials, and granting test database creation capability to the local development role. The clean migration graph now applies `accounts.0001_initial` before `admin.0001_initial`, and both the focused accounts tests and full test suite pass against PostgreSQL. Local `CREATEDB` exists only to support this development/test workflow and is not a production database-role recommendation.

### 2026-07-30 - Protect Business ownership boundary from silent owner deletion

Decision:
Use `on_delete=PROTECT` for the initial `Business.owner` relationship.

Reason:
The Business row is the tenant boundary future seller-owned data will depend on. Until an owner-approved account/business lifecycle policy exists, protecting the owner relationship prevents accidental deletion from silently removing the ownership boundary while keeping active business selection and deletion workflows deferred.

### 2026-07-30 - Authentication baseline keeps redirects and logout server-owned

Decision:
Build the first seller login flow on Django's `LoginView` and `LogoutView`, keep the shell behind `LoginRequiredMixin`, normalize email input in the authentication form, reject unsafe external `next` redirects through Django's built-in checks, and require POST for logout.

Reason:
This keeps P2.3 limited to a minimal server-rendered authentication baseline while preserving server-side validation, CSRF-protected session exit, safe return paths, and no seller navigation before authentication. Signup, password reset, demo accounts, business selection, and owner-scoped object access remain separate approved slices or owner decisions.

### 2026-07-30 - Demo seller access is environment-gated and explicit

Decision:
Keep synthetic demo seller access disabled by default, expose configured demo credentials on the login page only when explicitly enabled by environment, and create or reset the account only through an explicit management command.

Reason:
The portfolio demo needs a repeatable seller login without creating a registration flow or hardcoding a password in tracked source. Environment gating, placeholder-only committed configuration, ignored local values, Django password hashing, and no automatic startup seed keep the demo account separate from admin, database, production, and personal credentials.

### 2026-07-31 - Active business resolution is read-only and policy-limited

Decision:
Add a small read-side Business selector boundary that filters by authenticated owner, returns no active business when none exists, and refuses multiple-business resolution until an owner-approved active-business policy or switcher exists.

Reason:
Future seller-owned queries need one reusable ownership boundary before catalog objects exist, but P2.4 should not silently create Business rows or decide the unresolved one-business-versus-switcher policy. Making the unsupported multi-business state explicit keeps later Product, dashboard, and HTMX endpoints from copying prototype-style implicit first-business behavior.

### 2026-08-01 - Product model baseline excludes unresolved catalog behavior

Decision:
Introduce the first `catalog.Product` model as a business-owned identity and stored-lifecycle baseline only, with `draft` and `active` lifecycle values, and leave price, choices, stock, availability, recognition, media, archive/restore, and Product UI to later approved micro-slices.

Reason:
Phase 3 needs a concrete Product table before forms and workflows can be built, but the unresolved price policy, choice/variant behavior, archive terminology, recognition scope, and stock service boundaries should not be silently decided by the first model migration. Keeping the baseline small preserves Business ownership isolation while avoiding premature schema commitments.

### 2026-08-01 - Product form keeps ownership server-assigned

Decision:
Expose only `name`, `description`, and stored `lifecycle` through the baseline `ProductForm`; keep `business` assignment outside the form and leave price, choices, stock, availability, recognition, material facts, measurements, media, and Product UI to later approved slices.

Reason:
A seller-submitted Product form must not be able to choose or spoof the Business ownership boundary. Keeping the first form aligned to the existing Product model baseline provides reusable server-side validation without silently resolving later catalog policy decisions.

### 2026-08-01 - First Product list is read-only and policy-limited

Decision:
Make the first Product UI route a read-only, authenticated list scoped through the active Business resolver, and return an explicit unsupported state when a seller owns multiple Businesses.

Reason:
P3.3 needs to expose existing Product records without expanding into create/edit, stock, recognition, search, or final workspace-card behavior. Reusing the existing Business resolver keeps cross-business isolation centralized and avoids silently deciding the unresolved one-business-versus-switcher policy.

### 2026-08-01 - Product create/edit keeps the first mutation boundary narrow

Decision:
Add Product create/edit routes around the existing ProductForm, assign Business ownership only from the resolved active Business, hide cross-business Product edits with `Http404`, and keep no-Business and multiple-Business states explicit instead of creating or selecting a workspace.

Reason:
P3.4 introduces the first seller Product mutation path, so it needs stricter ownership behavior than the read-only list while still avoiding later catalog decisions. Price, choices, stock, availability, recognition, material, measurements, media, Product Detail, clone, archive, and HTMX behavior remain separate approved slices because adding them here would turn the baseline Product form into the broad product bundle that the roadmap deliberately defers.

### 2026-07-27 - Variant-level stock

Decision:
Stock truth belongs to product choices/variants.

Reason:
A clothing product may be available in one size/color and sold out in another.

### 2026-07-27 - Initial structured clothing data boundary

Decision:
Document clothing product attributes, category-specific measurements, variant data, and fit guidance in `docs/domain/CLOTHING_DATA_SPEC_V1.md` before freezing product scope.

Reason:
The active planning docs previously covered size, color, and quantity but did not define material, fit, garment measurements, category templates, or fit guidance. These need owner-approved boundaries before models or forms are built.

Status:
Superseded by the 2026-07-28 description-first semantic recognition decision below. The current direction keeps material as a small typed semantic fact and defers detailed measurements to a separate approved micro-slice.

### 2026-07-28 - Description-first semantic recognition

Decision:
Keep the product assistant-first. Product description is the primary seller input, while recognition separates observed text, candidate meaning, and confirmed structured fact.

Reason:
The seller should not manage a large ecommerce form. Existing Product Type and Tag recognition should continue, material becomes a small typed semantic fact when confirmed, and buyer replies must use confirmed facts only.

### 2026-07-28 - Measurements deferred from the first product form

Decision:
Detailed garment measurements remain a separate approved micro-slice.

Reason:
Measurements need type, value, unit, method, and a clear product-or-choice boundary before they can safely support search, readiness, or buyer replies. Adding them too early would turn the product form into the kind of large fashion specification the rebuild is avoiding.

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

### 2026-07-27 - Micro-slice execution workflow Version 1

Decision:
The original workflow separated delivery into multiple checkpointed stages before Release closure was formalized.

Reason:
The workflow prevents context loss, scope creep, stale documentation, and unreviewable AI-generated diffs.

Status:
Superseded by the 2026-08-01 Workflow Version 2 delivery closure decision.

### 2026-08-01 - Workflow Version 2 delivery closure

Decision:
One functional micro-slice now uses one five-prompt cycle and closes through a single Release step; successful push/CI is not a documentation micro-slice.

Reason:
Documentation stores stable project truth while Git/GitHub stores exact delivery metadata such as commit hashes, remote alignment, CI runs, and CI conclusions. Post-push documentation is exceptional for failures, divergence, blockers, phase/gate closure, deployment/demo/public-release changes, or public factuality correction, not routine delivery bookkeeping.

### 2026-07-28 - Private workflow prompt stays local

Decision:
Keep `codex_prompt_ERP.txt` as a private local workflow prompt file and exclude it from Git.

Reason:
The file contains the owner's recurring prompt sequence for running Codex micro-slices. The public repository should expose the project documentation and implementation history, while private local prompt mechanics should not become repository authority.

### 2026-07-28 - Owner-controlled documents frozen for Phase 1 baseline

Decision:
Treat `docs/Portfolio_MVP_V1.md`, `docs/Technical_Planning_v1.md`, `docs/domain/CLOTHING_DATA_SPEC_V1.md`, and `docs/User_Journey_Freeze_v1.md` as frozen owner-controlled baseline documents for the start of Phase 1.

Reason:
The rebuild needs stable product, technical, domain, and journey boundaries before implementation. Future `OWNER_DECISION_REQUIRED` items remain explicit and deferred instead of being silently approved.

### 2026-07-28 - Assistant-first synthesis confirms product boundary

Decision:
Use `docs/discovery/ASSISTANT_FIRST_PRODUCT_DESIGN_SYNTHESIS.md` as discovery support for the assistant-first product thesis, not as direct implementation authority.

Reason:
The synthesis clearly explains the product's core boundary: assistant-first seller operations, not another ecommerce administration system. That reasoning supports active plans, but active frozen and semi-frozen documents remain the controlling sources.
