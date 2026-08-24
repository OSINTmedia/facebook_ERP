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

### 2026-08-01 - Recognition service starts as a pure candidate contract

Decision:
Implement the first semantic recognition boundary as a pure `catalog.recognition` service that preserves observed seller text, returns immutable unconfirmed candidates from caller-supplied terms and aliases, and leaves confirmed facts empty until a later seller-confirmation/persistence slice.

Reason:
Phase 4 needs executable recognition semantics before Product Type, Tag, material, choice, or form integration models exist. Keeping P4.1 database-free prevents the assistant layer from silently becoming structured truth, avoids unresolved alias/material UI decisions, and gives later slices a tested contract for observed text versus candidate meaning versus confirmed facts.

### 2026-08-01 - Product Type vocabulary is business-scoped before Product assignment

Decision:
Introduce `catalog.BusinessProductType` as the business-owned canonical Product Type vocabulary and feed Product Type recognition only from the supplied Business. Leave Product assignment, confirmation UI, aliases, Tags, and type-management screens to later approved slices.

Reason:
Existing Product Type recognition needs a persisted vocabulary source, but a recognized type candidate is still not a confirmed Product fact. Scoping the vocabulary through Business prevents cross-seller leakage while avoiding unresolved decisions about how sellers create, manage, alias, and confirm Product Types in the UI.

### 2026-08-02 - Tag vocabulary is business-scoped before Product tagging

Decision:
Introduce `catalog.BusinessTag` as the business-owned canonical Tag vocabulary and feed Tag recognition only from the supplied Business. Leave Product tag assignment, tag confirmation UI, aliases, management screens, and readiness impact to later approved slices.

Reason:
Tags are useful as reusable seller vocabulary, but a recognized tag candidate is still not a confirmed Product tag and must not affect readiness or buyer replies before explicit confirmation behavior exists. Scoping the vocabulary through Business prevents cross-seller leakage while preserving the unresolved owner decision about whether tags affect readiness or only organization/search.

### 2026-08-02 - Aliases normalize vocabulary without becoming product truth

Decision:
Represent Product Type and Tag aliases as separate business-owned vocabulary rows, validate that each alias points to a canonical value in the same Business, prevent per-destination alias/name collisions, and feed aliases into recognition while returning canonical unconfirmed candidates.

Reason:
Seller wording should normalize over time without leaking across Businesses or turning a matched alias into a confirmed Product fact. Keeping aliases separate from Product assignment, confirmation UI, material alias policy, and management screens preserves the observed/candidate/confirmed boundary and keeps unresolved owner decisions out of the baseline schema.

### 2026-08-02 - Material facts persist only after confirmation

Decision:
Store material as a Product-owned, Business-scoped confirmed fact with canonical material, optional percentage, original seller wording, source, and confirmed-only state. Keep material recognition candidates, material aliases, Product form integration, readiness, and buyer replies outside the first material persistence slice.

Reason:
Material can affect buyer answers, but it must not become buyer-facing truth from description recognition alone. Persisting only confirmed facts gives later recognition, confirmation UI, readiness, and deterministic reply slices a durable backend boundary without deciding the unresolved material UI or alias policy early.

### 2026-08-02 - Material recognition reads confirmed seller facts before alias policy

Decision:
Derive material recognition candidates from a Business's confirmed `ProductMaterialFact` canonical material values, returning transient unconfirmed candidates only. Do not introduce material aliases, a global textile dictionary, Product form integration, readiness, or buyer replies in this baseline.

Reason:
This lets recognition reuse seller-confirmed material truth without promoting observed description text into buyer-facing fact. Keeping material aliases and confirmation UX out of the helper preserves Business isolation and avoids silently resolving the unresolved material UI and alias policy.

### 2026-08-02 - Size/color recognition stays suggestion-only before choice rows

Decision:
Recognize caller-supplied size and color values as transient `CHOICE_SIZE` and `CHOICE_COLOR` candidates only. Do not introduce a global size/color dictionary, `ProductChoice` persistence, duplicate-choice policy, Product form integration, stock, availability, readiness, or buyer replies in this baseline.

Reason:
Size and color are eventual stock-bearing choice truth, so description recognition must not silently create confirmed variants. Keeping P4.6 suggestion-only lets later form and choice-model slices reuse the recognition boundary without resolving the owner-required duplicate size/color policy early.

### 2026-08-14 - Preserve released Phase 4 numbering

Decision:
Keep the historical P4.1 through P4.6 slice numbering already present in Git and CI history, and require owner approval for the duplicate size/color choice policy before implementing `ProductChoice`.

Reason:
Renaming released slices after they are committed, pushed, and CI-passed would make the documentation harder to reconcile with repository history. Persisted choice behavior depends on a policy decision, while P4.6 remains suggestion-only recognition.

### 2026-08-14 - Duplicate ProductChoice rows remain distinct in V1

Decision:
Allow duplicate size/color rows within one Product, including case-insensitive, trim-normalized matches. Each row is a distinct sellable choice with its own identity, quantity, and active state. Do not merge rows automatically; future inventory mutations must target a specific `ProductChoice` row. Defer aggregation, buyer-facing wording, and UI disambiguation for similar rows.

Reason:
The released P4.7 baseline encoded the opposite policy with a normalized uniqueness constraint. Preserve honest migration and Git history by removing that released constraint through a forward corrective migration rather than rewriting migration `0006` or the previous commit.

### 2026-08-17 - Product and choice writes use one atomic bundle boundary

Decision:
Keep `ProductForm` and `ProductChoiceForm` field-restricted, use a custom inline formset for aggregate lifecycle and row validation, and assign Business/Product ownership inside a dedicated atomic bundle coordinator. Validate Product first so the submitted lifecycle drives the choice rule. Keep duplicate choice rows distinct and defer view/template integration to P4.9.

Reason:
Product and choice rows form one seller mutation even though their field validation belongs in separate forms. A transaction-scoped coordinator prevents partial persistence, keeps ownership input server-controlled, and lets later views remain thin without moving inventory or availability behavior into the formset.

### 2026-08-17 - Automatic preview stays transient before controlled Size/Color vocabulary

Decision:
Show Product Type, Tag, material, size, and color recognition candidates automatically beside the description through a debounced HTMX request with a full-page fallback. Keep the preview read-only: Product Type/Tag vocabulary and aliases, confirmed material facts, and current confirmed ProductChoice size/color values provide Business-scoped terms, but no candidate is confirmed or persisted. Treat raw ProductChoice-derived size/color terms as a temporary baseline. Before candidate transfer, add seller-managed Business-scoped canonical Size/Color vocabularies, multilingual aliases, dropdown-only selection, contextual value creation, and a safe forward migration for existing choices.

Reason:
P4.9b can prove the observed/candidate/confirmed and automatic-assistant interaction without silently adding schema or writes. The owner rejected unrestricted open-text size/color as the final workflow because typos can become repeated suggestions. A dedicated forward slice preserves honest history, aligns the frozen `Select size` / `Select color` journey with Georgian-first multilingual normalization, and avoids turning every description word into a dictionary entry.

### 2026-08-17 - Product choices reference controlled Business Size/Color vocabulary

Decision:
Store canonical Size and Color values in Business-owned vocabularies and make `ProductChoice` reference them through Business-scoped dropdowns. Preserve every historical ProductChoice row and its quantity during migration; case/trim-equivalent legacy labels within one Business reuse the deterministic first canonical value without merging choice rows. Aliases are explicit seller-approved recognition inputs. Automatic alias learning, automatic form filling, and silent candidate confirmation remain deferred.

Reason:
Canonical dropdown truth prevents new spelling drift and cross-Business leakage while multilingual aliases can absorb known Georgian/English wording. Keeping automatic assistance outside this baseline preserves the observed-to-candidate-to-confirmed boundary and lets the later UX refinement address lazy or chaotic input without silently inventing structured truth.

### 2026-08-17 - Size/Color vocabulary needs a visible maintenance surface

Decision:
Extend the still-unreleased P4.9d delivery with P4.9d_expand: an authenticated Business-scoped Size/Color vocabulary page that shows aliases grouped under each canonical value and supports add, canonical rename, explicit alias-list replacement, and activation/deactivation. Keep canonical deletion, merging, automatic alias learning, and Product Type/Tag/material administration outside this extension.

Reason:
Contextual creation prevents the Product form from becoming blocked, but it does not let a seller prepare vocabulary in advance or understand which Georgian, English, and inconsistent wording resolves to one canonical value. Editing the existing canonical row preserves ProductChoice foreign keys; atomic alias replacement prevents partial dictionary state; deactivation safely removes a value from new recognition and dropdown selection without deleting historical choice truth. Locking the owning Business row serializes concurrent vocabulary writes so cross-table canonical/alias validation cannot race inside these service boundaries.

### 2026-08-21 - Candidate transfer binds the displayed canonical meaning

Decision:
Include the displayed canonical Size/Color meaning in the explicit candidate-transfer intent and require the server to match it against the freshly recomputed Business-scoped candidate before changing copied formset data.

Reason:
Candidate index, semantic destination, and observed-text span alone did not detect a concurrent vocabulary rename or alias reassignment that preserved the same span but changed its canonical meaning. Binding the displayed meaning prevents the seller's explicit action from transferring a different current interpretation while retaining the no-write-before-bundle-save boundary.

### 2026-08-21 - Confirmed Product classification uses explicit Business-owned associations

Decision:
Represent confirmed Product Type as one optional protected canonical reference and confirmed Tags through an explicit `ProductTag` association that carries Business ownership. Persist type/tag selection, correction, and removal only through the existing atomic Product bundle after explicit canonical form selection; never preselect or attach recognition candidates automatically.

Reason:
The nullable type reference preserves existing Products without inventing classification, while the explicit tag association lets the mutation boundary assign and validate Business ownership instead of relying on an implicit many-to-many write. Keeping recognition preview separate from confirmed controls preserves observed-to-candidate-to-confirmed truth, deterministic error recovery, and the existing inventory, availability, readiness, and buyer-reply boundaries.

### 2026-08-21 - Product classification shares the controlled vocabulary manager

Decision:
Extend the authenticated Product vocabulary surface with Business-scoped Product Types and Tags instead of adding a separate taxonomy application. Use the same explicit canonical/alias creation, rename, full alias-list replacement, activation/deactivation, collision validation, and atomic Business-locking boundary as Size/Color while preserving destination-specific models and Product truth.

Reason:
P4.9e confirmation is not usable when a seller cannot create its vocabulary. A shared surface keeps navigation compact without merging semantic destinations: inactive Type/Tag values leave existing Product associations intact but disappear from new confirmation and recognition, and no description text creates vocabulary or confirmed truth automatically.

### 2026-08-21 - Owner browser acceptance requires current local migration state

Decision:
Treat `migrate --check` against the local owner-review database as a required operational precondition before declaring a migration-bearing browser slice ready or accepted; test-database migration success alone is insufficient.

Reason:
P4.9e_expand tests passed on newly migrated test databases while the running local server still used a schema without the new Type/Tag activation fields, breaking Product Add with an undefined-column error. Applying the additive migration restored the route without data loss; explicit local migration-state verification prevents the same false PASS.

### 2026-08-21 - Material confirmation stays explicit and does not learn aliases

Decision:
Place compact confirmed-material rows immediately after Product recognition feedback. A seller may explicitly transfer a freshly recomputed material candidate into an unsaved row, then correct or remove the canonical material, optional percentage, original wording, and source before the atomic Product bundle saves it as confirmed. Do not add a material-alias model or learn an alias from corrected wording in P4.9f.

Reason:
The candidate action reduces repeated typing without crossing the observed-to-candidate-to-confirmed boundary. Recomputing and binding candidate identity prevents stale or changed interpretations from being transferred, while deferring alias persistence avoids treating one Product correction as reusable Business vocabulary without a separately approved collision, maintenance, and deactivation policy.

### 2026-08-21 - Technical acceptance is separate from assistant UX quality

Decision:
Accept P4.9f and the wider P4.9 Product create/edit recognition integration as technically correct after owner/browser review, while recording that the current Product create/edit surface is still inconvenient and does not yet feel like the intended smart assistant-style operational application.

Reason:
Phase 4 validates the semantic-recognition, controlled vocabulary, confirmed-fact, choice truth, and Business-isolation boundaries. The owner UX note is important, but it should drive a separately approved UX-focused slice or phase instead of reopening technically accepted P4.9 behavior or silently broadening P4.10 beyond audit and transition.

### 2026-08-24 - Inventory adjustments are immutable transition facts

Decision:
Record each inventory adjustment against one Business, exact ProductChoice row, and authenticated Business-owner actor with before quantity, after quantity, nonzero delta, and creation time. Enforce consistent nonnegative arithmetic in PostgreSQL, reject cross-Business facts in the model boundary, and block application-level update/delete behavior. Do not let the ledger baseline mutate stock or introduce reason codes; a later transaction-safe inventory service must atomically pair the stock write with record creation.

Reason:
An immutable before/after fact makes stock history independently auditable and preserves the identity of duplicate-looking choice rows. Separating record integrity from the later concurrency-sensitive mutation service avoids silently resolving direct-set or movement-reason policy while ensuring the service has a trustworthy destination.

### 2026-08-24 - Stock mutation and adjustment creation share one locked transaction

Decision:
Make `apply_choice_quantity_delta` the first centralized quantity mutation boundary. Accept only integer `+1` or `-1`, lock the current Business-owned ProductChoice row with `select_for_update()`, reject underflow and ownership violations before writing, and commit the quantity transition with its immutable `InventoryAdjustment` in one transaction. Compute availability from the committed choice-level state without changing lifecycle or `is_active`.

Reason:
The adjustment ledger is only trustworthy when the stock write and its transition fact cannot diverge. PostgreSQL-backed concurrent-decrement coverage verifies that row locking prevents lost updates and duplicate transition facts. The concurrency fixture also restores the latest migration graph after the existing historical migration test leaves the disposable test database at an earlier catalog state, keeping the full suite schema-isolated without changing production migrations or runtime behavior.

### 2026-08-14 - Superseded: normalized duplicate choices were blocked

Status:
Superseded by the owner correction above; retained to preserve the decision trail.

Decision:
Block case-insensitive, trim-normalized duplicate size/color combinations within one Product across active and inactive rows. Reuse or reactivate the existing choice instead of creating a second stock-bearing row; allow the same normalized combination on another Product. P4.7 owns individual choice-row persistence and integrity, while P4.8 owns atomic Product-plus-choice validation and the rule that an active Product requires at least one valid active choice.

Reason:
One normalized row per sellable combination prevents split stock truth and ambiguous reactivation. Keeping aggregate validation in P4.8 avoids breaking the current Product create/edit flow before a choice formset and atomic bundle-save boundary exist.

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
One functional micro-slice closes through one bounded implementation, audit, and release cycle; successful push/CI is not a documentation micro-slice.

Reason:
Documentation stores stable project truth while Git/GitHub stores exact delivery metadata such as commit hashes, remote alignment, CI runs, and CI conclusions. Post-push documentation is exceptional for failures, divergence, blockers, phase/gate closure, deployment/demo/public-release changes, or public factuality correction, not routine delivery bookkeeping.

### 2026-07-28 - Private workflow artifacts stay local

Decision:
Keep owner-specific workflow artifacts local and excluded from Git.

Reason:
The public repository should expose product reasoning, implementation boundaries, verification evidence, and honest history without publishing owner-specific operating mechanics.

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
