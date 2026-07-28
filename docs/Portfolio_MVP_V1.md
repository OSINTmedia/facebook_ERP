# Portfolio MVP V1

## Document Metadata

- Status: DRAFT_FOR_OWNER_REVIEW
- Version: 1.0-draft
- Owner: osMit
- Source prototype: `/home/giga/Desktop/OSINT/facebook_MVP/`
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Freeze authority: owner only
- Codex automatic scope changes: forbidden

## 1. Portfolio Objective

OWNER_PROVIDED_DIRECTION: The rebuild must be a portfolio-grade GitHub project that demonstrates product thinking, systems thinking, Django/Python engineering, relational modeling, operational UI/UX, state management, testing, documentation discipline, Git workflow, and online deployment.

RECOMMENDED_FROM_EVIDENCE: The portfolio should make the work visible in this order:

1. Problem investigation.
2. Product decisions.
3. Frozen scope.
4. Architecture.
5. Build phases.
6. Implementation.
7. Verification.
8. Documentation updates.
9. Meaningful chronological commits.
10. Online demo when deployment exists.

OBSOLETE_OR_REJECTED: The current source prototype has no Git repository at `/home/giga/Desktop/OSINT/facebook_MVP/`, so it cannot provide a real portfolio history. The rebuild must start fresh and must not fabricate earlier commits or backdated development history.

## 2. Product Definition

RECOMMENDED_FROM_EVIDENCE: Portfolio MVP V1 is a private, seller-first catalog and inventory operations assistant for small social-commerce sellers, focused on turning seller descriptions into confirmed product, choice, price, stock, classification, material, buyer-question coverage, and deterministic buyer-reply truth before any public catalog, chatbot, order, payment, or delivery layer exists.

## 3. Target User

OWNER_PROVIDED_DIRECTION: The primary user is a solo or very small Facebook/Instagram seller who maintains product and stock information personally and needs a faster, more trustworthy daily workflow than Messenger memory, notebooks, spreadsheets, or ad hoc posts.

RECOMMENDED_FROM_EVIDENCE: Portfolio V1 should keep the primary user narrow: one authenticated seller operating one current business workspace.

DEFERRED_HYPOTHESIS: Future users may include buyers, staff members, delivery operators, or assistant/chatbot integrations, but they are not V1 users.

## 4. Core Problem

VALIDATED_PROTOTYPE_LESSON: Social-commerce product truth is fragmented across posts, messages, memory, photos, spreadsheets, and repeated seller replies. Sellers are asked the same questions about price, availability, size, color, and stock. When catalog truth is stale, every downstream automation layer becomes unreliable.

RECOMMENDED_FROM_EVIDENCE: A public catalog cannot be trusted until the seller has a private workflow that keeps product and stock data current. Chatbot or LLM output cannot be the source of price, size, color, stock, lifecycle, or availability truth.

## 5. Core Product Principle

OWNER_PROVIDED_DIRECTION: Seller-maintained catalog truth is the foundation for all future automation.

RECOMMENDED_FROM_EVIDENCE: Inventory should be part of the seller's daily work, not a separate spreadsheet-like island. The product should reduce memory burden by surfacing what needs attention, what is low stock, what is sold out, and what information is ready for buyer answers.

## 6. Validated Prototype Lessons

### Successful Patterns

- VERIFIED_BY_CURRENT_SOURCE: Business-owned product data creates a clear seller workspace boundary.
- VERIFIED_BY_CURRENT_SOURCE: Stock truth lives on `ProductVariant.quantity_on_hand`, not on `Product`.
- VERIFIED_BY_CURRENT_SOURCE: Availability is computed from lifecycle and active variant quantities.
- VERIFIED_BY_CURRENT_SOURCE: Readiness and deterministic buyer replies can be computed from stored facts without an LLM.
- VERIFIED_BY_CURRENT_SOURCE: Django Templates + HTMX + Alpine.js can support a server-rendered operational cockpit without a full SPA.
- VERIFIED_BY_CURRENT_SOURCE: Safe `next` return paths exist on many key routes and are covered by tests.

### Failed Patterns

- VALIDATED_PROTOTYPE_LESSON: A large `catalog.views` module makes workflow boundaries hard to reason about.
- VALIDATED_PROTOTYPE_LESSON: Stock changes are split between product edit and inventory endpoint, making the adjustment ledger incomplete.
- VALIDATED_PROTOTYPE_LESSON: Readiness logic depends on decorated view attributes and legacy type fields.
- VALIDATED_PROTOTYPE_LESSON: Product cards and product edit forms can become overloaded when every late feature is added to the primary surface.
- VALIDATED_PROTOTYPE_LESSON: Partial HTMX updates can leave surrounding counts and grouping state stale.

### UX Lessons

- VALIDATED_PROTOTYPE_LESSON: The product workspace is valuable when stock, readiness, and reply actions are close to the product card.
- VALIDATED_PROTOTYPE_LESSON: The seller must not rely on browser Back; return context has to be part of the app contract.
- VALIDATED_PROTOTYPE_LESSON: The first viewport must expose useful work, not only summaries.
- VALIDATED_PROTOTYPE_LESSON: Georgian wording should avoid technical terms such as ERP, SKU, variant matrix, schema, or stock ledger.

### Architecture Lessons

- RECOMMENDED_FROM_EVIDENCE: Keep the modular monolith, but move domain rules into explicit services.
- RECOMMENDED_FROM_EVIDENCE: Centralize current-business selection, return URL safety, stock mutation, readiness, availability, search, clone, and deterministic answer generation.
- RECOMMENDED_FROM_EVIDENCE: Remove migration-era `_table_exists()` request-path branching after schema is stable.

### Scope Lessons

- OWNER_PROVIDED_DIRECTION: Public catalog, chatbot, orders, payments, delivery, accounting, supplier management, and broad ERP functionality are out of V1.
- OWNER_DECISION_REQUIRED: Product Detail, product relations, clone modes, tag/type management pages, direct stock set, and taxonomy assistant behavior need explicit owner approval before they become V1 scope.

## 7. Portfolio V1 Vertical Slice

RECOMMENDED_FROM_EVIDENCE: The smallest complete end-to-end slice should be:

Seller -> login -> business workspace -> enter product description -> recognize type/tag/material candidates -> confirm structured facts where needed -> add size/color choices -> maintain variant-level stock -> compute availability -> view operational workspace -> see buyer-question coverage -> prepare deterministic buyer reply from confirmed facts.

OWNER_PROVIDED_DIRECTION: Clothing domain data follows `docs/domain/CLOTHING_DATA_SPEC_V1.md`. Product description is the primary seller input; recognized text is separated into observed text, candidate meaning, and confirmed structured fact. Material is a small typed semantic fact when confirmed. Size and color remain choice/variant truth, and description-recognized size/color may only suggest adding a choice.

OWNER_PROVIDED_DIRECTION: Detailed garment measurements remain a separate approved micro-slice and must not be added as a mandatory first-form requirement.

OWNER_DECISION_REQUIRED: Clone, archive/restore, type/tag management pages, and Product Detail are valuable prototype behaviors but should be owner-approved before entering the frozen V1 slice.

## 8. In Scope

- RECOMMENDED_FROM_EVIDENCE: Django project foundation with one portfolio-ready configuration path.
- RECOMMENDED_FROM_EVIDENCE: Custom authenticated seller account.
- RECOMMENDED_FROM_EVIDENCE: One active business workspace per seller for V1.
- RECOMMENDED_FROM_EVIDENCE: Product creation and editing for core seller truth.
- OWNER_PROVIDED_DIRECTION: Description-first product capture with semantic recognition.
- RECOMMENDED_FROM_EVIDENCE: Clothing-first domain boundary documented in `docs/domain/CLOTHING_DATA_SPEC_V1.md`.
- OWNER_PROVIDED_DIRECTION: Product Type and Tag recognition using business vocabulary and aliases.
- OWNER_PROVIDED_DIRECTION: Optional confirmed material facts as a small typed extension.
- RECOMMENDED_FROM_EVIDENCE: Clothing-first choice data: size, color, quantity.
- OWNER_PROVIDED_DIRECTION: Description-recognized size/color suggests adding choices instead of becoming generic tags.
- DEFERRED_HYPOTHESIS: Detailed garment measurements with type, value, unit, method, and product/choice boundary.
- RECOMMENDED_FROM_EVIDENCE: Variant-level stock updates through a single inventory service.
- RECOMMENDED_FROM_EVIDENCE: Stored lifecycle separated from computed availability.
- RECOMMENDED_FROM_EVIDENCE: Product workspace with search/filter only to the level needed for daily operations.
- RECOMMENDED_FROM_EVIDENCE: Dashboard or attention surface that answers what needs work today.
- RECOMMENDED_FROM_EVIDENCE: Product readiness computed from stored facts.
- OWNER_PROVIDED_DIRECTION: Readiness is expressed as buyer-question coverage, not a completion percentage.
- RECOMMENDED_FROM_EVIDENCE: Deterministic seller-side buyer reply.
- RECOMMENDED_FROM_EVIDENCE: Explicit return paths for all drilldowns.
- RECOMMENDED_FROM_EVIDENCE: Automated tests and CI for critical flows.
- RECOMMENDED_FROM_EVIDENCE: Synthetic demo data and safe reset process.
- RECOMMENDED_FROM_EVIDENCE: Online Django demo after owner-approved hosting decision.

## 9. Explicitly Out of Scope

- OWNER_PROVIDED_DIRECTION: Public buyer catalog implementation.
- OWNER_PROVIDED_DIRECTION: Chatbot or messaging integration.
- OWNER_PROVIDED_DIRECTION: LLM-based source of truth.
- OWNER_PROVIDED_DIRECTION: Orders.
- OWNER_PROVIDED_DIRECTION: Reservations.
- OWNER_PROVIDED_DIRECTION: Payments.
- OWNER_PROVIDED_DIRECTION: Delivery.
- OWNER_PROVIDED_DIRECTION: Accounting.
- OWNER_PROVIDED_DIRECTION: Supplier management.
- OWNER_PROVIDED_DIRECTION: Analytics BI dashboard.
- OWNER_PROVIDED_DIRECTION: Multi-staff permissions.
- OWNER_PROVIDED_DIRECTION: Microservices.
- OWNER_PROVIDED_DIRECTION: Broad ERP functionality.
- RECOMMENDED_FROM_EVIDENCE: Full REST/DRF API unless needed by a later approved public/buyer layer.
- RECOMMENDED_FROM_EVIDENCE: AI form filling, morphology-aware search, and automatic taxonomy generation.
- OWNER_PROVIDED_DIRECTION: Universal fashion ontology, mandatory full specification forms, and AI sizing.

## 10. Future-Ready Boundaries

- RECOMMENDED_FROM_EVIDENCE: Product truth should be accessible through services that future public catalog or assistant layers can read without owning truth.
- RECOMMENDED_FROM_EVIDENCE: Deterministic answer generation should remain a reusable domain/application service.
- RECOMMENDED_FROM_EVIDENCE: Product availability should be computed centrally and exposed consistently to dashboard, workspace, and future APIs.
- RECOMMENDED_FROM_EVIDENCE: Stock mutations should produce an auditable adjustment record that future order workflows can reuse.
- OWNER_PROVIDED_DIRECTION: Recognition should preserve observed text, candidate meaning, and confirmed structured fact so future interpretation can assist without owning truth.
- DEFERRED_HYPOTHESIS: Measurement support can be added later after method, unit, and applies-to boundaries are frozen.
- DEFERRED_HYPOTHESIS: Product relations can become future recommendation/assistant input, but not a V1 requirement unless owner-approved.
- DEFERRED_HYPOTHESIS: Public visibility/publication can remain a future boundary if not used in V1 UI.

## 11. Source-of-Truth Rules

- RECOMMENDED_FROM_EVIDENCE: Product ownership truth belongs to `Business`.
- RECOMMENDED_FROM_EVIDENCE: Product lifecycle truth is a stored product field.
- OWNER_PROVIDED_DIRECTION: Product description is the primary seller input, but not the automatic source of structured buyer-facing truth.
- OWNER_PROVIDED_DIRECTION: Observed text and candidate meaning are not the same as confirmed structured facts.
- RECOMMENDED_FROM_EVIDENCE: Stock truth belongs to active product choices/variants.
- RECOMMENDED_FROM_EVIDENCE: Product availability is computed from lifecycle and active variant stock.
- OWNER_PROVIDED_DIRECTION: Readiness is computed and expressed as buyer-question coverage.
- RECOMMENDED_FROM_EVIDENCE: Buyer replies are deterministic text generated from stored facts and computed state.
- RECOMMENDED_FROM_EVIDENCE: LLMs must not decide or invent price, stock, size, color, lifecycle, availability, or readiness.
- OWNER_PROVIDED_DIRECTION: Buyer replies use confirmed facts only.
- OWNER_PROVIDED_DIRECTION: Material is a typed semantic fact when confirmed, not a required large form section.
- OWNER_PROVIDED_DIRECTION: Size and color truth belongs to choices/variants, not generic tags.
- OWNER_PROVIDED_DIRECTION: Measurements require type, value, unit, method, and product/choice boundary before they can become buyer-answer facts.
- RECOMMENDED_FROM_EVIDENCE: Weight alone must not determine size or availability.
- RECOMMENDED_FROM_EVIDENCE: Deterministic replies must not invent material, measurements, or fit guidance.
- OWNER_DECISION_REQUIRED: Whether `0.00` is allowed as a real price, treated as missing, or rejected.
- OWNER_DECISION_REQUIRED: Whether tags are required for readiness or optional organization only.

## 12. Portfolio Completion Criteria

Portfolio V1 is functionally complete when:

- RECOMMENDED_FROM_EVIDENCE: A seller can sign in and operate one business workspace.
- RECOMMENDED_FROM_EVIDENCE: A seller can create a product from a description and at least one size/color/quantity choice.
- OWNER_PROVIDED_DIRECTION: Recognized type/tag/material candidates can become confirmed facts without making the form large.
- RECOMMENDED_FROM_EVIDENCE: A seller can edit core product truth and validation failures are clear.
- RECOMMENDED_FROM_EVIDENCE: A seller can update stock safely through the inventory service.
- RECOMMENDED_FROM_EVIDENCE: A product moves between available, low stock, partially sold out, sold out, draft, and archived states according to explicit rules.
- RECOMMENDED_FROM_EVIDENCE: The dashboard/workspace surfaces attention and readiness signals.
- RECOMMENDED_FROM_EVIDENCE: The deterministic buyer reply remains truthful when information is missing or stock is sold out.
- RECOMMENDED_FROM_EVIDENCE: Critical regression tests run in CI.
- RECOMMENDED_FROM_EVIDENCE: Documentation explains scope, setup, architecture, journeys, tests, and deferred features.
- RECOMMENDED_FROM_EVIDENCE: Git history shows real chronological development from planning through implementation.

## 13. Online Demo Completion Criteria

- RECOMMENDED_FROM_EVIDENCE: Public GitHub repository exists.
- RECOMMENDED_FROM_EVIDENCE: Setup is reproducible from documented commands.
- RECOMMENDED_FROM_EVIDENCE: CI is passing.
- RECOMMENDED_FROM_EVIDENCE: Demo data is synthetic.
- RECOMMENDED_FROM_EVIDENCE: Demo account is safe and resettable.
- RECOMMENDED_FROM_EVIDENCE: Online URL points to a backend-capable Django deployment.
- RECOMMENDED_FROM_EVIDENCE: Safe reset or reseed process exists.
- RECOMMENDED_FROM_EVIDENCE: No `.env`, secrets, real media, backups, customer data, database dumps, or private logs are published.
- RECOMMENDED_FROM_EVIDENCE: Mobile usability is manually verified.
- RECOMMENDED_FROM_EVIDENCE: README links to the demo only after deployment exists.
- OBSOLETE_OR_REJECTED: GitHub Pages is not a valid host for the Django/PostgreSQL backend demo.
- OWNER_DECISION_REQUIRED: Hosting provider and demo access model.

## 14. Quality Gates

- RECOMMENDED_FROM_EVIDENCE: Scope gate: owner approves Portfolio V1 scope before implementation.
- RECOMMENDED_FROM_EVIDENCE: Data gate: source-of-truth rules are documented before models are built.
- RECOMMENDED_FROM_EVIDENCE: Security gate: no secrets, real media, real backups, or customer data enter Git.
- RECOMMENDED_FROM_EVIDENCE: Test gate: critical regression matrix is automated before release.
- RECOMMENDED_FROM_EVIDENCE: UX gate: mobile first viewport, return paths, and stock feedback are manually checked.
- RECOMMENDED_FROM_EVIDENCE: Deployment gate: CI passes and demo environment uses production-safe settings.
- RECOMMENDED_FROM_EVIDENCE: Documentation gate: README, build plan, and current checkpoint are created only after owner approval in later phases.

## 15. Deferred Scope

| Capability | Why Deferred | Required Foundation | Possible Future Phase |
|---|---|---|---|
| Public buyer catalog | Seller truth must be reliable first | Product publication boundary, media policy, availability service | Public Catalog |
| Buyer chatbot | Must not invent truth | Deterministic answer service, public-safe API, missing-data handling | Buyer Assistant |
| LLM interpretation | Optional interpretation cannot own business facts | Clean product data, audit trail, human confirmation | AI Assist |
| Detailed garment measurements | Requires method/unit/applies-to boundaries and compact UX | Description-first product flow, semantic recognition, owner-approved measurement convention | Measurement Micro-Slice |
| Orders/reservations | Stock mutation must be reliable first | Inventory ledger, transaction safety, reservation model | Orders |
| Payments | Premature without orders | Order/payment status boundaries | Payments |
| Delivery | Premature without orders | Address/order data and privacy rules | Delivery |
| Product relations | Current value is future-oriented | Owner-approved relation UX and tests | Assistant/Recommendations |
| Advanced analytics BI | Portfolio MVP needs verification, not dashboards | Usage events, privacy/retention rules | Pilot Analytics |
| Multi-staff permissions | V1 seller is narrow | Role model and object permissions | Team Mode |
| Full REST API | No current public/buyer consumer | Stable domain services and auth policy | API Layer |
| Morphology/fuzzy search | Useful but not required for initial truth loop | Normalization strategy and test data | Search Upgrade |

## 16. Owner Decisions Required

- Whether Portfolio V1 includes Product Detail.
- Exact material confirmation UI and alias policy.
- Measurement micro-slice timing, convention, and product/choice boundary.
- Whether fit guidance appears in a later approved micro-slice, and how strongly it is worded.
- Whether Portfolio V1 includes product clone, and whether clone copies or resets stock.
- Whether Portfolio V1 includes archive/restore.
- Whether Portfolio V1 includes product relations or defers them.
- Whether tags are required for readiness or optional organization.
- Whether type and tag management are separate pages or inline-only in V1.
- Whether direct stock set is available in V1 or only `+1/-1`.
- Whether price `0.00` is valid, missing, or invalid.
- Whether hidden and archived are separate V1 lifecycle states.
- Hosting provider and public demo access model.
