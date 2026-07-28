# App Experience Plan

## Document Metadata

- Status: DRAFT_FOR_OWNER_REVIEW
- Version: 1.0-draft
- Freeze authority: owner only

## 1. Experience Objective

RECOMMENDED_FROM_EVIDENCE: UX for this product is an operational-system concern, not visual polish. The interface must help a seller maintain accurate catalog truth, update stock, notice missing information, and prepare truthful buyer replies with low cognitive load on mobile.

VALIDATED_PROTOTYPE_LESSON: The source prototype became useful because it placed product state and actions close together, but it also became dense because too many workflows were stacked into the same card and form surfaces.

## 2. Lessons from the Existing Prototype

- VALIDATED_PROTOTYPE_LESSON: Navigation loss was a real historical risk; newer source added many contextual `next` flows, but tag toggling still depends on `HTTP_REFERER`.
- VALIDATED_PROTOTYPE_LESSON: Excessive route hopping weakens seller trust when detail, edit, management, and filtered lists do not preserve origin context.
- VALIDATED_PROTOTYPE_LESSON: Product cards are high value but overloaded when they contain status, readiness, ready replies, tags, stock controls, clone, archive, edit, and detail links.
- VALIDATED_PROTOTYPE_LESSON: Product forms are near the practical complexity limit when product data, taxonomy, variants, photo, recognition preview, and relations live together.
- VALIDATED_PROTOTYPE_LESSON: Repeated information can help scanning, but after partial updates it can become stale.
- VALIDATED_PROTOTYPE_LESSON: Late UI refactoring introduced regression risk around return paths, hidden behavior, and duplicated answer/card logic.
- VALIDATED_PROTOTYPE_LESSON: Mobile density is the main UX risk, especially filters before cards and long edit forms.
- OWNER_PROVIDED_DIRECTION: The revised clothing direction keeps the product as an assistant: product description is the primary seller input, recognition produces candidates, and only confirmed facts become reply/search/readiness truth.

## 3. Experience Principles

- RECOMMENDED_FROM_EVIDENCE: Action-first: every page should expose the next useful seller action.
- OWNER_PROVIDED_DIRECTION: Mobile-first: phone use is primary, not an afterthought.
- RECOMMENDED_FROM_EVIDENCE: One primary responsibility per page.
- RECOMMENDED_FROM_EVIDENCE: Explicit return paths everywhere.
- RECOMMENDED_FROM_EVIDENCE: First viewport usefulness before decoration or broad summaries.
- RECOMMENDED_FROM_EVIDENCE: Server truth after interaction; no local UI state may contradict persisted data.
- RECOMMENDED_FROM_EVIDENCE: Progressive disclosure for secondary explanation.
- RECOMMENDED_FROM_EVIDENCE: No critical information hidden behind optional disclosure.
- RECOMMENDED_FROM_EVIDENCE: Low cognitive load and stable Georgian terminology.
- RECOMMENDED_FROM_EVIDENCE: Destructive or lifecycle-changing actions are visually subordinate and confirmed.
- OWNER_PROVIDED_DIRECTION: Recognition is useful only when it lowers seller work; it must not become a giant ecommerce specification form.
- OWNER_PROVIDED_DIRECTION: Readiness should be buyer-question coverage, not a completion percentage.

## 4. Proposed Information Architecture

| Surface | Responsibility | Notes |
|---|---|---|
| Login | Secure entry | Keep simple and non-marketing |
| Dashboard | What needs attention today | Action queue first, summaries second |
| Product workspace | Daily catalog and stock operations | Product cards, search/filter, inline stock |
| Product create | Add a new product truth bundle | Keep focused; avoid relation/admin concepts |
| Product edit/correction | Correct product facts and choices | Consider focused correction paths later |
| Taxonomy management | Maintain approved types/tags if in V1 | OWNER_DECISION_REQUIRED |
| Product detail | Focused inspection or remove from V1 | OWNER_DECISION_REQUIRED |

DEFERRED_HYPOTHESIS: Public catalog, buyer inquiry, chatbot, orders, payment, delivery, and BI analytics are not V1 experience surfaces.

OWNER_PROVIDED_DIRECTION: Dashboard and Product workspace are the two primary operating surfaces. Create/edit and correction flows support those surfaces and must not become places where sellers get stuck.

## 5. Global Navigation Anchors

- RECOMMENDED_FROM_EVIDENCE: Dashboard.
- RECOMMENDED_FROM_EVIDENCE: Products/workspace.
- RECOMMENDED_FROM_EVIDENCE: Add product.
- RECOMMENDED_FROM_EVIDENCE: Logout/account.

Rules:

- RECOMMENDED_FROM_EVIDENCE: Show current page state.
- RECOMMENDED_FROM_EVIDENCE: Keep global nav compact on mobile.
- RECOMMENDED_FROM_EVIDENCE: Do not use global nav as a substitute for contextual return.
- RECOMMENDED_FROM_EVIDENCE: Avoid labels that imply ERP or broad admin software.

## 6. Dashboard Experience Contract

- Question answered: `What do I need to manage today?`
- First viewport: RECOMMENDED_FROM_EVIDENCE: show one useful action area, not only business name and metrics.
- Primary action: address attention item, low stock, sold-out/restock, or add product depending on state.
- Allowed summaries: compact counts that lead to filtered work.
- Prohibited clutter: charts, BI panels, decorative hero content, broad explanations, order/payment widgets.
- Drilldown behavior: every dashboard link carries explicit return context back to dashboard.
- Feedback: stock or data changes from dashboard must not leave visible counts stale in final V1.

OWNER_DECISION_REQUIRED: exact first-viewport priority order.

## 7. Product Workspace Experience Contract

- Question answered: `Which product do I need to find, update, or answer about?`
- Primary action: inspect and update product state from compact cards.
- Required elements: search, visible active filters, product cards, stock controls, readiness signal, edit/correction route.
- Optional elements: type/tag filters and ready reply if owner approves V1 scope.
- Prohibited clutter: unrelated analytics, public catalog controls, order/payment status, long helper explanations.
- Return behavior: workspace URL preserves search/filter/tab context and survives edit/detail/correction flows.

## 8. Product Card Experience Contract

Maximum responsibilities:

- RECOMMENDED_FROM_EVIDENCE: identify product visually and by name.
- RECOMMENDED_FROM_EVIDENCE: show price, lifecycle/availability, and total stock.
- RECOMMENDED_FROM_EVIDENCE: show active choices and quick stock update.
- RECOMMENDED_FROM_EVIDENCE: show readiness at a glance.
- RECOMMENDED_FROM_EVIDENCE: provide one primary correction/edit path.
- OWNER_DECISION_REQUIRED: ready reply inline or separate surface.
- OWNER_DECISION_REQUIRED: clone and archive on card or secondary menu.

Action hierarchy:

1. Stock update and product identity.
2. Missing data/readiness correction.
3. Deterministic reply if approved inline.
4. Secondary actions: clone, archive, tags, detail.

Rule: the card must not become the entire application.

## 9. Create/Edit Form Experience Contract

- Create form responsibility: add enough truth to make a product usable.
- Edit form responsibility: correct existing truth without losing origin context.
- Required structure: description-first input, price/lifecycle if approved, recognition feedback for known type/tag/material terms, size/color-to-choice suggestions, choices/stock, optional product media, optional tags.
- Recognition feedback: separate observed text, candidate meaning, and confirmed structured fact.
- Progressive disclosure: secondary explanations, material confirmation details, advanced taxonomy, future relations, and detailed measurement capture.
- Constraint: do not turn the product form into one huge fashion specification; material is a small typed semantic fact when confirmed, while detailed garment measurements remain a separate approved micro-slice.
- Validation: errors must appear at the exact section and preserve data.
- Actions: save, cancel/return, and no ambiguous destructive action in primary path.

OWNER_DECISION_REQUIRED: whether relations are excluded from V1 edit form.

## 10. Choice/Variant Interaction Contract

- RECOMMENDED_FROM_EVIDENCE: Seller-facing term should be `choice`/`არჩევანი`, not technical variant language.
- RECOMMENDED_FROM_EVIDENCE: Each choice has size, color, and quantity.
- RECOMMENDED_FROM_EVIDENCE: Variant/choice rows do not carry all product-level clothing attributes or every garment measurement.
- RECOMMENDED_FROM_EVIDENCE: Optional approved price override is variant-level only if owner approves it.
- OWNER_PROVIDED_DIRECTION: Size/color recognized from description may suggest adding a choice, but confirmed choice rows remain the only size/color truth.
- RECOMMENDED_FROM_EVIDENCE: Add/remove behavior must be robust and testable.
- RECOMMENDED_FROM_EVIDENCE: Removing the last valid choice is blocked or clearly changes product into a draft-only state if owner approves.
- RECOMMENDED_FROM_EVIDENCE: Quantity cannot be negative.
- OWNER_DECISION_REQUIRED: duplicate size/color choice behavior.

## 11. Search and Filter Experience Contract

- RECOMMENDED_FROM_EVIDENCE: Search should support product description/name, size, color, approved type, approved tags, aliases, and normalized observed text where this does not create false buyer-facing facts.
- RECOMMENDED_FROM_EVIDENCE: Active query/filter state must be visible.
- RECOMMENDED_FROM_EVIDENCE: Clear action must be obvious.
- RECOMMENDED_FROM_EVIDENCE: No-result state should suggest simpler terms.
- RECOMMENDED_FROM_EVIDENCE: Mobile filters must not bury products below multiple dense rows.
- DEFERRED_HYPOTHESIS: fuzzy/morphology-aware search is later.

## 12. Ready Reply Experience Contract

- RECOMMENDED_FROM_EVIDENCE: Replies are seller-side tools for copying truthful buyer answers.
- RECOMMENDED_FROM_EVIDENCE: Reply text uses confirmed structured facts and computed state only.
- RECOMMENDED_FROM_EVIDENCE: Missing data creates seller notes and correction links, not invented buyer statements.
- RECOMMENDED_FROM_EVIDENCE: Sold-out products must produce truthful sold-out wording.
- RECOMMENDED_FROM_EVIDENCE: Copy success and copy failure must both be visible.
- OWNER_PROVIDED_DIRECTION: Recognition candidates may prompt the seller, but buyer replies must not use unconfirmed candidate meaning.
- OWNER_DECISION_REQUIRED: whether ready reply lives inline on cards, on detail, or in a focused panel.

## 13. Loading, Success, Error, and Recovery Feedback

- RECOMMENDED_FROM_EVIDENCE: Form submit shows validation errors and preserves input.
- RECOMMENDED_FROM_EVIDENCE: Stock update shows loading, success, transition feedback, and failure recovery.
- RECOMMENDED_FROM_EVIDENCE: HTMX failures must not silently leave stale state.
- RECOMMENDED_FROM_EVIDENCE: Copy failure shows a visible fallback.
- RECOMMENDED_FROM_EVIDENCE: Delete/archive/hide actions require confirmation and clear success/failure messages.
- RECOMMENDED_FROM_EVIDENCE: Global messages should be semantically exposed and visually distinguish severity.

## 14. Navigation and Return-Path Rules

- RECOMMENDED_FROM_EVIDENCE: Every detail/edit/management route accepts safe internal return context.
- RECOMMENDED_FROM_EVIDENCE: Every POST redirects through a safe return helper or a deliberate fallback.
- RECOMMENDED_FROM_EVIDENCE: No state-changing journey depends on raw `HTTP_REFERER`.
- RECOMMENDED_FROM_EVIDENCE: Filtered list context survives edit/detail/save.
- RECOMMENDED_FROM_EVIDENCE: Dashboard attention returns to dashboard.
- RECOMMENDED_FROM_EVIDENCE: Management recovery flows return to management.
- RECOMMENDED_FROM_EVIDENCE: Contextual return links are compact but visible near the top of pages.

## 15. Mobile Constraints

- RECOMMENDED_FROM_EVIDENCE: The first useful action should appear without excessive scrolling on common phone heights.
- RECOMMENDED_FROM_EVIDENCE: Tabs/filter chips may wrap or collapse, but must not dominate the page.
- RECOMMENDED_FROM_EVIDENCE: Buttons use safe tap targets.
- RECOMMENDED_FROM_EVIDENCE: Long Georgian labels must wrap cleanly without overlap.
- RECOMMENDED_FROM_EVIDENCE: Clone/archive/destructive actions must not sit where accidental taps are likely.
- RECOMMENDED_FROM_EVIDENCE: Variant rows must remain readable with many choices.
- RECOMMENDED_FROM_EVIDENCE: Live mobile testing is required before release.

## 16. Accessibility Baseline

- RECOMMENDED_FROM_EVIDENCE: Buttons for actions, links for navigation.
- RECOMMENDED_FROM_EVIDENCE: Semantic headings in order.
- RECOMMENDED_FROM_EVIDENCE: Form labels and error associations.
- RECOMMENDED_FROM_EVIDENCE: Disclosure buttons with `aria-expanded` and keyboard support.
- RECOMMENDED_FROM_EVIDENCE: Menus have keyboard/focus behavior or are simplified.
- RECOMMENDED_FROM_EVIDENCE: Images have meaningful alt text or clear empty state.
- RECOMMENDED_FROM_EVIDENCE: Status is not color-only.
- RECOMMENDED_FROM_EVIDENCE: HTMX updates announce important changes.

No full WCAG compliance claim is made by this draft.

## 17. Georgian Terminology Principles

- OWNER_PROVIDED_DIRECTION: Georgian-first seller UI.
- RECOMMENDED_FROM_EVIDENCE: Prefer concrete seller words: პროდუქცია, ნაშთი, დარჩენილია, ფასი, ზომა, ფერი, შევსება, დაარქივება.
- RECOMMENDED_FROM_EVIDENCE: Avoid seller-facing technical words: ERP, SKU, schema, variant matrix, inventory ledger, event.
- RECOMMENDED_FROM_EVIDENCE: Freeze one term for choice/variant.
- RECOMMENDED_FROM_EVIDENCE: Freeze type/tag distinction.
- OWNER_DECISION_REQUIRED: final wording for dashboard, ready reply, archive/hidden, and product workspace labels.

## 18. HTMX/Alpine Interaction Boundaries

- RECOMMENDED_FROM_EVIDENCE: HTMX is for server-truth refresh, not client-owned business state.
- RECOMMENDED_FROM_EVIDENCE: HTMX swaps must define whether they update card only, list counts, dashboard counts, or navigation state.
- RECOMMENDED_FROM_EVIDENCE: Alpine is for local UI state only: disclosure, copy, small menus, client-side row helpers.
- RECOMMENDED_FROM_EVIDENCE: Alpine state loss after HTMX replacement must be acceptable or handled deliberately.
- RECOMMENDED_FROM_EVIDENCE: Inline scripts should not duplicate domain logic.
- RECOMMENDED_FROM_EVIDENCE: All HTMX and Alpine interactions require accessible fallback or failure feedback.

## 19. UI Regression Checklist

- RECOMMENDED_FROM_EVIDENCE: Product card still shows stock after refresh.
- RECOMMENDED_FROM_EVIDENCE: Product card ready reply still works after HTMX replacement.
- RECOMMENDED_FROM_EVIDENCE: Stock transition updates card, counts, and filters according to contract.
- RECOMMENDED_FROM_EVIDENCE: `next` survives dashboard -> edit -> save.
- RECOMMENDED_FROM_EVIDENCE: `next` survives filtered list -> edit/detail -> save/return.
- RECOMMENDED_FROM_EVIDENCE: Tag/type recovery returns to management.
- RECOMMENDED_FROM_EVIDENCE: Validation errors appear near fields after dynamic choices.
- RECOMMENDED_FROM_EVIDENCE: Mobile card actions do not overlap.
- RECOMMENDED_FROM_EVIDENCE: Copy success/failure is visible.
- RECOMMENDED_FROM_EVIDENCE: No public/chat/order/payment controls appear in V1 screens.

## 20. Screen-Level Acceptance Criteria

| Screen | Acceptance Criteria |
|---|---|
| Login | Email/password fields, validation errors, no seller nav before auth |
| Dashboard | First viewport has useful work/action, drilldowns preserve return, counts align with shared state |
| Product workspace | Search/filter visible but not dominant, cards expose stock/readiness clearly, state updates are server-backed |
| Product card | One clear primary action hierarchy, compact stock controls, no stale critical facts after update |
| Product create | Description-first input, recognition feedback remains lightweight, first valid product can be created without route confusion |
| Product edit | Missing data can be corrected, validation preserves input, return path explicit |
| Taxonomy management | If in scope, used items cannot be deleted silently, recovery links return to management |
| Product detail | If in scope, has a distinct job not duplicated by card |

## 21. UX Stop Gates

- OWNER_DECISION_REQUIRED: Page responsibilities approved.
- RECOMMENDED_FROM_EVIDENCE: First viewport checked on mobile.
- RECOMMENDED_FROM_EVIDENCE: Return-path matrix manually verified.
- RECOMMENDED_FROM_EVIDENCE: Product card density reviewed against action hierarchy.
- RECOMMENDED_FROM_EVIDENCE: Form completion and error recovery tested.
- RECOMMENDED_FROM_EVIDENCE: HTMX stale-state behavior resolved or explicitly accepted.
- RECOMMENDED_FROM_EVIDENCE: Accessibility baseline checked.
- RECOMMENDED_FROM_EVIDENCE: Georgian terminology approved.

## 22. Deferred Experience Work

- OWNER_PROVIDED_DIRECTION: Public buyer catalog.
- OWNER_PROVIDED_DIRECTION: Chatbot/messaging UI.
- OWNER_PROVIDED_DIRECTION: Order/payment/delivery experiences.
- DEFERRED_HYPOTHESIS: Guided task queue.
- DEFERRED_HYPOTHESIS: Advanced analytics dashboard.
- DEFERRED_HYPOTHESIS: Detailed measurement capture and fit-guidance UI.
- DEFERRED_HYPOTHESIS: AI-assisted product parsing.
- DEFERRED_HYPOTHESIS: Morphology-aware search.
- DEFERRED_HYPOTHESIS: Multi-staff navigation.
- DEFERRED_HYPOTHESIS: Relation-based buyer suggestions.

## 23. Owner Decisions Required

- Dashboard first-viewport priority.
- Product card maximum action set.
- Ready reply placement.
- Product Detail existence and purpose.
- Product Relations inclusion or deferral.
- Material confirmation placement and wording.
- Measurement capture timing, method wording, and product/choice boundary for a later approved micro-slice.
- Fit guidance placement and wording if included later.
- Type/tag management page inclusion.
- Card tag toggle inclusion.
- Direct stock set placement.
- Clone inclusion and clone-mode UI.
- Archive/restore inclusion and hidden/archive terminology.
- Final Georgian vocabulary.
- Mobile filter density limit.
