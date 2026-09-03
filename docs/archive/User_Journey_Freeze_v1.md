# User Journey Freeze V1

## Document Metadata

- Status: FROZEN
- Version: 1.0
- Freeze authority: owner only
- Frozen boundary: `OWNER_DECISION_REQUIRED` journeys remain deferred unless separately approved

## 1. Journey Purpose

RECOMMENDED_FROM_EVIDENCE: These journeys protect the rebuild from route and UI chaos by defining what the seller is trying to accomplish, what context must be preserved, what feedback is required, and which paths are explicitly deferred. They are now the owner-controlled journey baseline for Phase 1, while `OWNER_DECISION_REQUIRED` journeys remain deferred until separately approved.

VALIDATED_PROTOTYPE_LESSON: The source prototype became useful but dense because product creation, stock updates, readiness, replies, taxonomy, clone, archive, and relations were repeatedly added to the same surfaces. The rebuild should make each journey explicit before screens are built.

## 2. Primary User

OWNER_PROVIDED_DIRECTION: The primary user is a seller who personally maintains products, choices, price, stock, and answer-readiness for a small Facebook/Instagram commerce operation.

RECOMMENDED_FROM_EVIDENCE: V1 should assume a single authenticated seller operating one active business workspace. Buyer, staff, delivery, and chatbot journeys are future users and remain deferred.

## 3. Core Journey Principles

- RECOMMENDED_FROM_EVIDENCE: The seller always knows where they are.
- RECOMMENDED_FROM_EVIDENCE: Every page has one primary responsibility.
- RECOMMENDED_FROM_EVIDENCE: Return paths are explicit.
- RECOMMENDED_FROM_EVIDENCE: The seller does not depend on browser Back.
- RECOMMENDED_FROM_EVIDENCE: Product truth updates remain visible after interaction.
- OWNER_PROVIDED_DIRECTION: Mobile is the primary interaction environment.
- RECOMMENDED_FROM_EVIDENCE: The system reduces memory burden by surfacing missing data, stock state, and answer readiness.
- RECOMMENDED_FROM_EVIDENCE: The system never invents product truth.
- OWNER_PROVIDED_DIRECTION: Product description is the primary seller input.
- OWNER_PROVIDED_DIRECTION: Recognized text is separated into observed text, candidate meaning, and confirmed structured fact.
- OWNER_PROVIDED_DIRECTION: Readiness appears as buyer-question coverage, not completion percentage.

## 4. Global Navigation Journey

RECOMMENDED_FROM_EVIDENCE: Top-level navigation should be limited to the work surfaces needed for V1:

- Dashboard: what needs attention now.
- Product workspace: daily catalog and stock operations.
- Add product: create a new product truth bundle.
- Account/logout: secure session exit.

Acceptance criteria:

- RECOMMENDED_FROM_EVIDENCE: Current location is visible.
- RECOMMENDED_FROM_EVIDENCE: Navigation does not replace contextual return links.
- RECOMMENDED_FROM_EVIDENCE: Navigation labels avoid ERP or developer terminology.
- RECOMMENDED_FROM_EVIDENCE: Mobile layout preserves tap targets and does not bury primary work.

## 5. First Product Creation Journey

- Start state: seller is signed in and has an active business workspace.
- User intent: add a product that can later be found, stocked, and answered about.
- Entry route: Add Product from global nav, dashboard, or empty product workspace.
- Steps:
  1. Enter product description/name as the primary seller input.
  2. Enter price according to owner-approved price rule.
  3. System shows recognized candidates from the description: existing Product Type, Tags, material, and size/color suggestions.
  4. Seller confirms or corrects high-impact candidates.
  5. Choose lifecycle status if exposed.
  6. Confirm or create product type if type is in scope.
  7. Confirm optional tags if tags are in scope.
  8. Confirm material if recognized or manually added.
  9. Add at least one size/color/quantity choice, including any size/color suggestion the seller accepts.
  10. Optionally add product media.
  11. Save.
- System response: product, confirmed facts, choices, media reference, and optional tags are saved as one product bundle.
- Validation/failure path: missing required fields show field-level errors; missing choice shows formset-level error; file/media failure must not leave an unexplained partial product.
- Success state: product appears in the operational workspace with computed availability and buyer-question coverage.
- Return path: seller returns to originating dashboard/workspace context or sees a clear next action.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: no product can be saved without at least one valid choice unless owner explicitly approves drafts without choices.
  - RECOMMENDED_FROM_EVIDENCE: successful save does not require browser Back.
  - RECOMMENDED_FROM_EVIDENCE: validation returns seller to the exact problem.
- RECOMMENDED_FROM_EVIDENCE: category-specific clothing measurements do not require every measurement for every product.
- RECOMMENDED_FROM_EVIDENCE: weight alone is never accepted as reliable sizing truth.
- OWNER_PROVIDED_DIRECTION: detailed garment measurements are not required in the first product-creation journey and remain a separate approved micro-slice.
- OWNER_PROVIDED_DIRECTION: buyer replies may use confirmed material facts but not unconfirmed recognition candidates.
- Explicit exclusions: buyer catalog page, order creation, payment, delivery, chatbot, LLM field generation.

## 6. Add Multiple Size/Color Choices

- Start state: seller is on product create/edit.
- User intent: represent available selling choices accurately.
- Entry route: product create or edit form.
- Steps:
  1. Add a choice row.
  2. Select size.
  3. Select color.
  4. Enter quantity.
  5. Add optional approved price override only if V1 scope allows it.
  6. Repeat for each real choice.
  7. Save.
- System response: active choices are stored as variant-level stock records.
- Validation/failure path: incomplete rows are ignored only if empty; partially filled rows show errors; deleting all active choices is blocked unless product draft behavior is owner-approved.
- Success state: product card shows each active choice and stock.
- Return path: back to originating list/dashboard context.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: quantity cannot be negative.
  - RECOMMENDED_FROM_EVIDENCE: active product availability uses active choices only.
  - OWNER_PROVIDED_DIRECTION: duplicate `ProductChoice` rows with the same case-insensitive, trim-normalized size and color are allowed in V1 as distinct sellable choices. They are not merged automatically; later inventory changes must target a specific row. Aggregation, buyer-facing wording, and UI disambiguation for visually similar choices remain deferred to later approved slices.
- Explicit exclusions: matrix generator, SKU system, warehouse bins, supplier stock.

## 7. Update Stock

- Start state: seller sees product choices in the workspace or focused product surface.
- User intent: adjust stock quickly after a sale, correction, or restock.
- Entry route: product workspace card; OWNER_DECISION_REQUIRED for detail-only direct set.
- Steps:
  1. Choose `+1`, `-1`, or direct set if approved.
  2. System validates quantity.
  3. Inventory service writes the stock change.
  4. UI refreshes product state.
- System response: variant quantity, product total, availability, readiness, and buyer reply state update from server truth.
- Validation/failure path: decrement below zero is blocked; invalid set quantity shows an error and recovery path; failed HTMX request shows visible retry guidance.
- Success state: seller sees new quantity and any availability transition.
- Return path: stay in current workspace context.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: every stock mutation goes through one inventory service.
  - RECOMMENDED_FROM_EVIDENCE: every stock mutation creates an adjustment record.
  - RECOMMENDED_FROM_EVIDENCE: surrounding counts or grouping do not silently remain stale.
- Explicit exclusions: reservation, order decrement, payment-driven stock changes, stock movement reason codes unless owner adds them later.

## 8. Sold-Out Transition

- Start state: active product has one or more active choices with positive stock.
- User intent: record final sale or correction that makes stock zero.
- Entry route: stock update control.
- Steps:
  1. Seller decrements or sets final positive quantity to zero.
  2. System recomputes availability.
  3. Product becomes sold out when all active choices are zero or no active sellable stock remains.
- System response: sold-out state appears in workspace, dashboard signal, readiness/reply output, and filters consistently.
- Validation/failure path: concurrent updates must not produce incorrect stock or duplicate misleading logs.
- Success state: no manual mark-sold-out step is required.
- Return path: seller remains in current context and can move to sold-out view explicitly.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: sold-out is computed, not manually stored.
  - RECOMMENDED_FROM_EVIDENCE: buyer reply does not claim availability when sold out.
  - RECOMMENDED_FROM_EVIDENCE: UI transition feedback is visible.
- Explicit exclusions: order/reservation sold-out logic.

## 9. Restock Transition

- Start state: active product is sold out.
- User intent: make product available again by adding stock.
- Entry route: sold-out product in workspace or approved focused product surface.
- Steps:
  1. Seller increments or sets a positive quantity on one active choice.
  2. System recomputes availability.
  3. Product returns to available/low-stock state depending on quantity.
- System response: visible restock feedback and updated answer readiness.
- Validation/failure path: invalid quantity shows error; failed partial update can be retried or full page refreshed.
- Success state: buyer reply can truthfully include available choices.
- Return path: stay in current context.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: restock transition is server-computed.
  - RECOMMENDED_FROM_EVIDENCE: list/dashboard counts do not become stale in final V1.
- Explicit exclusions: supplier replenishment, purchase orders, delivery status.

## 10. Find a Product

- Start state: seller is in product workspace.
- User intent: locate a product by description, alias-normalized observed text, confirmed type, tag, size, color, material, or status.
- Entry route: product workspace search/filter controls.
- Steps:
  1. Enter search term or select approved filter.
  2. System applies visible URL-backed search/filter state.
  3. Seller opens or edits a result.
- System response: result count, active filters, clear action, and no-result state are visible.
- Validation/failure path: empty result gives suggestions; unsupported fuzzy/morphology expectations are not promised.
- Success state: seller finds product and can act without losing filter context.
- Return path: edit/detail save returns to the same filtered context.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: filtered context survives drilldowns.
  - OWNER_DECISION_REQUIRED: exact filter set for V1.
- Explicit exclusions: AI search, typo tolerance, public catalog search, Georgian morphology beyond documented normalization.

## 11. Fix Missing Information

- Start state: dashboard/workspace shows readiness or attention signal.
- User intent: complete data needed for selling or buyer answer.
- Entry route: dashboard attention, readiness filter, product card action, or ready-reply note.
- Steps:
  1. Open correction action.
  2. Land on focused correction or full edit surface.
  3. Update missing facts.
  4. Save.
- System response: buyer-question coverage recomputes and missing-data signal disappears or changes.
- Validation/failure path: invalid field remains visible with specific message.
- Success state: product is closer to answer-ready or fully ready.
- Return path: return to originating dashboard/workspace/filter.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: missing-data actions use contextual labels where possible.
  - RECOMMENDED_FROM_EVIDENCE: correction journey is not buried in unrelated form sections.
- Explicit exclusions: chatbot asks seller for missing data; automated AI correction.

## 12. Prepare a Deterministic Buyer Reply

- Start state: product has enough stored facts for at least one reply mode.
- User intent: answer a buyer accurately without retyping facts from memory.
- Entry route: product card or owner-approved reply surface.
- Steps:
  1. Open ready reply.
  2. Choose reply mode.
  3. Review generated text.
  4. Copy reply.
  5. If missing data exists, follow correction link.
- System response: text is generated only from confirmed structured facts and computed state.
- Validation/failure path: unconfirmed recognition candidates and missing facts produce seller notes, not invented buyer facts; copy failure shows recovery.
- Success state: seller can paste a truthful answer externally.
- Return path: no route change unless correction is needed; correction returns to origin.
- Acceptance criteria:
  - RECOMMENDED_FROM_EVIDENCE: LLM is not used as source of truth.
  - RECOMMENDED_FROM_EVIDENCE: sold-out wording is truthful.
  - RECOMMENDED_FROM_EVIDENCE: internal warnings do not leak as buyer-facing claims.
- OWNER_PROVIDED_DIRECTION: recognized material can be used only after confirmation.
- Explicit exclusions: sending messages, chatbot, Meta integration, buyer-facing API.

## 13. Clone or Add Similar Product

- Status: OWNER_DECISION_REQUIRED for Portfolio V1.
- Start state: seller has an existing similar product.
- User intent: reduce repetitive data entry.
- Entry route: product workspace clone action if approved.
- Steps:
  1. Choose clone mode.
  2. System creates draft copy.
  3. Seller edits distinguishing fields.
  4. Save.
- System response: copy opens in edit with rename/change nudge.
- Validation/failure path: invalid clone mode is rejected; copied stock behavior follows owner-approved rule.
- Success state: similar product is created without phantom active stock.
- Return path: original workspace/filter context is preserved.
- Acceptance criteria:
  - OWNER_DECISION_REQUIRED: exact clone modes and stock-copy policy.
  - RECOMMENDED_FROM_EVIDENCE: clones should default to draft.
- Explicit exclusions: bulk import, catalog scraping, AI product creation.

## 14. Archive and Restore

- Status: OWNER_DECISION_REQUIRED for Portfolio V1.
- Start state: seller has active/draft product that should leave daily operations.
- User intent: remove product from active work without deleting history.
- Entry route: product workspace action.
- Steps:
  1. Archive product with confirmation.
  2. Product leaves active operational view.
  3. Seller can view archive.
  4. Restore if needed.
- System response: lifecycle changes and availability is recomputed.
- Validation/failure path: archive/restore failure shows message and recovery.
- Success state: product lifecycle is explicit and reversible.
- Return path: current workspace context is preserved.
- Acceptance criteria:
  - OWNER_DECISION_REQUIRED: whether hidden and archived are separate V1 concepts.
  - RECOMMENDED_FROM_EVIDENCE: archived products are not buyer-answer/sellable by default.
- Explicit exclusions: hard delete, public unpublish workflow, order cancellation.

## 15. Error Recovery Journeys

- Invalid form: RECOMMENDED_FROM_EVIDENCE: show field errors, non-field errors, and preserve typed data.
- Missing required choice: RECOMMENDED_FROM_EVIDENCE: show a clear choice-level or formset-level error and path to add a choice.
- Negative quantity: RECOMMENDED_FROM_EVIDENCE: block write, show error, preserve current product context.
- Stale filter context: RECOMMENDED_FROM_EVIDENCE: preserve `next` or URL state across edit/detail/return.
- Failed HTMX request: RECOMMENDED_FROM_EVIDENCE: show visible retry/full-refresh recovery instead of silent failure.
- Missing image: RECOMMENDED_FROM_EVIDENCE: show placeholder and readiness signal, not a broken layout.
- Unauthorized object access: RECOMMENDED_FROM_EVIDENCE: return 404 or forbidden without leaking cross-business object existence.

## 16. Navigation and Return-Path Matrix

| Journey | Start | Destination | Context to Preserve | Explicit Return | Failure Recovery |
|---|---|---|---|---|---|
| First product creation | Dashboard/workspace | Description-first create form | Origin route | Return/cancel link | Same form with errors |
| Add choices | Product form | Same form | Current product/form data | Save/cancel | Row errors and add-choice action |
| Update stock | Product workspace | Same product card | Current filters/tab/search | Stay in place | Visible HTMX error/retry |
| Sold-out transition | Product workspace | Sold-out state | Current filters plus transition | Stay or sold-out link | Refresh/retry |
| Restock transition | Sold-out view | Available state | Current filters/tab | Stay or active link | Refresh/retry |
| Find product | Workspace | Filtered result | Query/filter URL | Clear filters | No-result guidance |
| Fix missing info | Dashboard/card | Edit/correction | Dashboard/list/detail origin | Return link and post redirect | Field errors |
| Prepare reply | Card/reply surface | Clipboard | Product/card context | No route change | Copy failure message |
| Clone similar product | Card/detail | Edit cloned draft | Source list/filter | Return link after edit | Invalid mode message |
| Archive/restore | Card | List state | Current list/filter | Redirect to origin | Message and unchanged state |

## 17. Journey Acceptance Checklist

- RECOMMENDED_FROM_EVIDENCE: Every journey starts from a defined route.
- RECOMMENDED_FROM_EVIDENCE: Every mutation has a success and failure path.
- RECOMMENDED_FROM_EVIDENCE: Every drilldown has explicit return context.
- RECOMMENDED_FROM_EVIDENCE: Every state transition is visible in the UI.
- RECOMMENDED_FROM_EVIDENCE: Mobile first viewport exposes a useful next action.
- RECOMMENDED_FROM_EVIDENCE: No journey requires buyer, chatbot, order, payment, or delivery functionality.
- RECOMMENDED_FROM_EVIDENCE: All critical journeys have automated tests where practical and manual UX checks where browser behavior matters.

## 18. Deferred Journeys

- OWNER_PROVIDED_DIRECTION: Buyer browses public catalog.
- OWNER_PROVIDED_DIRECTION: Buyer asks chatbot a question.
- OWNER_PROVIDED_DIRECTION: Seller approves order.
- OWNER_PROVIDED_DIRECTION: Buyer submits delivery address.
- OWNER_PROVIDED_DIRECTION: Payment is requested or confirmed.
- OWNER_PROVIDED_DIRECTION: Delivery/export status is managed.
- DEFERRED_HYPOTHESIS: LLM interprets uploaded photo or free text.
- DEFERRED_HYPOTHESIS: Multi-staff user works inside one business.

## 19. Owner Decisions Required

- Approve or reject Product Detail as a V1 journey.
- Approve or reject clone as a V1 journey.
- Decide clone stock-copy/reset behavior.
- Approve or reject archive/restore as a V1 journey.
- Decide direct stock set in V1.
- Decide exact V1 search/filter scope.
- Decide whether type/tag management pages are V1 journeys.
- Decide whether tags affect readiness or only organization/search.
- Decide whether correction journeys use full edit form or focused correction surfaces.
- Decide exact material confirmation UI and alias behavior.
- Decide measurement micro-slice timing, convention, and product/choice boundary.
- Decide whether fit guidance is required, optional, or deferred in a later micro-slice.
- Decide whether variant-level price override is included in V1.
