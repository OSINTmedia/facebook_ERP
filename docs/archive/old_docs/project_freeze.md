# PROJECT.md — Social Commerce Operating Assistant MVP

**Project codename:** MVP  
**Working directory:** `/home/giga/Desktop/MVP/`  
**Primary market:** Georgia  
**Primary users:** small / solo Facebook & Instagram sellers  
**Document language:** Georgian  
**Document purpose:** Full MVP/product/architecture/business context for Codex or any developer who has no access to the original discussion history.

---

## 0. One-sentence product definition

ეს პროექტი არის **mobile-first Social Commerce Operating Assistant** მცირე Facebook/Instagram seller-ებისთვის, რომელიც Messenger-ის ქაოსს აქცევს დალაგებულ **პროდუქციის კატალოგად, ნაშთებად, seller dashboard-ად, buyer-facing interaction layer-ად, chatbot/intermediary assistant-ად და მომავალ order/payment/delivery workflow-ად**.

პირველი რეალური MVP იწყება **inventory/catalog cockpit-ით**, რადგან ყველა შემდეგი automation ფენა დამოკიდებულია სანდო პროდუქტისა და ნაშთის მონაცემებზე.

---

## 1. Core principle

> **Inventory უნდა იყოს seller-ის ყოველდღიური სამუშაოს ნაწილი, არა ცალკე Excel-ის მსგავსი კუნძული.**

ეს პრინციპი მართავს მთელ სისტემას.

სისტემის მიზანი არ არის seller-ს კიდევ ერთი ცხრილი მიეცეს. მიზანია seller ყოველდღე შედიოდეს dashboard-ში, რადგან იქ ხედავს:

- რა პროდუქცია აქვს;
- რა აკლია;
- რა ამოიწურა;
- რა არის დასამატებელი;
- რა შეიძლება უპასუხოს მყიდველს;
- რა უნდა განახლდეს;
- რა შექმნის გაყიდვას;
- რა შეამცირებს Messenger-ის ხელით პასუხების რაოდენობას.

---

## 2. Background and market context

სამიზნე მომხმარებლები არიან მცირე და სოლო ბიზნესები, რომლებიც ძირითადად ყიდიან Facebook/Instagram-ზე:

- სახლში მკერავი;
- ქალის/საბავშვო ტანსაცმლის seller;
- handmade seller;
- საჩუქრების/სუვენირების seller;
- seasonal seller;
- მცირე საოჯახო ბიზნესი;
- seller, რომელსაც არ აქვს საიტი, IT გუნდი, Shopify, WooCommerce ან ERP.

მათი დღევანდელი რეალობა:

- დებენ პროდუქტებს Facebook/Instagram-ზე;
- მყიდველები Messenger-ში ეკითხებიან:
  - ფასი?
  - გაქვთ?
  - რა ზომებია?
  - სხვა ფერი გაქვთ?
  - ბათუმში აგზავნით?
  - სად ჩავრიცხო?
  - ეს მისამართია...
- seller პასუხობს ხელით;
- მისამართები ინახება Messenger-ში, რვეულში ან Excel-ში;
- stock ხშირად მეხსიერებით იცის;
- პროდუქტი შეიძლება გაყიდული იყოს, მაგრამ პოსტში ისევ ჩანდა;
- Excel სცადეს, მაგრამ მიატოვეს, რადგან:
  - static ფაილია;
  - ცუდი mobile UX აქვს;
  - არ უკავშირდება გაყიდვებს;
  - არ აქვს warning-ები;
  - არ აქვს smart defaults;
  - არ აქვს ყოველდღიური სამუშაო flow.

---

## 3. Long-term vision

სრული ხედვა არის:

> **Social Commerce Operating Assistant for Facebook/Instagram sellers.**

სისტემა საბოლოოდ უნდა გახდეს შუამავალი seller-სა და buyer-ს შორის.

გრძელვადიანი ფენები:

1. **Inventory/Catalog Cockpit**
   - პროდუქციის მართვა;
   - ფოტოები;
   - ფასები;
   - ნაშთები;
   - variants;
   - computed availability;
   - warnings;
   - daily dashboard.

2. **Buyer-facing Product Layer**
   - product mini-pages;
   - shareable product links;
   - catalog mini-page;
   - buyer inquiry/request form.

3. **Intermediary Assistant Layer**
   - chatbot / product assistant;
   - პასუხობს buyer-ის კითხვებს პროდუქტის, ფასის, ზომის, ფერის, ნაშთის, მიწოდების შესახებ;
   - ეყრდნობა inventory/catalog მონაცემებს;
   - seller-ს სთხოვს confirmation-ს critical ქმედებებზე.

4. **Order Workflow Layer**
   - buyer request;
   - seller approval;
   - order status;
   - stock decrement;
   - reservation;
   - cancellation;
   - fulfillment.

5. **Payment Layer**
   - payment link;
   - bank transfer note;
   - manual confirmation;
   - future payment integration.

6. **Delivery/Export Layer**
   - address capture;
   - delivery status;
   - courier/export integration;
   - labels/reports.

7. **Recovery/Intent Layer**
   - buyer intent detection;
   - unanswered questions;
   - abandoned inquiries;
   - reminder to seller;
   - “buyer asked about X, answer now”.

---

## 4. Current MVP scope

### 4.1 First MVP

პირველი MVP არის:

> **Ultra-fast, pleasant, smart, mobile-first პროდუქციის კატალოგის მართვის სისტემა / inventory-catalog cockpit for solo Facebook/Instagram sellers.**

MVP უნდა ამოწმებდეს:

- შეუძლია თუ არა seller-ს 20–50 პროდუქტის დამატება;
- შეუძლია თუ არა seller-ს ნაშთების განახლება;
- ბრუნდება თუ არა dashboard-ში;
- გრძნობს თუ არა, რომ ეს Excel-ზე უკეთესია;
- არის თუ არა catalog საკმარისად usable მომავალი chatbot/order layer-ისთვის.

### 4.2 MVP is NOT

პირველი MVP არ არის:

- Shopify clone;
- WooCommerce clone;
- ERP;
- full order management;
- payment system;
- public storefront;
- Facebook/Instagram importer;
- AI automation platform;
- chatbot-first product;
- delivery management;
- accounting;
- supplier management.

---

## 5. Strategic pivot: why inventory-first

ყველა მომავალი ფენა საჭიროებს სანდო catalog/inventory-ს:

- chatbot ვერ უპასუხებს ფასზე, თუ ფასი არ არის;
- chatbot ვერ იტყვის ზომას/ფერს, თუ variant data არ არის;
- order workflow ვერ შეამცირებს stock-ს, თუ stock არ არსებობს;
- buyer link უსარგებლოა, თუ product incomplete-ია;
- payment წინსწრებულია, თუ seller-ს არ აქვს დალაგებული product data.

ამიტომ პირველი validation უნდა იყოს:

> გამოიყენებს თუ არა seller ყოველდღე inventory/catalog cockpit-ს?

თუ არა, დანარჩენი ფენები ნაადრევია.

---

## 6. MVP hypothesis

**Main hypothesis:**

თუ seller-ს მივცემ იმდენად მარტივ და სასიამოვნო inventory/catalog dashboard-ს, რომ პროდუქტის დამატება/განახლება 1 წუთზე ნაკლებში შეძლოს, ხოლო stock/status update ბუნებრივად იყოს dashboard workflow-ის ნაწილი, მაშინ მას ექნება რეალური მიზეზი სისტემაში ყოველდღე შესასვლელად.

**Validation target:**

21 დღეში seller-მა უნდა შეძლოს:

- 20–50 პროდუქტის დამატება;
- product/variant quantity updates;
- clone/duplicate flow-ის გამოყენება;
- warnings-ის ნახვა/გასწორება;
- dashboard-ში დაბრუნება;
- Excel-ზე უკეთესად აღქმა.

---

## 7. User personas

### 7.1 Solo clothing seller

საჭირო data:

- photo;
- name;
- price;
- category;
- gender/audience;
- size;
- color;
- sub-color;
- material;
- quantity per variant;
- status/availability;
- preorder flag optional.

Pain:

- ბევრი ზომა/ფერი;
- buyer მუდმივად ეკითხება availability-ს;
- stock memory-ზეა;
- sold-out product ჩანს პოსტში;
- მსგავსი პროდუქტების დამატება repetitive-ია.

Abandonment risk:

- მაღალი, თუ variant UX რთულია;
- მაღალი, თუ form ძალიან გრძელია;
- მაღალი, თუ clone არ მუშაობს.

### 7.2 Handmade seller

საჭირო data:

- photo;
- name;
- price;
- quantity often 1;
- custom/preorder option;
- production time;
- material;
- notes.

Pain:

- unique items;
- “იგივე შეგიძლია გამიკეთო?”;
- production time-ის განმეორებით თქმა.

Abandonment risk:

- საშუალო, თუ სისტემა ზედმეტად physical stock-oriented იქნება.

### 7.3 Gift/souvenir seller

საჭირო data:

- photo;
- name;
- price;
- category;
- occasion;
- quantity;
- gift set options;
- delivery note.

Pain:

- seasonal spikes;
- lots of similar items;
- fast sold-out.

Abandonment risk:

- საშუალო-მაღალი, თუ clone/collection flow სუსტი იქნება.

### 7.4 Preorder/custom seller

საჭირო data:

- product/service name;
- base price;
- preorder flag;
- production time;
- custom notes/options;
- availability.

Pain:

- physical quantity ყოველთვის არ აქვს;
- buyer-ს აინტერესებს ვადა და customization.

Abandonment risk:

- მაღალი, თუ quantity compulsory იქნება preorder product-ზე.

### 7.5 Seasonal seller

საჭირო data:

- collection/season;
- photo;
- price;
- quantity;
- availability;
- preorder deadline;
- archive/reuse.

Pain:

- მოკლე პერიოდში ბევრი product;
- სწრაფი changes;
- old catalog reuse.

Abandonment risk:

- საშუალო, თუ bulk/clone არ არის.

---

## 8. Business model and pricing hypothesis

### 8.1 First monetization hypothesis

Inventory-only MVP-ის რეალისტური ფასები:

- 21 დღე უფასო trial;
- შემდეგ 49 GEL/month;
- 99 GEL/month later, როცა დაემატება order/chatbot/payment value.

### 8.2 Why 49 GEL first

49 GEL არის უფრო რეალისტური small seller-ისთვის, როცა ჯერ გვაქვს მხოლოდ catalog/inventory cockpit.

99 GEL შეიძლება გამართლდეს მხოლოდ მაშინ, როცა სისტემა:

- ამცირებს buyer questions-ს;
- იღებს order request-ს;
- ეხმარება payment/delivery-ში;
- ცვლის manual Messenger burden-ს.

### 8.3 Success payment signal

კითხვა pilot-ის ბოლოს:

> “დღეს რომ trial დასრულდეს, გადაიხდიდით 49 ლარს თვეში?”

Strong signal:

- seller ამბობს “კი”;
- seller იყენებდა სისტემას დამოუკიდებლად;
- seller დაამატა product-ები;
- seller დაბრუნდა dashboard-ში;
- seller ამბობს “Excel-ზე უკეთესია”.

---

## 9. Product modules

### 9.1 Seller Dashboard / Cockpit

Seller dashboard არის MVP-ის მთავარი ადგილი.

პირველი ეკრანი უნდა აჩვენებდეს:

- Quick Add Product;
- Needs Attention;
- Low Stock;
- Sold Out computed products;
- Draft products;
- Products missing data;
- Recently updated products;
- Quick search/filter;
- Clone action;
- Quantity quick update.

Dashboard არ არის ცხრილი.

Dashboard უნდა იყოს **mobile-first card-based cockpit**.

### 9.2 Catalog Management

Functions:

- create product;
- edit product;
- upload photo;
- set price;
- set category;
- set clothing-specific profile;
- add variants;
- set quantities;
- duplicate/clone;
- hide/archive;
- search/filter.

### 9.3 Inventory / Quantity Management

Functions:

- variant-level quantity;
- quick +1;
- quick -1;
- set quantity;
- low stock threshold;
- computed sold out;
- computed availability;
- inventory adjustment log.

### 9.4 Domain Brain

The system must not use one universal product table for everything.

Use:

- shared core product model;
- domain-specific product/variant profile.

First domain:

- clothing.

Later domains:

- toys;
- gifts;
- handmade;
- custom/preorder;
- electronics;
- cosmetics;
- food.

### 9.5 Buyer Side — later

Not MVP.

Future buyer side:

- product mini-page;
- catalog link;
- “ask about this product” button;
- request/order form;
- availability answer;
- size/color selection;
- delivery question capture.

### 9.6 Intermediary Assistant / Chatbot — later

Not MVP.

Future assistant:

- reads product/catalog data;
- answers buyer’s questions;
- detects missing fields;
- asks seller for confirmation;
- does not blindly publish or modify critical data;
- can bridge buyer inquiry and seller dashboard.

### 9.7 Order Workflow — later

Not MVP.

Future order layer:

- buyer request;
- seller approval;
- order status;
- stock adjustment;
- reservation;
- cancellation;
- payment status;
- delivery status.

### 9.8 Payment — later

Not MVP.

Future:

- manual bank transfer instructions;
- payment link;
- payment confirmation;
- payment status.

### 9.9 Delivery/Export — later

Not MVP.

Future:

- buyer address;
- phone;
- city;
- delivery note;
- export to courier;
- delivery status.

---

## 10. Confirmed technical stack

### Backend

- Django;
- modular monolith;
- PostgreSQL;
- Django admin for internal debugging.

### Frontend

- Django Templates;
- HTMX;
- Alpine.js;
- Tailwind CSS;
- mobile-first responsive layout.

### Local environment

- Linux;
- Python venv;
- PyCharm;
- local PostgreSQL;
- local media storage.

### API

- no full REST API in MVP;
- small internal endpoints for HTMX / JSON if useful;
- DRF later only when chatbot/public/order layers need API.

### Not initially

- React;
- Next.js;
- FastAPI as main MVP backend;
- Celery;
- Redis;
- Docker required;
- microservices;
- GraphQL;
- Elasticsearch;
- Kubernetes.

---

## 11. Technical architecture

### 11.1 Architecture style

```text
Modular monolith
```

Reason:

- solo developer-friendly;
- faster iteration;
- easier debugging;
- less infrastructure;
- no premature microservices.

### 11.2 Django apps

Recommended app structure:

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

### 11.3 Module responsibilities

#### accounts

- user auth;
- email/password;
- profile later.

#### businesses

- Business model;
- owner relation;
- template type;
- settings.

#### catalog

- Product;
- ProductVariant;
- ProductPhoto;
- Category;
- product creation;
- product edit;
- clone.

#### clothing

- ClothingProductProfile;
- ClothingVariantProfile;
- clothing-specific validation;
- clothing-specific forms;
- size/color/sub-color/gender fields.

#### inventory

- quantity update;
- InventoryAdjustment;
- availability computation;
- low stock logic.

#### dashboard

- cockpit queries;
- needs attention;
- recent changes;
- quick actions.

#### analytics

- UsageEvent;
- 21-day validation metrics.

#### validation

- computed warning rules;
- common/domain-specific warning dispatcher.

---

## 12. Data model v1

### 12.1 Business

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

Template types:

```text
clothing
generic
```

### 12.2 Category

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

Categories are seller/business-specific, not global taxonomy.

### 12.3 Product

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

Do not store `sold_out` as lifecycle status. It is computed.

### 12.4 ProductVariant

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

Quantity truth lives here.

All products must have at least one variant.

Simple product uses default variant.

### 12.5 ClothingProductProfile

```text
ClothingProductProfile
- product_id
- target_audience / gender
- material nullable
- season nullable
- fit_style nullable
- extra_attributes JSONB nullable
```

Required in clothing MVP:

- target audience/gender.

Optional:

- material;
- season;
- fit/style.

### 12.6 ClothingVariantProfile

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

- size;
- color;
- quantity_on_hand from ProductVariant.

Optional:

- sub-color;
- material.

### 12.7 ProductPhoto

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

- multiple product photos;
- one primary photo;
- local storage;
- basic resize/compress.

Variant-level photos later.

### 12.8 InventoryAdjustment

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

This is not order management. It is audit and future integration path.

### 12.9 UsageEvent

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

Events:

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

---

## 13. Computed availability model

### 13.1 Stored product status

```text
draft
active
hidden
archived
```

### 13.2 Seller-facing display status

Computed display statuses:

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

### 13.3 Rules

If product lifecycle status = hidden:

```text
display = Hidden
```

If product lifecycle status = archived:

```text
display = Archived
```

If product lifecycle status = draft:

```text
display = Draft
```

If product active and at least one active variant quantity > 0:

```text
display = Available
```

If product active and some variants are 0 while others are > 0:

```text
display = Partially sold out
```

If product active and all active variants quantity = 0 and preorder_enabled = false:

```text
display = Sold out
```

If product active and all active variants quantity = 0 and preorder_enabled = true:

```text
display = Preorder available
```

If any active variant quantity <= low_stock_threshold and > 0:

```text
display includes Low stock warning
```

---

## 14. Preorder model

Preorder is a product capability, not order workflow.

Fields:

```text
preorder_enabled
production_time_min_days
production_time_max_days
```

Rules:

- preorder product can have stock quantity;
- if quantity is 0 but preorder is enabled, show “Preorder available”;
- preorder without production time should trigger warning;
- preorder must not create order/reservation/payment in MVP.

---

## 15. Product creation UX

### 15.1 Goal

Product creation under 60 seconds.

### 15.2 Clothing product add flow

Required visible fields:

1. Photo
2. Product name
3. Price
4. Target audience/gender
5. Category
6. Variant block:
   - size;
   - color;
   - quantity.

Optional/collapsible:

- sub-color;
- material;
- season;
- fit/style;
- preorder;
- production time;
- notes.

### 15.3 UX principles

- photo-first;
- mobile-first;
- one-tap chips for size/color;
- remembered last category;
- remembered colors/sizes;
- save & add another;
- save & duplicate;
- clone with new color;
- clone with new size;
- no ERP terminology.

---

## 16. Clone/duplicate UX

Clone is critical.

Actions:

- duplicate exact product;
- duplicate with new color;
- duplicate with new size;
- duplicate with new photo;
- save & add another in same category.

Copied fields:

- name optionally;
- price;
- category;
- gender/audience;
- material;
- season;
- notes;
- preorder settings;
- variant structure where useful.

Seller changes:

- photo;
- color;
- size;
- quantity.

---

## 17. Dashboard / cockpit design

### 17.1 First screen sections

1. Quick Add Product
2. Needs Attention
3. Low Stock
4. Sold Out / Preorder Available
5. Drafts
6. Recently Updated
7. Search/filter
8. Product cards

### 17.2 Product card must show

- photo;
- name;
- price;
- computed status;
- variants summary;
- quantity summary;
- quick + / - / set;
- edit;
- clone;
- hide/archive.

### 17.3 Avoid

- spreadsheet table as primary interface;
- dense ERP-like forms;
- excessive settings;
- generic admin UI for seller.

---

## 18. Validation and warnings

Warnings initially computed on dashboard load.

### MVP-critical warnings

- missing price;
- missing photo;
- active product with no variants;
- clothing product missing gender/audience;
- clothing variant missing size;
- clothing variant missing color;
- active product with all variants quantity 0;
- low stock variant;
- draft product ready to activate;
- preorder product missing production time.

### Tone

Use helpful Georgian messages.

Example:

```text
ამ პროდუქტს ფასი აკლია — მყიდველისთვის პასუხი ვერ მომზადდება.
```

Not:

```text
Validation error.
```

---

## 19. Seller-facing wording

Preferred product name:

```text
პროდუქციის კატალოგის მართვის სისტემა
```

Preferred UI words:

- კატალოგი;
- პროდუქცია;
- ნაშთები;
- დარჩენილია;
- სწრაფი განახლება;
- ზომა;
- ფერი;
- ქვეფერი;
- ვისთვისაა;
- დამალვა;
- არქივი;
- შევსება;
- გასასწორებელია.

Avoid seller-facing words:

- ERP;
- SKU;
- inventory ledger;
- variant matrix;
- event sourcing;
- stock movement;
- database;
- schema.

---

## 20. Buyer side — future full design

Not MVP, but project-level design should leave room for this.

### 20.1 Product mini-page

Buyer sees:

- photos;
- name;
- price;
- available sizes/colors;
- availability;
- preorder time if stock 0 and preorder enabled;
- delivery note;
- ask/request button.

### 20.2 Buyer inquiry form

Buyer can ask:

- is this available?
- choose size/color;
- choose quantity;
- provide phone/address;
- ask custom question.

### 20.3 Buyer experience principle

Buyer should not need to know the seller’s internal workflow.

The system should reduce repetitive Messenger questions.

---

## 21. Intermediary assistant / chatbot — future full design

The assistant sits between buyer and seller.

It must:

- read catalog/inventory data;
- answer product-specific questions;
- detect missing data;
- ask seller to confirm critical actions;
- never blindly change price/quantity/status;
- never publish uncertain data without seller confirmation.

Safe AI workflow:

1. suggest;
2. highlight uncertainty;
3. seller confirms;
4. then apply.

Potential assistant abilities:

- answer price;
- answer availability;
- answer size/color;
- answer preorder time;
- ask seller when missing field;
- recover unanswered buyer intent;
- route buyer to mini-page/order request.

---

## 22. Order side — future full design

Not MVP.

Future order lifecycle:

```text
Buyer inquiry
→ order request
→ seller approval
→ stock reservation
→ payment pending
→ paid
→ packed
→ delivered
→ completed / cancelled
```

Important:

- order action should create inventory adjustment;
- seller should not need duplicate manual work;
- inventory action and order action should be linked later.

MVP should not implement orders, but InventoryAdjustment exists to make future integration clean.

---

## 23. Inventory side — full design

### 23.1 MVP

- variant quantity;
- quick update;
- computed sold out;
- low stock;
- adjustment log.

### 23.2 Later

- reservation;
- order-linked stock decrement;
- restock;
- returns;
- bulk edit;
- import/export;
- inventory history report.

### 23.3 Avoid in MVP

- full ledger UI;
- stock valuation;
- cost/profit;
- accounting;
- supplier management.

---

## 24. Design system direction

### 24.1 Mobile-first

Primary target device: mobile phone.

Design principles:

- large tap targets;
- card layout;
- bottom-friendly actions;
- minimal typing;
- chips/selectors;
- photo-first product identity;
- progressive disclosure;
- collapsible advanced fields.

### 24.2 Visual hierarchy

Dashboard:

- action first;
- warnings second;
- product cards third.

Product add form:

- required fields visible;
- optional fields collapsible;
- save actions sticky if possible.

### 24.3 Tone

Friendly, assistant-like, not corporate.

Example:

```text
ყველა ზომა ამოიწურა — პროდუქტი მყიდველისთვის Sold out-ად გამოჩნდება.
```

---

## 25. Analytics and validation

### 25.1 21-day metrics

Track:

- product_created;
- product_updated;
- product_cloned;
- variant_created;
- variant_quantity_changed;
- dashboard_opened;
- warning_seen;
- warning_fixed;
- photo_uploaded.

### 25.2 Success criteria

Minimum success:

- 60%+ pilot sellers add at least 10 products;
- 40%+ add at least 20 products;
- median product creation time under 90 seconds;
- 40%+ return at least 5 separate days in 21 days;
- 30%+ update quantity/status at least 3 times;
- at least 3 sellers say “Excel-ზე უკეთესია”.

Strong success:

- 50%+ sellers add 20+ products;
- median creation time under 60 seconds;
- 40%+ use clone;
- 40%+ fix warnings;
- 20–30% willing to pay 49 GEL/month.

### 25.3 Kill criteria

- sellers add 1–3 products and stop;
- median product creation time > 2 minutes;
- nobody returns without reminder;
- clone not used;
- quantity updates not used;
- sellers say “კარგია, მაგრამ მეზარება”;
- no one would pay 49 GEL.

---

## 26. Build stages

### Stage 0 — Project foundation

- initialize Django project;
- configure PostgreSQL;
- app structure;
- templates/static/media;
- base mobile layout;
- auth;
- admin;
- dependencies.

### Stage 1 — Business + catalog core

- User → Business;
- Product;
- ProductVariant;
- ProductPhoto;
- Category;
- basic add/edit/list.

### Stage 2 — Clothing brain

- ClothingProductProfile;
- ClothingVariantProfile;
- clothing form;
- size/color/quantity;
- required validation.

### Stage 3 — Inventory quantity engine

- quick +1 / -1 / set;
- InventoryAdjustment;
- computed availability;
- sold out auto display;
- low stock.

### Stage 4 — Clone/speed layer

- duplicate product;
- duplicate with new color;
- duplicate with new size;
- save & add another;
- remembered last category;
- remembered sizes/colors.

### Stage 5 — Daily cockpit

- Needs Attention;
- low stock;
- sold out;
- drafts;
- missing fields;
- recent updates;
- quick actions.

### Stage 6 — Validation analytics pilot

- UsageEvent logging;
- pilot metrics;
- admin/debug metrics;
- 21-day validation.

### Stage 7 — Future layers

Only after validation:

- public catalog;
- buyer mini-pages;
- assistant/chatbot;
- orders;
- payment;
- delivery;
- AI-assisted filling.

---

## 27. Implementation rules for Codex/developer

1. Always work inside `/home/giga/Desktop/MVP/`.
2. Read `inventory.md`, `checkpoint.md`, and this `project.md` before major implementation.
3. Update `checkpoint.md` after each completed stage according to its status log rules.
4. Do not delete existing files without explicit reason.
5. Do not overwrite documentation without preserving context.
6. Do not expand scope into orders/payments/chatbot/public catalog during MVP.
7. Keep seller UI Georgian-first.
8. Keep backend names clean and technical.
9. Keep business logic in service layer where practical.
10. Prefer simple Django code over unnecessary abstraction.
11. Use Django admin for internal debugging.
12. Use PostgreSQL event table for validation analytics.
13. Avoid microservices.
14. Avoid enterprise/ERP concepts.
15. Keep mobile-first UX as primary constraint.

---

## 28. Current final scope statement

The MVP should let a seller:

1. create a business;
2. select clothing/generic template;
3. add clothing products quickly;
4. upload product photos;
5. set price;
6. set gender/audience;
7. create size/color/quantity variants;
8. update quantity quickly;
9. see computed availability;
10. see sold out automatically when quantity becomes 0;
11. use preorder flag without order system;
12. clone similar products;
13. see dashboard warnings;
14. maintain a usable catalog over 21 days.

The MVP should prove whether this is useful enough before building chatbot/order/payment layers.

---

## 29. Final reminder

Do not build “everything”.

Build the cockpit first.

The future system can become a full Social Commerce Operating Assistant only if the seller first adopts the daily inventory/catalog cockpit.

> **Inventory უნდა იყოს seller-ის ყოველდღიური სამუშაოს ნაწილი, არა ცალკე Excel-ის მსგავსი კუნძული.**

---

## 30. Document metadata

```text
document_name: project.md
document_type: full_mvp_product_and_architecture_context
version: 1.0
created_at: 2026-05-27T10:05:54
status: initial_full_context
primary_owner: osMit
target_reader: Codex / developer / future technical assistant
```
