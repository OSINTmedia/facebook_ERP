# Inventory / Catalog Cockpit MVP Context

**Project:** Social Commerce Operating Assistant — Inventory-first MVP  
**Document purpose:** This document gives Codex / a developer full project context without needing the prior conversation history.  
**Language context:** Product reasoning and UI language are Georgian-first, but code, database names, enums, and technical identifiers should be English.  
**Current decision:** Build a mobile-first private seller dashboard for managing product catalog and inventory. No public buyer catalog, no orders, no payments, no chatbot in MVP.

---

## 1. Product Vision

The long-term product vision is a **Social Commerce Operating Assistant** for small Facebook/Instagram sellers in Georgia.

Target sellers:

- solo clothing sellers;
- small Facebook/Instagram shops;
- handmade sellers;
- gifts/souvenirs sellers;
- small family businesses;
- sellers without a website, IT team, Shopify/WooCommerce, or structured internal system.

These sellers currently manage sales through Messenger/Instagram DMs manually. Buyers ask questions such as:

- “ფასი?” / “Price?”
- “გაქვთ?” / “Is it available?”
- “ზომები?” / “Which sizes?”
- “სხვა ფერი?” / “Other color?”
- “ბათუმში აგზავნით?” / “Do you ship to Batumi?”
- “სად ჩაგირიცხოთ?” / “Where should I transfer payment?”
- “მისამართი ეს არის...” / “This is my address...”

The seller answers manually, tracks addresses in Messenger/notebooks/Excel, remembers stock mentally, and often forgets that a product is sold out or unavailable.

Long-term future layers may include:

- product mini-pages;
- buyer-facing product question assistant;
- chatbot as intermediary between inventory and buyer;
- buyer order request;
- seller approval;
- stock updates through order workflow;
- payment;
- delivery/export;
- intent recovery.

However, the current MVP is explicitly **inventory/catalog first**.

---

## 2. Core Product Principle

> **Inventory must be part of the seller's daily work, not a separate Excel-like island.**

This principle drives every technical and UX decision.

The seller should not enter the system only to “fill inventory”. The dashboard must become the place where they see today’s product state, low-stock items, missing information, draft products, sold-out computed states, and quick actions.

The MVP must not feel like:

- Excel;
- Shopify admin;
- WooCommerce;
- ERP;
- a static product table.

It must feel like:

- a fast mobile catalog cockpit;
- a smart assistant for managing product chaos;
- a practical daily dashboard.

---

## 3. Inventory-first Pivot Decision

The MVP starts with an **inventory/catalog cockpit** because every future automation layer depends on reliable product data.

If the seller does not use the inventory/catalog cockpit daily, later chatbot, order automation, payment, delivery, and recovery layers lose value.

### Main hypothesis

If a seller can add or update products in under 60 seconds, with smart defaults, clone flows, variant-level quantity, and automatic availability logic, then the seller has a real reason to use the system daily.

### MVP validation target

Check whether a seller can add/update 20–50 products and keep using the system for 21 days without abandoning it.

### Main strength of this pivot

Inventory is the foundation of every future social-commerce automation.

A chatbot cannot answer correctly without knowing:

- product name;
- photo;
- price;
- availability;
- size;
- color;
- stock quantity;
- preorder status;
- production time;
- hidden/draft status.

### Main risk

Inventory entry can feel like administrative work. If product creation/editing is slow, static, or boring, sellers will abandon it.

### MVP failure condition

The MVP fails if it becomes a product table rather than an operational cockpit.

---

## 4. Final MVP Scope

### In scope

- private seller dashboard only;
- mobile-first responsive web/PWA-friendly UI;
- User → Business → Products architecture;
- clothing-first MVP domain brain;
- generic fallback mode;
- domain-aware product model, not one universal mega-table;
- variant-level quantity;
- automatic computed availability / sold-out logic;
- quick stock update actions: `+1`, `-1`, `set quantity`;
- product clone / duplicate flows;
- smart defaults;
- local media storage for pilot/training base;
- basic image resize/compression;
- Django admin for internal debugging;
- PostgreSQL usage event table for 21-day validation;
- computed warnings initially.

### Out of scope for MVP

- orders;
- reservations;
- payments;
- delivery integration;
- chatbot;
- buyer-facing public catalog;
- Facebook/Instagram importer;
- AI assistant;
- customer database;
- multi-staff permissions;
- accounting;
- supplier management;
- ERP-style stock ledger;
- microservices.

---

## 5. Chosen Technology Stack

### Final stack

```text
Backend: Django
Database: PostgreSQL
Frontend: Django Templates + HTMX + Alpine.js + Tailwind CSS
Environment: Linux local + Python venv + PyCharm
Media: Local media storage initially
API: Small internal JSON/HTMX endpoints only
Architecture: Modular monolith
```

### Rationale

Django is chosen because the project needs:

- fast CRUD;
- auth;
- admin/debug tooling;
- migrations;
- server-side forms and validation;
- PostgreSQL support;
- fast solo-development velocity;
- minimal dependency sprawl;
- one cohesive framework instead of many separate libraries.

FastAPI/React are postponed because they would require more manual setup for auth, admin, permissions, forms, and validation UI. Full REST/DRF API can be added later when public catalog, chatbot, or order assistant requires it.

### Frontend rationale

Django Templates + HTMX + Alpine.js + Tailwind CSS are selected to prioritize:

- speed;
- mobile responsiveness;
- simple server-driven UI;
- low JavaScript complexity;
- fast form interactions;
- HTMX partial updates for quantity/status/dashboard cards.

React/Vue are postponed until workflow complexity proves they are needed.

---

## 6. Architecture Style

The architecture is a **modular monolith**.

No microservices. No event bus. No Kafka. No Kubernetes. No distributed complexity.

The codebase should be organized into Django apps with clear module boundaries:

```text
apps/
  accounts/
  businesses/
  catalog/
  clothing/
  inventory/
  dashboard/
  analytics/
  validation/
```

Future modules may include:

```text
orders/
customers/
payments/
delivery/
chatbot/
public_catalog/
ai_suggestions/
```

but not in MVP.

---

## 7. Domain-aware Product Model

The system must not use one giant universal product table with 150 nullable fields.

Correct pattern:

```text
Common catalog core
+
Domain-specific brain
```

Common core:

- Product;
- ProductVariant;
- ProductPhoto;
- Category;
- InventoryAdjustment;
- UsageEvent.

Domain-specific modules:

- ClothingProductProfile;
- ClothingVariantProfile;
- future ToyProductProfile;
- future GiftProductProfile;
- future HandmadeProductProfile;
- future CustomProductProfile.

The first real domain brain is **clothing** because it forces the architecture to handle:

- size;
- color;
- sub-color;
- target audience/gender;
- variant quantities;
- material;
- fit/style;
- season;
- filters;
- future chatbot-readable product intelligence.

Generic fallback exists, but development focus is clothing-first.

---

## 8. Data Model v1

### User

Use Django built-in User or a custom user model configured for email/password login.

MVP auth:

```text
email/password
```

Phone login is later.

---

### Business

Each user can own multiple businesses, even if UI initially shows one.

```text
Business
- id
- owner_user_id
- name
- template_type
- default_currency
- created_at
- updated_at
```

`template_type`:

```text
clothing
generic
```

Products belong to Business, not directly to User.

---

### Category

Seller/business-specific categories.

```text
Category
- id
- business_id
- name
- parent_id nullable
- sort_order
- created_at
- updated_at
```

Do not build a global taxonomy in MVP.

---

### Product

Product is the catalog-level item. It is not the source of stock truth.

```text
Product
- id
- business_id
- category_id nullable
- name
- base_price
- currency
- lifecycle_status
- preorder_enabled
- production_time_min_days nullable
- production_time_max_days nullable
- internal_notes nullable
- visibility
- created_at
- updated_at
```

Lifecycle status:

```text
draft
active
hidden
archived
```

Do not store these as product lifecycle statuses:

```text
available
sold_out
reserved
```

Reason:

- `available` is computed;
- `sold_out` is computed from variant quantities;
- `reserved` belongs to future order/reservation layer, not MVP.

---

### ProductVariant

Every product has at least one variant.

Simple product:

```text
Product: Handmade candle
Variant: Default
quantity_on_hand: 3
```

Clothing product:

```text
Product: Black dress
Variant 1: S / Black / qty 2
Variant 2: M / Black / qty 1
Variant 3: L / Black / qty 0
```

Model:

```text
ProductVariant
- id
- product_id
- label nullable
- price_override nullable
- quantity_on_hand
- low_stock_threshold
- is_active
- created_at
- updated_at
```

Quantity source of truth is **only** variant-level.

There is no product-level quantity as source of truth.

---

### ClothingProductProfile

Product-level clothing-specific intelligence.

```text
ClothingProductProfile
- product_id
- target_gender / target_audience
- season nullable
- material nullable
- fit_style nullable
- extra_attributes JSONB nullable
```

Required in clothing MVP:

```text
target_gender / target_audience
```

Optional:

```text
season
material
fit_style
extra_attributes
```

Seller-facing Georgian UI wording should probably use:

```text
ვისთვისაა?
- ქალი
- კაცი
- ბავშვი
- unisex
```

instead of a technical “gender” label.

---

### ClothingVariantProfile

Variant-level clothing-specific attributes.

```text
ClothingVariantProfile
- variant_id
- size
- color
- sub_color nullable
- material nullable
- extra_attributes JSONB nullable
```

Required in clothing MVP:

```text
size
color
quantity_on_hand
```

Optional:

```text
sub_color
material
```

---

### ProductPhoto

```text
ProductPhoto
- id
- product_id
- image
- is_primary
- sort_order
- created_at
```

MVP:

- product can have multiple photos;
- one primary photo;
- local media storage;
- basic image resize/compression;
- variant-level photos later.

---

### InventoryAdjustment

This is an inventory audit/action log, not an order system.

```text
InventoryAdjustment
- id
- business_id
- product_id
- variant_id
- change_type
- old_quantity
- new_quantity
- delta
- note nullable
- created_by
- created_at
```

Change types:

```text
initial_stock
manual_set
quick_increment
quick_decrement
bulk_set
system_correction
```

This prepares the future order system: later an order action can create the same type of inventory adjustment. For MVP, only manual/quick inventory updates exist.

---

### UsageEvent

Needed for 21-day MVP validation.

```text
UsageEvent
- id
- business_id
- user_id
- event_type
- object_type
- object_id nullable
- metadata JSONB nullable
- created_at
```

Event types:

```text
dashboard_opened
product_created
product_updated
product_cloned
variant_created
variant_quantity_changed
warning_seen
warning_fixed
photo_uploaded
```

External analytics tool is not needed for MVP.

---

## 9. Availability and Status Logic

### DB lifecycle status

Stored product status:

```text
draft
active
hidden
archived
```

### Computed seller-facing display status

Computed in service layer or query helper:

```text
Draft
Available
Low stock
Partially sold out
Sold out
Preorder available
Hidden
Archived
```

### Rule examples

If product lifecycle is `hidden`, display status is `Hidden`, regardless of quantity.

If product lifecycle is `archived`, display status is `Archived`, regardless of quantity.

If product lifecycle is `draft`, display status is `Draft`.

If product lifecycle is `active` and at least one active variant has quantity > 0, display status is `Available`.

If product lifecycle is `active`, some active variants have quantity = 0 and some > 0, display status is `Partially sold out` or Georgian UI wording: `ზოგი ზომა/ფერი ამოწურულია`.

If product lifecycle is `active`, all active variants have quantity = 0, and preorder is false, display status is `Sold out`.

If product lifecycle is `active`, all active variants have quantity = 0, and preorder is true, display status is `Preorder available`.

If a variant quantity is <= low stock threshold and > 0, show low-stock warning.

---

## 10. Preorder Logic

Preorder must not become an order system in MVP.

Preorder is product-level mode:

```text
preorder_enabled = true/false
production_time_min_days
production_time_max_days
```

Rules:

- preorder product may still have physical quantity;
- if quantity is 0 and preorder is false, computed display status is `Sold out`;
- if quantity is 0 and preorder is true, computed display status is `Preorder available`;
- preorder does not create order;
- preorder does not create reservation;
- production time is required/recommended when preorder is enabled.

Future chatbot can use this information to answer:

> “This item is not currently in stock, but it can be made/preordered in 5–7 days.”

---

## 11. Quantity UX

Because MVP has no orders/reservations, stock changes must be extremely fast.

Variant/product card should support:

```text
+1
-1
Set quantity
```

Seller-facing labels should use Georgian language like:

```text
ნაშთი
დარჩენილია
განახლება
```

Do not call this “Mark sold”, “Reserve”, or “Order” in MVP.

When a variant quantity becomes 0:

- that variant appears sold out automatically;
- if all variants are 0, the product appears sold out automatically;
- seller does not need to manually switch status to sold out.

This is one of the key smart behaviors that differentiates the product from Excel.

---

## 12. Warning Engine v1

Warnings are computed on dashboard load initially. Persistent warning table may be added later.

MVP warnings:

```text
missing price
missing photo
active product with no variants
clothing variant missing size
clothing variant missing color
clothing product missing target audience/gender
active product with all variants quantity 0
low stock variant
draft product ready to activate
preorder product missing production time
```

Tone must be assistant-like, not punitive.

Bad:

```text
Validation failed.
```

Good:

```text
ამ პროდუქტს ფასი აკლია — მყიდველისთვის პასუხი ვერ მომზადდება.
```

Good:

```text
ყველა ზომა/ფერი ამოწურულია. პროდუქტი ავტომატურად Sold out-ად გამოჩნდება.
```

---

## 13. Product Creation UX

Goal: product creation under 60 seconds.

### Clothing add product flow

Required top section:

```text
Photo
Name
Price
Target audience / “ვისთვისაა?”
Category
```

Variant section:

```text
Size
Color
Sub-color optional
Quantity
```

Optional/collapsible section:

```text
Material
Season
Fit/style
Preorder
Production time
Internal notes
```

### Required clothing fields

```text
photo
name
price
target audience/gender
at least one variant
variant size
variant color
variant quantity
```

### Optional

```text
sub-color
material
season
fit/style
notes
preorder
production time
```

For preorder-enabled product:

- quantity can be 0;
- production time should be required/recommended.

---

## 14. Clone / Duplicate UX

Clone is a retention-critical feature, especially for clothing.

Product card actions should include:

```text
Duplicate
Duplicate with new color
Duplicate with new size
Duplicate with new photo
Save & add another
```

Clone should copy:

- product name or base name;
- category;
- price;
- target audience;
- material/optional fields;
- variants depending on clone type;
- photos depending on clone type;
- preorder settings if relevant.

It should let the seller create many similar products quickly without re-entering repeated fields.

---

## 15. Smart Defaults

MVP-required smart defaults:

```text
last used category
remembered sizes
remembered colors
default quantity
copied fields from previous product
default lifecycle status based on completeness
```

Rules:

- if required fields are complete, default lifecycle can be `active`;
- if missing required data, default lifecycle should be `draft`;
- in clothing, last-used size/color chips should be shown;
- quantity is required for normal physical stock products;
- preorder product may have quantity 0 if production time exists.

Later smart defaults:

```text
suggested price from similar items
AI-generated product name
caption parser
OCR extraction
category suggestions
```

Do not build AI in MVP.

---

## 16. Dashboard / Daily Cockpit

First dashboard screen must answer:

> “What do I need to manage today?”

Not:

> “Here is a table of products.”

Priority blocks:

1. Quick Add / Add Similar;
2. Needs Attention;
3. Low Stock;
4. Sold Out / Computed sold-out products;
5. Drafts ready to activate;
6. Recently updated products;
7. Product search/filter.

Product cards should show:

- primary photo;
- product name;
- price;
- computed display status;
- total quantity / variant summary;
- quick quantity update;
- clone action;
- edit action.

No heavy spreadsheet table as primary UX.

---

## 17. Routes v1

Main pages:

```text
/login/
/business/setup/
/dashboard/
/products/
/products/new/
/products/<id>/
/products/<id>/edit/
/products/<id>/clone/
```

Variant routes:

```text
/products/<id>/variants/
/variants/<id>/edit/
/variants/<id>/quantity/
```

HTMX partials:

```text
/partials/dashboard/needs-attention/
/partials/products/<id>/card/
/partials/variants/<id>/quantity-control/
/partials/products/<id>/availability-badge/
```

Internal JSON endpoints only if useful:

```text
/internal/products/<id>/availability/
```

Full DRF REST API is later.

---

## 18. Service Layer

Do not put domain logic directly in views.

Expected services:

```text
catalog/services/product_create.py
catalog/services/product_clone.py
inventory/services/quantity_update.py
inventory/services/availability.py
validation/services/warnings.py
analytics/services/events.py
```

Responsibilities:

### create_product

- create product;
- create default variant or clothing variants;
- create clothing profiles when business template is clothing;
- log `product_created`.

### clone_product

- copy product;
- copy domain profile;
- copy selected variants;
- copy/carry photos depending on clone mode;
- log `product_cloned`.

### update_quantity

- validate quantity >= 0;
- update variant quantity;
- create InventoryAdjustment;
- log `variant_quantity_changed`;
- return computed availability.

### compute_product_availability

- check lifecycle status;
- check active variants;
- check quantity;
- check preorder;
- return display status and warning hints.

### compute_warnings

- run common product rules;
- run clothing-specific rules;
- return dashboard warning objects.

---

## 19. Validation Plan: 21-day Pilot

### Activation metrics

- did seller add first product?
- did seller add 5 products?
- did seller add 20 products?
- time to first product;
- median product creation time.

### Catalog depth

- total products added;
- products with photo + name + price + status;
- products with variant quantity;
- clothing products with size/color.

### Speed metrics

- median product creation time;
- clone creation time;
- edit/update time.

### Retention metrics

- Day 1 return;
- Day 3 return;
- Day 7 return;
- Day 14 return;
- Day 21 return.

### Operational usage metrics

- quantity updates;
- clone usage;
- warning seen/fixed;
- dashboard opens.

### Success threshold

Minimum success:

- 60%+ sellers add at least 10 products;
- 40%+ sellers add at least 20 products;
- median product creation under 90 seconds;
- 40%+ return at least 5 separate days in 21 days;
- 30%+ make at least 3 quantity/status/product updates;
- at least 3 sellers say it is better than Excel/Messenger notes.

Strong success:

- 50%+ sellers add 20+ products;
- median creation under 60 seconds;
- 40%+ use clone;
- 40%+ fix warnings;
- 20–30% willingness to pay 49 GEL/month.

Kill criteria:

- most sellers add only 1–3 products and stop;
- median creation time > 2 minutes;
- sellers say “it is good, but I am too lazy to use it”;
- no dashboard return without reminders;
- clone is not used;
- quantity update is not used;
- nobody says it is better than Excel;
- nobody would pay even 29–49 GEL after pilot.

Main validation metric:

```text
In 21 days, how many sellers perform 10+ meaningful inventory/catalog actions without being reminded?
```

Meaningful actions:

- product create;
- product edit;
- product clone;
- variant create;
- quantity update;
- warning fix;
- dashboard revisit.

Threshold to proceed to chatbot/order layer:

```text
At least 40% of pilot sellers perform 10+ meaningful actions in 21 days.
```

---

## 20. Pricing Hypothesis

Inventory-only MVP pricing hypothesis:

```text
21-day free trial
then 49 GEL/month
```

99 GEL/month is probably too high before order/chatbot/payment layers exist.

29 GEL/month may be acceptable for early adopters but could weaken value signal.

Billing integration is not required in MVP. Manual payment is enough during pilot.

---

## 21. Build Philosophy

Build for local pilot first. Avoid enterprise architecture.

Prioritize:

- product creation speed;
- mobile UX;
- variant quantity correctness;
- clone speed;
- computed status intelligence;
- dashboard usefulness;
- validation metrics.

Avoid:

- over-modeling;
- universal mega-tables;
- premature public catalog;
- premature AI;
- premature orders;
- premature payments;
- frontend framework complexity;
- ERP-style inventory ledger.

Repeated guiding principle:

> **Inventory must be part of the seller's daily work, not a separate Excel-like island.**
