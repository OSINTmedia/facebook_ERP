# Build Plan

## Document Metadata

- Status: FROZEN_BY_DEFAULT
- Version: 3.0
- Owner: osMit
- Project: Social Commerce Operating Assistant
- Workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Document path: `docs/BUILD_PLAN.md`
- Canonical context: `docs/PROJECT_BIBLE.md` (token-optimized canonical version)
- Operational log: `docs/DEVELOPMENT_NOTES.md`
- Roadmap authority: this file controls implementation order, dependencies, phase/micro-slice boundaries, acceptance, verification, owner-test gates, and stop gates.
- Product authority: `docs/PROJECT_BIBLE.md` controls product intent,  scope, domain semantics, source-of-truth rules, UX contracts, architecture, security, deployment boundaries, and non-goals.
- Execution-state authority: `docs/DEVELOPMENT_NOTES.md` records actual implementation/audit/release state, blockers, recoveries, plan splits/amendments, and the next handoff.
- Release-truth authority: Git/GitHub/CI control exact commit, branch, remote alignment, push, and CI state.
- Update rule: do not update this file for routine progress, Code PASS, Git PASS, commit hashes, CI results, test counts, or normal slice closure. Update only through an owner-approved `PLAN_AMENDMENT` that changes roadmap order, dependency, scope boundary, stop gate, or verification strategy.
- Codex may reorder phases automatically: no.
- Scope-preserving split: allowed only when required for implementation quality; record as `PLAN_SPLIT` in `docs/DEVELOPMENT_NOTES.md` without changing this file.
- Historical documents: earlier planning/discovery/UX/journey/technical/domain documents are provenance, not routine Codex context after Bible adoption.

---

# 1. Purpose

This file is the complete technical execution map for Portfolio .

It answers:

- what must be built;
- in what order;
- which dependencies must exist first;
- what each micro-slice may and may not change;
- what evidence closes the code stage;
- when owner/browser testing is required;
- what evidence closes the Git/release stage;
- which failures require recovery, splitting, or a real plan amendment.

It is not a changelog, runtime checkpoint, CI ledger, commit ledger, or duplicate of the Bible.

The plan favors one coherent, reviewable behavior per micro-slice. Minor implementation details belong inside the owning slice; unrelated high-risk behaviors, schema transitions, or large UX jobs are separated when combining them would lower implementation or audit quality.

---

# 2. Runtime Context and Authority

## 2.1 Normal Codex context

A fresh Codex chat should normally load only:

1. `docs/PROJECT_BIBLE.md` once;
2. this `docs/BUILD_PLAN.md`, focusing first on the current/relevant phase;
3. the latest relevant entries from `docs/DEVELOPMENT_NOTES.md`;
4. current Git/remote/CI facts;
5. relevant source and tests.

Do not routinely reload archived discovery/frozen/UX/journey documents after Bible adoption.

## 2.2 Same-chat incremental context

After Prompt 1 establishes context, subsequent micro-slices in the same chat should not reread the whole Bible or plan unless a concrete conflict or dependency requires it. Use the approved micro-slice contract, current diff/source/tests, relevant plan section, and latest notes.

## 2.3 Read order does not override authority

- Bible controls durable product/system truth.
- Build Plan controls execution order and slice boundaries.
- Development Notes controls current operational handoff/history.
- Code/tests show implementation reality.
- Git/GitHub/CI show exact delivery reality.

A conflict that cannot be resolved within those authorities is `OWNER_DECISION_REQUIRED`; do not silently choose a new product rule.

---

# 3. Frozen-Plan and Exception Rules

## 3.1 Routine progress never edits this plan

Do not edit BUILD_PLAN for:

- NOT_STARTED -> IN_PROGRESS -> CLOSED status churn;
- implementation summaries;
- test counts;
- owner `TEST PASS` results;
- commit hashes;
- push status;
- CI run IDs/results;
- normal phase closure;
- post-push bookkeeping.

Those facts belong in `docs/DEVELOPMENT_NOTES.md` and Git/GitHub/CI.

## 3.2 Code and Git closure semantics

For each micro-slice:

- **Code PASS** = approved implementation completed + P4 audit/hardening passed + required automated verification passed + any REQUIRED owner test returned `TEST PASS` + required pre-release documentation state is coherent.
- **Git PASS** = P5 exact release set committed and pushed + working tree clean + local `HEAD` aligned with actual remote `main` + required exact-SHA CI succeeded.
- **CLOSED** = both Code PASS and Git PASS are proven.

BUILD_PLAN stores the target conditions, never the changing result.

## 3.3 Exception states

Record exceptions by append in `docs/DEVELOPMENT_NOTES.md`:

- `BLOCKER` — approved work cannot proceed.
- `RECOVERY` — smallest correction for a real failure; no unrelated work.
- `PLAN_SPLIT` — parent scope unchanged; split only for safe/reviewable execution.
- `PLAN_AMENDMENT` — real change to roadmap order, dependency, scope, gate, or verification strategy; requires owner approval before editing this plan.
- `DECISION` — durable implementation/product decision not already fixed by the Bible.

A failure never authorizes silent phase skipping or later-phase scope.

## 3.4 Micro-slice sizing

Keep one slice when the work is one coherent behavior with one meaningful acceptance boundary.

Split when a parent item would otherwise combine:

- independent state transitions;
- risky schema/data migrations with unrelated UI work;
- separate security/integrity boundaries;
- multiple unrelated seller jobs;
- verification scopes large enough to reduce implementation/audit quality.

Do not split minor template text, one validation branch, one test assertion, or a small correction into artificial phases.

## 3.5 Owner-test rule

Every future micro-slice declares owner testing as `REQUIRED`, `ADVISORY`, or `NOT_REQUIRED`.

If REQUIRED:

- P4 prints one short reproducible scenario;
- Code PASS is blocked until owner replies `TEST PASS`;
- owner verification stays inside the same slice;
- it never creates a second documentation/micro-slice cycle.

## 3.6 No post-closure sync cycle

P4 owns audit/hardening plus all required pre-release documentation coherence.

P5 owns exact staging, commit, push, alignment, and exact-SHA CI verification.

Successful P5 closes the slice. Do not create a follow-up docs/hash/CI synchronization slice.

---

# 4. Global  Engineering Guardrails

These constraints apply to every phase and need not be repeated unless a slice has a special risk.

## Product and UX

- Seller-first private operating assistant; not public ecommerce/ERP administration.
- Product Workspace is the primary daily work surface.
- Dashboard is secondary and action-oriented.
- No dedicated Product Detail in .
- Description is the primary seller-authored capture/identity surface.
- UI is Georgian-first; code/DB/enums remain English.
- Keep the seller on a small number of surfaces; use progressive disclosure rather than new pages.
- Preserve explicit safe return context; browser Back is never the only workflow.
- Mobile-first and accessibility are architecture/release concerns, not final decoration.

## Truth and domain

- Observed Text != Candidate != Confirmed Fact.
- Candidates never silently become buyer-facing truth.
- No LLM owns operational truth.
- Business is the tenant/ownership boundary.
-  UI has one active Business workspace and never silently selects an arbitrary first Business.
- Product lifecycle is stored and separate from computed availability.
- Lifecycle values: `draft`, `active`, `archived`; no `hidden`.
- Draft may have zero choices.
- Active requires >=1 valid active ProductChoice.
- Restore always returns archived Product to Draft.
- ProductChoice owns size, color, quantity, active state, and stable row identity.
- Duplicate trim/case-normalized size+color ProductChoice rows are valid distinct identities; never auto-merge.
- Product quantity is never a Product-level truth.
- Price: `NULL=missing`, `>0=confirmed`, `0/negative=invalid`; no free-price mode.
- Active Product may remain operational with missing price, but is not price-answer-ready.
- Material is a typed confirmed fact, not a generic Tag; negation must not create positive material truth.
- Detailed measurements, fit guidance, AI sizing/body profile, publication/public catalog, chatbot, orders, payments, delivery, CRM, suppliers, accounting, product relations, and broad ERP remain deferred/out of .

## Inventory

- All mutable stock operations use one inventory service boundary.
- Allowed  operations: `+1`, `-1`, direct set nonnegative quantity; direct set is secondary UI.
- Existing ProductBundle editing must not become an alternate stock-write path.
- Mutation must be Business/actor/exact-choice authorized, nonnegative, concurrency-safe, atomic, and audited.
- Every accepted mutation creates one immutable InventoryAdjustment in the same successful transaction; rejected mutations create no successful fact.
- Availability is centralized and computed from lifecycle + active choice stock.
- Dashboard, Workspace, filters, readiness, and Ready Reply must consume the same availability logic.
- Low-stock policy is centralized/configurable; it is not lifecycle.
- HTMX carries intent and transports server truth; client state does not own quantity/availability/lifecycle/readiness.

## Architecture and security

- Django modular monolith + PostgreSQL.
- Django Templates + HTMX + Alpine local state only + reproducible production asset handling.
- Views orchestrate HTTP; domain truth belongs in explicit forms/services/policies/query helpers.
- No microservices/event bus/Kafka/Kubernetes/premature Celery/Redis/API-first/SPA complexity without a current consumer/need.
- Seller routes require authentication.
- Business isolation is release-blocking.
- CSRF remains enabled; mutations use correct methods.
- Unsafe external `next` is rejected; raw `HTTP_REFERER` is not canonical workflow authority.
- Never commit secrets, `.env`, dumps, backups, private logs/media/data, live sessions, caches, or local DB artifacts.
- If uploads exist: validate type/size, use safe names/paths, keep outside source control, and define failure cleanup.

## Verification and Git

- AI-generated code requires source inspection and appropriate tests/manual checks.
- Critical business/inventory/isolation regressions are release-blocking.
- CI minimum: install dependencies, Django system check, migration consistency/missing-migration check, tests.
- Git history remains honest/chronological; no force-push/rewrite of published main, fake/backdated commits, or meaningless commit noise.
- One meaningful delivery intention per commit.
- Exact hashes/CI metadata live in Git/GitHub, not this plan.

---

# 5. Stop Gates

| Gate | Purpose | Pass condition |
|---|---|---|
| Gate 0 | Planning/repository baseline | owner-approved baseline and safe repository history exist |
| Gate 1 | Django/PostgreSQL/CI foundation | reproducible scaffold/settings/PostgreSQL/tests/CI proven |
| Gate 2 | Ownership/isolation | auth + Business boundary + cross-Business tests proven |
| Gate 3 | Core truth/inventory integrity | Product/recognition/choices/inventory/availability boundaries proven |
| Gate 4 | Seller UX/operational coherence | final Workspace/Dashboard/readiness/reply/maintenance/mobile/a11y flow proven |
| Gate 5 | Portfolio hardening | synthetic demo lifecycle, setup, security, docs, local release rehearsal proven |
| Gate 6 | Deployment/demo | real Django/PostgreSQL hosted demo and smoke/owner verification proven |
| Gate 7 | Public release | final drift/security/evidence audit and owner release approval proven |

Do not move past a gate while a release-blocking defect or unresolved required owner test remains.

---

# 6. Historical Execution Baseline — Completed Work Through P6.7c

This section is a compact execution anchor, not a status ledger. Exact commits, CI runs, detailed decisions, and correction history remain in Git/GitHub and `docs/DEVELOPMENT_NOTES.md`.

## Phase 0 — Documentation and Repository Foundation

Historical result: completed.

Delivered intent:

- discovery/planning baseline;
- existing public GitHub history preserved;
- repository hygiene established before substantive implementation;
- honest chronological rebuild history started;
- public README kept factual for the implementation stage.

Historical micro-slice families: owner review/freeze, GitHub/local reconciliation, hygiene baseline, documentation baseline, README baseline, first approved push, governance correction. Optional issue/milestone setup remained nonessential.

## Phase 1 — Django/PostgreSQL Foundation and CI

Historical result: completed; Gate 1 passed.

Delivered micro-slices:

- P1.1 Python/Django dependency baseline;
- P1.2 clean Django scaffold;
- P1.3 environment-aware settings;
- P1.4 PostgreSQL/test database baseline and runtime proof;
- P1.5 minimal private application shell;
- P1.6 CI and initial test harness.

Preserved truth: PostgreSQL-only architecture, fail-fast production settings, no secret fallback, reproducible tests/checks, server-rendered shell.

## Phase 2 — User and Business Ownership

Historical result: completed; Gate 2 passed.

Delivered micro-slices:

- P2.1 Accounts app and custom seller User baseline;
- P2.2 Business model and ownership boundary;
- P2.3 authenticated login/logout baseline;
- environment-gated synthetic demo seller access bootstrap;
- P2.4 owner-scoped active Business resolver/query boundary;
- P2.5 cross-Business access test baseline.

Preserved truth: no hidden Business creation/selection side effects; unsupported multi-Business ambiguity remains explicit; Business isolation is reusable and release-blocking.

## Phase 3 — Catalog Core

Historical result: completed.

Delivered micro-slices:

- P3.1 Product model baseline;
- P3.2 Product form baseline;
- P3.3 authenticated Business-scoped Product list baseline;
- P3.4 Product create/edit baseline.

Historical limitation intentionally carried forward: price semantics were not implemented while unresolved; canonical price truth is scheduled in P7.1 rather than retroactively rewriting Phase 3.

## Phase 4 — Semantic Recognition and Choice Model

Historical result: completed.

Delivered micro-slices/families:

- P4.1 semantic recognition service contract;
- P4.2 Business Product Type recognition;
- P4.3 Business Tag recognition;
- P4.4 Business-scoped alias normalization;
- P4.5a confirmed material fact baseline;
- P4.5b material candidate recognition from confirmed facts;
- P4.6 size/color suggestion-only recognition;
- P4.7 ProductChoice model baseline plus forward correction allowing duplicate visible choices;
- P4.8 atomic Product/choice bundle validation;
- P4.9a ProductChoice create/edit integration;
- P4.9b automatic transient recognition preview;
- P4.9c Business Size/Color controlled vocabulary/dropdowns;
- P4.9d explicit candidate-to-choice transfer;
- P4.9d_expand Size/Color vocabulary maintenance;
- P4.9e explicit Product Type/Tag confirmation attachment;
- P4.9e_expand Product Type/Tag vocabulary maintenance;
- P4.9f explicit material confirmation/correction/removal;
- P4.10 Phase 4 audit/transition.

Preserved truth: Description/Observed/Candidate/Confirmed separation, Business vocabulary, controlled size/color truth, confirmed material, duplicate ProductChoice identity, atomic bundle, no measurements/LLM/public buyer scope.

Known accepted UX debt: Product create/edit is technically correct but not yet sufficiently assistant-like; it is intentionally refined in P7.3 rather than reopening historical Phase 4 work.

## Phase 5 — Inventory and Computed Availability

Historical result: completed; Gate 3 passed.

Delivered micro-slices:

- P5.1 pure Product availability service;
- P5.2 Business-scoped immutable InventoryAdjustment ledger;
- P5.3 atomic `+1/-1` inventory service with locking/concurrency protection;
- P5.4 ProductBundle stock-write boundary enforcement;
- P5.5 authenticated Business-scoped stock mutation route;
- P5.6 HTMX/native exact-choice stock controls;
- P5.6A one-save initial stock capture through a guarded `0 -> N` transition;
- P5.7 integrated inventory transition/regression readiness;
- P5.8 inventory integrity hardening for bulk/overflow edges.

Preserved truth: one mutable stock boundary, immutable ledger, exact ProductChoice identity, no lost updates, ProductBundle cannot overwrite existing stock, computed availability is separate from lifecycle.

Historical deferred item now owner-resolved by the Bible: ongoing Direct Set is  scope and is scheduled in P10.1; it is not retroactively inserted into Phase 5 history.

## Phase 6 — Operational Product Workspace

Historical/current baseline: P6.1 through P6.7c delivered; P6.7d is the next closure gate. Runtime proof always comes from Development Notes + Git/GitHub/CI.

Delivered sequence:

- P6.1 Product Workspace route/query baseline;
- P6.2 compact Product card and shared availability read model;
- P6.3 exact-choice Workspace stock controls with native truthful fallback;
- P6.4 deterministic Business-scoped Product search;
- P6.5 bounded lifecycle + availability filters and canonical URL state;
- P6.6 full-results HTMX truth refresh/state coherence;
- P6.7a first-viewport/mobile-density repair;
- P6.7b canonical Workspace return-path hardening;
- P6.7c accessibility and recovery hardening.

Preserved truth: Workspace is primary; lifecycle != availability; duplicate choices remain exact identities; query/filter state is server-owned and canonical; stock writes still use Phase 5; HTMX cannot leave quantity/availability/result membership stale; return paths and focus/recovery are explicit.

---

# 7. P6.7d — Phase 6 Integrated Regression and Owner Closure Gate

- Objective: prove the complete P6.1-P6.7c Product Workspace contract and close Phase 6 without adding new product behavior.
- Dependency: P6.7c must have Code PASS and Git PASS according to current source/tests, `docs/DEVELOPMENT_NOTES.md`, Git, remote alignment, and exact-SHA CI evidence.
- Scope: execute the integrated Phase 6 matrix across authentication, Business isolation, canonical search/filter/return state, Product cards, exact duplicate-choice identity, native/HTMX stock transitions, loading/error/recovery/focus, empty/no-result states, query growth, responsive behavior, and keyboard accessibility. Add only missing regression assertions inside the established Phase 6 test boundary.
- Excludes: source repair, new Product behavior, Dashboard, readiness, Ready Reply, Product Detail, new filters, pagination, Product create/edit redesign, Direct Set, Add Similar, Archive/Restore, media, price, schema/dependency changes, deployment, and opportunistic refactoring.
- Failure rule: any real functional/security/integrity/navigation/accessibility/responsive/stale-truth defect makes the gate FAIL/BLOCKED and creates the smallest separately approved P6.7 recovery slice. P6.7d does not absorb repair work.
- Acceptance: focused Phase 6 tests and full PostgreSQL regression pass; Django system/migration checks and diff checks pass; desktop and ~390px owner/browser matrix passes; no Phase 6 Business-isolation, stale-truth, return-path, accessibility, or responsive blocker remains.
- Verify: Phase 6 focused tests; Product/choice/inventory/return/isolation regressions; full PostgreSQL suite; system check; migration consistency; JS syntax where applicable; diff/whitespace checks.
- Owner test: REQUIRED — combined search/filter state; Edit Cancel/save return; one exact duplicate-looking choice mutation; `1 -> 0` and `0 -> 1`; slow request; expected validation error; forced transport recovery; keyboard focus; ~390px layout; no horizontal overflow. Owner reply: `TEST PASS` or concise failure.
- Code status target: PASS.
- Git status target: PASS.
- Next: Phase 7.
- Commit intent: `test: verify product workspace release readiness`.

---

# 8. Phase 7 — Product Truth Completion and Readiness

## Goal

Close remaining canonical Product truth gaps and make Description-first Product correction visibly assistant-led before Dashboard and Ready Reply consume the truth model.

## Boundaries

- Keep Product Workspace primary.
- No Product Detail.
- No public catalog/chatbot/orders/payments/delivery.
- No measurement subsystem/fit guarantee/body profile/AI sizing.
- No LLM-owned truth.
- No new top-level seller surface.

### P7.1 Price Truth Integration

- Objective: implement canonical Product price semantics end-to-end.
- Scope: nullable Product price; `NULL=missing`, `>0=confirmed`, `0/negative=invalid`; use Business/default currency semantics already present or add only the minimum canonical currency relation needed; migration; server validation; Product create/edit capture; Workspace price display; expose missing-price truth to later readiness/reply consumers.
- Excludes: free mode, discounts, currency conversion, ProductChoice price override, public pricing, readiness UI, reply generation.
- Acceptance: existing Products migrate safely with missing price; Draft and valid Active Product may remain missing-price; zero/negative confirmed price is rejected; missing price never appears as zero/free; ProductBundle atomicity and Business isolation remain intact.
- Verify: migration/model/form/ProductBundle/view tests; missing/zero/negative/positive matrix; Workspace regression; full PostgreSQL suite.
- Owner test: REQUIRED — create/edit one missing-price Product, attempt zero, save positive price, verify Workspace display and canonical return context. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P7.2.
- Commit intent: `feat: add product price truth`.

### P7.2 Optional Product Media Baseline

- Objective: implement safe optional Product media sufficient for Product identification and portfolio demo use.
- Scope: optional Business/Product-owned media boundary; one stable primary representation/deterministic first-media rule; create/edit attachment; Workspace thumbnail and deliberate placeholder; type/size/path validation; safe generated filenames/paths; failure cleanup; source-control exclusion; synthetic/demo-safe media compatibility.
- Excludes: OCR, image recognition, semantic photo roles, large gallery management, buyer gallery, automatic Add Similar media copy, private prototype media.
- Acceptance: Product saves without media; valid owned media displays; missing media never breaks layout; unsafe/cross-Business media access/attachment is rejected; failure does not leave misleading partial sellable Product/media state.
- Verify: model/form/service/view/upload validation; cleanup/failure path; Business isolation; ProductBundle regression; media path/security checks; full PostgreSQL suite.
- Owner test: REQUIRED — create Product without media, then with one safe test image; verify placeholder/image on desktop and ~390px and no broken return/validation state. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P7.3.
- Commit intent: `feat: add optional product media`.

### P7.3 Description-First Create/Edit Assistant Refinement

- Objective: make Product create/edit behave like the intended seller assistant rather than an ecommerce specification form while preserving all released truth boundaries.
- Scope: Description becomes the dominant required seller-authored capture/identity field; reduce secondary-field competition; organize price, recognition, confirmed Type/Tags/material, controlled Size/Color choices, starting stock, and optional media through compact hierarchy/progressive disclosure; preserve no-write preview/transfer and exact return context. If a separate `name` field remains in current schema, remove its mandatory seller burden when safe, or keep it only when current implementation proves a necessary non-duplicative identity role.
- Scope also includes: accidental duplicate-operation protection for candidate-to-choice actions/retries/repeated taps; normalized-equivalent existing choice must be surfaced before any intentional additional distinct row action.
- Excludes: new semantic destinations, full Georgian morphology/fuzzy/AI parsing, measurements, Ready Reply, Dashboard, silent candidate confirmation, universal taxonomy, large form-builder behavior.
- Acceptance: seller can begin from minimal Description; recognition remains visible but non-authoritative; seller can explicitly confirm/correct facts without navigating through taxonomy bureaucracy; validation is local and preserves all input; intentional duplicate choices remain allowed but accidental repeated transfer side effects do not occur; vocabulary management stays subordinate/contextual.
- Verify: create/edit/ProductBundle/recognition/transfer/vocabulary/material/choice/return tests; duplicate-operation/idempotency regression; mobile/a11y checks; full PostgreSQL suite.
- Owner test: REQUIRED — create from a short Description; inspect recognition; confirm/correct one semantic fact; transfer one choice suggestion; intentionally repeat the transfer action and verify no accidental duplicate; trigger validation error; recover without data loss at ~390px. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P7.4.
- Commit intent: `fix: refine description first product workflow`.

### P7.4 Buyer-Question Coverage Service

- Objective: create one pure readiness service that reports which supported buyer questions are answerable from confirmed/computed truth.
- Scope: centralized coverage for price, availability/stock, size/color, Product Type, and confirmed material; structured missing reasons; correction targets; no percentage score. A Tag affects a specific question only if an explicit semantic rule exists; mere Tag count never improves readiness.
- Excludes: unimplemented measurements/fit questions; generic completion scoring; LLM inference; Dashboard UI; Ready Reply text generation.
- Acceptance: identical confirmed truth gives identical coverage; missing price/material/etc. creates explicit seller gaps; unconfirmed Candidate never satisfies coverage; sold-out truth remains truthful; optional Tags do not create generic readiness; service consumes centralized availability.
- Verify: pure service truth matrix; missing/confirmed states; sold-out/partial-choice states; duplicate-choice identity; candidate-vs-confirmed; Business-scoped consumer tests; full regression.
- Owner test: NOT_REQUIRED.
- Code status target: PASS.
- Git status target: PASS.
- Next: P7.5.
- Commit intent: `feat: add buyer question coverage service`.

### P7.5 Workspace Readiness, Partial-Stock Signal, and Correction Loop

- Objective: expose readiness as a concrete reward and smallest-next-action loop without overloading Product cards.
- Scope: compact answerable/missing state; no completion percentage; smallest useful correction action; missing-price and other answer-critical signals; explicit partial-sold-out signal when active choices contain both zero and positive stock; preserve lifecycle/availability distinction and existing availability filter semantics; correction returns to exact Workspace state.
- Excludes: Ready Reply generation, permanently expanded readiness dashboard, nagging optional fields, measurements, new top-level page, arbitrary new filters.
- Acceptance: well-structured Product visibly communicates useful answer coverage; incomplete Product says exactly what is missing; partial sold-out is a computed operational signal rather than lifecycle; missing-fact correction improves coverage after save; no Candidate/stale state is presented as answer-ready; card priority remains Product/price/lifecycle+availability/choice stock before secondary readiness actions.
- Verify: Workspace/readiness/partial-stock rendering; correction return matrix; stock `1->0`/`0->1`; HTMX state coherence; price/media regressions; mobile/a11y; full PostgreSQL suite.
- Owner test: REQUIRED — compare a strong Product, missing-price Product, missing-material Product, and mixed-stock Product; follow one correction and verify updated coverage without card overload. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Phase 7 closure: all P7 slices CLOSED and integrated Product/recognition/price/media/readiness regressions pass.
- Next: Phase 8.
- Commit intent: `feat: surface product answer readiness`.

---

# 9. Phase 8 — Dashboard and Attention Signals

## Goal

Build the secondary seller overview that answers “what needs attention now?” using shared Product, inventory, availability, and readiness truth.

### P8.1 Attention Query Service and Low-Stock Policy

- Objective: centralize seller attention signals without creating a second truth model.
- Scope: Business-scoped queries for sold out/restock candidates, partially sold-out choices, low stock, missing answer-critical facts, and empty catalog; one centralized/configurable low-stock threshold/policy; deterministic counts/lists; bounded query behavior.
- Excludes: charts, BI analytics, notifications, polling, background jobs, duplicated availability/readiness formulas, order/payment signals.
- Acceptance: signals match shared availability/readiness exactly; low-stock threshold is defined once and reused; draft/archived semantics are intentional; inactive choices do not create false sellable alerts; cross-Business facts never contribute; query growth remains bounded.
- Verify: service/query matrix; threshold boundaries; sold/partial/restock/readiness parity; Business isolation; query-count tests.
- Owner test: NOT_REQUIRED.
- Code status target: PASS.
- Git status target: PASS.
- Next: P8.2.
- Commit intent: `feat: add seller attention queries`.

### P8.2 Action-First Dashboard and Workspace Drilldowns

- Objective: expose only actionable overview information and route real work back to the Product Workspace.
- Scope: first viewport prioritizes needs attention, low stock, sold-out/restock, missing answer-critical facts, and empty-catalog quick add; compact summaries drill into canonical Workspace contexts; add only minimum server-owned attention state needed for precise drilldown; explicit safe return to Dashboard where the journey originates there.
- Excludes: decorative metrics/charts, marketing content, analytics BI, separate CRUD cockpit, Product Detail, client-owned counts, live polling, unrelated navigation branches.
- Acceptance: Dashboard remains secondary; every signal leads to real work in Workspace/correction; counts/membership equal shared truth; no duplicated state formula; return path is explicit; mobile first viewport shows useful action rather than decoration.
- Verify: dashboard view/query tests; attention drilldown/return matrix; Business isolation; query growth; readiness/availability parity; full regression.
- Owner test: REQUIRED — verify empty, low-stock, sold-out/partial-stock, and missing-info states; open two drilldowns, correct/mutate one Product, return explicitly, check desktop and ~390px. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Phase 8 closure: P8.1-P8.2 CLOSED with integrated Dashboard/Workspace truth checks.
- Next: Phase 9.
- Commit intent: `feat: add action first seller dashboard`.

---

# 10. Phase 9 — Deterministic Ready Reply Reward Loop

## Goal

Turn confirmed Product truth into immediate seller value through truthful, copyable responses without Product Detail or LLM truth ownership.

### P9.1 Deterministic Reply Service

- Objective: generate seller-ready answer content exclusively from confirmed facts and centralized computed state.
- Scope: Business/Product authorization; deterministic response components for known price, availability/stock, size/color, Product Type, confirmed material, and safe Description text; conservative duplicate-choice wording; sold-out truth; seller-only missing-data notes; reusable service boundary for future buyer assistant.
- Excludes: sending messages, chatbot/public API, LLM-generated commercial facts, unimplemented measurements/fit claims, scientific material inference, buyer account state.
- Acceptance: missing truth is omitted/flagged seller-side; missing price never becomes zero/free; sold-out never implies availability; duplicate-visible choices never gain fabricated distinctions/aggregation; unconfirmed Candidates never enter buyer text; same truth yields deterministic output.
- Verify: reply truth matrix; missing price/material; available/partial/sold-out; duplicate-choice ambiguity; Description safety; Business isolation; readiness parity.
- Owner test: ADVISORY — inspect representative deterministic outputs.
- Code status target: PASS.
- Git status target: PASS.
- Next: P9.2.
- Commit intent: `feat: add deterministic ready reply service`.

### P9.2 On-Demand Workspace Ready Reply UI

- Objective: expose Ready Reply as an on-demand reward without permanently increasing Product-card density.
- Scope: subordinate Workspace action opens focused server-backed panel/drawer/disclosure; buyer-facing text and seller-only notes are visibly separated; copy action with success and clipboard-failure fallback; missing-data correction links preserve Product/Workspace context; accessible focus/close behavior.
- Excludes: dedicated Product Detail; always-expanded giant reply panel; auto-send; chatbot; client-generated truth; excessive mode/tab proliferation.
- Acceptance: normal card remains compact; reply appears only on seller intent; copied text never includes internal warnings; missing truth produces seller correction guidance; clipboard failure is visible and recoverable; sold-out/partial state remains truthful; no route wandering.
- Verify: service/view/partial integration; no-warning-leak tests; copy hooks/fallback; focus/a11y; return paths; mobile density; full truth regression.
- Owner test: REQUIRED — open Ready Reply for complete, incomplete, partial-stock, and sold-out Products; copy; force clipboard failure; follow one correction and return; confirm reward value without card clutter. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Phase 9 closure: P9.1-P9.2 CLOSED and truth-safe reply regression passes.
- Next: Phase 10.
- Commit intent: `feat: add workspace ready reply`.

---

# 11. Phase 10 — Seller Speed and Lifecycle Maintenance

## Goal

Add owner-approved maintenance actions that reduce repetitive work without weakening stock identity, auditability, or the Workspace-first UX.

### P10.1 Secondary Direct Stock Set

- Objective: support deliberate exact-quantity correction/restock through the existing inventory service and ledger.
- Scope: direct set nonnegative quantity on one exact ProductChoice; same Business/actor checks, lock/concurrency safety, transaction, availability/reply/readiness refresh, and immutable InventoryAdjustment path as `+/-`; ensure ledger mutation-kind semantics can distinguish set from other accepted transitions without inventing a broad reason-code taxonomy; secondary UI hierarchy.
- Excludes: bulk set, Product-level quantity, arbitrary stock forms, optimistic client quantity, ProductBundle saved-stock writes, advanced movement reasons/accounting.
- Acceptance: set-to-current is no-op and creates no false transition; real set creates one exact audited transition; invalid/out-of-range/cross-Business request writes nothing; duplicate-looking rows remain exact targets; all affected Workspace membership/availability/readiness/reply truth refreshes correctly.
- Verify: service/concurrency/ledger/mutation-kind/route/HTMX tests; storage edges; Business isolation; existing `+/-` and initial-stock regressions; full suite.
- Owner test: REQUIRED — direct-set one exact choice higher and then zero, including one duplicate-looking row; confirm action is subordinate to `+/-` and exact identity is obvious. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P10.2.
- Commit intent: `feat: add direct stock set`.

### P10.2 Add Similar

- Objective: reduce repeated entry with one explicit Add Similar command.
- Scope: new Product identity; starts Draft; copy useful stable confirmed Product-level facts and approved choice structure; every copied quantity reset to zero; never copy InventoryAdjustment history; media not copied by default; seller enters normal correction/edit context; originating Workspace state preserved.
- Excludes: similarity recommendation AI; clone modes; live-stock copy; ledger copy; silent activation; media copy by default; bulk cloning.
- Acceptance: source unchanged; new Product is Draft; copied choices are new identities with zero quantity; no inventory fact/history copied; seller reviews distinguishing facts before activation; Business isolation and bundle atomicity hold.
- Verify: command/service transaction tests; copied/not-copied field matrix; choice identity; no-ledger assertions; return context; full regression.
- Owner test: REQUIRED — Add Similar from a populated Product; confirm copied truth/choice structure, zero stock, no copied media/history; edit one difference and save; return to originating Workspace. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P10.3.
- Commit intent: `feat: add similar product workflow`.

### P10.3 Archive and Restore-to-Draft

- Objective: remove obsolete Products from daily operations without deleting history and restore them safely for explicit review.
- Scope: complete `archived` lifecycle; explicit confirmed archive; archived Products excluded from normal daily operation, availability, readiness-as-sellable, and normal Ready Reply; subordinate archived retrieval/filter context; restore always to Draft; history/choices/inventory preserved; secondary action hierarchy.
- Excludes: hard delete, separate Hidden state, public unpublish/publication field, automatic reactivation, bulk archive.
- Acceptance: archive preserves history but removes sellability/daily work; archived Product cannot produce wording implying active availability; restore never silently Active; Business isolation applies; archive action cannot compete visually with stock operations.
- Verify: lifecycle/service/view/filter/readiness/reply tests; migration if required; archive/restore return paths; Business isolation; full regression.
- Owner test: REQUIRED — archive active Product, confirm it leaves normal work/reply availability; retrieve archived Product, restore, confirm Draft and history intact. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Phase 10 closure: P10.1-P10.3 CLOSED with integrated Workspace/readiness/reply/lifecycle/inventory regression.
- Next: Phase 11.
- Commit intent: `feat: add product archive restore workflow`.

---

# 12. Phase 11 — Workspace Scale and Final Seller UX Hardening

## Goal

Ensure the final seller workflow remains bounded, mobile-first, accessible, recoverable, and assistant-like after all  operational features are present.

### P11.1 Server-Side Pagination / Bounded Catalog Loading

- Objective: remove the unbounded-list scaling risk while preserving canonical Workspace state and server truth.
- Scope: server-side pagination or equivalent bounded loading; canonical `page` state; deterministic ordering; preserve `q`, lifecycle/availability/attention state; understandable result/page state; explicit empty/out-of-range recovery; stock/HTMX/correction actions preserve or return to valid page context; deliberate select/prefetch/index review for common Business/search/filter paths.
- Excludes: infinite-scroll-only strategy, client-owned result truth, Elasticsearch/OpenSearch, external search service, fuzzy/morphology search, speculative distributed cache.
- Acceptance: representative large catalog never requires unbounded render; state survives page/edit/correction/mutation journeys; last-item membership change resolves to valid server page/state; no N+1/query-growth regression; result/no-result/page state understandable on mobile.
- Verify: pagination/state/query-count tests; search/filter/attention composition; mutation membership; return-path matrix; indexes/query review; full regression.
- Owner test: REQUIRED — use multi-page catalog on desktop/~390px; search/filter/page, edit-return, stock mutation near availability boundary, clear state, verify no scroll-wall or lost context. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P11.2.
- Commit intent: `feat: paginate product workspace`.

### P11.2 Final Cross-Surface UX, Georgian Terminology, Accessibility, and Failure Hardening

- Objective: harden final  seller experience without adding new product scope.
- Scope: Product Workspace, Dashboard, create/edit/correction, vocabulary sub-surface, readiness, Ready Reply, Direct Set, Add Similar, Archive/Restore; first viewport; action hierarchy; Georgian terminology consistency and long-label wrapping; Product card priority; tap targets; keyboard/focus; announcements; image alt/placeholder; form/error association; HTMX loading/failure/recovery; clipboard failure; safe return matrix; no color-only state; no accidental destructive tap zones; Tailwind/asset behavior must remain compatible with final production strategy.
- Excludes: new features, full WCAG compliance claim, measurements, public buyer surfaces, chatbot, decorative redesign, SPA/framework migration, new frontend dependency without demonstrated need.
- Acceptance: Workspace remains primary and Dashboard secondary; seller does not wander; no Product Detail dependency; cards remain compact; secondary actions remain subordinate; mobile has no horizontal overflow or buried primary work; keyboard/focus/failure recovery works; Georgian seller language is concrete/non-ERP; server truth remains authoritative.
- Verify: cross-surface focused regressions; JS syntax; template/a11y assertions where useful; full PostgreSQL suite; manual matrix.
- Owner test: REQUIRED — complete final seller journey on desktop and ~390px: create/correct, vocabulary recovery, search/filter/page, `+/-` and set, readiness, Ready Reply/copy failure, Dashboard drilldown, Add Similar, archive/restore, keyboard/focus, HTMX failure. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Phase 11 closure / Gate 4: Gate 4 passes only when P11.1-P11.2 are CLOSED and no unresolved seller UX/navigation/accessibility/stale-state blocker remains.
- Next: Phase 12.
- Commit intent: `fix: harden final seller experience`.

---

# 13. Phase 12 — Demo Lifecycle and Portfolio Hardening

## Goal

Make the repository and local demo safe, reproducible, resettable, reviewer-ready, and deployment-ready using synthetic data only.

### P12.1 Synthetic Demo Seed and Reset/Reseed

- Objective: provide deterministic interactive demo data and a safe restoration lifecycle.
- Scope: explicit management commands/processes for synthetic demo User/Business/catalog/media seed and reset/reseed; protected identities; deliberate destructive confirmation/dry-run where appropriate; representative states: available, low stock, partially sold out, sold out, Draft, missing price, missing media, confirmed recognition/material truth, strong/weak readiness, duplicate-visible choices, Ready Reply examples, Add Similar/archive scenarios.
- Excludes: real prototype/customer/seller data, private source media, automatic destructive startup seed, commercial onboarding, analytics BI.
- Acceptance: known baseline can be created/recreated; reset cannot escape approved demo scope; protected owner/demo identities remain safe; media cleanup policy is explicit; commands are tested/idempotent where designed; no private data enters Git.
- Verify: management-command tests; reset scoping; confirmation/dry-run; idempotency; media cleanup; full regression.
- Owner test: REQUIRED — seed, use several workflows, reset/reseed, confirm expected baseline returns and protected login still works. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P12.2.
- Commit intent: `feat: add safe demo lifecycle`.

### P12.2 Repository, Security, Setup, Asset, and Production-Readiness Hardening

- Objective: remove portfolio/deployment blockers before external hosting.
- Scope: reproducible setup verification; dependency review; PostgreSQL-only parity; production fail-fast settings; `DEBUG=False`; required secret key; explicit hosts/CSRF origins; secure-cookie expectations for HTTPS; secret/repository hygiene; migration consistency; production static/media strategy; replace/avoid prototype CDN assumptions with reproducible production asset handling (including Tailwind strategy if used); upload validation/storage policy; health-check entry point if needed; CI completeness; README setup accuracy for currently verified local behavior.
- Excludes: public demo URL claim before deployment; new Product functionality; provider-specific commercial feature work.
- Acceptance: clean setup path is reproducible; no secret/private/generated artifact tracked; production configuration fails safely; static/media/assets have a deployable strategy; migrations/tests/CI are coherent; README does not overclaim deployment.
- Verify: setup/runtime checks; repository/secret scan; Django system/deploy checks as appropriate; migration checks; static/asset build/collect check; full tests/CI-equivalent checks.
- Owner test: ADVISORY — review setup/security/public wording if changed materially.
- Code status target: PASS.
- Git status target: PASS.
- Next: P12.3.
- Commit intent: `chore: harden portfolio deployment readiness`.

### P12.3 Local Portfolio Release Rehearsal

- Objective: prove complete Portfolio  locally from reviewer and engineering perspectives before deployment.
- Scope: full critical regression matrix; Business-isolation/security checks; synthetic seed/reset rehearsal; complete seller walkthrough; Bible/Build Plan/Development Notes/source/tests/README drift audit; no deferred features accidentally implemented as scope; repository hygiene and Git-history sanity.
- Excludes: feature repair inside rehearsal; any discovered defect becomes smallest RECOVERY slice.
- Acceptance: no unresolved local release blocker; Gate 5 evidence complete; no false README claim; project can deploy without hidden local-only assumptions.
- Verify: full PostgreSQL suite; CI-equivalent checks; manual demo rehearsal; docs/security/hygiene drift scan.
- Owner test: REQUIRED — concise reviewer path from login through create/correct, Workspace/search/filter/page, stock, readiness, Ready Reply, Dashboard, Add Similar, archive/restore, reset/reseed. Reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Phase 12 closure / Gate 5: Gate 5 passes only when P12.1-P12.3 are CLOSED.
- Next: Phase 13.
- Commit intent: `chore: verify portfolio release readiness`.

---

# 14. Phase 13 — Deployment and Online Demo

## Goal

Deploy the real Django/PostgreSQL portfolio application on backend-capable hosting and verify the hosted system rather than only local/repository state.

### P13.1 Deployment Target and Production Configuration

- Objective: select/configure a technically honest hosting path without provider lock-in in application architecture.
- Scope: backend-capable provider decision; Django service + PostgreSQL + HTTPS + environment secrets + migrations + static/media + reset/reseed capability; build/start/migration commands; allowed hosts/CSRF/security settings; provider account/cost decision only where owner authority is genuinely required.
- Excludes: GitHub Pages as runtime; SQLite substitution; product feature changes; fake/live URL claim before proof.
- Acceptance: deployment model can run Django/PostgreSQL securely; no insecure fallback; platform-specific config is minimized/documented; owner choices are requested only when account/cost authorization is necessary.
- Verify: production-settings import/checks using safe environment; deployment config review; no secret leakage.
- Owner test: REQUIRED only when provider/account/cost authorization is needed; otherwise ADVISORY.
- Code status target: PASS.
- Git status target: PASS for any repository/config changes.
- Next: P13.2.
- Commit intent: `chore: configure production deployment`.

### P13.2 Hosted Application and PostgreSQL Provisioning

- Objective: bring up the exact repository application and PostgreSQL schema on the selected host.
- Scope: provision service/database; deploy exact Git revision; install/build; migrations; collect static; media strategy; health/startup verification; production logging sufficient for failures; no public demo claim yet.
- Excludes: untracked manual hot patches, SQLite, real user data imports, feature changes.
- Acceptance: application starts under production settings; DB is PostgreSQL; migrations current; static/media intentional; health/startup succeeds; no secrets exposed.
- Verify: platform status/logs; migration state; HTTPS/host/CSRF basics; health check; deployed revision identity.
- Owner test: ADVISORY unless platform access requires owner action.
- Code status target: PASS if repository changes required; otherwise N/A with deployment evidence.
- Git status target: PASS for repository changes; otherwise deployed revision must already be Git PASS.
- Next: P13.3.
- Commit intent: `chore: prepare hosted django demo` only when tracked repository changes exist.

### P13.3 Demo Seed, Hosted Smoke Test, and Owner Acceptance

- Objective: prove the hosted authenticated synthetic demo is usable by an external portfolio reviewer.
- Scope: seed demo User/Business/catalog/media; verify login, Workspace, search/filter/pagination, `+/-`/Direct Set, readiness, Ready Reply/copy, Dashboard, Add Similar, archive/restore, media/placeholder, reset/reseed, mobile behavior; only after success add README demo URL/access instructions.
- Excludes: real/private data, commercial SLA/scale claims, public buyer storefront, auto-send/chatbot.
- Acceptance: live demo reachable; authenticated demo access works; PostgreSQL-backed mutations persist correctly; reset/reseed restores baseline; no sensitive data exposed; desktop/mobile smoke passes; README demo claim matches verified reality.
- Verify: hosted smoke matrix; transition sanity; reset/reseed; HTTPS/security basics; exact deployed revision; README link check after proof.
- Owner test: REQUIRED — use live demo as external reviewer on desktop and phone/~390px; reply `TEST PASS` only after the short full demo path succeeds.
- Code status target: PASS for final tracked docs/config change after verified reality.
- Git status target: PASS for any release containing demo URL/docs/config.
- Phase 13 closure / Gate 6: Gate 6 passes only after hosted smoke, owner TEST PASS, known deployed revision, and repository truth alignment.
- Next: Phase 14.
- Commit intent: `docs: publish verified demo access` only after live proof.

---

# 15. Phase 14 — Public Portfolio Release

## Goal

Freeze a truthful portfolio state demonstrating product reasoning, systems engineering, full-stack implementation, verification, deployment, documentation discipline, and honest history without inventing commercial maturity.

### P14.1 Final Integrity, Scope, Security, and Drift Audit

- Objective: prove Bible, Build Plan, Development Notes, code/tests, CI, Git, deployed demo, and README tell one truthful story.
- Scope: /non-goal audit; Business isolation; source-of-truth invariants; lifecycle/availability/readiness/publication separation; ProductChoice duplicates; inventory mutation/ledger/concurrency; migrations; tests/CI; deployment; synthetic demo safety; secrets/private-data scan; stale/historical-doc authority scan; Git history sanity; current manual smoke evidence.
- Excludes: feature implementation; discovered defect requires separate RECOVERY slice.
- Acceptance: no release-blocking drift/security/integrity issue; no deferred scope accidentally presented as ; no false public claim.
- Verify: full regression/CI evidence; repository scan; Bible-to-code/test coverage review; deployed smoke recheck where needed.
- Owner test: ADVISORY unless a visual/public-claim issue requires owner judgment.
- Code status target: PASS.
- Git status target: PASS for any audit-driven tracked fix; otherwise reuse existing release evidence.
- Next: P14.2.
- Commit intent: `chore: complete portfolio integrity audit` only if a real tracked change exists.

### P14.2 Public README and Portfolio Presentation

- Objective: present verified project reality concisely to a potential employer.
- Scope: canonical product statement; portfolio objective; concise architecture; setup/test commands; verified CI; live demo link/access; current screenshots only; scope/non-goals; high-value engineering story; deployment/demo instructions; no duplication of the full Bible or internal prompt workflow.
- Excludes: fabricated pilot/adoption/retention/willingness-to-pay metrics; historical hypotheses presented as results; obsolete screenshots; unverified feature claims.
- Acceptance: GitHub landing experience is concise/current/externally understandable; demo/screenshots match current app; links/setup commands work; no secret/private workflow artifact is exposed.
- Verify: factuality/link/setup review against deployed app and repository.
- Owner test: REQUIRED — review GitHub landing page and live demo as a hiring reviewer; reply `TEST PASS`.
- Code status target: PASS.
- Git status target: PASS.
- Next: P14.3.
- Commit intent: `docs: finalize portfolio presentation`.

### P14.3 Owner Public Release Closure

- Objective: close Portfolio  with explicit owner approval and no hidden pending gate.
- Scope: verify clean/aligned `main`, required CI success, live demo health, final README accuracy, no unresolved  blocker/recovery; optional tag/release only if it adds real portfolio value.
- Excludes: new scope; cosmetic Git-history rewriting; unnecessary release ceremony.
- Acceptance: owner returns `TEST PASS / RELEASE APPROVED`; Gate 7 passes; Development Notes points to no unresolved required  action.
- Verify: Git/remote/CI; live smoke; final repository hygiene.
- Owner test: REQUIRED — `TEST PASS / RELEASE APPROVED`.
- Code status target: PASS or N/A if no tracked change is necessary.
- Git status target: PASS and clean/aligned public `main`.
- Phase 14 closure / Gate 7: Portfolio  complete.
- Next: none. Future product work requires a new owner-approved Bible/plan version.
- Commit intent: none unless a real final tracked change exists.

---

# 16. Release-Blocking Regression Matrix

The exact test implementation may evolve, but these outcomes remain mandatory before Portfolio  closes.

| Scenario | Required result | Planned/implemented gate |
|---|---|---|
| Cross-Business Product view/edit | 404/forbidden; no leak | historical + all phases |
| Cross-Business stock mutation | no write/leak | historical Phase 5 + P10.1 |
| Valid Product bundle | atomic complete persistence | historical Phase 4 + P7 |
| Invalid Product bundle | no partial sellable state | historical Phase 4 + P7 |
| Draft without choices | allowed | historical |
| Active without valid active choice | rejected | historical |
| Duplicate visible size/color rows | distinct identities allowed | historical + P7/P9/P10 |
| Candidate repeated transfer/retry | no accidental duplicate side effect | P7.3 |
| Missing price | operational but not price-answer-ready; no invented price | P7/P9 |
| Price zero/negative | rejected | P7.1 |
| Material negation | no positive material fact | historical + P7/P9 |
| Qty `1 -> 0` | exact adjustment + sold-out transition | historical + all stock consumers |
| Qty `0 -> 1` | exact adjustment + restock | historical + all stock consumers |
| Concurrent mutation | no lost update | historical + P10.1 |
| Direct Set | exact row, same service/ledger, no false no-op fact | P10.1 |
| Partial sold-out | centralized computed signal | P7.5/P8 |
| Add Similar | new Draft, qty zero, no ledger/media copy by default | P10.2 |
| Archive | exits normal daily/sellable behavior; history preserved | P10.3 |
| Restore | returns Draft, never silent Active | P10.3 |
| Unconfirmed Candidate | never satisfies readiness/reply truth | historical + P7/P9 |
| Ready Reply sold-out | no current-availability claim | P9 |
| Duplicate-choice reply ambiguity | no fabricated distinction/aggregation | P9.1 |
| Internal return | canonical context preserved | historical + all UI phases |
| Unsafe external return | rejected to safe fallback | historical + all UI phases |
| HTMX failure | visible recovery; DB truth authoritative | historical + P11 |
| Clipboard failure | visible fallback; no false copied state | P9/P11 |
| Large catalog | bounded pagination/loading; state preserved | P11.1 |
| Demo reset/reseed | only scoped synthetic data; protected identity safe | P12/P13 |
| Production runtime | Django + PostgreSQL + safe settings | P12/P13 |

---

# 17. Documentation and Token-Economy Contract

## Canonical files for routine development

- `docs/PROJECT_BIBLE.md` — frozen durable truth.
- `docs/BUILD_PLAN.md` — frozen-by-default execution map.
- `docs/DEVELOPMENT_NOTES.md` — live append-only operational anchor.
- `README.md` — public presentation only, read/write only when public reality changes.

Archived/superseded planning/discovery docs are not routine Codex context.

## Development Notes usage

Routine workflow may append concise entries for:

- P3 implementation outcome/short write summary when the workflow requires it;
- P4 audit/hardening, tests, docs coherence, owner-test gate/result;
- P5 commit/push/CI closure;
- `BLOCKER`, `RECOVERY`, `PLAN_SPLIT`, `PLAN_AMENDMENT`, `DECISION`.

Do not rewrite old entries merely to change status. The latest relevant entries plus Git truth form the operational handoff.

## README usage

Update only for material verified public reality: setup, capabilities, CI, screenshots, demo link, deployment/access instructions. It is never implementation authority or a work log.

---

# 18. Bible-to-Plan Coverage Matrix

This matrix exists to prevent silent loss when the plan is optimized later.

| Bible concern | Execution coverage |
|---|---|
| Canonical authority / anti-scope-creep | Sections 1-4, 17 |
| Product/portfolio objective | global guardrails + P12-P14 |
| deferred product layers/publication separation | Section 4 + P14 audit |
| Primary user / one active Business | historical Phase 2 + all Business-isolation gates |
| Workspace primary / Dashboard secondary / no Detail | historical Phase 6 + P8/P9/P11 |
| Return paths / mobile / accessibility | historical Phase 6 + P11 + all REQUIRED owner tests |
| Description primary capture surface | historical Phase 4 + P7.3 |
| Observed/Candidate/Confirmed | historical Phase 4 + P7.3/P7.4/P9 |
| Recognition trust/confirmation/duplicate-operation safety | historical Phase 4 + P7.3 |
| Business Type/Tag vocabulary + aliases / no global taxonomy | historical Phase 4 + P7.3/P11 |
| Material typed fact / negation / no invented composition | historical Phase 4 + P7/P9 regression |
| Size/Color choice truth / Free size no fit guarantee | historical Phase 4 + global guardrails |
| Measurements/fit/AI sizing deferred | global exclusions + P14 audit |
| Price semantics | P7.1 + P7.4/P7.5/P9 |
| Lifecycle Draft/Active/Archived / Restore Draft | historical + P10.3 |
| Central availability / partial sold-out / low-stock | historical Phase 5/6 + P7.5/P8.1 |
| Duplicate ProductChoice identity | historical + P7/P9/P10 regressions |
| Product bundle atomicity | historical Phase 4 + P7 media/price/refinement |
| Optional Product media + placeholder/security | P7.2 + P12/P13 |
| Inventory +/-/set single boundary/concurrency/ledger | historical Phase 5 + P10.1 |
| HTMX server truth / stale-state prevention | historical Phase 6 + P7/P10/P11 |
| Search/filter scalability/pagination | historical Phase 6 + P11.1 |
| Readiness = buyer-question coverage | P7.4-P7.5 + P8/P9 |
| Ready Reply reward/truth/copy recovery | P9 + P11 |
| Add Similar | P10.2 |
| Archive/Restore | P10.3 |
| Modular monolith/services | historical architecture + all future slices |
| Business isolation/auth | historical Phase 2 + release-blocking tests |
| Repository/runtime/upload security | P7.2 + P12.2 + P14.1 |
| Failure/recovery/accessibility/performance | all slice acceptance + P11 + P14 |
| Testing/regression/CI | Sections 3, 5, 16 + every Verify field |
| Synthetic demo/reset | P12.1 + P13.3 |
| Real Django/PostgreSQL deployment | P12.2 + P13 |
| Honest Git/GitHub portfolio history | global guardrails + P14 |
| AI/documentation minimal context | Sections 2-3, 17 |
| Historical hypotheses not claims | P14.2 |
| Final Portfolio DoD | Gates 4-7 + P14.3 |

---

# 19. Final Portfolio  Definition of Done

Portfolio  is complete only when all applicable statements are true:

## Product

- authenticated seller operates one active Business workspace;
- Description-first Product creation/correction works without mandatory ecommerce-form burden;
- price semantics are enforced;
- Type/Tag vocabulary/aliases and confirmed material work without collapsing Candidate into Fact;
- size/color ProductChoice truth and intentional duplicate identities work;
- optional Product media/placeholder works safely;
- Draft/Active/Archived lifecycle is correct; Restore -> Draft;
- stock `+/-` and Direct Set are exact-row, atomic, concurrency-safe, audited, and use one service;
- centralized availability/partial sold-out/low-stock signals are coherent;
- scalable Workspace supports search/filter/pagination and remains primary;
- buyer-question coverage identifies answerable/missing truth without percentages;
- Dashboard is action-first and secondary;
- Ready Reply is on-demand, deterministic, truth-safe, copyable, and recoverable;
- Add Similar resets stock and never copies ledger/media by default;
- archive/restore preserves history without silent sellability.

## Integrity and security

- Business isolation regression matrix passes;
- Product bundle atomicity holds;
- no alternate mutable stock-write path exists;
- no lost-update or false ledger path remains;
- candidates never silently become buyer claims;
- safe return/CSRF/method/upload/security contracts hold;
- no secrets/private source data/artifacts are tracked.

## UX

- Product Workspace is the clear primary work surface;
- Dashboard is secondary;
- no Product Detail dependency;
- seller does not rely on browser Back;
- cards remain compact and actions prioritized;
- mobile ~390px flow has no major overflow/density/tap-target defect;
- Georgian-facing terminology is consistent and non-ERP;
- keyboard/focus/status/error/loading/recovery baseline is verified;
- HTMX/clipboard failure paths are visible and recoverable.

## Portfolio engineering

- setup is reproducible;
- PostgreSQL parity is maintained;
- migrations are current;
- critical regression suite passes in CI;
- synthetic demo data is safe/resettable;
- production settings/assets/static/media strategy is deployable;
- backend-capable hosted Django/PostgreSQL demo is live and smoke-tested;
- README reflects only verified current reality;
- screenshots/demo links are current;
- Git history is honest, chronological, focused, and unre-written;
- Bible/Build Plan/Development Notes/code/tests/README do not materially drift;
- owner returns final `TEST PASS / RELEASE APPROVED`.

Deferred boundaries remain deferred. Portfolio  is a controlled proof, not a complete commercial ERP/ecommerce platform.
