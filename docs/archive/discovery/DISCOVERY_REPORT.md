# Discovery Report

## Document Metadata

- Status: LIVE
- Phase: 1A — Repository Map and Evidence Inventory
- Source project: `/home/giga/Desktop/OSINT/facebook_MVP/`
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Created/updated at: 2026-07-27 13:23:27 +0400
- Owner: osMit
- Codex edit rule: update only through an approved reconnaissance or documentation task

## 1. Reconnaissance Objective

The existing `facebook_MVP` project is being studied as an unfinished discovery prototype for a seller-first Social Commerce Operations Assistant. This phase captures repository structure, documentation artifacts, Django architecture, routes, entities, services, and visible verification assets.

The future project will be rebuilt separately because the prototype contains useful behavioral evidence and product learning, but it also contains documentation drift, late-stage patch history, unclear canonical scope, and prototype-era implementation coupling. The source project is evidence, not the automatic architecture or codebase for the rebuild.

This report is evidence collection only. It is not a complete backend audit, UI/UX audit, security review, testing review, product freeze, or rebuild plan.

## 2. Inspection Coverage

### Inspected

- VERIFIED_IMPLEMENTED: Source root directory `/home/giga/Desktop/OSINT/facebook_MVP/`.
- VERIFIED_IMPLEMENTED: Root files: `manage.py`, `requirements.txt`, `.env.example`, `.gitignore`, `RUN.txt`.
- VERIFIED_IMPLEMENTED: Django project package: `config/`, `config/settings/base.py`, `config/settings/local.py`, `config/urls.py`, `config/asgi.py`, `config/wsgi.py`.
- VERIFIED_IMPLEMENTED: App directories: `apps/accounts`, `apps/businesses`, `apps/catalog`, `apps/clothing`, `apps/inventory`, `apps/dashboard`, `apps/analytics`, `apps/validation`.
- VERIFIED_IMPLEMENTED: Model files, URL files, forms, service modules, views, admin files, migrations, test files, and the catalog management command.
- VERIFIED_IMPLEMENTED: Template files under `templates/`, including product, dashboard, registration, and partial templates.
- VERIFIED_IMPLEMENTED: Static file `static/css/app.css`.
- VERIFIED_IMPLEMENTED: Documentation/planning files at the source root: `README.md`, `hook.md`, `checkpoint.md`, `specs.md`, `inventory.md`, `project_freeze.md`, `sitemap.md`, `type_tag_assistant.md`, `reset.md`, `startup_idea.txt`, `seller.txt`, `patch-prompts future.txt`, `pre-prompt.txt`, `RUN.txt`.

### Not Yet Inspected Deeply

- UNKNOWN: Full backend correctness, transaction boundaries, domain duplication, and all edge-case failure paths.
- UNKNOWN: Full UI/UX behavior, mobile rendering, navigation trust under real browser use, and seller cognitive load.
- UNKNOWN: Security hardening, authentication edge cases, CSRF/session behavior beyond visible Django defaults, and deployment posture.
- UNKNOWN: Live database contents, applied migration state, and media file condition.
- UNKNOWN: Full documentation drift across all long documents line by line.
- UNKNOWN: Portfolio readiness, CI feasibility, deployment target, GitHub history strategy, and online demo constraints.

### Inspection Limitations

- `rg` was not available in the shell, so `find`, `grep`, `sed`, `wc`, and Git commands were used.
- The source directory is not a Git repository, so branch, history, and diff evidence are unavailable.
- Tests were not run because this phase is mapping-only and test execution may require database setup/mutation.
- Migrations were not run, database state was not read, and the development server was not started.
- `.env` was intentionally not read because credentials were not needed for this phase.

## 3. Repository Identity

- Source directory: `/home/giga/Desktop/OSINT/facebook_MVP/`
- Git status: UNKNOWN/VERIFIED_IMPLEMENTED as absent. `git status --short --branch`, `git branch --show-current`, and `git log --oneline -8` all reported `fatal: not a git repository`.
- Current branch: UNKNOWN, no Git repository detected.
- Recent history summary: UNKNOWN, no Git repository detected.
- Project/framework identity: VERIFIED_IMPLEMENTED Django modular monolith using Django 6.0.5, PostgreSQL, Django templates, HTMX, Alpine.js, Tailwind CDN, and local media storage.
- Python/Django entrypoint: VERIFIED_IMPLEMENTED `manage.py` sets `DJANGO_SETTINGS_MODULE` to `config.settings.local`.

Root directory map:

```text
.
├── apps/
│   ├── accounts/
│   ├── analytics/
│   ├── businesses/
│   ├── catalog/
│   ├── clothing/
│   ├── dashboard/
│   ├── inventory/
│   └── validation/
├── backups/
├── config/
│   └── settings/
├── media/
├── static/
├── templates/
├── .env
├── .env.example
├── README.md
├── RUN.txt
├── checkpoint.md
├── hook.md
├── inventory.md
├── project_freeze.md
├── reset.md
├── sitemap.md
├── specs.md
├── startup_idea.txt
├── seller.txt
├── patch-prompts future.txt
├── pre-prompt.txt
├── requirements.txt
└── manage.py
```

## 4. Documentation Inventory

| Document | Path | Apparent Role | Stated Status | Evidence Status | Notes |
|---|---|---|---|---|---|
| `README.md` | `/home/giga/Desktop/OSINT/facebook_MVP/README.md` | Setup note and early scaffold summary | Stage 0 scaffold; Stage 1 planned | OBSOLETE_OR_SUPERSEDED | Code contains later models, views, templates, tests, and management command. |
| `hook.md` | `/home/giga/Desktop/OSINT/facebook_MVP/hook.md` | Continuation anchor for future coding chats | Patch 3 pending; Patch 1/2 completed | PARTIAL | Some listed current features are verified, but patch order is superseded by `checkpoint.md` and source. |
| `checkpoint.md` | `/home/giga/Desktop/OSINT/facebook_MVP/checkpoint.md` | Working execution checkpoint and patch log | MVP-Freeze active; Stage 8 in progress; many Stage 7/8/9 patches recorded | PARTIAL | Closest live-looking document, but it contains older “last updated” text and requires drift audit. |
| `specs.md` | `/home/giga/Desktop/OSINT/facebook_MVP/specs.md` | Current-state product and technical specification | Stage 7N complete; pilot-ready claims | PARTIAL | Many entities/routes verified; starter taxonomy and sentinel tag claims conflict with newer source/checkpoint evidence. |
| `inventory.md` | `/home/giga/Desktop/OSINT/facebook_MVP/inventory.md` | Broad product/architecture context | Current decision: private inventory/catalog MVP; no public buyer catalog/orders/payments/chatbot | DOCUMENTED_NOT_VERIFIED | Useful product framing; not fully checked against all source behavior. |
| `project_freeze.md` | `/home/giga/Desktop/OSINT/facebook_MVP/project_freeze.md` | Older project freeze / full context | Working directory `/home/giga/Desktop/MVP/`; MVP scope and future layers | OBSOLETE_OR_SUPERSEDED | Wrong working directory for current source; still useful as historical product context. |
| `sitemap.md` | `/home/giga/Desktop/OSINT/facebook_MVP/sitemap.md` | Navigation audit and route/action map | Recommends Patch 9F return paths | PARTIAL | Route map mostly aligns with source; Patch 9F recommendation appears partly superseded by tests/source with `next` handling. |
| `type_tag_assistant.md` | `/home/giga/Desktop/OSINT/facebook_MVP/type_tag_assistant.md` | Type/tag assistant planning and phased behavior | Phase 1 implemented; later phases deferred | PARTIAL | Existing registry recognition and inline escape hatches are visible in source; document also retains old “no code/no UI changes” non-goals. |
| `reset.md` | `/home/giga/Desktop/OSINT/facebook_MVP/reset.md` | Safe catalog reset runbook | Dry-run-first reset instructions | VERIFIED_IMPLEMENTED | Matching management command file exists; command was not executed. |
| `startup_idea.txt` | `/home/giga/Desktop/OSINT/facebook_MVP/startup_idea.txt` | Master product/startup context and future architecture narrative | Broad current/future product strategy | DOCUMENTED_NOT_VERIFIED | Useful for product intent and future boundaries; not a verified implementation source. |
| `seller.txt` | `/home/giga/Desktop/OSINT/facebook_MVP/seller.txt` | Seller/product-parameter research notes | Research/recommendation text | DOCUMENTED_NOT_VERIFIED | Contains advanced clothing/material/measurement/photo ideas; source implementation not verified for these ideas. |
| `patch-prompts future.txt` | `/home/giga/Desktop/OSINT/facebook_MVP/patch-prompts future.txt` | Historical/future patch prompts | Patch 1 through Patch 6 prompt sequence | OBSOLETE_OR_SUPERSEDED | Several prompted features appear implemented later; use as intent history only. |
| `pre-prompt.txt` | `/home/giga/Desktop/OSINT/facebook_MVP/pre-prompt.txt` | Prior continuation instructions | Treat selected docs as source of truth before implementation | OBSOLETE_OR_SUPERSEDED | Useful as process history; current task explicitly supersedes it. |
| `RUN.txt` | `/home/giga/Desktop/OSINT/facebook_MVP/RUN.txt` | Local run command note | Activate venv and run server on `0.0.0.0:8000` | DOCUMENTED_NOT_VERIFIED | Server was not started. |

## 5. Django Application Map

| App / Module | Main Responsibility | Important Files | Evidence Status | Notes |
|---|---|---|---|---|
| `config` | Django project configuration and root routing | `config/settings/base.py`, `config/settings/local.py`, `config/urls.py`, `config/asgi.py`, `config/wsgi.py` | VERIFIED_IMPLEMENTED | Uses PostgreSQL via env, custom user model, media/static config, `django_htmx`. |
| `apps.accounts` | Custom email authentication user and login form | `models.py`, `managers.py`, `forms.py`, `urls.py`, `admin.py`, `migrations/0001_initial.py` | VERIFIED_IMPLEMENTED | Login/logout routes use Django auth views. |
| `apps.businesses` | Seller workspace/business ownership model | `models.py`, `admin.py`, `migrations/0001_initial.py` | VERIFIED_IMPLEMENTED | No app-level URLs found. |
| `apps.catalog` | Core product catalog, taxonomy, relations, forms, main seller workflows | `models.py`, `forms.py`, `views.py`, `services.py`, `answer_generator.py`, `urls.py`, `admin.py`, migrations, tests, management command | VERIFIED_IMPLEMENTED | Largest app; most seller workflows live here. |
| `apps.clothing` | Clothing-specific product and variant profiles | `models.py`, `admin.py`, migrations | VERIFIED_IMPLEMENTED | Views/tests are placeholders. |
| `apps.inventory` | Inventory adjustment records and quantity update service/endpoint | `models.py`, `services.py`, `views.py`, `urls.py`, `admin.py`, migration | VERIFIED_IMPLEMENTED | HTMX and normal POST stock update paths found. |
| `apps.dashboard` | Seller cockpit dashboard and signal summaries | `views.py`, `services.py`, `urls.py`, template | VERIFIED_IMPLEMENTED | Models/tests/admin mostly placeholder or light. |
| `apps.analytics` | Usage event table/admin for pilot behavior tracking | `models.py`, `admin.py`, migration | VERIFIED_IMPLEMENTED | No custom analytics UI found. |
| `apps.validation` | Product readiness computation | `services.py` | VERIFIED_IMPLEMENTED | Model/view/test files are placeholders. |
| `templates` | Server-rendered UI | `base.html`, catalog/dashboard/registration templates and partials | VERIFIED_IMPLEMENTED | HTMX and Alpine usage found. |
| `static` | Small static CSS layer | `static/css/app.css` | VERIFIED_IMPLEMENTED | Tailwind is loaded from CDN in `base.html`. |

## 6. Core Entity Inventory

| Entity | Source File | Responsibility | Ownership / Relations | Evidence Status |
|---|---|---|---|---|
| `User` | `apps/accounts/models.py` | Email-based custom auth user | Owns `Business` through `Business.owner`; referenced by `InventoryAdjustment.created_by` and `UsageEvent.user` | VERIFIED_IMPLEMENTED |
| `Business` | `apps/businesses/models.py` | Seller workspace/shop boundary | FK to `AUTH_USER_MODEL`; owns products, tags, product types, relations, inventory adjustments, usage events | VERIFIED_IMPLEMENTED |
| `Product` | `apps/catalog/models.py` | Central catalog item with name, price, currency, lifecycle, visibility, notes | FK to `Business`; has variants, photos, tags, relations, clothing profile, inventory adjustments | VERIFIED_IMPLEMENTED |
| `ProductVariant` | `apps/catalog/models.py` | Product choice/variant and stock source of truth | FK to `Product`; has `quantity_on_hand`, optional price override, clothing variant profile | VERIFIED_IMPLEMENTED |
| `ProductPhoto` | `apps/catalog/models.py` | Product image record | FK to `Product`; image stored under `products/photos/`; primary and sort-order flags | VERIFIED_IMPLEMENTED |
| `ClothingProductProfile` | `apps/clothing/models.py` | Clothing-specific product metadata | One-to-one with `Product`; target audience; legacy `product_type`; FK `custom_type` to `BusinessProductType` | VERIFIED_IMPLEMENTED |
| `ClothingVariantProfile` | `apps/clothing/models.py` | Clothing choice metadata | One-to-one with `ProductVariant`; size and color | VERIFIED_IMPLEMENTED |
| `InventoryAdjustment` | `apps/inventory/models.py` | Stock mutation audit record | FK to `Business`, `Product`, `ProductVariant`, nullable creator user | VERIFIED_IMPLEMENTED |
| `BusinessProductType` | `apps/catalog/models.py` | Business-scoped product type registry | FK to `Business`; referenced by `ClothingProductProfile.custom_type`; active-normalized unique constraint | VERIFIED_IMPLEMENTED |
| `BusinessTag` | `apps/catalog/models.py` | Business-scoped tag registry | FK to `Business`; joined to products via `ProductTag`; active-normalized unique constraint | VERIFIED_IMPLEMENTED |
| `ProductTag` | `apps/catalog/models.py` | Product-to-tag join | FK to `Product` and `BusinessTag`; unique together product/tag | VERIFIED_IMPLEMENTED |
| `ProductRelation` | `apps/catalog/models.py` | Manual directed relation between products | FK to `Business`, source product, target product; clean/save enforces same-business and no self-relation | VERIFIED_IMPLEMENTED |
| `UsageEvent` | `apps/analytics/models.py` | Pilot usage/activity event record | Nullable FK to `Business` and user; event type, object metadata, JSON payload | VERIFIED_IMPLEMENTED |

## 7. Route and UI Surface Inventory

| Route / URL | View | Template | Purpose | Evidence Status |
|---|---|---|---|---|
| `/admin/` | Django admin | Django admin templates | Internal admin/debug surface | VERIFIED_IMPLEMENTED |
| `/accounts/login/` | `django.contrib.auth.views.LoginView` via `apps.accounts.urls` | `templates/registration/login.html` | Seller login with email form | VERIFIED_IMPLEMENTED |
| `/accounts/logout/` | `django.contrib.auth.views.LogoutView` | Django auth behavior | Seller logout | VERIFIED_IMPLEMENTED |
| `/` | `apps.dashboard.views.home` | `templates/dashboard/home.html` | Seller dashboard/cockpit with inventory and readiness summaries | VERIFIED_IMPLEMENTED |
| `/products/` | `apps.catalog.views.product_list` | `templates/catalog/product_list.html`, `templates/catalog/partials/product_card.html` | Main product workspace with tabs, filters, search, cards, stock controls, answer snippets | VERIFIED_IMPLEMENTED |
| `/products/new/` | `apps.catalog.views.product_create` | `templates/catalog/product_form.html` | Product creation form | VERIFIED_IMPLEMENTED |
| `/products/<pk>/` | `apps.catalog.views.product_detail` | `templates/catalog/product_detail.html` | Product detail, answer helper, stock controls | VERIFIED_IMPLEMENTED |
| `/products/<pk>/edit/` | `apps.catalog.views.product_edit` | `templates/catalog/product_form.html` | Product correction/edit form and relation management | VERIFIED_IMPLEMENTED |
| `/products/search-suggestions/` | `apps.catalog.views.search_suggestions` | `templates/catalog/partials/search_suggestions.html` | HTMX/datalist search suggestions | VERIFIED_IMPLEMENTED |
| `/products/tags/` | `apps.catalog.views.business_tag_list` | `templates/catalog/tag_list.html` | Tag management page | VERIFIED_IMPLEMENTED |
| `/products/tags/create/` | `apps.catalog.views.business_tag_create` | Redirect/no full template | POST tag create | VERIFIED_IMPLEMENTED |
| `/products/tags/<pk>/rename/` | `apps.catalog.views.business_tag_rename` | Redirect/no full template | POST tag rename | VERIFIED_IMPLEMENTED |
| `/products/tags/<pk>/deactivate/` | `apps.catalog.views.business_tag_deactivate` | Redirect/no full template | POST tag hide/deactivate | VERIFIED_IMPLEMENTED |
| `/products/tags/<pk>/reactivate/` | `apps.catalog.views.business_tag_reactivate` | Redirect/no full template | POST tag restore/reactivate | VERIFIED_IMPLEMENTED |
| `/products/tags/<pk>/delete/` | `apps.catalog.views.business_tag_delete` | Redirect/no full template | POST unused tag delete | VERIFIED_IMPLEMENTED |
| `/products/tags/inline-create/` | `apps.catalog.views.product_form_tag_inline_create` | `templates/catalog/partials/product_tag_section.html` | HTMX inline tag creation in product form | VERIFIED_IMPLEMENTED |
| `/products/types/` | `apps.catalog.views.business_type_list` | `templates/catalog/type_list.html` | Product type management page | VERIFIED_IMPLEMENTED |
| `/products/types/create/` | `apps.catalog.views.business_type_create` | Redirect/no full template | POST type create | VERIFIED_IMPLEMENTED |
| `/products/types/<pk>/rename/` | `apps.catalog.views.business_type_rename` | Redirect/no full template | POST type rename | VERIFIED_IMPLEMENTED |
| `/products/types/<pk>/deactivate/` | `apps.catalog.views.business_type_deactivate` | Redirect/no full template | POST type hide/deactivate | VERIFIED_IMPLEMENTED |
| `/products/types/<pk>/reactivate/` | `apps.catalog.views.business_type_reactivate` | Redirect/no full template | POST type restore/reactivate | VERIFIED_IMPLEMENTED |
| `/products/types/<pk>/delete/` | `apps.catalog.views.business_type_delete` | Redirect/no full template | POST unused type delete | VERIFIED_IMPLEMENTED |
| `/products/types/inline-create/` | `apps.catalog.views.product_form_type_inline_create` | `templates/catalog/partials/product_type_section.html` | HTMX inline type creation in product form | VERIFIED_IMPLEMENTED |
| `/products/<pk>/clone/` | `apps.catalog.views.product_clone` | Redirect to edit | POST product clone/copy | VERIFIED_IMPLEMENTED |
| `/products/<pk>/archive/` | `apps.catalog.views.product_archive` | Redirect | POST archive product | VERIFIED_IMPLEMENTED |
| `/products/<pk>/restore/` | `apps.catalog.views.product_restore` | Redirect | POST restore archived/hidden product | VERIFIED_IMPLEMENTED |
| `/products/<pk>/tag/` | `apps.catalog.views.product_tag_toggle` | Redirect | POST tag attach/detach from card | VERIFIED_IMPLEMENTED |
| `/products/<pk>/relation/add/` | `apps.catalog.views.product_relation_add` | Redirect | POST manual related-product link creation | VERIFIED_IMPLEMENTED |
| `/products/<pk>/relation/remove/` | `apps.catalog.views.product_relation_remove` | Redirect | POST hide/remove relation | VERIFIED_IMPLEMENTED |
| `/inventory/variants/<pk>/quantity/` | `apps.inventory.views.variant_quantity_update` | `templates/dashboard/partials/quantity_controls.html` or `templates/catalog/partials/product_card.html` for HTMX; redirect otherwise | POST stock increment/decrement/set | VERIFIED_IMPLEMENTED |

## 8. Service and Domain Logic Inventory

| Responsibility | Current Location | Main Function/Class | Evidence Status | Deep Audit Needed |
|---|---|---|---|---|
| Product creation/editing orchestration | `apps/catalog/views.py` | `_build_product_forms`, `_save_product_bundle`, `product_create`, `product_edit` | VERIFIED_IMPLEMENTED | Yes |
| Product forms and variant formset | `apps/catalog/forms.py` | `ProductForm`, `ClothingProductProfileForm`, `ProductPhotoForm`, `VariantForm`, `BaseVariantFormSet`, `build_variant_formset` | VERIFIED_IMPLEMENTED | Yes |
| Product cloning | `apps/catalog/services.py`, `apps/catalog/views.py` | `clone_product_exact`, `product_clone` | VERIFIED_IMPLEMENTED | Yes |
| Quantity update service | `apps/inventory/services.py` | `update_variant_quantity` | VERIFIED_IMPLEMENTED | Yes |
| Quantity update endpoint | `apps/inventory/views.py` | `variant_quantity_update` | VERIFIED_IMPLEMENTED | Yes |
| Computed availability | `apps/inventory/services.py` | `compute_product_availability`, `is_low_stock_variant` | VERIFIED_IMPLEMENTED | Yes |
| Product readiness | `apps/validation/services.py` | `compute_product_readiness` | VERIFIED_IMPLEMENTED | Yes |
| Dashboard warnings/signals | `apps/dashboard/services.py`, `apps/dashboard/views.py` | `build_inventory_summary`, `build_needs_attention_items`, `build_low_stock_items`, `build_sold_out_items`, `build_partially_sold_out_items`, `build_last_piece_items`, `home` | VERIFIED_IMPLEMENTED | Yes |
| Product-list decoration and seller-facing computed state | `apps/catalog/views.py` | `_decorate_product` | VERIFIED_IMPLEMENTED | Yes |
| Search and search ranking | `apps/catalog/views.py` | `_tokenize_search_query`, `_search_result_rank`, `product_list`, `search_suggestions` | VERIFIED_IMPLEMENTED | Yes |
| Deterministic buyer replies | `apps/catalog/answer_generator.py` | `build_product_answer_payload` | VERIFIED_IMPLEMENTED | Yes |
| Related-product safety helper | `apps/catalog/services.py` | `get_confirmed_related_products` | VERIFIED_IMPLEMENTED | Yes |
| Business ownership scoping | `apps/catalog/views.py`, `apps/inventory/views.py`, `apps/dashboard/views.py` | `_get_active_business`, query filters using `business=business` | PARTIAL | Yes |
| Usage tracking | `apps/analytics/models.py`, `apps/catalog/views.py`, `apps/inventory/services.py`, `apps/dashboard/views.py` | `UsageEvent` plus event creation calls | PARTIAL | Yes |
| Taxonomy management | `apps/catalog/views.py`, `apps/catalog/forms.py`, templates | `business_tag_*`, `business_type_*`, inline create helpers | VERIFIED_IMPLEMENTED | Yes |
| Reset/test-data cleanup | `apps/catalog/management/commands/reset_catalog_test_data.py` | `Command` | VERIFIED_IMPLEMENTED | Yes |

## 9. Test and Verification Inventory

Test files found:

- VERIFIED_IMPLEMENTED: `apps/catalog/tests.py` contains 658 lines of Django `TestCase` tests.
- PARTIAL: `apps/accounts/tests.py`, `apps/analytics/tests.py`, `apps/businesses/tests.py`, `apps/clothing/tests.py`, `apps/dashboard/tests.py`, `apps/inventory/tests.py`, and `apps/validation/tests.py` are placeholders with no meaningful tests found.

Areas apparently covered in `apps/catalog/tests.py`:

- VERIFIED_IMPLEMENTED: Deterministic answer payload generation for complete, missing-price, missing-variant, weak-description, partial-sold-out, fully sold-out, and variant-price-conflict scenarios.
- VERIFIED_IMPLEMENTED: Product detail and product list rendering of answer-helper UI.
- VERIFIED_IMPLEMENTED: Product list search by tag, custom type, and size.
- VERIFIED_IMPLEMENTED: Clone success message behavior.
- VERIFIED_IMPLEMENTED: HTMX restock response updating a product card.
- VERIFIED_IMPLEMENTED: Product edit correction flows for removing tags, changing product type, deactivating choices, and blocking last-choice deletion.
- VERIFIED_IMPLEMENTED: Taxonomy delete/recovery link behavior and sentinel tag hiding.
- VERIFIED_IMPLEMENTED: Navigation return context and safe `next` handling for some flows.

Areas apparently uncovered:

- UNKNOWN: Dedicated tests for `inventory.services` outside catalog-integrated test paths.
- UNKNOWN: Dedicated tests for `dashboard.services` and dashboard signal edge cases.
- UNKNOWN: Dedicated tests for `validation.services` as an isolated domain service.
- UNKNOWN: Dedicated ownership/security tests across all views.
- UNKNOWN: Dedicated tests for management command dry-run/confirm behavior.
- UNKNOWN: Browser-level HTMX/Alpine behavior, mobile layout, and copy-to-clipboard behavior.
- UNKNOWN: CI execution, linting, formatting, type checking, and deployment verification.

Tests not executed during this phase:

- Tests were not run. No pass/fail claim is made.

Environment requirements discovered:

- VERIFIED_IMPLEMENTED: `requirements.txt` declares Django 6.0.5, `django-environ`, `django-htmx`, Pillow, and `psycopg[binary]`.
- VERIFIED_IMPLEMENTED: `.env.example` points to PostgreSQL database `facebook_mvp`.
- UNKNOWN: Whether the local database exists, is current, or contains required data.

## 10. Initial Implementation Status

### VERIFIED_IMPLEMENTED

- Custom email auth user and login/logout routing.
- Seller `Business` model with owner relation.
- Catalog product, variant, photo, tag, product type, relation, and join models.
- Clothing-specific product and variant profiles.
- Variant-level stock field on `ProductVariant.quantity_on_hand`.
- Inventory adjustment model and quick/manual quantity update service.
- Computed availability service with draft, hidden, archived, available, sold-out, low-stock, partially sold-out, and last-piece signals.
- Product readiness service for buyer-answer readiness/missing-data labels.
- Dashboard route and template with inventory/readiness/signal sections.
- Product list route and template with tabs, search, type/tag filters, product cards, HTMX stock controls, answer helper, clone/archive/tag actions.
- Product create/edit/detail routes and templates.
- Business tag/type management pages and inline HTMX create partials.
- Deterministic buyer-answer payload generation grounded in product, variant, availability, and readiness data.
- Manual product relation model and edit-page relation add/remove routes.
- Reset management command and reset runbook.

### DOCUMENTED_NOT_VERIFIED

- Pilot readiness and 14/21-day seller validation claims.
- Generic fallback UI behavior.
- Basic image resize/compression.
- PWA-friendly behavior.
- Full “assistant-like” seller value loop as experienced by real sellers.
- Advanced clothing field strategy, measurement maps, material model, and photo slot strategy from `seller.txt`.
- Online demo/deployment readiness.

### PARTIAL

- Business ownership isolation is visible in many views, but full edge-path coverage was not audited.
- Usage tracking exists, but analytics UI and complete event semantics were not audited.
- Product readiness and dashboard signals exist, but duplication/correctness boundaries were not deeply audited.
- Type/tag assistant Phase 1 has visible recognition/inline-create behavior, but later phases are deferred and document wording conflicts remain.
- Return-path handling exists in source/tests, but full navigation UX was not audited in browser.

### DEFERRED

- Public buyer catalog.
- Buyer-facing mini-pages and inquiry/request form.
- Chatbot or messaging integration.
- AI generation or AI-assisted interpretation.
- Orders, reservations, payments, and delivery.
- DRF/full REST API.
- Pagination.
- Fuzzy search/morphology-aware matching.
- Automated relation discovery.
- Advanced analytics dashboard.
- Stock movement reason codes.
- Material assistant and clothing measurement/photo-slot expansion.

### OBSOLETE_OR_SUPERSEDED

- `README.md` Stage 0 scaffold description.
- `project_freeze.md` current working directory `/home/giga/Desktop/MVP/`.
- `hook.md` next-action statement that Patch 3 is pending.
- `sitemap.md` Patch 9F recommendation as future work, because source/tests show some return-context work already exists.
- `specs.md` claim that starter taxonomy seeding and automatic `თეგის გარეშე` assignment are current behavior.

### UNKNOWN

- Applied migration state.
- Live database contents and data hygiene.
- Actual runtime behavior on the local machine.
- Browser/mobile rendering and interaction reliability.
- Production security posture.
- Deployment/hosting readiness.
- Git/GitHub history strategy.
- Whether current prototype behavior should be retained, changed, or discarded in the rebuild.

### OWNER_DECISION_REQUIRED

- Which documents, if any, should become canonical inputs for the rebuild after drift audit.
- Whether the new rebuild should remain clothing-first or make domain boundaries explicit from day one.
- Which current seller workflows are owner-approved as validated behavior.
- Whether deterministic buyer-answer helper belongs in the initial rebuilt MVP or later phase.
- Whether product relations, tags, and dynamic types are required in the frozen MVP or should be phased separately.
- What online demo access model and seed/demo data policy should be used for portfolio presentation.

## 11. Obvious Documentation or Project-State Conflicts

1. Conflicting sources: `README.md` vs source code.
   - Exact inconsistency: `README.md` says the repository is Stage 0 scaffold only, while source contains advanced catalog models, views, templates, tests, and management command.
   - Blocks further reconnaissance: No.
   - Later audit: Documentation-drift audit.

2. Conflicting sources: `project_freeze.md` vs current filesystem.
   - Exact inconsistency: `project_freeze.md` says to work inside `/home/giga/Desktop/MVP/`, but inspected source is `/home/giga/Desktop/OSINT/facebook_MVP/`.
   - Blocks further reconnaissance: No.
   - Later audit: Documentation-drift audit.

3. Conflicting sources: `hook.md`, `checkpoint.md`, source code.
   - Exact inconsistency: `hook.md` says Patch 3 is pending; `checkpoint.md` records many later Stage 7/8/9 patches, and source shows clone modes, answer helper, search updates, taxonomy work, and return-context tests.
   - Blocks further reconnaissance: No.
   - Later audit: Documentation-drift audit plus validated-behavior synthesis.

4. Conflicting sources: `specs.md`, `checkpoint.md`, `apps/catalog/views.py`, `apps/catalog/forms.py`, `apps/catalog/tests.py`.
   - Exact inconsistency: `specs.md` describes starter taxonomy seeding and automatic `თეგის გარეშე` tag assignment; checkpoint and tests indicate seeding/sentinel leakage was removed or hidden, and source excludes the sentinel from seller-facing tag selection.
   - Blocks further reconnaissance: No.
   - Later audit: Backend/domain audit and documentation-drift audit.

5. Conflicting sources: `sitemap.md` vs current source/tests.
   - Exact inconsistency: `sitemap.md` recommends Patch 9F contextual return paths as next work; source/tests show `next` handling and return-link behavior exist in several routes.
   - Blocks further reconnaissance: No.
   - Later audit: Frontend/navigation UX audit and documentation-drift audit.

6. Conflicting sources: `type_tag_assistant.md` internal sections.
   - Exact inconsistency: It says Phase 1 is now implemented, but its explicit non-goals still include “no code” and “no UI changes.”
   - Blocks further reconnaissance: No.
   - Later audit: Documentation-drift audit and backend/domain audit.

## 12. Initial Rebuild Inputs

High-confidence observations that may inform the rebuild:

- VERIFIED_IMPLEMENTED: Variant-level quantity is the implemented stock truth, with product availability computed from active variants.
- VERIFIED_IMPLEMENTED: Business ownership is a central conceptual boundary and appears throughout model relationships and many view queries.
- VERIFIED_IMPLEMENTED: Stored product lifecycle state is separate from computed availability.
- VERIFIED_IMPLEMENTED: Buyer-answer readiness is computed rather than stored.
- VERIFIED_IMPLEMENTED: Deterministic buyer-answer text can be generated from stored product data without using an LLM.
- VERIFIED_IMPLEMENTED: Seller-facing cockpit value comes from dashboard signals, fast product-list operations, search, taxonomy, stock updates, and answer-readiness cues.
- PARTIAL: Current architecture puts a large amount of orchestration in `catalog.views`, so the rebuild should study behavior before copying boundaries.
- PARTIAL: Product type, tag, relation, readiness, and answer-helper concepts are promising but need owner confirmation before frozen MVP scope.
- PARTIAL: UI surfaces are compact and operational, but product card and product form density require a dedicated UX audit.
- OWNER_DECISION_REQUIRED: The rebuild should not inherit all prototype features automatically; each behavior needs owner approval and phase assignment.

No rebuild architecture or frozen scope is defined in this phase.

## 13. Required Next Dedicated Audits

1. Backend, domain, state, and ownership audit.
   - Objective: Verify state boundaries, ownership isolation, domain logic placement, stock truth, readiness/availability correctness, and data-integrity risks.
   - Exact scope: Models, migrations, services, forms, views, management command, and relevant tests.
   - Important files: `apps/catalog/models.py`, `apps/clothing/models.py`, `apps/inventory/models.py`, `apps/businesses/models.py`, `apps/catalog/views.py`, `apps/inventory/views.py`, `apps/catalog/forms.py`, `apps/catalog/services.py`, `apps/inventory/services.py`, `apps/validation/services.py`, `apps/dashboard/services.py`, `apps/catalog/answer_generator.py`, migrations, `apps/catalog/tests.py`.
   - Explicit exclusions: No UI redesign, no rebuild plan, no code changes, no documentation rewrite, no migrations, no database mutation.
   - Expected update to `DISCOVERY_REPORT.md`: Add a Phase 1B backend/domain/state findings section and update unknowns/owner decisions.

2. Frontend, navigation, and seller UX audit.
   - Objective: Evaluate seller workflows, route trust, product-list density, form density, mobile behavior, hidden state, and action hierarchy.
   - Exact scope: Templates, HTMX/Alpine interactions, route-return behavior, dashboard/product-list/product-form/product-detail/tag/type pages.
   - Important files: `templates/base.html`, `templates/dashboard/home.html`, `templates/dashboard/partials/quantity_controls.html`, `templates/catalog/product_list.html`, `templates/catalog/partials/product_card.html`, `templates/catalog/product_form.html`, `templates/catalog/product_detail.html`, `templates/catalog/tag_list.html`, `templates/catalog/type_list.html`, `templates/catalog/partials/*.html`, `static/css/app.css`, `sitemap.md`.
   - Explicit exclusions: No backend redesign, no implementation, no visual redesign deliverable, no browser automation unless explicitly approved.
   - Expected update to `DISCOVERY_REPORT.md`: Add a Phase 1C seller UX/navigation findings section and update validated journeys/risks.

3. Tests, security, operations, and deployment audit.
   - Objective: Map verification gaps, authentication/authorization risks, CI/deployment absence, environment assumptions, management commands, and portfolio-demo needs.
   - Exact scope: Tests, settings, env examples, admin exposure, static/media config, requirements, management command, deployment/config discovery.
   - Important files: `apps/*/tests.py`, `config/settings/*.py`, `config/urls.py`, `.env.example`, `requirements.txt`, `RUN.txt`, `reset.md`, `apps/catalog/management/commands/reset_catalog_test_data.py`.
   - Explicit exclusions: No test execution unless approved, no package install, no deployment setup, no Git initialization.
   - Expected update to `DISCOVERY_REPORT.md`: Add a Phase 1D verification/security/ops findings section and rebuild readiness risks.

4. Documentation-drift audit.
   - Objective: Compare all docs against source evidence, mark canonical/historical/obsolete areas, and identify owner decisions needed before freezing rebuild documentation.
   - Exact scope: All Markdown/text planning files and source evidence from previous audits.
   - Important files: `README.md`, `hook.md`, `checkpoint.md`, `specs.md`, `inventory.md`, `project_freeze.md`, `sitemap.md`, `type_tag_assistant.md`, `reset.md`, `startup_idea.txt`, `seller.txt`, `patch-prompts future.txt`, `pre-prompt.txt`.
   - Explicit exclusions: No rewrite of existing source docs, no new `README.md`, no `BUILD_PLAN.md`, no scope freeze.
   - Expected update to `DISCOVERY_REPORT.md`: Add documentation authority map and contradiction resolution queue.

5. Validated-behavior and rebuild-input synthesis.
   - Objective: Convert audited evidence into owner-reviewable rebuild inputs without yet implementing the rebuild.
   - Exact scope: Summarize verified behaviors, reject/retain candidates, edge cases, future-ready boundaries, and phase candidates.
   - Important files: `DISCOVERY_REPORT.md` plus prior audit outputs.
   - Explicit exclusions: No app creation, no code copying, no implementation, no final build plan until owner review.
   - Expected update to `DISCOVERY_REPORT.md`: Add synthesis section and owner approval checklist.

## 14. Recommended Next Prompt

Recommended next audit: Backend, Domain, State, and Ownership Audit.

This should come before UI/UX and rebuild planning because the rebuild needs a trustworthy map of product truth, stock truth, lifecycle state, computed availability, answer readiness, ownership isolation, and data-integrity boundaries. If those are unclear, UI decisions and portfolio planning will be built on unstable assumptions.

## 15. Operation Log

- Source files modified: none.
- Source files created: none.
- Destination files created/updated: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md`.
- Packages installed: none.
- Migrations run: none.
- Database changes: none.
- Commits: none.
- Pushes: none.

Commands executed:

```text
pwd
ls -la /home/giga/Desktop/OSINT
test -d /home/giga/Desktop/OSINT/GITHUB_MVP_ERP && ls -la /home/giga/Desktop/OSINT/GITHUB_MVP_ERP || true
test -f /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md && sed -n '1,260p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md || true
git status --short --branch
git branch --show-current
git log --oneline -8
find . -maxdepth 2 -type d -print | sort
find . -maxdepth 3 -type f -not -path './.venv/*' -not -path './*/__pycache__/*' -print | sort
find . -maxdepth 1 -type f -printf '%TY-%Tm-%Td %TH:%TM %p\n' | sort
sed -n '1,260p' config/settings/base.py
sed -n '1,160p' config/settings/local.py
sed -n '1,220p' config/urls.py
sed -n '1,160p' requirements.txt
find apps -path '*/migrations/*.py' -type f -not -name '__init__.py' -print | sort
find templates -type f -print | sort
find static -type f -print | sort
find apps -path '*/management/*' -type f -not -path '*/__pycache__/*' -print | sort
sed -n '1,280p' apps/accounts/models.py
sed -n '1,280p' apps/businesses/models.py
sed -n '1,360p' apps/catalog/models.py
sed -n '1,260p' apps/clothing/models.py
sed -n '1,260p' apps/inventory/models.py
sed -n '1,220p' apps/analytics/models.py
sed -n '1,220p' apps/validation/models.py
sed -n '1,220p' apps/accounts/urls.py apps/catalog/urls.py apps/inventory/urls.py apps/dashboard/urls.py
grep -R -n "^class \|^def \|^@login_required" apps --include='*.py' | sort
sed -n '1,260p' apps/catalog/forms.py
sed -n '1,280p' apps/catalog/services.py
sed -n '1,300p' apps/inventory/services.py
sed -n '1,300p' apps/validation/services.py
sed -n '1,340p' apps/dashboard/services.py
sed -n '1,280p' apps/catalog/answer_generator.py
grep -R -n "@admin.register\|class .*Admin" apps --include='admin.py' | sort
grep -R -n "render(request\|return render\|template_name\|hx-\|x-data\|json_script" apps templates --include='*.py' --include='*.html' | sort
wc -l apps/*/tests.py templates/*.html templates/catalog/*.html templates/catalog/partials/*.html templates/dashboard/*.html templates/dashboard/partials/*.html templates/registration/*.html static/css/app.css apps/catalog/views.py apps/inventory/views.py apps/dashboard/views.py
grep -R -n "^class .*Test\|^    def test_\|^def test_" apps --include='tests.py' | sort
sed -n '1,240p' apps/dashboard/views.py
sed -n '536,980p' apps/catalog/views.py
sed -n '980,1605p' apps/catalog/views.py
sed -n '1,260p' apps/inventory/views.py
find . -maxdepth 1 -type f \( -name '*.md' -o -name '*.txt' \) -printf '%TY-%Tm-%Td %TH:%TM %p\n' | sort
for f in README.md hook.md checkpoint.md specs.md inventory.md project_freeze.md sitemap.md type_tag_assistant.md reset.md startup_idea.txt seller.txt 'patch-prompts future.txt' pre-prompt.txt RUN.txt; do printf '\nFILE: %s\n' "$f"; sed -n '1,45p' "$f"; done
grep -nE "Status:|STATUS|Current version|Last updated|Stage|Phase|Patch|Ready for Pilot|MVP-Freeze|Working directory|canonical|source of truth|single execution|Future|future|deferred|Deferred|Do not|Do NOT|not in MVP|Not MVP" README.md hook.md checkpoint.md specs.md inventory.md project_freeze.md sitemap.md type_tag_assistant.md reset.md startup_idea.txt seller.txt 'patch-prompts future.txt' pre-prompt.txt
grep -R -n "starter\|თეგის გარეშე\|reset_catalog_test_data\|Patch 9F\|Stage 0 scaffold\|/home/giga/Desktop/MVP\|/home/giga/Desktop/OSINT/facebook_MVP\|Phase 1 is now implemented\|no code\|no UI changes" *.md *.txt apps templates --include='*.md' --include='*.txt' --include='*.py' --include='*.html'
date '+%Y-%m-%d %H:%M:%S %Z'
date '+%Y-%m-%d %H:%M:%S %z'
find . -maxdepth 3 -type d -name '.github' -o -name 'staticfiles' -o -name 'scripts'
find . -maxdepth 3 -type f \( -name '*.yml' -o -name '*.yaml' -o -name 'Dockerfile' -o -name 'Procfile' -o -name 'pyproject.toml' -o -name 'setup.cfg' -o -name 'tox.ini' -o -name 'pytest.ini' \) -print
find /home/giga/Desktop/OSINT/GITHUB_MVP_ERP -maxdepth 2 -type f -print
find /home/giga/Desktop/OSINT/GITHUB_MVP_ERP -maxdepth 1 -type f -name 'DISCOVERY_REPORT.md' -print
sed -n '1,260p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md
sed -n '261,520p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md
```
