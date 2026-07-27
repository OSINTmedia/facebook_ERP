# Navigation Audit — Full Button / Link / Page Flow Map

Project: `facebook_MVP`  
Working directory: `/home/giga/Desktop/OSINT/facebook_MVP`  
Audit type: seller-side navigation / action / return-path audit  
Scope: audit only, no product behavior changes

---

## Executive Assessment

Core MVP flows are present and usable:
- seller can add product truth
- seller can edit and correct product truth
- seller can manage tags/types
- seller can update stock quickly
- seller can generate ready buyer replies

The app does **not** currently have a hard blocker in the main seller workflow.

The main remaining product risk is not missing functionality. It is **navigation trust**:
- sellers often need browser Back
- origin context is not preserved well
- some pages do not provide a clear “return to where I came from” path
- some nearby actions compete semantically, especially on product cards

My assessment:
- **P0 blockers:** none found
- **Main P1 issue:** contextual return paths
- **Main P2 issue:** label clarity and action hierarchy
- **Main P3 issue:** density polish

Recommended next stabilization direction:
- **Patch 9F — Contextual Return Paths / Navigation Trust**

---

## A. Architectural Route Map

### Full seller-facing pages

#### `/accounts/login/`
- View: `django.contrib.auth.views.LoginView`
- Template: `templates/registration/login.html`
- Purpose: seller login
- Response type: full page

#### `/`
- View: `apps.dashboard.views.home`
- Template: `templates/dashboard/home.html`
- Purpose: seller dashboard, summary, attention, drilldowns
- Response type: full page

#### `/products/`
- View: `apps.catalog.views.product_list`
- Template: `templates/catalog/product_list.html`
- Purpose: main operational surface for:
  - search
  - filters
  - stock updates
  - ready buyer reply
  - duplicate/copy
  - archive/restore
- Response type: full page

#### `/products/new/`
- View: `apps.catalog.views.product_create`
- Template: `templates/catalog/product_form.html`
- Purpose: add new product truth
- Response type: full page

#### `/products/<pk>/`
- View: `apps.catalog.views.product_detail`
- Template: `templates/catalog/product_detail.html`
- Purpose: single-product detail, stock, ready buyer reply
- Response type: full page

#### `/products/<pk>/edit/`
- View: `apps.catalog.views.product_edit`
- Template: `templates/catalog/product_form.html`
- Purpose: correct product truth, tags, types, choices, relations
- Response type: full page

#### `/products/tags/`
- View: `apps.catalog.views.business_tag_list`
- Template: `templates/catalog/tag_list.html`
- Purpose: tag create/rename/hide/show/delete management
- Response type: full page

#### `/products/types/`
- View: `apps.catalog.views.business_type_list`
- Template: `templates/catalog/type_list.html`
- Purpose: type create/rename/hide/show/delete management
- Response type: full page

### POST + redirect routes

#### `/products/<pk>/clone/`
- View: `apps.catalog.views.product_clone`
- Purpose: duplicate product, then redirect to copied product edit page
- Response type: POST + redirect

#### `/products/<pk>/archive/`
- View: `apps.catalog.views.product_archive`
- Purpose: safe hide/archive path for products
- Response type: POST + redirect to list

#### `/products/<pk>/restore/`
- View: `apps.catalog.views.product_restore`
- Purpose: restore archived product
- Response type: POST + redirect to list

#### `/products/<pk>/tag/`
- View: `apps.catalog.views.product_tag_toggle`
- Purpose: quick add/remove tag from product list card
- Response type: POST + redirect back

#### `/products/<pk>/relation/add/`
- View: `apps.catalog.views.product_relation_add`
- Purpose: add related product from edit page
- Response type: POST + redirect

#### `/products/<pk>/relation/remove/`
- View: `apps.catalog.views.product_relation_remove`
- Purpose: remove related product from edit page
- Response type: POST + redirect

#### `/products/tags/create|rename|deactivate|reactivate|delete/`
- Views: `apps.catalog.views.business_tag_*`
- Purpose: tag management write actions
- Response type: POST + redirect

#### `/products/types/create|rename|deactivate|reactivate|delete/`
- Views: `apps.catalog.views.business_type_*`
- Purpose: type management write actions
- Response type: POST + redirect

### HTMX / partial routes

#### `/products/search-suggestions/`
- View: `apps.catalog.views.search_suggestions`
- Template: `templates/catalog/partials/search_suggestions.html`
- Purpose: search suggestions under the list search field
- Response type: HTMX partial

#### `/products/tags/inline-create/`
- View: `apps.catalog.views.product_form_tag_inline_create`
- Template: `templates/catalog/partials/product_tag_section.html`
- Purpose: add tag inline from product form
- Response type: HTMX partial

#### `/products/types/inline-create/`
- View: `apps.catalog.views.product_form_type_inline_create`
- Template: `templates/catalog/partials/product_type_section.html`
- Purpose: add type inline from product form
- Response type: HTMX partial

#### `/inventory/variants/<pk>/quantity/`
- View: `apps.inventory.views.variant_quantity_update`
- Templates:
  - `templates/catalog/partials/product_card.html` when `response_scope=product_card`
  - `templates/dashboard/partials/quantity_controls.html` as row-level fallback
- Purpose: quantity increment/decrement/set
- Response type: HTMX partial or POST redirect fallback

### Reusable partials with user-visible behavior

- `templates/catalog/partials/product_card.html`
- `templates/dashboard/partials/quantity_controls.html`
- `templates/catalog/partials/product_type_section.html`
- `templates/catalog/partials/product_tag_section.html`
- `templates/catalog/partials/search_suggestions.html`

---

## B. Button / Action Table by Page

## Base shell — `templates/base.html`

### `სამუშაო დაფა`
- Target: `/`
- Method: GET
- Result: navigate to dashboard
- Failure: low risk
- Way back afterward: yes, base nav persists

### `პროდუქცია`
- Target: `/products/`
- Method: GET
- Result: navigate to product list
- Failure: low risk
- Way back afterward: yes, base nav persists

### `+ დამატება`
- Target: `/products/new/`
- Method: GET
- Result: open create form
- Failure: low risk

### `გასვლა`
- Target: `/accounts/logout/`
- Method: POST
- Result: logout
- Confirmation: none

---

## Dashboard — `/`

### Inventory state cards
Labels:
- `ხელმისაწვდომია`
- `დაბალი ნაშთი აქვს`
- `ამოწურულია`
- `დრაფტია`

- Target: `/products/?tab=...`
- Method: GET
- Result: filtered product list
- Failure: low risk
- Way back: weak; usually base nav only

### Readiness rows
Labels:
- `პასუხისთვის მზადაა`
- `მცირე ინფორმაცია აკლია`
- `მნიშვნელოვანი ინფორმაცია აკლია`

- Target: `/products/?readiness=...`
- Method: GET
- Result: filtered list
- Way back: base nav only

### Quick actions
Labels:
- `ყველა პროდუქცია`
- `დაბალი ნაშთის ნახვა`
- `ამოწურულის ნახვა`
- `ინფორმაცია აკლია`

- Method: GET
- Result: filtered list

### Attention-needed actions
Labels vary:
- `ფასის შევსება`
- `ფოტოს დამატება`
- `არჩევანის დამატება`
- `ინფორმაციის შევსება`
- `თეგის დამატება`
- `რედაქტირება`

- Target: usually `/products/<pk>/edit/`
- Method: GET
- Result: product edit page
- Failure: low risk
- Return path: weak; base nav or browser Back

### Dashboard stock controls
- Target: `/inventory/variants/<pk>/quantity/`
- Method: HTMX POST
- Result: row-level quantity control refresh
- Failure: possible if inventory update fails
- Failure visibility: limited
- Return path: not relevant

Assessment:
- dashboard drilldowns are useful
- dashboard is not the main navigation problem
- edit-return path from dashboard is weak

---

## Product list — `/products/`

This is the real operational center of the MVP.

### Top-level actions

#### `დამატება`
- Target: `/products/new/`
- Method: GET
- Result: create form

#### Tab chips
- Target: `/products/?tab=...`
- Method: GET
- Result: filtered list

#### Type chips
- Target: `/products/?type=<id>`
- Method: GET
- Result: filtered list

#### Tag chips
- Target: `/products/?tag=<id>`
- Method: GET
- Result: filtered list

#### `+ ტიპების მართვა`
- Target: `/products/types/`
- Method: GET
- Result: type management page

#### `+ თეგების მართვა`
- Target: `/products/tags/`
- Method: GET
- Result: tag management page

### Search controls

#### Search field
- Query param: `q`
- Method: GET
- Result: filtered same page
- Failure: low risk

#### Search suggestions
- Target: `/products/search-suggestions/`
- Method: HTMX GET
- Result: suggestion partial

#### `ძებნის გასუფთავება`
- Target: `/products/`
- Method: GET
- Result: reset list

### Product card actions

#### Product title
- Target: `/products/<pk>/`
- Method: GET
- Result: product detail page
- Return path afterward: weak; no explicit return link on detail page

#### `მზა პასუხი`
- Method: local Alpine toggle
- Result: expand/collapse in-card ready-reply block
- Failure: possible only if JS fails
- Failure visibility: no clear fallback

#### `დეტალურად`
- Target: `/products/<pk>/`
- Method: GET
- Result: navigate to detail page

#### Ready reply chips
Labels:
- `ფასი`
- `ზომა-ფერი`
- `მარაგი`
- `აღწერა`
- `სრული პასუხი`

- Method: local Alpine only
- Result: switch preview mode

#### `კოპირება` inside ready reply
- Method: local JS
- Result: clipboard copy
- Failure: browser clipboard limitations possible
- Failure visibility: weak

#### `შევსება` / `რედაქტირება` inside ready reply
- Target: `/products/<pk>/edit/`
- Method: GET
- Result: edit form
- Return path afterward: weak; success always returns to generic list

#### `რატომ?`
- Method: local Alpine toggle
- Result: readiness explainer expand/collapse

#### `+ თეგი`
- Method: local Alpine toggle
- Result: open quick tag section on card

#### Tag pill toggle
- Target: `/products/<pk>/tag/`
- Method: POST
- Result: add/remove tag, redirect back
- Failure: possible
- Failure visibility: moderate, depends on message

#### Stock controls `-1` / `+1` / direct quantity update
- Target: `/inventory/variants/<pk>/quantity/`
- Method: HTMX POST
- Result: full product-card refresh
- Confirmation: none
- Failure: possible
- Failure visibility: moderate
- Feedback: local card refresh + flash + sold-out/restock event

#### `რედაქტირება`
- Target: `/products/<pk>/edit/`
- Method: GET
- Result: edit form

#### `დააკოპირე`
- Method: local Alpine menu
- Sub-actions:
  - `ზუსტი ასლი`
  - `სხვა ფერით`
  - `სხვა ზომით`
  - `ახალი ფოტოთი`
- Target: `/products/<pk>/clone/`
- Method: POST
- Result: redirect to copied product edit page
- Failure: possible
- Return path afterward: weak

#### `დაარქივება`
- Target: `/products/<pk>/archive/`
- Method: POST
- Confirmation: yes
- Result: archive product and redirect/update list

#### `დაბრუნება`
- Target: `/products/<pk>/restore/`
- Method: POST
- Result: restore product

Assessment:
- This card is the most overloaded interactive surface in the app.
- It still works, but action hierarchy is not obvious enough for a confused seller.
- Biggest risk is not missing buttons; it is **too many competing buttons**.

---

## Product detail — `/products/<pk>/`

### Ready reply block
- Chips: local Alpine
- `კოპირება`: local JS
- `შევსება` / `რედაქტირება`: GET `/products/<pk>/edit/`

### Stock controls
- `-1` / `+1` / `შეცვლა`
- Target: `/inventory/variants/<pk>/quantity/`
- Method: POST / redirect fallback
- Result: stock update

### Product actions
- `რედაქტირება` -> GET `/products/<pk>/edit/`
- `დააკოპირე` -> POST `/products/<pk>/clone/`

Gap:
- explicit `უკან პროდუქტებზე` link is missing

Assessment:
- detail page is useful
- but it is not yet a trustworthy waypoint because return path is weak

---

## Product create/edit — `/products/new/`, `/products/<pk>/edit/`

### Save actions
- `შენახვა` / `განახლება`
- Method: POST same page
- Validation failure: stays on form with inline errors
- Success: redirects to `/products/`

### `უკან`
- Target: `/products/`
- Method: GET
- Problem: ignores origin context

### Inline taxonomy actions
- Type inline add -> HTMX POST `/products/types/inline-create/`
- Tag inline add -> HTMX POST `/products/tags/inline-create/`

### Choice editing
- `ახალი არჩევანის წაშლა` -> local Alpine only for unsaved rows
- `ამ არჩევანის წაშლა` -> checkbox + save for existing rows

### Related products
- `დაკავშირება` -> POST `/products/<pk>/relation/add/`
- `წაშლა` -> POST `/products/<pk>/relation/remove/`

Assessment:
- this form is feature-rich and already near the practical density limit
- do not add more direct UI here unless it removes another surface

---

## Tag management — `/products/tags/`

### Actions
- `დამატება` -> POST `/products/tags/create/`
- `შეცვლა` -> POST `/products/tags/<pk>/rename/`
- `დამალვა` -> POST `/products/tags/<pk>/deactivate/`
- `გამოჩენა` -> POST `/products/tags/<pk>/reactivate/`
- `წაშლა` -> POST `/products/tags/<pk>/delete/`, only when unused
- `პროდუქტების ნახვა` -> GET `/products/?tag=<id>` when delete is blocked
- `უკან დაბრუნება` -> GET `/products/`

Assessment:
- blocked-delete behavior is correct
- recovery link is useful
- biggest gap is return path back from filtered products to this management page

---

## Type management — `/products/types/`

### Actions
- `დამატება` -> POST `/products/types/create/`
- `შეცვლა` -> POST `/products/types/<pk>/rename/`
- `დამალვა` -> POST `/products/types/<pk>/deactivate/`
- `გამოჩენა` -> POST `/products/types/<pk>/reactivate/`
- `წაშლა` -> POST `/products/types/<pk>/delete/`, only when unused
- `პროდუქტების ნახვა` -> GET `/products/?type=<id>` when delete is blocked
- `უკან დაბრუნება` -> GET `/products/`

Assessment:
- same pattern as tags
- same return-path weakness

---

## Login — `/accounts/login/`

### Action
- `შესვლა`
- Method: POST
- Validation failure: inline errors
- Success: Django redirect

Assessment:
- not part of current navigation risk cluster

---

## C. Main User-Flow Maps

## A. Add new product
1. Seller starts from dashboard or product list.
2. Clicks `+ დამატება`.
3. Lands on `/products/new/`.
4. Fills product truth.
5. If validation fails:
   - stays on form
   - inline field and non-form errors appear
6. If save succeeds:
   - redirects to `/products/`
7. Seller checks `მზა პასუხი` from the list card or opens detail page.

Assessment:
- flow works
- post-save landing is functional
- missing enhancement: direct path to the created product or auto-opened ready reply

## B. Edit product truth
1. Seller starts from product list card.
2. Clicks `რედაქტირება` or `შევსება`.
3. Lands on edit form.
4. Updates fields/tags/types/choices.
5. Saves.
6. Redirects to `/products/`.
7. Ready reply is visible again from product list.

Assessment:
- flow is operational
- but origin context is lost if seller came from:
  - product detail
  - filtered list
  - tag/type recovery path
  - dashboard attention item

## C. Remove wrong tag from product
1. Seller finds the product on `/products/`.
2. Opens `რედაქტირება`.
3. Unchecks the tag.
4. Saves.
5. Redirects to `/products/`.
6. Tag is no longer attached.
7. Tag deletion may become available on tag page.

Assessment:
- task is possible
- but there is no guided return to tag management if seller came from blocked delete flow

## D. Delete/hide tag or type
1. Seller opens `/products/tags/` or `/products/types/`.
2. If item is unused:
   - hard delete is available with confirm
3. If item is used:
   - delete is blocked
   - `პროდუქტების ნახვა` opens filtered `/products/`
4. Seller edits connected products.
5. Seller must manually return to tag/type management.

Assessment:
- protection is correct
- recovery exists
- return path is weak

## E. Delete/deactivate product choice
1. Seller opens product edit page.
2. Ticks `ამ არჩევანის წაშლა`.
3. Saves.
4. If the choice is not the last active one:
   - choice is deactivated safely
5. If it is the last active choice:
   - deletion is blocked
   - non-form error appears

Assessment:
- behavior is safe
- message exists
- missing enhancement: direct CTA to add a replacement choice after blocked delete

## F. Update stock
1. Seller uses `-1` / `+1` or quantity set on product card.
2. HTMX refreshes the affected card.
3. Quantity, total stock, availability, and ready-reply payload update.
4. `0 -> sold out` and `>0 -> restock` states are shown locally.

Assessment:
- card-level truth is now good
- page-level state still does not fully live-refresh:
  - tabs
  - header counts
  - dashboard metrics

## G. Prepare buyer reply
1. Seller opens `მზა პასუხი` on product card.
2. Picks answer mode.
3. Copies answer.
4. If the answer is weak:
   - short missing-data note appears
   - `შევსება` opens edit page
5. Seller fixes data and saves.
6. Returns to list.

Assessment:
- this is now one of the strongest MVP flows
- missing enhancement: preserve expanded reply state after returning from edit

## H. Duplicate product
1. Seller clicks `დააკოპირე`.
2. Picks copy mode.
3. POST clone runs.
4. Seller is redirected to copied product edit page.
5. Rename nudge appears.

Assessment:
- operationally sound
- missing enhancement: explicit “done / back to products” return guidance after rename

## I. Search / filter product
1. Seller types query or taps tag/type/tab chips.
2. Results stay on `/products/`.
3. Search feedback appears near the search area.
4. Reset path exists.

Assessment:
- flow works
- context is lost if seller opens management pages from filtered results

---

## D. Missing Return / Back Paths

### 1. Product detail page
- Current issue: no explicit `უკან პროდუქტებზე`
- Current fallback: browser Back or base nav
- Recommendation:
  - add compact return link
  - preserve optional `next` param
- Severity: **P1**

### 2. Product edit page
- Current issue: `უკან` always goes to `/products/`
- Affected origins:
  - detail page
  - filtered list
  - tag/type recovery flow
  - ready-reply `შევსება`
  - dashboard attention item
- Recommendation:
  - support `?next=...`
  - preserve it across GET and POST success redirect
- Severity: **P1**

### 3. Tag/type management -> connected products -> back
- Current issue:
  - recovery links get seller to the right products
  - but there is no in-app way back to management page afterward
- Recommendation:
  - recovery links should carry `next=/products/tags/` or `next=/products/types/`
  - filtered list should show contextual back link
- Severity: **P1**

### 4. Duplicate product lands on edit
- Current issue: return path after rename is generic
- Recommendation:
  - preserve list origin
  - or show `პროდუქტებზე დაბრუნება`
- Severity: **P2**

### 5. Dashboard attention -> edit -> back
- Current issue: no return-to-dashboard CTA
- Recommendation:
  - optional `next` param from dashboard edit links
- Severity: **P2**

### 6. Validation error loops on create/edit
- Current issue: technically safe but no contextual action summary
- Recommendation:
  - low priority, leave for later
- Severity: **P3**

---

## E. Confusing Labels

## Critical / near-term

### `ნახვა`
- Where: dashboard/list-like surfaces
- Why confusing:
  - unclear whether this opens a list, detail page, or management view
- Suggested alternative:
  - `პროდუქტების ნახვა`
  - `სიის ნახვა`
- Priority: **P2**

### `შევსება`
- Where:
  - ready reply block
  - dashboard attention actions
- Why confusing:
  - does not say what is missing or what will be filled
- Suggested alternative:
  - contextual wording where possible:
    - `ფასის შევსება`
    - `ინფორმაციის შევსება`
    - `არჩევანის შევსება`
- Priority: **P1/P2**

### `მზა პასუხი`
- Where: product list card trigger
- Why confusing:
  - may sound like a final sent answer, not an expandable tool
- Assessment:
  - acceptable now because the in-card block makes meaning visible
- Possible later alternative:
  - `პასუხის მომზადება`
- Priority: **P2**

### `დეტალურად`
- Where: product card
- Why confusing:
  - competes directly with `მზა პასუხი`
  - seller may not know which is the primary next step
- Suggested alternative:
  - `პროდუქტის გვერდი`
  - or keep label but visually subordinate it
- Priority: **P1**

### `აქტიური პროდუქტი`
- Where: product form lifecycle dropdown
- Why confusing:
  - conflicts with seller-facing availability vocabulary that prefers `ხელმისაწვდომი`
- Suggested alternative:
  - this should eventually align with seller-facing terminology
- Priority: **P2**

## Lower priority / polish

### `დამალვა`
- Where: tag/type management
- Assessment:
  - acceptable there because context is management, not product lifecycle
- Priority: **P3**

### `პასუხი ნაწილობრივ მზადაა`
- Where: ready reply block
- Why confusing:
  - understandable but abstract
- Suggested alternative:
  - maybe pair it with shorter guidance later
- Priority: **P3**

### `ყურადღება სჭირდება`
- Where: dashboard
- Assessment:
  - acceptable for now
- Priority: **P3**

---

## F. Overloaded UI Areas

## 1. Product list card
- Competing elements:
  - title/detail
  - ready-reply toggle
  - status badges
  - readiness explainer
  - tags
  - stock controls
  - copy menu
  - archive/restore
  - expanded reply block
- What may move/collapse later:
  - readiness explainer can become less prominent
  - quick tag editor can become secondary
- What should not change now:
  - stock controls
  - ready-reply quick access

Assessment:
- this is the most overloaded surface in the product
- but it is also the highest-value surface
- do not redesign broadly; improve hierarchy instead

## 2. Product edit form
- Competing elements:
  - base fields
  - token preview
  - recognition
  - photo
  - type
  - tags
  - choices
  - inline type/tag create
  - relations
- What may move later:
  - relations can become collapsible
  - guidance text can be tightened
- What should not change now:
  - choice editing
  - inline type/tag escape hatch

Assessment:
- already close to the practical complexity limit
- further additions should replace something else, not stack on top

## 3. Dashboard top area
- Competing elements:
  - summary
  - inventory state
  - readiness
  - quick actions
  - attention
  - low stock
  - sold out
- What may move later:
  - lower sections could consolidate or use progressive disclosure
- What should not change now:
  - drilldown links

## 4. Mobile list page
- Competing elements:
  - tabs
  - type chips
  - tag chips
  - search
  - product cards
- What may move later:
  - one of the chip bars could be collapsible
- What should not change now:
  - search
  - stock controls

Assessment:
- mobile still works, but this is where discoverability and density most directly collide

---

## G. Risk Ranking

## P0 — blocks user from completing task
- None found in the current stabilized MVP.

## P1 — causes user to rely on browser Back / get lost
- Missing contextual return path from detail/edit/management flows
- Filtered-list context is not preserved across correction flows
- Product card has two nearby entry points (`მზა პასუხი`, `დეტალურად`) without a clear primary hierarchy

## P2 — causes confusion but task remains possible
- Ambiguous `ნახვა` labels
- Generic `შევსება`
- Product form lifecycle wording still leaks `აქტიური პროდუქტი`
- Dashboard -> edit -> return path is weak

## P3 — polish / density / terminology
- readiness wording polish
- card density polish
- dashboard label polish

---

## H. Recommendations

## Primary recommendation

### Patch 9F — Contextual Return Paths / Navigation Trust

This should be the next patch.

Why:
- It directly addresses the strongest remaining trust problem.
- It does not require redesign.
- It does not add new product concepts.
- It reduces browser Back dependence.

### Recommended scope
1. Add optional `next` param support to:
   - product detail
   - product edit
   - clone redirect
   - ready-reply fill/edit shortcut
   - dashboard attention edit links
   - tag/type recovery links
2. Add compact contextual links:
   - `უკან პროდუქტებზე`
   - `თეგებზე დაბრუნება`
   - `ტიპებზე დაბრუნება`
   - `დაფაზე დაბრუნება`
3. Preserve filtered search/tag/type context through:
   - list -> detail -> edit -> list
   - tag/type management -> filtered products -> edit -> tag/type management
4. Tighten only the labels that hurt navigation clarity:
   - dashboard `ნახვა`
   - card `დეტალურად` vs `მზა პასუხი`
   - generic `შევსება` where context is too weak

## Secondary recommendation

After `9F`, if needed:
- do **hierarchy tightening**, not redesign
- especially on product cards
- avoid adding new buttons
- prefer:
  - better return links
  - clearer label hierarchy
  - preserved context

## Recommendation explicitly rejected for now

Do **not** solve navigation with:
- onboarding tutorial
- video walkthrough
- documentation page
- big breadcrumbs everywhere
- new dashboard widgets
- moving more flows into modals

Reason:
- this seller profile will not reliably consume instructions
- the product itself must carry the navigation logic

---

## Recommended Next Patch Prompt

### Patch 9F — Contextual Return Paths / Navigation Trust

Goal:
Remove reliance on browser Back by preserving origin context through detail, edit, management-recovery, and duplicate flows.

Constraints:
- No redesign
- No new features
- No AI/API
- No migrations
- Navigation/context only

Required changes:
1. Add optional `next` support to:
   - product detail
   - product edit
   - product clone redirect
   - ready-reply fill/edit shortcut
   - dashboard attention edit links
   - tag/type recovery links
2. Add compact contextual return links:
   - `უკან პროდუქტებზე`
   - `თეგებზე დაბრუნება`
   - `ტიპებზე დაბრუნება`
   - `დაფაზე დაბრუნება`
3. Preserve filtered query context when navigating:
   - list -> detail -> edit -> list
   - tag/type management -> products filter -> edit -> tag/type management
4. Tighten only the labels that block navigation understanding.

Success criteria:
- seller can move across detail/edit/recovery flows without browser Back
- filtered list context is preserved
- management recovery flows have a clear return path
- no redesign, no new major actions

