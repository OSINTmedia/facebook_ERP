# Assistant-First Product Design Synthesis

## Document Metadata

- **Status:** DISCOVERY_SYNTHESIS_FOR_OWNER_REVIEW
- **Project:** Social Commerce Seller Operations Assistant
- **Target location:** `docs/discovery/ASSISTANT_FIRST_PRODUCT_DESIGN_SYNTHESIS.md`
- **Primary audience:** Product owner, product designer, UI/UX designer, Django architect, domain-model reviewer, QA reviewer, and future Codex sessions
- **Document type:** Product and experience discovery synthesis
- **Implementation authority:** No
- **Scope authority:** No
- **Owner approval required before promotion into active planning documents:** Yes
- **Update rule:** Update only when new seller evidence, prototype observations, or owner-approved product reasoning materially changes the product thesis

## 1. Document Role and Authority Boundary

This document explains the product idea in one coherent narrative.

It exists to preserve the reasoning behind the interface, the assistant behavior, the anti-chaos mechanisms, and the seller workflow. It is intentionally placed under `docs/discovery/` because it synthesizes product evidence and design direction rather than controlling implementation by itself.

The active authority order remains:

1. `changelog_checkpoint.md` for current project state and next micro-slice;
2. `BUILD_PLAN.md` for implementation order and stop gates;
3. `APP_EXPERIENCE_PLAN.md` for approved experience contracts;
4. owner-approved frozen product, technical, clothing-domain, and journey documents for scope;
5. this document as discovery and reasoning support.

If this document conflicts with an owner-approved active document, the active document wins. The conflict must be reviewed rather than silently resolved.

## 2. Review Lenses Used in This Synthesis

This synthesis is written through several coordinated roles.

### Product Designer

Defines the real seller problem, product value, boundaries, and assistant behavior.

### UI/UX Designer

Defines low-friction interaction, information hierarchy, mobile behavior, feedback, progressive disclosure, and the difference between a simple interface and a weak data model.

### Service Designer

Examines the seller's full operational loop: publishing a product, receiving repetitive buyer questions, checking stock, correcting missing information, and preparing replies.

### Information Architect

Defines the minimum number of primary surfaces, page responsibility, navigation, return paths, and where information should appear.

### Domain Architect

Separates product facts, choices, stock, lifecycle, availability, semantic vocabulary, measurements, and answer readiness.

### Django/PostgreSQL Systems Architect

Translates the experience into server-owned truth, relational boundaries, auditable updates, and deterministic behavior without forcing premature microservices or API-first complexity.

### Conversational-Commerce Designer

Defines how reliable product truth becomes useful seller-side answers without allowing an LLM to invent price, stock, size, color, material, or availability.

### Behavioral UX Reviewer

Focuses on the time-constrained, inconsistent, or low-discipline seller who will avoid complex forms and repeat the easiest available behavior.

### Accessibility and Mobile Reviewer

Ensures that compactness does not become unreadability, hidden state, color-only meaning, or unsafe small tap targets.

### QA and Failure-Path Reviewer

Examines stale state, ambiguous measurements, accidental stock changes, recognition errors, lost navigation context, and misleading ready replies.

### Scope-Control Reviewer

Continuously asks whether a proposed feature helps the seller manage product truth or merely turns the product into another ecommerce administration system.

## 3. Executive Product Definition

The Social Commerce Seller Operations Assistant is a private, seller-first catalog and inventory cockpit for small Facebook and Instagram sellers.

It helps a seller:

- capture product truth with low effort;
- reuse consistent product vocabulary;
- manage size, color, and stock choices;
- notice missing information;
- update operational state quickly;
- understand which buyer questions can already be answered;
- prepare truthful replies from confirmed data;
- reduce repeated Messenger or direct-message work.

The product is not primarily a storefront.

It is not a public marketplace.

It is not a broad ERP.

It is not a conventional ecommerce admin panel with many sections, nested settings, taxonomy screens, specification tables, order management, payment management, delivery management, and analytics dashboards.

Its job is narrower and more practical:

> Turn chaotic seller knowledge into reliable operational product truth without making the seller feel that data management has become a second job.

## 4. The Core Problem

Small social-commerce sellers often publish only a product photo and a short caption.

The seller may know the price, available colors, available sizes, current stock, fabric, measurements, or fit guidance, but this knowledge is scattered across:

- memory;
- old Messenger conversations;
- Instagram direct messages;
- copied captions;
- phone notes;
- photos;
- supplier messages;
- informal naming habits;
- repeated customer questions.

The buyer then has to ask basic questions that would have been unnecessary if the listing contained enough usable information:

- What is the price?
- Which sizes are available?
- Do you have black?
- Is it still in stock?
- What material is it?
- Does the fabric stretch?
- What is the garment length?
- What is the sleeve length?
- What is the waist measurement?
- Does it run small or large?
- What body weight does it fit?

These questions are not irrational. They are a predictable consequence of incomplete seller-maintained product truth.

The seller experiences them as repetitive interruption. The buyer experiences them as uncertainty. The system problem exists before either person opens Messenger.

## 5. Product Thesis

The product should not punish the seller for operating chaotically.

It should absorb part of that chaos, reveal where information is missing, and reward the seller when a small amount of extra truth removes future work.

The product thesis is:

> The easiest seller action should gradually create better structured truth.

This means:

- one description field may remain the primary capture surface;
- existing vocabulary should be recognized automatically;
- repeated terms should be normalized instead of duplicated;
- structured facts should be extracted or suggested where useful;
- the seller should confirm only high-impact or ambiguous meaning;
- each confirmed fact should immediately unlock a visible benefit;
- the application should recommend the next useful correction rather than display a giant empty form.

## 6. The Anti-Goal: “Another Ecommerce Site”

The product must actively resist becoming another ecommerce administration system.

A conventional ecommerce admin often assumes that the merchant will:

- navigate through many screens;
- understand catalog terminology;
- complete long specification forms;
- manage categories, attributes, variants, media, SEO, shipping, orders, and payments;
- tolerate configuration work before receiving value;
- maintain data according to the system's structure.

This project starts from the opposite assumption:

- the seller is busy;
- the seller may be inconsistent;
- the seller may prefer one description field;
- the seller may not know formal textile terminology;
- the seller may post supplier photos rather than measure every garment;
- the seller will abandon workflows that feel administrative;
- the seller needs immediate operational value.

The design therefore prioritizes:

- two primary working surfaces;
- compact contextual actions;
- description-first input;
- recognized vocabulary;
- visible answer readiness;
- quick stock operations;
- progressive disclosure;
- explicit return paths;
- server-backed truth;
- low mobile cognitive load.

A feature is suspicious when it adds a page, a form section, or a new taxonomy but does not clearly reduce seller effort, buyer uncertainty, or operational error.

## 7. Primary User

The primary user is a small social-commerce seller who sells through Facebook, Instagram, Messenger, or similar channels.

Typical characteristics:

- manages a small or medium catalog;
- works mainly from a phone;
- publishes product photos quickly;
- frequently copies or rewrites descriptions;
- answers repetitive questions manually;
- may use inconsistent spelling or synonyms;
- may not maintain a separate website or catalog;
- may not think in terms of database fields;
- cares about speed more than perfect data entry;
- notices the cost of missing information only after buyers begin asking.

The interface should use concrete seller language rather than system language.

Seller-facing terms should prefer words equivalent to:

- products;
- stock;
- remaining;
- price;
- size;
- color;
- add;
- edit;
- archive;
- ready answer.

Seller-facing UI should avoid terms such as:

- ERP;
- schema;
- entity;
- variant matrix;
- inventory ledger;
- semantic ontology;
- event sourcing.

The backend may use technical concepts. The seller should not have to.

## 8. Primary Jobs to Be Done

### Job 1: Add a usable product quickly

The seller needs to create enough product truth without completing a long specification form.

### Job 2: Find a product quickly

The seller needs to search by the words naturally used in descriptions, types, tags, sizes, and colors.

### Job 3: Update stock with minimal interruption

The seller needs to change a choice quantity directly where the product is visible.

### Job 4: Correct missing information

The seller needs to see why a product is not ready to answer a common buyer question and fix that missing fact.

### Job 5: Prepare a truthful answer

The seller needs a copyable response generated only from stored facts and computed state.

### Job 6: Maintain vocabulary without administrative work

The seller needs the system to recognize repeated product types, tags, materials, and aliases so inconsistent writing does not create uncontrolled duplication.

## 9. Experience Objective

UX is an operational-system concern, not visual decoration.

The interface should help the seller maintain reliable truth with the lowest practical cognitive load.

The experience should feel like a compact assistant that says:

- “I recognized this.”
- “You already use this term.”
- “This product is missing one fact.”
- “You can now answer material questions.”
- “This size/color choice is sold out.”
- “Update the stock here.”
- “Here is a truthful answer you can copy.”

It should not feel like a system that says:

- “Complete the remaining 23 fields.”
- “Navigate to attribute management.”
- “Configure a variant matrix.”
- “Open inventory settings.”
- “Your product profile is 61% complete.”

## 10. Two Primary Operating Surfaces

The product should preserve two main working spaces.

## 10.1 Dashboard

The Dashboard answers:

> What needs my attention today?

The first viewport should provide useful action, not decorative metrics.

Useful dashboard attention items may include:

- low-stock choices;
- sold-out products that may need restocking;
- products missing critical answer data;
- products with no usable choice;
- recently changed stock;
- a direct path to add a product when the catalog is empty.

Allowed summaries should lead into real work.

Examples:

- `3 low-stock choices`
- `2 products cannot answer size questions`
- `4 sold-out products`
- `1 product missing a price`

The Dashboard should not become:

- a BI dashboard;
- a chart collection;
- an order monitor;
- a payment dashboard;
- a delivery dashboard;
- a marketing homepage.

Every attention link should preserve a clear return path to the Dashboard.

## 10.2 Product Workspace

The Product Workspace answers:

> Which product do I need to find, update, correct, or answer about?

Its essential elements are:

- search;
- visible active filters;
- compact product cards;
- stock and choice state;
- readiness or answer-coverage signal;
- one clear correction/edit path;
- optional ready-reply access when approved.

The workspace is the daily operational cockpit.

The seller should not need to open a separate inventory page for every stock adjustment or navigate through several administrative sections to inspect one product.

## 11. Supporting Surfaces

Supporting surfaces may exist, but they should not compete with the two primary operating surfaces.

### Product Create

Purpose:

> Add enough truth to make a product usable.

The first visible path should stay compact.

### Product Edit/Correction

Purpose:

> Correct existing truth and missing information without losing the seller's origin context.

### Taxonomy Management

May exist only when separate management is genuinely necessary.

Recognition and inline recovery should reduce the need to visit it.

### Product Detail

Should exist only if it has a clear responsibility that is not already handled by the product card or edit flow.

### Login and Account

Should remain simple and operational, not marketing-heavy.

## 12. Description-First Product Capture

The product description is the primary seller input.

This is not an accidental shortcut. It is a deliberate UX strategy based on realistic seller behavior.

A seller may write:

> Classic wide-leg trousers with pockets, black and beige, sizes M and L, 70% cotton and 30% polyester.

The seller should not be forced to repeat every part of that sentence in separate form fields before receiving value.

The system should analyze the description against known business vocabulary and structured patterns.

Potential destinations include:

- Product Type;
- Generic or Feature Tag;
- Material;
- Size candidate;
- Color candidate;
- Measurement candidate;
- Search-only token.

The description remains human-readable seller text.

Recognized structured facts become separate truth only through safe rules or confirmation.

## 13. Three Information States

The system should distinguish three states of information.

### 13.1 Observed Text

The exact wording entered by the seller.

It supports traceability and search.

### 13.2 Recognized Candidate

A word or phrase that appears to match a known type, tag, material, size, color, measurement, or alias.

It may be shown as a recognition chip.

### 13.3 Confirmed Fact

A value approved by the seller or persisted through a safe deterministic rule.

Confirmed facts may drive:

- stock state;
- availability;
- readiness;
- filtering;
- deterministic buyer replies.

This separation prevents a search token from becoming an unsafe buyer-facing claim.

## 14. Product Type, Tag, and Description

These three concepts form the current recognition foundation.

## 14.1 Product Description

The description is the flexible human input.

It may contain:

- product identity;
- style;
- features;
- material wording;
- sizes;
- colors;
- measurements;
- seller notes;
- commercial language.

The system should not require every word to be classified.

## 14.2 Product Type

Product Type answers:

> What kind of product is this?

Examples:

- trousers;
- dress;
- blouse;
- jacket;
- skirt.

A recognized existing type tells the seller that a known category term has been reused rather than duplicated.

## 14.3 Tag

Tags support seller vocabulary, search, grouping, style, feature, detail, or occasion.

Examples:

- classic;
- casual;
- wide-leg;
- pockets;
- evening;
- summer.

The first version should avoid splitting every possible meaning into separate attribute systems.

A tag becomes a separate semantic type only when a real product behavior requires it.

## 15. Recognition as a Chaos-Control Mechanism

Recognition is not merely a search feature.

It is a standards mechanism.

When the seller reuses an existing Product Type or Tag, the system can show:

- the term already exists;
- the existing canonical form was recognized;
- the seller is reusing a stable vocabulary.

The emotional message is not “validation succeeded.”

It is:

> Good. You kept the catalog consistent.

The system should make order visible without lecturing the seller about data governance.

## 16. Alias Normalization

Seller vocabulary is often inconsistent.

Examples may include:

- misspellings;
- grammatical forms;
- alternative spellings;
- supplier terminology;
- colloquial material names;
- singular and plural forms.

The system should preserve the seller's wording while mapping reusable aliases to a canonical value.

Conceptual example:

```text
Observed wording: "polyestir"
Canonical value: "polyester"
Semantic type: material
```

Rules:

- the seller should correct an alias once;
- future uses should be recognized;
- search should match both alias and canonical value;
- buyer replies should use the canonical confirmed value;
- business-specific aliases should not automatically become global truth;
- negative phrases must not be interpreted through naive token matching.

For example:

```text
"does not contain polyester"
```

must not become:

```text
Material: polyester
```

## 17. Semantic Labels Without Form Expansion

The system may assign semantic labels to recognized words, but the seller should not classify every token manually.

A recognition area may show:

```text
Recognized:

[Type · Trousers]
[Tag · Classic]
[Feature · Pockets]
[Material · Cotton]
[Size · M → Add to choices]
[Color · Black → Add to choices]
```

The UI may use visually distinct chips or compact labels.

The architecture should preserve the difference between:

- a search token;
- a type;
- a generic tag;
- a material fact;
- a size/color choice;
- a measurement candidate.

The seller should intervene only when:

- the match is ambiguous;
- the term is new;
- the fact is high impact;
- the recognition affects buyer-facing truth;
- the system cannot safely infer negation or context.

## 18. Material as a Small Typed Extension

Material is more important than an ordinary search tag because it may affect:

- allergy concerns;
- comfort;
- fabric expectations;
- washing questions;
- precise buyer replies.

However, material should not force the seller into a separate large textile form.

The primary path remains:

1. seller writes material wording in the description;
2. the system recognizes a known material or alias;
3. the system shows the candidate;
4. the seller confirms or corrects where needed;
5. the product gains material answer readiness.

Possible stored material facts may include:

- canonical material;
- optional percentage;
- original seller wording;
- confirmation state;
- source.

Examples:

- `100% cotton`
- `70% cotton, 30% polyester`
- `satin`
- `chiffon`

Important boundary:

Everyday seller fabric names are commercially useful but are not always equivalent to scientific fiber composition. The system should preserve the seller's wording and avoid inventing technical material composition.

## 19. General Size Versus Garment Measurements

A general size such as `M`, `XL`, `38`, or `Free size` is useful, but often insufficient.

General size belongs to a sellable product choice.

Detailed garment measurements answer different questions.

Examples include:

- chest/bust;
- waist;
- hip;
- shoulder width;
- sleeve length;
- garment length;
- inseam;
- rise;
- thigh;
- hem width;
- approved custom measurement.

The product should not confuse these two levels.

## 19.1 Size Choice

Size choice answers:

> Which labeled size can the seller sell?

It belongs with color and quantity.

## 19.2 Detailed Measurement

Detailed measurement answers:

> What is the physical garment dimension?

It requires more context than a number.

For example:

```text
Waist: 38 cm
```

may mean:

- flat garment width;
- half circumference;
- full circumference;
- recommended body measurement.

A precise number without a method is dangerous.

## 19.3 Measurement Capability Direction

Detailed measurement entry should be a separate, optional, progressive action:

```text
+ Add measurements
```

The system should show category-relevant prompts rather than all possible measurements.

Examples:

- trousers: waist, hip, inseam, rise, thigh, garment length;
- tops: chest/bust, shoulder width, sleeve length, garment length;
- dresses: chest/bust, waist, hip, garment length;
- jackets: chest/bust, shoulder width, sleeve length, garment length;
- skirts: waist, hip, garment length.

A measurement record should eventually distinguish:

- measurement type;
- numeric value;
- unit;
- method;
- applicability to product, size, or choice;
- optional note;
- confirmation state.

Measurement implementation should remain a separate approved micro-slice because measurement language, tailoring conventions, product-level versus size-level applicability, and seller comprehension require focused design.

## 20. The “What Weight Does It Fit?” Problem

Buyers often ask what body weight a garment fits because:

- the listing has no measurements;
- general size labels vary;
- the seller may use supplier photos;
- the buyer cannot inspect the garment;
- the seller may not provide fit context.

The question is imprecise but understandable.

The system should not treat weight as sizing truth.

Possible seller guidance may include approximate weight or height context, but it must remain:

- optional;
- seller-provided;
- clearly labeled as guidance;
- never the only sizing rule;
- never a guaranteed fit claim.

The better long-term answer is not an AI sizing engine. It is better confirmed garment measurements and clearer seller guidance.

## 21. Choice and Variant Truth

Seller-facing language should prefer a simple term such as `choice` rather than `variant`.

A choice represents a sellable combination such as:

- size `M`, color `black`;
- size `L`, color `beige`.

Each choice owns its stock quantity.

The source-of-truth boundary is:

- Product owns general identity and product-level facts.
- Choice owns size and color.
- Choice owns quantity.
- Availability is computed from lifecycle and active choice quantities.

A size or color recognized in the description may create a suggestion:

```text
Size M recognized — add to choices?
```

It should not become only a generic tag.

## 22. Operational Product Card

The product card should function as a compact operational control surface.

It should answer, at a glance:

- Which product is this?
- What is the price?
- Is it active, available, low stock, or sold out?
- Which choices exist?
- How much stock remains?
- Is the product ready to answer common questions?
- What is the next useful correction?
- Can I prepare a truthful reply?

The card must not become the entire application.

## 22.1 Product Card Information Priority

Recommended priority:

1. Product image and identity.
2. Price and lifecycle/availability.
3. Choice stock state.
4. Quick stock operation.
5. Readiness or buyer-question coverage.
6. One primary correction/edit action.
7. Ready reply when approved.
8. Secondary actions in a subordinate menu or separate path.

## 22.2 Quick Stock Controls

Stock updates are high-frequency operational actions.

The seller should be able to update a choice without navigating through a long edit form.

Possible approved controls:

- decrement quantity;
- increment quantity;
- direct set when explicitly approved;
- restock path;
- sold-out state as computed feedback;
- visible loading, success, and failure state.

Safety rules:

- quantity cannot become negative;
- the affected size/color must be unmistakable;
- the final server value must replace temporary UI state;
- card totals and dashboard counts must not remain stale;
- repeated taps or network delay must not silently create incorrect stock;
- direct stock set, if included, must be clearly distinguishable from increment/decrement;
- inventory changes should pass through one application service boundary.

## 22.3 Other Fast Operations

Other fast operations may include:

- copy ready reply;
- correct missing price;
- add a missing choice;
- add a recognized material;
- open measurement capture;
- edit the product;
- archive or restore when owner-approved;
- clone when owner-approved;
- choose a primary photo when multiple media support is implemented.

The presence of an operation on the card should depend on frequency, urgency, risk, and mobile density.

Destructive or lifecycle-changing actions should not compete visually with stock updates.

## 23. Readiness Is Not One Percentage

A generic completion percentage is weak product feedback.

For example:

```text
Product complete: 68%
```

does not tell the seller:

- what is missing;
- why it matters;
- which buyer question remains unanswered;
- what action should be taken next.

The product should use buyer-question coverage.

Example:

```text
The assistant can answer:

✓ Price
✓ Available size and color
✓ Remaining stock
✓ Product type
✓ Material

The assistant cannot answer yet:

• Garment length
• Waist measurement
```

The seller then receives one useful action:

```text
+ Add measurements
```

This transforms “data completion” into visible operational value.

## 24. Rewarding the Low-Effort Seller

The system should not reward empty activity, points, or decorative badges.

It should reward the seller by removing future work.

The reward loop is:

1. The seller writes naturally.
2. The system recognizes known vocabulary.
3. The seller sees that order was preserved.
4. One confirmed fact unlocks one answer capability.
5. The seller sees fewer missing-question warnings.
6. A ready reply becomes more complete.
7. Future product entry becomes easier through learned aliases.

Examples of useful reward feedback:

- `Known product type recognized.`
- `Existing tag reused.`
- `Material questions are now covered.`
- `Size M was added to product choices.`
- `This product can now answer stock questions.`
- `One measurement is still missing for length questions.`

The seller should experience enrichment as relief, not administration.

## 25. Deterministic Ready Replies

Ready replies are seller-side tools.

They are not autonomous buyer-facing AI messages in Portfolio V1.

A ready reply may combine:

- product name;
- price;
- confirmed size/color availability;
- stock state;
- confirmed material;
- confirmed measurements;
- seller-provided fit guidance;
- truthful sold-out wording.

Rules:

- only stored facts and computed state may be used;
- missing facts create seller notes, not invented claims;
- sold-out products must produce sold-out wording;
- price, size, color, stock, lifecycle, and availability never come from an LLM guess;
- copy success and copy failure must be visible;
- the seller remains the sender and final reviewer.

A future LLM may help interpret buyer language, but it must not own operational truth.

## 26. Search Experience

Search should match how the seller remembers products.

Useful search inputs may include:

- product description/name;
- Product Type;
- Tags;
- size;
- color;
- confirmed material;
- normalized aliases;
- observed seller wording when safe.

Search should not require the seller to remember internal catalog structure.

The interface should show:

- the active query;
- active filters;
- an obvious clear action;
- a useful no-result state;
- compact mobile behavior.

Fuzzy or morphology-aware search can be deferred until exact normalized vocabulary and alias reuse are reliable.

## 27. Photos

Multiple photos are a general Product Media capability rather than a clothing-specification requirement.

A future media extension may include:

- multiple photos;
- primary photo selection;
- photo ordering;
- optional semantic roles such as front, back, detail, label, closure, or pocket.

The first extension should remain small:

- multiple uploads;
- one primary image;
- stable ordering.

Photo-role classification, image analysis, and label OCR should remain separate decisions.

## 28. Progressive Disclosure

Progressive disclosure protects the product from ecommerce-form expansion.

The first visible product path should contain only information needed to create a usable product.

Secondary or contextual actions may reveal:

- material confirmation;
- detailed measurements;
- fit guidance;
- advanced tags;
- photo ordering;
- secondary lifecycle actions;
- relations if ever approved.

Rules:

- critical information must not be hidden;
- advanced information should appear where it becomes relevant;
- one missing fact should not open a page containing twenty unrelated fields;
- a contextual correction is preferable to a new navigation branch;
- the seller should always know how to return to the previous workspace state.

## 29. Navigation and Return Paths

The seller should not “wander” through the application.

Every edit, correction, detail, or management action should preserve origin context.

Examples:

- Dashboard → low-stock product → update → return to Dashboard;
- filtered Product Workspace → edit → save → return to same query/filter;
- Product Card → add measurement → save → return to the same product context;
- taxonomy recovery → confirm term → return to the product being edited.

Navigation rules:

- every route should have one clear responsibility;
- global navigation should remain compact;
- contextual return should not depend on raw browser referrer behavior;
- POST actions should redirect through a safe return mechanism or deliberate fallback;
- search and filters should survive correction flows.

## 30. Mobile-First Constraints

Phone use is primary.

The interface should assume:

- narrow width;
- one-handed interaction;
- intermittent attention;
- long Georgian labels;
- repeated quick stock updates;
- possible network delay;
- limited tolerance for scrolling.

Mobile rules:

- the first useful action appears early;
- filter controls do not bury products;
- buttons have safe tap targets;
- active size/color choice remains readable;
- destructive actions avoid accidental tap zones;
- stock feedback is immediate and visible;
- long labels wrap without overlap;
- cards remain scannable;
- advanced sections collapse without hiding critical state.

## 31. Feedback and Recovery

Every state-changing action should communicate:

- loading;
- success;
- failure;
- final persisted state;
- recovery path.

Examples:

### Stock update

- show which choice is changing;
- show temporary loading;
- replace with server-confirmed quantity;
- update affected totals and readiness;
- show failure and preserve the previous confirmed value.

### Form validation

- show the error next to the relevant section;
- preserve all entered data;
- avoid returning the seller to an empty form;
- keep the return path visible.

### Recognition

- show what was recognized;
- explain ambiguous meaning;
- allow correction;
- preserve original text;
- avoid silently creating high-impact facts.

### Copy reply

- show copy success;
- show a fallback when clipboard access fails.

## 32. Accessibility Baseline

Compactness should not remove semantic clarity.

Baseline expectations:

- actions use buttons;
- navigation uses links;
- headings remain ordered;
- form fields have labels;
- errors are associated with fields;
- disclosures expose expanded state;
- keyboard and focus behavior are deliberate;
- status is not communicated by color alone;
- images have meaningful alternative text or a clear empty state;
- important asynchronous updates are announced appropriately.

No broad compliance claim should be made until tested.

## 33. Visual Language

The visual system should communicate operational meaning rather than ecommerce decoration.

Recommended qualities:

- compact;
- calm;
- high-contrast;
- mobile-readable;
- action-oriented;
- low ornament;
- stable terminology;
- visible state hierarchy;
- clear distinction between primary, corrective, and destructive actions.

Color may support state, but text or icon meaning must remain present.

Visual color swatches may help with product colors, but the seller-facing color name remains the stable truth because screen color cannot guarantee real fabric color.

## 34. Source-of-Truth Boundaries

The application should keep the following boundaries explicit.

### Product

Owns:

- identity;
- description;
- base price;
- lifecycle;
- Product Type;
- confirmed generic/feature Tags;
- optional confirmed material facts;
- product media.

### Choice

Owns:

- size;
- color;
- quantity;
- active state;
- approved price override only if frozen later.

### Measurement

Owns:

- measurement type;
- value;
- unit;
- method;
- applicability;
- seller note;
- confirmation state.

### Computed State

Includes:

- total stock;
- availability;
- low-stock attention;
- sold-out state;
- readiness;
- buyer-question coverage.

### Reply

Uses:

- confirmed stored facts;
- computed state;
- approved deterministic templates.

The same state should not be independently calculated in multiple templates or UI fragments.

## 35. Architecture Implications

The experience suggests a Django modular monolith with PostgreSQL.

The architecture should support:

- integrated authentication;
- Business ownership isolation;
- relational product and choice data;
- server-side validation;
- transaction-safe stock updates;
- deterministic computed state;
- reusable recognition and normalization services;
- testable ready-reply generation;
- server-rendered pages;
- HTMX for small server-truth updates;
- Alpine.js for local UI disclosure and small interaction state;
- Tailwind CSS for compact responsive layout.

HTMX should refresh server-owned truth.

Alpine.js should not own price, stock, lifecycle, availability, readiness, or confirmed recognition facts.

## 36. Recognition Service Boundary

The recognition system may conceptually perform:

```text
Description
→ normalization
→ existing vocabulary match
→ alias match
→ candidate classification
→ seller confirmation when needed
→ confirmed structured fact
→ search/readiness/reply use
```

It should not become an unrestricted AI extraction system in V1.

Initial recognition can remain deterministic and business-scoped.

Potential recognition outputs:

- existing Product Type;
- existing Tag;
- known material alias;
- size candidate;
- color candidate;
- measurement pattern candidate;
- unclassified search token.

The service should preserve:

- original text;
- canonical value;
- semantic destination;
- confidence or match reason when useful;
- confirmation state.

## 37. Inventory Operation Boundary

Stock is operational truth.

All stock-changing paths should use one domain service boundary rather than updating quantities through unrelated views or templates.

The service should enforce:

- Business ownership;
- valid product choice;
- non-negative quantity;
- atomic update where needed;
- auditable result;
- consistent computed state refresh;
- testable failure behavior.

A complete inventory adjustment trail is desirable, but reason codes and advanced inventory accounting may remain deferred unless frozen in active scope.

## 38. Failure Paths to Design Before Polish

### Recognition failure

A word is matched to the wrong type or material.

Required response:

- show candidate;
- allow correction;
- do not generate precise buyer facts before confirmation.

### Negation failure

The description says a material or feature is absent.

Required response:

- avoid naive positive token extraction;
- preserve text;
- request confirmation when needed.

### Measurement ambiguity

A number lacks method or applicability.

Required response:

- do not present it as precise buyer truth;
- ask for method or mark it incomplete.

### Stale stock

The UI shows a temporary quantity that was not persisted.

Required response:

- replace local state with server-confirmed state;
- expose failure.

### Duplicate choice

The same size/color combination is added twice.

Required response:

- block, merge, or explicitly resolve according to an owner-approved rule.

### Lost return context

The seller edits a filtered product and returns to an unfiltered workspace.

Required response:

- preserve query/filter/origin context through safe return handling.

### Overloaded product card

Too many actions compete on mobile.

Required response:

- preserve action hierarchy;
- move secondary actions out of the primary row.

### Incomplete ready reply

The product lacks material or measurement facts.

Required response:

- provide a truthful partial answer;
- show seller-facing missing-data notes;
- never invent the missing detail.

## 39. Product Success Signals

Early success should be evaluated through behavior and usability, not fabricated business metrics.

Useful qualitative or testable signals include:

- a seller can create a usable product without guidance;
- a seller can find a product using natural remembered wording;
- repeated vocabulary is recognized;
- a seller understands why a recognized term matters;
- a seller updates stock without entering a separate administration area;
- buyer-question coverage identifies a useful missing fact;
- ready replies contain no invented operational truth;
- mobile use does not require excessive route hopping;
- errors preserve data and provide recovery;
- the interface remains smaller than the operational problem it solves.

## 40. Anti-Overengineering Test

Before approving a new feature, ask:

1. Which repeated seller problem does this solve?
2. Which buyer uncertainty does it remove?
3. Does it reduce or increase seller data-entry burden?
4. Can it appear contextually instead of becoming a new page?
5. Does it need a new semantic type, or can it remain a Tag?
6. Does it need to be structured now, or can it remain searchable text?
7. Does a deterministic reply require this fact?
8. Is it current V1 scope or future architecture preparation?
9. What ambiguity or failure path does it introduce?
10. Can the feature be tested as one small micro-slice?
11. Will the product still feel like an assistant after this is added?
12. Would a seller understand the value before doing the work?

A proposal should be deferred when its answer is mainly:

- “ecommerce systems usually have this”;
- “it may be useful one day”;
- “the data model would be more complete”;
- “AI could use it later”;
- “it makes the project look larger.”

## 41. Explicit Product Non-Goals

Portfolio V1 should not become:

- a public buyer catalog;
- a marketplace;
- an autonomous buyer chatbot;
- an LLM-owned product database;
- an order system;
- a reservation system;
- a payment system;
- a delivery system;
- an accounting system;
- supplier management software;
- a broad analytics platform;
- a multi-staff permission suite;
- a universal clothing ontology;
- an AI sizing engine;
- a body-profile database;
- a microservice architecture;
- a large ERP.

## 42. Deferred Capabilities

Potential later work includes:

- public buyer catalog;
- buyer inquiry surface;
- messaging integration;
- LLM-assisted buyer-language interpretation;
- composition-label OCR;
- morphology-aware search;
- richer material normalization;
- detailed measurement templates;
- fit-guidance workflows;
- multiple product photos and primary-image selection;
- photo semantic roles;
- product relations;
- clone workflows;
- archive/restore;
- advanced inventory adjustment history;
- analytics;
- order/payment/delivery workflows.

Deferred does not mean rejected. It means the current seller-assistant loop must prove itself first.

## 43. Owner Decisions Still Required

The following decisions should remain explicit rather than being silently inferred from this document:

- exact Dashboard first-viewport priority;
- final product-card action set;
- ready-reply placement;
- Product Detail existence and purpose;
- relations inclusion or deferral;
- clone inclusion;
- archive/restore inclusion and terminology;
- direct stock set inclusion;
- separate Type/Tag management pages;
- material confirmation interaction;
- alias approval and correction behavior;
- measurement unit;
- flat width versus circumference convention;
- product-level versus size-level measurement applicability;
- initial category measurement templates;
- custom measurement support;
- fit-guidance inclusion;
- final Georgian UI terminology;
- multiple-photo implementation timing;
- demo access and hosting policy.

## 44. Canonical Product Narrative

The project can be explained in one sequence:

1. A social seller posts products with incomplete descriptions.
2. Buyers ask repetitive questions because the product truth is missing.
3. The seller carries the missing catalog in memory and Messenger history.
4. The application provides one compact private workspace.
5. The seller writes naturally in a product description.
6. The system recognizes existing types, tags, aliases, and structured candidates.
7. Confirmed facts become reusable catalog truth.
8. Size, color, and quantity remain structured sellable-choice truth.
9. Operational buttons keep stock current without route hopping.
10. Readiness shows which buyer questions can be answered.
11. Missing information produces one useful correction action.
12. Deterministic ready replies reduce repetitive seller work.
13. The interface rewards better data through immediate usefulness.
14. The product remains an assistant rather than expanding into ecommerce administration.
15. Reliable seller truth becomes the foundation for any later public catalog, chatbot, or automation layer.

## 45. Final Design Statement

The web application should feel smaller than the chaos it manages.

Its intelligence is not the number of fields, screens, or AI features it contains.

Its intelligence is visible when:

- a repeated word becomes a stable vocabulary term;
- a misspelling becomes a reusable alias;
- a description becomes searchable truth;
- a size/color phrase becomes a valid product choice;
- one material fact removes a repeated buyer question;
- one stock button keeps availability honest;
- one missing-data signal produces one useful correction;
- one ready reply saves another Messenger explanation;
- the seller stays inside a compact operational flow.

The product succeeds when the seller does less administrative work while the system knows more reliable truth.

That is the central design boundary:

> Assistant-first seller operations, not another ecommerce site where the seller has to wander.
