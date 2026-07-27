# Clothing Data Spec V1

## Document Metadata

- Status: DRAFT_FOR_OWNER_REVIEW
- Version: 1.0-draft
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Scope: structured clothing product data for Portfolio MVP planning
- Freeze authority: owner only
- Code generation: forbidden by this document

## 1. Purpose

This document defines the clothing-specific data boundary for the clean rebuild before product scope is frozen.

The goal is to make clothing product truth useful for sellers and deterministic buyer replies without turning the MVP into an AI sizing engine, public catalog, or broad ERP.

## 2. Scope Rules

- Not every clothing category requires every measurement.
- Measurements must be category-specific and optional unless the owner freezes them as required for a category.
- Weight alone must not determine size or fit.
- Fit guidance is seller-provided guidance, not a medical, biometric, or AI sizing guarantee.
- Variant-level stock remains separate from product-level clothing attributes.
- Do not add every field directly to `Product`.
- Do not implement models, migrations, forms, AI sizing, buyer catalog, orders, payments, or delivery from this document alone.

## 3. Product-Level Clothing Attributes

Product-level attributes describe the garment itself. They apply across all variants unless the owner later approves a more granular exception.

| Attribute | Meaning | Requirement Direction | Notes |
|---|---|---|---|
| Material composition | Fabric/material makeup, such as cotton, polyester, wool, elastane, or mixed composition | Optional by default; category dependent | Should support plain seller wording first; structured percentages can be future work |
| Fit type | How the garment is intended to fit the body | Optional by default | Examples: slim, regular, relaxed, oversized, fitted |
| Stretch | Whether the fabric stretches | Optional by default | Examples: none, slight, medium, high |
| Silhouette/cut | Shape or cut of the garment | Optional by default; category dependent | Examples: A-line, straight, skinny, wide-leg, cropped, bodycon |
| Garment length type | Seller-friendly length category | Optional by default; category dependent | Examples: mini, midi, maxi, cropped, regular, long |
| Care | Washing/care guidance | Optional by default | Keep concise; avoid complex textile-care modeling in V1 |
| Lining | Whether the garment has lining | Optional by default | Useful for dresses, skirts, jackets, outerwear |
| Opacity | How transparent the garment is | Optional by default | Useful for light fabrics, dresses, tops, skirts |
| Closure | How the garment closes | Optional by default; category dependent | Examples: zipper, buttons, elastic waist, tie, hook, pullover |

## 4. Category-Specific Measurement Templates

Measurement templates define which measurements are useful for a category. They do not make every field globally required.

| Category Template | Common Measurements | Optional Measurements | Notes |
|---|---|---|---|
| Tops and blouses | chest/bust, shoulder width, sleeve length, garment length | waist, hem width | Use for shirts, blouses, T-shirts, sweaters |
| Dresses | chest/bust, waist, hip, garment length | shoulder width, sleeve length, hem width | Length type is often useful |
| Jackets and outerwear | chest/bust, shoulder width, sleeve length, garment length | waist, hem width | Lining and closure are often useful |
| Pants and jeans | waist, hip, inseam, rise, thigh, hem width | garment length | Stretch and cut are often important |
| Skirts | waist, hip, garment length, hem width | rise | Lining and opacity are often useful |
| Shorts | waist, hip, inseam, rise, thigh, hem width | garment length | Similar to pants but shorter length |
| Sets | category-specific measurements for each main piece | seller fit note | Avoid forcing one measurement shape across all pieces |

## 5. Measurement Definitions

| Measurement | Description | Applies Often To |
|---|---|---|
| Chest/bust | Garment width or circumference around chest/bust area, depending on owner-approved measurement convention | Tops, dresses, jackets |
| Waist | Garment waist measurement | Dresses, pants, skirts, shorts |
| Hip | Garment hip measurement | Dresses, pants, skirts, shorts |
| Shoulder width | Shoulder-to-shoulder garment measurement | Tops, jackets, dresses |
| Sleeve length | Sleeve measurement | Tops, jackets, long-sleeve dresses |
| Garment length | Total garment length by category convention | Most categories |
| Inseam | Inside-leg length | Pants, jeans, shorts |
| Rise | Waist-to-crotch rise | Pants, jeans, shorts |
| Thigh | Thigh width/circumference area | Pants, jeans, shorts |
| Hem width | Opening width at bottom edge | Tops, pants, skirts, dresses |

OWNER_DECISION_REQUIRED: Freeze whether measurements are stored as flat garment measurements, circumference, half-width, centimeters only, or another seller-friendly convention.

## 6. Variant-Level Data

Variant-level data describes the sellable choice and stock.

| Field | Meaning | Requirement Direction | Notes |
|---|---|---|---|
| Size | Seller-facing size label | Required for sellable clothing choices | Examples: XS, S, M, L, XL, 36, 38, one size |
| Color | Seller-facing color label | Required for sellable clothing choices unless owner approves colorless categories | Keep seller wording stable |
| Quantity | Stock truth for the choice | Required; cannot be negative | Quantity belongs to the variant/choice, not product |
| Optional approved price override | Variant-specific price | OWNER_DECISION_REQUIRED | Only if approved; product base price remains simpler for V1 |

Variant data must stay separate from product-level garment attributes. A product may have one material and fit, while each size/color choice has its own quantity.

## 7. Fit Guidance

Fit guidance helps the seller answer sizing questions without pretending the system can guarantee fit.

| Guidance | Meaning | Requirement Direction | Notes |
|---|---|---|---|
| Body measurement ranges | Suggested body ranges for a size | Optional and category dependent | Can include bust/chest, waist, hip ranges |
| Height range | Seller-provided height guidance | Optional | Useful for garment length expectations |
| Approximate weight range | Seller-provided approximate guidance | Optional | Must never be the only sizing truth |
| Seller fit note | Free text note from seller | Optional | Examples: runs small, loose fit, fabric stretches, size up |

Rules:

- Weight alone must not determine size.
- Fit guidance should support seller judgment, not replace it.
- No AI sizing or automated recommendation is in V1.
- Buyer-facing sizing automation remains deferred.

## 8. Source-of-Truth Boundary

- Product-level clothing facts are seller-maintained facts.
- Size and color are variant/choice facts.
- Quantity is variant/choice stock truth.
- Availability is computed from lifecycle and active choice quantities.
- Fit guidance is seller-entered guidance.
- Deterministic replies may use these facts only when present.
- Missing clothing facts must produce seller-facing prompts or notes, not invented buyer claims.

## 9. Portfolio V1 Use

Portfolio V1 should implement only the subset of this spec that the owner freezes.

Recommended minimum:

- Product-level clothing profile boundary exists.
- Variant/choice records include size, color, and quantity.
- Category-specific measurements are documented before model work begins.
- Product forms do not require every measurement.
- UI keeps advanced clothing data behind progressive disclosure.
- Deterministic replies never invent material, fit, measurements, or sizing guidance.

OWNER_DECISION_REQUIRED:

- Which product-level attributes are included in V1.
- Which category templates are included in V1.
- Which measurements are required, optional, or deferred by category.
- Whether approximate fit guidance appears in V1.
- Whether variant price override is included in V1.

## 10. Explicit Non-Goals

- No AI sizing.
- No buyer catalog implementation.
- No public fit recommendation engine.
- No body-profile storage.
- No order/reservation/payment/delivery scope.
- No migration or model design generated by this document alone.
- No requirement that every product has every clothing field.
