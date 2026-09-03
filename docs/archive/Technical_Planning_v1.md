# Technical Planning V1

## Document Metadata

- Status: FROZEN
- Version: 1.0
- Freeze authority: owner only
- Frozen boundary: unresolved `OWNER_DECISION_REQUIRED` items remain deferred unless separately approved

## 1. Technical Objective

RECOMMENDED_FROM_EVIDENCE: The rebuild should create a clean, portfolio-grade Django application that demonstrates disciplined backend modeling, source-of-truth separation, operational UI architecture, automated verification, safe repository hygiene, reproducible setup, CI, and deployable demo readiness.

VALIDATED_PROTOTYPE_LESSON: The source prototype proves the product direction but also shows why the rebuild must not copy code blindly: business logic is concentrated in large views, stock mutation paths are inconsistent, readiness is duplicated, UI state can become stale after HTMX updates, and operations/deployment assets are incomplete.

## 2. Architecture Style

RECOMMENDED_FROM_EVIDENCE: Use a Django modular monolith with explicit app and service boundaries. Avoid microservices, event buses, broad ERP abstractions, and premature REST/API-first architecture.

RECOMMENDED_FROM_EVIDENCE: Keep server-rendered pages as the default. Use HTMX for targeted interactions and Alpine.js for local UI state only where the behavior is small, isolated, and accessible.

OBSOLETE_OR_REJECTED: Do not preserve prototype-era `_table_exists()` runtime branching, fat view orchestration, or implicit first-business auto-creation as final architecture.

## 3. Proposed Technology Stack

| Technology | Status | Justification |
|---|---|---|
| Python | RECOMMENDED_FROM_EVIDENCE | Current prototype and portfolio objective are Django/Python oriented |
| Django | RECOMMENDED_FROM_EVIDENCE | Auth, forms, templates, admin, migrations, tests, and PostgreSQL support fit the product |
| PostgreSQL | RECOMMENDED_FROM_EVIDENCE | Relational ownership, constraints, and demo parity need real SQL behavior |
| Django Templates | RECOMMENDED_FROM_EVIDENCE | Source prototype validates server-rendered operational workflows |
| HTMX | RECOMMENDED_FROM_EVIDENCE | Useful for stock and inline taxonomy partials if update boundaries are explicit |
| Alpine.js | RECOMMENDED_FROM_EVIDENCE | Suitable for lightweight disclosure/copy/formset behavior, with accessibility constraints |
| Tailwind CSS | RECOMMENDED_FROM_EVIDENCE | Prototype uses utility styling; rebuild should use a controlled local build or documented CDN decision |

Alternatives deferred:

- React/Vue: DEFERRED_HYPOTHESIS until server-rendered interaction cannot support approved workflows.
- DRF/full REST API: DEFERRED_HYPOTHESIS until public catalog, chatbot, or order layers need an API.
- FastAPI: OBSOLETE_OR_REJECTED for V1 because Django gives faster integrated auth/admin/forms.
- SQLite-only demo: OWNER_DECISION_REQUIRED; PostgreSQL is recommended for parity with constraints.

## 4. Application Module Boundaries

| Module | Responsibility | Notes |
|---|---|---|
| `accounts` | User model, authentication forms, login/logout support | RECOMMENDED_FROM_EVIDENCE |
| `businesses` | Business workspace, active business selection, onboarding/default business policy | Redesign implicit auto-create behavior |
| `catalog` | Product, product choices, product media, taxonomy, lifecycle, product workspace queries | Keep views thin |
| `recognition` or `catalog.recognition` | Observed text, candidate meaning, vocabulary aliases, and confirmation flow | Assistant layer only; does not own truth until confirmed |
| `clothing` | Material facts, clothing-specific semantic boundaries, choice attributes, and deferred measurement capability | Keep domain profile boundary explicit; follow `docs/domain/CLOTHING_DATA_SPEC_V1.md` |
| `inventory` | Quantity mutation, availability computation, adjustment ledger | All quantity writes must pass through one service |
| `readiness` or `validation` | Product readiness and warning rules | Pure service, no view-decorated hidden inputs |
| `dashboard` | Cockpit query composition and attention summaries | Consume shared availability/readiness services |
| `reply` or `catalog.reply` | Deterministic seller-side buyer reply generation | No LLM truth ownership |
| `analytics` | Minimal usage events for portfolio/pilot evidence | Privacy and retention rules required |
| `demo` or management commands | Synthetic seed/reset utilities | Keep out of runtime seller workflow |

OWNER_DECISION_REQUIRED: Whether product relations are a V1 module or a deferred future boundary.

## 5. Data Model Direction

Planning-level entities:

- RECOMMENDED_FROM_EVIDENCE: `User` as authenticated seller identity.
- RECOMMENDED_FROM_EVIDENCE: `Business` as ownership/tenant boundary.
- OWNER_PROVIDED_DIRECTION: `Product` as catalog item with lifecycle, primary description/name, base price, currency, and timestamps.
- RECOMMENDED_FROM_EVIDENCE: `ProductChoice` or `ProductVariant` as the stock-bearing choice record.
- OWNER_PROVIDED_DIRECTION: `ProductMedia` or `ProductPhoto` as general product media with optional multiple-photo and primary-photo policy.
- OWNER_PROVIDED_DIRECTION: Clothing domain data should follow `docs/domain/CLOTHING_DATA_SPEC_V1.md`.
- OWNER_PROVIDED_DIRECTION: Recognition data separates observed text, candidate meaning, and confirmed structured fact.
- OWNER_PROVIDED_DIRECTION: Material is a small typed semantic fact when confirmed, with canonical material, optional percentage, original wording, confirmation state, and source.
- OWNER_PROVIDED_DIRECTION: Size and color belong to the stock-bearing choice record; description-recognized size/color may only suggest creating a choice.
- DEFERRED_HYPOTHESIS: Measurement records require type, value, unit, method, applicable product/choice boundary, seller note, and confirmation state before implementation.
- RECOMMENDED_FROM_EVIDENCE: `BusinessProductType` as controlled business vocabulary if approved.
- RECOMMENDED_FROM_EVIDENCE: `BusinessTag` and join table if approved.
- RECOMMENDED_FROM_EVIDENCE: `InventoryAdjustment` as complete stock audit record.
- RECOMMENDED_FROM_EVIDENCE: `UsageEvent` as minimal pilot/demo analytics.
- OWNER_DECISION_REQUIRED: `ProductRelation`.

No migration code is generated by this document.

## 6. Source-of-Truth Matrix

| Fact | Stored Source | Computed Layer | Consumer | Invariant |
|---|---|---|---|---|
| Ownership | `Business` and business FKs | Active-business resolver | All queries/forms/services | Every seller object is scoped to business |
| Lifecycle | Product field | Lifecycle policy service | Workspace, dashboard, replies | Lifecycle is not stock availability |
| Stock | Active choice quantity | Inventory service | Workspace, dashboard, replies | Product total is computed |
| Availability | None | Availability service | Dashboard, cards, filters, replies | Computed consistently everywhere |
| Price | Product price or approved price model | Reply/readiness service | Forms, cards, replies | Missing/free price meaning is explicit |
| Size/color | Choice profile fields | Display helper | Forms, cards, replies | No duplicate drift from label fields |
| Observed text | Product description | Recognition service | Search, candidate UI | Not buyer-facing structured truth |
| Candidate meaning | Recognition candidate object or transient service output | Recognition service | Confirmation UI | Not used in replies until confirmed |
| Confirmed fact | Type/tag/material/choice/measurement record depending on semantic destination | Domain services | Search, readiness, replies | Confirmed facts only drive buyer answers |
| Material | Confirmed material fact | Readiness/reply services when present | Confirmation UI, cards/replies if approved | Small typed semantic fact, not mandatory form sprawl |
| Garment measurements | Deferred measurement record | Future measurement service | Future optional measurement UI/replies | Requires type, value, unit, method, applies-to boundary |
| Fit guidance | Deferred seller guidance field or note | Future reply service if approved | Future optional UI/replies | Weight alone must not determine size |
| Type | Approved canonical type field | Readiness/search | Forms, filters, cards | One canonical type truth |
| Tags | Tag dictionary + join | Readiness/search if approved | Forms, filters, cards | Tags do not leak across businesses |
| Product media | Product media/photo record | Primary-media selector | Cards, forms, readiness | Multiple photos are general media, not clothing ontology |
| Readiness | None | Buyer-question coverage service | Dashboard, cards, replies | Concrete answer coverage, not completion percentage |
| Buyer reply | None | Deterministic reply service | Seller copy UI | Confirmed facts only, no invented claims |

## 7. Stored vs Computed State

- RECOMMENDED_FROM_EVIDENCE: Lifecycle is stored.
- RECOMMENDED_FROM_EVIDENCE: Availability is computed.
- RECOMMENDED_FROM_EVIDENCE: Readiness is computed.
- RECOMMENDED_FROM_EVIDENCE: Dashboard warnings/signals are computed from shared services.
- RECOMMENDED_FROM_EVIDENCE: Answer readiness is computed through readiness plus deterministic reply rules.
- OWNER_PROVIDED_DIRECTION: Observed text and candidate meaning are recognition state, not confirmed buyer-facing truth.
- OWNER_PROVIDED_DIRECTION: Readiness is buyer-question coverage, not a generic completion score.
- DEFERRED_HYPOTHESIS: Publication readiness is a future public-catalog boundary, not V1 state unless owner approves it.

## 8. Service Boundaries

- Product save: validates and saves product bundle, but delegates stock writes to inventory service.
- Quantity update: single service for increment, decrement, set, audit, events, and transition result.
- Availability: pure computation from lifecycle and active choices.
- Readiness: pure computation from product facts, no view decoration.
- Recognition: service boundary that parses product description into observed text, candidate meaning, and confirmation actions.
- Vocabulary aliases: business-scoped normalization for inconsistent seller wording.
- Clothing data: explicit service/schema boundary for material facts, choice-level size/color, and deferred measurement capability.
- Measurements: separate future service boundary; do not mix type/value/unit/method/applies-to decisions into the initial product-form slice.
- Clone: explicit command with validated clone mode and owner-approved stock-copy behavior.
- Search: query service with documented tokenization and filter scope.
- Deterministic answer: reply service that consumes confirmed stored facts and computed availability/buyer-question coverage.
- Return URLs: centralized safe internal return helper.
- Active business: centralized resolver with no hidden GET side effects.

## 9. Transaction and Integrity Rules

- RECOMMENDED_FROM_EVIDENCE: Product bundle save must be atomic.
- RECOMMENDED_FROM_EVIDENCE: Stock mutation must use transaction-safe updates, row locks, or database expressions to avoid lost updates.
- RECOMMENDED_FROM_EVIDENCE: Every stock-changing path writes `InventoryAdjustment`.
- RECOMMENDED_FROM_EVIDENCE: Cross-business joins are blocked in forms, services, tests, and database constraints where feasible.
- RECOMMENDED_FROM_EVIDENCE: A product cannot become partially persisted after successful validation.
- RECOMMENDED_FROM_EVIDENCE: Media writes require cleanup or documented failure behavior.
- OWNER_DECISION_REQUIRED: Whether direct stock edits in product form are allowed or moved to inventory-only controls.

## 10. Business Isolation

RECOMMENDED_FROM_EVIDENCE: Business isolation is release-blocking. Every product, choice, photo, tag, type, relation, adjustment, event, dashboard query, form queryset, and HTMX endpoint must be scoped through the active business.

Required tests:

- Seller cannot view another business's product.
- Seller cannot edit/archive/restore/clone another business's product.
- Seller cannot update another business's variant quantity.
- Seller cannot attach another business's tag/type.
- Search suggestions do not leak another business's product/type/tag terms.
- Dashboard counts only current business.

## 11. Authentication Direction

RECOMMENDED_FROM_EVIDENCE: Use email login with Django authentication. Public signup, password reset, email verification, and multi-staff permissions are not V1 requirements unless owner-approved.

RECOMMENDED_FROM_EVIDENCE: Seller-facing routes require authentication. Admin is for development/demo maintenance only and must not be the seller UI.

## 12. Validation Strategy

- RECOMMENDED_FROM_EVIDENCE: Use Django forms/formsets for server-side validation.
- RECOMMENDED_FROM_EVIDENCE: Client-side helpers are convenience only; server validation owns truth.
- RECOMMENDED_FROM_EVIDENCE: Validation messages should be Georgian, concrete, and action-oriented.
- RECOMMENDED_FROM_EVIDENCE: Minimum one valid choice is required for active sellable products.
- RECOMMENDED_FROM_EVIDENCE: Negative quantity is rejected.
- OWNER_PROVIDED_DIRECTION: Description-recognized size/color creates suggestions only; confirmed choices remain required for size/color truth.
- OWNER_PROVIDED_DIRECTION: Material candidates require confirmation before reply use.
- OWNER_PROVIDED_DIRECTION: Clothing measurements are deferred and must include type, value, unit, method, and product/choice boundary before buyer reply use.
- RECOMMENDED_FROM_EVIDENCE: Weight alone must not determine size.
- RECOMMENDED_FROM_EVIDENCE: No AI sizing is implemented in V1.
- OWNER_DECISION_REQUIRED: Price zero/null policy.
- OWNER_DECISION_REQUIRED: Duplicate size/color choice policy.
- OWNER_DECISION_REQUIRED: Tag readiness policy.
- OWNER_DECISION_REQUIRED: Exact material confirmation UI and alias policy.
- OWNER_DECISION_REQUIRED: Measurement convention and implementation micro-slice.

## 13. Testing Strategy

Required layers:

- Unit tests: pure helpers, normalization, alias matching, display labels.
- Service tests: availability, buyer-question coverage, deterministic replies, inventory mutation, recognition, clone.
- View/access tests: login required, business scoping, safe redirects, HTMX responses.
- Form/formset tests: product creation/editing, required fields, dynamic choices, invalid rows.
- Clothing/recognition tests: observed text does not become confirmed fact silently, Product Type/Tag aliases normalize, material confirmation gates reply use, negative material phrases do not create positive facts, size/color candidates suggest choices only, variant stock separation remains intact.
- Future measurement tests: measurement type/value/unit/method/applies-to boundary, no all-fields-required behavior, and buyer-reply wording after measurement scope is approved.
- Management-command tests: dry-run, scoped reset, confirm guard, protected users/businesses/media.
- Manual UX verification: mobile first viewport, return paths, HTMX failures, copy behavior, accessibility basics.
- CI gates: install, system check, migration check, tests.

Current source test audit:

- VERIFIED_BY_CURRENT_SOURCE: `apps/catalog/tests.py` contains meaningful tests for answer generation, list/detail answer UI, search by tag/type/size, clone message, HTMX restock response, product edit corrections, taxonomy recovery, sentinel hiding, and several safe return paths.
- VALIDATED_PROTOTYPE_LESSON: Other app test files are placeholders.
- RECOMMENDED_FROM_EVIDENCE: The rebuild should distribute tests by domain rather than centralizing almost all coverage in catalog tests.
- UNKNOWN: No tests were executed during reconnaissance, so no pass claim exists.

## 14. Critical Regression Matrix

| Scenario | Expected Result | Test Layer | Release Blocking |
|---|---|---|---|
| Cross-business product detail | 404/forbidden, no leak | View/access | Yes |
| Cross-business quantity update | 404/forbidden, no stock change | View/access/service | Yes |
| Product create valid bundle | Product, profile, choice, optional media/tags saved atomically | Form/view/service | Yes |
| Product create invalid bundle | Nothing partial persists | Form/view/service | Yes |
| Last active choice deletion | Blocked with clear error | Formset/view | Yes |
| Quantity 1 -> 0 | Stock becomes sold out and adjustment is logged | Service/view/HTMX | Yes |
| Quantity 0 -> 1 | Product restocks and adjustment is logged | Service/view/HTMX | Yes |
| Concurrent stock update | No lost update | Service/database | Yes |
| Draft with stock | Not buyer-available | Service/view | Yes |
| Archived with stock | Not buyer-available | Service/view | Yes |
| Search by approved fields | Results scoped to business and visible filters | Query/view | Yes |
| Recognition candidate unconfirmed | Candidate appears for review but does not drive buyer reply | Service/view | Yes |
| Description size/color | Suggests adding a choice; does not become generic tag truth | Service/form/view | Yes |
| Material candidate confirmed | Confirmed material can be used in buyer-question coverage and replies | Service/form/view | Yes |
| Readiness missing data | Buyer-question coverage does not show unsupported answers | Service/view | Yes |
| Deterministic reply missing price | Seller note, no invented price | Service/view | Yes |
| Sold-out reply | No availability claim | Service/view | Yes |
| Safe `next` internal URL | Redirects to internal context | View | Yes |
| External `next` URL | Rejected to safe fallback | View | Yes |
| Reset dry-run | Deletes nothing | Management command | Yes |
| Reset confirm scoped | Deletes only approved demo/catalog data | Management command | Yes |

## 15. Security and Repository Hygiene

Source audit findings:

- VERIFIED_BY_CURRENT_SOURCE: `.env` exists in the source project and must not be read into docs or published.
- VERIFIED_BY_CURRENT_SOURCE: `.gitignore` excludes `.env`, `.venv`, `staticfiles`, and `media/*` except `media/.gitkeep`.
- VERIFIED_BY_CURRENT_SOURCE: `.env.example` includes local placeholder values and PostgreSQL URL.
- VERIFIED_BY_CURRENT_SOURCE: `SECRET_KEY` has an insecure fallback in prototype settings.
- VERIFIED_BY_CURRENT_SOURCE: `DEBUG` defaults to true in `local.py`.
- VERIFIED_BY_CURRENT_SOURCE: media files and `backups/catalog_before_reset.json` exist in the source project.
- VERIFIED_BY_CURRENT_SOURCE: Admin registers many models and is not tenant-scoped for staff.
- VERIFIED_BY_CURRENT_SOURCE: most mutation views reject non-POST with `HttpResponseNotAllowed`.
- VERIFIED_BY_CURRENT_SOURCE: CSRF tokens are present in inspected POST forms.
- VERIFIED_BY_CURRENT_SOURCE: safe `next` helpers exist; `product_tag_toggle` still redirects to `HTTP_REFERER`.

Repository rules:

- RECOMMENDED_FROM_EVIDENCE: Never commit `.env`, real media, backups, database dumps, private logs, credentials, API keys, production secrets, or customer/seller data.
- RECOMMENDED_FROM_EVIDENCE: Commit `.env.example` with placeholders only.
- RECOMMENDED_FROM_EVIDENCE: Use production settings without insecure fallback secrets.
- RECOMMENDED_FROM_EVIDENCE: Centralize safe redirect handling and avoid raw `HTTP_REFERER` redirects.
- RECOMMENDED_FROM_EVIDENCE: Keep demo account credentials synthetic and documented only when safe.

## 16. Demo Data Strategy

RECOMMENDED_FROM_EVIDENCE: The online demo should use synthetic business, products, choices, stock states, photos, and usage events. No real seller/customer/media data should be copied from the source prototype.

Required synthetic states:

- Available product.
- Low-stock product.
- Partially sold-out product.
- Fully sold-out product.
- Draft product.
- Product missing price or photo.
- Product missing choice details.
- Product ready for deterministic reply.

OWNER_DECISION_REQUIRED: Whether demo uses a shared demo login, per-reviewer generated demo data, or a read-only public mode.

## 17. Reset and Recovery Strategy

VALIDATED_PROTOTYPE_LESSON: The source reset command is dry-run-first, can scope by business id, and protects users/businesses/schema/session tables and physical media files. This pattern is worth preserving conceptually.

RECOMMENDED_FROM_EVIDENCE: The rebuild needs a tested demo reset or reseed command that:

- defaults to dry-run or safe seed preview.
- requires explicit confirmation for destructive cleanup.
- scopes demo data separately from real data.
- never deletes users/business owners unless explicitly designed for ephemeral demo.
- handles media cleanup policy deliberately.
- has management-command tests.

## 18. Deployment Direction

- GitHub repository: RECOMMENDED_FROM_EVIDENCE: source code, docs, tests, CI, and issue/commit history live here.
- CI: RECOMMENDED_FROM_EVIDENCE: run checks on pull/push.
- Online Django demo: OWNER_DECISION_REQUIRED: use a backend-capable platform, not GitHub Pages.
- PostgreSQL: RECOMMENDED_FROM_EVIDENCE: use managed or provisioned PostgreSQL for demo parity.
- Static files: RECOMMENDED_FROM_EVIDENCE: collect and serve through approved deployment stack.
- Media: OWNER_DECISION_REQUIRED: use synthetic bundled/static demo images or managed media storage; do not use real source media.
- Environment variables: RECOMMENDED_FROM_EVIDENCE: secret key, debug false, allowed hosts, database URL, CSRF trusted origins where needed.
- Migrations: RECOMMENDED_FROM_EVIDENCE: run as deployment step or documented release operation.
- Health check: RECOMMENDED_FROM_EVIDENCE: simple authenticated-independent health endpoint or platform check if approved.
- Demo account: OWNER_DECISION_REQUIRED: access model and reset cadence.
- Reset behavior: RECOMMENDED_FROM_EVIDENCE: safe reseed command before/after demo sessions if public mutation is allowed.

## 19. CI Requirements

Minimum CI:

- install dependencies.
- run Django system check.
- check migrations are committed and consistent.
- run test suite.
- optionally run lint/format checks after owner chooses tooling.

Recommended later CI:

- basic accessibility/static template checks if tooling is introduced.
- deployment smoke check after online demo exists.
- secret scanning or repository hygiene check.

## 20. Observability and Failure Visibility

RECOMMENDED_FROM_EVIDENCE: Portfolio V1 should keep observability proportional:

- server logs for errors.
- clear user-facing messages for failed forms and failed stock updates.
- minimal `UsageEvent` only if privacy rules are documented.
- admin/debug visibility for synthetic demo data.

DEFERRED_HYPOTHESIS: Analytics dashboards, event funnels, and retention BI are not V1 release requirements.

## 21. Performance Boundaries

- RECOMMENDED_FROM_EVIDENCE: Product list should not assume unlimited products on one page.
- RECOMMENDED_FROM_EVIDENCE: Dashboard counts should use shared query/service logic and avoid divergent Python-only filtering at scale.
- RECOMMENDED_FROM_EVIDENCE: Prefetch known product card dependencies.
- DEFERRED_HYPOTHESIS: Pagination or incremental loading may be required before demo data grows beyond a small portfolio set.

## 22. Accessibility and Mobile Technical Constraints

- RECOMMENDED_FROM_EVIDENCE: Mobile first viewport must be manually verified.
- RECOMMENDED_FROM_EVIDENCE: Disclosure controls use semantic buttons and `aria-expanded`.
- RECOMMENDED_FROM_EVIDENCE: Messages use `role=status` or `role=alert` where appropriate.
- RECOMMENDED_FROM_EVIDENCE: HTMX updates expose loading, success, and error states.
- RECOMMENDED_FROM_EVIDENCE: Tap targets remain safe with Georgian labels.
- RECOMMENDED_FROM_EVIDENCE: No color-only status communication.

## 23. AI-Assisted Development Boundary

- OWNER_PROVIDED_DIRECTION: Codex may assist planning, code generation, audit, and documentation.
- OWNER_PROVIDED_DIRECTION: Owner controls scope, architecture, acceptance, testing, and commits.
- RECOMMENDED_FROM_EVIDENCE: AI output is not trusted without source inspection, tests, and owner review.
- RECOMMENDED_FROM_EVIDENCE: LLM does not own business truth.
- RECOMMENDED_FROM_EVIDENCE: AI/chatbot/public assistant features remain future scope unless explicitly approved later.

## 24. Technical Non-Goals

- OWNER_PROVIDED_DIRECTION: No chatbot implementation in V1.
- OWNER_PROVIDED_DIRECTION: No public buyer catalog implementation in V1.
- OWNER_PROVIDED_DIRECTION: No orders, payments, reservations, or delivery in V1.
- OWNER_PROVIDED_DIRECTION: No microservices.
- OWNER_PROVIDED_DIRECTION: No broad ERP/accounting/supplier scope.
- RECOMMENDED_FROM_EVIDENCE: No full REST API until a real consumer exists.
- RECOMMENDED_FROM_EVIDENCE: No real production/seller data in portfolio demo.
- RECOMMENDED_FROM_EVIDENCE: No fake Git history.

## 25. Risks and Mitigations

| Risk | Evidence | Mitigation |
|---|---|---|
| Stock race/lost update | VALIDATED_PROTOTYPE_LESSON | Transaction-safe inventory service and tests |
| Incomplete inventory ledger | VALIDATED_PROTOTYPE_LESSON | Route all stock writes through inventory service |
| Cross-business data leak | PARTIAL prototype enforcement | Business-scoping tests and constraints |
| Overloaded views | VALIDATED_PROTOTYPE_LESSON | Thin views plus command/query services |
| Stale HTMX aggregate state | VALIDATED_PROTOTYPE_LESSON | Define partial refresh contracts and tests |
| Secrets/media published | VERIFIED_BY_CURRENT_SOURCE source artifacts exist | Strict `.gitignore`, review, synthetic data |
| Deployment mismatch | No deployment config found | Create documented production/demo settings later |
| Scope creep | OWNER_PROVIDED_DIRECTION | Frozen owner-approved scope before build |

## 26. Technical Stop Gates

- OWNER_DECISION_REQUIRED: Scope decisions approved.
- RECOMMENDED_FROM_EVIDENCE: Data model and source-of-truth rules approved.
- RECOMMENDED_FROM_EVIDENCE: Security/repository hygiene checklist satisfied.
- RECOMMENDED_FROM_EVIDENCE: Critical regression matrix has tests.
- RECOMMENDED_FROM_EVIDENCE: CI passes.
- RECOMMENDED_FROM_EVIDENCE: Demo data is synthetic and resettable.
- RECOMMENDED_FROM_EVIDENCE: Deployment settings are not local/debug settings.
- RECOMMENDED_FROM_EVIDENCE: Mobile and accessibility smoke checks complete.

## 27. Owner Decisions Required

- Hosting provider and demo access model.
- One business per seller for V1, or active business switcher.
- Material confirmation UI and alias policy.
- Measurement implementation timing, convention, and product/choice boundary.
- Whether fit guidance appears in a later approved micro-slice.
- Whether variant price override is included in V1.
- Price zero/null/missing policy.
- Direct stock set in V1.
- Clone scope and stock-copy/reset behavior.
- Product Detail scope.
- Product Relations scope.
- Type/tag scope and readiness impact.
- Public visibility field in initial schema or later migration.
- Whether analytics/usage events ship in V1 or stay admin/demo-only.
