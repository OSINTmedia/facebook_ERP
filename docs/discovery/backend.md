# Backend Discovery and Domain Audit

## Document Metadata

- Status: LIVE
- Phase: 1B — Backend, Domain, State, and Ownership Audit
- Source project: `/home/giga/Desktop/OSINT/facebook_MVP/`
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Based on: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md`
- Created/updated at: 2026-07-27 13:35:46 +0400
- Owner: osMit
- Codex edit rule: update only through an approved backend audit task

## 1. Audit Objective

This audit exists to document what the prototype backend actually implements: ownership, data truth, stored and computed state, domain logic placement, schema constraints, workflow safety, and failure risks.

VERIFIED_IMPLEMENTED: The source project is a Django modular monolith for a seller-side inventory/catalog cockpit. It is useful evidence for the future rebuild, but it should not be copied as the future architecture without owner approval and scope freeze.

This phase intentionally excludes implementation, refactoring, database changes, migrations, test execution, final data-model design, frontend UX audit, public catalog planning, chatbot implementation, order/payment/delivery design, and `BUILD_PLAN.md`.

## 2. Evidence Method

- VERIFIED_IMPLEMENTED: Directly confirmed in active Python, template, configuration, or management-command source.
- VERIFIED_BY_MIGRATION: Confirmed by migration files or schema declarations generated into migration history.
- VERIFIED_BY_TEST: Explicitly covered by existing test source. Tests were not executed, so this does not mean the tests currently pass.
- DOCUMENTED_NOT_VERIFIED: Described in Markdown/text documents but not verified in implementation.
- PARTIAL: Implementation exists but the workflow, boundary, or enforcement is incomplete or inconsistent.
- DUPLICATED: Similar business rules are implemented in multiple places.
- FRAGILE: Behavior depends on defensive checks, private helper imports, implicit conventions, broad assumptions, or non-transactional side effects.
- DEFERRED: Explicitly planned outside the current prototype scope.
- OBSOLETE_OR_SUPERSEDED: Evidence appears to describe an older project state.
- UNKNOWN: Insufficient evidence or not inspected deeply enough.
- OWNER_DECISION_REQUIRED: Product-owner judgment is required before treating a behavior as future scope.

Source code was treated as primary evidence. Migrations were treated as schema-evolution evidence. Tests were treated as intended behavior only. Documentation was used to identify deferred scope and contradictions, not to promote unverified claims into implementation facts.

## 3. Inspection Coverage

### Inspected

- VERIFIED_IMPLEMENTED: `manage.py`, `requirements.txt`, `.env.example`, `.gitignore`, `RUN.txt`.
- VERIFIED_IMPLEMENTED: `config/settings/base.py`, `config/settings/local.py`, `config/urls.py`, `config/asgi.py`, `config/wsgi.py`.
- VERIFIED_IMPLEMENTED: Local app models, forms, services, views, URLs, admin files, app configs, migrations, tests, and catalog management command.
- VERIFIED_IMPLEMENTED: Backend-relevant template behavior in `templates/base.html`, `templates/dashboard/home.html`, `templates/dashboard/partials/quantity_controls.html`, `templates/catalog/product_form.html`, `templates/catalog/product_detail.html`, `templates/catalog/product_list.html`, `templates/catalog/partials/product_card.html`, `templates/catalog/partials/product_type_section.html`, and `templates/catalog/partials/product_tag_section.html`.
- DOCUMENTED_NOT_VERIFIED: Backend-relevant claims in `README.md`, `inventory.md`, `project_freeze.md`, `specs.md`, `checkpoint.md`, `hook.md`, `type_tag_assistant.md`, `reset.md`, `startup_idea.txt`, and `seller.txt`.

### Not Inspected Deeply

- UNKNOWN: Live database contents, applied migration state, existing media-file consistency, and production runtime state.
- UNKNOWN: Browser execution of HTMX/Alpine behavior.
- UNKNOWN: PostgreSQL query plans, lock behavior under load, and race behavior under concurrent requests.
- UNKNOWN: Full security audit of Django admin and deployment settings.
- UNKNOWN: Full documentation-drift resolution.

### Limitations

- `rg` was unavailable; `find`, `grep`, `sed`, `wc`, and Git commands were used.
- The source project is not a Git repository, so branch, diff, and history evidence are unavailable.
- Tests were not run because this phase forbids database-changing verification.
- Migrations were inspected but not executed.
- `.env` was not read; `.env.example` was read.

## 4. Backend Architecture Overview

VERIFIED_IMPLEMENTED: The project is a Django 6.0.5 server-rendered application using Django templates, PostgreSQL via `django-environ`, `django-htmx`, Pillow, and `psycopg[binary]`.

VERIFIED_IMPLEMENTED: The backend entry points are `manage.py`, root URL routing in `config/urls.py`, and app URL modules for `accounts`, `catalog`, `inventory`, and `dashboard`.

PARTIAL: The architecture resembles a modular monolith, but the largest app, `catalog`, owns much of the application orchestration. `inventory.views` imports private helper functions from `catalog.views`, which blurs app boundaries.

Evidence-based dependency map:

```text
accounts
  -> businesses
      -> catalog
          -> clothing
          -> analytics
          -> inventory.services
          -> validation.services
      -> inventory
          -> catalog models
          -> catalog.views private helpers
          -> analytics
      -> dashboard
          -> catalog
          -> inventory.services
          -> validation.services
          -> analytics
analytics
validation
```

FRAGILE: Defensive `_table_exists()` checks appear in active request paths, so runtime behavior partially compensates for migration/schema uncertainty.

## 5. Django App Responsibility Map

| App | Responsibility | Main Models | Main Services | Depends On | Evidence |
|---|---|---|---|---|---|
| `accounts` | Email-based custom user and auth forms | `User` | None | Django auth | VERIFIED_IMPLEMENTED |
| `businesses` | Seller workspace/tenant boundary | `Business` | None | `accounts.User` | VERIFIED_IMPLEMENTED |
| `catalog` | Product catalog, taxonomy, relations, product forms, search, clone, answer payload, seller product workspace | `Product`, `ProductVariant`, `ProductPhoto`, `BusinessTag`, `ProductTag`, `BusinessProductType`, `ProductRelation` | `clone_product_exact`, `get_confirmed_related_products`, answer generator helpers | `businesses`, `clothing`, `inventory`, `validation`, `analytics` | VERIFIED_IMPLEMENTED |
| `clothing` | Clothing-specific product and variant metadata | `ClothingProductProfile`, `ClothingVariantProfile` | None | `catalog` | VERIFIED_IMPLEMENTED |
| `inventory` | Quantity mutation endpoint, availability computation, adjustment ledger | `InventoryAdjustment` | `compute_product_availability`, `is_low_stock_variant`, `update_variant_quantity` | `catalog`, `businesses`, `analytics` | VERIFIED_IMPLEMENTED |
| `dashboard` | Seller cockpit summaries and attention signals | None | Dashboard signal builders | `catalog`, `inventory`, `validation`, `analytics`, `businesses` | VERIFIED_IMPLEMENTED |
| `validation` | Product readiness computation | None | `compute_product_readiness` | Product/clothing object shape by convention | VERIFIED_IMPLEMENTED |
| `analytics` | Usage-event table for pilot signal tracking | `UsageEvent` | None | `businesses`, `accounts` | PARTIAL |

DUPLICATED: Active-business resolution exists separately in `catalog.views`, `inventory.views`, and `dashboard.views`.

## 6. Configuration and Environment

- VERIFIED_IMPLEMENTED: `manage.py` defaults to `config.settings.local`.
- VERIFIED_IMPLEMENTED: `base.py` reads `BASE_DIR / ".env"` through `django-environ`.
- VERIFIED_IMPLEMENTED: `DEBUG` defaults to `False` in `base.py`; `local.py` overrides with default `True`.
- VERIFIED_IMPLEMENTED: `SECRET_KEY` falls back to `django-insecure-change-me`.
- VERIFIED_IMPLEMENTED: `ALLOWED_HOSTS` defaults to `["127.0.0.1", "localhost"]`.
- VERIFIED_IMPLEMENTED: `DATABASE_URL` defaults to local PostgreSQL database `facebook_mvp`.
- VERIFIED_IMPLEMENTED: `AUTH_USER_MODEL = "accounts.User"`.
- VERIFIED_IMPLEMENTED: Middleware includes Django security, session, common, CSRF, auth, messages, clickjacking, and `django_htmx.middleware.HtmxMiddleware`.
- VERIFIED_IMPLEMENTED: Static and media roots are local filesystem paths. Media URLs are served in `config/urls.py` only under `settings.DEBUG`.
- FRAGILE: No production settings module, CI config, container config, or deployment config was found.
- FRAGILE: CDN scripts for Tailwind, HTMX, and Alpine are loaded in `templates/base.html`, creating network assumptions for runtime UI behavior.
- FRAGILE: The insecure fallback `SECRET_KEY` and local `DEBUG=True` default are acceptable for a prototype but not portfolio demo deployment.

## 7. Authentication and User Model

- VERIFIED_IMPLEMENTED: `User` subclasses `AbstractUser`, removes `username`, makes `email` unique, and uses email as `USERNAME_FIELD`.
- VERIFIED_IMPLEMENTED: `UserManager` normalizes email and enforces `is_staff=True` and `is_superuser=True` for superusers.
- VERIFIED_IMPLEMENTED: Login uses Django `LoginView` with `EmailAuthenticationForm`; logout uses Django `LogoutView`.
- VERIFIED_IMPLEMENTED: `catalog`, `inventory`, and `dashboard` routes inspected in active URL configuration use `@login_required`.
- PARTIAL: No signup, onboarding, password reset, email verification, or staff-role model was found.
- PARTIAL: Admin is standard Django admin and exposes cross-business data to staff users.
- FRAGILE: Login identity is clear, but authorization depends on each view applying business filters correctly; there is no shared permission policy object.

## 8. Business Ownership and Isolation

VERIFIED_IMPLEMENTED: `Business.owner` is the root seller ownership link. Seller-facing data is usually scoped through the first business owned by the logged-in user.

PARTIAL: The schema supports multiple businesses per user, but the UI/backend selects `user.businesses.order_by("created_at").first()` and no business switcher was found.

FRAGILE: Missing-business fallback silently creates a business named `ჩემი მაღაზია` in dashboard, catalog, and inventory paths. This is duplicated and can create unexpected tenant records.

| Operation | Business Scope Applied Where | DB Protection | Risk | Evidence |
|---|---|---|---|---|
| Dashboard home | `Product.objects.filter(business=business)` after first owned business selection | Product FK to Business | PARTIAL: multi-business selection unsupported; auto-create side effect | VERIFIED_IMPLEMENTED |
| Product list/search | Queryset starts with `Product.objects.filter(business=business)` | Product FK to Business | PARTIAL: post-filtering uses Python-decorated products; search suggestions include all lifecycle states | VERIFIED_IMPLEMENTED |
| Product detail/edit | `get_object_or_404(..., pk=pk, business=business)` | Product FK to Business | VERIFIED_IMPLEMENTED for direct product lookup | VERIFIED_IMPLEMENTED |
| Product create/edit forms | Tag/type querysets are business-scoped | DB has FK but no cross-object business check | PARTIAL: admin or direct writes can assign cross-business tags/types | VERIFIED_IMPLEMENTED |
| Product archive/restore | Product lookup scoped by business | Product FK to Business | VERIFIED_IMPLEMENTED for seller route | VERIFIED_IMPLEMENTED |
| Product clone | Source product lookup scoped by business; clone keeps source business | Product FK to Business | PARTIAL: unknown clone mode accepted as exact-like behavior | VERIFIED_IMPLEMENTED |
| Product tag toggle | Product and tag are both scoped by business | ProductTag has no DB constraint ensuring same business | FRAGILE: redirect uses `HTTP_REFERER` without the same safe-return helper | VERIFIED_IMPLEMENTED |
| Tag/type CRUD | `BusinessTag` and `BusinessProductType` lookups scoped by business | Active normalized uniqueness per business | PARTIAL: admin can bypass view-level delete protections | VERIFIED_IMPLEMENTED and VERIFIED_BY_MIGRATION |
| Inventory update | Variant lookup requires `product__business=business` | Variant FK to Product; adjustment FK to Business/Product/Variant | PARTIAL: adjustment consistency is not DB-enforced | VERIFIED_IMPLEMENTED |
| Product relations | Source and target products are scoped by business; model `clean()` checks same business | Unique tuple on source/target/type; no DB cross-business check | PARTIAL: model save protects normal paths; bulk/admin/direct writes can bypass `full_clean`-style choice validation | VERIFIED_IMPLEMENTED |
| Reset command | Querysets can be all-business or `--business-id` scoped | Depends on FK cascades | FRAGILE: dangerous all-business confirm is allowed with warning only | VERIFIED_IMPLEMENTED |
| Admin | Global admin model registrations | Django admin permissions only | PARTIAL: no per-business admin scoping | VERIFIED_IMPLEMENTED |

## 9. Core Data Model

### User

VERIFIED_IMPLEMENTED: Source file `apps/accounts/models.py`.

VERIFIED_BY_MIGRATION: `apps/accounts/migrations/0001_initial.py` creates `User` with unique `email`, inherited auth fields, group/user permission M2M fields, and custom manager.

Purpose: authentication identity.

Relations: one user can own many `Business` records; can be referenced by `InventoryAdjustment.created_by` and `UsageEvent.user`.

Deletion behavior: deleting a user cascades owned businesses; adjustment and usage creator links use `SET_NULL`.

Legacy concerns: none found.

### Business

VERIFIED_IMPLEMENTED: Source file `apps/businesses/models.py`.

VERIFIED_BY_MIGRATION: `apps/businesses/migrations/0001_initial.py` creates `Business` with `owner`, `name`, `template_type`, timestamps, and ordering by name.

Purpose: seller workspace and ownership boundary.

Relations: owns products, tags, product types, product relations, inventory adjustments, and usage events.

Constraints: no uniqueness on `(owner, name)` and no explicit active/default business flag.

Deletion behavior: deleting a business cascades products, tags, types, relations, and inventory adjustments; usage events use `SET_NULL`.

Legacy concerns: multiple businesses are schema-supported but not workflow-supported.

### BusinessProductType

VERIFIED_IMPLEMENTED: Source file `apps/catalog/models.py`.

VERIFIED_BY_MIGRATION: `apps/catalog/migrations/0004_businessproducttype.py` adds the model with conditional unique constraint `unique_active_normalized_ptype_per_business`.

Purpose: business-scoped dynamic product type dictionary.

Fields: `business`, `name`, `normalized_name`, `is_active`, timestamps.

Relations: referenced by `ClothingProductProfile.custom_type`.

Constraints: unique active normalized type per business.

Deletion behavior: deleting a type sets `custom_type` to null on clothing profiles; view-level delete blocks if in use, but DB/admin can still allow nulling through FK behavior.

Legacy concerns: it coexists with legacy `ClothingProductProfile.product_type`.

### BusinessTag

VERIFIED_IMPLEMENTED: Source file `apps/catalog/models.py`.

VERIFIED_BY_MIGRATION: `apps/catalog/migrations/0002_businesstag_producttag_and_more.py` adds the model with conditional unique constraint `unique_active_normalized_tag_per_business`.

Purpose: business-scoped reusable seller tag dictionary.

Fields: `business`, `name`, `normalized_name`, `is_active`, timestamps.

Relations: assigned to products through `ProductTag`.

Constraints: unique active normalized tag per business.

Deletion behavior: deleting a tag cascades its `ProductTag` rows; seller view blocks deletion if used.

Legacy concerns: reserved normalized name `თეგის გარეშე` is still recognized and hidden/blocked in code.

### ProductTag

VERIFIED_IMPLEMENTED: Source file `apps/catalog/models.py`.

VERIFIED_BY_MIGRATION: `apps/catalog/migrations/0002_businesstag_producttag_and_more.py`.

Purpose: join table between product and tag.

Fields: `product`, `tag`, `created_at`.

Constraints: unique pair `(product, tag)`.

Deletion behavior: cascades with either product or tag.

Integrity risk: PARTIAL because there is no database constraint proving `product.business == tag.business`; seller forms/views scope this, but admin/direct writes can violate it.

### Product

VERIFIED_IMPLEMENTED: Source file `apps/catalog/models.py`.

VERIFIED_BY_MIGRATION: `apps/catalog/migrations/0001_initial.py`.

Purpose: catalog-level sellable item.

Fields: `business`, `name`, `base_price`, `currency`, `lifecycle_status`, `visibility`, `internal_notes`, timestamps.

Relations: variants, photos, tags, relations, clothing profile, inventory adjustments.

Constraints: no product uniqueness per business; no database-level price range constraint; lifecycle and visibility are model choices, not named DB check constraints.

Deletion behavior: deleting a product cascades variants, photos, tags, relations, clothing profile, and inventory adjustments.

Legacy concerns: `name` functions as both product name and lightweight buyer description. There is no separate description field.

### ProductRelation

VERIFIED_IMPLEMENTED: Source file `apps/catalog/models.py`.

VERIFIED_BY_MIGRATION: `apps/catalog/migrations/0003_productrelation.py`.

Purpose: manual directed product-to-product relationship for future upsell/assistant use.

Fields: `business`, `source_product`, `target_product`, `relation_type`, `status`, `source`, timestamps.

Constraints: unique tuple `(source_product, target_product, relation_type)`.

Application enforcement: `clean()` blocks self-relations, cross-business products, and business mismatch; `save()` calls `clean()`.

Integrity risk: PARTIAL because cross-row business invariants are not DB constraints, and `relation_type` choice validity is not explicitly form-validated in `product_relation_add`.

### ProductVariant

VERIFIED_IMPLEMENTED: Source file `apps/catalog/models.py`.

VERIFIED_BY_MIGRATION: `apps/catalog/migrations/0001_initial.py`.

Purpose: product choice/variant and stock source.

Fields: `product`, `label`, `quantity_on_hand`, `price_override`, `is_active`, timestamps.

Relations: one clothing variant profile; inventory adjustments.

Constraints: no unique label or unique size/color per product; no minimum one-active-variant DB constraint.

Deletion behavior: deleting a product cascades variants; seller edit deactivates existing variants instead of deleting them.

Source-of-truth note: VERIFIED_IMPLEMENTED quantity is on `ProductVariant.quantity_on_hand`, not `Product`.

### ProductPhoto

VERIFIED_IMPLEMENTED: Source file `apps/catalog/models.py`.

VERIFIED_BY_MIGRATION: `apps/catalog/migrations/0001_initial.py`.

Purpose: product photo records backed by local media files.

Fields: `product`, `image`, `is_primary`, `sort_order`, `created_at`.

Constraints: no DB constraint limiting one primary photo per product.

Deletion behavior: cascades with product; reset command deletes records but not files.

Risk: FRAGILE because image file writes are not transactionally rolled back with database transactions.

### ClothingProductProfile

VERIFIED_IMPLEMENTED: Source file `apps/clothing/models.py`.

VERIFIED_BY_MIGRATION: `apps/clothing/migrations/0001_initial.py`, `0002_clothingproductprofile_product_type.py`, and `0003_clothingproductprofile_custom_type.py`.

Purpose: clothing-specific product metadata.

Fields: one-to-one `product`, required `target_audience`, legacy `product_type`, nullable dynamic `custom_type`.

Relations: `custom_type` points to `BusinessProductType` with `SET_NULL`.

Constraints: one profile per product.

Legacy concerns: DUPLICATED because legacy `product_type` and dynamic `custom_type` both represent type-like classification, and readiness still checks legacy `product_type`.

### ClothingVariantProfile

VERIFIED_IMPLEMENTED: Source file `apps/clothing/models.py`.

VERIFIED_BY_MIGRATION: `apps/clothing/migrations/0001_initial.py`.

Purpose: clothing-specific variant metadata.

Fields: one-to-one `variant`, `size`, `color`.

Constraints: one profile per variant; size/color choices are form-level only.

Deletion behavior: cascades with variant.

Legacy concerns: `ProductVariant.label` duplicates size/color text derived from this profile.

### InventoryAdjustment

VERIFIED_IMPLEMENTED: Source file `apps/inventory/models.py`.

VERIFIED_BY_MIGRATION: `apps/inventory/migrations/0001_initial.py`.

Purpose: audit log for stock changes.

Fields: `business`, `product`, `variant`, `change_type`, `old_quantity`, `new_quantity`, `delta`, `note`, nullable `created_by`, `created_at`.

Constraints: no DB constraint tying `business`, `product`, and `variant` together consistently.

Deletion behavior: cascades with business/product/variant; creator uses `SET_NULL`.

Coverage risk: PARTIAL because product create/edit quantity changes bypass this ledger.

### UsageEvent

VERIFIED_IMPLEMENTED: Source file `apps/analytics/models.py`.

VERIFIED_BY_MIGRATION: `apps/analytics/migrations/0001_initial.py`.

Purpose: pilot usage telemetry.

Fields: nullable `business`, nullable `user`, `event_type`, `object_type`, optional `object_id`, optional JSON `metadata`, `created_at`.

Constraints: no explicit event taxonomy enforcement beyond model choices; no retention policy found.

Deletion behavior: business/user use `SET_NULL`.

Coverage risk: PARTIAL because several event types are defined but not emitted by inspected code.

## 10. Entity Relationship Map

```text
User
  1 -> many Business

Business
  1 -> many Product
  1 -> many BusinessTag
  1 -> many BusinessProductType
  1 -> many ProductRelation
  1 -> many InventoryAdjustment
  1 -> many UsageEvent

Product
  1 -> 1 ClothingProductProfile
  1 -> many ProductVariant
  1 -> many ProductPhoto
  1 -> many ProductTag
  1 -> many InventoryAdjustment
  1 -> many ProductRelation as source_product
  1 -> many ProductRelation as target_product

ProductVariant
  1 -> 1 ClothingVariantProfile
  1 -> many InventoryAdjustment

BusinessTag
  1 -> many ProductTag

BusinessProductType
  1 -> many ClothingProductProfile through custom_type
```

PARTIAL: The relationship map shows the intended business boundary, but several cross-object consistency rules are enforced only by forms/views/model `save()`, not database constraints.

## 11. Source-of-Truth Matrix

| Business Fact | Stored Source | Computed By | UI Representation | Conflicts/Fallbacks | Evidence |
|---|---|---|---|---|---|
| Ownership | `Business.owner`, `Product.business`, business FKs | View-level `_get_active_business` and scoped querysets | Current seller sees first owned business | PARTIAL: multi-business schema without active-business workflow | VERIFIED_IMPLEMENTED |
| Lifecycle | `Product.lifecycle_status` | Direct model field checks | Tabs, badges, archive/restore actions | PARTIAL: `hidden` exists but no seller route to set it | VERIFIED_IMPLEMENTED |
| Stock | `ProductVariant.quantity_on_hand` on active variants | `update_variant_quantity`, `_save_variants` | `+1`, `-1`, set controls, totals | PARTIAL: product edit changes stock without adjustment ledger | VERIFIED_IMPLEMENTED |
| Availability | No stored field | `compute_product_availability` | product cards, detail, dashboard counts/tabs | DUPLICATED dashboard/list filtering definitions diverge for zero active variants | VERIFIED_IMPLEMENTED |
| Price | `Product.base_price`; optional `ProductVariant.price_override` | answer generator price rules | product cards/detail, buyer reply modes | FRAGILE: zero price is used as missing price; variant override not exposed in seller form | VERIFIED_IMPLEMENTED |
| Size | `ClothingVariantProfile.size`; duplicated into `ProductVariant.label` | form save label composition | choice labels | DUPLICATED stored label can drift from profile if edited outside form | VERIFIED_IMPLEMENTED |
| Color | `ClothingVariantProfile.color`; duplicated into `ProductVariant.label` | form save label composition | choice labels | DUPLICATED stored label can drift from profile if edited outside form | VERIFIED_IMPLEMENTED |
| Product type | `ClothingProductProfile.custom_type` and legacy `product_type` | forms/views/readiness | dynamic type chips/radio list | DUPLICATED: readiness checks legacy `product_type`, UI uses `custom_type` | VERIFIED_IMPLEMENTED |
| Tags | `BusinessTag` and `ProductTag` | form/view assignment; decorated `active_tag_ids` | checkboxes, chips, filters | FRAGILE: readiness requires decorated `active_tag_ids` and has no DB-query fallback | VERIFIED_IMPLEMENTED |
| Photos | `ProductPhoto` records and media files | `_get_primary_photo`, `_save_primary_photo` | primary image preview/card | PARTIAL: one-primary invariant is application-only | VERIFIED_IMPLEMENTED |
| Readiness | No stored field | `compute_product_readiness` | readiness badges, missing info, next actions | DUPLICATED with dashboard attention and `_decorate_product` incomplete logic | VERIFIED_IMPLEMENTED |
| Buyer reply | No stored field | `build_product_answer_payload` | copyable seller-side answer modes | PARTIAL: relations not integrated; no public buyer API | VERIFIED_IMPLEMENTED |
| Product relations | `ProductRelation` | `get_confirmed_related_products`, edit views | edit-page relation controls, relation count | PARTIAL: helper not used by answer generator | VERIFIED_IMPLEMENTED |
| Visibility/publication | `Product.visibility` | No implemented publication engine | Not exposed in seller form | DEFERRED: public catalog boundary not implemented | VERIFIED_IMPLEMENTED |

## 12. Stored States vs Computed States

- VERIFIED_IMPLEMENTED: Stored lifecycle states are `draft`, `active`, `hidden`, and `archived` on `Product.lifecycle_status`.
- VERIFIED_IMPLEMENTED: Computed availability returns `draft`, `hidden`, `archived`, `available`, or `sold_out`, plus `is_low_stock`, `is_partially_sold_out`, `is_last_piece`, and `total_quantity`.
- VERIFIED_IMPLEMENTED: Product readiness is computed as `good`, `partial`, or `poor` and includes critical missing data, secondary missing data, ready answers, next actions, `can_answer_basic_questions`, and `message_service_safe`.
- VERIFIED_IMPLEMENTED: Dashboard warnings/signals are computed separately from readiness using `dashboard.services`.
- VERIFIED_IMPLEMENTED: Answer readiness is represented by readiness level plus answer-generator per-mode `ready` flags and notes.
- PARTIAL: Publication readiness is not implemented as a clear backend boundary. `Product.visibility` exists and can be `public`, but `_save_product_bundle()` forces `PRIVATE` and no public catalog route was found.
- DUPLICATED: Incomplete/attention/readiness rules appear in `validation.services`, `dashboard.services`, `catalog.views._decorate_product`, and `catalog.answer_generator`.

## 13. Product Lifecycle State Table

| Stored Lifecycle | Variant State | Computed Availability | Seller Visibility | Notes | Evidence |
|---|---|---|---|---|---|
| `draft` | Any active/inactive quantities | `draft`; low/partial/last flags false; total still summed | Drafts tab; broad search can show it | Lifecycle overrides sellability even with stock | VERIFIED_IMPLEMENTED |
| `hidden` | Any active/inactive quantities | `hidden`; label text matches archive wording | Archived tab with restore action | No seller route to set hidden found | VERIFIED_IMPLEMENTED |
| `archived` | Any active/inactive quantities | `archived`; label text archive wording | Archived tab with restore action | Archive route stores this state; restore sets active | VERIFIED_IMPLEMENTED |
| `active` | No active variants | `sold_out` | Sold-out tab in product list; dashboard sold-out group may miss it | Readiness marks choices missing; dashboard sold-out builder requires active variants | DUPLICATED |
| `active` | All active variants quantity `0` | `sold_out` | Sold-out tab and sold-out dashboard | Buyer reply says not in stock | VERIFIED_IMPLEMENTED |
| `active` | Some active variants `0`, some `>0` | `available`, `is_partially_sold_out=True` | Active tab and partially sold-out dashboard | Buyer choices list only in-stock labels | VERIFIED_IMPLEMENTED and VERIFIED_BY_TEST |
| `active` | Total active quantity `1` | `available`, `is_last_piece=True` | Active tab and last-piece dashboard | Last-piece flag suppressed for draft/hidden/archived | VERIFIED_IMPLEMENTED |
| `active` | Any active variant quantity `1` | `available`, `is_low_stock=True` | Low-stock tab/dashboard | Low-stock threshold is constant `1` | VERIFIED_IMPLEMENTED |
| `active` | Positive quantities and no low-stock variant | `available` | Active tab/dashboard | Normal sellable state | VERIFIED_IMPLEMENTED |
| `active` | Only inactive variants with positive quantity | `sold_out` | Sold-out in product list; dashboard grouping inconsistent | Inactive stock ignored by availability | VERIFIED_IMPLEMENTED |

## 14. Product Creation Flow

Request -> View -> Forms/Formsets -> Validation -> Transaction -> Models -> Events -> Redirect:

1. VERIFIED_IMPLEMENTED: `POST /products/new/` reaches `product_create`.
2. VERIFIED_IMPLEMENTED: `_get_active_business(request.user)` selects or silently creates the first business.
3. VERIFIED_IMPLEMENTED: `_build_product_forms()` creates `ProductForm`, `ClothingProductProfileForm`, `ProductPhotoForm`, and a prefixed variant formset.
4. VERIFIED_IMPLEMENTED: `ProductForm` requires name and non-null base price, defaults lifecycle to `active`, and limits seller-visible lifecycle choices to active/draft.
5. VERIFIED_IMPLEMENTED: `ClothingProductProfileForm` requires `target_audience` and business-scoped `custom_type`.
6. VERIFIED_IMPLEMENTED: `ProductPhotoForm` accepts an optional primary image.
7. VERIFIED_IMPLEMENTED: `BaseVariantFormSet.clean()` requires at least one completed non-deleted choice.
8. VERIFIED_IMPLEMENTED: `_save_product_bundle()` wraps product, clothing profile, photo, variants, tags, and usage event in `transaction.atomic()`.
9. VERIFIED_IMPLEMENTED: Saved products are forced to `Product.Visibility.PRIVATE`.
10. VERIFIED_IMPLEMENTED: Variants are created from size/color/quantity form data, and `ProductVariant.label` is derived from size and color.
11. VERIFIED_IMPLEMENTED: Tags are assigned from the business-scoped queryset; reserved sentinel tag links are deleted.
12. VERIFIED_IMPLEMENTED: `UsageEvent.PRODUCT_CREATED` is logged if the usage event table exists.
13. VERIFIED_IMPLEMENTED: Success redirects to safe `next` or product list fallback.

Failure and partial-save risks:

- PARTIAL: If no business product types exist, product creation cannot pass `custom_type` validation until a type is created inline.
- FRAGILE: Uploaded files are not transactionally rolled back if a later DB write fails.
- PARTIAL: Initial stock entered through product creation does not create `InventoryAdjustment` records.
- FRAGILE: `Product.base_price=0.00` is accepted by tests and code as a stand-in for missing price even though the field is non-null.
- FRAGILE: Business auto-creation can happen as a side effect of visiting a route.

## 15. Product Editing Flow

Request -> View -> Forms/Formsets -> Validation -> Transaction -> Models -> Events -> Redirect:

1. VERIFIED_IMPLEMENTED: `product_edit` scopes product lookup by current business.
2. VERIFIED_IMPLEMENTED: Existing active variants are loaded into initial formset data through `_variant_initial_data()`.
3. VERIFIED_IMPLEMENTED: Existing `ClothingProductProfile` is edited through `ClothingProductProfileForm`.
4. VERIFIED_IMPLEMENTED: Existing product tags are pre-selected in `ProductForm`.
5. VERIFIED_IMPLEMENTED: Valid POST calls `_save_product_bundle()` inside one transaction.
6. VERIFIED_IMPLEMENTED: Existing variants with submitted IDs are updated; submitted deletions set `is_active=False`; new completed forms create variants.
7. VERIFIED_IMPLEMENTED: Existing primary photo is replaced if a new photo is uploaded; other photos are set non-primary.
8. VERIFIED_IMPLEMENTED: Product tags are replaced by the submitted tag set.
9. VERIFIED_IMPLEMENTED: `UsageEvent.PRODUCT_UPDATED` is logged for product edit.
10. VERIFIED_IMPLEMENTED: Relation management is rendered on the edit page and handled by separate relation POST routes.

Failure and partial-save risks:

- PARTIAL: Product edit quantity changes directly update `ProductVariant.quantity_on_hand` without `InventoryAdjustment`.
- PARTIAL: Inactive variants are not shown in the edit form and remain in the database.
- FRAGILE: A tampered `variant_id` outside the product is ignored for update and results in a new variant if the form is otherwise complete.
- DUPLICATED: Product type and tag correction rules are split across forms, views, templates, and tests.
- PARTIAL: Relation add/remove is not part of the product edit transaction; it is a separate workflow.

## 16. Variant / Choice Domain Rules

- VERIFIED_IMPLEMENTED: Quantity belongs to `ProductVariant.quantity_on_hand`.
- VERIFIED_IMPLEMENTED: Active choices are determined by `ProductVariant.is_active`.
- VERIFIED_IMPLEMENTED: Seller edit deletes an existing choice by deactivating it, not deleting it.
- VERIFIED_IMPLEMENTED: At least one completed non-deleted submitted choice is required by the formset.
- VERIFIED_IMPLEMENTED: Size and color are required for non-empty, non-deleted forms.
- VERIFIED_IMPLEMENTED: `quantity_on_hand` is required for completed variant forms and has form-level `min_value=0`.
- VERIFIED_IMPLEMENTED: `ClothingVariantProfile.size` and `.color` store the structured clothing attributes.
- DUPLICATED: `ProductVariant.label` duplicates the size/color profile text.
- PARTIAL: No DB constraint enforces at least one active variant per active product.
- PARTIAL: No DB uniqueness prevents duplicate size/color choices for one product.
- FRAGILE: `dashboard.services` and `_decorate_product()` iterate all variants for some incompleteness checks, while readiness and availability use active variants.

## 17. Inventory Engine

| Operation | Validation | DB Update | Audit/Event | Response | Risk |
|---|---|---|---|---|---|
| Increment | Action whitelist in view; service accepts `increment` | Sets `quantity_on_hand = old + 1` inside `transaction.atomic()` | Creates `InventoryAdjustment` and `UsageEvent.VARIANT_QUANTITY_CHANGED` | HTMX partial/card or redirect to detail | FRAGILE: no `select_for_update` or atomic `F()` expression, so concurrent increments can lose updates |
| Decrement | Blocks decrement when old quantity is `0`; prevents negative result | Sets `quantity_on_hand = old - 1` | Creates adjustment and usage event only if changed | HTMX partial/card or redirect | FRAGILE: concurrent decrements can produce misleading duplicate audit events |
| Manual set | View parses int and rejects blank/non-int/negative; service also rejects missing/negative | Sets requested quantity if changed | Creates adjustment and usage event if changed | HTMX partial/card or redirect | PARTIAL: no reason code or note is captured by seller route |
| Same-value set | Service returns unchanged info response | No DB update | No adjustment/event | Redirect message for non-HTMX; HTMX silently rerenders | PARTIAL |
| Product edit quantity change | Form validates min `0` | `_save_variants()` writes quantity directly | Only product update usage event; no `InventoryAdjustment` | Redirect after product save | PARTIAL: stock ledger incomplete |

VERIFIED_IMPLEMENTED: The inventory endpoint checks sold-out/restocked transitions and can emit HTMX triggers `product-sold-out` and `product-restocked` when refreshing a product card.

FRAGILE: Transition checks are outside row-level locking and can be stale under simultaneous requests.

## 18. Clone and Copy Engine

| Clone Mode | Copied | Reset | New Lifecycle | Risk | Evidence |
|---|---|---|---|---|---|
| `exact` | Product name with `(ასლი)` suffix, price, currency, visibility, notes, clothing profile, custom type, legacy type, active variants with quantities, photos | Relations and tags are not copied | `draft` | PARTIAL: exact stock is duplicated into a draft and can become phantom stock if later activated casually | VERIFIED_IMPLEMENTED and VERIFIED_BY_TEST for success message |
| `new_color` | Product fields, size values, photos, profile/type | Variant color blank; quantities reset to `0` | `draft` | PARTIAL: blank color creates intentionally incomplete choices requiring correction | VERIFIED_IMPLEMENTED |
| `new_size` | Product fields, color values, photos, profile/type | Variant size blank; quantities reset to `0` | `draft` | PARTIAL: blank size creates intentionally incomplete choices requiring correction | VERIFIED_IMPLEMENTED |
| `new_photo` | Product fields, profile/type, active variants with quantities | Photos omitted | `draft` | PARTIAL: stock is copied while photo is reset | VERIFIED_IMPLEMENTED |
| Unknown mode | Behaves like exact for quantity/photo logic except message fallback | Nothing explicitly reset | `draft` | FRAGILE: `copy_mode` is not validated against allowed modes | VERIFIED_IMPLEMENTED |

VERIFIED_IMPLEMENTED: `clone_product_exact` is transactional and logs `UsageEvent.PRODUCT_CLONED`.

PARTIAL: Clone does not copy tags or product relations.

## 19. Product Types and Tags

- VERIFIED_IMPLEMENTED: Types are business-scoped in `BusinessProductType`; tags are business-scoped in `BusinessTag`.
- VERIFIED_IMPLEMENTED: Both normalize names by trimming, lowercasing, and collapsing whitespace in `save()`.
- VERIFIED_BY_MIGRATION: Active normalized uniqueness is enforced per business for tags and product types.
- VERIFIED_IMPLEMENTED: Seller CRUD can create, rename, deactivate, reactivate, and delete unused tags/types.
- VERIFIED_IMPLEMENTED: Product form inline HTMX endpoints can create or reactivate tags/types and return updated partials with `assistant-registry-updated`.
- VERIFIED_IMPLEMENTED: Product assignment uses business-scoped form querysets.
- VERIFIED_IMPLEMENTED: Search includes active tags and dynamic custom types.
- VERIFIED_IMPLEMENTED: Reserved tag name `თეგის გარეშე` is blocked from creation/rename and excluded from product form/list/tag management.
- VERIFIED_BY_TEST: Tests cover no sentinel tag creation on tag removal and hiding existing sentinel tags from management.
- PARTIAL: No source code for automatic starter taxonomy seeding was found; earlier docs claiming seeding are obsolete or superseded.
- FRAGILE: Type/tag name normalization does not normalize hyphen/no-hyphen variants; advanced morphology/fuzzy matching is deferred.
- DUPLICATED: Type truth is split between legacy `product_type` and dynamic `custom_type`.

## 20. Product Relations

- VERIFIED_IMPLEMENTED: `ProductRelation` is manual, directed, business-owned, statused, and typed.
- VERIFIED_IMPLEMENTED: Relation types are `goes_with`, `similar_to`, `alternative_to`, `part_of_set`, and `upsell_with`.
- VERIFIED_IMPLEMENTED: Removal hides a relation by setting `status=hidden`; it does not delete the row.
- VERIFIED_IMPLEMENTED: `ProductRelation.clean()` blocks self-relation, cross-business source/target products, and mismatched relation business.
- VERIFIED_IMPLEMENTED: `product_relation_add` scopes source and target products to the current business.
- VERIFIED_IMPLEMENTED: `get_confirmed_related_products()` returns confirmed relations whose targets are active and have at least one active variant with quantity `>0`.
- PARTIAL: The deterministic buyer reply engine does not use related products.
- FRAGILE: `relation_type` is accepted directly from POST and is not validated by a Django form in the route.
- PARTIAL: No explicit tests for relation add/remove, relation validation, hidden relation restore, or cross-business relation rejection were found.

## 21. Search and Filtering Backend

- VERIFIED_IMPLEMENTED: Search tokenization lowercases input, replaces hyphen/slash/underscore with spaces, removes punctuation, collapses whitespace, and keeps tokens longer than one character.
- VERIFIED_IMPLEMENTED: Multi-token search applies AND semantics across tokens; each token uses OR across product name, target audience, variant size, variant color, tag name, and custom type name.
- VERIFIED_IMPLEMENTED: Short or untokenizable search falls back to a single OR query using the raw string.
- VERIFIED_IMPLEMENTED: Type and tag filters filter by `clothing_profile__custom_type_id` and `product_tags__tag_id`.
- VERIFIED_IMPLEMENTED: Readiness filters are applied after products are decorated in Python.
- VERIFIED_IMPLEMENTED: Availability tabs `low_stock` and `sold_out` are applied after products are decorated in Python.
- VERIFIED_IMPLEMENTED: Broad search without a requested tab searches across all lifecycle statuses.
- VERIFIED_IMPLEMENTED: Search result ordering ranks available products first, then low stock, sold out, drafts, and archived/hidden.
- VERIFIED_IMPLEMENTED: Suggestion endpoint searches product names, colors, sizes, active tags, active types, and matching product-name tokens.
- FRAGILE: Availability/readiness filtering requires loading and decorating candidate products in Python, which will not scale cleanly.
- FRAGILE: Suggestion queries do not filter by product lifecycle.
- DEFERRED: Fuzzy search, Georgian morphology, pagination, and full API search are not implemented.

## 22. Validation, Warning, and Readiness Engine

| Rule | Source Data | Severity | Output | Used By | Evidence |
|---|---|---|---|---|---|
| Product must be active for answer safety | `Product.lifecycle_status` | Critical | Poor readiness and next action to enable product | Product cards, detail, dashboard counts, answer payload | VERIFIED_IMPLEMENTED |
| Product name/description exists | `Product.name` | Critical if missing | Ready answer `პროდუქტის აღწერა` or missing description | Readiness and answer payload | VERIFIED_IMPLEMENTED |
| Price exists | truthiness of `Product.base_price` | Critical if falsey | Ready answer `ფასი` or missing price note | Readiness, dashboard, answer payload | VERIFIED_IMPLEMENTED and VERIFIED_BY_TEST |
| Type/audience exists | `ClothingProductProfile.target_audience` and legacy `product_type` | Secondary if missing | Ready answer `პროდუქტის ტიპი` or next action | Readiness | DUPLICATED |
| At least one active choice | Active `ProductVariant` list | Critical if absent | Missing choice note | Readiness, formset, availability | VERIFIED_IMPLEMENTED and VERIFIED_BY_TEST |
| Active choices have size/color | `ClothingVariantProfile.size/color` | Critical if missing | Missing size/color note | Readiness and dashboard | VERIFIED_IMPLEMENTED |
| Stock total is positive | Sum of active variant quantities | Secondary if zero | Stock missing/sold-out note | Readiness and answer payload | VERIFIED_IMPLEMENTED and VERIFIED_BY_TEST |
| Photo exists | Decorated `primary_photo` or `product.photos.exists()` | Secondary | Missing photo note | Readiness and dashboard | VERIFIED_IMPLEMENTED |
| Tags exist | Decorated `active_tag_ids` | Secondary | Missing tag note | Readiness and dashboard | FRAGILE |
| Description weak | Product name token/length heuristic | Seller note only | `აღწერა სუსტია` | Answer generator | VERIFIED_IMPLEMENTED and VERIFIED_BY_TEST |
| Old active product | `updated_at < 30 days` and stock positive | Attention item | Dashboard action | Dashboard only | VERIFIED_IMPLEMENTED |
| Stale sold-out | computed sold-out and `updated_at < 14 days` | Attention item | Dashboard action | Dashboard only | VERIFIED_IMPLEMENTED |

DUPLICATED: Readiness, dashboard attention, product decoration, and buyer-reply notes each maintain related but non-identical definitions of missing data.

FRAGILE: `compute_product_readiness()` only recognizes tags if `active_tag_ids` was attached before the service call; direct service reuse can falsely mark tagged products as missing tags.

PARTIAL: Publication readiness is not separated from buyer-answer readiness.

## 23. Deterministic Buyer Reply Engine

- VERIFIED_IMPLEMENTED: `build_product_answer_payload(product)` supports reply modes `price`, `choices`, `stock`, `description`, and `full`.
- VERIFIED_IMPLEMENTED: Data sources are `Product.base_price`, `Product.currency`, `Product.name`, active variants, `ClothingVariantProfile.size/color`, computed availability, and computed readiness.
- VERIFIED_IMPLEMENTED: In-stock choice replies include only active variants with quantity `>0`.
- VERIFIED_IMPLEMENTED: Fully sold-out products receive sold-out stock/full wording.
- VERIFIED_IMPLEMENTED: Non-active products can produce a stock reply that says the product is not currently enabled for sale.
- VERIFIED_IMPLEMENTED: Missing price and missing choice data are notes, not invented buyer facts.
- VERIFIED_IMPLEMENTED: Tags do not create extra buyer description claims.
- VERIFIED_BY_TEST: Existing tests cover complete replies, missing price, no variants, weak description, partial sold-out, fully sold-out, conflicting variant prices, and avoiding tag-based buyer claims.
- PARTIAL: Related products are not included even though `ProductRelation` and `get_confirmed_related_products()` exist.
- PARTIAL: Variant price overrides are detected for conflicts but are not exposed in the seller form and are not explained per variant.
- FRAGILE: The engine relies on decorated `product.readiness` / `product.inventory_state` when present, otherwise recomputes with the readiness caveats above.
- REBUILD_INPUT: This is deterministic and database-grounded; no LLM is needed or appropriate as the source of price, stock, size, color, or availability truth.

## 24. Dashboard Backend

- VERIFIED_IMPLEMENTED: Dashboard loads the first business, silently creates one if missing, fetches all products for that business, and prefetches product tags, photos, and variants with clothing profiles.
- VERIFIED_IMPLEMENTED: Inventory summary counts available, low-stock, sold-out, draft, and total positive stock units.
- VERIFIED_IMPLEMENTED: Attention items include missing price, missing active-product photo, missing variants, missing target audience, missing variant size/color, missing tags, old active products, and stale sold-out products.
- VERIFIED_IMPLEMENTED: Additional groups include low-stock items, sold-out items, partially sold-out items, and last-piece items.
- VERIFIED_IMPLEMENTED: Readiness counts are computed per product after attaching `active_tag_ids`.
- PARTIAL: Dashboard logs `DASHBOARD_OPENED` only when there are signals, and logs on every qualifying page load.
- DUPLICATED: Dashboard availability and attention rules partly duplicate `inventory.services` and `validation.services`.
- FRAGILE: `build_sold_out_items()` excludes active products with zero active variants, while product-list sold-out filtering includes them.
- FRAGILE: Product staleness uses `Product.updated_at`, but inventory quantity changes update the variant, not the product.

## 25. Analytics and Usage Events

- VERIFIED_IMPLEMENTED: `UsageEvent` stores event type, object type/id, business, user, metadata, and timestamp.
- VERIFIED_IMPLEMENTED: Product create/update logs include product id and variant count.
- VERIFIED_IMPLEMENTED: Product clone logs source product id, copy mode, and cloned variant count.
- VERIFIED_IMPLEMENTED: Inventory quantity changes log product id, old/new quantity, delta, and change type.
- VERIFIED_IMPLEMENTED: Dashboard opens with signals log counts and readiness summary.
- PARTIAL: Event types `WARNING_SEEN` and `WARNING_FIXED` are defined but no creation sites were found.
- PARTIAL: Tag toggle, tag/type CRUD, relation add/remove, search, answer-copy, and detail-open events are not logged.
- FRAGILE: `UsageEvent.object_type` and `object_id` are string fields rather than protected FK relationships.
- UNKNOWN: Retention, privacy policy, export, and pilot-analysis workflows are not implemented.

## 26. Admin and Management Commands

- VERIFIED_IMPLEMENTED: Admin registers `User`, `Business`, `Product`, `ProductVariant`, `ProductPhoto`, `BusinessTag`, `ProductTag`, `ProductRelation`, `ClothingProductProfile`, `ClothingVariantProfile`, `InventoryAdjustment`, and `UsageEvent`.
- PARTIAL: `BusinessProductType` was not registered in inspected `apps/catalog/admin.py`.
- PARTIAL: Admin list/filter/search coverage is useful for debugging but not tenant-scoped.
- VERIFIED_IMPLEMENTED: `reset_catalog_test_data` is dry-run by default and requires `--confirm` for deletion.
- VERIFIED_IMPLEMENTED: Reset command can scope by `--business-id`.
- VERIFIED_IMPLEMENTED: Reset command deletes catalog/inventory/taxonomy/product relation records and intentionally protects users, businesses, schema tables, sessions, and physical media files.
- FRAGILE: The reset command allows all-business confirmed deletion and only warns when `DEBUG=False`.
- UNKNOWN: No tests for the management command were found.

## 27. Migration and Legacy Analysis

| Migration / Change | Purpose | Current Relevance | Legacy Risk | Evidence |
|---|---|---|---|---|
| `accounts.0001_initial` | Custom email user | Active auth model | Low | VERIFIED_BY_MIGRATION |
| `businesses.0001_initial` | Business ownership model | Active tenant boundary | Medium: no default/current business concept | VERIFIED_BY_MIGRATION |
| `catalog.0001_initial` | Product, variant, photo | Core catalog and stock schema | Medium: no product uniqueness, one-primary, one-active-variant, or price check constraints | VERIFIED_BY_MIGRATION |
| `inventory.0001_initial` | Inventory adjustment ledger | Stock audit model | High: direct product edit quantity changes bypass ledger | VERIFIED_BY_MIGRATION |
| `analytics.0001_initial` | Usage event telemetry | Pilot tracking | Medium: event coverage incomplete | VERIFIED_BY_MIGRATION |
| `clothing.0001_initial` | Clothing profiles and size/color | Clothing MVP boundary | Medium: size/color form choices not DB constraints | VERIFIED_BY_MIGRATION |
| `catalog.0002` | Business tags and product tags | Active taxonomy | Medium: no DB check that tag and product share business | VERIFIED_BY_MIGRATION |
| `catalog.0003` | Product relations | Active relation feature | Medium: model-level cross-business clean, no DB equivalent | VERIFIED_BY_MIGRATION |
| `clothing.0002` | Legacy fixed `product_type` | Still present and used by readiness | High: conflicts with dynamic `custom_type` | VERIFIED_BY_MIGRATION |
| `catalog.0004` | Dynamic business product type | Active product-type dictionary | Medium: not admin registered; nullable profile FK | VERIFIED_BY_MIGRATION |
| `clothing.0003` | `custom_type` FK | Active UI product type | High: readiness does not use it as primary type truth | VERIFIED_BY_MIGRATION |

FRAGILE: Runtime `_table_exists()` checks suggest the prototype was patched through schema changes while keeping old screens usable. The rebuild should remove this class of defensive migration-era branching after migrations are stable.

## 28. Existing Test Coverage

| Domain Area | Test File | Behavior Covered | Missing Cases | Evidence |
|---|---|---|---|---|
| Deterministic buyer replies | `apps/catalog/tests.py` | Complete, missing price, no variants, weak description, partial/fully sold-out, conflicting prices, no tag claim leakage | Relation suggestions, draft/hidden/archived answer behavior, direct readiness tag fallback | VERIFIED_BY_TEST |
| Product detail/list answer UI | `apps/catalog/tests.py` | Detail answer block, list shortcut, fill shortcut | Browser copy behavior, Alpine state, mobile behavior | VERIFIED_BY_TEST |
| Search | `apps/catalog/tests.py` | Search by tag, custom type, size | Multi-token ranking, lifecycle behavior, suggestions, performance | VERIFIED_BY_TEST |
| Clone | `apps/catalog/tests.py` | Exact clone success message rename nudge | Field copying, reset modes, invalid mode, stock duplication safety | VERIFIED_BY_TEST |
| Inventory HTMX | `apps/catalog/tests.py` | Restock product-card response and `product-restocked` trigger | Decrement, set, sold-out transition, concurrency, audit records | VERIFIED_BY_TEST |
| Product edit corrections | `apps/catalog/tests.py` | Remove tag without sentinel, change product type, deactivate variant, block last-choice delete | Cross-business posted IDs, direct stock ledger gap, duplicate variants | VERIFIED_BY_TEST |
| Taxonomy delete/recovery | `apps/catalog/tests.py` | Recovery links, unused delete actions, sentinel hidden | Rename/reactivate conflicts, inline create, DB constraint behavior | VERIFIED_BY_TEST |
| Return context | `apps/catalog/tests.py` | Safe internal next, external next rejection, return links from list/detail/dashboard | `HTTP_REFERER` redirect in tag toggle, inventory invalid-action return paths | VERIFIED_BY_TEST |
| Ownership isolation | Placeholder app tests only | No explicit full cross-business tests found | All seller-facing route families need cross-business tests | UNKNOWN |
| Management command | No meaningful test found | None | Dry-run, business scope, confirm guard, protected data | UNKNOWN |
| Dashboard services | Placeholder app tests only | Indirect coverage through dashboard attention link test | Counts, stale state, zero active variant mismatch | PARTIAL |

Tests were not executed, so no pass/fail statement is made.

## 29. Backend Technical Debt

### Critical

- Location: `apps/inventory/services.py`.
  Mechanism: Quantity updates read old value and write new value without `select_for_update` or atomic `F()` expressions.
  Consequence: Concurrent increments/decrements can lose stock updates or create misleading audit records.
  Rebuild implication: Stock mutation must be transactionally safe and tested under concurrent requests.
  Evidence: FRAGILE.

- Location: `apps/catalog/views.py` and `apps/inventory/services.py`.
  Mechanism: Product create/edit writes variant quantities directly; inventory endpoint writes quantities with ledger records.
  Consequence: `InventoryAdjustment` is not a complete stock ledger.
  Rebuild implication: All quantity-changing paths must go through one inventory domain service.
  Evidence: PARTIAL and DUPLICATED.

- Location: `apps/validation/services.py`.
  Mechanism: Readiness checks legacy `product_type` and decorated `active_tag_ids` rather than canonical dynamic type/tag sources.
  Consequence: Readiness can be wrong when called outside decorated list/dashboard paths.
  Rebuild implication: Readiness must be a pure, database-grounded domain service with explicit inputs.
  Evidence: FRAGILE and DUPLICATED.

### High

- Location: `apps/catalog/views.py`.
  Mechanism: 1,598-line view module owns forms orchestration, search, decorators, taxonomy, clone routing, lifecycle changes, relations, and return URLs.
  Consequence: High regression risk and unclear service/application boundaries.
  Rebuild implication: Split application services by workflow before scaling features.
  Evidence: VERIFIED_IMPLEMENTED.

- Location: cross-business relations in `ProductTag`, `ClothingProductProfile.custom_type`, `InventoryAdjustment`, and admin.
  Mechanism: Business consistency is mostly view/form enforced, not DB enforced.
  Consequence: Admin/direct writes can create inconsistent tenant data.
  Rebuild implication: Encode tenant consistency in services, constraints where possible, and tests.
  Evidence: PARTIAL.

- Location: `Product.base_price` and price validation.
  Mechanism: Non-null decimal field uses `0.00` as missing price in logic/tests.
  Consequence: Missing price and free product are indistinguishable.
  Rebuild implication: Decide whether price can be null, zero, variant-specific, or explicitly unknown.
  Evidence: FRAGILE and OWNER_DECISION_REQUIRED.

- Location: `apps/catalog/views.py`, `apps/inventory/views.py`, `apps/dashboard/views.py`.
  Mechanism: active business is selected by first created business and auto-created if absent.
  Consequence: Multi-business support is misleading and side effects can occur on GET/POST.
  Rebuild implication: Define current-business selection and onboarding explicitly.
  Evidence: PARTIAL.

### Medium

- Location: `apps/catalog/models.py`.
  Mechanism: `ProductPhoto.is_primary` has no unique primary-per-product constraint.
  Consequence: Admin/direct writes can create multiple primary photos; view picks first primary.
  Rebuild implication: Enforce primary photo invariant or model ordered gallery explicitly.
  Evidence: PARTIAL.

- Location: `apps/catalog/services.py`.
  Mechanism: clone mode is not validated.
  Consequence: unknown mode behaves like exact clone and may preserve stock unexpectedly.
  Rebuild implication: Validate command parameters with explicit value objects/forms.
  Evidence: FRAGILE.

- Location: `apps/dashboard/services.py`.
  Mechanism: Dashboard sold-out and attention logic differs from availability/readiness services.
  Consequence: Product-list and dashboard counts can disagree.
  Rebuild implication: Put dashboard summaries behind shared query/domain services.
  Evidence: DUPLICATED.

- Location: `apps/catalog/views.py` and `apps/inventory/views.py`.
  Mechanism: runtime `_table_exists()` checks in normal request handling.
  Consequence: Migration drift is hidden at runtime, and code paths are harder to reason about.
  Rebuild implication: Remove migration-era defensive branches after schema freeze.
  Evidence: FRAGILE.

- Location: `apps/catalog/views.py`.
  Mechanism: `product_tag_toggle` redirects to raw `HTTP_REFERER`.
  Consequence: Potential unsafe redirect behavior compared with safer `next` helper.
  Rebuild implication: Use one safe return-url helper for all redirects.
  Evidence: FRAGILE.

### Low

- Location: `apps/catalog/models.py` and `apps/clothing/models.py`.
  Mechanism: `ProductVariant.label` duplicates structured size/color.
  Consequence: Label drift is possible outside normal forms.
  Rebuild implication: Generate display label from variant attributes or enforce sync.
  Evidence: DUPLICATED.

- Location: `apps/analytics/models.py`.
  Mechanism: usage events store object references as strings.
  Consequence: Flexible but weak referential integrity.
  Rebuild implication: Keep flexible analytics only if event taxonomy and privacy rules are documented.
  Evidence: PARTIAL.

- Location: `apps/catalog/admin.py`.
  Mechanism: `BusinessProductType` is not registered in admin.
  Consequence: Debug/admin management of dynamic product types is incomplete.
  Rebuild implication: Admin coverage should match operational entities.
  Evidence: PARTIAL.

## 30. Backend Patterns Worth Preserving

- VERIFIED_IMPLEMENTED: Modular monolith with separate apps for accounts, businesses, catalog, clothing, inventory, dashboard, analytics, and validation.
- VERIFIED_IMPLEMENTED: Business-owned product data as the seller tenant boundary.
- VERIFIED_IMPLEMENTED: Variant-level stock truth instead of product-level stock.
- VERIFIED_IMPLEMENTED: Stored lifecycle status separated from computed availability.
- VERIFIED_IMPLEMENTED: Computed readiness separated from stored product fields.
- VERIFIED_IMPLEMENTED: Deterministic buyer-answer payload generation grounded in stored data and computed state.
- VERIFIED_IMPLEMENTED: Service-layer functions for availability, quantity update, readiness, clone, related products, and dashboard summaries.
- VERIFIED_IMPLEMENTED: Transactional product bundle save for product/profile/photo/variant/tag persistence.
- VERIFIED_IMPLEMENTED: Dry-run-first reset command that protects users and businesses.
- VERIFIED_BY_TEST: Tests around answer truthfulness, edit correction, taxonomy sentinel hiding, HTMX restock response, and safe `next` redirects.

## 31. Backend Patterns Requiring Redesign

- Current issue: Business selection is implicit first-business selection with silent creation.
  Why it matters: Tenant context is a critical invariant.
  Rebuild direction: Define onboarding and active-business selection explicitly.
  Must not copy blindly: Duplicated `_get_active_business()` helpers.

- Current issue: Inventory changes are split between product form save and inventory endpoint.
  Why it matters: Audit history and stock correctness are core product truth.
  Rebuild direction: Route all stock mutations through one inventory service.
  Must not copy blindly: Direct variant quantity assignment from product edit.

- Current issue: Readiness depends on decorated attributes and legacy product type.
  Why it matters: Future buyer assistant/API cannot rely on view decoration.
  Rebuild direction: Make readiness a pure domain/query service with explicit source fields.
  Must not copy blindly: `active_tag_ids` hidden input contract and `product_type` fallback.

- Current issue: Large `catalog.views` module contains many workflow responsibilities.
  Why it matters: It will make micro-slice rebuilds hard to verify.
  Rebuild direction: Separate command/query services for create/edit, taxonomy, search, clone, lifecycle, and relations.
  Must not copy blindly: fat view orchestration.

- Current issue: Documentation mentions public/buyer/chatbot/order future layers, while current code only has seller-side deterministic helper.
  Why it matters: Scope drift can distort the rebuild.
  Rebuild direction: Keep future boundaries explicit and deferred until seller truth is stable.
  Must not copy blindly: Treating all documented future features as current requirements.

## 32. Backend Invariants for the Rebuild

- VERIFIED_EXISTING: Every seller-owned operational object should be reachable through a `Business` boundary.
- VERIFIED_EXISTING: Product ownership belongs to `Business`, not directly to `User`.
- VERIFIED_EXISTING: Stock truth lives on active `ProductVariant` records.
- VERIFIED_EXISTING: Product availability is computed, not stored.
- VERIFIED_EXISTING: Lifecycle and availability are separate concepts.
- VERIFIED_EXISTING: Archived/draft/hidden lifecycle states override sellability.
- VERIFIED_EXISTING: Buyer replies must use stored product facts and computed availability/readiness, not invented AI output.
- VERIFIED_EXISTING: Cross-business product relations are forbidden by normal model save logic.
- VERIFIED_EXISTING: Product bundles should not partially persist after form validation succeeds and a DB write fails inside the save transaction.
- RECOMMENDED_FROM_EVIDENCE: Every stock mutation path should create an inventory adjustment record.
- RECOMMENDED_FROM_EVIDENCE: Readiness should not depend on view-decorated ad hoc attributes.
- RECOMMENDED_FROM_EVIDENCE: Product type truth should be one canonical field or explicitly versioned through a migration plan.
- RECOMMENDED_FROM_EVIDENCE: Safe return URL handling should be centralized.
- RECOMMENDED_FROM_EVIDENCE: Tenant consistency should be backed by tests and, where feasible, database constraints.
- OWNER_DECISION_REQUIRED: Whether exact clone should copy stock or always reset stock.
- OWNER_DECISION_REQUIRED: Whether price `0.00` means free, missing, or invalid.
- OWNER_DECISION_REQUIRED: Whether product relations belong in the frozen MVP or a later phase.
- OWNER_DECISION_REQUIRED: Whether dynamic product types and tags are mandatory for MVP or phased after core product/stock truth.
- OWNER_DECISION_REQUIRED: Whether public `visibility` should remain in the initial schema before a public catalog exists.

## 33. Unresolved Questions

- OWNER_DECISION_REQUIRED: Should one seller be allowed to operate multiple businesses in the MVP, and if so how is the active business selected?
- OWNER_DECISION_REQUIRED: Is `0.00` a valid product price or a missing-price sentinel?
- OWNER_DECISION_REQUIRED: Should exact clone copy stock, reset stock, or require an explicit owner-approved choice every time?
- OWNER_DECISION_REQUIRED: Is dynamic `BusinessProductType.custom_type` the canonical type truth, and should legacy `product_type` be removed or retained as compatibility?
- OWNER_DECISION_REQUIRED: Are tags required for answer readiness, search readiness, or only optional seller organization?
- OWNER_DECISION_REQUIRED: Should hidden and archived remain separate backend lifecycle states?
- UNKNOWN: Whether current migrations are applied to the local database.
- UNKNOWN: Whether existing data contains cross-business inconsistencies created through admin or earlier prototype code.
- UNKNOWN: Whether tests pass under the local PostgreSQL setup.
- UNKNOWN: Whether media files referenced by `ProductPhoto` records exist and are clean.
- UNKNOWN: Whether admin will be available in the public portfolio demo.

## 34. Inputs for the Future Rebuild Documentation

- PROJECT_BIBLE.md input: VERIFIED_IMPLEMENTED seller-first cockpit purpose, Business ownership boundary, variant stock truth, deterministic answer helper, and explicit future scope deferrals.
- DATA_MODEL_V1.md input: VERIFIED_IMPLEMENTED entities and relationships plus unresolved owner decisions around price, visibility, type, tags, clone stock, and lifecycle.
- TECHNICAL_ARCHITECTURE_V1.md input: VERIFIED_IMPLEMENTED modular monolith pattern, but with redesign notes for fat views, private cross-app helper imports, inventory service centralization, and readiness purity.
- TEST_STRATEGY_V1.md input: VERIFIED_BY_TEST existing useful catalog tests plus missing tests for ownership, concurrency, service-level readiness, inventory ledger completeness, relations, taxonomy conflicts, and management command safety.
- BUILD_PLAN.md input: Backend micro-slices should start with auth/business boundary, product/variant truth, inventory transaction safety, readiness, and deterministic reply generation before public catalog or buyer automation.

No future documentation files were created in this phase.

## 35. Recommended Next Audit

Recommended next audit: Frontend, Navigation, and Seller UX Audit.

It follows this backend truth audit because the UI should be judged against the verified domain boundaries: Business ownership, variant stock truth, lifecycle vs availability, readiness vs publication, and deterministic answer preparation. A UX audit before backend truth would risk validating screens that expose misleading or inconsistent state.

## 36. Operation Log

- Source files modified: none.
- Source files created: none.
- Destination files created/updated: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/backend.md`.
- Packages installed: none.
- Migrations run: none.
- Database changes: none.
- Tests executed: none.
- Commits: none.
- Pushes: none.
- `DISCOVERY_REPORT.md` modified: no.

Commands executed:

```text
sed -n '1,260p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md
find /home/giga/Desktop/OSINT/GITHUB_MVP_ERP -maxdepth 1 -type f -name 'backend.md' -print
command -v rg
sed -n '261,520p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md
find . -maxdepth 4 -type f -not -path './.venv/*' -not -path './*/__pycache__/*' -print | sort
find . -maxdepth 4 -type d -not -path './.venv/*' -not -path './*/__pycache__/*' -print | sort
sed -n '1,260p' manage.py
sed -n '1,280p' config/settings/base.py
sed -n '1,180p' config/settings/local.py
sed -n '1,220p' config/urls.py
sed -n '1,180p' .env.example
sed -n '1,160p' requirements.txt
sed -n '1,240p' apps/accounts/models.py
sed -n '1,240p' apps/accounts/managers.py
sed -n '1,220p' apps/accounts/forms.py
sed -n '1,220p' apps/accounts/urls.py
sed -n '1,220p' apps/accounts/admin.py
sed -n '1,200p' apps/accounts/migrations/0001_initial.py
sed -n '1,260p' apps/businesses/models.py
sed -n '1,220p' apps/businesses/admin.py
sed -n '1,220p' apps/businesses/migrations/0001_initial.py
sed -n '1,420p' apps/catalog/models.py
sed -n '1,260p' apps/clothing/models.py
sed -n '1,260p' apps/catalog/migrations/0001_initial.py
sed -n '1,300p' apps/catalog/migrations/0002_businesstag_producttag_and_more.py
sed -n '1,260p' apps/catalog/migrations/0003_productrelation.py
sed -n '1,260p' apps/catalog/migrations/0004_businessproducttype.py
sed -n '1,260p' apps/clothing/migrations/0001_initial.py
sed -n '1,220p' apps/clothing/migrations/0002_clothingproductprofile_product_type.py
sed -n '1,220p' apps/clothing/migrations/0003_clothingproductprofile_custom_type.py
sed -n '1,260p' apps/inventory/models.py
sed -n '1,260p' apps/inventory/migrations/0001_initial.py
sed -n '1,240p' apps/analytics/models.py
sed -n '1,240p' apps/analytics/migrations/0001_initial.py
grep -R -n "@admin.register\|class .*Admin\|list_display\|list_filter\|search_fields\|readonly_fields" apps --include='admin.py' | sort
sed -n '1,260p' apps/catalog/management/commands/reset_catalog_test_data.py
sed -n '1,360p' apps/inventory/services.py
sed -n '1,320p' apps/catalog/services.py
sed -n '1,360p' apps/validation/services.py
sed -n '1,400p' apps/dashboard/services.py
sed -n '1,360p' apps/catalog/answer_generator.py
sed -n '1,360p' apps/catalog/forms.py
sed -n '1,260p' apps/catalog/urls.py
sed -n '1,260p' apps/inventory/urls.py
sed -n '1,220p' apps/dashboard/urls.py
grep -R -n "transaction.atomic\|select_for_update\|get_object_or_404\|login_required\|permission_required\|csrf_exempt\|require_POST\|require_http_methods\|Business.objects\|objects.create\|objects.get\|filter(.*business\|business=" apps --include='*.py' | sort
sed -n '1,240p' apps/catalog/views.py
sed -n '241,535p' apps/catalog/views.py
sed -n '536,805p' apps/catalog/views.py
sed -n '806,1105p' apps/catalog/views.py
sed -n '1106,1365p' apps/catalog/views.py
sed -n '1366,1610p' apps/catalog/views.py
sed -n '1,260p' apps/inventory/views.py
sed -n '1,260p' apps/dashboard/views.py
find apps -maxdepth 2 -type f -name 'views.py' -print -exec sed -n '1,120p' {} \;
grep -R -n "@login_required\|def .*request\|HttpResponseNotAllowed\|redirect(request.META\|url_has_allowed_host\|next\|HTTP_REFERER" apps --include='views.py' | sort
grep -R -n "name=\|hx-post\|hx-target\|hx-swap\|response_scope\|current_tab\|current_path\|csrf_token\|next\|quantity\|copy_mode\|target_product_id\|relation_type\|DELETE\|variant_id\|inline_" templates --include='*.html' | sort
sed -n '1,280p' templates/catalog/product_form.html
sed -n '281,620p' templates/catalog/product_form.html
sed -n '1,320p' templates/catalog/partials/product_card.html
sed -n '320,420p' templates/catalog/partials/product_card.html
sed -n '1,260p' templates/dashboard/partials/quantity_controls.html
sed -n '1,240p' templates/catalog/product_detail.html
sed -n '1,260p' templates/dashboard/home.html
sed -n '1,140p' templates/catalog/partials/product_type_section.html
sed -n '1,140p' templates/catalog/partials/product_tag_section.html
sed -n '1,180p' apps/catalog/tests.py
sed -n '181,360p' apps/catalog/tests.py
sed -n '361,540p' apps/catalog/tests.py
sed -n '541,720p' apps/catalog/tests.py
grep -R -n "^class .*Test\|^    def test_\|^def test_" apps --include='tests.py' | sort
wc -l apps/*/tests.py
sed -n '1,220p' .gitignore
find apps -maxdepth 2 -type f \( -name 'models.py' -o -name 'forms.py' -o -name 'services.py' -o -name 'views.py' -o -name 'urls.py' -o -name 'admin.py' -o -name 'apps.py' \) -print | sort
grep -R -n "Product\.LifecycleStatus\|lifecycle_status\|inventory_state\|compute_product_availability\|compute_product_readiness\|is_low_stock\|is_partially_sold_out\|is_last_piece\|message_service_safe\|can_answer_basic_questions" apps templates --include='*.py' --include='*.html' | sort
grep -R -n "BusinessTag\|BusinessProductType\|ProductTag\|EMPTY_TAG_NORMALIZED_NAME\|თეგის გარეშე\|custom_type\|product_type\|normalized_name" apps templates --include='*.py' --include='*.html' | sort
sed -n '1,180p' templates/base.html
find apps -name 'apps.py' -print -exec sed -n '1,80p' {} \;
find . -maxdepth 3 -type f \( -name '*.yml' -o -name '*.yaml' -o -name 'Dockerfile' -o -name 'Procfile' -o -name 'pyproject.toml' -o -name 'setup.cfg' -o -name 'tox.ini' -o -name 'pytest.ini' -o -name 'docker-compose*' \) -print | sort
find apps -path '*/migrations/*.py' -type f -not -name '__init__.py' -print | sort
git -C /home/giga/Desktop/OSINT/facebook_MVP status --short --branch
sed -n '1,120p' apps/dashboard/models.py
sed -n '1,120p' apps/validation/models.py
sed -n '1,120p' apps/businesses/views.py
sed -n '1,120p' apps/analytics/views.py
sed -n '1,120p' apps/clothing/views.py
sed -n '1,120p' apps/validation/views.py
sed -n '1,220p' apps/catalog/admin.py
sed -n '1,180p' apps/analytics/admin.py && sed -n '1,180p' apps/inventory/admin.py && sed -n '1,180p' apps/clothing/admin.py
grep -nE "public catalog|buyer|chatbot|AI|LLM|orders|payments|delivery|source of truth|variant|stock|ProductVariant|lifecycle|readiness|Business|owner|multi|PostgreSQL|DRF|API|future|deferred|not in MVP|Not MVP|scope|phase|Phase|Stage|Patch" inventory.md project_freeze.md specs.md checkpoint.md type_tag_assistant.md hook.md README.md reset.md startup_idea.txt seller.txt
sed -n '1,180p' reset.md
sed -n '1,160p' RUN.txt
sed -n '1,100p' README.md
grep -R -n "UsageEvent\.EventType\|UsageEvent.objects.create\|WARNING_SEEN\|WARNING_FIXED\|PRODUCT_CREATED\|PRODUCT_UPDATED\|PRODUCT_CLONED\|VARIANT_QUANTITY_CHANGED\|DASHBOARD_OPENED" apps --include='*.py' | sort
grep -R -n "select_for_update\|F(\|bulk_create\|bulk_update\|full_clean\|clean()\|unique_together\|UniqueConstraint\|CheckConstraint\|validators\|MinValueValidator\|MaxValueValidator" apps --include='*.py' | sort
grep -R -n "price_override\|base_price\|visibility\|internal_notes\|ProductPhoto\|is_primary\|primary_photo" apps templates --include='*.py' --include='*.html' | sort
date '+%Y-%m-%d %H:%M:%S %z'
wc -l apps/catalog/views.py apps/catalog/forms.py apps/inventory/services.py apps/dashboard/services.py apps/validation/services.py apps/catalog/answer_generator.py apps/catalog/tests.py
find /home/giga/Desktop/OSINT/GITHUB_MVP_ERP -maxdepth 1 -type f -print | sort
```
