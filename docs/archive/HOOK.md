# Project Hook — Social Commerce Seller Operations Assistant

## 1. Hook Role

This file is a durable context anchor for the "Social Commerce Seller Operations Assistant" project. Future model sessions must read it to understand the project's history, goals, architectural principles, and verified lessons from the prototype. It is a handoff document, not an implementation authority. Always re-read live sources for current Git/CI/project phase information.

## 2. Project Identity

- **Project Name:** Social Commerce Seller Operations Assistant
- **Workspace:** `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- **Historical Archive:** `docs/archive/old_docs/`
- **Discovery Audits:** `docs/discovery/`
- **Clothing Domain Authority:** `docs/domain/CLOTHING_DATA_SPEC_V1.md` (FROZEN, OWNER-CONTROLLED)
- **Target Market:** Small and solo social media sellers in Georgia.
- **Target User:** Individuals selling products (e.g., clothing, handmade goods) on platforms like Facebook and Instagram without a formal e-commerce setup, who primarily work from a mobile phone.
- **Product Definition:** A private, seller-first, mobile-first catalog and inventory cockpit. It helps a seller capture product truth with low effort, manage stock, understand what information is missing, and prepare truthful, deterministic replies for buyers, thereby reducing the chaos of managing sales through Messenger and spreadsheets.

## 3. Why the Clean GitHub Rebuild Exists

A previous local prototype existed and served as a validation ground for core product and engineering concepts. Discovery audits confirmed it contains significant product learning but also prototype-era coupling, documentation drift, and technical debt. This GitHub repository is a deliberate, clean, and controlled rebuild. The goal is to preserve validated reasoning while implementing a more robust, testable, and maintainable architecture based on verified lessons.

## 4. Product Problem

Solo social media sellers in Georgia manage their business manually, leading to scattered data, forgotten stock levels, inconsistent customer replies, and operational errors. They lack a simple, mobile-friendly tool that integrates inventory management into their daily workflow. Complex systems like Excel or traditional ERPs are often abandoned because they feel like administrative burdens rather than operational assistants.

## 5. Durable Product Thesis

- **Inventory as Daily Workflow:** Inventory management must be an integral part of the seller's daily work, not an isolated, administrative task. The UI must feel like a fast, operational cockpit.
- **Catalog Truth is Foundational:** Clean, structured catalog data is the bedrock for all future automation. The system must guide the seller toward creating this clean data with minimal friction.
- **Immediate, Visible Value:** Every required field and feature must provide immediate, demonstrable value to the seller. The "Value Loop" (showing what buyer questions can be answered) is a key example.
- **Description-First, Assistant-Led:** The easiest seller action (writing a description) should be the starting point for creating structured truth, with the system acting as an assistant that recognizes, suggests, and confirms.
- **Resist Becoming Another E-commerce Admin:** The product must actively avoid the complexity, nested menus, and administrative feel of conventional e-commerce backends.

## 6. Product Boundary

### Current / First MVP Direction
- Private, seller-only inventory and catalog management cockpit.
- Mobile-first web application.
- Variant-level stock tracking and fast, inline updates.
- Automated availability computation (e.g., "Sold Out," "Low Stock").
- A proactive dashboard that surfaces items needing attention.
- Business-scoped, seller-managed vocabularies for product types and tags.

### Future Layers (Explicitly Deferred)
- Public-facing buyer catalog or product mini-pages.
- A "Ready Replies" assistant to answer buyer questions.
- Order, payment, and delivery workflows.
- Direct integration with a Meta (Facebook/Instagram) chatbot.
- AI-powered suggestions or data extraction.

### Explicit Non-Goals for the First MVP
- A public e-commerce storefront or marketplace.
- Direct payment processing or accounting.
- Automated order fulfillment or delivery integration.
- A buyer-facing chatbot.
- Broad ERP features like supplier or customer management.

## 7. Core Domain Truths

- **Business is the Data Boundary:** All seller-owned data (products, types, tags) is strictly scoped to a `Business`. There is no global taxonomy.
- **Product vs. Choice:** `Product` holds general identity (name, description). `ProductVariant` (or "Choice") is the definitive source of truth for size, color, and `quantity_on_hand`.
- **Stock is Variant-Level:** There is no product-level stock field. Total stock is always computed from its active variants.
- **Lifecycle vs. Availability:** `Lifecycle` (e.g., `active`, `archived`) is a stored state. `Availability` (e.g., `Available`, `Sold Out`) is a computed truth based on lifecycle and stock levels.
- **Text is Not Truth Until Confirmed:** Seller-entered text is `Observed Text`. It only becomes a `Confirmed Fact` (like a `ProductType` or `Tag`) after a safe, deterministic rule or explicit seller confirmation.

## 8. Semantic Assistant Model

The system's intelligence follows a clear, safe progression:
**Observed Text → Recognized Candidate → Confirmed Fact**

- **Observed Text:** The seller's natural language input, primarily in the product description. It is always searchable.
- **Recognized Candidate:** A word or phrase the system matches against existing business vocabulary (types, tags, aliases) or known patterns (size, color, material, measurements).
- **Confirmed Fact:** A candidate that is approved by the seller or a high-confidence rule. Only confirmed facts are used for filtering, readiness checks, and deterministic buyer replies.
- **Roles:**
    - `ProductType`: Answers "What is this?" (e.g., "Dress").
    - `Tag`: Answers "How can this be found/grouped?" (e.g., "Summer," "Oversized").
    - `Material`: Fabric or composition fact.
    - `Choice — Size/Color`: Sellable size/color option.
    - `Measurement`: Garment measurement with method and unit.

## 9. Primary Seller Experience

- **Two Primary Surfaces:** The seller operates mainly from the `Dashboard` and the `Product Workspace`.
- **Dashboard:** Answers "What needs my attention today?" with proactive, actionable signals about stock and data completeness.
- **Product Workspace:** The central operational hub for finding, filtering, and performing quick actions on products via dense, operational `Product Cards`.
- **Quick, Contextual Operations:** Inline stock updates (`+1/-1`), quick tagging, and contextual "next action" chips are critical to the workflow.
- **Readiness & Ready Replies:** The system shows "readiness" based on buyer-question coverage, not an arbitrary percentage. This incentivizes data entry by showing the direct payoff: a more complete, copyable "ready reply."
- **Progressive Disclosure:** The UI hides complexity (e.g., advanced fields, management pages) until needed, keeping the primary paths clean and fast.

## 10. Technical Direction

- **Stack:** Django modular monolith, PostgreSQL, Django Templates with HTMX and Alpine.js.
- **Architecture:** A modular monolith with clear app boundaries. Business logic should be in services, not directly in views.
- **Server-Owned Truth:** The backend is the single source of truth. HTMX refreshes fragments of server-rendered state; Alpine.js manages local-only UI state (e.g., disclosure).
- **Business Scoping:** All queries and data manipulations must be strictly and consistently scoped to the authenticated user's active `Business`.
- **Testing:** The rebuild must have a strong test posture, covering domain logic, data integrity, ownership isolation, and key user journeys.

## 11. Historical Prototype — Verified Capabilities

The following capabilities were **VERIFIED_IMPLEMENTED** in the prototype's source code. This is a historical record, not a statement of current features in the rebuild.

- **Core Backend:** Django 6.0.5, PostgreSQL, custom email-based `User` model, and a `Business` model for tenancy.
- **Catalog & Inventory:** `Product`, `ProductVariant` (with `quantity_on_hand`), `ProductPhoto`, and `InventoryAdjustment` models.
- **Taxonomy:** Business-scoped `BusinessProductType` and `BusinessTag` models with uniqueness constraints and management views.
- **Domain Logic:** Services for computing availability, readiness, and dashboard signals. A transactional `_save_product_bundle` for product creation/editing.
- **Seller UI:** A dashboard with signals, and a product workspace with filtering and operational product cards.
- **Interactivity:** HTMX-powered inline stock updates and inline creation of types/tags. Alpine.js for disclosures and dynamic formsets.
- **Seller Tools:** A deterministic "Ready Reply" generator, product cloning, and a `reset_catalog_test_data` management command.
- **Navigation:** Evidence of `next` parameter handling for contextual return paths in many key workflows.

## 12. Discovery-Verified Architecture Lessons

- **Centralize Domain Logic:** The prototype's logic was scattered. Readiness rules were duplicated across `validation`, `dashboard`, and `catalog` apps. The rebuild must centralize core logic (e.g., stock mutation, readiness) into dedicated, pure services.
- **Enforce Strict Boundaries:** The prototype had blurred app boundaries (e.g., `inventory` views importing from `catalog` views). The rebuild must use clear, explicit service interfaces between apps.
- **Eliminate Runtime Defenses:** The prototype used `_table_exists()` checks in request paths, hiding potential migration drift. The rebuild should rely on a stable, migrated schema.
- **Fat Views are a Risk:** The prototype's `catalog.views` module was over 1,500 lines, handling orchestration, search, decoration, and more. The rebuild should favor smaller views that delegate to application services.

## 13. Discovery-Verified Domain/Data Risks

- **Incomplete Stock Ledger:** The prototype's `InventoryAdjustment` log was bypassed during product creation/editing. The rebuild's inventory service must be the *only* path for all stock mutations.
- **Concurrency Unsafe:** Stock updates were not atomic (`F()` expressions) or locked (`select_for_update`), creating race conditions. The rebuild must ensure transactional integrity for stock changes.
- **Ambiguous Price:** The prototype used `0.00` as a sentinel for a missing price, making "free" and "unknown" indistinguishable. The rebuild needs a clear, owner-approved price strategy.
- **Inconsistent Tenancy:** Business ownership was enforced at the view level but not always with database constraints. The rebuild must have robust, test-backed tenancy enforcement at all layers.
- **Duplicated Truth:** The prototype had duplicated data (e.g., `ProductVariant.label` vs. `ClothingVariantProfile` fields; legacy vs. custom product types). The rebuild must enforce a single source of truth for each domain fact.

## 14. Discovery-Verified UX and Navigation Lessons

- **Navigation is Trust Infrastructure:** The prototype suffered from weak return paths. The rebuild must implement robust, explicit, and tested contextual navigation (`next` parameter handling) for all workflows. Do not rely on `HTTP_REFERER`.
- **Avoid Overloaded Surfaces:** The prototype's product card and edit form became overloaded with too many competing actions. The rebuild must establish a clear information and action hierarchy, moving secondary actions out of primary surfaces.
- **Manage State Coherently:** HTMX partial updates in the prototype often left surrounding page state (like dashboard counts or list filters) stale. The rebuild must define clear contracts for what gets updated after a partial refresh.
- **The Detail Page Needs a Job:** The prototype's `Product Detail` page largely duplicated functionality already on the product card, creating an unnecessary route hop. Its purpose must be clarified or it should be deferred.

## 15. Discovery-Verified Testing / QA Lessons

- **Coverage was Spotty:** The prototype had meaningful tests in `apps/catalog/tests.py` (covering answer generation, some navigation, and edit corrections) but almost none in other apps.
- **Critical Gaps:** There were no dedicated tests for ownership/security, inventory concurrency, service-level readiness, or the `reset_catalog` command.
- **Rebuild Mandate:** The rebuild must have comprehensive, automated tests for its critical paths, especially data integrity, ownership, and state transitions.

## 16. Discovery-Verified Deployment / Security Lessons

- **Prototype was Local-Only:** The prototype had no production settings, containerization, or CI/CD configuration. It relied on a development `SECRET_KEY` and `DEBUG=True`.
- **CDN Dependency:** The frontend relied on CDN-hosted scripts, creating a runtime network dependency.
- **Rebuild Mandate:** The portfolio-grade rebuild must have a secure, production-ready configuration and a clear deployment strategy.

## 17. Preserve in the Rebuild

- The modular monolith architecture and the Django/HTMX/Alpine stack.
- The core data model: Business -> Product -> Variant.
- The separation of stored `lifecycle` from computed `availability`.
- The concept of a computed, buyer-question-based `readiness` score.
- The deterministic, database-grounded "Ready Reply" generator.
- Fast, inline stock operations as a primary seller interaction.

## 18. Do Not Blindly Copy

- The scattered and duplicated domain logic for readiness and availability.
- The non-atomic, incomplete inventory update mechanism.
- The overloaded product card and edit form designs.
- The implicit, auto-creating business/tenant selection.
- The fragile client-side variant formset implementation.
- The reliance on `HTTP_REFERER` for redirects.

## 19. Superseded / Obsolete Historical Areas

- The `README.md` describing the project as a "Stage 0 scaffold."
- The `project_freeze.md` referencing an old working directory.
- Documentation claims of automatic starter-taxonomy seeding or a sentinel "no tag" tag, which were removed or superseded in the prototype's source.
- The `sitemap.md` recommendation to add contextual return paths, as this work was partially implemented in the prototype.

## 20. Important Historical Decisions

- **Inventory-First Pivot:** The foundational strategic choice to focus exclusively on the seller's private inventory cockpit and postpone all buyer-facing and order-management features.
- **Computed Availability & Readiness:** The key architectural principle to compute dynamic state from stored truth, ensuring data integrity and reducing manual seller work.
- **Business-Scoped Taxonomy:** The decision to make product types and tags seller-specific dictionaries rather than a global, platform-wide taxonomy.
- **Server-Rendered Stack:** The deliberate choice of Django with HTMX/Alpine to maximize solo-developer velocity and avoid heavy frontend complexity.

## 21. Open Questions / Owner Decisions

- **Business/Tenant Model:** How should the active business be selected if a user has multiple? What is the explicit onboarding flow?
- **Price Model:** Is `0.00` a valid price, or should price be nullable?
- **Clone Behavior:** Should an "exact clone" also copy stock, or should stock always be reset to zero?
- **Core Scope:** Are product relations, tags, and dynamic types required for the initial MVP, or can they be phased in later?
- **UI/UX:** What is the final, approved responsibility of the Product Detail page? What is the action hierarchy on the Product Card?

## 22. Evidence and Authority Model

1.  **Current Owner-Approved / Frozen Domain Authority:** `docs/domain/CLOTHING_DATA_SPEC_V1.md` (for clothing-specific truth, semantic recognition, and optional measurement support).
2.  **Live/Current Implementation:** The actual source code, tests, and migrations in the `main` branch of the rebuild repository.
3.  **Controlling Documents:** Future owner-approved documents like `BUILD_PLAN.md` that define the current phase and scope.
4.  **Discovery Evidence (`docs/discovery/`):** Analyzed, structured evidence from the prototype. It is more reliable than the raw archive but does not dictate current scope.
5.  **Archive Evidence (`docs/archive/old_docs/`):** Raw historical documents. Useful for intent but the least reliable source for implementation facts.

## 23. Archive Rule

The contents of `docs/archive/old_docs/` represent **historical raw evidence only**. They must never override discovery audits, approved project documentation, or the reality of the live source code.

## 24. Discovery Rule

The contents of `docs/discovery/` represent **analyzed historical evidence and product synthesis**. This layer is highly valuable for understanding prototype lessons but does not automatically define the scope, architecture, or implementation of the current rebuild.

## 25. Context Restoration Checklist

Every future session should begin by checking:
1.  This file: `docs/HOOK.md`.
2.  The current controlling documentation (e.g., `BUILD_PLAN.md`, if it exists).
3.  Relevant source code and tests for the task at hand in the rebuild.
4.  Current `git status` and recent `git log`.
5.  Current CI/build status, when relevant.
6.  The active project phase or functional micro-slice being worked on.

## 26. Drift Guards

- Never treat historical implementation as current implementation.
- Never silently resurrect a prototype feature without explicit approval.
- Never conflate stored `lifecycle` with computed `availability`.
- Never bypass the central inventory service for stock mutations.
- Never allow cross-tenant data access in queries or services.
- Never let a UI partial update leave the global page state inconsistent.
- Never broaden the MVP into orders/payments/public-catalog features without a new, approved scope.
- **Clothing-Specific:**
    - Never promote uncertain text recognition into a factual claim for buyer replies.
    - Never use weight alone to determine size.
    - Never implement measurements without a confirmed value, unit, and method.

## 27. Short Handoff Summary

This project is a clean rebuild of a prototype for a "Social Commerce Seller Operations Assistant." The target is solo sellers in Georgia. The first MVP is an **inventory-first, mobile-first cockpit** to replace spreadsheets.

**Key Lessons from Discovery:** The prototype validated the core product thesis but had significant technical debt. The rebuild must focus on:
1.  **Data Integrity:** Centralize all stock updates through a single, atomic service and create a complete audit trail.
2.  **Strict Tenancy:** Implement robust, test-backed ownership isolation at all layers.
3.  **Clean Architecture:** Separate domain logic into pure services and avoid fat, overloaded views.
4.  **Coherent UX:** Fix the prototype's navigation and state management issues. Ensure partial updates refresh all relevant UI and that all workflows have clear, trustworthy return paths.

**New Clothing Domain Contract:** The `CLOTHING_DATA_SPEC_V1.md` is now the FROZEN authority for clothing data. It emphasizes description-first input, semantic recognition (Observed Text → Recognized Candidate → Confirmed Fact), and structured handling of materials and measurements (with separate implementation for measurements). This contract supersedes older prototype assumptions.

The MVP scope is strictly limited to the private seller dashboard. Do not build buyer-facing features, orders, or payments yet.

---

## Clothing Domain Authority

`docs/domain/CLOTHING_DATA_SPEC_V1.md` is the **FROZEN, OWNER-CONTROLLED, CURRENT CLOTHING-DOMAIN AUTHORITY** for clothing-specific truth, semantic recognition, and optional measurement support. It outranks conflicting historical archive material, prototype implementation behavior, and discovery-only recommendations on these topics.

## Clothing Domain Evolution

The clothing-domain model defined in `CLOTHING_DATA_SPEC_V1.md` represents a significant product/domain expansion and refinement created *after* lessons from the prototype and discovery work. It is a newer, owner-approved direction that goes beyond what was fully implemented or even clearly articulated in the original prototype.

## Description-First Clothing Truth

The core principle for clothing data is **simple seller input leading to structured backend truth**. The seller's primary interaction model is:
`seller description → recognized terms → normalized meaning → seller confirmation only where needed → structured facts → search, readiness, and buyer-question coverage`.
The system acts as an assistant, absorbing inconsistency without forcing complex form bureaucracy.

## Clothing Semantic Destinations

Recognized content from seller input is routed to specific semantic destinations:
-   **Product Type:** What kind of product it is (e.g., "Trousers").
-   **Generic / Feature Tag:** For search, grouping, style, detail, or occasion (e.g., "Classic," "Pockets").
-   **Material:** Fabric or composition fact (e.g., "Cotton").
-   **Choice — Size:** Sellable size option (e.g., "M").
-   **Choice — Color:** Sellable color option (e.g., "Black").
-   **Measurement:** Garment measurement with method and unit (e.g., "Waist: 38 cm, flat width").
-   **Search Token:** For search support only, from normalized observed text.

The system avoids creating a large ontology for every clothing attribute; most style/detail/occasion information remains Generic/Feature Tags unless a specific product behavior requires a separate semantic type.

## Choice-Level Truth

-   **Size** belongs to a `ProductChoice` / `ProductVariant`.
-   **Color** belongs to a `ProductChoice` / `ProductVariant`.
-   **Quantity** belongs to the `ProductChoice` / `ProductVariant`.
-   Size/color recognized in the description are **candidates** for transfer into choices; they must not exist only as generic tags.
-   Confirmed choices remain the source of truth for sellable options and stock.

## Material Truth

Material is a separate typed semantic fact because it affects buyer comfort, allergy concerns, washing expectations, and precise buyer replies.
-   It is recognized from the description, with seller confirmation/correction.
-   A **canonical material** is required for a confirmed material fact.
-   **Percentage** is optional.
-   **Original seller wording** is preserved for traceability.
-   **Confirmation state** is required.
-   The system must not invent technical composition; commercial fabric names are preserved as seller wording.

## Measurement Direction

General size labels (M, XL) belong to the sellable choice. **Detailed garment measurements are a separate capability.**
-   A confirmed measurement needs: `measurement type`, `numeric value`, `unit`, `method/convention`, `applicability` (product/size/choice), `optional seller note`, and `confirmation state`.
-   The **method** (e.g., flat width, circumference) is mandatory because a precise-looking number without context is unsafe.
-   **UX Direction:** Measurements appear behind an optional action (`+ Add measurements`) with category-relevant prompts (e.g., trousers: waist, hip, inseam).
-   **Implementation Boundary:** Measurement implementation requires a **separate approved micro-slice** after conventions are frozen. It is **not** part of the current rebuild's initial scope.

## Fit Guidance Boundary

Fit guidance is **seller-provided context**, not deterministic sizing truth.
-   Examples: "runs small," "relaxed fit," "approximate height/weight guidance."
-   **Rules:** Weight alone never determines size. The assistant must not make medical, biometric, or guaranteed-fit claims. Body profiles and AI sizing are not V1.

## Buyer-Question Coverage

Readiness is **not** a generic completion percentage. Instead, it explains **what buyer questions the assistant can answer truthfully**.
-   Example: "Can answer: Price, Available size/color, Material. Cannot answer yet: Garment length, Waist measurement."
-   The system then recommends one small next action (e.g., "+ Add measurements"). This is a durable product direction.

## Clothing Source-of-Truth Rules

-   **Description text:** Primary seller input, not structured truth.
-   **Product Type / Tags:** Confirmed business vocabulary.
-   **Material replies:** Confirmed material facts.
-   **Size / Color:** Confirmed Product Choices.
-   **Quantity:** Choice-level stock.
-   **Measurements:** Confirmed value + unit + method.
-   **Availability:** Computed from lifecycle + active choice quantities.
-   **Search:** May use normalized observed text and aliases.
-   **Deterministic replies:** Must never promote uncertain search tokens into factual claims.
-   **Missing data:** Creates seller prompts, not invented answers.

## Clothing Anti-Overengineering Guards

-   No field for every imaginable clothing property.
-   Advanced clothing data is not mandatory.
-   Seller does not classify every token.
-   No universal fashion ontology in V1.
-   Not every tag becomes buyer-facing fact.
-   No guaranteed fit.
-   Do not implement the full measurement subsystem inside basic product form work.
-   Do not create pages without real workflow value.
-   Do not add architecture with no current search/reply/readiness/seller-workflow use.

## Deferred Clothing Capabilities

### Architecturally prepared but separately implemented
-   Category-relevant garment measurements.
-   Measurement method/convention.
-   Description-to-measurement candidate recognition.
-   Optional seller fit guidance.
-   Multiple photos and primary-photo selection.

### Deferred (beyond Portfolio V1)
-   AI sizing, automatic fit recommendation, body profile.
-   Public buyer catalog, chatbot integration, label-photo OCR.
-   Universal textile ontology, mandatory full spec forms.
-   Orders, reservations, payment, and delivery.

## Clothing Owner Decisions

The following decisions remain unresolved and require owner approval before measurement implementation:
-   Default measurement unit.
-   Flat width versus circumference convention.
-   Scope of measurement convention (business-wide, category-specific, or per measurement).
-   Whether measurements belong to the product, a size/choice, or both.
-   Initial supported category templates.
-   Whether custom measurement types are allowed in V1.
-   Whether approximate fit guidance appears in V1.
-   Exact buyer-reply wording for measurements.
-   Exact seller UI for confirming recognized measurements.