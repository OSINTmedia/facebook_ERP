# Frontend, Navigation, and Seller UX Audit

## Document Metadata

- Status: LIVE
- Phase: 1C — Frontend, Navigation, and Seller UX Audit
- Source project: `/home/giga/Desktop/OSINT/facebook_MVP/`
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Based on: `DISCOVERY_REPORT.md` Phase 1A and `backend.md` Phase 1B
- Created/updated at: 2026-07-27 13:46:55 +04
- Owner: osMit
- Codex edit rule: update only through an approved frontend/UX audit task

## 1. Audit Objective

This audit records what the source prototype currently exposes to the seller through Django templates, route wiring, forms, HTMX partials, and Alpine.js interactions. Frontend and UX are treated as architecture because this product's core value depends on whether a seller can quickly maintain catalog truth, stock, taxonomy, readiness, and buyer-answer data without getting lost or doing extra navigation work.

The audit supports a future clean rebuild by separating verified frontend behavior from documentation claims, identifying navigation and state-feedback risks, and extracting rebuild inputs without creating the final UX plan. Out of scope: implementation, redesign, visual restyling, live browser testing, mobile device testing, backend redesign, test execution, and any source-project modification.

## 2. Evidence Method

Evidence labels used in this document:

- VERIFIED_IMPLEMENTED: directly confirmed in active templates, scripts, views, forms, or route wiring.
- VERIFIED_BY_SCREENSHOT: visible in a supplied or repository screenshot, but not necessarily verified as current behavior.
- VERIFIED_BY_ROUTE: confirmed by URL/view/template wiring.
- VERIFIED_BY_BACKEND_CONTRACT: supported by backend behavior recorded in `backend.md` and inspected view/form code.
- DOCUMENTED_NOT_VERIFIED: mentioned in documentation but not verified in active frontend code.
- PARTIAL: frontend behavior exists, but the flow is incomplete, inconsistent, or depends on another route.
- DUPLICATED: similar interface or interaction logic exists in multiple templates or scripts.
- FRAGILE: behavior depends on hidden coupling, DOM structure, browser behavior, template assumptions, or weak feedback.
- OVERLOADED: a page, card, form, or first viewport carries too many competing responsibilities.
- DEFERRED: explicitly planned for a future phase.
- OBSOLETE_OR_SUPERSEDED: appears to represent an older interface or project state.
- UNKNOWN: insufficient evidence or behavior not fully inspected.
- OWNER_DECISION_REQUIRED: requires product-owner judgment.

Source-code evidence was prioritized over documentation. Tests were inspected as evidence of intended contracts, but no tests were executed. No screenshots were found beyond uploaded media files, and no server or browser session was started, so rendered responsive behavior remains source-based only.

## 3. Inspection Coverage

### Inspected

- `templates/base.html`
- `templates/registration/login.html`
- `templates/dashboard/home.html`
- `templates/dashboard/partials/quantity_controls.html`
- `templates/catalog/product_list.html`
- `templates/catalog/partials/product_card.html`
- `templates/catalog/partials/product_type_section.html`
- `templates/catalog/partials/product_tag_section.html`
- `templates/catalog/partials/search_suggestions.html`
- `templates/catalog/product_form.html`
- `templates/catalog/product_detail.html`
- `templates/catalog/tag_list.html`
- `templates/catalog/type_list.html`
- `static/css/app.css`
- `apps/catalog/urls.py`
- `apps/inventory/urls.py`
- `apps/dashboard/urls.py`
- `config/urls.py`
- Frontend-relevant portions of `apps/catalog/views.py`
- Frontend-relevant portions of `apps/catalog/forms.py`
- Frontend-relevant portions of `apps/inventory/views.py`
- Frontend-relevant portions of `apps/dashboard/views.py`
- Frontend-related assertions in `apps/catalog/tests.py`
- UX/status claims in `checkpoint.md`, `hook.md`, `inventory.md`, `project_freeze.md`, `sitemap.md`, `specs.md`, and `type_tag_assistant.md`

### Not Inspected Deeply

- Live browser behavior, screenshots, viewport rendering, focus order, and actual mobile tap testing.
- Full static/media inspection beyond identifying uploaded product photos and minimal CSS.
- Full accessibility testing with assistive technology.
- Full JavaScript runtime behavior under HTMX replacement.
- Full documentation drift analysis; only obvious UX conflicts are recorded here.
- Performance under large product lists.
- Full backend state correctness; Phase 1B remains the backend source.

### Limitations

- `rg` was unavailable in the shell, so `find`, `grep`, and `sed` were used.
- The source project is not a Git repository at `/home/giga/Desktop/OSINT/facebook_MVP/`; `git status --short` returned `fatal: not a git repository`.
- No development server was started.
- No tests were run.
- No database inspection was performed.
- No browser, device, screenshot, or Playwright verification was performed.
- The audit is source-first; actual rendered layout may differ due to browser, data volume, media dimensions, and Tailwind CDN runtime behavior.

## 4. Frontend Architecture Overview

The prototype uses a server-rendered Django template architecture with Tailwind classes, HTMX for small partial updates, and Alpine.js for local disclosure, formset, copy-to-clipboard, and toast state.

Evidence map:

```text
config/urls.py
  -> dashboard: "" -> templates/dashboard/home.html
  -> catalog: "/products/" -> product list/detail/form/management templates
  -> inventory: "/inventory/variants/<pk>/quantity/" -> HTMX or redirect responses
  -> accounts: login/logout templates/routes

templates/base.html
  -> authenticated shell and navigation
  -> global messages
  -> Tailwind CDN, HTMX CDN, Alpine CDN, app.css

catalog/product_list.html
  -> search/filter controls
  -> catalog/partials/product_card.html
  -> search_suggestions datalist partial
  -> Alpine toast and productCardAnswer component

catalog/product_form.html
  -> product, clothing, photo, tag, type, variant, relation editing
  -> inline type/tag HTMX partials
  -> Alpine tokenPreview and variantFormset

dashboard/home.html
  -> summary/action sections
  -> dashboard/partials/quantity_controls.html
```

VERIFIED_IMPLEMENTED: Tailwind is loaded from CDN in `templates/base.html`; no Tailwind build configuration was inspected. VERIFIED_IMPLEMENTED: HTMX `2.0.6` and Alpine `3.14.9` are loaded from CDN. VERIFIED_IMPLEMENTED: `static/css/app.css` only sets `letter-spacing: 0`.

## 5. Template and Static Asset Inventory

| File / Directory | Role | Used By | Evidence | Notes |
|---|---|---|---|---|
| `templates/base.html` | Global shell, scripts, messages, nav | All extending templates | VERIFIED_IMPLEMENTED | Authenticated nav, no active-page indication |
| `templates/registration/login.html` | Login form | Accounts auth flow | VERIFIED_IMPLEMENTED | Email/password labels, card-like form |
| `templates/dashboard/home.html` | Seller dashboard | `dashboard.views.home` | VERIFIED_BY_ROUTE | Summary, readiness, quick actions, attention and inventory sections |
| `templates/dashboard/partials/quantity_controls.html` | HTMX +/- controls | Dashboard low-stock rows and product cards | VERIFIED_IMPLEMENTED | Target changes depending on whether `product` is passed |
| `templates/catalog/product_list.html` | Product workspace | `catalog.views.product_list` | VERIFIED_BY_ROUTE | Tabs, filters, search, cards, toasts |
| `templates/catalog/partials/product_card.html` | Product card partial | Product list and HTMX card refresh | VERIFIED_IMPLEMENTED | Dense operational card with many actions |
| `templates/catalog/product_form.html` | Create/edit form | `product_create`, `product_edit` | VERIFIED_BY_ROUTE | Product data, taxonomy, variants, relations, Alpine helpers |
| `templates/catalog/product_detail.html` | Product inspection page | `product_detail` | VERIFIED_BY_ROUTE | Summary, ready reply, variants, direct stock set |
| `templates/catalog/tag_list.html` | Tag management | Tag management views | VERIFIED_BY_ROUTE | Add, rename, hide/show, conditional delete |
| `templates/catalog/type_list.html` | Type management | Type management views | VERIFIED_BY_ROUTE | Add, rename, hide/show, conditional delete |
| `templates/catalog/partials/product_type_section.html` | Inline type picker/create | Product form HTMX endpoint | VERIFIED_IMPLEMENTED | Replaced with `outerHTML` |
| `templates/catalog/partials/product_tag_section.html` | Inline tag picker/create | Product form HTMX endpoint | VERIFIED_IMPLEMENTED | Replaced with `outerHTML` |
| `templates/catalog/partials/search_suggestions.html` | Search datalist | Search input HTMX | VERIFIED_IMPLEMENTED | Native `<datalist>` only |
| `static/css/app.css` | Global CSS | Base template | VERIFIED_IMPLEMENTED | Minimal CSS |
| `media/products/photos/*.jpg` | Uploaded product media | Product photo rendering | VERIFIED_IMPLEMENTED | Runtime media, not design assets |

## 6. Global Application Shell

VERIFIED_IMPLEMENTED: `base.html` defines `html lang="ka"`, viewport meta, Tailwind/HTMX/Alpine CDN scripts, and a centered responsive container using `max-w-md` with `sm:max-w-3xl`.

VERIFIED_IMPLEMENTED: authenticated navigation exposes `სამუშაო დაფა`, `პროდუქცია`, `+ დამატება`, and a POST logout form. There is no active route indicator, no global loading indicator, and global messages are rendered as simple white cards without severity-specific styling or ARIA live-region semantics.

PARTIAL: the global shell gives primary route access, but seller location is inferred from page heading and not reinforced in navigation. FRAGILE: reliance on CDN frontend dependencies affects offline/dev portability and portfolio-demo reliability unless frozen later.

## 7. Route-to-Template Map

| Route | View | Template | Primary Purpose | Primary Action | Return Path | Evidence |
|---|---|---|---|---|---|---|
| `/accounts/login/` | Django/accounts login view | `registration/login.html` | Seller sign-in | Submit login | Redirect behavior not deeply inspected | VERIFIED_IMPLEMENTED |
| `/` | `dashboard.views.home` | `dashboard/home.html` | Daily seller dashboard | Drill into attention/stock/readiness | Dashboard links pass `next` to product flows | VERIFIED_BY_ROUTE |
| `/products/` | `catalog.views.product_list` | `catalog/product_list.html` | Product workspace | Search/filter/update products | Optional return link from `next` | VERIFIED_BY_ROUTE |
| `/products/new/` | `catalog.views.product_create` | `catalog/product_form.html` | Create product | Save product bundle | Hidden `next`, contextual return link | VERIFIED_BY_ROUTE |
| `/products/<pk>/` | `catalog.views.product_detail` | `catalog/product_detail.html` | Product inspection | Copy reply or edit/update stock | Contextual return link from `next` | VERIFIED_BY_ROUTE; VERIFIED_BY_TEST |
| `/products/<pk>/edit/` | `catalog.views.product_edit` | `catalog/product_form.html` | Edit product bundle | Update product | Hidden `next`, contextual return link | VERIFIED_BY_ROUTE; VERIFIED_BY_TEST |
| `/products/search-suggestions/` | `catalog.views.search_suggestions` | `catalog/partials/search_suggestions.html` | Search autocomplete | Update datalist | No route navigation | VERIFIED_IMPLEMENTED |
| `/products/tags/` | `business_tag_list` | `catalog/tag_list.html` | Tag management | Add/rename/hide/show/delete | Contextual return link | VERIFIED_BY_ROUTE |
| `/products/types/` | `business_type_list` | `catalog/type_list.html` | Type management | Add/rename/hide/show/delete | Contextual return link | VERIFIED_BY_ROUTE |
| `/products/tags/inline-create/` | `product_form_tag_inline_create` | `catalog/partials/product_tag_section.html` | Inline form taxonomy creation | Create/select tag | Partial replacement only | VERIFIED_IMPLEMENTED |
| `/products/types/inline-create/` | `product_form_type_inline_create` | `catalog/partials/product_type_section.html` | Inline form taxonomy creation | Create/select type | Partial replacement only | VERIFIED_IMPLEMENTED |
| `/products/<pk>/tag/` | `product_tag_toggle` | Redirect only | Toggle card tag | POST tag attach/detach | `HTTP_REFERER` fallback | VERIFIED_BY_ROUTE; FRAGILE |
| `/products/<pk>/clone/` | `product_clone` | Redirect to edit | Clone product | POST clone mode | Redirects to edit with `next` | VERIFIED_BY_ROUTE |
| `/products/<pk>/archive/` | `product_archive` | Redirect only | Archive product | POST archive | Hidden `next` where template provides it | VERIFIED_BY_ROUTE |
| `/products/<pk>/restore/` | `product_restore` | Redirect only | Restore product | POST restore | Hidden `next` where template provides it | VERIFIED_BY_ROUTE |
| `/products/<pk>/relation/add/` | `product_relation_add` | Redirect to edit | Add relation | POST relation | Hidden `next` in edit form | VERIFIED_BY_ROUTE |
| `/products/<pk>/relation/remove/` | `product_relation_remove` | Redirect to edit | Hide relation | POST remove | Hidden `next` in edit form | VERIFIED_BY_ROUTE |
| `/inventory/variants/<pk>/quantity/` | `inventory.views.variant_quantity_update` | Partial or redirect | Update quantity | POST increment/decrement/set | HTMX local replace or redirect to detail | VERIFIED_IMPLEMENTED |

## 8. Page Responsibility Matrix

| Page | Intended Responsibility | Actual Responsibility | Main Action | Overlap | Risk |
|---|---|---|---|---|---|
| Dashboard | Answer what needs attention today | Summary, readiness report, quick links, attention, low stock, last piece, sold-out groups | Drill down to product list/edit/detail | Product workspace stock controls appear in low-stock section | OVERLOADED first viewport may delay specific work |
| Product workspace | Daily catalog and stock operations | Search, filters, taxonomy entry, cards, stock, readiness, replies, tags, clone, archive | Operate on product cards | Detail page duplicates answer and stock operations | OVERLOADED cards and filter rows |
| Create form | Add catalog truth | Product, photo, type, tags, variants, recognition preview | Save | Edit form shares same template | PARTIAL progressive disclosure |
| Edit form | Correct/complete catalog truth | Same as create plus relations | Update | Product detail and card both link into edit | OVERLOADED for routine small corrections |
| Detail page | Secondary inspection | Summary, answer helper, stock controls, clone/edit | Copy reply or set stock | Product card duplicates most answer behavior | OWNER_DECISION_REQUIRED |
| Tag management | Controlled vocabulary management | Add, rename, hide/show, delete/recovery links | Maintain tags | Inline tag creation also exists in form and card tag toggles exist | PARTIAL distinction from types |
| Type management | Controlled vocabulary management | Add, rename, hide/show, delete/recovery links | Maintain types | Inline type creation also exists in form | PARTIAL distinction from tags |

## 9. Dashboard Audit

VERIFIED_IMPLEMENTED: the dashboard opens with a business summary, then inventory state, readiness summary, quick actions, attention items, last-piece, low-stock, partially sold-out, and fully sold-out sections.

PARTIAL: the dashboard answers `დღეს რას მივხედო?` through attention and stock sections, but the first viewport is likely consumed by business summary, inventory metrics, and readiness summary before concrete per-product work appears. This is source-based only because no rendered viewport was tested.

VERIFIED_IMPLEMENTED: inventory and readiness rows are links to filtered product lists with `next={{ current_page_url|urlencode }}`. VERIFIED_IMPLEMENTED: attention links point to product edit with `next` back to dashboard. VERIFIED_IMPLEMENTED: low-stock rows include `quantity_controls.html`, but because no `product` context is passed, HTMX replaces only the control fragment, not the dashboard section or summary counts.

FRAGILE: dashboard local stock updates can leave dashboard counts, low-stock groups, and sold-out sections stale until page refresh. OVERLOADED: repeated summary blocks and many cards compete with the daily action queue.

## 10. Product Workspace Audit

VERIFIED_IMPLEMENTED: the product workspace includes a top return link when `next` is present, header card, add button, lifecycle tabs, type filter row, tag filter row, search form, token display, search clearing, empty states, product cards, and Alpine toast handling for sold-out/restocked HTMX events.

VERIFIED_IMPLEMENTED: the product card exposes photo, title/detail link, price, ready reply toggle, status badges, readiness explanation, timestamps, quick tag toggles, variant-level stock controls, edit, clone menu, archive/restore.

OVERLOADED: the page attempts to be list, search, taxonomy browser, stock cockpit, readiness console, reply generator, clone hub, and archive surface at the same time. On mobile, the tab row, type row, tag row, and search block can consume substantial vertical space before the seller reaches product cards.

PARTIAL: server-rendered state remains the main truth after HTMX product-card refresh, but surrounding list state can become stale after stock transitions.

## 11. Product Card Anatomy

Ordered structural map:

1. Outer `<article>` with product id and Alpine flash/answer state.
2. Photo thumbnail or placeholder.
3. Name link to detail, price, `მზა პასუხი` toggle, `დეტალურად` link.
4. Inventory status badge.
5. Type/readiness/stock/lifecycle/relation/quantity badges.
6. Collapsible buyer-ready reply panel.
7. Collapsible readiness explanation and next-action chips.
8. Created/updated timestamps.
9. Visible tag chips and collapsible tag toggle picker.
10. Active variant rows with HTMX quantity controls.
11. Edit, clone dropdown, archive/restore actions.

| Element | Purpose | Action Type | State Dependency | Feedback | UX Risk | Evidence |
|---|---|---|---|---|---|---|
| Product photo | Visual recognition | Link-adjacent display | `primary_photo` | Placeholder if missing | Small image may be insufficient for visual inventory | VERIFIED_IMPLEMENTED |
| Product title | Detail navigation | Link | Product id, `current_list_url` | Browser navigation | Competes with `დეტალურად` link | VERIFIED_IMPLEMENTED |
| Price | Seller scan fact | Display | `base_price`, currency | None | Zero-price semantics not explained on card | VERIFIED_IMPLEMENTED |
| Ready reply toggle | Reveal buyer answer | Alpine local toggle | `answer_generator_payload` | Panel opens/closes | Hidden until discovered; adds card complexity | VERIFIED_IMPLEMENTED |
| Status badges | Fast state scan | Display | Decorated backend state | Color/text badges | Badge count can become noisy | VERIFIED_IMPLEMENTED |
| Ready reply panel | Copy buyer text | Alpine local state | Deterministic payload | Copy text changes to `დაკოპირდა` | DUPLICATED with detail page; clipboard failure has no visible error | VERIFIED_IMPLEMENTED |
| Readiness explanation | Explain missing facts | Alpine local toggle | Readiness service | Opens with action chips | FRAGILE as interactive `<div>` without button semantics | VERIFIED_IMPLEMENTED |
| Quick tags | Attach/detach tags | POST forms | `business_tags`, `active_tag_ids` | Redirect via referer | FRAGILE return context, local panel closes after navigation | VERIFIED_IMPLEMENTED |
| Variant controls | Increment/decrement stock | HTMX POST | Variant quantity | Button disabled during request; card flash/toast possible | Surrounding counts/tabs stale after transitions | VERIFIED_IMPLEMENTED |
| Clone menu | Choose copy mode | Alpine menu + POST | Product id, copy mode | Redirect and global message | Menu lacks formal menu semantics; adds action competition | VERIFIED_IMPLEMENTED |
| Archive/restore | Lifecycle update | POST form | lifecycle status | Confirm for archive, message after redirect | Destructive action close to routine actions | VERIFIED_IMPLEMENTED |

## 12. Product Create/Edit Form Audit

VERIFIED_IMPLEMENTED: the shared form template starts with a contextual return link, renders non-field errors, then `ძირითადი ინფორმაცია`, name/token recognition, price/status, target audience, photo, inline type picker/create, inline tag picker/create, variant formset, save/cancel, and relation management when editing an existing product.

VERIFIED_BY_BACKEND_CONTRACT: required backend fields include product name, price, lifecycle, target audience, custom type, and at least one completed active variant with size, color, and quantity. Photo and tags are optional.

OVERLOADED: the edit form combines deep catalog editing, stock truth, type/tag dictionary creation, recognition preview, photo upload, and product relations. This is powerful but heavy for small corrections triggered from readiness chips.

PARTIAL: helper text explains why fields matter for search and answer readiness, but repeated helper copy increases cognitive load. PARTIAL: token/type/tag recognition preview is visible, but source shows it only displays recognized values and does not automatically select them.

## 13. Dynamic Choice Form Audit

VERIFIED_IMPLEMENTED: `variantFormset()` reads `id_variants-TOTAL_FORMS` and `id_variants-MAX_NUM_FORMS`, clones `empty-form-template`, replaces `__prefix__`, appends rows, increments `TOTAL_FORMS`, and removes newly added rows from the DOM.

VERIFIED_BY_BACKEND_CONTRACT: backend formset validation requires at least one non-deleted, non-empty completed choice.

FRAGILE: unsaved-row removal does not decrement or renumber `TOTAL_FORMS`; it relies on Django formset tolerance for absent or empty indexes. Existing rows use a visible DELETE checkbox, so the UI allows the seller to mark every existing choice for deletion before backend validation rejects it.

PARTIAL: validation errors are rendered after a server response, but no source evidence shows focus management or automatic scroll to the problematic variant row.

## 14. Product Detail Audit

VERIFIED_IMPLEMENTED: detail page has a contextual return link, product summary, buyer-ready reply block, active variant list, increment/decrement buttons, direct set quantity input, edit link, and clone form.

DUPLICATED: buyer-ready reply behavior is implemented separately from the product-card answer panel. DUPLICATED: stock increment/decrement appears both on cards and detail; direct set quantity appears only on detail.

OWNER_DECISION_REQUIRED: the unique purpose of Product Detail is not clear enough from source. It may be valuable as a focused inspection and stock-set surface, but it also creates a route hop because core card operations already exist in the workspace.

## 15. Ready Reply Interface Audit

VERIFIED_IMPLEMENTED: product cards reveal `მყიდველისთვის მზა პასუხი` inside an Alpine panel with answer modes, buyer text, seller-only notes, copy button, and edit/fill link. Detail page shows a similar answer generator using JSON from `answer_generator_payload`.

VERIFIED_BY_BACKEND_CONTRACT: answer text is generated from stored/decorated product data, not from an LLM. Missing data can disable or empty an answer mode and show notes.

PARTIAL: the feature is discoverable through a compact `მზა პასუხი` link on every card, but it competes with `დეტალურად`, readiness badges, tag toggles, and stock controls. PARTIAL: copy success is local and short-lived; copy failure falls back to `document.execCommand('copy')` with no visible failure message if both mechanisms fail.

## 16. Search and Filter UX

VERIFIED_IMPLEMENTED: product list search uses a GET form, hidden fields for active filters, native `<datalist>` suggestions via HTMX, token display, clear-search link, no-result guidance, and a broad-search note when no tab is requested.

VERIFIED_BY_BACKEND_CONTRACT: search tokenization/filtering includes product name, target audience, variant size/color, tags, and custom type where tables exist.

PARTIAL: filter state is visible through selected tabs/pills and token chips, but multiple horizontal/overflow filter rows can dominate mobile. FRAGILE: suggestions are native datalist entries only; there is no loading or error feedback for the HTMX suggestion request.

## 17. Type and Tag Management UX

### Types

VERIFIED_IMPLEMENTED: type management supports create, inline rename, hide, show, conditional permanent delete, disabled delete when products use a type, and recovery link to `catalog:list?type=<id>&next=<type_list>`.

PARTIAL: terminology presents types as product classification, but management and inline form creation compete with each other as two places to create the same dictionary entries.

### Tags

VERIFIED_IMPLEMENTED: tag management supports create, inline rename, hide, show, conditional permanent delete, disabled delete when products use a tag, and recovery link to `catalog:list?tag=<id>&next=<tag_list>`.

PARTIAL: tags are explained as grouping/search helpers. Source verifies that the reserved `თეგის გარეშე` sentinel is excluded from tag selection and management visibility.

### Conceptual Distinction

PARTIAL: source wording separates type as `რა ტიპის პროდუქციაა?` and tags as optional grouping/search labels. OWNER_DECISION_REQUIRED: whether separate management pages are necessary in Portfolio V1, or whether inline-first taxonomy is enough.

## 18. Product Relations UX

VERIFIED_IMPLEMENTED: relations appear only on the edit form for existing products. The UI lists confirmed outgoing relations, allows removal with confirm, and offers relation type plus target product selects for active products in the same business.

PARTIAL: product cards show only a relation-count badge. The ready-reply surface does not visibly use relations for buyer recommendations. OVERLOADED: relation controls extend the already-long edit form and may not belong in the first portfolio MVP.

OWNER_DECISION_REQUIRED: whether Product Relations should remain in Portfolio V1 or be deferred as future assistant/public-catalog infrastructure.

## 19. HTMX Interaction Inventory

| Trigger | Endpoint | Target | Swap/Redirect | Success Feedback | Failure Feedback | Risk |
|---|---|---|---|---|---|---|
| Search input keyup/change | `catalog:search_suggestions` | `#search-suggestions` | `outerHTML` datalist | Native browser suggestions | No visible HTMX error | PARTIAL |
| Product-card +/- quantity | `inventory:variant_quantity_update` | `#product-card-<pk>` | `outerHTML` card refresh | Card flash; optional sold-out/restocked toast | Non-HTMX errors redirect to detail; HTMX error surface unclear | FRAGILE stale list counts/tab membership |
| Dashboard low-stock +/- quantity | `inventory:variant_quantity_update` | `#variant-<pk>-controls` | `outerHTML` controls only | Quantity control updates | No section/count refresh | FRAGILE stale dashboard state |
| Inline type add | `catalog:type_inline_create` | `#product-type-section` | `outerHTML` | Inline message and selected radio | Inline message | PARTIAL registry preview updates through custom event |
| Inline tag add | `catalog:tag_inline_create` | `#product-tag-section` | `outerHTML` | Inline message and selected checkbox | Inline message | PARTIAL registry preview updates through custom event |

## 20. Alpine.js Interaction Inventory

| Component/State | Template | Purpose | DOM Dependency | HTMX Interaction | Risk |
|---|---|---|---|---|---|
| `productCardAnswer` | `product_list.html` + `product_card.html` | Answer mode and copy | Searches `data-reply-mode` inside `$root` | Product-card replacement keeps markup but script lives on list page | FRAGILE if partial reused elsewhere |
| `answerOpen` | `product_card.html` | Toggle answer panel | Local article state | Lost after HTMX card replacement | PARTIAL |
| `expanded` readiness | `product_card.html` | Show readiness explanation | Clickable div and local state | Lost after HTMX card replacement | Accessibility risk |
| `showTags` | `product_card.html` | Reveal tag toggle forms | Local state | POST causes page navigation | FRAGILE return via referer |
| `cloneOpen` | `product_card.html` | Clone mode menu | Absolute dropdown, click-away | POST redirects | Accessibility/menu semantics risk |
| Sold-out/restocked toast | `product_list.html` | Transition feedback | Window events and fixed container | Uses `HX-Trigger` from inventory view | PARTIAL global counts unchanged |
| `tokenPreview` | `product_form.html` | Token/type/tag recognition preview | Reads JSON script registries and input id | Inline taxonomy response dispatches registry event | PARTIAL recognition does not auto-apply |
| `variantFormset` | `product_form.html` | Add/remove variant rows | Requires management-form ids and template id | None | FRAGILE index management |
| `productAnswerGenerator` | `product_detail.html` | Detail reply modes and copy | Reads JSON script id | None | DUPLICATED with card answer logic |
| `submitting` | `product_detail.html` | Disable stock buttons on submit | Per-form local state | Plain POST, not HTMX | PARTIAL no inline failure recovery |

## 21. Loading, Success, Error, and Recovery Feedback

| Action | Loading | Success | Failure | Recovery | Evidence |
|---|---|---|---|---|---|
| Login | None visible in template | Auth redirect assumed | Field/non-field errors rendered | Retry form | VERIFIED_IMPLEMENTED |
| Product create/edit | None visible | Global message after redirect | Form and formset errors rendered | Same form, contextual return link | VERIFIED_IMPLEMENTED |
| Inline type/tag create | No explicit loader | Inline message | Inline warning/error message | Continue in same form section | VERIFIED_IMPLEMENTED |
| Add variant row | Immediate DOM append | New row appears | No max warning source found | Manual remove unsaved row | VERIFIED_IMPLEMENTED |
| Existing variant deletion | None | Save if backend accepts | Non-form error if zero choices | Return to form | VERIFIED_BY_BACKEND_CONTRACT |
| Product-card quantity | Disabled buttons via `hx-disabled-elt` | Card refresh, flash, possible toast | HTMX error display not visible | Full page refresh likely needed | VERIFIED_IMPLEMENTED |
| Dashboard quantity | Disabled buttons via `hx-disabled-elt` | Control refresh | HTMX error display not visible | Full page refresh likely needed | VERIFIED_IMPLEMENTED |
| Detail quantity set | Buttons disabled by Alpine submit state | Redirect/global message | Redirect/global message | Detail page | VERIFIED_IMPLEMENTED |
| Copy reply | None | Button text `დაკოპირდა` | No visible failure after fallback | Retry | VERIFIED_IMPLEMENTED |
| Clone | None | Global message and edit redirect | Not visibly surfaced for server failure | Edit page/return link | VERIFIED_IMPLEMENTED |
| Archive | Native confirm | Global message and redirect | Not visibly detailed | Return list/detail via `next` | VERIFIED_IMPLEMENTED |
| Tag/type delete blocked | Disabled delete if count > 0; backend also guards | Delete message if unused | Error message if used | Connected-products link | VERIFIED_IMPLEMENTED |

## 22. Navigation and Return-Path Map

| Journey | Start | Destination | Context Preserved | Explicit Return | Browser Back Dependency | Risk |
|---|---|---|---|---|---|---|
| Dashboard -> products | Dashboard cards/quick actions | Product list filtered by tab/readiness | `next` back to dashboard | Product list return link | Low | VERIFIED_IMPLEMENTED |
| Dashboard attention -> edit -> dashboard | Attention item | Product edit | `next` back to dashboard | Form return link and post redirect | Low | VERIFIED_BY_TEST |
| Product list -> detail -> list | Card title/detail | Detail | `next=current_list_url` | Detail return link | Low | VERIFIED_BY_TEST |
| Product list -> edit -> filtered list | Card edit/fill | Edit | `next=current_list_url` | Form return link and post redirect | Low | VERIFIED_BY_TEST |
| Ready reply -> fill missing data -> return | Card/detail answer note | Edit | `next` from current list/detail | Form return link | Low/medium | VERIFIED_IMPLEMENTED |
| Clone -> copied product edit -> original context | Card/detail clone | Edit cloned product | Original `next` passed to edit | Form return link | Low/medium | VERIFIED_IMPLEMENTED |
| Tag management -> connected products -> management | Tag list | Filtered product list | `next=tag_list` | Product list return link | Low | VERIFIED_BY_TEST |
| Type management -> connected products -> management | Type list | Filtered product list | `next=type_list` | Product list return link | Low | VERIFIED_BY_TEST |
| Card tag toggle | Product card | Redirect back | `HTTP_REFERER` only | No explicit hidden `next` in toggle forms | Medium | FRAGILE |
| Archive/restore | Product card | Return URL | Hidden `next=current_list_url` | Redirect target | Low | VERIFIED_IMPLEMENTED |
| Search/filter -> stock update | Product list | Same card | Current path sent to HTMX | Card links keep current path after refresh | Medium | PARTIAL counts and tab membership stale |

## 23. Information Hierarchy and Visual Density

### First Viewport Problems

Dashboard first viewport is likely weighted toward business summary and metrics before concrete per-product actions. Product workspace first viewport stacks return/header, tabs, type filters, tag filters, search, helper text, and only then product cards. Evidence is source-based, not rendered.

### Card Density

Product cards carry photo, title, price, multiple badges, reply controls, readiness, tags, variants, stock controls, edit, clone, and archive/restore. OVERLOADED: the card is the central operating unit, but too many responsibilities compete.

### Form Density

Product form combines create/edit concerns, taxonomy, photo, variants, recognition preview, and relations. OVERLOADED on edit.

### Repeated Information

Readiness and answer-readiness appear on dashboard, product cards, and detail. Stock appears on dashboard, card, detail, and badges. DUPLICATED information can help scanning, but risks inconsistent freshness after partial updates.

### Competing Actions

On cards, `მზა პასუხი`, `დეტალურად`, edit, clone, tags, stock buttons, and archive all appear within one card. The primary action is not visually singular.

### Excessive Helper Copy

Helper copy exists in search, form name, type/tag sections, variant section, dashboard summaries, and empty states. Some copy is operationally useful; later UX planning should reduce repeated explanations once the interface itself communicates the workflow.

### Disclosure Problems

Alpine disclosures reduce initial clutter but lack `aria-expanded`/`aria-controls` evidence and lose state after HTMX replacement.

## 24. Mobile-First Assessment

### Verified from Source

VERIFIED_IMPLEMENTED: templates use small-screen-first classes, `flex-wrap`, `overflow-x-auto`, `sm:grid-cols-2`, `w-full sm:w-auto`, and compact `max-w-md` container defaults. Buttons generally have adequate padding, and card actions often stack.

### Verified by Screenshot

UNKNOWN: no repository screenshots were found or inspected. Uploaded media exists in `media/products/photos/`, but these are product photos, not UI screenshots.

### Requires Live Device Testing

- Actual first viewport content on common mobile heights.
- Long Georgian labels in filters, badges, and action buttons.
- Clone dropdown placement near the bottom of cards.
- Keyboard/focus behavior of Alpine disclosures and menus.
- HTMX error rendering on mobile.
- Whether type/tag rows and search create excessive scroll before products.

### Main Mobile Risks

OVERLOADED filter stack, tall cards, long edit form, relation controls on edit, many close-proximity actions, native datalist inconsistency across mobile browsers, and stale surrounding dashboard/list state after partial updates.

## 25. Accessibility and Semantic Assessment

| Area | Current Evidence | Risk | Rebuild Requirement |
|---|---|---|---|
| Navigation | Links and logout form in header | No active-current state | Current page must be explicit |
| Forms | Labels are mostly explicit | Errors not clearly associated with fields via ARIA | Field error association and focus recovery |
| Disclosure controls | Some are buttons, readiness trigger is clickable div | Keyboard and screen-reader ambiguity | Use buttons with `aria-expanded`/`aria-controls` |
| Clone menu | Alpine dropdown with click-away | No menu semantics or Escape handling visible | Accessible menu or simpler command structure |
| Status badges | Text labels accompany colors | Many small badges may be hard to parse | Text-first status hierarchy |
| Images | Product photo alt uses product name | Placeholder is text only | Maintain meaningful alt and empty-photo state |
| Global messages | Rendered visually | No `role=status` or `role=alert` evidence | Semantic message regions |
| HTMX updates | Button disabling on quantity controls | No announced updates/errors | Accessible loading/success/error feedback |
| Native confirm | Used for archive/delete/hide | Browser modal is blunt but accessible-ish | Clear safer destructive-action patterns |

No full WCAG compliance claim is made.

## 26. Georgian Terminology Audit

| Concept | Current Wording | Inconsistency/Ambiguity | Risk | Owner Decision |
|---|---|---|---|---|
| Product workspace | `პროდუქცია` | Broad label for catalog, inventory, replies, filters | Seller may not know page's primary job | OWNER_DECISION_REQUIRED |
| Dashboard | `სამუშაო დაფა`, `ინვენტარის cockpit` | Mixed Georgian/English `cockpit` | Could feel prototype-like | OWNER_DECISION_REQUIRED |
| Ready reply | `მზა პასუხი`, `მყიდველისთვის მზა პასუხი` | Compact label may be unclear until opened | Discoverability risk | OWNER_DECISION_REQUIRED |
| Readiness | `პასუხისთვის მზადაა`, `შესავსებია`, `მცირე ინფორმაცია აკლია` | Wording mostly operational | Needs final vocabulary freeze | OWNER_DECISION_REQUIRED |
| Type | `ტიპი`, `რა ტიპის პროდუქციაა?` | Clearer than legacy free text | Must remain distinct from tags | OWNER_DECISION_REQUIRED |
| Tags | `თეგები`, `#` chips | Georgian sellers may know tags, but concept overlaps type | Taxonomy confusion | OWNER_DECISION_REQUIRED |
| Variant/choice | `არჩევანები`, `ზომა/ფერის არჩევანი`, code uses variant | UI avoids technical variant term | Need freeze wording | OWNER_DECISION_REQUIRED |
| Archive/hidden | `არქივი`, `დაარქივება`, hidden mapped to archive label | Stored hidden state has no distinct UI meaning | Lifecycle confusion | OWNER_DECISION_REQUIRED |
| Stock | `ნაშთი`, `დარჩენილია`, `სულ` | Mostly consistent | `სულ` badge may be too terse | OWNER_DECISION_REQUIRED |

## 27. Seller Journey Reconstruction

### 1. Seller signs in

- Start: `/accounts/login/`.
- Actions: enter email/password and submit.
- System response: authentication flow redirects if valid.
- Feedback: non-field errors render in login template.
- Return path: not deeply inspected.
- Friction: no password-reset or onboarding evidence in inspected template.
- Evidence: VERIFIED_IMPLEMENTED for template; UNKNOWN for full auth redirects.

### 2. Seller creates a first product

- Start: global `+ დამატება` or product-list add link.
- Actions: fill name, price, lifecycle, target audience, type, optional tags/photo, at least one choice.
- System response: view saves bundle and redirects to safe `next` or product list.
- Feedback: global success message; form errors on invalid POST.
- Return path: form return link and hidden `next`.
- Friction: first product may require creating a type inline before saving.
- Evidence: VERIFIED_IMPLEMENTED; VERIFIED_BY_BACKEND_CONTRACT.

### 3. Seller adds multiple size/color choices

- Start: product form.
- Actions: click `+ ზომა/ფერის არჩევანის დამატება`, complete size/color/quantity.
- System response: Alpine appends form rows; backend validates on POST.
- Feedback: field/formset errors after submit.
- Return path: same product form.
- Friction: dynamic row indexes and delete behavior are fragile.
- Evidence: VERIFIED_IMPLEMENTED; FRAGILE.

### 4. Seller searches for a product

- Start: `/products/`.
- Actions: type into search input, optionally choose browser datalist suggestion, submit.
- System response: HTMX updates datalist; GET list filters results.
- Feedback: tokens, result count, clear search, no-result guidance.
- Return path: URL encodes query/filter state.
- Friction: datalist behavior varies by browser; filter stack is dense.
- Evidence: VERIFIED_IMPLEMENTED.

### 5. Seller updates stock from the product workspace

- Start: product card variant row.
- Actions: press `-1` or `+1`.
- System response: HTMX POST replaces product card.
- Feedback: disabled buttons during request, flash, optional sold-out/restocked toast.
- Return path: stays on list.
- Friction: global counts and current tab membership can become stale.
- Evidence: VERIFIED_IMPLEMENTED; PARTIAL.

### 6. Product becomes sold out

- Start: active product card stock decrement.
- Actions: reduce final active variant to zero.
- System response: card refresh and `product-sold-out` toast when transition detected.
- Feedback: toast says product moved to sold-out and includes `ნახვა` link.
- Return path: stays on current page unless seller clicks sold-out tab link.
- Friction: card may remain visible in active tab until full refresh.
- Evidence: VERIFIED_IMPLEMENTED; FRAGILE.

### 7. Seller restocks a product

- Start: sold-out tab product card or detail page.
- Actions: increment or set positive quantity.
- System response: HTMX card refresh or plain redirect.
- Feedback: restocked toast for HTMX card scope; global message for plain POST.
- Return path: current path sent to card response.
- Friction: surrounding tab counts/sections remain stale.
- Evidence: VERIFIED_IMPLEMENTED; PARTIAL.

### 8. Seller fixes missing product information

- Start: dashboard attention, readiness filter, card readiness explanation, or ready reply notes.
- Actions: click edit/fill action, update fields, save.
- System response: save redirects to `next`.
- Feedback: global success or inline validation errors.
- Return path: `next` preserves dashboard/list/detail in most inspected flows.
- Friction: edit form is long for narrow fixes.
- Evidence: VERIFIED_IMPLEMENTED; VERIFIED_BY_TEST for several return paths.

### 9. Seller prepares and copies a buyer reply

- Start: product card `მზა პასუხი` or detail answer block.
- Actions: choose mode, copy.
- System response: Alpine copies deterministic reply.
- Feedback: button text changes to `დაკოპირდა`.
- Return path: no navigation unless edit/fill clicked.
- Friction: failure is not visibly surfaced; feature competes with other card controls.
- Evidence: VERIFIED_IMPLEMENTED.

### 10. Seller clones a product

- Start: card clone dropdown or detail clone button.
- Actions: choose clone mode on card, or submit default clone on detail.
- System response: clone view redirects to edit cloned product with contextual `next`.
- Feedback: global message gives rename/change nudge.
- Return path: edit form return link/post redirect uses preserved `next`.
- Friction: card has richer clone modes than detail.
- Evidence: VERIFIED_IMPLEMENTED.

### 11. Seller manages product types

- Start: product-list `+ ტიპების მართვა`, product form inline type section, or recovery link.
- Actions: create, rename, hide/show, delete unused, inspect used products.
- System response: redirects to management page with `next`, or HTMX partial for inline creation.
- Feedback: global messages or inline message.
- Return path: explicit top and bottom return links.
- Friction: separate page plus inline creation may split workflow.
- Evidence: VERIFIED_IMPLEMENTED.

### 12. Seller manages tags

- Start: product-list `+ თეგების მართვა`, product form inline section, card `+ თეგი`, or recovery link.
- Actions: create, rename, hide/show, delete unused, inspect used products, toggle card tags.
- System response: redirects/partials depending on action.
- Feedback: global messages or inline message.
- Return path: management page links preserve context; card toggle relies on `HTTP_REFERER`.
- Friction: card tag toggle route lacks explicit hidden `next`.
- Evidence: VERIFIED_IMPLEMENTED; FRAGILE.

### 13. Seller archives and restores a product

- Start: product card.
- Actions: archive with confirm or restore from archived/hidden card.
- System response: lifecycle changes and redirects to current list URL.
- Feedback: global success message.
- Return path: hidden `next=current_list_url`.
- Friction: hidden and archived states are displayed together as archive.
- Evidence: VERIFIED_IMPLEMENTED; OWNER_DECISION_REQUIRED for terminology.

## 28. Frontend Duplication and Technical Debt

### Critical

- Location: `product_card.html` with `product_list.html` toast/count context.
- Mechanism: HTMX refresh replaces one card but not surrounding list/dashboard counts or current tab membership.
- Seller consequence: seller can see stale dashboard/list state after stock transitions.
- Rebuild implication: define partial-update boundaries and global-state refresh rules.
- Evidence: PARTIAL; FRAGILE.

### High

- Location: `product_card.html`.
- Mechanism: one card contains reply generation, readiness, tags, variants, inventory, clone, archive, detail, and edit.
- Seller consequence: primary action hierarchy is unclear, especially on mobile.
- Rebuild implication: product workspace card anatomy needs a frozen responsibility model.
- Evidence: OVERLOADED.

- Location: `product_form.html`.
- Mechanism: create/edit form includes core product data, taxonomy creation, dynamic variants, photo upload, recognition preview, and relation management.
- Seller consequence: small fixes require entering a long form.
- Rebuild implication: distinguish quick corrections from deep edit.
- Evidence: OVERLOADED.

### Medium

- Location: `product_card.html` and `product_detail.html`.
- Mechanism: separate Alpine answer generators duplicate ready-reply behavior.
- Seller consequence: inconsistent maintenance risk and unclear detail-page value.
- Rebuild implication: one answer surface contract should be frozen.
- Evidence: DUPLICATED.

- Location: `product_card.html` tag toggle forms and `catalog.views.product_tag_toggle`.
- Mechanism: redirect uses `HTTP_REFERER` instead of explicit `next`.
- Seller consequence: context depends on browser headers.
- Rebuild implication: all state-changing operations should carry explicit safe return context.
- Evidence: FRAGILE.

- Location: `product_form.html` variant formset.
- Mechanism: client-side add/remove relies on management-form ids and non-renumbered indexes.
- Seller consequence: data loss or confusing validation is possible under edge cases.
- Rebuild implication: dynamic choice editing needs robust formset or simpler server-rendered pattern.
- Evidence: FRAGILE.

### Low

- Location: `base.html`.
- Mechanism: no active nav indicator and generic global message styling.
- Seller consequence: weaker wayfinding and lower feedback specificity.
- Rebuild implication: shell should expose current location and semantic messages.
- Evidence: PARTIAL.

- Location: templates broadly.
- Mechanism: repeated helper text and status copy.
- Seller consequence: cognitive load.
- Rebuild implication: freeze Georgian vocabulary and reduce repeated explanations.
- Evidence: PARTIAL.

## 29. Possible Lost or Regressed Behaviors

| Feature | Evidence | Current Visibility | Confidence | Deep Verification Required |
|---|---|---|---|---|
| Contextual return paths described as missing in `sitemap.md` | Source/tests now show many `next` flows | Mostly visible in product/detail/edit/management pages | Medium | Documentation-drift audit |
| Global count sync after HTMX stock changes | `checkpoint.md` says dashboard/header/tab sync deferred; source confirms local-only refresh | Not visible after partial update | High | Live interaction test |
| Card answer behavior after HTMX replacement | Card partial relies on Alpine component registered in `product_list.html` | Works when page script is present | Medium | HTMX/browser test |
| Product relations in buyer reply | Relation badge/edit UI exists; reply UI does not visibly include related recommendations | Relation value mostly hidden | Medium | Backend/frontend synthesis |
| Public visibility/hidden lifecycle distinction | Hidden stored state displayed as archive; public catalog absent | Not separately visible | High | Product owner decision |
| Type/tag recognition as assistant | Source shows preview only; no auto-apply | Visible as `ამოვიცანი` in form | High | Owner decision on expected behavior |

## 30. Frontend Patterns Worth Preserving

- VERIFIED_IMPLEMENTED: server-rendered Django pages with small HTMX partials fit the seller-first cockpit without requiring a SPA.
- VERIFIED_IMPLEMENTED: variant-level inline `+1/-1` controls make stock truth directly actionable.
- VERIFIED_IMPLEMENTED: contextual `next` return links are now present on many high-friction flows.
- VERIFIED_IMPLEMENTED: deterministic ready-reply surface turns stored product truth into seller-usable text.
- VERIFIED_IMPLEMENTED: controlled type/tag dictionaries appear in both management pages and inline form creation.
- VERIFIED_IMPLEMENTED: empty states and blocked-delete recovery links give practical seller next steps.
- VERIFIED_IMPLEMENTED: Georgian seller-facing copy avoids most internal code terms such as `variant`.

## 31. Frontend Patterns Requiring Redesign

- Current behavior: product cards carry too many actions and statuses.
  Why it fails: scanning and primary-action hierarchy weaken.
  Rebuild direction: freeze card responsibility and move secondary actions behind deliberate paths.
  Evidence: OVERLOADED.

- Current behavior: dashboard begins with summaries before specific work items.
  Why it fails: daily cockpit value may be delayed below the fold.
  Rebuild direction: first viewport should prioritize actionable attention or stock work.
  Evidence: PARTIAL; source-based mobile assessment.

- Current behavior: edit form combines routine correction, taxonomy creation, variant editing, and relations.
  Why it fails: correction journeys become heavy.
  Rebuild direction: separate quick corrections from full edit where evidence supports it.
  Evidence: OVERLOADED.

- Current behavior: HTMX partial updates do not refresh surrounding aggregate state.
  Why it fails: visible counts and grouping can become stale.
  Rebuild direction: define update contract for card, list counters, dashboard widgets, and transition movements.
  Evidence: FRAGILE.

- Current behavior: detail page duplicates card reply and stock behavior.
  Why it fails: route-hop cost may exceed unique value.
  Rebuild direction: owner must decide whether detail is inspection, advanced stock set, or deferred.
  Evidence: DUPLICATED; OWNER_DECISION_REQUIRED.

- Current behavior: Alpine disclosure/menu controls lack explicit accessibility state.
  Why it fails: keyboard and assistive tech behavior is uncertain.
  Rebuild direction: semantic controls with predictable focus and state.
  Evidence: PARTIAL.

## 32. Frontend and UX Invariants for Rebuild

- Every seller page has one primary responsibility: RECOMMENDED_FROM_EVIDENCE.
- Every drilldown has an explicit safe return path: VERIFIED_EXISTING for many flows; RECOMMENDED_FROM_EVIDENCE globally.
- Filtered workspace context survives edit/detail flows: VERIFIED_EXISTING for list edit/detail; RECOMMENDED_FROM_EVIDENCE globally.
- Seller does not depend on browser Back: PARTIAL existing; RECOMMENDED_FROM_EVIDENCE.
- First viewport exposes useful work, not just summaries: RECOMMENDED_FROM_EVIDENCE.
- Stock changes provide immediate local feedback: VERIFIED_EXISTING.
- Server-rendered state remains truth after HTMX updates: VERIFIED_EXISTING for card refresh; RECOMMENDED_FROM_EVIDENCE.
- Aggregate counts and grouping do not remain stale after local updates: RECOMMENDED_FROM_EVIDENCE.
- Critical product truth is visible before secondary explanations: RECOMMENDED_FROM_EVIDENCE.
- Secondary explanations use accessible progressive disclosure: RECOMMENDED_FROM_EVIDENCE.
- Mobile filter controls cannot bury the product list: RECOMMENDED_FROM_EVIDENCE.
- UI does not expose internal technical terminology: PARTIAL existing; OWNER_DECISION_REQUIRED for vocabulary freeze.
- Product Detail remains only if it has a distinct job: OWNER_DECISION_REQUIRED.
- Product Relations stay out of primary workflows unless their seller value is proven: OWNER_DECISION_REQUIRED.

## 33. Owner Decisions Required

- Whether Product Detail remains in Portfolio V1.
- Whether Product Relations belong in Portfolio V1 or are deferred.
- Whether ready reply stays inline on cards, moves to detail, or becomes a focused drawer/page.
- How much readiness explanation belongs on product cards.
- What must appear in the dashboard first viewport.
- Whether dashboard should prioritize action queue over summary metrics.
- How many filter rows are acceptable before product cards on mobile.
- Whether tag/type management remain separate pages or become mostly inline.
- Whether card tag toggles should stay or move to edit/taxonomy surfaces.
- Whether detail-only direct stock set is required on the product card too.
- Whether hidden and archived need separate seller-facing meanings.
- Whether type/tag recognition should auto-apply suggestions or remain preview-only.
- Which current features are deferred from the rebuild.

## 34. Inputs for Future Rebuild Documentation

- `PROJECT_BIBLE.md`: seller-first operational purpose, source-of-truth UX, buyer-answer boundary, deferred public catalog/chat/order/payment/delivery layers.
- `USER_JOURNEY_FREEZE_V1.md`: thirteen reconstructed seller journeys and required return paths.
- `APP_EXPERIENCE_PLAN.md`: page responsibility matrix, dashboard/workspace/detail/form hierarchy, card anatomy constraints.
- `DESIGN_SYSTEM_V1.md`: Georgian vocabulary, status badge hierarchy, destructive-action styling, compact mobile controls, accessible disclosure/menu requirements.
- `TEST_STRATEGY_V1.md`: route/context-preservation tests, HTMX partial refresh tests, stale-count regression tests, accessibility smoke tests, mobile viewport checks.
- `BUILD_PLAN.md`: micro-slices for shell, dashboard, workspace, product form, stock HTMX, ready reply, taxonomy management, and owner-approved deferred features.

## 35. Recommended Next Audit

Recommended next audit: Tests, Security, Operations, and Deployment Audit.

It should follow backend and frontend truth audits because the major product surfaces and state boundaries are now mapped. The next step should verify test coverage, authentication/security posture, environment assumptions, deployment readiness, CI gaps, and operational risks before any documentation freeze or rebuild plan is written.

## 36. Operation Log

- Source files modified: none
- Source files created: none
- Destination files created/updated: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/frontend.md`
- Commands executed:
  - `sed -n '1,220p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/DISCOVERY_REPORT.md`
  - `sed -n '1,260p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/backend.md`
  - `sed -n '260,930p' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/backend.md`
  - `test -f /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/frontend.md`
  - `find templates static -maxdepth ...` frontend file inventory commands
  - `wc -l` on inspected template/static files
  - `sed` reads for all inspected templates and partials listed in section 3
  - `sed` reads for `apps/catalog/urls.py`, `apps/inventory/urls.py`, `apps/dashboard/urls.py`, `config/urls.py`
  - `grep -n` for route, return-link, HTMX, Alpine, confirm, and clipboard evidence
  - `sed` reads for frontend-relevant view/form/test sections
  - `find` for repository image/screenshot candidates
  - `grep -R -n` for UX/navigation documentation claims; command returned nonzero because the optional `docs` path was absent, while root Markdown matches were still printed
  - `date '+%Y-%m-%d %H:%M:%S %Z'`
  - `ls -la /home/giga/Desktop/OSINT/GITHUB_MVP_ERP`
  - `git status --short` in source project; command reported source is not a Git repository
  - `wc -l /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/frontend.md`
  - `grep -n '^## ' /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/frontend.md`
  - `ls -la /home/giga/Desktop/OSINT/GITHUB_MVP_ERP/frontend.md`
  - `find /home/giga/Desktop/OSINT/facebook_MVP -maxdepth 1 -type f -newermt '2026-07-27 13:46:55 +0400'`
- Packages installed: none
- Migrations run: none
- Database changes: none
- Server started: no
- Browser/device testing performed: not performed
- Tests executed: not executed
- Commits: none
- Pushes: none
