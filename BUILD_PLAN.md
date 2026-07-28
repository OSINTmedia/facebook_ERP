# Build Plan

## Document Metadata

- Status: SEMI_FROZEN
- Version: 1.0
- Owner: osMit
- Source documents: `APP_EXPERIENCE_PLAN.md`, `DEVELOPMENT_NOTES.md`, `docs/Portfolio_MVP_V1.md`, `docs/Technical_Planning_v1.md`, `docs/domain/CLOTHING_DATA_SPEC_V1.md`, `docs/User_Journey_Freeze_v1.md`, `docs/discovery/backend.md`, `docs/discovery/frontend.md`, `docs/discovery/DISCOVERY_REPORT.md`
- Update rule: update only after an approved planning, implementation, verification, or checkpoint task
- Roadmap authority: this file controls implementation order; frozen product documents control scope
- Codex may reorder phases automatically: no

## 1. Implementation Objective

Build a clean Social Commerce Seller Operations Assistant from zero in `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`. The source prototype in `/home/giga/Desktop/OSINT/facebook_MVP/` remains read-only discovery evidence and behavior reference, not source code to copy wholesale.

The rebuild must proceed through small, reviewable micro-slices with explicit acceptance criteria, automated verification where possible, manual owner verification where needed, documentation sync, and honest Git history.

## 2. Portfolio Delivery Objective

The portfolio deliverable must show:

- public GitHub repository with real chronological history;
- documentation-first product and architecture reasoning;
- meaningful commits with one clear intention each;
- reproducible setup;
- automated tests and CI;
- owner-approved scope control;
- safe synthetic demo data;
- online Django demo after deployment approval;
- README that accurately reflects the current project state.

## 3. Documentation Hierarchy

Use this exact context-transfer order:

1. `changelog_checkpoint.md`
   - Controls the current state, active phase, active micro-slice, blockers, last verification, and handoff instruction.
2. `BUILD_PLAN.md`
   - Controls implementation sequence, stop gates, micro-slice scope, verification expectations, and commit intent.
3. `APP_EXPERIENCE_PLAN.md`
   - Controls UX contracts, page responsibilities, navigation and return-path rules, mobile constraints, and interaction boundaries.
4. `DEVELOPMENT_NOTES.md`
   - Records meaningful decisions, rejected alternatives, trade-offs, bugs, workarounds, and engineering lessons. It is not a daily changelog.
5. `docs/Portfolio_MVP_V1.md`
   - Controls product scope, portfolio purpose, completion criteria, source-of-truth rules, and deferred scope.
6. `docs/Technical_Planning_v1.md`
   - Controls architecture direction, data boundaries, service boundaries, integrity rules, testing strategy, security, and deployment constraints.
7. `docs/domain/CLOTHING_DATA_SPEC_V1.md`
   - Controls description-first semantic recognition, observed/candidate/confirmed fact boundaries, type/tag recognition, material facts, size/color choice truth, and deferred measurement boundaries.
8. `docs/User_Journey_Freeze_v1.md`
   - Controls required seller journeys, return paths, acceptance criteria, and journey exclusions.
9. Relevant source files
   - Read only after the current micro-slice is approved or when implementation exists.
10. `README.md` only for public presentation context
   - Public-facing summary only. It is not implementation authority and not a work log.

Private local workflow prompts, including `codex_prompt_ERP.txt`, may be used by the owner to run the micro-slice workflow, but they are not public repository authority and must not be staged or committed.

## 4. Status Vocabulary

Use only these status values:

- NOT_STARTED
- IN_PROGRESS
- BLOCKED
- NEEDS_OWNER_REVIEW
- PASSED
- FAILED
- DEFERRED

## 5. Global Scope Guardrails

- Build from zero inside the rebuild workspace.
- Do not copy source code, migrations, media, database dumps, or private configuration from the prototype.
- Keep V1 seller-side and source-of-truth focused.
- Do not add public catalog, chatbot, LLM truth, orders, reservations, payments, delivery, accounting, supplier management, broad ERP, DRF/API-first architecture, or microservices unless owner-approved in a later phase.
- Treat stock, price, lifecycle, size, color, readiness, and availability as deterministic database-backed truth.
- Treat product description as the primary seller input, not as automatically trusted structured truth.
- Separate recognized text into observed text, candidate meaning, and confirmed structured fact.
- Keep Product Type and Tag recognition in scope, with business-scoped vocabulary aliases.
- Treat material as a small typed semantic fact when confirmed, not as a large mandatory form section.
- Keep size and color as choice/variant truth; description-recognized size/color may only suggest adding a choice.
- Express readiness as buyer-question coverage, not as a completion percentage.
- Keep detailed garment measurements as a separate approved micro-slice; do not add a universal fashion ontology or one giant product form.
- Do not use an LLM as the source of price, stock, availability, size, color, lifecycle, or ownership truth.
- Do not start a new phase while the current phase is `IN_PROGRESS`, `BLOCKED`, `NEEDS_OWNER_REVIEW`, or `FAILED`.
- No commit is allowed while `changelog_checkpoint.md` is stale.
- Frozen product documents are not modified automatically.
- Every UI screen receives an early UX audit before large feature accumulation.
- Deployment is a separate phase. Local success is not online demo readiness.

## 6. Git and Commit Discipline

- Git history must be honest and chronological.
- Do not fabricate older commits, backdate commits, or create synthetic history.
- The GitHub repository already exists at `https://github.com/OSINTmedia/facebook_ERP`.
- The remote repository is public, uses default branch `main`, and contains the preserved initial README commit `dce852b`.
- Local Git is initialized.
- Local branch `main` tracks `origin/main`.
- Local remote is `ssh://git@ssh.github.com:443/OSINTmedia/facebook_ERP.git`.
- GitHub SSH authentication works through `ssh.github.com` on port `443`.
- The first substantive rebuild-planning commit is `549db75 docs: add portfolio rebuild planning baseline`.
- Existing remote history must be preserved.
- Force push is prohibited.
- Do not inflate history with empty or meaningless commits.
- Use one clear intention per commit.
- Commit only after source changes and documentation state are synchronized.
- Before commit, record source changes, verification performed, known gaps, and checkpoint update.
- Push only after owner approval for that checkpoint.
- Commit messages should describe the delivered slice, for example `docs: add planning baseline` or `feat: add business-owned product model`.

## 7. Standard Micro-Slice Workflow

1. Context load
   - Read `changelog_checkpoint.md` first, then this plan and controlling documents.
2. Next-step report
   - State the active micro-slice, allowed changes, exclusions, and expected verification.
3. Owner approval
   - Do not implement until the owner explicitly approves the micro-slice.
4. Implementation
   - Make only the scoped changes.
5. Automated verification
   - Run the tests/checks defined for the slice.
6. Manual owner test
   - Provide exact steps for owner verification when UI or workflow behavior changed.
7. Integrity audit
   - Review scope, ownership, state boundaries, security, UX, and regression risks.
8. Documentation sync
   - Update checkpoint and any non-frozen planning documents required by the change.
9. Git checkpoint
   - Show changed files and verification summary.
10. Commit/push
   - Commit and push only after approval.
11. Checkpoint update
   - Record last commit, current status, next micro-slice, blockers, and verification.

## 8. Mandatory Stop Gates

- Gate 0: documents owner-reviewed.
- Gate 1: repository and CI foundation passed.
- Gate 2: data ownership and business isolation passed.
- Gate 3: first vertical slice passed.
- Gate 4: UX/navigation passed.
- Gate 5: portfolio hardening passed.
- Gate 6: deployment/demo passed.
- Gate 7: public release approved.

## 9. Phase Overview

| Phase | Name | Goal | Status | Stop Gate | Portfolio Evidence |
|---|---|---|---|---|---|
| Phase 0 | Documentation Approval and Repository Foundation | Freeze planning docs and establish honest repository baseline | PASSED | Gate 0 | Frozen docs, honest history, corrective checkpoint before Phase 1 |
| Phase 1 | Django/PostgreSQL Foundation and CI | Create minimal clean Django project, settings, test harness, and CI | NOT_STARTED | Gate 1 | Scaffold commits, CI workflow, reproducible setup |
| Phase 2 | User and Business Ownership | Implement authentication and business ownership boundary | NOT_STARTED | Gate 2 | User/business tests, access-control tests |
| Phase 3 | Catalog Core | Implement product core facts and lifecycle | NOT_STARTED | Gate 3 | Product model/forms/views/tests |
| Phase 4 | Semantic Recognition and Choice Model | Implement description-first recognition for type/tag/material candidates plus stock-bearing choices | NOT_STARTED | Gate 3 | Recognition contract, alias tests, choice validation |
| Phase 5 | Inventory and Computed Availability | Centralize stock mutations and computed availability | NOT_STARTED | Gate 3 | Inventory service tests and ledger tests |
| Phase 6 | Operational Product Workspace | Build seller product workspace with compact product cards | NOT_STARTED | Gate 4 | Workspace UI, HTMX stock checks, UX audit notes |
| Phase 7 | Dashboard and Attention Signals | Build daily attention surface from shared domain truth | NOT_STARTED | Gate 4 | Dashboard signal tests and manual workflow proof |
| Phase 8 | Deterministic Buyer Replies | Generate seller-side ready replies from verified facts | NOT_STARTED | Gate 4 | Reply service tests and copy workflow |
| Phase 9 | UX Stabilization and Regression Audit | Fix navigation, density, mobile, accessibility, and stale-state risks | NOT_STARTED | Gate 4 | UX checklist, route-return matrix, browser notes |
| Phase 10 | Portfolio Hardening | Strengthen setup docs, demo data, security hygiene, and README | NOT_STARTED | Gate 5 | Public-ready docs, synthetic data, no secrets |
| Phase 11 | Deployment and Online Demo | Deploy backend-capable demo after provider decision | NOT_STARTED | Gate 6 | Live URL, smoke test, reset/reseed policy |
| Phase 12 | Public Release | Final owner review and publishable portfolio state | NOT_STARTED | Gate 7 | Release checklist, final README, tagged state if approved |

## 10. Phase 0 Micro-Slices

### P0.1 Owner Review and Document Freeze

- Objective: review and approve or revise `docs/Portfolio_MVP_V1.md`, `docs/Technical_Planning_v1.md`, `docs/domain/CLOTHING_DATA_SPEC_V1.md`, `docs/User_Journey_Freeze_v1.md`, `APP_EXPERIENCE_PLAN.md`, `DEVELOPMENT_NOTES.md`, this plan, README, and checkpoint.
- Dependency: Phase 1A to 1E documents exist.
- Exact scope: owner reads draft documents, freezes the owner-controlled scope/technical/domain/journey documents, keeps operational documents live or semi-frozen, and leaves future `OWNER_DECISION_REQUIRED` items explicit instead of silently approving them.
- Explicit exclusions: no Django initialization, no Git initialization, no code, no package install, no source prototype modification.
- Likely files: planning Markdown files only.
- Backend acceptance criteria: backend invariants are approved or marked deferred.
- Frontend/UX acceptance criteria: page responsibilities, first viewport priorities, return-path rules, and V1 surfaces are approved or marked deferred.
- Automated verification: document existence and cross-document consistency check.
- Manual user verification: owner confirms scope decisions and freeze status.
- Failure cases: unresolved decision blocks the next technical slice; document contradiction; owner rejects proposed V1.
- Documentation updates: update status lines and `changelog_checkpoint.md`.
- Proposed commit message: `docs: freeze portfolio planning baseline`.
- Rollback/recovery note: if owner rejects scope, keep drafts and update blocker list rather than implementing.
- Stop gate: Gate 0.
- Current verified state: owner approved freezing the docs/ scope, technical, clothing-domain, and journey documents; operational status and phase state remain controlled by `changelog_checkpoint.md` and `DEVELOPMENT_NOTES.md`.
- Status: PASSED.

### P0.2 GitHub Authentication and Safe Local/Remote Repository Reconciliation

- Objective: confirm GitHub authentication and safely connect the local documentation workspace to the existing public remote without overwriting local docs or remote history.
- Dependency: owner approval for repository reconciliation.
- Exact scope: confirm authenticated identity, preserve local docs, initialize local Git if needed, connect to the existing remote, fetch `origin/main`, adopt the existing remote `main` history, preserve the remote initial README commit, and intentionally keep the local planning README before the baseline commit.
- Current verified state: local Git is initialized; `main` tracks `origin/main`; remote is `ssh://git@ssh.github.com:443/OSINTmedia/facebook_ERP.git`; GitHub SSH authentication works through `ssh.github.com` on port `443`; existing remote commit `dce852b Initial commit` is preserved.
- Explicit exclusions: no force push, no app code, no dependency install, no source copy, no silent README replacement, no remote history deletion.
- Likely files: Git metadata only plus checkpoint updates after verification.
- Backend acceptance criteria: none.
- Frontend/UX acceptance criteria: none.
- Automated verification: GitHub auth identity is known, remote URL is exact, `origin/main` is fetched, histories are reconciled without unrelated duplicate history, and local docs remain intact.
- Manual user verification: owner confirms authenticated account, remote URL, branch, and preservation of remote initial commit.
- Failure cases: GitHub authentication unknown, wrong account, remote mismatch, local README overwritten, unrelated history, force-push attempt.
- Documentation updates: update `changelog_checkpoint.md` Git Checkpoint.
- Proposed commit message: none for initialization alone unless combined with approved baseline files.
- Rollback/recovery note: stop and restore from the temporary backup if local docs are disturbed.
- Stop gate: local repository is safely based on existing remote `main` and ready for docs-only staging.
- Status: PASSED.

### P0.3 Repository Hygiene Baseline

- Objective: create safe repository hygiene before any code is committed.
- Dependency: P0.2 `PASSED`.
- Exact scope: add `.gitignore`, `.env.example`, and minimal repository policy notes as approved.
- Explicit exclusions: no secrets, no real media, no database dumps, no prototype files, no source implementation.
- Likely files: `.gitignore`, optional `.env.example`, optional docs updates.
- Backend acceptance criteria: `.env.example` uses placeholders only and does not expose credentials.
- Frontend/UX acceptance criteria: none.
- Automated verification: inspect ignored patterns for `.env`, virtualenvs, database dumps, media uploads, static build output, backups, cache files.
- Manual user verification: owner confirms no private data paths are included.
- Failure cases: accidental real secret, media, backup, or source prototype reference.
- Documentation updates: `changelog_checkpoint.md`.
- Proposed commit message: `chore: add repository hygiene baseline`.
- Rollback/recovery note: remove unsafe files before staging.
- Stop gate: no sensitive files visible in `git status`.
- Status: PASSED.

### P0.4 Documentation-Only Baseline Commit

- Objective: commit the approved planning baseline as the first substantive rebuild commit on top of the preserved remote initial README commit.
- Dependency: P0.3 `PASSED` and owner approval before commit.
- Exact scope: stage approved planning docs, public README, checkpoint, hygiene files.
- Explicit exclusions: no application code, no generated files, no old prototype files.
- Likely files: `README.md`, `BUILD_PLAN.md`, `changelog_checkpoint.md`, approved planning docs, `.gitignore`, `.env.example`.
- Backend acceptance criteria: none.
- Frontend/UX acceptance criteria: none.
- Automated verification: `git diff --cached --stat` and content scan for fake demo/CI/test claims.
- Manual user verification: owner approves the first commit contents.
- Failure cases: stale checkpoint; README overclaims; unapproved draft marked frozen.
- Documentation updates: record commit hash after commit.
- Current verified state: baseline committed as `549db75 docs: add portfolio rebuild planning baseline`.
- Proposed commit message: `docs: add portfolio rebuild planning baseline`.
- Rollback/recovery note: unstage unsafe files and fix docs before commit.
- Stop gate: first substantive rebuild documentation commit exists without rewriting remote history.
- Status: PASSED.

### P0.5 Minimal Public README Publication

- Objective: make README accurate for the planning stage and future GitHub visitors.
- Dependency: P0.4 `PASSED`.
- Exact scope: ensure README explains status, scope, docs, non-goals, workflow, and history note.
- Explicit exclusions: no setup commands before verified foundation, no demo URL, no CI badge before CI exists.
- Likely files: `README.md`, `changelog_checkpoint.md`.
- Backend acceptance criteria: README does not imply backend exists before implementation.
- Frontend/UX acceptance criteria: README does not imply screenshots or demo exist before verification.
- Automated verification: text scan for forbidden claims.
- Manual user verification: owner approves public wording.
- Failure cases: misleading project name, false demo status, fake adoption or metrics.
- Documentation updates: checkpoint last operation.
- Proposed commit message: `docs: refine public portfolio readme`.
- Rollback/recovery note: revert only the README wording from this slice if owner rejects it.
- Stop gate: README factuality check passed.
- Status: PASSED.

### P0.6 First Approved Push

- Objective: push the approved documentation baseline to the existing GitHub repository after local/remote reconciliation and owner approval.
- Dependency: P0.4 `PASSED`.
- Exact scope: push the local branch to `origin/main` preserving the existing remote history.
- Explicit exclusions: no force push, no fake history, no source prototype import, no unapproved branch or repository creation.
- Likely files: none locally unless checkpoint is updated after push.
- Backend acceptance criteria: none.
- Frontend/UX acceptance criteria: none.
- Automated verification: remote URL, branch, commit graph, and pushed file list.
- Manual user verification: owner confirms pushed repository content.
- Failure cases: wrong remote, force push attempt, private/public visibility mismatch, accidental push.
- Documentation updates: checkpoint Git Checkpoint.
- Proposed commit message: none.
- Rollback/recovery note: stop before push if remote mismatch is found.
- Stop gate: remote configured and approved.
- Current verified state: baseline commit `549db75` was pushed normally to `origin/main`; preserved `dce852b Initial commit`; no force push was used.
- Status: PASSED.

### P0.7 Issue and Milestone Setup

- Objective: create optional GitHub issues/milestones matching the approved phases.
- Dependency: P0.6 `PASSED`.
- Exact scope: create milestone/issue structure only if owner wants issue-based workflow.
- Explicit exclusions: no implementation, no issue spam, no unapproved late-scope items.
- Likely files: none locally unless issue templates are approved.
- Backend acceptance criteria: backend issue labels match frozen phase order.
- Frontend/UX acceptance criteria: UX review gates are visible in issue/milestone plan.
- Automated verification: none unless GitHub CLI/API is approved.
- Manual user verification: owner approves issue structure.
- Failure cases: over-detailed issues before implementation evidence exists.
- Documentation updates: checkpoint.
- Proposed commit message: `docs: add issue workflow templates` only if local templates are created.
- Rollback/recovery note: close or rename issues if scope changes before implementation.
- Stop gate: issue workflow accepted or explicitly deferred.
- Status: DEFERRED.

### P0.8 Documentation Governance Corrective Sync Before Phase 1

- Objective: align document authority, checkpoint reality, private workflow prompt handling, and measurement scope before technical implementation begins.
- Dependency: P0.1 through P0.6 `PASSED`; P0.7 explicitly `DEFERRED`.
- Exact scope: mark owner-controlled docs frozen, mark this plan and the app experience plan semi-frozen, keep `changelog_checkpoint.md` and `DEVELOPMENT_NOTES.md` live, ignore private local workflow prompts, update Git reality, and keep detailed garment measurement implementation deferred.
- Explicit exclusions: no Django initialization, no dependency install, no app code, no CI, no migrations, no source prototype changes, no commit or push during the sync itself.
- Likely files: `.gitignore`, `README.md`, `BUILD_PLAN.md`, `APP_EXPERIENCE_PLAN.md`, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md`, selected owner-controlled docs for status and approved measurement-boundary correction.
- Backend acceptance criteria: no backend code exists or changes.
- Frontend/UX acceptance criteria: the assistant-first, two-primary-surface UX contract remains intact.
- Automated verification: `git status --short --branch`, `git diff --stat`, `git diff --check`, link/path scan, and stale-state grep.
- Manual user verification: owner confirms this corrective sync before Git checkpoint.
- Failure cases: private prompt staged; checkpoint remains stale; measurement implementation appears as V1 scope; frozen docs gain unapproved scope.
- Documentation updates: record this sync and next Git checkpoint in `changelog_checkpoint.md`.
- Proposed commit message: `docs: sync governance before phase 1`.
- Rollback/recovery note: revert only this corrective documentation sync if owner rejects it.
- Current verified state: corrective sync committed and pushed as `accc24b docs: sync governance before phase 1`; Phase 1 readiness checkpoint committed and pushed as `0c04cbd docs: mark phase 1 ready`.
- Stop gate: corrective sync reviewed, committed, pushed, and checkpoint aligned before P1.1 starts.
- Status: PASSED.

## 11. Phase 1 Micro-Slices

### P1.1 Python and Django Dependency Baseline

- Objective: define the clean rebuild dependency baseline.
- Dependency: Phase 0 `PASSED`.
- Exact scope: choose Python/Django/PostgreSQL dependency versions, add dependency file, and document install path.
- Explicit exclusions: no models, no product routes, no source prototype copy.
- Likely files: dependency file, `.env.example`, `README.md`, `changelog_checkpoint.md`.
- Backend acceptance criteria: dependencies support Django, PostgreSQL, env loading, tests, and later HTMX templates.
- Frontend/UX acceptance criteria: frontend dependencies are not yet introduced unless shell work starts.
- Automated verification: dependency install in clean environment if owner approves environment setup.
- Manual user verification: owner confirms stack direction.
- Failure cases: unsupported Python/Django version, unpinned critical dependencies, hidden local dependency.
- Documentation updates: README setup placeholder becomes verified setup only after install works.
- Proposed commit message: `chore: define python and django dependency baseline`.
- Rollback/recovery note: revise dependency file before scaffold if compatibility fails.
- Stop gate: dependency baseline verified.
- Status: NOT_STARTED.

#### Deployment Compatibility Guardrail

Every dependency must be compatible with the planned hosted
Django/PostgreSQL demo environment.

Avoid libraries that depend on:

- desktop-only UI;
- local-only services without a hosted equivalent;
- operating-system-specific binaries without a documented deployment path;
- hardcoded local filesystem paths;
- unavailable proprietary services.

### P1.2 Clean Django Project Scaffold

- Objective: create a minimal Django project without product features.
- Dependency: P1.1 `PASSED`.
- Exact scope: create project package, `manage.py`, settings package, root URLs, WSGI/ASGI entry points.
- Explicit exclusions: no old app copy, no product models, no UI beyond default minimal response if needed.
- Likely files: `manage.py`, project settings package, root URL files.
- Backend acceptance criteria: Django system check can run.
- Frontend/UX acceptance criteria: no seller UI claims yet.
- Automated verification: `python manage.py check`.
- Manual user verification: owner sees project scaffold status and file map.
- Failure cases: wrong settings module, accidental source path references, missing env handling.
- Documentation updates: checkpoint and README setup if verified.
- Proposed commit message: `chore: scaffold clean django project`.
- Rollback/recovery note: remove only scaffold files from this slice if created in wrong path.
- Stop gate: system check passes.
- Status: NOT_STARTED.

### P1.3 Settings and Environment Structure

- Objective: separate local/test/production-safe settings early.
- Dependency: P1.2 `PASSED`.
- Exact scope: configure env loading, secret requirements, allowed hosts, database URL, static/media paths, and debug defaults.
- Explicit exclusions: no production provider selection, no real secrets, no deployment.
- Likely files: settings modules, `.env.example`, `.gitignore`, tests/checks if applicable.
- Backend acceptance criteria: missing required production secrets fail safely; local settings use placeholders only.
- Frontend/UX acceptance criteria: static path is ready for later assets.
- Automated verification: Django system check, env example review.
- Manual user verification: owner confirms no secrets are present.
- Failure cases: insecure fallback secret in production path, accidental `.env` commit, hardcoded local credentials.
- Documentation updates: README setup and checkpoint.
- Proposed commit message: `chore: configure environment-aware django settings`.
- Rollback/recovery note: stop before committing if any secret is found.
- Stop gate: repository hygiene and settings check passed.
- Status: NOT_STARTED.

### P1.4 PostgreSQL and Test Database Baseline

- Objective: verify the rebuild runs against PostgreSQL-oriented settings.
- Dependency: P1.3 `PASSED`.
- Exact scope: configure database URL handling and test database expectations.
- Explicit exclusions: no migrations beyond default framework if not needed, no production database, no prototype database access.
- Likely files: settings, `.env.example`, README setup.
- Backend acceptance criteria: database configuration is explicit and portable.
- Frontend/UX acceptance criteria: none.
- Automated verification: `python manage.py check`; database-dependent verification only after owner-approved local DB setup.
- Manual user verification: owner confirms local PostgreSQL expectation.
- Failure cases: SQLite-only drift, hardcoded database credentials, unmanaged local assumptions.
- Documentation updates: README local setup after verified commands exist.
- Proposed commit message: `chore: document postgresql database baseline`.
- Rollback/recovery note: revise settings before adding models.
- Stop gate: database configuration approved.
- Status: NOT_STARTED.

### P1.5 Base Application Shell

- Objective: create the minimal authenticated layout shell before feature pages accumulate.
- Dependency: P1.3 `PASSED`.
- Exact scope: base template structure, message region, navigation placeholders, static CSS path.
- Explicit exclusions: no product workspace, dashboard metrics, inventory controls, or public catalog.
- Likely files: base template, static CSS, URL/view placeholder if needed.
- Backend acceptance criteria: route protection direction is documented.
- Frontend/UX acceptance criteria: active location pattern, semantic messages, mobile container, and no marketing landing page.
- Automated verification: template render smoke test if route exists.
- Manual user verification: owner reviews shell first viewport and nav anchors.
- Failure cases: nav labels imply broader ERP scope; no active-state pattern; inaccessible messages.
- Documentation updates: APP experience notes if owner changes shell contract, checkpoint.
- Proposed commit message: `feat: add minimal application shell`.
- Rollback/recovery note: keep shell small so it can be revised before feature pages.
- Stop gate: shell UX gate passed.
- Status: NOT_STARTED.

### P1.6 CI and Initial Test Harness

- Objective: establish automated verification before domain implementation.
- Dependency: P1.2 `PASSED`.
- Exact scope: add CI workflow, minimal smoke tests, Django system check in CI, migration consistency command once migrations exist.
- Explicit exclusions: no fake pass claims, no deployment, no broad lint stack unless approved.
- Likely files: CI workflow, test config, minimal tests, README status after passing.
- Backend acceptance criteria: CI runs dependency install, Django check, and tests.
- Frontend/UX acceptance criteria: no browser UI claims yet.
- Automated verification: local equivalent commands and first CI run after GitHub setup.
- Manual user verification: owner sees CI result before badge or README claim.
- Failure cases: CI depends on unavailable secrets; README claims CI before it runs.
- Documentation updates: README and checkpoint after verified CI.
- Proposed commit message: `ci: add django verification workflow`.
- Rollback/recovery note: fix or remove broken CI before next feature phase.
- Stop gate: Gate 1.
- Status: NOT_STARTED.

## 12. Remaining Phase Outlines

### Phase 2: User and Business Ownership

- Objective: implement custom auth direction and business ownership boundary.
- Dependency: Gate 1.
- Scope boundary: User, Business, login/logout, active business policy, access tests.
- Expected micro-slices: auth model, business model, login flow, owner-scoped query helper, cross-business access tests.
- Stop gate: every seller-owned object created later has a business boundary and test pattern.

### Phase 3: Catalog Core

- Objective: implement product facts and lifecycle without stock complexity first.
- Dependency: Phase 2.
- Scope boundary: product name/description, price policy after owner decision, lifecycle, business ownership, create/list/edit basics.
- Expected micro-slices: product model, product form, product list, product create/edit, lifecycle tests.
- Stop gate: seller can create and edit a business-owned product and cannot access another business's product.

### Phase 4: Semantic Recognition and Choice Model

- Objective: add the description-first assistant layer that recognizes existing Product Types, Tags, material aliases, and size/color candidates while preserving choice-level stock truth.
- Dependency: Phase 3.
- Scope boundary: `docs/domain/CLOTHING_DATA_SPEC_V1.md`, observed text, candidate meaning, confirmed structured facts, type/tag recognition, business-scoped aliases, material facts, choice rows, minimum valid choice rule, duplicate policy after owner decision, form/formset tests.
- Expected micro-slices: semantic-recognition service contract, Product Type recognition, Tag recognition, alias normalization, material fact confirmation, size/color-to-choice suggestions, choice model, formset/service validation, create/edit integration, mobile form audit.
- Separate deferred micro-slice: detailed garment measurements, only after type, value, unit, method, applicable product/choice boundary, category prompts, and buyer-reply wording are owner-approved.
- Stop gate: product bundle save cannot persist partial invalid choice state, and buyer replies consume confirmed facts only.

### Phase 5: Inventory and Computed Availability

- Objective: centralize quantity mutations and availability computation.
- Dependency: Phase 4.
- Scope boundary: inventory service, adjustment ledger, +1/-1 and owner-approved direct set, computed availability, concurrency strategy.
- Expected micro-slices: inventory models, service tests, stock route, HTMX response, transition tests.
- Stop gate: all stock changes go through one service and create a complete audit trail.

### Phase 6: Operational Product Workspace

- Objective: build the daily seller workspace for search, cards, and stock work.
- Dependency: Phase 5.
- Scope boundary: compact product cards, filters approved for V1, inline stock controls, explicit return context.
- Expected micro-slices: workspace route, card partial, HTMX card update, search/filter, UX density review.
- Stop gate: product workspace passes UX review gate and critical HTMX regression tests.

### Phase 7: Dashboard and Attention Signals

- Objective: expose what needs attention today using shared backend truth.
- Dependency: Phase 6.
- Scope boundary: dashboard action queue, low-stock/sold-out/readiness summaries, drilldowns with return paths.
- Expected micro-slices: dashboard service, route/template, attention tests, stale-state handling decision.
- Stop gate: dashboard first viewport and return-path matrix pass owner review.

### Phase 8: Deterministic Buyer Replies

- Objective: generate seller-side copyable replies from stored product facts.
- Dependency: Phase 5 and owner approval for reply placement.
- Scope boundary: deterministic modes, missing-data notes, sold-out wording, copy workflow.
- Expected micro-slices: reply service, reply UI surface, tests for truthfulness, UX placement audit.
- Stop gate: replies never invent price, stock, size, color, or availability.

### Phase 9: UX Stabilization and Regression Audit

- Objective: reduce density, fix route trust, mobile issues, accessibility gaps, and stale UI behavior.
- Dependency: Phase 6 to Phase 8.
- Scope boundary: stabilization only, no new product scope.
- Expected micro-slices: route-return audit, mobile viewport audit, accessibility pass, HTMX stale-state audit, terminology freeze update.
- Stop gate: Gate 4.

### Phase 10: Portfolio Hardening

- Objective: make the repository credible and reproducible for public review.
- Dependency: Gate 4.
- Scope boundary: README, setup, tests, synthetic seed, reset/reseed, security hygiene, screenshots only after verified if approved.
- Expected micro-slices: setup verification, demo seed command, reset guard tests, repository secret scan, README finalization.
- Stop gate: Gate 5.

### Phase 11: Deployment and Online Demo

- Objective: deploy a backend-capable Django/PostgreSQL demo after owner selects access model and provider.
- Dependency: Gate 5.
- Scope boundary: production-safe settings, environment variables, static/media, migrations, demo account, reset policy, smoke tests.
- Expected micro-slices: provider decision, deployment config, database provisioning, static/media strategy, seed/reset, smoke test, README demo link.
- Stop gate: Gate 6.

### Phase 12: Public Release

- Objective: owner-approved public portfolio release.
- Dependency: Gate 6.
- Scope boundary: final release checklist, README accuracy, license decision, public repository state.
- Expected micro-slices: release audit, final docs sync, owner approval, push/public release.
- Stop gate: Gate 7.

## 13. UI/UX Review Gates

Required review after the first usable version of:

- application shell;
- product workspace;
- create/edit form;
- dashboard;
- ready reply surface.

Each review must check first viewport usefulness, primary action clarity, explicit return paths, mobile density, accessibility baseline, and whether the screen has gained unapproved scope.

## 14. Test and CI Gates

- Gate 1 requires Django system check and test harness in CI.
- Gate 2 requires auth and cross-business isolation tests.
- Gate 3 requires product creation/editing, semantic-recognition validation, confirmed-fact handling, choice validation, lifecycle, inventory, and availability tests.
- Gate 4 requires route-return, HTMX response, stale-state, mobile/manual UX, and accessibility smoke checks.
- Gate 5 requires setup, seed/reset, security hygiene, and README factuality checks.
- Gate 6 requires deployment smoke test and demo reset/reseed verification.

No document may claim tests pass or CI passes until they have actually run.

## 15. Documentation Update Matrix

| Change Type | changelog_checkpoint.md | BUILD_PLAN.md | APP_EXPERIENCE_PLAN.md | DEVELOPMENT_NOTES.md | Frozen Docs | README.md |
|---|---|---|---|---|---|---|
| Owner scope decision | Update blocker/current phase | Update affected phase or owner decisions | Update only if UX contract changes | Record meaningful trade-off if useful | Update only with owner approval | Usually no |
| New micro-slice starts | Update current phase and micro-slice | No unless plan changes | No | No | No | No |
| Feature implemented | Update completed work, verification, next action | Update status if phase/slice passed | Update if UX evidence changes | Record lesson only if meaningful | No automatic edits | Update only if public status changes |
| UX finding | Update risks/blockers if current | Update gate if needed | Update non-frozen UX plan or add owner decision | Record rejected alternative or lesson if meaningful | No automatic edits | No |
| Test/CI result | Update verification | Update phase/gate status if relevant | No | Record only if it changes strategy | No | Add only after stable public-facing result |
| Deployment result | Update online demo status | Update Gate 6 status | Update demo UX verification if needed | Record provider trade-off if meaningful | No automatic edits | Add real URL only after verified |
| Commit/push | Update Git checkpoint | No unless roadmap status changes | No | No | No | No |
| Documentation drift | Update blockers | Update if execution order affected | Update if UX contract affected | Record decision if it changes future behavior | Owner-approved amendment only | Fix public factuality if needed |

## 16. Deployment and Demo Phase

Deployment remains a separate phase and requires owner approval. GitHub is the source-code and portfolio platform, but GitHub Pages is not a normal backend host for Django/PostgreSQL.

Deployment micro-slices:

- deployment target decision;
- production-safe settings;
- environment variables;
- PostgreSQL provisioning;
- migration execution policy;
- static files;
- media strategy;
- synthetic demo seed;
- demo account;
- reset/reseed;
- health check;
- deployment smoke test;
- README demo link;
- mobile demo verification;
- security review.

Do not choose a provider or claim a demo URL before owner approval and verification.

## 17. Portfolio Release Criteria

- Owner-approved scope and documents.
- Public repository with honest commit history.
- Reproducible local setup.
- CI passing on current branch.
- Critical tests passing.
- No secrets, real media, database dumps, customer data, or source prototype artifacts committed.
- Synthetic demo data available.
- Online Django demo deployed on a backend-capable platform.
- Demo smoke test passed.
- README accurately states project status and demo instructions.
- Mobile seller workflow manually checked.
- Deferred scope explicitly documented.

## 18. Risks and Anti-Patterns

- Endless rebuild without stop gates.
- Large Codex-generated diffs that cannot be reviewed.
- Stale `changelog_checkpoint.md`.
- UI feature accumulation before page responsibility review.
- Documentation drift between frozen docs, README, and implementation.
- Fake or inflated commit history.
- Premature public catalog, chatbot, order, payment, or delivery work.
- Secrets or real media in Git.
- Demo using real seller/customer data.
- Prototype behavior copied without owner approval.

## 19. Deferred Roadmap

| Capability | Status | Reason |
|---|---|---|
| Public buyer catalog | DEFERRED | Seller truth must be reliable first |
| Chatbot/messaging assistant | DEFERRED | Deterministic seller-side truth boundary comes first |
| LLM interpretation | DEFERRED | LLM must never own product truth |
| Orders/reservations | DEFERRED | Requires reliable stock and explicit transaction rules |
| Payments | DEFERRED | Requires orders and production-grade security/compliance decisions |
| Delivery workflow | DEFERRED | Requires order lifecycle foundation |
| Accounting/ERP | DEFERRED | Outside seller catalog cockpit V1 |
| Supplier management | DEFERRED | Outside V1 problem |
| Analytics BI | DEFERRED | Usage events may exist, BI dashboards later |
| Multi-staff permissions | DEFERRED | Single-seller owner workflow first |
| DRF/public API | DEFERRED | Server-rendered V1 first; API later if public/buyer layers need it |

## 20. Owner Decisions Required

- Owner approval before implementing P1.1.
- Final public project/repository name.
- License choice.
- Exact V1 behavior for recognizing observed text, candidate meaning, and confirmed facts.
- Material confirmation UI and alias policy.
- Detailed measurement micro-slice timing, including measurement type, value, unit, method, and product/choice boundary.
- Whether fit guidance appears in a later approved measurement/fit micro-slice.
- Whether Product Detail remains in Portfolio V1.
- Whether product relations are V1 or deferred.
- Whether clone and archive/restore are V1.
- Exact clone stock-copy policy.
- Whether type/tag management pages are V1 or mostly inline.
- Whether tags affect readiness or only organization/search.
- Price policy for zero, null, missing, and free products.
- Duplicate size/color choice policy.
- Direct stock set placement.
- Dashboard first-viewport priority.
- Ready reply placement.
- Final Georgian terminology.
- Deployment provider and demo access model.
- Demo media strategy and reset cadence.
