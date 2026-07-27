# Social Commerce Operating Assistant — MVP Specification

**Document Type:** Current-State Technical and Product Specification  
**Project Context:** Inventory-first MVP (Stage 7N complete)  
**Target Audience:** Product Founders, Lead Developers, Future Chatbot Integration Team  
**Last Updated:** Following Stage 7N (Seller Value Loop + Readiness Explanation)

---

## 1. Project Overview

*   **Product Purpose:** A mobile-first inventory and catalog management cockpit for solo Facebook/Instagram sellers in Georgia.
*   **Current MVP Definition:** A fast, operational workspace that replaces Excel/Messenger notes, allowing sellers to easily manage products, track variant-level stock, organize catalog data, and receive proactive assistant signals.
*   **Target Seller/User:** Solo clothing sellers, small handmade/gift businesses operating mainly on social media without a dedicated ERP or eCommerce website.
*   **Core Principle:** "Inventory უნდა იყოს seller-ის ყოველდღიური სამუშაოს ნაწილი, არა ცალკე Excel-ის მსგავსი კუნძული" (Inventory must be part of the seller's daily workflow, not an isolated island like Excel).
*   **What the product is NOT:** It is NOT a public eCommerce storefront (like Shopify/WooCommerce), NOT an accounting ERP, NOT a generic POS, and does NOT yet include orders, payments, or an active chatbot.

## 2. Current Product Philosophy

*   **Inventory Manager vs. Inventory Management Assistant:** Instead of forcing sellers to manually search for empty stocks or missing data, the system proactively computes "Signals" and "Readiness" metrics to guide daily work.
*   **Catalog Truth Matters:** The system strictly controls inputs (like sizes, colors, product types, and business-scoped tags) so that future AI/Chatbot layers will have clean, predictable data. Free-text chaos is intentionally restricted.
*   **Seller-facing Simplicity:** Sellers operate from mobile phones. The UI relies on large tap targets, direct inline actions (e.g., +1/-1 stock), and visual badges rather than deep nested menus or complex grids.
*   **Value Loop:** Every required field explicitly demonstrates its value to the seller by stating exactly what the future assistant/chatbot will be able to answer based on that data (e.g. "მყიდველი შეიძლება გკითხოს და ჩვენ ვუპასუხებთ: ✓ ფასი").

## 3. Current User-Facing Pages

### Login
*   **URL:** `/accounts/login/` (or default Django auth paths)
*   **Purpose:** Secure access. Custom user model utilizes email instead of username.

### სამუშაო დაფა (Dashboard)
*   **URL:** `/` (maps to `dashboard:home`)
*   **Purpose:** Proactive daily assistant. Answers "დღეს რას მივხედო?" (What needs my attention today?).
*   **Main UI:**
    *   "კატალოგის მზადყოფნა" (Readiness summary: ready, partial, poor).
    *   "სწრაფი მოქმედებები" (Quick add/view actions).
    *   Assistant signal blocks: "ყურადღება სჭირდება", "ბოლო ცალი", "დაბალი ნაშთი", "ნაწილობრივ ამოწურული", "სრულად ამოწურულია".
*   **Data:** Computed signals without redundant database storage.

### პროდუქცია (Product Workspace)
*   **URL:** `/products/` (`catalog:list`)
*   **Purpose:** The central operational hub.
*   **Main UI:** Product cards, search bar, grouping tabs (აქტიური, დრაფტები, დაბალი ნაშთი, ამოწურული, არქივი), Types Palette, and Tag Palette.
*   **Actions:** `+1` / `-1` / `set` quantity inline, edit, clone, archive/restore, and tag attach/detach directly on the card. Dynamic readiness explanations with clickable next-action chips (e.g. "მიუთითე ფასი").
*   **Backend:** `catalog.views.product_list` decorated with dynamically computed signals and relations.

### პროდუქტის დამატება/რედაქტირება (Create/Edit Form)
*   **URL:** `/products/new/`, `/products/<id>/edit/`
*   **Purpose:** Manage core product facts and relations.
*   **Main UI:** Mobile-friendly stacked forms. Infinite variants via Alpine.js `<template>`. Radio buttons for Product Type. Dropdowns for exact sizes and colors.
*   **Actions:** Save, add variant row, remove variant row, add/remove `ProductRelation` (on edit only).

### ტიპების მართვა (Product Type Management)
*   **URL:** `/products/types/` (`catalog:type_list`)
*   **Purpose:** Maintain the controlled business product types vocabulary.
*   **Main UI:** Add new type form. List of active types with rename, hide (deactivate), and delete buttons.

### თეგების მართვა (Tag Management)
*   **URL:** `/products/tags/` (`catalog:tag_list`)
*   **Purpose:** Maintain the controlled business tag vocabulary.
*   **Main UI:** Add new tag form. List of active tags with rename, hide (deactivate), and delete buttons.

### პროდუქტის დეტალები (Product Detail)
*   **URL:** `/products/<id>/` (`catalog:detail`)
*   **Purpose:** Secondary inspection route. Deprioritized in the main workflow as the list page now handles operational tasks.

## 4. Current Navigation Model

*   **Main Nav Items:** The header exposes three simple links: `სამუშაო დაფა`, `პროდუქცია`, and `+ დამატება`.
*   **Workflow:** The seller is explicitly encouraged to work entirely from the Dashboard and Product List.
*   **Non-pages:** `/inventory/` is NOT a page; it routes POST requests for stock adjustments (`/inventory/variants/<id>/quantity/`).

## 5. Backend Architecture

*   **Structure:** Django Modular Monolith, Python 3, PostgreSQL.
*   **Apps & Responsibilities:**
    *   `accounts`: Custom `User` model focusing on email-based auth.
    *   `businesses`: `Business` model mapping owners to their shop template.
    *   `catalog`: Core product models (`Product`, `ProductVariant`, `ProductPhoto`), relation definitions, tags, dynamic product types, and all primary UI views/forms.
    *   `clothing`: Domain-specific brains (`ClothingProductProfile`, `ClothingVariantProfile`).
    *   `inventory`: `InventoryAdjustment` audit logs and pure stock-computation services.
    *   `dashboard`: Dashboard views gathering signals.
    *   `analytics`: `UsageEvent` model logging core seller habits.
    *   `validation`: `compute_product_readiness` service providing the value loop and missing data hints.
*   **Service Layer:** Business logic is kept out of models and views where possible (e.g., `compute_product_availability`, `_save_product_bundle`, `compute_product_readiness`).

## 6. Data Model Specification

### Business
*   **Purpose:** Isolates data per seller workspace.
*   **Fields:** `name`, `owner`, `template_type` (clothing/generic).

### Product
*   **Purpose:** The central catalog entity.
*   **Fields:** `name`, `base_price`, `lifecycle_status` (draft, active, hidden, archived).
*   **Relationships:** Owned by Business. Has many Variants, Photos, Tags, Relations.

### ProductVariant
*   **Purpose:** The single source of truth for stock quantities.
*   **Fields:** `quantity_on_hand`, `is_active`, `label` (computed as size/color fallback).

### ClothingProductProfile & ClothingVariantProfile
*   **Purpose:** Keeps the `Product` table clean. Holds domain-specific facts.
*   **Fields:** `target_audience` (on Product), `custom_type` (ForeignKey to `BusinessProductType`), `size`, `color` (on Variant). Note: `product_type` CharField is retained as legacy fallback but effectively superseded by `custom_type`.

### BusinessProductType
*   **Purpose:** Dynamic, business-scoped categorization preventing free-text chaos ("რა ტიპის პროდუქციაა?").
*   **Fields:** `business`, `name`, `normalized_name`, `is_active`.
*   **Constraints:** PostgreSQL `UniqueConstraint` on active types per business using the normalized string.

### BusinessTag & ProductTag
*   **Purpose:** Controlled organizational vocabulary.
*   **Fields:** `BusinessTag` has `name`, `normalized_name`, `is_active`.
*   **Constraints:** PostgreSQL `UniqueConstraint` on active tags per business using the normalized string.

### ProductRelation
*   **Purpose:** Safe, explicit connections for future upselling/chatbot answers.
*   **Fields:** `source_product`, `target_product`, `relation_type` (e.g., goes_with, similar_to), `status` (confirmed, hidden).

### InventoryAdjustment & UsageEvent
*   **Purpose:** Auditability and pilot metrics without 3rd party SDKs.
*   **Fields:** Capture who, what, when, delta, old/new values, and metadata JSON.

## 7. Product Lifecycle and Availability Logic

*   **Stored Statuses:** DB holds `draft`, `active`, `hidden`, `archived`. Default is `active` upon creation to prevent "lost product" confusion.
*   **Computed Display Statuses:** Derived dynamically via `compute_product_availability()`.
    *   `available`
    *   `low_stock`
    *   `sold_out`
    *   `partially_sold_out`
*   **Hidden/Archived Behavior:** Overrides stock logic. An archived product never shows as "Available" regardless of stock count.
*   **Sold Out Rules:** Triggered natively when all *active* variants reach `quantity_on_hand = 0`. No manual "Mark Sold Out" button is needed.

## 8. Inventory Quantity Logic

*   **Source of Truth:** Variant-level `quantity_on_hand`. Product total is computed.
*   **Operations:** `+1` (increment), `-1` (decrement), `set` (manual override) via HTMX POST.
*   **Safety:** Decrementing at 0 returns early without crashing. Database enforces positive integers.
*   **Logging:** Every valid change writes an `InventoryAdjustment` and a `UsageEvent`.
*   **Omitted features:** No "stock movement reasons" (e.g., damaged, returned) yet. No order reservation logic.

## 9. Product Creation/Editing Flow

*   **Required Fields:** Product Type (`custom_type`), Name, Base Price, Target Audience, Size, Color, Quantity.
*   **Controlled Inputs:** Type utilizes `RadioSelect`. Audience, Size, and Color utilize specific Django `ChoiceField` dropdowns.
*   **Unlimited Variants:** Managed frontend-side using Alpine.js injecting a hidden Django `empty_form`. Minimum 1 required.
*   **Validation:** Custom `clean()` methods ensure Georgian error messages (e.g., "მინიმუმ ერთი ზომა/ფერი (ვარიანტი) უნდა დაამატო.").
*   **Transaction Safety:** `_save_product_bundle` wraps Product, Profiles, Photos, Variants, and Tags in a single atomic DB block.

## 10. Variant System

*   **Creation:** Handled natively in the Product form via Django Formsets (`extra=1` for new, `extra=0` for edit).
*   **Choices:** Hardcoded lists of standard sizes (XS-3XL, baby months, years) and colors.
*   **Limitations:** No advanced matrix generator (e.g., "Create all Sizes X Colors"). Handled manually by the seller row-by-row.

## 11. Product Types & Tags System

*   **Model Structure:** `BusinessProductType` and `BusinessTag` dictionary tables.
*   **Starter Data:** "კაბა", "შარვალი", etc. for Types. "ახალი", "საზაფხულო", "ბოლო ცალი" for Tags. Automatically seeded via a safe `try...except ProgrammingError` block on active business retrieval.
*   **"თეგის გარეშე" Logic:** Auto-assigns the "თეგის გარეშე" tag if a product is saved without tags, ensuring no product goes completely uncategorized.
*   **Palette:** Horizontal scroll on `product_list.html` applying `?type=<id>` and `?tag=<id>` filters.
*   **Attach/Detach:** Alpine.js dropdown directly on the product card posts to `tag_toggle`.
*   **Management Pages:** Standalone `/types/` and `/tags/` routes. Allows create, rename, deactivate, and conditional delete (if unused).
*   **Duplicate Prevention:** Handled flawlessly via `re.sub` lowering and collapsing whitespace into `normalized_name`.

## 12. Search System

*   **Location:** Top of the product list.
*   **Fields Searched:** Product Name, Variant Size, Variant Color, Target Audience, Types, and Tag Names using PostgreSQL `Q()` objects with `icontains`.
*   **Suggestions:** HTMX datalist endpoint (`/search-suggestions/`) returns distinct, deduplicated terms based on seller typing.
*   **Limitations:** No typo tolerance. Exact or partial match only. No complex faceted search UI.

## 13. Dashboard / Assistant Signals

*   **Purpose:** Proactively guide the seller.
*   **Signals Computed:**
    *   `Needs Attention`: Checks for missing core data, old updates (>30 days), missing tags, missing photos.
    *   `Low Stock`: Variant falls to exactly 1.
    *   `Last Piece`: Total quantity exactly 1.
    *   `Sold Out`: Total quantity is 0.
    *   `Partially Sold Out`: Mixed 0 and >0 quantities across variants.
    *   `Stale Sold Out`: Sold out and unchanged for > 14 days.
*   **Implementation:** `dashboard.services.py` combined with boolean properties injected by `catalog.views._decorate_product`.

## 14. Product Readiness & Seller Value Loop

*   **Levels:**
    *   `good` -> "მზადაა"
    *   `partial` -> "ნაწილობრივ მზადაა"
    *   `poor` -> "შესავსებია"
*   **Location:** Computed strictly via `validation.services.compute_product_readiness`. Not stored in DB. Abandoned arbitrary numerical scoring.
*   **UI Value Loop:** The product card uses an Alpine.js expander to show exactly what questions the system can answer (e.g. "✓ ფასი", "✓ ნაშთი").
*   **Missing Items & Actions:** Clearly highlights what is missing ("○ ფოტო აკლია") alongside clickable action chips ("დაამატე ფოტო") routing to the edit form.

## 15. Product Relations

*   **Model:** `ProductRelation` with typed directionality (`goes_with`, `similar_to`, `alternative_to`, `part_of_set`, `upsell_with`).
*   **UI Management:** Native form added to the `product_edit` page allowing selection of other active products in the same business.
*   **Assistant-Safe Helper:** `get_confirmed_related_products` exists to guarantee that future message layers only pull active, confirmed, and in-stock related products.
*   **Limitations:** No automatic AI or tag-based relational inferences are built. 100% manual.

## 16. Analytics / Usage Tracking

*   **Model:** `UsageEvent` storing timestamp, user, business, event type, and generic JSON metadata.
*   **Tracked Actions:** `dashboard_opened`, `product_created`, `product_updated`, `product_cloned`, `variant_quantity_changed`.
*   **Limitations:** No custom chart views exist in the UI yet; data must be read via Django Admin or SQL queries.

## 17. Admin / Debug Tools

*   **Registered Models:** `Product`, `ProductVariant`, `ProductPhoto`, `BusinessTag`, `BusinessProductType`, `ProductTag`, `ProductRelation`, `UsageEvent`.
*   **Usage:** Crucial for developers and product founders to monitor pilot health, debug `UsageEvent` sequences, and evaluate database hygiene without raw SQL. Not accessible to standard sellers.

## 18. Frontend Architecture

*   **Frameworks:** Django Templates (Server-Side Rendering), HTMX (Partial dom swapping), Alpine.js (Lightweight client-side interactions like modals/toggles/unlimited forms), Tailwind CSS (Utility classes).
*   **Approach:** Strictly mobile-first. Relies on `flex`, `gap`, `rounded-xl`, and `p-4` spacing.
*   **Known UI Fragility:** Very little. Alpine and HTMX states are isolated per-product card. No heavy JS framework conflicts exist.

## 19. Security, Integrity, and Ownership Scoping

*   **Scoping:** The application mandates `business = _get_active_business(request.user)` inside every view.
*   **Query Filtering:** All `get_object_or_404` and `Product.objects.filter` calls append `business=business`.
*   **Relations/Tags/Types:** `ProductRelation` clean methods block relating products across different businesses. Constraints ensure tags/types cannot leak globally.
*   **Migration Resilience:** All dynamic late-stage evaluations referencing newly added models (Relations, Tags, Types) are strictly wrapped in `try...except ProgrammingError` forcing list evaluations at the view level. The app will never crash prior to `migrate`.

## 20. Current Routes / URLs

*   **App: Catalog (`/products/`)**
    *   `/products/` (`list`): Main operational workspace. Seller-facing.
    *   `/products/new/` (`create`): Full product form.
    *   `/products/search-suggestions/` (`search_suggestions`): HTMX internal datalist JSON/HTML.
    *   `/products/tags/` (`tag_list`): Standalone tag management.
    *   `/products/types/` (`type_list`): Standalone product type management.
    *   `/products/tags/create/`, `rename/`, `deactivate/`, `delete/`: POST-only endpoints.
    *   `/products/types/create/`, `rename/`, `deactivate/`, `delete/`: POST-only endpoints.
    *   `/products/<id>/clone/` (`clone`): POST-only fast duplicate.
    *   `/products/<id>/archive/`, `restore/`: POST-only soft-delete triggers.
    *   `/products/<id>/tag/` (`tag_toggle`): HTMX POST attach/detach.
    *   `/products/<id>/relation/add/`, `remove/`: POST-only relation mapping.
    *   `/products/<id>/` (`detail`): Legacy view, mostly superseded by the list.
    *   `/products/<id>/edit/` (`edit`): Full product modification + Relations manager.
*   **App: Inventory**
    *   `/inventory/variants/<id>/quantity/`: HTMX POST for +/-1 updates.

## 21. Current Limitations

*   **UX / Scaling:** Without formal pagination, rendering 500+ products on a single `tab` will cause vertical scrolling fatigue.
*   **Search Flexibility:** Strict string matching. "kaba" will not find "კაბა".
*   **Operations:** No concept of draft reservations, carts, or checkout links.
*   **Finance/Movement:** No cost-basis tracking, return tracking, or stock damage reporting.

## 22. Deferred Features

*   **Near-future:** Pagination for product lists. Guided Attention Flow (Task Queue). Visual analytics dashboard.
*   **Post-pilot:** Stock movement reason codes. AI-assisted form filling from uploaded images.
*   **Messaging/Chatbot:** DRF API endpoints exposing the `compute_product_readiness` and related product graphs to a Meta webhook.

## 23. Overengineering Risk Assessment

**Risk Level: LOW**
*   **Why:** The application has successfully matured into an operational assistant while completely resisting the urge to become a generic eCommerce admin or an overly complex ERP. The codebase remains a standard Django monolith leveraging standard server-rendered HTML. Complexity has been added strictly to improve data hygiene (Tags, Types, Readiness, Relations) rather than pursuing unnecessary technological abstractions.

## 24. Pilot Readiness Assessment

**Ready for Pilot Testing:** **YES**
*   **What works natively:** A solo seller can easily register, add unlimited variants seamlessly, classify them strictly by Product Type and Tags, immediately see exactly what information is missing via the Value Loop readiness explanation, and update stock balances dynamically via HTMX. The UI actively rewards the seller for accurate data entry.
*   **Suggested Pilot Scenario:** Onboard 3-5 clothing sellers. Ask them to add their latest collection. Do not give them a tutorial. Measure if they return to the dashboard to update stock manually based on the Assistant Signals over the next 14 days without prompts.

## 25. Final Current-State Summary

The application is a **proactive inventory management assistant**. It completely replaces the chaos of Excel spreadsheets and Messenger notes by creating a strict but fast mobile-friendly workspace. The recent implementation of Product Types, Controlled Tags, and explicitly worded Readiness Statuses establishes the exact data foundation required for future Chatbot/AI integrations, while simultaneously providing immediate organizational value to the human seller today. The system is structurally sound, safe against unapplied migrations, and fully primed for Pilot Testing.
