# Portfolio Demo Catalog Blueprint

## 1. Purpose

This document is the authoritative synthetic data specification for the future Phase 13 (P13.3) hosted portfolio demo of the Georgian Social Commerce Product Assistant.

- **Exact Size:** Exactly 50 Products (numbered D001 through D050).
- **Nature:** Purely synthetic demo data representing a realistic Georgian social-commerce seller's catalog. It does not represent real customer data, production secrets, or uncurated database dumps.
- **Goal:** To demonstrate the application's core capabilities — description-first capture, semantic candidate recognition, explicit seller confirmation, Business-scoped vocabulary and aliases, inventory ledger accuracy, buyer readiness evaluation, deterministic Ready Replies, and workflow tools (Add Similar, Archive/Restore) — under believable commercial conditions ranging from meticulous to chaotic seller behavior.

---

## 2. Scope and Constraints

### 2.1 In Scope (Portfolio V1 Truth)
- Single Business tenancy (`Seller Studio`, currency `GEL`).
- Three supported lifecycle states: `draft`, `active`, `archived`.
- Optional single primary image per Product (`ProductMedia`) with clean fallback placeholder when absent.
- Controlled Business-scoped vocabulary: Product Types, Tags, Sizes, Colors.
- Controlled Business-scoped aliases matching token and phrase recognition rules.
- Confirmed material facts (`ProductMaterialFact`) with optional percentages (1–100%).
- Multi-variant inventory (`ProductChoice`) with exact per-choice stock counts.
- Non-negative integer choice quantities with initial stock recording and +1/-1 steppers via `InventoryAdjustment`.
- Centralized availability computation (`available`, `partially_sold_out`, `sold_out`).
- Centralized buyer-question readiness evaluation across Price, Stock, Size/Color, Type, and Material.
- Deterministic Georgian Ready Reply generation with actionable seller warnings (missing information, duplicate choice ambiguity).
- Operational workflows: Add Similar, Archive, Restore-to-Draft, correction deep links, recognition candidate transfer.

### 2.2 Strictly Deferred / Out of Scope (V2 Guardrails)
- Multi-image galleries or carousels (strictly 0 or 1 primary image).
- Garment / body measurements (chest, waist, hip, length subsystem).
- Public buyer storefront or public catalog URL.
- Orders, checkout, shopping carts, or reservations.
- Social messaging integrations (Facebook Messenger / Instagram DM direct webhook APIs).
- Automated AI/LLM-generated descriptions or live operational truth overrides.
- Fuzzy string matching or Georgian morphological stemming not implemented in the current token/phrase recognizer.

---

## 3. Demo Business Story

**Business Persona:** *Seller Studio* (სელერ სტუდიო)  
**Location:** Tbilisi, Georgia  
**Channel:** Instagram / Facebook Page Social Commerce  
**Assortment Style:** Contemporary women's and unisex casual-to-festive apparel, knitwear, and seasonal outerwear.  
**Operational Profile:**  
A boutique apparel seller managing rapid daily stock intake directly from mobile or web admin. Like most small social sellers, their catalog reflects real operational history:
- Some products are meticulously documented with full composition percentages, formal tags, and clear pricing.
- Other products were quickly uploaded on the go with hurried, minimal descriptions, conversational Georgian slang, English fashion loanwords, or missing prices.
- Fast-moving items experience partial depletion (popular sizes sell out first) or total stock depletion.
- Several product models share similar silhouettes or identical fabrics across different colorways.
- Past season items are archived, with occasional pieces restored for clearance.

The application serves as this seller's operational truth backbone, turning informal descriptions into structured catalog entries and generating reliable Ready Replies for incoming customer DMs.

---

## 4. Vocabulary

All vocabulary entities and aliases are strictly scoped to the active Business (`Seller Studio`).

### 4.1 Product Types (14 Canonical Values)
1. `კაბა` (Dress)
2. `ჟაკეტი` (Jacket / Blazer)
3. `შარვალი` (Trousers / Pants)
4. `პერანგი` (Shirt)
5. `ბლუზა` (Blouse)
6. `მაისური` (T-Shirt)
7. `ქვედაბოლო` (Skirt)
8. `პალტო` (Coat)
9. `ჯინსი` (Jeans)
10. `ჰუდი` (Hoodie)
11. `სვიტერი` (Sweater)
12. `კარდიგანი` (Cardigan)
13. `ტოპი` (Top)
14. `ორეული` (Two-Piece Set)

### 4.2 Tags (10 Canonical Values)
1. `სადღესასწაულო` (Festive / Evening)
2. `ყოველდღიური` (Casual / Everyday)
3. `ზაფხული` (Summer)
4. `ზამთარი` (Winter)
5. `კლასიკური` (Classic / Formal)
6. `ოვერსაიზი` (Oversize)
7. `ბაზური` (Basic essentials)
8. `საგაზაფხულო` (Spring)
9. `პრემიუმი` (Premium)
10. `სპორტული` (Sporty)

### 4.3 Sizes (8 Canonical Values)
1. `XS`
2. `S`
3. `M`
4. `L`
5. `XL`
6. `XXL`
7. `Free size`
8. `36`

### 4.4 Colors (12 Canonical Values)
1. `შავი` (Black)
2. `თეთრი` (White)
3. `ლურჯი` (Blue)
4. `წითელი` (Red)
5. `ბეჟი` (Beige)
6. `მწვანე` (Green)
7. `ნაცრისფერი` (Gray)
8. `ყავისფერი` (Brown)
9. `ვარდისფერი` (Pink)
10. `კრემისფერი` (Cream)
11. `შინდისფერი` (Burgundy)
12. `ზეთისხილისფერი` (Olive)

### 4.5 Alias Matrix

| Alias | Canonical Value | Vocabulary Family | Demonstrated By Products | Description Note / Linguistic Context |
| :--- | :--- | :--- | :--- | :--- |
| `dress` | `კაბა` | Product Type | D001, D012, D043 | Common English fashion term |
| `სარაფანი` | `კაბა` | Product Type | D010, D034 | Georgian colloquial for sundress |
| `jacket` | `ჟაკეტი` | Product Type | D004, D028 | English loanword |
| `მოსაცმელი` | `ჟაკეტი` | Product Type | D018, D045 | Georgian descriptive term for light outerwear |
| `pants` | `შარვალი` | Product Type | D006, D038 | English loanword |
| `trousers` | `შარვალი` | Product Type | D022 | English formal loanword |
| `shirt` | `პერანგი` | Product Type | D007, D025 | English loanword |
| `რუბაშკა` | `პერანგი` | Product Type | D040 | Colloquial Georgian/Russian loanword |
| `t-shirt` | `მაისური` | Product Type | D009, D031 | Standard English loanword |
| `tee` | `მაისური` | Product Type | D046 | Informal English shorthand |
| `skirt` | `ქვედაბოლო` | Product Type | D015, D037 | English loanword |
| `იუბკა` | `ქვედაბოლო` | Product Type | D041 | Colloquial Georgian/Russian loanword |
| `coat` | `პალტო` | Product Type | D019, D048 | English loanword |
| `jeans` | `ჯინსი` | Product Type | D008, D036 | English spelling of jeans |
| `hoodie` | `ჰუდი` | Product Type | D011, D044 | English loanword |
| `sweater` | `სვიტერი` | Product Type | D016, D039 | English loanword |
| `cardigan` | `კარდიგანი` | Product Type | D020, D047 | English loanword |
| `top` | `ტოპი` | Product Type | D014, D042 | English loanword |
| `set` | `ორეული` | Product Type | D023, D049 | English loanword for two-piece suit |
| `casual` | `ყოველდღიური` | Tag | D007, D022, D031 | English fashion tag |
| `evening` | `სადღესასწაულო` | Tag | D001, D012, D043 | English tag for formal/evening wear |
| `საზეიმო` | `სადღესასწაულო` | Tag | D002, D027 | Georgian synonym |
| `party` | `სადღესასწაულო` | Tag | D014 | English party tag |
| `winter` | `ზამთარი` | Tag | D019, D048 | English seasonal tag |
| `summer` | `ზაფხული` | Tag | D009, D010, D034 | English seasonal tag |
| `classic` | `კლასიკური` | Tag | D005, D038 | English style loanword |
| `basic` | `ბაზური` | Tag | D008, D024, D046 | English basic wardrobe tag |
| `oversized` | `ოვერსაიზი` | Tag | D011, D040, D044 | English adjective variation |
| `უნივერსალური` | `Free size` | Size | D010, D020, D047 | Georgian synonym for universal size |
| `one size` | `Free size` | Size | D014, D033, D042 | Common English one-size designation |
| `oversize` | `Free size` | Size | D011, D025, D044 | Size alias where fit implies free size |
| `Small` | `S` | Size | D001, D026 | Full English word capitalized |
| `small` | `S` | Size | D012, D043 | Full English word lowercase |
| `Medium` | `M` | Size | D003, D030 | Full English word capitalized |
| `medium` | `M` | Size | D007, D040 | Full English word lowercase |
| `Large` | `L` | Size | D006, D035 | Full English word capitalized |
| `large` | `L` | Size | D015, D041 | Full English word lowercase |
| `black` | `შავი` | Color | D001, D005, D021, D038 | English color name |
| `white` | `თეთრი` | Color | D007, D009, D024, D031 | English color name |
| `blue` | `ლურჯი` | Color | D008, D026, D036 | English color name |
| `navy` | `ლურჯი` | Color | D003, D019, D048 | English dark blue shade |
| `red` | `წითელი` | Color | D004, D027, D045 | English color name |
| `beige` | `ბეჟი` | Color | D006, D016, D039 | English color name |
| `ხორცისფერი` | `ბეჟი` | Color | D013, D032 | Georgian colloquial synonym |
| `green` | `მწვანე` | Color | D017, D030 | English color name |
| `gray` | `ნაცრისფერი` | Color | D011, D035, D044 | English color name |
| `grey` | `ნაცრისფერი` | Color | D022 | British English spelling |
| `brown` | `ყავისფერი` | Color | D018, D029 | English color name |
| `pink` | `ვარდისფერი` | Color | D015, D041 | English color name |
| `cream` | `კრემისფერი` | Color | D020, D047 | English color name |
| `bordeaux` | `შინდისფერი` | Color | D002, D037 | French/English wine color loanword |
| `olive` | `ზეთისხილისფერი` | Color | D023, D049 | English olive color loanword |

---

## 5. Catalog Coverage Matrix

### 5.1 Lifecycle Distribution (Total: 50)
- **Active:** 41 Products (D001–D036, D043–D047)
- **Draft:** 6 Products (D037–D042)
- **Archived:** 3 Products (D048–D050)

### 5.2 Availability Distribution (Active: 41)
- **Available (Fully in stock or positive variants):** 28 Products
- **Partially Sold Out (Mixed stock choices: >0 and =0):** 8 Products (D003, D006, D008, D012, D015, D021, D026, D035)
- **Sold Out (All active choices qty = 0):** 5 Products (D004, D013, D017, D028, D032)
*(Draft and Archived products are excluded from active selling availability by definition)*

### 5.3 Buyer-Question Readiness Coverage (Active & Draft: 47)
- **Fully Answer-Ready (All 5 questions covered):** 24 Products
- **Missing Price Only (`price=None`):** 4 Products (D029, D030, D039, D040)
- **Missing Confirmed Material Only:** 6 Products (D005, D014, D022, D027, D031, D044)
- **Missing Product Type Only (`product_type=None`):** 2 Products (D038, D042)
- **Multiple Information Missing:** 4 Products (D037, D041, D045, D046)
- **Zero-Choice Incomplete Drafts:** 2 Products (D037, D042)
- **Sold Out but Fully Structured:** 5 Products (D004, D013, D017, D028, D032)

### 5.4 Seller Description Style Distribution (Total: 50)
- **Lazy / Minimal:** 12 Products (D005, D009, D013, D017, D024, D029, D032, D036, D038, D041, D042, D046)
- **Normal:** 18 Products (D002, D003, D004, D006, D008, D010, D015, D018, D021, D023, D026, D027, D030, D033, D034, D035, D037, D045)
- **Detailed:** 12 Products (D001, D007, D011, D014, D016, D019, D020, D022, D025, D028, D047, D048)
- **Chaotic / Shorthand / Alias-Heavy:** 8 Products (D012, D031, D039, D040, D043, D044, D049, D050)

### 5.5 Media Coverage (Total: 50)
- **With Primary Image (`WITH_PRIMARY_IMAGE`):** 36 Products
- **No Image Placeholder (`NO_IMAGE`):** 14 Products (D005, D009, D013, D017, D021, D024, D029, D032, D036, D037, D038, D041, D042, D046)

### 5.6 Dashboard Seller Attention Signals (Computed Truth)
- **Sold Out Products:** 5 Products (D004, D013, D017, D028, D032)
- **Partially Sold Out Choices:** 8 Products (choices at 0 qty in D003, D006, D008, D012, D015, D021, D026, D035)
- **Low Stock Choices (1 <= qty <= 3):** 12 Products (D002, D003, D006, D010, D011, D016, D018, D020, D025, D033, D034, D043)
- **Missing Information Products:** 16 Products across Active and Draft

---

## 6. Product Families

To reflect real social boutique inventory, the catalog incorporates three intentional similarity structures:

### 6.1 Near-Identical Products (Distinct IDs, Nearly Identical Presentation)
- **Black Slip Dress Twins:**
  - `D001`: Premium Silk Black Slip Dress (`აბრეშუმი` 100%, price 189.00 GEL, detailed description).
  - `D021`: Budget Satin Viscose Black Slip Dress (`ვისკოზა` 100%, price 99.00 GEL, normal description).
  - *Demonstration:* Two distinct active items with the same silhouette, demonstrating that the system avoids false identity collisions while keeping choice inventories separate.
- **Classic White Tee Pair:**
  - `D009`: Minimal white tee (`ბამბა` 100%, price 45.00 GEL, lazy description, no image).
  - `D024`: Basic white organic tee (`ბამბა` 95%, `ელასტანი` 5%, price 55.00 GEL, normal description, with primary image).
  - *Demonstration:* Separately tracked basic inventory items with distinct supplier compositions.

### 6.2 Product Families (Sharing Silhouettes, Types, and Sizing)
- **Family F1: Classic Straight Pants:** `D006` (Beige), `D022` (Gray), `D038` (Black Draft). Same cut, distinct colors, shared size grid (S, M, L).
- **Family F2: Linen Summer Sundresses:** `D010` (Yellow/Beige), `D034` (Olive), `D037` (White Draft).
- **Family F3: Wool Winter Knitwear:** `D016` (Sweater), `D020` (Cardigan), `D047` (Oversized Cardigan), `D048` (Archived Coat).
- **Family F4: Structured Denim:** `D008` (Blue Jeans), `D026` (Light Blue Jeans), `D036` (Black Denim).

### 6.3 Highly Distinct Products
Items with unique patterns, such as the two-piece linen set (`D023`), evening sequin top (`D014`), sporty oversized hoodie (`D011`), and formal tailored wool blazer (`D028`).

---

## 7. Exact 50-Product Specification

### D001 — ელეგანტური აბრეშუმის შავი კაბა
- **Seller description:** `დახვეწილი საღამოს შავი კაბა (black dress), დამზადებულია 100% ნატურალური აბრეშუმისგან. ზომები Small და M. იდეალურია evening წვეულებისთვის. ფასი 189 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `189.00`
- **Product Type:** `კაბა`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** `აბრეშუმი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Elegant black silk slip dress on neutral boutique mannequin.
- **Choices:**
  - `S` / `შავი` / 4 / active
  - `M` / `შავი` / 5 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready (all 5 questions answered)
- **Alias/vocabulary demonstrated:** Aliases `black` -> `შავი`, `dress` -> `კაბა`, `Small` -> `S`, `evening` -> `სადღესასწაულო`
- **Recognition/correction story:** Rich description generates candidates for type, color, size, material, tag, price.
- **Ready Reply scenario:** Complete reply showing price 189.00 GEL, 100% silk, active choices S and M in stock.
- **Demo purpose:** Benchmark golden product for full assistant readiness.
- **Similar/family relationship:** Near-identical counterpart to D021.
- **Maintenance demo role:** ADD_SIMILAR_SOURCE

---

### D002 — შინდისფერი საზეიმო კაბა
- **Seller description:** `ულამაზესი შინდისფერი (bordeaux) კაბა საზეიმო ღონისძიებებისთვის. ზომა S და M. ფასი 145 ლარი. მასალა: 100% ვისკოზა.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `145.00`
- **Product Type:** `კაბა`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** `ვისკოზა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Burgundy A-line midi dress on hanger against studio wall.
- **Choices:**
  - `S` / `შინდისფერი` / 2 / active (Low Stock)
  - `M` / `შინდისფერი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `bordeaux` -> `შინდისფერი`, `საზეიმო` -> `სადღესასწაულო`
- **Recognition/correction story:** Demonstrates color and tag synonym recognition.
- **Ready Reply scenario:** Full reply with low-stock status (2 left in S).
- **Demo purpose:** Normal intake with low-stock variant.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D003 — მუქი ლურჯი ყოველდღიური კაბა
- **Seller description:** `ლურჯი (navy) კომფორტული კაბა სამსახურისთვის. ზომები S და Medium. 95% ბამბა, 5% ელასტანი. ფასი 115 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `115.00`
- **Product Type:** `კაბა`
- **Tags:** `ყოველდღიური`
- **Confirmed material:** `ბამბა` (95%), `ელასტანი` (5%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Navy blue casual cotton dress on studio background.
- **Choices:**
  - `S` / `ლურჯი` / 0 / active (Depleted)
  - `M` / `ლურჯი` / 3 / active (Low Stock)
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `navy` -> `ლურჯი`, `Medium` -> `M`
- **Recognition/correction story:** Multi-fiber material percentage parsing.
- **Ready Reply scenario:** Emits partial stock notice: S is 0, M has 3 units.
- **Demo purpose:** Demonstrates partially sold-out warning and multi-fiber recognition.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D004 — წითელი კლასიკური ჟაკეტი
- **Seller description:** `წითელი (red) კლასიკური jacket, იდეალურად ზის ტანზე. ზომა M. 100% მატყლი. ფასი 175 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `175.00`
- **Product Type:** `ჟაკეტი`
- **Tags:** `კლასიკური`
- **Confirmed material:** `მატყლი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Red tailored blazer on mannequin.
- **Choices:**
  - `M` / `წითელი` / 0 / active (Sold Out)
- **Intended availability:** `sold_out`
- **Intended readiness:** Fully structured but sold out
- **Alias/vocabulary demonstrated:** `red` -> `წითელი`, `jacket` -> `ჟაკეტი`
- **Recognition/correction story:** Complete structured data, inventory is completely exhausted.
- **Ready Reply scenario:** Accurate Ready Reply stating 0 stock to prevent false sales promises.
- **Demo purpose:** Benchmark Sold-Out active product.
- **Similar/family relationship:** Family F1 / Outerwear
- **Maintenance demo role:** NONE

---

### D005 — შავი საბაზისო ჟაკეტი
- **Seller description:** `შავი black ჟაკეტი 140ლ`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `140.00`
- **Product Type:** `ჟაკეტი`
- **Tags:** None
- **Confirmed material:** None
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `S` / `შავი` / 4 / active
  - `M` / `შავი` / 6 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `black` -> `შავი`
- **Recognition/correction story:** Lazy description lacks material fact; triggers `#material-section` correction.
- **Ready Reply scenario:** Emits seller note `CONFIRMED_MATERIAL_MISSING`.
- **Demo purpose:** Lazy seller intake missing material facts.
- **Similar/family relationship:** Family F1 / Outerwear
- **Maintenance demo role:** NONE

---

### D006 — ბეჟი სწორი შარვალი
- **Seller description:** `კლასიკური ბეჟი (beige) შარვალი (pants), მაღალი წელით. ზომები S, M, Large. 100% ბამბა. ფასი 120 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `120.00`
- **Product Type:** `შარვალი`
- **Tags:** `კლასიკური`, `ყოველდღიური`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Beige high-waisted straight trousers on mannequin.
- **Choices:**
  - `S` / `ბეჟი` / 3 / active (Low Stock)
  - `M` / `ბეჟი` / 5 / active
  - `L` / `ბეჟი` / 0 / active (Depleted)
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `beige` -> `ბეჟი`, `pants` -> `შარვალი`, `Large` -> `L`
- **Recognition/correction story:** Multi-size grid with partial depletion.
- **Ready Reply scenario:** Reports S (3) and M (5) available, L out of stock.
- **Demo purpose:** Anchor member of Family F1 (Straight Pants).
- **Similar/family relationship:** Family F1
- **Maintenance demo role:** ADD_SIMILAR_SOURCE

---

### D007 — თეთრი ბამბის პერანგი
- **Seller description:** `კლასიკური თეთრი shirt ყოველდღიური casual სტილისთვის. 100% ნატურალური ბამბა. ზომები S, medium, L. ფასი 85.00 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `85.00`
- **Product Type:** `პერანგი`
- **Tags:** `კლასიკური`, `ყოველდღიური`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Crisp white button-down cotton shirt on mannequin.
- **Choices:**
  - `S` / `თეთრი` / 4 / active
  - `M` / `თეთრი` / 7 / active
  - `L` / `თეთრი` / 5 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `shirt` -> `პერანგი`, `casual` -> `ყოველდღიური`, `medium` -> `M`
- **Recognition/correction story:** Meticulous entry with complete facts and strong stock.
- **Ready Reply scenario:** Complete clean reply.
- **Demo purpose:** Everyday core inventory baseline.
- **Similar/family relationship:** Counterpart to D025.
- **Maintenance demo role:** NONE

---

### D008 — კლასიკური ლურჯი ჯინსი
- **Seller description:** `სწორი ჭრის ლურჯი jeans, basic მოდელი. ზომები 36, S, M. 98% ბამბა, 2% ელასტანი. ფასი 135 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `135.00`
- **Product Type:** `ჯინსი`
- **Tags:** `ბაზური`, `ყოველდღიური`
- **Confirmed material:** `ბამბა` (98%), `ელასტანი` (2%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Classic blue denim straight-leg jeans folded on wooden table.
- **Choices:**
  - `36` / `ლურჯი` / 0 / active (Depleted)
  - `S` / `ლურჯი` / 4 / active
  - `M` / `ლურჯი` / 6 / active
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `jeans` -> `ჯინსი`, `basic` -> `ბაზური`, numeric size `36`
- **Recognition/correction story:** Demonstrates mixed sizing (numeric 36 alongside S, M).
- **Ready Reply scenario:** Shows 36 out of stock, S and M available.
- **Demo purpose:** Family F4 (Denim) anchor product.
- **Similar/family relationship:** Family F4
- **Maintenance demo role:** NONE

---

### D009 — თეთრი საბაზისო მაისური
- **Seller description:** `თეთრი white t-shirt summer 45ლ`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `45.00`
- **Product Type:** `მაისური`
- **Tags:** `ზაფხული`
- **Confirmed material:** `ბამბა` (100%), source: `manual`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `S` / `თეთრი` / 8 / active
  - `M` / `თეთრი` / 10 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready (material confirmed manually)
- **Alias/vocabulary demonstrated:** `white` -> `თეთრი`, `t-shirt` -> `მაისური`, `summer` -> `ზაფხული`
- **Recognition/correction story:** Minimal description where seller manually confirmed material in UI.
- **Ready Reply scenario:** Standard clean reply.
- **Demo purpose:** Near-identical counterpart to D024.
- **Similar/family relationship:** Basic White Tee Pair
- **Maintenance demo role:** NONE

---

### D010 — ყვითელი ზაფხულის სარაფანი
- **Seller description:** `ზაფხულის მსუბუქი სარაფანი, ფერი კრემისფერი/ბეჟი. ზომა უნივერსალური (Free size). 100% თეთრეული/სელი. ფასი 95 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `95.00`
- **Product Type:** `კაბა`
- **Tags:** `ზაფხული`
- **Confirmed material:** `თეთრეული/სელი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Light cream/beige linen sundress hanging against bright backdrop.
- **Choices:**
  - `Free size` / `კრემისფერი` / 2 / active (Low Stock)
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `სარაფანი` -> `კაბა`, `უნივერსალური` -> `Free size`
- **Recognition/correction story:** Georgian colloquial aliases for both type and size.
- **Ready Reply scenario:** Single choice reply with low stock note (2 left).
- **Demo purpose:** Family F2 (Linen Sundresses) anchor product.
- **Similar/family relationship:** Family F2
- **Maintenance demo role:** NONE

---

### D011 — ნაცრისფერი ოვერსაიზ ჰუდი
- **Seller description:** `თბილი ნაცრისფერი (gray) oversized hoodie. შემადგენლობა: 80% ბამბა, 20% პოლიესტერი. ზომა oversize. ფასი 110 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `110.00`
- **Product Type:** `ჰუდი`
- **Tags:** `ოვერსაიზი`, `სპორტული`
- **Confirmed material:** `ბამბა` (80%), `პოლიესტერი` (20%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Heather gray oversized hoodie with kangaroo pocket on mannequin.
- **Choices:**
  - `Free size` / `ნაცრისფერი` / 3 / active (Low Stock)
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `gray` -> `ნაცრისფერი`, `oversized` -> `ოვერსაიზი`, `hoodie` -> `ჰუდი`, `oversize` -> `Free size`
- **Recognition/correction story:** Multi-fact candidate extraction from English adjectives.
- **Ready Reply scenario:** Complete reply for sporty/unisex category.
- **Demo purpose:** Demonstrates streetwear styling and blend composition.
- **Similar/family relationship:** Counterpart to D044.
- **Maintenance demo role:** NONE

---

### D012 — შავი წვეულების კაბა
- **Seller description:** `შავი საღამოს წვეულების კაბა (evening party dress black). ზომა Small და Medium. 100% პოლიესტერი. ფასი 130 ლარი.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `active`
- **Price:** `130.00`
- **Product Type:** `კაბა`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** `პოლიესტერი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Black evening mini dress with shimmer on dark studio backdrop.
- **Choices:**
  - `S` / `შავი` / 0 / active (Depleted)
  - `M` / `შავი` / 4 / active
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `evening` -> `სადღესასწაულო`, `dress` -> `კაბა`, `black` -> `შავი`, `small` -> `S`, negation `ar aris tetri`
- **Recognition/correction story:** Demonstrates negation handling (`ar aris tetri` suppresses white candidate).
- **Ready Reply scenario:** Shows partial stock (S=0, M=4).
- **Demo purpose:** Demonstrates chaotic input with negation protection.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D013 — ხორცისფერი აბრეშუმის ბლუზა
- **Seller description:** `ხორცისფერი ბლუზა 90ლ 1ცალი M`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `90.00`
- **Product Type:** `ბლუზა`
- **Tags:** None
- **Confirmed material:** `აბრეშუმი` (100%), source: `manual`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `M` / `ბეჟი` / 0 / active (Sold Out)
- **Intended availability:** `sold_out`
- **Intended readiness:** Fully structured but sold out
- **Alias/vocabulary demonstrated:** `ხორცისფერი` -> `ბეჟი`
- **Recognition/correction story:** Georgian colloquial color alias parsed correctly; stock was stepped down to 0.
- **Ready Reply scenario:** Shows 0 stock available.
- **Demo purpose:** Sold out single-variant product with Georgian color alias.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D014 — ბრჭყვიალა სადღესასწაულო ტოპი
- **Seller description:** `სადღესასწაულო party top ვერცხლისფერი დეტალებით. ზომა one size. ფასი 65.00 GEL.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `65.00`
- **Product Type:** `ტოპი`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** None
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Festive metallic shimmer sleeveless top on hanger.
- **Choices:**
  - `Free size` / `შავი` / 6 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `party` -> `სადღესასწაულო`, `top` -> `ტოპი`, `one size` -> `Free size`
- **Recognition/correction story:** Missing material fact triggers correction badge; links to `#material-section`.
- **Ready Reply scenario:** Emits note `CONFIRMED_MATERIAL_MISSING`.
- **Demo purpose:** Demonstrates missing material workflow with English size alias.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D015 — ვარდისფერი ატლასის ქვედაბოლო
- **Seller description:** `ელეგანტური ვარდისფერი (pink) ატლასის ქვედაბოლო (skirt). ზომები S, M, large. 100% პოლიესტერი. ფასი 95 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `95.00`
- **Product Type:** `ქვედაბოლო`
- **Tags:** `სადღესასწაულო`, `ყოველდღიური`
- **Confirmed material:** `პოლიესტერი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Pastel pink satin midi skirt on studio mannequin.
- **Choices:**
  - `S` / `ვარდისფერი` / 4 / active
  - `M` / `ვარდისფერი` / 0 / active (Depleted)
  - `L` / `ვარდისფერი` / 5 / active
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `pink` -> `ვარდისფერი`, `skirt` -> `ქვედაბოლო`, `large` -> `L`
- **Recognition/correction story:** Multi-size row with middle size depleted.
- **Ready Reply scenario:** S and L in stock, M out of stock.
- **Demo purpose:** Skirt category representation with partial depletion.
- **Similar/family relationship:** Counterpart to D037.
- **Maintenance demo role:** NONE

---

### D016 — თბილი ნაქსოვი სვიტერი
- **Seller description:** `ზამთრის თბილი ნაქსოვი სვიტერი (sweater), ფერი ბეჟი (beige). შემადგენლობა: 70% მატყლი, 30% აკრილი. ზომები S და M. ფასი 135 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `135.00`
- **Product Type:** `სვიტერი`
- **Tags:** `ზამთარი`
- **Confirmed material:** `მატყლი` (70%), `აკრილი` (30%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Chunky beige cable-knit wool sweater folded on rustic wooden bench.
- **Choices:**
  - `S` / `ბეჟი` / 2 / active (Low Stock)
  - `M` / `ბეჟი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `sweater` -> `სვიტერი`, `beige` -> `ბეჟი`
- **Recognition/correction story:** Dual-fiber blend composition with explicit percentages.
- **Ready Reply scenario:** Complete reply with low-stock flag on S.
- **Demo purpose:** Family F3 (Knitwear) anchor product.
- **Similar/family relationship:** Family F3
- **Maintenance demo role:** ADD_SIMILAR_SOURCE

---

### D017 — მწვანე ზაფხულის მაისური
- **Seller description:** `მწვანე green მაისური S 35ლ`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `35.00`
- **Product Type:** `მაისური`
- **Tags:** `ზაფხული`
- **Confirmed material:** `ბამბა` (100%), source: `manual`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `S` / `მწვანე` / 0 / active (Sold Out)
- **Intended availability:** `sold_out`
- **Intended readiness:** Fully structured but sold out
- **Alias/vocabulary demonstrated:** `green` -> `მწვანე`
- **Recognition/correction story:** Minimalist entry with single sold-out variant.
- **Ready Reply scenario:** Conveys 0 stock accurately.
- **Demo purpose:** Sold-out casual tee.
- **Similar/family relationship:** Basic Tees
- **Maintenance demo role:** NONE

---

### D018 — ყავისფერი შემოდგომის მოსაცმელი
- **Seller description:** `ყავისფერი (brown) თბილი მოსაცმელი ღილებით. 100% ბამბა. ზომა M და L. ფასი 125 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `125.00`
- **Product Type:** `ჟაკეტი`
- **Tags:** `ყოველდღიური`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Brown corduroy buttoned overshirt/jacket on mannequin.
- **Choices:**
  - `M` / `ყავისფერი` / 1 / active (Low Stock)
  - `L` / `ყავისფერი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `brown` -> `ყავისფერი`, `მოსაცმელი` -> `ჟაკეტი`
- **Recognition/correction story:** Georgian synonym for light jacket mapped to canonical `ჟაკეტი`.
- **Ready Reply scenario:** Shows M at 1 unit left, L at 4.
- **Demo purpose:** Demonstrates Georgian colloquial garment type recognition.
- **Similar/family relationship:** Outerwear
- **Maintenance demo role:** NONE

---

### D019 — მუქი ლურჯი ზამთრის პალტო
- **Seller description:** `კლასიკური გრძელი პალტო (coat), ფერი navy/ლურჯი. შემადგენლობა: 90% მატყლი, 10% პოლიესტერი. ზომები S, M, L. ფასი 280 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `280.00`
- **Product Type:** `პალტო`
- **Tags:** `ზამთარი`, `კლასიკური`, `პრემიუმი`
- **Confirmed material:** `მატყლი` (90%), `პოლიესტერი` (10%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Tailored long navy wool coat on studio mannequin.
- **Choices:**
  - `S` / `ლურჯი` / 3 / active (Low Stock)
  - `M` / `ლურჯი` / 4 / active
  - `L` / `ლურჯი` / 3 / active (Low Stock)
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `coat` -> `პალტო`, `navy` -> `ლურჯი`
- **Recognition/correction story:** Premium outerwear multi-tag classification.
- **Ready Reply scenario:** Complete premium product reply.
- **Demo purpose:** High-ticket winter outerwear anchor.
- **Similar/family relationship:** Counterpart to archived D048.
- **Maintenance demo role:** NONE

---

### D020 — კრემისფერი გრძელი კარდიგანი
- **Seller description:** `კრემისფერი (cream) რბილი კარდიგანი (cardigan), ზომა უნივერსალური. 80% მატყლი, 20% აკრილი. ფასი 145 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `145.00`
- **Product Type:** `კარდიგანი`
- **Tags:** `ყოველდღიური`, `ზამთარი`
- **Confirmed material:** `მატყლი` (80%), `აკრილი` (20%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Cream oversized long knit cardigan draped over armchair.
- **Choices:**
  - `Free size` / `კრემისფერი` / 2 / active (Low Stock)
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `cream` -> `კრემისფერი`, `cardigan` -> `კარდიგანი`, `უნივერსალური` -> `Free size`
- **Recognition/correction story:** Dual alias extraction for color and size.
- **Ready Reply scenario:** Low stock alert (2 units).
- **Demo purpose:** Family F3 member.
- **Similar/family relationship:** Family F3
- **Maintenance demo role:** NONE

---

### D021 — შავი ატლასის კაბა
- **Seller description:** `შავი black ატლასის კაბა, ზომები S და M. 100% ვისკოზა. ფასი 99 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `99.00`
- **Product Type:** `კაბა`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** `ვისკოზა` (100%), source: `description`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `S` / `შავი` / 0 / active (Depleted)
  - `M` / `შავი` / 5 / active
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `black` -> `შავი`
- **Recognition/correction story:** Distinct budget alternative to D001.
- **Ready Reply scenario:** Shows S depleted, M available.
- **Demo purpose:** Near-identical counterpart to D001 demonstrating distinct product identity.
- **Similar/family relationship:** Black Slip Dress Twins
- **Maintenance demo role:** NONE

---

### D022 — ნაცრისფერი კლასიკური შარვალი
- **Seller description:** `კლასიკური ნაცრისფერი (grey) შარვალი (trousers), casual სტილი. ზომები S, M, L. ფასი 115 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `115.00`
- **Product Type:** `შარვალი`
- **Tags:** `კლასიკური`, `ყოველდღიური`
- **Confirmed material:** None
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Charcoal gray tailored wool-blend trousers on mannequin.
- **Choices:**
  - `S` / `ნაცრისფერი` / 4 / active
  - `M` / `ნაცრისფერი` / 6 / active
  - `L` / `ნაცრისფერი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `grey` -> `ნაცრისფერი`, `trousers` -> `შარვალი`, `casual` -> `ყოველდღიური`
- **Recognition/correction story:** Recognizes British spelling `grey`. Missing material prompts correction.
- **Ready Reply scenario:** Emits seller note `CONFIRMED_MATERIAL_MISSING`.
- **Demo purpose:** Family F1 member with missing material state.
- **Similar/family relationship:** Family F1
- **Maintenance demo role:** NONE

---

### D023 — ზეთისხილისფერი თეთრეულის ორეული
- **Seller description:** `ზაფხულის ზეთისხილისფერი (olive) თეთრეულის ორეული (set) — პერანგი და შორტი. ზომები S და M. 100% თეთრეული/სელი. ფასი 165 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `165.00`
- **Product Type:** `ორეული`
- **Tags:** `ზაფხული`, `ყოველდღიური`
- **Confirmed material:** `თეთრეული/სელი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Olive green relaxed linen two-piece shirt and shorts set on mannequin.
- **Choices:**
  - `S` / `ზეთისხილისფერი` / 3 / active (Low Stock)
  - `M` / `ზეთისხილისფერი` / 5 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `olive` -> `ზეთისხილისფერი`, `set` -> `ორეული`
- **Recognition/correction story:** Multi-piece set category parsing.
- **Ready Reply scenario:** Complete reply for two-piece suit.
- **Demo purpose:** Demonstrates two-piece set category and linen composition.
- **Similar/family relationship:** Counterpart to D049.
- **Maintenance demo role:** NONE

---

### D024 — თეთრი ორგანული მაისური
- **Seller description:** `თეთრი white მაისური basic S M 55ლ`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `55.00`
- **Product Type:** `მაისური`
- **Tags:** `ბაზური`
- **Confirmed material:** `ბამბა` (95%), `ელასტანი` (5%), source: `manual`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `S` / `თეთრი` / 6 / active
  - `M` / `თეთრი` / 8 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `white` -> `თეთრი`, `basic` -> `ბაზური`
- **Recognition/correction story:** Near-identical counterpart to D009 with distinct supplier pricing.
- **Ready Reply scenario:** Standard clean reply.
- **Demo purpose:** Basic White Tee Pair member.
- **Similar/family relationship:** Basic White Tee Pair
- **Maintenance demo role:** NONE

---

### D025 — ლურჯი ზოლიანი პერანგი
- **Seller description:** `ლურჯი ზოლიანი shirt, ოვერსაიზი (oversize) სტილი. 100% ბამბა. ზომები S, M, L. ფასი 95 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `95.00`
- **Product Type:** `პერანგი`
- **Tags:** `ყოველდღიური`, `ოვერსაიზი`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Blue and white striped oversized poplin shirt on hanger.
- **Choices:**
  - `S` / `ლურჯი` / 2 / active (Low Stock)
  - `M` / `ლურჯი` / 5 / active
  - `L` / `ლურჯი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `shirt` -> `პერანგი`, `oversize` -> `Free size` / `ოვერსაიზი`
- **Recognition/correction story:** Oversize tag candidate extracted alongside shirt type.
- **Ready Reply scenario:** Complete reply showing low stock on S.
- **Demo purpose:** Demonstrates button-down shirt category variation.
- **Similar/family relationship:** Counterpart to D007.
- **Maintenance demo role:** NONE

---

### D026 — ღია ლურჯი სწორი ჯინსი
- **Seller description:** `ღია ლურჯი (blue) ჯინსი, სწორი ჭრა. ზომები Small და M. 100% ბამბა. ფასი 130 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `130.00`
- **Product Type:** `ჯინსი`
- **Tags:** `ყოველდღიური`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Light blue wash straight-fit denim jeans on studio mannequin.
- **Choices:**
  - `S` / `ლურჯი` / 0 / active (Depleted)
  - `M` / `ლურჯი` / 4 / active
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `blue` -> `ლურჯი`, `Small` -> `S`
- **Recognition/correction story:** Family F4 denim member.
- **Ready Reply scenario:** Informs buyer S is sold out, M has 4 left.
- **Demo purpose:** Family F4 (Denim) member.
- **Similar/family relationship:** Family F4
- **Maintenance demo role:** NONE

---

### D027 — წითელი საზეიმო აბრეშუმის ტოპი
- **Seller description:** `წითელი red საზეიმო ტოპი. ზომა S და M. ფასი 75 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `75.00`
- **Product Type:** `ტოპი`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** None
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Crimson red silk halter-neck top on hanger.
- **Choices:**
  - `S` / `წითელი` / 3 / active (Low Stock)
  - `M` / `წითელი` / 5 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `red` -> `წითელი`, `საზეიმო` -> `სადღესასწაულო`
- **Recognition/correction story:** Missing material prompts `#material-section` correction.
- **Ready Reply scenario:** Emits note `CONFIRMED_MATERIAL_MISSING`.
- **Demo purpose:** Festive category item missing material.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D028 — შავი ორბორტიანი პალტო-ჟაკეტი
- **Seller description:** `შავი კლასიკური jacket ორბორტიანი ღილებით. 80% მატყლი, 20% პოლიესტერი. ზომა M. ფასი 210 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `210.00`
- **Product Type:** `ჟაკეტი`
- **Tags:** `კლასიკური`, `პრემიუმი`
- **Confirmed material:** `მატყლი` (80%), `პოლიესტერი` (20%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Black double-breasted structured wool jacket on mannequin.
- **Choices:**
  - `M` / `შავი` / 0 / active (Sold Out)
- **Intended availability:** `sold_out`
- **Intended readiness:** Fully structured but sold out
- **Alias/vocabulary demonstrated:** `jacket` -> `ჟაკეტი`
- **Recognition/correction story:** Premium tailored jacket exhausted from past sales.
- **Ready Reply scenario:** Accurately states 0 stock.
- **Demo purpose:** High-ticket sold-out item triggering dashboard attention.
- **Similar/family relationship:** Outerwear
- **Maintenance demo role:** NONE

---

### D029 — ყავისფერი ნაქსოვი ჟაკეტი
- **Seller description:** `ყავისფერი brown ჟაკეტი ზომა M L 100% ბამბა`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** None
- **Product Type:** `ჟაკეტი`
- **Tags:** `ყოველდღიური`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `M` / `ყავისფერი` / 4 / active
  - `L` / `ყავისფერი` / 5 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing price only
- **Alias/vocabulary demonstrated:** `brown` -> `ყავისფერი`
- **Recognition/correction story:** Hurried seller upload omitted price; flags `#id_price` deep-link correction.
- **Ready Reply scenario:** Emits seller note `PRICE_MISSING` and suppresses price line in buyer text.
- **Demo purpose:** Primary Active demo for missing price state.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D030 — მწვანე აბრეშუმის პერანგი
- **Seller description:** `მწვანე (green) აბრეშუმის პერანგი. ზომა Medium. 100% აბრეშუმი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** None
- **Product Type:** `პერანგი`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** `აბრეშუმი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Emerald green long-sleeve silk blouse/shirt on mannequin.
- **Choices:**
  - `M` / `მწვანე` / 3 / active (Low Stock)
- **Intended availability:** `available`
- **Intended readiness:** Missing price only
- **Alias/vocabulary demonstrated:** `green` -> `მწვანე`, `Medium` -> `M`
- **Recognition/correction story:** Complete physical specs, price pending supplier invoice.
- **Ready Reply scenario:** Shows available stock (3) but omits price with seller alert.
- **Demo purpose:** Demonstrates missing price warning on high-value silk item.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D031 — თეთრი პრინტიანი მაისური
- **Seller description:** `თეთრი მაისური პრინტით (white t-shirt). ყოველდღიური საბაზისო სტილი (casual basic). ზომები S და M. 100% ბამბა. ფასი 40 ლარი.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `active`
- **Price:** `40.00`
- **Product Type:** `მაისური`
- **Tags:** `ყოველდღიური`, `ბაზური`
- **Confirmed material:** None
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** White graphic print t-shirt laid flat on marble surface.
- **Choices:**
  - `S` / `თეთრი` / 5 / active
  - `M` / `თეთრი` / 6 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only (word `bamba` in Latin text unconfirmed)
- **Alias/vocabulary demonstrated:** `white` -> `თეთრი`, `t-shirt` -> `მაისური`, `casual` -> `ყოველდღიური`, `basic` -> `ბაზური`
- **Recognition/correction story:** Demonstrates Latin shorthand recognition while material remains unconfirmed.
- **Ready Reply scenario:** Emits seller note `CONFIRMED_MATERIAL_MISSING`.
- **Demo purpose:** Demonstrates assistant caution (Latin material not auto-assumed as truth).
- **Similar/family relationship:** Basic Tees
- **Maintenance demo role:** NONE

---

### D032 — ხორცისფერი ნაქსოვი ტოპი
- **Seller description:** `ხორცისფერი ტოპი free size 45ლ`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `45.00`
- **Product Type:** `ტოპი`
- **Tags:** `ზაფხული`
- **Confirmed material:** `ბამბა` (100%), source: `manual`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `Free size` / `ბეჟი` / 0 / active (Sold Out)
- **Intended availability:** `sold_out`
- **Intended readiness:** Fully structured but sold out
- **Alias/vocabulary demonstrated:** `ხორცისფერი` -> `ბეჟი`
- **Recognition/correction story:** Georgian colloquial color alias parsed; stock stepped down to 0.
- **Ready Reply scenario:** States 0 stock.
- **Demo purpose:** Sold-out summer knit top.
- **Similar/family relationship:** NONE
- **Maintenance demo role:** NONE

---

### D033 — ბეჟი ოვერსაიზ სვიტერი (Duplicate Choice Demo)
- **Seller description:** `ბეჟი beige oversize სვიტერი, ზომა one size. 100% მატყლი. ფასი 140 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `140.00`
- **Product Type:** `სვიტერი`
- **Tags:** `ოვერსაიზი`, `ზამთარი`
- **Confirmed material:** `მატყლი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Oversized beige wool turtleneck sweater on hanger.
- **Choices:**
  - `Free size` / `ბეჟი` / 2 / active (Row 1, Low Stock)
  - `Free size` / `ბეჟი` / 1 / active (Row 2, duplicate size/color pair, Low Stock)
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `beige` -> `ბეჟი`, `one size` -> `Free size`
- **Recognition/correction story:** Seller added two separate warehouse rows for the same size/color.
- **Ready Reply scenario:** Emits seller warning `ReadyReplyNoteCode.DUPLICATE_CHOICE_AMBIGUITY` with choice IDs.
- **Demo purpose:** Golden demo for duplicate choice row disambiguation note.
- **Similar/family relationship:** Family F3
- **Maintenance demo role:** NONE

---

### D034 — ზეთისხილისფერი თეთრეულის სარაფანი
- **Seller description:** `ზეთისხილისფერი (olive) მსუბუქი სარაფანი ზაფხულისთვის. ზომები S და M. 100% თეთრეული/სელი. ფასი 90 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `90.00`
- **Product Type:** `კაბა`
- **Tags:** `ზაფხული`
- **Confirmed material:** `თეთრეული/სელი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Olive green linen sleeveless midi sundress on hanger.
- **Choices:**
  - `S` / `ზეთისხილისფერი` / 1 / active (Low Stock)
  - `M` / `ზეთისხილისფერი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `olive` -> `ზეთისხილისფერი`, `სარაფანი` -> `კაბა`
- **Recognition/correction story:** Family F2 member with low stock on S.
- **Ready Reply scenario:** S at 1 left, M at 4.
- **Demo purpose:** Family F2 (Linen Sundresses) member.
- **Similar/family relationship:** Family F2
- **Maintenance demo role:** NONE

---

### D035 — ნაცრისფერი სპორტული შარვალი
- **Seller description:** `ნაცრისფერი (gray) თავისუფალი შარვალი ყოველდღიური ჩაცმისთვის. ზომები S, M, Large. 100% ბამბა. ფასი 85 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `85.00`
- **Product Type:** `შარვალი`
- **Tags:** `სპორტული`, `ყოველდღიური`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Gray cotton relaxed-fit jogger pants on hanger.
- **Choices:**
  - `S` / `ნაცრისფერი` / 4 / active
  - `M` / `ნაცრისფერი` / 0 / active (Depleted)
  - `L` / `ნაცრისფერი` / 5 / active
- **Intended availability:** `partially_sold_out`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `gray` -> `ნაცრისფერი`, `Large` -> `L`
- **Recognition/correction story:** Partial stock with middle size exhausted.
- **Ready Reply scenario:** Clear stock delineation in reply.
- **Demo purpose:** Casual lounge pants in partial stock.
- **Similar/family relationship:** Bottoms
- **Maintenance demo role:** NONE

---

### D036 — შავი სწორი ჯინსი
- **Seller description:** `შავი jeans 36 S 125ლ`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `125.00`
- **Product Type:** `ჯინსი`
- **Tags:** `ყოველდღიური`
- **Confirmed material:** `ბამბა` (98%), `ელასტანი` (2%), source: `manual`
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `36` / `შავი` / 4 / active
  - `S` / `შავი` / 5 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `jeans` -> `ჯინსი`, numeric size `36`
- **Recognition/correction story:** Family F4 black denim variation.
- **Ready Reply scenario:** Standard clean reply.
- **Demo purpose:** Family F4 (Denim) member.
- **Similar/family relationship:** Family F4
- **Maintenance demo role:** NONE

---

### D037 — თეთრი თეთრეულის ქვედაბოლო (Draft Intake)
- **Seller description:** `თეთრი თეთრეულის skirt ზაფხულისთვის. ზომები და ფასი დასაზუსტებელია.`
- **Seller style:** NORMAL
- **Lifecycle:** `draft`
- **Price:** None
- **Product Type:** `ქვედაბოლო`
- **Tags:** `ზაფხული`
- **Confirmed material:** None
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:** (None — zero-choice Draft)
- **Intended availability:** `sold_out` (computed unavailable for Draft)
- **Intended readiness:** Multiple facts missing (price, choices, material)
- **Alias/vocabulary demonstrated:** `skirt` -> `ქვედაბოლო`
- **Recognition/correction story:** Demonstrates newly initiated seller intake draft before choice or price entry.
- **Ready Reply scenario:** Blocked in Draft (or warns choices and price missing).
- **Demo purpose:** Zero-choice Draft intake demonstration.
- **Similar/family relationship:** Family F2 counterpart
- **Maintenance demo role:** NONE

---

### D038 — შავი კლასიკური შარვალი (Draft Intake)
- **Seller description:** `შავი black pants classic 110ლ`
- **Seller style:** LAZY
- **Lifecycle:** `draft`
- **Price:** `110.00`
- **Product Type:** None (unconfirmed classification)
- **Tags:** `კლასიკური`
- **Confirmed material:** None
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `M` / `შავი` / 0 / active
- **Intended availability:** `sold_out` (computed unavailable for Draft)
- **Intended readiness:** Missing Product Type and Material
- **Alias/vocabulary demonstrated:** `black` -> `შავი`, `pants` -> `შარვალი`, `classic` -> `კლასიკური`
- **Recognition/correction story:** Candidate `შარვალი` recognized from `pants` but unconfirmed by seller; prompts `#classification-section`.
- **Ready Reply scenario:** Surfaced in missing information dashboard list.
- **Demo purpose:** Demonstrates unconfirmed type classification workflow.
- **Similar/family relationship:** Family F1 member
- **Maintenance demo role:** NONE

---

### D039 — ბეჟი ნაქსოვი კარდიგანი (Draft Work-in-Progress)
- **Seller description:** `თბილი ზამთრის ბეჟი კარდიგანი (beige sweater cardigan). ზომები S და M. 100% მატყლი. ფასი გასარკვევია.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `draft`
- **Price:** None
- **Product Type:** `კარდიგანი`
- **Tags:** `ზამთარი`
- **Confirmed material:** `მატყლი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Beige knit cardigan flat lay on wooden floor.
- **Choices:**
  - `S` / `ბეჟი` / 3 / active
  - `M` / `ბეჟი` / 4 / active
- **Intended availability:** `sold_out` (computed unavailable for Draft)
- **Intended readiness:** Missing price only
- **Alias/vocabulary demonstrated:** `beige` -> `ბეჟი`, `cardigan` -> `კარდიგანი`
- **Recognition/correction story:** Draft with confirmed choices and material but missing price.
- **Ready Reply scenario:** Draft preview shows missing price alert.
- **Demo purpose:** Demonstrates Draft ready for price confirmation and activation.
- **Similar/family relationship:** Family F3
- **Maintenance demo role:** NONE

---

### D040 — ოვერსაიზ კოტონის პერანგი (Draft Work-in-Progress)
- **Seller description:** `თეთრი ოვერსაიზ პერანგი (oversized rubashka). ზომა Medium. 100% ბამბა.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `draft`
- **Price:** None
- **Product Type:** `პერანგი`
- **Tags:** `ოვერსაიზი`
- **Confirmed material:** None
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Crisp white oversized boyfriend shirt hanging on studio rack.
- **Choices:**
  - `M` / `თეთრი` / 5 / active
- **Intended availability:** `sold_out` (computed unavailable for Draft)
- **Intended readiness:** Missing price and material
- **Alias/vocabulary demonstrated:** `rubashka` -> `პერანგი`, `oversized` -> `ოვერსაიზი`, `medium` -> `M`
- **Recognition/correction story:** Colloquial Georgian/Russian loanword `რუბაშკა` recognized into canonical `პერანგი`.
- **Ready Reply scenario:** Missing price and material notes.
- **Demo purpose:** Demonstrates slang loanword alias recognition.
- **Similar/family relationship:** Shirts
- **Maintenance demo role:** NONE

---

### D041 — ვარდისფერი ატლასის ქვედაბოლო (Draft Work-in-Progress)
- **Seller description:** `ვარდისფერი ქვედაბოლო (pink iubka), ზომა Large, 80ლ`
- **Seller style:** LAZY
- **Lifecycle:** `draft`
- **Price:** `80.00`
- **Product Type:** `ქვედაბოლო`
- **Tags:** None
- **Confirmed material:** None
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `L` / `ვარდისფერი` / 2 / active
- **Intended availability:** `sold_out` (computed unavailable for Draft)
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `pink` -> `ვარდისფერი`, `iubka` -> `ქვედაბოლო`, `large` -> `L`
- **Recognition/correction story:** Colloquial loanword `იუბკა` maps to `ქვედაბოლო`.
- **Ready Reply scenario:** Draft item awaiting activation.
- **Demo purpose:** Demonstrates colloquial skirt alias.
- **Similar/family relationship:** Counterpart to D015
- **Maintenance demo role:** NONE

---

### D042 — საზაფხულო ტოპი (Draft Zero-Choice)
- **Seller description:** `საზაფხულო ტოპი (summer top), ზომა one size`
- **Seller style:** LAZY
- **Lifecycle:** `draft`
- **Price:** None
- **Product Type:** None
- **Tags:** `ზაფხული`
- **Confirmed material:** None
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:** (None — zero-choice Draft)
- **Intended availability:** `sold_out` (computed unavailable for Draft)
- **Intended readiness:** Missing price, choices, classification, material
- **Alias/vocabulary demonstrated:** `top` -> `ტოპი`, `one size` -> `Free size`
- **Recognition/correction story:** Minimalist shell awaiting seller completion.
- **Ready Reply scenario:** Fully unanswerable draft.
- **Demo purpose:** Second zero-choice Draft intake item.
- **Similar/family relationship:** Tops
- **Maintenance demo role:** NONE

---

### D043 — შავი საღამოს კაბა (Duplicate Choice Active)
- **Seller description:** `შავი საღამოს კაბა (evening black dress). ზომები Small და Medium. 100% პოლიესტერი. ფასი 120 ლარი.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `active`
- **Price:** `120.00`
- **Product Type:** `კაბა`
- **Tags:** `სადღესასწაულო`
- **Confirmed material:** `პოლიესტერი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Fitted black evening cocktail dress on mannequin.
- **Choices:**
  - `S` / `შავი` / 3 / active (Row 1, Low Stock)
  - `S` / `შავი` / 2 / active (Row 2, duplicate size/color pair, Low Stock)
  - `M` / `შავი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `evening` -> `სადღესასწაულო`, `black` -> `შავი`, `dress` -> `კაბა`, `small` -> `S`
- **Recognition/correction story:** Multiple choices with identical S/Black variants.
- **Ready Reply scenario:** Surfaced with `ReadyReplyNoteCode.DUPLICATE_CHOICE_AMBIGUITY`.
- **Demo purpose:** Second active demo for duplicate choice ambiguity.
- **Similar/family relationship:** Evening Dresses
- **Maintenance demo role:** NONE

---

### D044 — ნაცრისფერი სპორტული ჰუდი
- **Seller description:** `ნაცრისფერი სპორტული ჰუდი (gray oversized hoodie). 100% ბამბა (არ არის სინთეტიკა). ზომა oversize. ფასი 95 ლარი.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `active`
- **Price:** `95.00`
- **Product Type:** `ჰუდი`
- **Tags:** `ოვერსაიზი`, `სპორტული`
- **Confirmed material:** None
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Gray fleece sportswear hoodie on studio hanger.
- **Choices:**
  - `Free size` / `ნაცრისფერი` / 5 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `gray` -> `ნაცრისფერი`, `oversized` -> `ოვერსაიზი`, `hoodie` -> `ჰუდი`, `oversize` -> `Free size`
- **Recognition/correction story:** Negation `ar aris sintetika` suppresses synthetic material candidates.
- **Ready Reply scenario:** Emits seller note `CONFIRMED_MATERIAL_MISSING`.
- **Demo purpose:** Demonstrates negation filtering in chaotic input.
- **Similar/family relationship:** Counterpart to D011
- **Maintenance demo role:** NONE

---

### D045 — წითელი საგაზაფხულო მოსაცმელი
- **Seller description:** `წითელი red მოსაცმელი საგაზაფხულო. ზომა M. ფასი 110 ლარი.`
- **Seller style:** NORMAL
- **Lifecycle:** `active`
- **Price:** `110.00`
- **Product Type:** `ჟაკეტი`
- **Tags:** `საგაზაფხულო`
- **Confirmed material:** None
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Red lightweight cotton utility jacket on mannequin.
- **Choices:**
  - `M` / `წითელი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `red` -> `წითელი`, `მოსაცმელი` -> `ჟაკეტი`
- **Recognition/correction story:** Georgian synonym for outerwear mapped to canonical jacket.
- **Ready Reply scenario:** Complete except missing material note.
- **Demo purpose:** Demonstrates Georgian descriptive terms.
- **Similar/family relationship:** Outerwear
- **Maintenance demo role:** NONE

---

### D046 — თეთრი საბაზისო მაისური
- **Seller description:** `white tee basic M 35ლ`
- **Seller style:** LAZY
- **Lifecycle:** `active`
- **Price:** `35.00`
- **Product Type:** `მაისური`
- **Tags:** `ბაზური`
- **Confirmed material:** None
- **Media:** `NO_IMAGE`
- **Media brief:** (No image placeholder demo).
- **Choices:**
  - `M` / `თეთრი` / 8 / active
- **Intended availability:** `available`
- **Intended readiness:** Missing material only
- **Alias/vocabulary demonstrated:** `white` -> `თეთრი`, `tee` -> `მაისური`, `basic` -> `ბაზური`
- **Recognition/correction story:** Demonstrates English shorthand `tee` -> `მაისური`.
- **Ready Reply scenario:** Emits note `CONFIRMED_MATERIAL_MISSING`.
- **Demo purpose:** English shorthand alias demonstration.
- **Similar/family relationship:** Basic Tees
- **Maintenance demo role:** NONE

---

### D047 — კრემისფერი თბილი კარდიგანი
- **Seller description:** `თბილი კრემისფერი (cream) cardigan ზამთრისთვის. ზომა უნივერსალური. შემადგენლობა: 70% მატყლი, 30% აკრილი. ფასი 150 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `active`
- **Price:** `150.00`
- **Product Type:** `კარდიგანი`
- **Tags:** `ზამთარი`, `ყოველდღიური`
- **Confirmed material:** `მატყლი` (70%), `აკრილი` (30%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Heavy knit cream cardigan with horn buttons on wooden hanger.
- **Choices:**
  - `Free size` / `კრემისფერი` / 4 / active
- **Intended availability:** `available`
- **Intended readiness:** Fully answer-ready
- **Alias/vocabulary demonstrated:** `cream` -> `კრემისფერი`, `cardigan` -> `კარდიგანი`, `უნივერსალური` -> `Free size`
- **Recognition/correction story:** Complete structured data for knitwear.
- **Ready Reply scenario:** Standard clean reply.
- **Demo purpose:** Family F3 member.
- **Similar/family relationship:** Family F3
- **Maintenance demo role:** NONE

---

### D048 — მუქი ლურჯი შალის პალტო (Archived Inventory)
- **Seller description:** `ძველი კოლექციის navy/ლურჯი პალტო (coat). 100% მატყლი. ზომები M და L. ფასი 260 ლარი.`
- **Seller style:** DETAILED
- **Lifecycle:** `archived`
- **Price:** `260.00`
- **Product Type:** `პალტო`
- **Tags:** `ზამთარი`, `კლასიკური`
- **Confirmed material:** `მატყლი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Dark navy wool trench-style coat on studio mannequin.
- **Choices:**
  - `M` / `ლურჯი` / 1 / active
  - `L` / `ლურჯი` / 2 / active
- **Intended availability:** `sold_out` (computed unavailable for Archived)
- **Intended readiness:** Blocked from Ready Reply in Archived state
- **Alias/vocabulary demonstrated:** `coat` -> `პალტო`, `navy` -> `ლურჯი`
- **Recognition/correction story:** Archived product preserving past choices and material facts.
- **Ready Reply scenario:** Blocked by domain validation (`Archived Products cannot produce a Ready Reply`).
- **Demo purpose:** Primary candidate for Restore-to-Draft demonstration.
- **Similar/family relationship:** Family F3 / Outerwear
- **Maintenance demo role:** ARCHIVE_RESTORE

---

### D049 — ზეთისხილისფერი ზაფხულის ორეული (Archived Inventory)
- **Seller description:** `გასული სეზონის ზეთისხილისფერი ორეული (olive set). 100% თეთრეული/სელი. ზომა M. ფასი 150 ლარი.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `archived`
- **Price:** `150.00`
- **Product Type:** `ორეული`
- **Tags:** `ზაფხული`
- **Confirmed material:** `თეთრეული/სელი` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Olive green linen two-piece resort set on mannequin.
- **Choices:**
  - `M` / `ზეთისხილისფერი` / 0 / active
- **Intended availability:** `sold_out` (computed unavailable for Archived)
- **Intended readiness:** Blocked from Ready Reply in Archived state
- **Alias/vocabulary demonstrated:** `olive` -> `ზეთისხილისფერი`, `set` -> `ორეული`
- **Recognition/correction story:** Out-of-season set retired to archived tab.
- **Ready Reply scenario:** Blocked in Archived state.
- **Demo purpose:** Secondary candidate for Restore-to-Draft demonstration.
- **Similar/family relationship:** Counterpart to D023
- **Maintenance demo role:** ARCHIVE_RESTORE

---

### D050 — შავი სპორტული ჰუდი (Archived Inventory)
- **Seller description:** `ძველი მოდელის შავი ჰუდი (black hoodie). 100% ბამბა. ზომა L. ფასი 80 ლარი.`
- **Seller style:** CHAOTIC
- **Lifecycle:** `archived`
- **Price:** `80.00`
- **Product Type:** `ჰუდი`
- **Tags:** `სპორტული`
- **Confirmed material:** `ბამბა` (100%), source: `description`
- **Media:** `WITH_PRIMARY_IMAGE`
- **Media brief:** Black oversized cotton hoodie with drawstrings on hanger.
- **Choices:**
  - `L` / `შავი` / 0 / active
- **Intended availability:** `sold_out` (computed unavailable for Archived)
- **Intended readiness:** Blocked from Ready Reply in Archived state
- **Alias/vocabulary demonstrated:** `black` -> `შავი`, `hoodie` -> `ჰუდი`
- **Recognition/correction story:** Archived fleece hoodie with 0 stock.
- **Ready Reply scenario:** Blocked in Archived state.
- **Demo purpose:** Demonstrates catalog hygiene for discontinued streetwear.
- **Similar/family relationship:** Streetwear
- **Maintenance demo role:** ARCHIVE_RESTORE

---

## 8. Demo Workflow Targets

During hosted portfolio walkthroughs or automated recording, use these exact Product IDs to showcase system features:

- **Recognition Demonstration (Semantic candidate extraction):** `D001`, `D007`, `D011`, `D016`.
- **Alias Recognition (Georgian & Latin synonyms):** `D002` (`bordeaux`), `D006` (`pants`, `Large`), `D010` (`სარაფანი`, `უნივერსალური`), `D018` (`მოსაცმელი`), `D040` (`რუბაშკა`).
- **Negation Filtering in Descriptions:** `D012` (`ar aris tetri`), `D044` (`ar aris sintetika`).
- **Lazy Description Capture:** `D005`, `D009`, `D017`, `D024`, `D029`, `D038`.
- **Chaotic Description Capture:** `D012`, `D031`, `D039`, `D040`, `D043`, `D044`.
- **Complete Answer-Ready Ready Reply:** `D001`, `D007`, `D010`, `D016`, `D019`, `D023`.
- **Missing Price Warning in Ready Reply (`PRICE_MISSING`):** `D029`, `D030`.
- **Missing Material Warning in Ready Reply (`CONFIRMED_MATERIAL_MISSING`):** `D005`, `D014`, `D022`, `D027`, `D031`, `D044`.
- **Low Stock Attention Alert (qty <= 3):** `D002` (S=2), `D003` (M=3), `D006` (S=3), `D010` (Free size=2), `D011` (Free size=3), `D016` (S=2), `D018` (M=1), `D020` (Free size=2), `D025` (S=2), `D033` (Free size=2, Free size=1), `D034` (S=1), `D043` (S=3, S=2).
- **Partially Sold Out Alert (Choice = 0 while Product available):** `D003`, `D006`, `D008`, `D012`, `D015`, `D021`, `D026`, `D035`.
- **Fully Sold Out Alert (All choices = 0):** `D004`, `D013`, `D017`, `D028`, `D032`.
- **Direct Stock Stepper (+1 / -1 Audit Fact):** Any choice on `D001` or `D006`.
- **Add Similar Workflow (Copy structure to Draft):** Use `D001`, `D006`, or `D016` as source.
- **Archive & Restore-to-Draft Workflow:** Inspect `D048`, `D049`, or `D050` in the archived workspace, click *Restore to Draft*, and observe safe reactivation.
- **Zero-Choice Incomplete Drafts:** `D037`, `D042`.
- **Duplicate-Looking Choice Disambiguation:** `D033` (two Free size / Beige rows) and `D043` (two S / Black rows) triggering `ReadyReplyNoteCode.DUPLICATE_CHOICE_AMBIGUITY`.

---

## 9. P13.3 Seeding Contract

When Phase 13 implements hosted portfolio seeding (P13.3), the seed routine must satisfy the following contractual guarantees:

1. **Exact Cardinality:** The database must contain exactly 50 Product records for the demo business (`Seller Studio`) after execution.
2. **Deterministic Baseline:** Running `demo_lifecycle reseed --confirm` must wipe previous residue and recreate the exact 50 products, choices, adjustments, materials, vocabularies, and aliases defined in this blueprint.
3. **Vocabulary & Aliases:** All 14 Product Types, 10 Tags, 8 Sizes, 12 Colors, and 50+ aliases specified in Section 4 must be initialized.
4. **Primary Media Generation:** For each product marked `WITH_PRIMARY_IMAGE` (36 products), a safe synthetic PNG/JPEG image matching the visual brief must be deterministically attached in tenant storage (`products/{business_id}/{product_id}/...`). The 14 products marked `NO_IMAGE` must have no `ProductMedia` record.
5. **Inventory Audit Ledger:** Initial positive quantities must be recorded via `initialize_choice_quantity` so that `InventoryAdjustment` records exist and choices have clean provenance.
6. **No Real Customer Data:** Every name, description, and price must remain completely synthetic.

---

## 10. Integrity Checklist

- [x] **Product Count:** Exactly 50 Products (D001 to D050). No missing or duplicate IDs.
- [x] **Lifecycles:** 41 Active, 6 Draft, 3 Archived. All within `Product.Lifecycle` enum.
- [x] **Availability:** Exactly 28 Available, 8 Partially Sold Out, 5 Sold Out among Active products. Draft and Archived products are not available.
- [x] **Readiness:** Computed strictly from facts (Price, Stock, Choice, Type, Material). No percentage scores.
- [x] **Active Product Rules:** Every Active product has at least one active `ProductChoice`.
- [x] **Draft Zero-Choice Rules:** D037 and D042 are explicitly defined with zero choices.
- [x] **Price Constraints:** All defined prices are > 0.00 (`DecimalField`). Missing prices are explicitly `None`. No zero or negative prices.
- [x] **Stock Constraints:** All choice quantities are integers >= 0. No product-level stock invented.
- [x] **Duplicate Choice Rows:** D033 and D043 maintain separate choice primary keys for duplicate `(size, color)` pairs, triggering Ready Reply ambiguity notes.
- [x] **Vocabulary Scoping:** All types, tags, sizes, and colors are scoped to Business ID 1.
- [x] **Alias Integrity:** All aliases in descriptions map strictly to defined canonical entries in Section 4.5.
- [x] **Single Image Guardrail:** Every product specifies either `WITH_PRIMARY_IMAGE` or `NO_IMAGE`. Zero multi-image galleries.
- [x] **Anti-Scope Creep:** No body measurements, no carts/orders, no storefront, no messaging APIs, no LLM commercial truth.
- [x] **Seller Realism:** Demonstrates authentic social seller variation from chaotic Georgian shorthand to meticulous boutique descriptions.
