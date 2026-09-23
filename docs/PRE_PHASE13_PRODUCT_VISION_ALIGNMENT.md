# Product Vision Alignment Review

**Date:** March 2025  
**Target Repository:** `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP`  
**Authorities:** `docs/PROJECT_BIBLE.md` (durable product truth), `docs/PRE_DEPLOYMENT_CODE_UX_INVENTORY.md` (audit baseline), `docs/PRE_PHASE13_REMAINING_WORK_ANALYSIS.md` (improvement analysis).  
**Purpose:** High-level strategic and product-design alignment to demonstrate full comprehension of the core product thesis, operating model, information architecture, and seller ergonomics before authoring `docs/REMAINING_RELEASE_PLAN.md`.

---

## 1. Product Identity

### What This Product Is
This product is a **Solo Seller Operating Assistant** for micro-apparel merchants in Georgia who sell primarily through social media messaging channels (Instagram Direct, Facebook Messenger, and WhatsApp). It acts as an ultra-fast, live companion tool that lives in a mobile or desktop browser tab alongside chat windows. It ingests messy, unstructured Georgian product descriptions, extracts structured attributes (sizes, colors, fiber materials, product types) using conservative deterministic heuristics, provides instant in-place stock updates, evaluates factual buyer-readiness, and generates 1-click copyable Georgian chat responses ("მზა პასუხი") with zero artificial hallucination.

### What This Product Is NOT
- **It is NOT an ERP:** It has no supplier purchasing orders, warehouse bin locations, general ledgers, tax compliance modules, depreciation tables, or role-based multi-department permissions.
- **It is NOT an Ecommerce Storefront:** There is no public customer-facing catalog, no buyer shopping cart, no checkout gateway, and no customer account portal (`active != published`).
- **It is NOT a Generic Database Admin Panel:** It does not force the seller to act as a data-entry clerk filling out 20 required database fields before an item can be saved.
- **It is NOT a Chatbot / Autonomous Agent:** It does not send messages autonomously via Meta APIs, nor does it let an LLM invent prices, fit advice, or fabric claims.

### The Concrete Problem It Solves
Social media apparel sellers in Georgia manage inventory in physical notebooks, phone note apps, or chaotic chat threads. When an Instagram buyer asks *"Do you have this black dress in M and what is it made of?"*, the seller must stop chatting, physically search clothing racks or scroll through endless photo albums, mentally calculate remaining stock, and manually type out the price, sizing, and fabric details in Georgian. This process is slow, leads to overselling out-of-stock items, causes lost sales due to delayed response times, and results in embarrassing customer conflicts.

### Why a Seller Keeps It Open All Day
Because it is their **fastest path to answering customer messages and recording closed sales**. It turns a 2-minute interruption into a 3-second lookup, copy, and stock decrement.

---

## 2. Primary User

- **Business Scale & Operation:** A solo operator (or small family duo) running a boutique or reselling clothing via Instagram/Facebook. They manage between 20 and 300 active unique clothing styles at any given time.
- **Working Context:** High-interruption, multitasking environment. The seller is typically holding a smartphone in one hand while packing orders, unboxing inventory shipments, or replying to 5 simultaneous customer inquiries across Instagram and WhatsApp.
- **Device Usage:** **Phone-first in execution (~390px viewport), desktop-secondary for evening batch work.** During peak daytime hours, 80%+ of interactions happen on a mobile browser while switching back and forth between Instagram and the assistant.
- **Technical Sophistication:** Low to moderate enterprise software tolerance. Highly fluent in consumer apps (Instagram, TikTok, WhatsApp, banking apps), but allergic to complex ERP navigation, multi-level dropdown hierarchies, tiny table cells, and administrative bureaucracy.
- **Intolerable Friction Points:**
  - Having to fill out 10 mandatory fields just to save an item they want to sell immediately.
  - Multi-page navigation hops just to decrement a sold item by 1.
  - Scrolling through endless screen lengths to find an item while a buyer is waiting for a reply.
  - Losing form progress or search context when clicking between tabs or correcting an error.

---

## 3. Core Jobs to Be Done (Ranked by Operational Frequency)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CORE JOBS TO BE DONE (RANKED)                        │
├────────────────────────────────────────────────────────────────────────┤
│ 1. LOCATE PRODUCT UNDER TIME PRESSURE (Sub-3 seconds during chat)     │
│ 2. ANSWER BUYER QUESTION TRUTHFULLY (1-click copy "მზა პასუხი")        │
│ 3. RECORD COMPLETED SALE IMMEDIATELY (-1 stock stepper with 0 lag)     │
│ 4. CAPTURE NEW PRODUCT FROM MESSY TEXT (Description-first intake)     │
│ 5. RESOLVE OPERATIONAL ATTENTION (Triage low stock / missing info)     │
│ 6. CORRECT INCOMPLETE FACTUAL TRUTH (Direct deep-linked enrichments)   │
│ 7. DUPLICATE RECURRENT PRODUCT VARIANT (Add Similar / Clone)           │
│ 8. RETIRE SOLD-OUT INVENTORY (Archive without losing audit history)    │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Locate Product While Talking to a Buyer (Highest Frequency):** Find the exact item using whatever fragments the seller remembers ("შავი აბრეშუმი", "midi dress", "ზოლიანი პერანგი") in under 3 seconds.
2. **Answer Buyer Inquiries Instantly & Truthfully:** Copy a complete, professional Georgian message containing confirmed price, available sizes, remaining quantities, and verified fabric facts without manual typing.
3. **Change Stock Immediately After a Sale:** Tap `−1` on the exact size/color choice the moment payment is confirmed, preventing overselling.
4. **Capture a Product Rapidly:** Paste the raw text prepared for an Instagram caption, let the assistant extract attributes, verify the price, and save a sellable product in under 30 seconds.
5. **Notice Operational Bottlenecks at a Glance:** Instantly see which items are sold out, running low ($\le 2$), or missing critical buyer facts (price/fabric).
6. **Correct Missing Truth Without Searching:** Jump directly from a readiness warning into the exact input field requiring attention (e.g. missing fabric percentage).
7. **Create Seasonal / Similar Variants:** Duplicate an existing style (e.g. same cut in a new colorway) with stock cleanly reset to 0.
8. **Retire Inactive Goods:** Archive items no longer offered, keeping the active working cockpit uncluttered while preserving historical ledger accuracy.

---

## 4. Main Data & Information Hierarchy

```
┌────────────────────────────────────────────────────────────────────────┐
│ ALWAYS IMPORTANT (Visible at One Glance)                               │
│ • Thumbnail Image · Product Title · Price · Product Type               │
│ • Aggregate Stock Status (e.g. "მარაგშია: 5") · Active/Draft Pill      │
│ • Choices Summary String (e.g. "S: 2 · M: 3 · L: 0")                   │
│ • Primary Actions: [ მზა პასუხი ] and [ მარაგი / მართვა ▼ ]            │
├────────────────────────────────────────────────────────────────────────┤
│ CONTEXTUALLY IMPORTANT (Revealed on Operator Demand)                   │
│ • Individual Size x Color Choice Steppers (+1 / -1 buttons)            │
│ • Exact Quantity Overrides (Inline numeric chip)                       │
│ • Buyer Readiness Breakdown (Answered vs Missing questions)            │
│ • Targeted Correction Links (e.g. [მასალის მითითება])                   │
│ • Full Description Text excerpt                                        │
├────────────────────────────────────────────────────────────────────────┤
│ MAINTENANCE / SECONDARY (Subordinate Overflow Menu [ ••• ])            │
│ • [ რედაქტირება ] (Full Edit)                                          │
│ • [ მსგავსის დამატება ] (Add Similar)                                  │
│ • [ დაარქივება ] (Archive Product)                                     │
├────────────────────────────────────────────────────────────────────────┤
│ RARE / ADMINISTRATIVE (Dedicated Management Surface)                   │
│ • Global Vocabulary Management (Registering custom sizes/colors)       │
│ • Raw Audit Ledger Records (`InventoryAdjustment` logs)               │
│ • Business Tenant Settings (GEL currency, Business profile)            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Ideal Seller Flow

### A. Seller Starts the Day (Orientation)
The seller opens the browser on phone or laptop and lands directly on the **Operating Cockpit** (`/`). At the top of the canvas, four high-contrast **Attention Badges** summarize urgent items:
- `ყურადღება (2)` (Missing price or material)
- `მარაგი ეწურება (3)` (Items with $\le 2$ pieces left)
- `ამოიწურა (4)` (Sold out)
- `ყველა (28)` (Full active catalog)

In 2 seconds, the seller knows whether any overnight messages need stock alerts or catalog fixes.

### B & C. Customer Inquires & Seller Locates Product
An Instagram customer asks: *"გამარჯობა, თეთრი თეთრეულის პერანგი გაქვთ L ზომა?"* (Hi, do you have the white linen shirt in size L?).  
The seller switches to the assistant tab. Without changing pages, the seller types "თეთრი პერანგი" into the sticky search bar. The card list filters instantly.

### D. Answering the Buyer
The seller taps `[მზა პასუხი]`.
- **On Mobile:** A sleek Bottom Sheet smoothly rises from the base of the screen, displaying the complete Georgian message:
  ```text
  თეთრი თეთრეულის პერანგი
  ფასი: 75.00 GEL
  მარაგშია: L (1 ცალი), XL (2 ცალი)
  მასალა: 100% სელი (თეთრეული)
  ```
- Anchored to the bottom of the phone screen is a large, thumb-friendly button: `[დაკოპირება და დახურვა]` (Copy & Close).
- The seller taps it. The text copies to the clipboard, a green pill flashes ("დაკოპირებულია!"), the sheet dismisses, and the seller double-taps their phone task switcher to return to Instagram and paste the message. Total elapsed time: **4 seconds**.

### E. Sale Finalized & Stock Decremented
The customer replies: *"ვიღებ L ზომას, გადმოგირიცხეთ"* (I'll take size L, money sent).  
The seller switches back to the assistant tab, taps `[მართვა ▼]` on the shirt card, and taps `[−1]` on the `L / თეთრი` choice row.  
The stepper decrements from 1 to 0 instantly, the choice row badges to `ამოიწურა` (Sold Out), the card's aggregate stock updates, an immutable `InventoryAdjustment` row is written to the database, and the seller returns to Instagram to confirm the tracking details. Total elapsed time: **2 seconds**.

### F. Capturing a New Product
The seller unboxes a new batch of floral summer dresses. On `/products/new/`, the seller pastes their prepared Instagram caption into the large description box:  
*"ულამაზესი ყვავილებიანი საზაფხულო კაბა, 100% ბამბა, ზომები S, M, L. ფასი 65 ლარი."*  
- Within 600ms, the live recognition engine highlights: `[ტიპი: კაბა]`, `[მასალა: 100% ბამბა]`, `[ზომა: S]`, `[ზომა: M]`, `[ზომა: L]`.
- The seller taps the photo upload box, selects a camera photo, confirms the price (65), reviews the pre-generated choices table, inputs initial quantities (e.g. 2 of each), and taps `[შენახვა]` on the sticky mobile action bar. The product is live and sellable.

### G. Correcting Incomplete Truth
On the Cockpit, the seller taps the `ყურადღება` attention badge. Two products appear that have missing facts. One shows: `აკლია: მასალა` (Missing: Material) with a direct link `[მასალის დამატება]`. Tapping the link opens the edit form and auto-scrolls directly to the material card. The seller selects `აბრეშუმი 100%` and taps `[შენახვა]`. The attention badge counter drops from 2 to 1.

### H. Handling Low-Stock / Sold-Out Items
When a product sells out completely, it transitions automatically from `available` to `sold_out`. It remains visible in the workspace so the seller can still answer inquiries with an honest *"სამწუხაროდ ამოიწურა"* (Unfortunately sold out). When the seller decides not to restock the style, they open the card's `[•••]` menu and tap `[დაარქივება]`. The product immediately leaves the active daily cockpit.

### I. Operating Strictly from a Phone
Every action is optimized for single-thumb execution on a 390px viewport. Search is sticky at the top; primary actions are thumb-reachable at the bottom; cards are compact and scannable; overlays slide from the bottom; horizontal overflow is physically impossible.

---

## 6. What "Assistant-Like" Means for This Product

| Attribute | Assistant-Like Behavior (THIS PRODUCT) | ERP / Administrative Behavior (TO BE AVOIDED) |
| :--- | :--- | :--- |
| **Information Intake** | Ingests free-form natural language; extracts structure automatically. | 15 empty textboxes, mandatory foreign key dropdowns, required SKU codes. |
| **Action Locality** | Actions live right on the product card (in-place steppers, slide-over reply). | Navigating to sub-menus: Inventory $\rightarrow$ Stock Adjustments $\rightarrow$ New Voucher. |
| **Truth & Certainty** | Proposes candidates; asks seller to confirm; never invents claims. | Silent database defaults; black-box auto-merging of data; LLM hallucinations. |
| **Surfaces & Context** | 1 primary working canvas; contextual drawers/sheets for temporary tasks. | 10 distinct navigation tabs (Products, Stock, Categories, Attributes, Ledger, Reports). |
| **Error Feedback** | Clear human Georgian alerts explaining exact recovery and safe internal fallbacks. | Cryptic database constraint errors ("IntegrityError: foreign key violation business_id"). |
| **Readiness Model** | Discrete checklist of 5 answered buyer questions. | Meaningless percentage bars ("Product is 63% complete! Add manufacturer code!"). |

---

## 7. Operational Speed Spectrum

- **One Glance ($\le 1$ second):**
  - Is this item in stock?
  - What is the price?
  - Does my business have any urgent attention alerts today?
  - Is my catalog filtered or showing all items?
- **One Tap / Click (Instant):**
  - Copy ready reply to clipboard.
  - Decrement stock by 1 (`−1`).
  - Increment stock by 1 (`+1`).
  - Filter by attention category (*მარაგი ეწურება*, *ამოიწურა*).
- **A Short Focused Interaction (5–15 seconds):**
  - Open choice deck and inspect individual sizes.
  - Set an exact numerical stock quantity override (e.g. set stock to 12).
  - Open Ready Reply drawer to inspect specific fabric notes.
  - Clone a product via Add Similar.
  - Archive a retired style.
- **A Dedicated Editing Flow (30–60 seconds):**
  - Ingesting a brand new product from description text.
  - Editing multi-choice matrices or adding new canonical colors/sizes.
  - Correcting missing fiber percentages.

---

## 8. Number of Core Surfaces / Pages

To satisfy the **at most 3 navigation surfaces** rule in Project Bible §3.2 and maintain extreme operational simplicity, the application must consist of:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 3 ESSENTIAL SELLER SURFACES                      │
├────────────────────────────────────────────────────────────────────────┤
│ 1. THE SELLER COCKPIT (Primary Surface - `/`)                          │
│    • Unified triage header (Attention Badges)                          │
│    • Sticky search and horizontal filter chips                         │
│    • Compact Product Cards with expandable choice steppers             │
│    • Contextual Overlays: Ready Reply Bottom Sheet                     │
├────────────────────────────────────────────────────────────────────────┤
│ 2. PRODUCT INTAKE & EDIT CANVAS (Task Surface - `/products/new/`, etc) │
│    • Description-first input with live semantic recognition            │
│    • Structured Form Cards: Media, Choices, Materials                  │
│    • Sticky mobile action footer (`[შენახვა]`, `[გაუქმება]`)           │
├────────────────────────────────────────────────────────────────────────┤
│ 3. BUSINESS VOCABULARY DESK (Maintenance Surface - `/vocabulary/`)     │
│    • Canonical Types, Tags, Sizes, Colors, and Aliases                 │
│    • Visited rarely (once a month) to organize business taxonomy       │
└────────────────────────────────────────────────────────────────────────┘
```

### What Must NEVER Have Its Own Page:
- **No standalone Dashboard page:** The triage counts belong directly inside the Cockpit header.
- **No standalone "Stock Adjustment" page:** Stock changes happen directly on the product card.
- **No dedicated "Product Detail" page:** Detailed choices and facts disclose directly on demand inside the card or slide-over drawer.
- **No standalone "Ready Reply" page:** Replies are copied from a lightweight sheet/drawer.

---

## 9. Navigation Philosophy

- **Seller Tasks Over Database Entities:** Traditional ERPs organize menus around SQL tables (*Products*, *Stock Movements*, *Categories*, *Ledger Entries*). This assistant organizes around **seller tasks**: *Check Attention*, *Search & Sell*, *Add New Item*.
- **The Zero-Hop Principle:** A seller should never have to navigate away from their active search results just to record a sale or copy a customer response.
- **Context Preservation:** Applying a filter, searching for an item, opening an overlay, and copying text must preserve the exact scroll position and active query parameters.
- **Subordinate Administration:** Destructive actions (archiving), administrative configurations (vocabulary management), and deep edits are visually de-emphasized so they never interfere with high-frequency selling.

---

## 10. Product Card Philosophy: "Scan First, Operate on Demand"

A product card is not a database row and not an administrative form. It is a **tactical selling instrument**.

```
┌────────────────────────────────────────────────────────┐
│ COMPACT SCAN-FIRST STATE (Default)                     │
│ ┌──────────┐  Title: შავი აბრეშუმის კაბა              │
│ │  Thumb   │  Price: 120.00 GEL · Type: კაბა           │
│ │  (90px)  │  [მარაგშია: 4 ცალი] [აქტიური]             │
│ └──────────┘  Sizes: S (1) · M (2) · L (1)             │
│ Action Row:                                            │
│ [ მზა პასუხი ]    [ მარაგი / მართვა ▼ ]    [ ••• ]    │
└────────────────────────────────────────────────────────┘
          │ Tap [მართვა ▼]
          ▼
┌────────────────────────────────────────────────────────┐
│ OPERATIONAL DECK (Disclosed on Demand)                 │
│ Choice 1: S / Black · [ -1 ]  [ 1 ცალი ]  [ +1 ]       │
│ Choice 2: M / Black · [ -1 ]  [ 2 ცალი ]  [ +1 ]       │
│ Choice 3: L / Black · [ -1 ]  [ 1 ცალი ]  [ +1 ]       │
│ Readiness: ფასი, მარაგი, ზომა/ფერი, ტიპი, მასალა       │
└────────────────────────────────────────────────────────┘
```

- **At One Glance (Default):** Seller verifies identity (image + title), price, aggregate stock availability, and a compact summary of available sizes (`S: 1 · M: 2 · L: 1`).
- **On Operator Demand (Expanded):** Seller taps `[მართვა ▼]` to reveal individual choice rows with fast `+1` / `-1` steppers and readiness details.
- **Desktop vs. Mobile:** Universal compact-first layout. On wide desktop monitors, cards sit in a clean grid; on mobile phones, cards stack in a single column measuring $<300\text{px}$ in height, completely eliminating scroll fatigue.

---

## 11. Mobile-First Experience (~390px Viewport)

1. **Thumb-Zone Geometry:** The primary interaction targets—search input, Ready Reply copy button, stock steppers, and form save buttons—are sized to at least **$44\times 44\text{px}$** and positioned within natural thumb reach.
2. **Elimination of Scroll Walls:** Compressing default card heights from $900\text{px}$ to $<300\text{px}$ means a seller can scan 3–4 products per screen swipe instead of being trapped in a single card.
3. **Bottom Sheets Over Centered Modals:** On mobile, dialogs opening in the center of the screen require awkward reaches to top corners to close. Bottom sheets anchor actions to the base of the screen, where thumbs naturally rest.
4. **Physical Prevention of Horizontal Scroll:** All containers enforce `min-width: 0`, strict flex/grid constraints, and `overflow-wrap: anywhere` to prevent broken mobile horizontal dragging.

---

## 12. Product Capture & Correction Philosophy

The Description-First intake workflow represents the heart of the assistant's progressive structuring thesis:

```
[ Messy Georgian Description ]
              │ (600ms Debounce)
              ▼
[ Deterministic Recognition Engine ]
              │
              ├─► Suggested Type: "კაბა" (1-tap attach)
              ├─► Suggested Material: "100% აბრეშუმი" (1-tap attach)
              └─► Suggested Choices: S, M, L (1-tap generate matrix)
              │
              ▼
[ Structured Factual Product Bundle ] ──► Atomic Database Commit
```

- **Natural Entry:** The seller begins by typing or pasting text exactly as they would for an Instagram caption.
- **Non-Destructive Assistance:** The recognition engine suggests candidates; it never silently overwrites confirmed database fields without explicit seller confirmation.
- **Separation of Daily Entry from Taxonomy Admin:** Adding regular choices uses clean dropdowns; registering brand-new sizes or colors into the business vocabulary is tucked into a collapsed secondary card so it does not distract from daily intake.
- **Sticky Actions:** When editing long forms on mobile, `[შენახვა]` (Save) and `[გაუქმება]` (Cancel) remain permanently visible in a sticky bottom toolbar.

---

## 13. Media Experience

### A. Single-Image Scope (V1 Boundary)
- **Card Presentation:** Clean, fixed-ratio square or $4:3$ thumbnail ($90\times 90\text{px}$ on compact cards, max $200\text{px}$ in expanded view) with subtle border radius and `object-fit: cover`. It must never expand into an unbounded vertical banner.
- **Form Presentation:** Selecting a file triggers an instant client-side preview via JavaScript `FileReader`, reassuring the seller that the correct photo was chosen before submitting.

### B. Multiple Images / Gallery Evaluation
- **Does it strengthen the V1 thesis?** While multiple photos (front, back, fabric detail) are valuable in fashion, adding a multi-image gallery requires changing `ProductMedia` from a `OneToOneField` to a `ForeignKey`, building image reordering logic, managing multi-file uploads, and designing a touch-friendly carousel.
- **Strategic Recommendation:** **Maintain the 1-image boundary for V1 deployment.** One robust image fully validates file validation, authenticated streaming, responsive thumbnail layout, and media replacement. Multi-image galleries belong in V1.1.

---

## 14. Flexibility vs. Simplicity: The Golden Balance

The assistant achieves internal flexibility without punishing the seller with UI complexity:
- **Duplicate Visible Choices:** The system permits multiple choices with the identical `(size, color)` (e.g. separate storage batches or different cost lots). Rather than exposing cryptic database IDs or confusing matrix tables, the UI lists them as distinct, clearly labeled rows.
- **Missing Facts Without Nagging:** If an item lacks fabric facts or a price, the system does not block saving with an aggressive modal alert. It quietly flags a readiness gap (`აკლია: მასალა`) and provides a 1-tap deep link to fix it when the seller has time.
- **Vocabulary Customization on Demand:** If a seller invents a custom color (e.g. "ალუბლისფერი"), they can register it directly without leaving the form, but default sizing and standard colors remain pre-populated.

---

## 15. Ideal Information Architecture

```mermaid
graph TD
    subgraph Primary Working Canvas
        C[Unified Seller Cockpit /]
        C -->|Attention Chips| C
        C -->|Search & Horizontal Filters| C
        C -->|Expand Choice Deck| C
        C -->|Open Bottom Sheet| RR[Ready Reply Overlay]
    end

    subgraph Dedicated Task Surfaces
        C -->|Click [+ ახალი პროდუქტი]| CF[Product Intake Canvas /products/new/]
        C -->|Click [რედაქტირება]| EF[Product Edit Canvas /products/id/edit/]
        C -->|Click [ლექსიკონი]| VOC[Business Vocabulary Desk /vocabulary/]
    end

    CF -->|Save / Cancel| C
    EF -->|Save / Cancel| C
    VOC -->|Return| C
```

- **The Seller's Home:** The Unified Cockpit (`/`).
- **Primary Working Canvas:** The Cockpit card stream.
- **Triage & Attention:** Integrated directly into the top of the Cockpit as live filter chips.
- **Temporary Operations (Ready Reply, Stock Mutation):** Handled via bottom sheets or in-card micro-steppers with zero page transitions.
- **Dedicated Navigation Surfaces:** Reserved exclusively for deep editing tasks (Create, Edit, Global Vocabulary).

---

## 16. Product & UX Principles (The 10 Invariants)

1. **Seller Task > Database Structure:** Group interactions around what the seller is trying to accomplish (sell, check, answer), not how SQL tables are relationalized.
2. **Scan First, Operate on Demand:** Show only what is needed to recognize an item at a glance; disclose operational controls only when the seller chooses to act.
3. **Preserve Seller Context Always:** Never reset search queries, filter states, or scroll positions when completing a stock change or closing an overlay.
4. **Zero-Reflow Overlays:** Opening Ready Reply or expanding choice steppers must never push surrounding product cards unpredictably off the screen.
5. **Truth Remains Server-Owned:** Client interactions (HTMX, Alpine.js) are strictly transport layers. The PostgreSQL database remains the absolute source of truth for stock, lifecycle, and readiness.
6. **No AI Hallucination in Operations:** Only confirmed structured facts may enter customer-facing reply text. The assistant never guesses or invents buyer claims.
7. **Thumb-First Mobile Ergonomics:** Every critical daily action must be reachable and easily tapped with one thumb on a 390px mobile screen.
8. **Progressive Structuring Over Bureaucracy:** The easiest seller action (pasting unstructured text) should progressively build structured truth without forcing tedious upfront form completion.
9. **Instant Operational Feedback:** Every mutation (`+1`, `-1`, copy reply) must provide unmistakable visual and screen-reader confirmation within 100 milliseconds.
10. **Subordinate Administration:** Secondary and destructive operations (cloning, editing, archiving) must remain tucked into compact overflow menus so they never clutter high-frequency sales workflows.

---

## 17. Ideal Portfolio V1: The First 5 Minutes

When an engineering hiring manager, senior product designer, or fellow technologist opens the live demo URL, the impression within 300 seconds must be unmistakable:

- **To the Seller:** *"Finally, a tool built for how I actually sell on Instagram, instead of an American ERP or a complicated Shopify backend."*
- **To the Senior Product Designer:** *"The information hierarchy is disciplined. No bloated accordion walls, no layout jumping, perfect mobile thumb zones, and progressive disclosure that respects cognitive load."*
- **To the Senior Django Architect:** *"Rock-solid multi-tenant isolation, concurrency-safe inventory ledgering using row locks, pure service layers, deterministic heuristic NLP, and zero premature microservice complexity."*
- **To the Hiring Reviewer:** *"This candidate understands that senior software engineering is not about stacking trendy libraries, but about deeply understanding a domain, enforcing uncompromising data integrity, and crafting a razor-sharp user experience."*

---

## 18. Current Gap vs. Ideal Product

| Gap | Why It Matters | Ideal Direction | Backend Impact | Pre-Deployment Priority |
| :--- | :--- | :--- | :--- | :--- |
| **G-1: Split Dashboard / Workspace** | Forces sellers to hop between `/` and `/products/`, fragmenting triage from action. | Merge Dashboard attention queues into the Cockpit header (`/`) as live filter chips. | `LOW` (recompose existing attention query) | **CRITICAL (UX-A)** |
| **G-2: Mobile Card Scroll Fatigue** | Permanently unrolled choices make cards 900px tall on mobile, requiring endless scrolling. | Implement compact scan-first card ($<300\text{px}$) with expandable choice deck. | `NONE` (template/CSS only) | **CRITICAL (UX-B)** |
| **G-3: Ready Reply Layout Reflow** | Expanding reply panel inside card pushes subsequent cards down by 300px. | Refactor Ready Reply into a non-disruptive mobile Bottom Sheet / desktop slide-over. | `NONE` (template/CSS/JS only) | **CRITICAL (UX-C)** |
| **G-4: Form Accordion Fatigue** | 4 nested browser `<details>` accordions hide required fields and feel unpolished. | Replace raw `<details>` with clean styled form cards and a sticky mobile action bar. | `NONE` (template/CSS only) | **HIGH (UX-D)** |
| **G-5: Hidden Workspace Filters** | Workspace filters are collapsed inside `<details>` without active count indicators. | Expose persistent horizontal filter chips (All, Available, Sold Out, Draft, Archived). | `NONE` (template/CSS only) | **HIGH (UX-A)** |
| **G-6: Clumsy Exact Stock Editing** | Exact stock overrides expand an inline `<details>` form, shifting row heights. | Tap-to-edit inline number chip replacing the stepper on demand. | `NONE` (template/JS only) | **OPTIONAL (UX-B)** |

---

## 19. What Should Remain Deferred (Guardrails Reaffirmed)

1. **Related Products ("უხდება", Outfits, Combos):**  
   *Verdict:* **STRICTLY DEFERRED TO V2.**  
   *Rationale:* Requires new relational models (`ProductRelation`), bidirectional graph logic, and workspace UI changes. Does not strengthen the core 1-click inquiry/stock loop enough to justify introducing new database risk before Phase 13.
2. **Structured Garment Measurements (Waist, Chest, Inseam, etc.):**  
   *Verdict:* **STRICTLY DEFERRED TO V2.**  
   *Rationale:* High modeling complexity (unit handling, flat vs. circumference, category differences). The existing clothing domain proof (Size $\times$ Color choices + Material facts + Heuristic recognition) already provides deep portfolio credibility.
3. **Multi-Image Photo Gallery:**  
   *Verdict:* **DEFERRED TO V1.1 / POST-PORTFOLIO.**  
   *Rationale:* The single primary image model fulfills V1 needs and proves media upload, validation, and security streaming without carousel asset bloat.
4. **Public Storefront & Buyer Cart:**  
   *Verdict:* **STRICTLY DEFERRED (OUT OF SCOPE).**  
   *Rationale:* Breaks the core identity of the product as a seller operating assistant.
5. **Direct Meta / Instagram Graph API Webhooks:**  
   *Verdict:* **STRICTLY DEFERRED.**  
   *Rationale:* Introducing brittle third-party API keys and OAuth webhook loops in a portfolio demo creates severe maintenance fragility without improving core engineering proof.

---

## 20. Model's Product Design Recommendations

### Recommendation P-1: The "1-Tap Copy & Close" Action Loop
- **Status:** `DESIGN RECOMMENDATION — NOT CURRENT PRODUCT AUTHORITY`
- **Observed Problem:** When copying a ready reply on a phone, the seller must tap "დაკოპირება", read the success toast, and then find a separate close button or tap the backdrop to dismiss the panel.
- **Proposed Experience:** In the Ready Reply Bottom Sheet, provide a prominent, high-contrast primary button: `[დაკოპირება და დახურვა]` (Copy & Close). Tapping it executes `navigator.clipboard.writeText`, flashes a brief confirmation toast, and auto-dismisses the sheet after 400ms, returning the seller to their phone's home screen or Instagram with zero extra taps.
- **Seller Value:** Eliminates 1 unnecessary tap on the most frequent daily customer-answering loop.
- **Implementation Impact:** `NONE` (10 lines of JavaScript in `product_workspace.js`).
- **Timing:** **Pre-deployment (Include in UX-C).**

### Recommendation P-2: Live Filter Pill Badges with Active Highlights
- **Status:** `DESIGN RECOMMENDATION — NOT CURRENT PRODUCT AUTHORITY`
- **Observed Problem:** Sellers applying filters forget why certain products are hidden.
- **Proposed Experience:** Render filter chips with explicit numerical counters: `[ყველა (28)]`, `[მარაგშია (21)]`, `[ამოიწურა (4)]`, `[მონახაზი (3)]`. The active filter is highlighted with deep teal fill; inactive filters have subtle gray outlines.
- **Seller Value:** Instant clarity on catalog distribution and current filter context.
- **Implementation Impact:** `LOW` (Template logic in `templates/catalog/product_list.html`).
- **Timing:** **Pre-deployment (Include in UX-A).**

### Recommendation P-3: Instant Photo Thumbnail Preview via FileReader
- **Status:** `DESIGN RECOMMENDATION — NOT CURRENT PRODUCT AUTHORITY`
- **Observed Problem:** Selecting a photo in the product form displays only a tiny system filename (e.g. `IMG_4021.jpg`). The seller cannot visually confirm they chose the right dress photo until after submitting.
- **Proposed Experience:** Attach a lightweight JavaScript `change` listener to `#id_media-file` that reads the selected file and immediately replaces the preview thumbnail with the selected image.
- **Seller Value:** Instant visual reassurance during product intake.
- **Implementation Impact:** `NONE` (5 lines of vanilla JavaScript).
- **Timing:** **Pre-deployment (Include in UX-D).**

---

## 21. Understanding Check: The 5-Paragraph Product Synthesis

If I had to describe the intended product to a new senior designer and engineer in five paragraphs, this is what I would tell them:

1. **The Core Thesis:** We are building an operating assistant for solo social-commerce clothing sellers in Georgia who run their businesses out of Instagram DMs and WhatsApp chats. They do not want an ERP, they do not want a complex Shopify admin, and they refuse to fill out bureaucratic multi-field forms. They want a blazingly fast companion tool that stays open on their phone or laptop, enabling them to find an item in two seconds, answer customer questions with 100% factual accuracy, and record sales before their inventory gets desynchronized.
2. **Description-First Progressive Structuring:** Rather than forcing structured data entry upfront, the product meets the seller where they are: in chaotic, unstructured Georgian text. The seller pastes the caption they wrote for Instagram into the assistant. Our deterministic heuristic analyzer instantly recognizes product types, fiber compositions, sizes, and colors, suggesting them as confirmable candidates. The easiest action for the seller—pasting messy text—progressively builds clean, structured database truth without friction.
3. **The Selling Loop (Sub-5 Seconds):** When an Instagram customer asks about an item, the seller searches one or two keywords in the unified cockpit. The product card displays verified price, available sizes, and aggregate stock in a single compact glance. Tapping "მზა პასუხი" opens an overlay with a perfectly formatted, polite Georgian reply listing price, available sizes, and confirmed fabric composition. Tapping "დაკოპირება და დახურვა" copies the message to the clipboard and closes the overlay so the seller can switch back to Instagram and paste it in seconds.
4. **Instant Stock Accountability:** When the customer confirms payment, the seller taps "მართვა" on the card, revealing large, touch-friendly `+1` and `−1` stepper buttons for each size/color choice. Tapping `−1` updates stock immediately with zero page reload. Under the hood, this mutation is concurrency-safe: it locks the database row with PostgreSQL `select_for_update`, appends an immutable entry to the `InventoryAdjustment` audit ledger, prevents stock from ever dropping below zero, and immediately recalculates availability across the catalog.
5. **Architectural & Design Discipline:** The user interface is strictly bound to three major surfaces: the unified operating cockpit, the product capture/edit canvas, and the occasional vocabulary desk. We reject premature complexity: no microservices, no public storefronts, no LLM hallucinations, and no sprawling accordion menus. Everything is engineered to feel like a high-speed personal assistant—delivering maximum operational speed to the seller while proving uncompromising backend integrity to any technical reviewer.

---

## 22. True Owner Ambiguities

After synthesizing the canonical Project Bible, the current codebase, and the approved decision directions, we evaluate whether any high-level product ambiguities remain:

- **Cockpit Unification:** Approved (Dashboard attention merged into Workspace header).
- **Product Card Architecture:** Approved (Compact-first scan layout across mobile and desktop; on-demand choice deck expansion).
- **Ready Reply Presentation:** Approved (Responsive Bottom Sheet on mobile; slide-over drawer on desktop; zero in-card reflow).
- **Product Create/Edit Flow:** Approved (Single-page structured form cards with sticky mobile save bar; wizard deferred).
- **Domain Scope Guardrails:** Approved (Related products, garment measurements, and multi-image galleries remain strictly deferred).
- **Core Invariants:** Approved (Tenant isolation, PostgreSQL row locks, immutable ledgers, and deterministic readiness remain protected).

**Conclusion:**  
**NO HIGH-LEVEL PRODUCT AMBIGUITY FOUND.**  
The product vision, user model, ergonomic strategy, and architectural boundaries are completely aligned and unambiguous. We are ready to author `docs/REMAINING_RELEASE_PLAN.md`.
