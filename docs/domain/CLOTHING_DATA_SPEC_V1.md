# Clothing Data Spec V1

## Document Metadata

- Status: DRAFT_FOR_OWNER_REVIEW
- Version: 1.1-draft
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Scope: clothing-specific truth, semantic recognition, and optional measurement support
- Freeze authority: owner only
- Code generation: forbidden by this document alone

## 1. Purpose

This document defines the clothing-data boundary for the clean rebuild.

The product is not intended to become another large ecommerce catalog or a spreadsheet-like product form. Its purpose is to help a busy or inconsistent social-commerce seller turn a short, imperfect product description into usable product truth, better search, clearer readiness signals, and deterministic buyer replies.

The primary interaction model is:

```text
seller description
→ recognized terms
→ normalized meaning
→ seller confirmation only where needed
→ structured facts
→ search, readiness, and buyer-question coverage
```

The system should absorb seller inconsistency without forcing the seller to understand a complex data model.

## 2. Product Principle

### Simple input, structured truth

A simple seller interface does not require a weak backend model.

The seller may mainly use one description field, while the system separately maintains:

- product type;
- generic and feature tags;
- material facts;
- size/color choices;
- quantity;
- optional measurements;
- aliases and normalized vocabulary;
- buyer-question coverage.

The seller should not be asked to classify every word manually.

### Assistant, not form bureaucracy

The system should:

- recognize already known vocabulary;
- reuse the seller's previous corrections;
- show what was understood;
- ask only when meaning is ambiguous;
- explain the practical value of adding information;
- avoid one giant clothing form;
- avoid completion percentages that feel like administrative work.

## 3. Input and Truth Layers

The system must distinguish three layers.

### 3.1 Observed text

Raw seller wording from the product description.

Examples:

- `პოლიესტირი`
- `M-ზომა`
- `წელი 38 სმ`
- `კლასიკური შარვალი ჯიბეებით`

Observed text is useful for search and recognition, but it is not automatically trusted as structured buyer-facing truth.

### 3.2 Recognized candidate

A term or phrase matched to an existing vocabulary item, alias, pattern, or structured concept.

Examples:

- `პოლიესტირი` → candidate for `პოლიესტერი`
- `M-ზომა` → candidate for size `M`
- `შარვალი` → candidate for product type
- `ჯიბეებით` → candidate for feature tag `ჯიბეები`

A candidate may be shown immediately in the UI.

### 3.3 Confirmed fact

A seller-approved or safely persisted structured value.

Only confirmed facts may drive deterministic buyer replies for:

- material composition;
- size and color;
- measurements;
- stock;
- price;
- lifecycle;
- availability.

Generic description text may still be used in a description reply, but the assistant must not convert uncertain wording into a precise factual claim.

## 4. Semantic Destinations

Recognized content should be routed to a small set of semantic destinations.

| Destination | Purpose | Source of Truth |
|---|---|---|
| Product Type | What kind of product it is | Confirmed business product type |
| Generic / Feature Tag | Search, grouping, style, detail, occasion | Confirmed business tag |
| Material | Fabric or composition fact | Confirmed material fact |
| Choice — Size | Sellable size option | Product choice/variant |
| Choice — Color | Sellable color option | Product choice/variant |
| Measurement | Garment measurement with method and unit | Confirmed measurement record |
| Search Token | Search support only | Normalized observed text |

The initial system should not create a large ontology for style, fit, closure, lining, care, opacity, occasion, silhouette, and other attributes.

Unless a separate buyer-facing or operational rule needs them, these remain Generic / Feature Tags.

## 5. Vocabulary Normalization and Alias Learning

The system should help the seller fight inconsistent wording over time.

Example:

```text
seller wording: პოლიესტირი
canonical value: პოლიესტერი
semantic type: material
```

Possible aliases:

```text
პოლიესტირი
პოლუესტერი
პოლიესტირის
```

All may resolve to the same canonical value:

```text
პოლიესტერი
```

Rules:

- The seller should correct an unfamiliar term once, not on every product.
- Future uses of the same alias should be recognized automatically.
- Search should match both aliases and canonical values.
- Buyer replies should use the canonical value.
- Alias learning should be business-scoped unless a globally reviewed vocabulary is introduced later.
- A negative phrase such as `პოლიესტერი არ აქვს` must not become a positive material fact through naive token matching.

## 6. Description-First Recognition Contract

The product description is the primary seller capture surface.

While the seller types, the system may show:

```text
ამოვიცანი:

[ტიპი · შარვალი]
[თეგი · კლასიკური]
[დეტალი · ჯიბეები]
[მასალა · ბამბა]
[ზომა · M → არჩევანში დამატება]
```

Interaction rules:

- Known terms are recognized automatically.
- Existing product types and tags are highlighted as reused vocabulary.
- New ambiguous terms are not silently persisted as facts.
- The seller is asked only for unresolved or high-impact meaning.
- The seller may remove or correct a mistaken recognition.
- Size/color candidates should be offered for transfer into choices, not stored as generic tags.
- Material candidates should be stored as material facts, not ordinary generic tags.
- Unclassified text may remain searchable without forcing classification.

## 7. Existing Core Data That Remains Structured

The following must not be reduced to free text.

### 7.1 Product-level facts

- product description/name;
- base price;
- currency;
- lifecycle;
- product type;
- confirmed generic/feature tags;
- optional confirmed material facts.

### 7.2 Choice/variant-level facts

- size;
- color;
- quantity;
- active/inactive state;
- optional approved price override.

Quantity remains the stock source of truth at choice/variant level.

Size and color detected in the description may create suggestions, but confirmed choices remain the source of truth.

## 8. Material Contract

Material deserves a separate semantic type because it can affect buyer comfort, allergy concerns, washing expectations, and precise buyer replies.

The seller should not be forced into a separate large material form.

Recommended interaction:

1. seller writes material information in the description;
2. the system recognizes known material names and aliases;
3. the system shows material candidates;
4. the seller confirms or corrects only when needed;
5. the assistant may then answer material questions.

Material fact direction:

| Field | Requirement |
|---|---|
| canonical material | Required for a confirmed material fact |
| percentage | Optional |
| original seller wording | Preserved for traceability |
| confirmation state | Required |
| source | Description, manual selection, or future label-photo extraction |

Examples:

```text
100% ბამბა
70% ბამბა, 30% პოლიესტერი
ატლასი
შიფონი
```

Important boundary:

Everyday seller fabric names may be commercially useful but not technically equivalent to fiber composition. The system should preserve seller wording and avoid inventing scientific composition.

A composition-label photo is a useful future capture method, but label OCR or automatic extraction is not part of this document's V1 implementation commitment.

## 9. Size Contract

General size labels such as `M`, `XL`, `38`, or `Free size` are not sufficient for many clothing buyers, but they remain useful choice identifiers.

Rules:

- Size belongs to a product choice/variant.
- A size detected in the description may be suggested for a choice.
- Size must not be stored only as a generic tag.
- `Free size` is a seller label, not a guarantee that the garment fits every body.
- Approximate weight must never be the sole sizing rule.
- The assistant must not guarantee fit.

Detailed garment measurements are handled separately.

## 10. Measurement Capability

Measurements are important because a general size label often does not answer real buyer questions.

However, measurement support must not become a mandatory spreadsheet.

### 10.1 Measurement record boundary

A confirmed measurement needs:

| Field | Meaning |
|---|---|
| measurement type | waist, chest/bust, garment length, sleeve length, inseam, rise, thigh, shoulder width, hem width, or approved custom type |
| value | numeric measurement |
| unit | centimeters by default for V1 |
| method | flat width, half-width, circumference, or another frozen convention |
| applies to | product or a specific size/choice where required |
| seller note | optional clarification |
| confirmation state | confirmed before buyer reply use |

### 10.2 Why the method is required

`წელი 38 სმ` may mean:

- flat garment width;
- half circumference;
- full circumference;
- recommended body measurement.

A precise-looking value without a measurement method is unsafe.

### 10.3 UX direction

Measurements should appear behind a deliberate optional action:

```text
+ გაზომვების დამატება
```

The system should show category-relevant prompts rather than every possible field.

Examples:

- trousers: waist, hip, inseam, rise, thigh, garment length;
- tops: chest/bust, shoulder width, sleeve length, garment length;
- dresses: chest/bust, waist, hip, garment length;
- jackets: chest/bust, shoulder width, sleeve length, garment length;
- skirts: waist, hip, garment length.

The seller should also be able to add an approved custom measurement when the standard list does not fit the garment.

### 10.4 Description recognition

If the seller writes:

```text
წელი 38 სმ, სიგრძე 102 სმ
```

the system may propose:

```text
ამოვიცანი გაზომვები:

წელი — 38 სმ
სიგრძე — 102 სმ
```

Before confirmation, the system must ask or reuse the seller's saved convention:

```text
გაზომილია:
[გაშლილ ტანსაცმელზე] [სრული გარშემოწერილობა]
```

### 10.5 V1 boundary

The architecture should preserve the ability to add measurements.

The initial Portfolio V1 does not need every measurement template fully implemented before the core seller workflow works.

Measurement implementation should be a separate approved micro-slice after:

- measurement convention is frozen;
- category prompts are reviewed;
- the form remains compact;
- buyer-reply wording is defined;
- manual testing confirms sellers understand what to enter.

## 11. Fit Guidance

Fit guidance is seller-provided context, not deterministic sizing truth.

Possible optional guidance:

- runs small;
- runs large;
- relaxed fit;
- fabric stretches;
- approximate height guidance;
- approximate weight guidance;
- seller note.

Rules:

- Weight alone never determines size.
- The assistant must not make medical, biometric, or guaranteed-fit claims.
- Fit guidance must be visibly described as seller guidance.
- Body-profile storage and AI sizing are not V1.

## 12. Buyer-Question Coverage

Readiness should not be shown as a generic completion percentage.

The system should explain concrete answer capability.

Example:

```text
ასისტენტს შეუძლია უპასუხოს:

✓ ფასი
✓ ხელმისაწვდომი ზომა და ფერი
✓ ნაშთი
✓ პროდუქტის ტიპი
✓ მასალა

ჯერ ვერ პასუხობს:

• ტანსაცმლის სიგრძე
• წელის ზომა
```

The next recommendation should be one small action, for example:

```text
+ გაზომვების დამატება
```

This creates an immediate reward for richer data without turning the workflow into form completion work.

## 13. Photo Boundary

Multiple product photos are a general Product Media capability, not a clothing-data requirement.

The future media extension may support:

- multiple photos;
- one primary photo;
- photo ordering;
- later optional roles such as front, back, detail, label, closure, or pocket.

This document does not require photo-role classification or image analysis.

## 14. Portfolio V1 Recommendation

### Required core

- description-first input;
- product type recognition;
- generic/feature tag recognition;
- business-scoped alias normalization;
- size/color/quantity choices;
- variant-level stock truth;
- deterministic buyer replies from confirmed facts;
- buyer-question coverage feedback.

### Recommended small extension

- material as a typed semantic fact;
- material alias normalization;
- optional percentage;
- material answer coverage.

### Architecturally prepared but separately implemented

- category-relevant garment measurements;
- measurement method/convention;
- description-to-measurement candidate recognition;
- optional seller fit guidance;
- multiple photos and primary-photo selection.

### Deferred

- AI sizing;
- automatic fit recommendation;
- body profile;
- public buyer catalog;
- chatbot integration;
- label-photo OCR;
- universal textile ontology;
- mandatory full specification forms;
- orders, reservations, payment, and delivery.

## 15. Source-of-Truth Rules

- Description text is the primary seller input, not the universal source of structured truth.
- Product type and tags are confirmed business vocabulary.
- Material replies use confirmed material facts.
- Size and color use confirmed product choices.
- Quantity uses variant-level stock.
- Measurements use confirmed values with unit and method.
- Availability is computed from lifecycle and active choice quantities.
- Search may use normalized observed text and aliases.
- Deterministic replies must not promote uncertain search tokens into factual claims.
- Missing information creates seller-facing prompts, not invented buyer answers.

## 16. Anti-Overengineering Rules

- Do not create one field for every possible clothing characteristic.
- Do not make advanced clothing details mandatory.
- Do not ask the seller to classify every token.
- Do not create a universal fashion ontology in V1.
- Do not treat every tag as buyer-facing truth.
- Do not use size or weight as guaranteed fit.
- Do not implement the entire measurement subsystem inside the initial product-form micro-slice.
- Do not add a new page when a small contextual interaction is sufficient.
- Do not add architecture that has no current search, reply, readiness, or seller-workflow use.

## 17. Owner Decisions Required Before Measurement Implementation

- Default measurement unit.
- Flat width versus circumference convention.
- Whether the convention is business-wide, category-specific, or per measurement.
- Whether measurements belong to the product, a size/choice, or both.
- Initial supported category templates.
- Whether custom measurement types are allowed in V1.
- Whether approximate fit guidance appears in V1.
- Exact buyer-reply wording for measurements.
- Exact seller UI for confirming recognized measurements.

## 18. Explicit Non-Goals

- No large ecommerce specification form.
- No AI sizing.
- No guaranteed fit.
- No buyer body-profile storage.
- No universal material science database.
- No public catalog implementation from this document alone.
- No model, migration, form, or UI generation without an approved micro-slice.
- No requirement that every product contains every clothing fact.
