# PROJECT_BIBLE — Compact Canonical Context

## 0. Document Contract

| Field | Canonical value |
|---|---|
| Status | CANONICAL BASELINE |
| Project | Social Commerce Operating Assistant |
| Purpose | Portfolio-grade GitHub project + live Django demo |
| Market | Georgia |
| Primary user | Small/solo Facebook & Instagram social-commerce seller |
| UI language | Georgian |
| Code/DB/enums/docs | English |
| Architecture | Django modular monolith + PostgreSQL |
| Frontend | Django Templates + HTMX + Alpine.js + Tailwind CSS |
| Owner | osMit |

This file is the durable implementation context for Portfolio V1. It replaces scattered durable truth from prior planning, discovery, prototype-audit, technical, journey, and domain docs.

Authority:
1. `docs/PROJECT_BIBLE.md` controls durable product intent, V1 scope, domain truth, UX contracts, architecture, verification, security, deployment, Git discipline, and AI-development boundaries.
2. `docs/BUILD_PLAN.md` controls implementation order, phase/micro-slice boundaries, dependencies, acceptance criteria, verification requirements, owner-test gates, and stop gates.
3. `docs/DEVELOPMENT_NOTES.md` is the append-only operational handoff for actual execution state, blockers, recoveries, plan splits/amendments, meaningful decisions, and next work.
4. Git/GitHub/CI control exact commit, push, remote-alignment, and CI truth.
5. `README.md` is public presentation/setup and must not redefine scope or implementation order.
6. Archived docs preserve provenance only and are not routine coding context.
7. Code/tests prove implementation reality; they do not change approved scope by themselves.
8. Later explicit owner decisions override this file only when they deliberately change durable truth; then synchronize the Bible and, if execution order is affected, the Build Plan.

Durable labels:
- **V1**: approved Portfolio V1 behavior.
- **HARD**: invariant that implementation must not weaken.
- **DEFERRED**: preserved future boundary, not V1 implementation.
- **HISTORICAL**: useful hypothesis/evidence, not current acceptance criteria.

### Anti-scope-creep rule
AI/engineering work may reconcile, strengthen, structure, and implement approved intent. Do not invent features because they would improve a hypothetical commercial product. Add scope only when required to complete an approved journey, protect correctness/security/accessibility/recovery, make approved behavior usable, satisfy demo/deployment correctness, or when owner-approved.

---

# 1. Product and Portfolio Definition

## 1.1 Canonical product statement

**Social Commerce Operating Assistant is a seller-first platform for social sellers prone to chaotic or minimal data entry. Starting from a natural Description, it progressively builds reliable, structured, reusable product truth; lets the seller manage catalog and stock from one primary workspace; shows which buyer questions can already be answered; and provides immediate value through Ready Reply and other assistant behaviors without becoming complex ecommerce/ERP administration.**

Primary promise: **an assistant that helps the seller organize product chaos.**

Core thesis: **the easiest seller action should gradually create better structured truth.**

A seller may begin with only `dress` or `trousers`. The system should preserve natural wording, recognize known vocabulary/aliases, show what it understood, suggest structure conservatively, request confirmation only where needed/high-impact, expose buyer-question coverage, recommend the smallest useful correction, and reward better truth through better search, stock clarity, and Ready Reply.

The problem exists before Messenger: product truth is incomplete/inconsistent/scattered across memory, posts, DMs, notes, photos, supplier messages, and prior conversations. Missing truth creates repeated questions about price, availability, size, color, material/composition, pockets/closure/stretch, garment measurements, and fit guidance.

### Anti-goal
Do not become:
- an Excel-like table;
- Shopify/WooCommerce-style administration;
- broad ERP;
- a giant specification form;
- taxonomy bureaucracy;
- a decorative BI dashboard;
- an AI system that invents commercial truth.

The system should remove work, not create a second job.

## 1.2 Portfolio objective

The repository must show cross-system engineering ability: product/scope reasoning, requirements, domain/source-of-truth design, Django/Python, PostgreSQL integrity/concurrency, server-rendered frontend/HTMX, mobile UX/accessibility, security/Business isolation, failure recovery, testing/CI, deployment, synthetic demo safety, documentation governance, honest Git history, and disciplined AI-assisted development.

Portfolio V1 is a **controlled proof**, not a finished commercial SaaS. Prefer a small number of deeply correct, interesting capabilities over broad shallow scope.

Repository history is part of the deliverable. Desired progression:
`decision/acceptance boundary -> focused implementation -> verification -> correction if needed -> durable-doc sync if needed -> commit -> push -> CI`.

Never fabricate or rewrite history to simulate process.

---

# 2. Product Layers and Scope

## 2.1 V1 foundation

Portfolio V1 implements the seller truth/catalog/inventory foundation:
- authenticated seller + one active Business workspace in UI;
- Description-first Product capture/edit/correction;
- Business vocabulary, aliases, recognition, confirmation;
- clothing material semantics;
- size/color ProductChoices;
- stock + audit trail + computed availability;
- Product Workspace search/filter/pagination;
- action-oriented Dashboard;
- buyer-question coverage;
- Ready Reply;
- Add Similar;
- archive/restore;
- optional Product media;
- critical tests/CI;
- synthetic resettable online Django/PostgreSQL demo;
- honest Git/GitHub history.

## 2.2 Explicitly out of V1

- dedicated Product Detail page;
- public buyer catalog implementation;
- buyer chatbot/messaging integration;
- LLM-owned product truth;
- orders/reservations;
- payments;
- delivery workflow;
- customer CRM;
- supplier/accounting scope;
- multi-staff/team permissions;
- broad ERP;
- Product Relations;
- universal taxonomy;
- giant clothing spec form;
- full measurement subsystem;
- AI sizing/body profile/guaranteed fit;
- label-photo OCR;
- full Georgian morphology/fuzzy search;
- advanced BI;
- full public REST API without a consumer;
- microservices/distributed architecture.

## 2.3 DEFERRED long-term architecture

Future product layers, in order of dependency:
1. **Buyer catalog**: seller-published products, minimal filters, open-text search, confirmed facts, availability, inquiry entry.
2. **Buyer assistant/chatbot**: buyer language -> intent -> trusted catalog retrieval -> truthful answer/uncertainty handling.
3. **Orders/reservations**: request -> seller approval -> reservation/stock integration -> cancellation/fulfillment.
4. **Payments**.
5. **Delivery/export**.
6. **Intent recovery** for unanswered/abandoned buyer intent.

### Publication invariant
Future publication is an explicit seller action and is separate from Product lifecycle and inventory availability. `active != published`. Do not add a publication field/UI before the public layer is actually approved.

### Future-readiness rule
Prepare stable service/data boundaries, not premature features. V1 foundations that future layers may reuse: confirmed truth, availability service, inventory ledger, deterministic reply service, search/query service, recognition states, media boundary, and Business isolation.

---

# 3. Primary User and UX Architecture

## 3.1 User model

Primary V1 user: authenticated solo/very-small social seller, phone-first, often inconsistent, impatient with administrative forms, and likely to enter minimal descriptions.

The system must support two common behaviors:
- **chaotic seller**: inconsistent spelling, synonyms, duplicated concepts, scattered truth;
- **low-effort seller**: enters the minimum and only adds more when immediate value is visible.

Vocabulary and readiness are behavioral assistance, not bureaucracy: reuse canonical terms, show what is known/missing, and reward better truth.

### Business policy
V1 UI exposes one active Business workspace; no switcher. Schema may remain future-ready for multiple Businesses, but do not silently choose the first Business when ownership is ambiguous. Business setup/resolution must be explicit; no hidden GET-side-effect auto-creation.

## 3.2 Navigation budget

Seller should work across at most three conceptual surfaces:
1. **Product Workspace** — primary daily work page.
2. **Dashboard** — secondary overview/attention page.
3. **Create/Edit/Correction** — supporting task surface; may use a full page, focused panel, modal, drawer, or disclosure when appropriate.

No dedicated Product Detail in V1. Add a new page only when it owns a distinct job that cannot remain clear in the existing surfaces.

## 3.3 Product Workspace — PRIMARY

Question answered: **Which product do I need to find, change, stock, correct, or answer about?**

Must provide:
- search;
- URL-backed, visible, clearable filters;
- pagination or bounded incremental loading;
- compact Product cards;
- choice/stock state;
- high-frequency stock controls;
- lifecycle + computed availability;
- buyer-question coverage + next useful correction;
- on-demand Ready Reply;
- Add Similar;
- subordinate archive/secondary actions.

Card priority:
1. identity/media;
2. price;
3. lifecycle/availability;
4. choice/stock;
5. high-frequency stock control;
6. readiness/next correction;
7. Ready Reply entry;
8. secondary actions under subordinate disclosure/menu.

Do not let lifecycle/destructive actions compete visually with routine stock work. The card is an operational control surface, not the whole app.

## 3.4 Dashboard — SECONDARY

Question answered: **What needs attention now?**

Prioritize actionable items in the first viewport:
- needs attention;
- low stock;
- sold out/restock candidates;
- missing answer-critical facts;
- empty-catalog Quick Add;
- compact summaries that open a filtered Workspace state.

Do not prioritize charts, decorative metrics, marketing, BI, or future order/payment widgets. Dashboard actions must preserve a safe explicit return path.

## 3.5 Create/Edit/Correction

Purpose: create/correct truth, not host every feature.

Rules:
- Description first;
- required/high-impact data early;
- progressive disclosure for secondary semantics;
- recognition/vocabulary actions remain contextual;
- no Product Relations/admin concepts;
- correction links target the relevant section where practical;
- validation identifies the exact problem and preserves entered data;
- origin/return context remains explicit.

## 3.6 Return/mobile/accessibility basics

Seller must not depend on browser Back. Use a validated internal return mechanism; reject external/unsafe targets and use a safe fallback. Preserve Workspace filter/page context through correction where practical.

Phone is primary. Requirements: useful first viewport, safe tap targets, Georgian labels that wrap, compact filters, scannable cards, obvious stock controls, separated destructive actions, visible loading/success/failure, no narrow-width breakage, and no unbounded-scroll-only strategy.

---

# 4. Description-First Assistant, Recognition, and Vocabulary

## 4.1 Description is the primary capture surface

`Product.description` is the required primary seller-authored identity/capture field. Do not require a second marketing-title field merely to mimic ecommerce schemas. Cards may render a concise/truncated Description.

Description is not a dead textbox: it is recognition/search input and the bridge from natural seller language to structured truth.

## 4.2 Three information states — HARD

1. **Observed Text**: exact seller wording; retained for traceability/search/recognition. Not automatically structured buyer truth.
2. **Candidate**: possible semantic match from Business vocabulary, aliases, or deterministic conservative parsing. May be shown immediately.
3. **Confirmed Fact**: seller-approved or safely persisted structured value. Only confirmed facts may drive precise buyer claims.

Never collapse these states.

## 4.3 Recognition contract

Priority:
1. reuse existing canonical Business vocabulary;
2. show recognized meaning;
3. allow correction/removal;
4. suggest new candidates conservatively;
5. require explicit confirmation before high-impact creation/attachment;
6. uncertainty -> no mutation; Description remains searchable.

Recognition and mutation are separate. A controlled action such as `M and L recognized -> add to choices?` is allowed only when explicit, deterministic, scoped, duplicate-safe, and followed by visible server truth.

### Duplicate-operation safety
Retries/repeated taps/repeated acceptance must not create accidental duplicates. If a normalized-equivalent ProductChoice already exists, surface it and require an intentional additional-row action. Intentional duplicate-visible choices remain valid; accidental duplicate side effects do not.

### LLM boundary — HARD
An LLM may assist future interpretation or development, but it never owns operational truth. V1 recognition is deterministic or explicitly confirmable.

## 4.4 Business vocabulary

No global Product Type/Tag taxonomy in V1.

**Product Type** answers “What product is this?” It is short, canonical, noun-like, one primary product kind; not size, color, material, price, stock/lifecycle, or full marketing text.

**Tag** supports search/grouping/feature/occasion. Tags are optional and do not increase generic readiness merely by existing. A feature Tag may answer a buyer question only when a specific readiness/reply rule understands it. Do not turn every token, size, color, price, stock state, adjective, or material into a Tag.

### Aliases
Business-scoped aliases map seller wording to canonical values. Preserve original Description; search may match alias/canonical forms; buyer output uses confirmed canonical wording. At minimum normalize safe whitespace/case. Full Georgian morphology/fuzzy matching is DEFERRED.

### Duplicate prevention
Block/reuse exact normalized vocabulary duplicates. Surface deterministic existing matches before creating new canonical values. Never silently merge uncertain similarity. Distinct meanings may remain distinct.

Vocabulary maintenance should be contextual. A compact subordinate management surface is allowed for rename/deactivate/alias maintenance, but it must not become another daily-work branch.

---

# 5. Clothing Domain Contract

Clothing is the first domain because it stresses choices, materials, repeated buyer questions, and inconsistent seller wording. Keep the architecture extensible without building a universal ontology.

| Semantic destination | Truth owner |
|---|---|
| Product Type | confirmed BusinessProductType |
| Generic/Feature Tag | confirmed BusinessTag |
| Material | confirmed Product material fact |
| Size | ProductChoice |
| Color | ProductChoice |
| Measurement | future confirmed Measurement |
| Search token | normalized observed text only |

## 5.1 Material — V1

Material is not a generic Tag. A confirmed material fact should preserve canonical material, optional percentage, original seller wording, source, and confirmation state.

HARD rules:
- candidate != confirmed material;
- negation such as “does not contain polyester” must not create positive polyester truth;
- commercial fabric names must not be converted into invented scientific composition;
- buyer replies use confirmed material only.

## 5.2 Size/Color — V1

Size and Color belong to ProductChoice. Description recognition may suggest choices but does not create choice truth until confirmed. `Free size` is a seller label, not a fit guarantee. Size/color must not be reduced to generic Tags.

## 5.3 Detailed measurements — DEFERRED

A future confirmed Measurement must preserve: type, numeric value, unit, measurement method, applies-to Product or choice/size, optional seller note, confirmation state.

A value such as `waist 38 cm` is unsafe without knowing flat width, half/full circumference, or body recommendation.

Do not implement until a future micro-slice freezes unit policy, convention, category prompts, Product-vs-Choice ownership, confirmation UI, and buyer-reply wording.

## 5.4 Fit guidance — DEFERRED

Seller-provided context only. Weight alone never determines size; no guaranteed-fit, medical/biometric claims, body-profile storage, or AI sizing in V1.

---

# 6. Data, Source of Truth, and Core Semantics

## 6.1 Source-of-truth matrix — HARD where marked

| Fact | Stored source | Derived consumer rule |
|---|---|---|
| Seller identity | User | auth/session; seller routes require auth |
| Ownership | Business + Business FKs | HARD: every seller object/query/action Business-scoped |
| Product identity/input | Product.description | recognition/search; not universal structured truth |
| Lifecycle | Product | separate from availability |
| Price | Product nullable price | `NULL=missing`, `>0=confirmed`, `0=invalid` |
| Type | confirmed Business vocabulary relation | one canonical type truth |
| Tags | confirmed Business vocabulary relations | optional/search; no cross-Business leakage |
| Material | confirmed material fact | candidate never drives buyer claim |
| Size/Color | ProductChoice | sellable choice truth |
| Quantity | ProductChoice | HARD: no Product-level stock truth |
| Product total | none | computed aggregation |
| Availability | none | HARD: centralized computation |
| Readiness | none | buyer-question coverage; never completion % |
| Ready Reply | none | deterministic confirmed truth only |
| Candidate | transient or recognition state | never silently buyer truth |
| Publication | future | explicit seller action; separate from lifecycle/availability |

## 6.2 Planning-level entities

- **User**: authenticated seller.
- **Business**: tenant/ownership boundary; owner, name, default currency, timestamps; one active workspace in V1 UI.
- **Product**: Business, Description, nullable price, currency, lifecycle, timestamps; never quantity owner.
- **ProductChoice**: Product, size, color, quantity, active/inactive, stable row ID; no V1 price override.
- **ProductMedia**: optional general Product media; stable primary representation/placeholder. Advanced roles/OCR deferred.
- **BusinessProductType**, **BusinessTag**: Business-scoped canonical vocabularies.
- **VocabularyAlias** or equivalent: Business-scoped alias mapping; schema shape may vary if invariant is preserved.
- **ProductMaterialFact**: confirmed material semantics.
- **InventoryAdjustment**: immutable/auditable accepted stock transition with Business, ProductChoice, old/new quantity, delta, mutation kind, actor, timestamp.
- **Recognition Candidate**: persistence optional unless a real audit need justifies it.

Do not require V1 models for Order, Reservation, Payment, Delivery, CRM/Buyer profile, body profile, Supplier, accounting ledger, ProductRelation graph, or BI warehouse.

## 6.3 Price — owner-resolved

- `NULL`: missing/unknown;
- `>0`: confirmed;
- `0` or negative: invalid;
- no “free” price mode in V1.

Draft may have missing price. Active Product may also remain operational with missing price if it has valid choices, but it is not price-answer-ready. Readiness surfaces the gap; Ready Reply never invents price. If “free” is later needed, use explicit semantics rather than zero.

## 6.4 Lifecycle and availability

Stored lifecycle: `draft`, `active`, `archived`. No `hidden` in V1.

- **Draft**: incomplete/not-active truth; may have zero choices; never buyer-available.
- **Active**: normal seller operations; must have >=1 valid active ProductChoice. `active != available`.
- **Archived**: removed from daily work without deleting history; not sellable/normal Ready Reply; reversible. Restore -> `draft` for review, never silent reactivation.

For Active Products:
- any active choice qty `>0` -> available;
- mix of `0` and `>0` -> partially sold out signal;
- all active choices `0` -> sold out;
- low-stock is a centralized computed signal, not lifecycle.

HARD: Dashboard, Workspace, filters, readiness, and Ready Reply use the same availability service.

## 6.5 ProductChoice identity and duplicate semantics — HARD OWNER RULE

Multiple rows with the same trim-normalized/case-insensitive size+color are valid distinct sellable choices. Never auto-merge and never impose normalized `(product,size,color)` uniqueness.

Requirements:
- stable row identity;
- stock mutation/ledger target exact row;
- UI makes the target row unambiguous;
- do not invent buyer-facing distinctions absent from stored truth.

If duplicate-visible rows make buyer quantity wording ambiguous, use conservative wording/seller note; do not invent aggregation. Advanced buyer-facing disambiguation is deferred.

---

# 7. Product Bundle and Seller Maintenance

## 7.1 Creation/edit journey

1. Seller starts from Workspace/Dashboard.
2. Enters Description first and price if known.
3. Recognition shows existing Type/Tag/material candidates and size/color suggestions.
4. Seller confirms/corrects high-impact candidates.
5. Product may remain Draft while incomplete.
6. Seller adds >=1 size/color/quantity choice before Active use.
7. Media optional.
8. Save persists the logical Product bundle atomically.
9. Return to operational context with computed availability/readiness.

### Product bundle atomicity — HARD
A successful logical save must not leave unexplained partial persistence. Validate before commit where feasible; use a DB transaction for the logical bundle; do not leave a half-created sellable Product; media failures require deliberate cleanup/recovery.

### Choice validation
- qty >=0;
- partially filled rows -> clear row errors;
- empty unsaved rows may be ignored;
- Active requires >=1 retained valid active choice;
- Draft may have none;
- removing all Active choices is rejected or accompanied by a validated lifecycle transition to Draft.

## 7.2 Add Similar — V1

Seller-facing concept: **Add Similar**, not a complex clone-mode menu. Purpose: speed first, assistant behavior second.

New Product:
- new identity;
- `draft` lifecycle;
- may copy useful stable confirmed product facts and choice structure;
- all copied quantities reset to `0`;
- never copy inventory history;
- media not copied by default to prevent wrong-product imagery;
- seller reviews distinguishing facts before activation.

Future similarity recommendations are deferred.

## 7.3 Archive/Restore — V1

Archive is explicit/confirmed, removes Product from normal active work, preserves history, and is reversible. Restore -> Draft. No seller hard-delete workflow and no separate Hidden state.

## 7.4 Media

Media is optional for initial Description-first capture and is general Product data, not clothing ontology. Missing media uses a deliberate placeholder. Demo media must be synthetic/licensed-safe and never private source media.

Possible later capabilities: multiple photos, primary/order, semantic roles, OCR; not automatic V1 commitments.

---

# 8. Inventory Contract — HARD CORE

Inventory is a high-frequency workflow and critical portfolio integrity boundary.

Allowed V1 operations on one ProductChoice: `+1`, `-1`, direct set to nonnegative quantity. Direct set is secondary in UI.

### Single mutation boundary — HARD
Every stock change, including HTMX/direct set and relevant internal operations, uses one inventory application/service boundary. Product Edit, Admin shortcuts, Add Similar, or alternate views must not create a second mutable-stock path.

### Transaction safety — HARD
Prevent lost updates with appropriate PostgreSQL/Django semantics (row locks, DB expressions, or equivalent). Exact mechanism may vary; correctness does not.

### Adjustment ledger — HARD
Every accepted mutation creates one `InventoryAdjustment` in the same successful transaction. Rejected mutations create no success ledger entry.

Mutation rules:
- never below zero;
- exact ProductChoice identity;
- final server value replaces temporary client state;
- recompute sold-out/restock/availability after change;
- readiness/Ready Reply consume updated truth;
- surrounding visible counts/groups must not remain misleadingly stale.

### HTMX contract
HTMX is transport/progressive enhancement, never truth ownership. Show loading/disable repeated unsafe input, persisted success, transition feedback, and visible failure/retry/full-refresh recovery. Refresh/invalidate every affected aggregate or otherwise avoid displaying stale truth.

---

# 9. Search, Scalability, Readiness, and Ready Reply

## 9.1 Search/catalog scalability

Search how the seller remembers Products. Approved inputs may include Description, normalized observed wording, aliases, confirmed Type/Tags/material, choice size/color. Lifecycle/availability/readiness belong in explicit filters where useful.

V1 does not promise AI semantic search, fuzzy/typo ranking, full Georgian morphology, Elasticsearch/OpenSearch.

Filters: visible when active, URL-backed, clearable, compact on mobile, preserved through corrections where practical. Keep dimensions limited to daily operations (e.g., lifecycle/availability, readiness, Type, Tag; size/color/material only when useful without density harm).

Use server-side pagination or bounded loading. Preserve query/filter state across pages, avoid unbounded scroll walls, prefetch/select card dependencies, and provide understandable result/no-result states.

## 9.2 Readiness — HARD PRODUCT CONTRACT

Readiness is **buyer-question coverage**, never a generic completion percentage.

Show which answers are available (e.g., price, size/color, stock, type, material) and which are not (e.g., missing measurements). Missing truth produces the smallest useful seller correction, not nagging about optional data.

Readiness is a reward loop: a meaningful enrichment should visibly unlock an answer, remove a signal, improve Ready Reply, improve vocabulary reuse, or improve search.

## 9.3 Ready Reply — V1 controlled reward

Purpose:
- practical seller-side copy tool;
- immediate reward for maintaining structured truth.

Placement: on-demand from Product Workspace in a focused panel/drawer/disclosure or equivalent server-backed interaction. No dedicated Product Detail and no permanently expanded card clutter.

### Truth contract — HARD
May use only confirmed structured facts, centrally computed state, and Product Description as human description text without promoting uncertain tokens into precise claims. Never invent price, stock, size, color, material, measurement, fit, lifecycle, or availability.

Missing facts -> seller-only correction note, not fabricated buyer text. Seller-only warnings must never enter copied text. Sold-out Product never implies availability.

Copy: seller reviews, explicitly copies, sees copy success or failure fallback; V1 sends no messages.

A small set of reply intents (price, size/color, stock, material, full answer, etc.) is allowed only if understandable and low-clutter. Fixed tab count is not a requirement.

Deterministic reply service should be reusable by a future buyer assistant without changing truth ownership.

---

# 10. System Architecture and Service Boundaries

## 10.1 Style/stack

**Django modular monolith** using Python, Django, PostgreSQL, Django Templates, HTMX for targeted server-owned updates, Alpine.js for small isolated local state, and Tailwind with reproducible production asset handling.

Avoid microservices, event bus/Kafka, Kubernetes, premature Celery/Redis, API-first design without a consumer, and SPA framework complexity when server-rendered workflows suffice. Prototype CDN usage is historical evidence, not deployment architecture.

## 10.2 Modules

| Module | Responsibility |
|---|---|
| `accounts` | auth identity/forms/login/logout |
| `businesses` | ownership, workspace resolution/setup |
| `catalog` | Product/Choice/Media, Type/Tag relations, bundle commands, Workspace queries, Add Similar, archive/restore |
| `recognition` or `catalog.recognition` | observed normalization, alias matching, candidates, confirmation; never owns confirmed truth alone |
| `clothing` | material rules + clothing recognition + deferred measurement boundary |
| `inventory` | mutations, ledger, availability/transition results |
| `readiness`/`validation` | buyer-question coverage + attention signals |
| `dashboard` | action-oriented query composition from shared services |
| `reply` | deterministic Ready Reply |
| `demo`/commands | synthetic seed/reset/setup |

Views orchestrate HTTP; domain truth belongs in forms/services/policies/query helpers. Avoid fat views and runtime schema-existence branching.

## 10.3 Core services

- **Product bundle**: validate Product + confirmed facts + choices + media refs; enforce lifecycle/choice rules; atomic save; do not bypass inventory policy for existing stock.
- **Recognition**: safe normalization, Business vocabulary/alias matching, conservative candidates, uncertainty preservation, no silent high-impact persistence.
- **Availability**: pure centralized lifecycle+active-choice computation.
- **Inventory mutation**: Business/actor/choice authorization, `+1/-1/set`, nonnegative validation, concurrency safety, ledger, transition, atomicity.
- **Readiness**: pure buyer-question coverage from confirmed facts/computed state.
- **Search/query**: Business scoping, normalized search, defined filters, pagination, predictable query behavior.
- **Reply**: confirmed facts + computed state only; no LLM truth.
- **Safe return helper**: internal destination validation.
- **Add Similar**: Draft copy semantics above.
- **Archive/restore**: explicit lifecycle transitions.

---

# 11. Authentication, Business Isolation, Security

## 11.1 Business isolation — RELEASE BLOCKER

Every seller-owned object/query/form/service/endpoint is scoped to active Business: Product, ProductChoice, media, Type, Tag, aliases, material facts, InventoryAdjustment, search suggestions/results, Dashboard counts, HTMX mutations, Add Similar, archive/restore.

A seller cannot view/edit/archive/restore/clone/mutate/attach vocabulary from another Business or discover another Business through search/dashboard. Use deliberate 404/forbidden behavior without leaking existence.

## 11.2 Authentication

Seller routes require auth. Email/password Django auth is enough for V1. Public signup/reset/verification are not required unless demo operation needs them. Django Admin is internal maintenance/debugging, not seller UX.

## 11.3 Repository/runtime security

Never commit `.env`, real credentials/secrets/API keys, DB dumps, prototype backups, private logs, seller/customer data, private source media, or live session data.

Commit-safe config: `.env.example` placeholders; production `SECRET_KEY` required; `DEBUG=False`; explicit hosts/CSRF origins; env-driven DB config.

HTTP: mutations use correct methods; CSRF stays enabled; unsafe `next` rejected; raw `HTTP_REFERER` is not canonical return authority; destructive lifecycle action requires deliberate confirmation.

If uploads exist: validate type/size, store outside source control, generate safe paths/names, define failed-transaction cleanup.

---

# 12. Failure, Accessibility, and Performance Contracts

## 12.1 Failure/recovery

Every mutation/journey defines success and failure.

- Form errors: field-local + visible non-field/formset errors; preserve values/context.
- Active without required choice: block with clear recovery.
- Negative stock: reject and preserve prior confirmed state.
- HTMX failure: visible retry/full-refresh guidance; no silent no-op.
- Clipboard failure: visible fallback; never falsely report copied.
- Missing media: placeholder, no broken layout.
- Unsafe return URL: reject -> safe internal fallback.
- Recognition uncertainty: no destructive side effect; keep Description searchable.
- Concurrent stock mutation: no lost update or misleading duplicate adjustment; persisted DB state wins.

## 12.2 Accessibility baseline

Use semantic links/buttons/headings/labels; associate errors; disclosures expose state (`aria-expanded` where applicable); deliberate focus/keyboard behavior; no color-only status; announce meaningful async status (`role=status`/`alert` as suitable); safe tap targets; meaningful image alt/placeholder; loading/disabled states must not trap users. HTMX/Alpine do not override semantic HTML. Make only verified accessibility claims.

## 12.3 Performance/scalability

No hyperscale requirement, but no obvious unbounded design. Use Business-scoped querysets, pagination/bounded loading, deliberate select/prefetch, DB/shared query logic for Dashboard aggregation, avoid search N+1, scoped HTMX partials, and indexes for justified ownership/common lookup paths. Do not add search engines, queues, or distributed caches without measured need.

---

# 13. Verification and CI

Testing is a release requirement and portfolio feature.

## 13.1 Test layers

- **Unit**: normalization, aliases, display helpers, pure state policies.
- **Service**: availability, inventory/concurrency, readiness, replies, recognition, Add Similar, archive/restore.
- **Form/formset**: create/edit, Draft-vs-Active choice rule, partial choices, negative qty, price, candidate confirmation.
- **View/access**: auth, Business isolation, safe return, HTMX success/failure, archive/clone/set access.
- **Domain**: candidate never becomes fact silently; material negation; size/color suggestion-only; duplicate-visible choices stay distinct; reply uses confirmed material only.
- **Management commands**: seed/reset dry-run/confirmation where applicable, demo scoping, protected identities, media policy.
- **Manual UX**: mobile viewport, filters/pagination, return paths, Ready Reply, HTMX failure, copy, accessibility basics.

## 13.2 Release-blocking regression matrix

| Scenario | Required result |
|---|---|
| Cross-Business Product/stock | 404/forbidden; no leak/change |
| Valid bundle | complete atomic persistence |
| Invalid bundle | no partial sellable state |
| Draft without choices | allowed |
| Active without choices | rejected |
| Duplicate-visible size/color | distinct row identities allowed |
| Qty `1->0` | sold-out transition + adjustment |
| Qty `0->1` | restock transition + adjustment |
| Concurrent mutation | no lost update |
| Direct set | exact row + same service/ledger |
| Unconfirmed candidate | never buyer claim |
| Negative material wording | no positive material fact |
| Missing price | coverage gap; no invented price |
| Price `0` | rejected |
| Sold-out reply | no availability claim |
| Safe internal return | context preserved |
| External return | rejected |
| Add Similar | Draft copy, stock 0, no ledger copy |
| Archive | exits active daily work |
| Restore | returns Draft |
| HTMX failure | visible recovery |
| Stock-dependent aggregates | no misleading stale UI |
| Demo reset | only scoped synthetic data |

## 13.3 CI gates

Minimum on push/PR: install dependencies -> Django system check -> migration consistency/missing-migration check -> automated tests. Add lint/format only when deliberately adopted. After deployment, add smoke/health verification and practical secret/repository checks.

A micro-slice is not complete because it works locally.

---

# 14. Demo and Deployment

## 14.1 Demo contract

Purpose: let an employer/reviewer experience UI/UX and engineering behavior; not operate as commercial production SaaS.

Owner-resolved access: **authenticated interactive synthetic demo seller**. Reviewer should be able to find Products, change stock, observe sold-out/restock, inspect readiness, open Ready Reply, correct missing data, Add Similar, archive/restore.

Seed a small purposeful catalog covering available, low-stock, partially sold-out, sold-out, Draft, missing-price/media, material/recognition truth, strong Ready Reply coverage, and duplicate-visible choices where useful.

Reset/reseed must be tested, synthetic-scope-only, deliberate for destructive operations, protect user/Business identities, have explicit media cleanup, and restore a known baseline. Never copy real prototype/seller/customer data.

## 14.2 Deployment contract

Live demo requires backend-capable hosting for Django + PostgreSQL. GitHub is repository/portfolio host; GitHub Pages cannot run the full app.

Provider choice is deferred to the deployment slice and is an engineering choice. Evaluate Django support, PostgreSQL, secrets, migration execution, static assets, predictable demo cost, and smoke/health verification.

Production settings: `DEBUG=False`, env-required secret key, explicit hosts/CSRF origins, PostgreSQL config, production static strategy, deliberate media strategy, secure cookies appropriate to HTTPS.

Use PostgreSQL in demo; do not replace architecture behavior with SQLite-only deployment.

Deployment slice: provision platform -> env/secrets -> PostgreSQL -> install/build -> migrations -> static collection -> synthetic seed -> authenticated demo -> health/smoke test -> add README demo link only after verification.

---

# 15. Git/GitHub Portfolio Contract

Git history must be honest, chronological, and meaningful.

Never fabricate/backdate commits, force-rewrite published `main` for storytelling, create meaningless activity noise, expose secrets/private data, or combine unrelated feature intentions unnecessarily.

## Micro-slice workflow
1. Establish current state from `docs/BUILD_PLAN.md`, the latest relevant `docs/DEVELOPMENT_NOTES.md`, and Git/GitHub/CI.
2. Freeze the exact micro-slice goal, acceptance criteria, exclusions, and owner-test requirement.
3. Inspect only relevant source and tests.
4. Implement only the approved slice.
5. Run focused verification and broaden regression checks according to risk.
6. Audit integrity, security, UX, failure recovery, and scope boundaries.
7. Complete required owner/browser verification before Code PASS.
8. Synchronize durable documentation only when durable truth actually changed.
9. Review the exact release diff and repository hygiene.
10. Commit one clear intention.
11. Push normally.
12. Verify remote alignment and required CI for the exact pushed revision.
13. Append the resulting operational handoff to `docs/DEVELOPMENT_NOTES.md`.

Commit prefixes may include `docs:`, `feat:`, `fix:`, `test:`, `refactor:`, `chore:` when they reflect real intent. Do not separate essential implementation/tests artificially just to increase commit count.

Meaningful defect discovery and focused correction are positive portfolio evidence; do not erase them to simulate perfection.

Push discipline: no force-push on published main; confirm clean expected tree, branch/remote alignment, no private staging, and exact pushed CI.

---

# 16. AI Development and Documentation Governance

## 16.1 AI/Codex contract

AI may assist analysis, planning, implementation, tests, review, docs, and drift audits. It does not control scope expansion, owner product semantics, release acceptance, secrets, business-truth invention, or Git-history fabrication.

Routine fresh-context order:
1. `docs/PROJECT_BIBLE.md` once for canonical durable context;
2. the current/relevant section of `docs/BUILD_PLAN.md`;
3. the latest relevant entries from `docs/DEVELOPMENT_NOTES.md`;
4. current Git/remote/CI facts;
5. relevant source and tests.

In the same Codex chat, do not reread the whole Bible or Build Plan unless a concrete conflict, dependency, or durable-truth question requires it.

Do not load `docs/archive/` routinely. Search archived material only when a specific historical rationale is genuinely required.

AI must not resurrect prototype features because they once existed, implement DEFERRED layers, promote examples/rationale into requirements, create pages/models/services without current need, or silently reinterpret owner decisions. AI code requires source inspection + appropriate tests + manual checks when relevant.

## 16.2 Minimal documentation architecture

- **`docs/PROJECT_BIBLE.md`**: frozen durable product/scope/domain/UX/architecture/integrity/testing/security/deployment truth.
- **`docs/BUILD_PLAN.md`**: frozen-by-default execution order, dependencies, micro-slice contracts, acceptance, verification, owner-test gates, and stop gates.
- **`docs/DEVELOPMENT_NOTES.md`**: live append-only operational handoff and meaningful execution/decision history.
- **`README.md`**: public portfolio overview, verified setup, architecture summary, tests, screenshots, and demo access.
- **`docs/archive/`**: provenance/history only; never routine implementation authority.
- **Git/GitHub/CI**: exact release and delivery evidence.

Routine execution should write primarily to `docs/DEVELOPMENT_NOTES.md`.

Update `docs/PROJECT_BIBLE.md` only when durable owner-approved truth changes.

Update `docs/BUILD_PLAN.md` only through an owner-approved `PLAN_AMENDMENT` that changes roadmap order, dependency, scope boundary, stop gate, or verification strategy.

Update `README.md` only when verified public-facing reality materially changes.

Before release milestones, compare Bible, Build Plan, Development Notes, code/tests, Git/CI, and README for material drift.

---

# 17. Historical Hypotheses — NOT ACCEPTANCE CRITERIA

Preserve, but never present as achieved without real evidence:
- seller may manage 20–50 Products;
- creation target roughly 60–90 seconds;
- repeated 21-day return/use;
- clone/quantity updates may improve retention;
- cockpit may feel better than Excel/Messenger notes;
- possible 21-day free trial;
- possible 49 GEL/month initial pricing and higher pricing after buyer/chatbot/order/payment value.

Never fabricate adoption, retention, willingness-to-pay, or pilot results.

---

# 18. Execution Plan Boundary

Implementation order, phases, micro-slices, dependencies, acceptance criteria, verification requirements, owner-test gates, and stop gates are defined exclusively in `docs/BUILD_PLAN.md`.

This Bible defines what must remain true; it does not duplicate the execution roadmap.

Routine progress or phase status must not be written here.

---

# 19. Definition of Done and Stop Gates

Portfolio V1 is done only when the approved product, integrity, UX, verification, demo, deployment, documentation, and Git contracts above are met.

Minimum end-state:
- seller signs in to one active Business;
- Description-first Draft/correction works;
- Type/Tag/material confirmation and size/color/qty choices work;
- Active validity, price semantics, duplicate-choice identity, stock service/ledger/concurrency, and centralized availability are enforced;
- Workspace scales through search/filter/pagination and remains the primary work page;
- Dashboard is action-oriented;
- buyer-question coverage and truth-safe Ready Reply work;
- Add Similar + archive/restore behave as specified;
- cross-Business access is blocked;
- mobile/accessibility/failure paths are verified;
- critical regressions pass in CI;
- synthetic resettable Django/PostgreSQL demo is deployed and smoke-tested;
- repository has no secrets/private source data and history remains honest;
- Bible/README/code/tests are not materially drifting.

### Stop gates
Do not proceed past a slice when its prerequisite truth is unresolved or release-blocking verification fails. In particular:
- Business isolation before deeper seller data;
- source-of-truth/lifecycle/price before dependent UI;
- choice identity/atomic bundle before inventory;
- concurrency/ledger/availability before stock-rich Workspace;
- server truth + failure behavior before HTMX polish;
- deterministic reply/readiness truth before Ready Reply UI;
- synthetic reset safety + production config before public demo;
- passing CI/drift/security checks before portfolio release.

---

# 20. Risk Controls

| Risk | Canonical mitigation |
|---|---|
| Scope creep / endless product | explicit V1/non-goals/deferred boundaries; micro-slice gates |
| Seller data-entry fatigue | Description-first recognition, progressive disclosure, reward loops |
| Vocabulary chaos | Business canonical vocabulary + aliases + explicit confirmation |
| Candidate becomes false truth | observed/candidate/confirmed separation |
| Material false positive | negation-aware rules + confirmation |
| Duplicate-choice confusion | stable row identity + exact-row mutations + conservative reply wording |
| Stock race/lost update | one transactional inventory service + concurrency tests |
| Incomplete ledger | adjustment in same successful mutation transaction |
| Cross-Business leak | scoped queries/forms/services/endpoints + release-blocking tests |
| Partial Product persistence | atomic logical bundle |
| Card/UI overload | fixed information/action priority + subordinate actions |
| Seller wandering | one primary Workspace + explicit safe returns |
| Large catalog scroll wall | search/filter + pagination/bounded loading |
| HTMX stale truth | explicit affected-state refresh/invalidation contract |
| Readiness becomes punitive | question coverage/reward, not completion % |
| Ready Reply clutter | on-demand focused UI |
| Clone phantom stock | Draft + qty reset + no ledger copy |
| Restore stale sellable truth | restore -> Draft |
| Old docs resurrect scope | Bible-first context; archive not routine context |
| Fabricated-looking portfolio | honest chronological Git + visible corrections |
| Demo data leak | synthetic-only seed/media/reset |
| Static hosting mismatch | backend-capable Django host + PostgreSQL |

---

# 21. Seller-Facing Language

UI should be Georgian, concrete, assistant-like, and non-technical. Prefer concepts equivalent to: Products, Description, Price, Choice, Size, Color, Stock/Remaining, Quick Update, Ready to Answer, Missing Information, Add Similar, Archive, Restore, Confirm, Skip, Recognized.

Avoid seller-facing: ERP, SKU, variant matrix, schema, inventory ledger, ontology, event sourcing, entity. Backend/code may use precise technical terms.

---

# 22. Deferred Decision Register

These do not block V1 and should be decided only when the corresponding future slice is proposed:
- public-catalog publication schema/UI;
- buyer chatbot channel/UI/integration;
- measurement unit/convention, Product-vs-Choice ownership, confirmation/reply wording;
- fit-guidance wording;
- public Business branding/slug/storefront identity;
- multi-Business switcher/team permissions;
- order/reservation lifecycle;
- payment/delivery/privacy workflows;
- fuzzy/morphology search;
- image/label OCR;
- advanced analytics/pilot telemetry;
- future pricing/business model.

---

# 23. Provenance / Traceability

This Bible consolidates the durable product, domain, UX, architecture, integrity, testing, deployment, and owner-decision truth from earlier project documentation.

Historical planning, discovery, prototype-analysis, and superseded specification documents are preserved under `docs/archive/` for provenance only. They are not active implementation authority and must not be loaded as routine Codex context.

Active documentation authority is limited to:

1. `docs/PROJECT_BIBLE.md` — canonical project truth.
2. `docs/BUILD_PLAN.md` — implementation order and execution contracts.
3. `docs/DEVELOPMENT_NOTES.md` — append-only operational state and decision history.


---

# 24. Canonical Engineering Principles

1. Seller truth before buyer automation.
2. Description-first != free-text-only.
3. Simple UI may sit on a strong relational model.
4. Observed text != Candidate != Confirmed Fact.
5. DB/service layer owns operational truth; browser/LLM do not.
6. Stock belongs to ProductChoice; lifecycle, availability, readiness, and future publication remain separate.
7. Every stock mutation is authorized, nonnegative, atomic, concurrency-safe, and audited.
8. Business isolation is release-blocking.
9. Readiness is buyer-question coverage; Ready Reply rewards better truth.
10. Seller works mainly from Product Workspace; navigation minimizes wandering.
11. Progressive disclosure beats page/form proliferation.
12. HTMX improves interaction, never changes truth semantics.
13. Mobile/accessibility/failure recovery are architecture concerns.
14. Future-ready means clean boundaries, not premature features.
15. Demo/deployment must be technically honest.
16. Git history is part of the portfolio artifact.
17. Documentation should reduce context, not multiply it.
18. AI may accelerate work but cannot expand scope or invent truth silently.
19. If a capability does not reduce seller effort, buyer uncertainty, operational error, or demonstrate an approved portfolio concern, its V1 value is suspect.
20. Do not build everything. Finish the controlled proof.

---

# 25. Final Canonical Outcome

The live demo should visibly prove this product chain:

`chaotic/minimal seller Description -> recognized meaning -> seller-confirmed structured truth -> searchable catalog -> exact-choice stock -> computed availability -> buyer-question coverage -> truthful Ready Reply`

The repository should prove this engineering chain:

`product reasoning -> scope/acceptance -> source-of-truth design -> focused micro-slice -> secure/transaction-safe implementation -> regression/failure/UX verification -> durable-doc sync when needed -> honest commit/push -> CI -> deployable demo`

That combination—not feature count—is the Portfolio V1 deliverable.
