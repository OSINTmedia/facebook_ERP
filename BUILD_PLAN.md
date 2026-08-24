# Build Plan

## Document Metadata

- Status: SEMI_FROZEN
- Version: 2.0
- Owner: osMit
- Source documents: `APP_EXPERIENCE_PLAN.md`, `DEVELOPMENT_NOTES.md`, `docs/Portfolio_MVP_V1.md`, `docs/Technical_Planning_v1.md`, `docs/domain/CLOTHING_DATA_SPEC_V1.md`, `docs/User_Journey_Freeze_v1.md`, `docs/discovery/backend.md`, `docs/discovery/frontend.md`, `docs/discovery/DISCOVERY_REPORT.md`
- Update rule: update only when roadmap, dependency, gate, scope, stop condition, or verification strategy changes
- Roadmap authority: this file controls implementation order; frozen product documents control scope
- Codex may reorder phases automatically: no

## 1. Implementation Objective

Build a clean Social Commerce Seller Operations Assistant from zero in `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`. The source prototype in `/home/giga/Desktop/OSINT/facebook_MVP/` remains read-only discovery evidence and behavior reference, not source code to copy wholesale.

The rebuild must proceed through small, reviewable micro-slices with explicit acceptance criteria, automated verification where possible, manual owner verification where needed, documentation updates only when the matrix requires them, and honest Git history.

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

Local-only workflow artifacts are not public repository authority and must remain excluded from version control.

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
- Commit only after source changes and any required documentation changes are synchronized.
- Before commit, summarize source changes, verification performed, and known gaps; update checkpoints only when the documentation matrix requires it.
- Push only after owner approval for the Release step.
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
7. Integrity audit and documentation decision
   - Review scope, ownership, state boundaries, security, UX, and regression risks.
   - Decide whether documentation must change under the documentation update matrix.
8. Release
   - Review the final diff and verification evidence.
   - Stage only explicit approved paths.
   - Commit with one clear intention.
   - Push after owner approval.
   - Check Git/remote alignment after push.
   - Verify the latest relevant CI result.

Successful commit, push, Git/remote alignment, and CI success are operational closure for the same functional micro-slice, not a new micro-slice. Exact `HEAD`, `origin/main`, remote branch state, and CI state must be read from Git and GitHub. Do not create a `.1 Post-Push...` slice solely to record successful delivery metadata.

## 8. Mandatory Stop Gates

- Gate 0: documents owner-reviewed.
- Gate 1: repository and CI foundation; passes only after P1.6 CI/test harness verification.
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
| Phase 1 | Django/PostgreSQL Foundation and CI | Create minimal clean Django project, settings, test harness, and CI | PASSED | Gate 1 | Scaffold commits, CI workflow, reproducible setup |
| Phase 2 | User and Business Ownership | Implement authentication and business ownership boundary | PASSED | Gate 2 | User/business tests, access-control tests |
| Phase 3 | Catalog Core | Implement product core facts and lifecycle | PASSED | Gate 3 | Product model/forms/views/tests |
| Phase 4 | Semantic Recognition and Choice Model | Implement description-first recognition for type/tag/material candidates plus stock-bearing choices | PASSED | Gate 3 | Recognition contract, alias tests, choice validation |
| Phase 5 | Inventory and Computed Availability | Centralize stock mutations and computed availability | IN_PROGRESS | Gate 3 | Inventory service tests and ledger tests |
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
- Likely files: Git metadata only plus checkpoint updates only if verification changes project state or exposes divergence.
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
- Likely files: none locally unless failure, divergence, or public factuality correction requires documentation.
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

- Objective: align document authority, checkpoint reality, local-only artifact handling, and measurement scope before technical implementation begins.
- Dependency: P0.1 through P0.6 `PASSED`; P0.7 explicitly `DEFERRED`.
- Exact scope: mark owner-controlled docs frozen, mark this plan and the app experience plan semi-frozen, keep `changelog_checkpoint.md` and `DEVELOPMENT_NOTES.md` live, keep local-only workflow artifacts ignored, update Git reality, and keep detailed garment measurement implementation deferred.
- Explicit exclusions: no Django initialization, no dependency install, no app code, no CI, no migrations, no source prototype changes, no commit or push during the sync itself.
- Likely files: `.gitignore`, `README.md`, `BUILD_PLAN.md`, `APP_EXPERIENCE_PLAN.md`, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md`, selected owner-controlled docs for status and approved measurement-boundary correction.
- Backend acceptance criteria: no backend code exists or changes.
- Frontend/UX acceptance criteria: the assistant-first, two-primary-surface UX contract remains intact.
- Automated verification: `git status --short --branch`, `git diff --stat`, `git diff --check`, link/path scan, and stale-state grep.
- Manual user verification: owner confirms this corrective sync before Git checkpoint.
- Failure cases: local-only workflow artifact staged; checkpoint remains stale; measurement implementation appears as V1 scope; frozen docs gain unapproved scope.
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
- Status: PASSED.

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
- Status: PASSED.

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
- Status: PASSED.

### P1.4 PostgreSQL and Test Database Baseline

- Objective: verify the rebuild runs against PostgreSQL-oriented settings.
- Dependency: P1.3 `PASSED`.
- Exact scope: configure database URL handling and test database expectations.
- Explicit exclusions: no migrations beyond default framework if not needed, no production database, no prototype database access.
- Likely files: settings, `.env.example`, README setup.
- Backend acceptance criteria: database configuration is explicit and portable; local PostgreSQL runtime access is verified.
- Frontend/UX acceptance criteria: none.
- Automated verification: `python manage.py check`, `python manage.py migrate --check`, `python manage.py showmigrations`, and `python manage.py test config -v 2` after owner-approved local DB setup.
- Manual user verification: owner confirms local PostgreSQL expectation and local server startup.
- Failure cases: SQLite-only drift, hardcoded database credentials, unmanaged local assumptions.
- Documentation updates: README local setup after verified commands exist.
- Proposed commit message: `chore: document postgresql database baseline`.
- Rollback/recovery note: revise settings before adding models.
- Stop gate: database configuration approved.
- Status: PASSED.
- Runtime verification: project-specific local PostgreSQL role/database `facebook_erp_dev` verified through `.venv`, direct Django database connection, applied default migrations, config test, local server startup, and HTTP response. PostgreSQL-only and no-SQLite boundaries remain.

### P1.5 Base Application Shell

- Objective: create the minimal private seller-workspace application shell before feature pages accumulate.
- Dependency: P1.3 `PASSED`.
- Exact scope: base template structure, message region, navigation placeholders, static CSS path.
- Explicit exclusions: no product workspace, dashboard metrics, inventory controls, or public catalog.
- Likely files: base template, static CSS, URL/view placeholder if needed.
- Backend acceptance criteria: route protection direction is documented.
- Frontend/UX acceptance criteria: active location pattern, semantic messages, mobile container, and no marketing landing page.
- Automated verification: template render smoke test, root route `200`, unknown route `404`, and shell CSS `200`.
- Manual user verification: owner/browser review completed for the foundation shell; mobile polish remains deferred UX refinement.
- Failure cases: nav labels imply broader ERP scope; no active-state pattern; inaccessible messages.
- Documentation updates: APP experience notes if owner changes shell contract, checkpoint.
- Proposed commit message: `feat: add minimal application shell`.
- Rollback/recovery note: keep shell small so it can be revised before feature pages.
- Stop gate: shell UX gate passed.
- Status: PASSED.

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
- Current implementation state: workflow committed and pushed as `23fb3ca`; GitHub Actions run `30537591111` completed successfully; local equivalent checks passed.
- Status: PASSED.

## 12. Remaining Phase Outlines

### Phase 2: User and Business Ownership

- Objective: implement custom auth direction and business ownership boundary.
- Dependency: Gate 1.
- Scope boundary: User, Business, login/logout, active business policy, access tests.
- Expected micro-slices: auth model, business model, login flow, owner-scoped query helper, cross-business access tests.
- Current dependency state: Gate 1 and Gate 2 are passed. P2.1 through P2.5 and the Environment-Gated Demo Seller Access Bootstrap are released and `PASSED`. Phase 3 and Phase 4 are `PASSED`; Gate 3 remains open pending Phase 5 inventory and computed-availability work.
- Stop gate: every seller-owned object created later has a business boundary and test pattern.

### Phase 3: Catalog Core

- Objective: implement product facts and lifecycle without stock complexity first.
- Dependency: Phase 2.
- Scope boundary: product name/description, price policy after owner decision, lifecycle, business ownership, create/list/edit basics.
- Expected micro-slices: product model, product form, product list, product create/edit, lifecycle tests.
- Current implementation state: P3.1 Product Model Baseline, P3.2 Product Form Baseline, P3.3 Product List Baseline, and P3.4 Product Create/Edit Baseline are implemented, integrity-audited, locally verified, committed, pushed, CI-passed, and passed. Earlier legacy post-push checkpoint syncs are historical records only and do not define the Version 2 workflow.
- Stop gate: seller can create and edit a business-owned product and cannot access another business's product.

### Phase 4: Semantic Recognition and Choice Model

- Objective: add the description-first assistant layer that recognizes Product Type, Tag, material, and size/color candidates while preserving observed text, candidate meaning, confirmed fact boundaries, and choice-level stock truth.
- Dependency: Phase 3.
- Scope boundary: `docs/domain/CLOTHING_DATA_SPEC_V1.md`, observed text, recognized candidates, confirmed structured facts, business-scoped vocabulary and aliases, material as typed semantic fact, distinct stock-bearing choice rows, owner-approved duplicate size/color preservation, minimum valid active-product choice behavior at the bundle boundary, compact create/edit integration, and product bundle validation.
- Current implementation state: Phase 4 is `PASSED`. P4.1 through P4.9f, including P4.9d_expand and P4.9e_expand, are released, owner-reviewed, and `PASSED`; P4.10 passed its code-first scope/integrity audit, local PostgreSQL verification, release, and exact-SHA CI without source repair. Phase 5 is `IN_PROGRESS`: P5.1 through P5.6 are released, owner-reviewed where required, and exact-SHA CI-passed. P5.6A is the next planned functional slice and owns the approved one-save initial-stock correction before P5.7 transition/regression readiness. Gate 3 remains open pending P5.6A and P5.7 evidence. Availability has no UI consumer yet, and readiness and buyer replies do not exist; exact delivery metadata remains Git/GitHub authority.
- Separate deferred micro-slice: detailed garment measurements remain outside Phase 4 implementation until measurement type, value, unit, method, applicable product/choice boundary, category-specific capture rules, buyer-reply wording, and seller UI are owner-approved.
- Stop gate: product bundle save cannot persist partial invalid choice state, size/color truth comes from confirmed choices, and buyer replies consume confirmed facts only.

#### P4.1 Semantic Recognition Service Contract Baseline

- Objective: create the pure recognition contract that keeps seller description text separate from candidate meaning and confirmed facts.
- Dependency: Phase 3 passed.
- Exact scope: recognition result contract; observed text, candidate meaning, and confirmed fact boundary; semantic destination enum or equivalent; immutable transient candidates; pure service boundary.
- Explicit exclusions: database migrations, UI integration, product form changes, choice model changes, material model implementation, buyer replies, public catalog, chatbot, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/recognition.py`, focused recognition tests, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: recognition preserves raw observed text; candidates require confirmation; confirmed facts are empty unless supplied by later confirmed persistence; semantic destinations distinguish type, tag, material, choice size, choice color, measurement, and search-token concepts; negative material phrases are not converted into positive candidates.
- Frontend/UX acceptance criteria where relevant: none; backend service only.
- Automated verification: Django system check, migration dry-run check, focused recognition tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none.
- Failure cases: recognition confirms facts automatically; candidate text overwrites observed text; global vocabulary or LLM extraction becomes source of truth; negation creates a positive material candidate.
- Documentation updates: update live checkpoint and development notes only when the implementation changes state, strategy, blocker, or meaningful decision; do not touch frozen docs without owner approval.
- Proposed commit message: `feat: add semantic recognition service contract`.
- Rollback/recovery note: revert the pure service and focused tests if the contract fails the observed/candidate/confirmed boundary; do not patch around it in forms or templates.
- Stop gate relation: required foundation for all later Phase 4 recognition work.
- Status: PASSED.

#### P4.2 Product Type Recognition Baseline

- Objective: add business-scoped Product Type vocabulary and recognition from product descriptions without making recognized type a Product fact automatically.
- Dependency: P4.1 `PASSED`.
- Exact scope: business-scoped product type vocabulary; Product Type recognition from description; canonical candidate output; negative/no-match cases; cross-business isolation tests.
- Explicit exclusions: tag recognition, aliases, material recognition, size/color choice suggestions, Product type assignment to Product, UI integration, type-management screens, public catalog, chatbot, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/models.py`, `catalog/recognition.py`, `catalog/tests.py`, catalog migration files when schema changes, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: Product Type vocabulary is owned by Business; names are stripped, nonblank, and unique per Business after case-insensitive normalization; recognition reads only the supplied Business vocabulary and returns unconfirmed Product Type candidates.
- Frontend/UX acceptance criteria where relevant: none for backend-only vocabulary/recognition; no seller UI may imply confirmed type assignment until a later integration slice.
- Automated verification: Django system check, migration dry-run check, focused Product Type model/recognition tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none unless an approved UI is added in a later slice.
- Failure cases: cross-business vocabulary leak; recognized Product Type becomes confirmed Product truth; blank or duplicate canonical names persist; Product form grows to include unmanaged type UI.
- Documentation updates: update live checkpoint and development notes only when required by the documentation matrix; do not update README or frozen docs for backend-only completion.
- Proposed commit message: `feat: add product type recognition`.
- Rollback/recovery note: revert the Product Type vocabulary, migration, and recognition changes together if the Business boundary or candidate contract fails.
- Stop gate relation: required before Product Type candidates can be shown or confirmed in create/edit flows.
- Status: PASSED.

#### P4.3 Tag Recognition Baseline

- Objective: add business-scoped generic/feature Tag vocabulary and recognition from product descriptions without creating buyer-facing truth claims.
- Dependency: P4.1 `PASSED`; P4.2 Product Type recognition boundaries understood.
- Exact scope: business-scoped generic/feature tags; Tag recognition from description; duplicate prevention; normalization tests; cross-business isolation tests.
- Explicit exclusions: aliases, material facts, size/color choices, Product tag assignment, tag readiness policy, buyer-facing truth claims, tag-management UI, public catalog, chatbot, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/models.py`, `catalog/recognition.py`, `catalog/tests.py`, catalog migration files when schema changes, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: Tag vocabulary is owned by Business; tag names are stripped, nonblank, and unique per Business after case-insensitive normalization; recognition reads only the supplied Business vocabulary and returns unconfirmed Tag candidates.
- Frontend/UX acceptance criteria where relevant: none for backend-only vocabulary/recognition; tags must not appear as confirmed Product facts or readiness requirements until owner-approved behavior exists.
- Automated verification: Django system check, migration dry-run check, focused Tag model/recognition tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none unless an approved UI is added in a later slice.
- Failure cases: cross-business tag leak; duplicate/casefold collision persists; recognized tag affects readiness or buyer replies before confirmation; material or choice size/color is stored as a generic tag.
- Documentation updates: update live checkpoint and development notes only when required by the documentation matrix; do not update README or frozen docs for backend-only completion.
- Proposed commit message: `feat: add tag recognition`.
- Rollback/recovery note: revert Tag vocabulary, migration, and recognition changes together if normalization or Business isolation fails.
- Stop gate relation: required before Tag candidates can be shown or confirmed in create/edit flows.
- Status: PASSED.

#### P4.4 Business-Scoped Alias Normalization Baseline

- Objective: add business-scoped aliases for existing Product Type and Tag vocabulary without turning matched aliases into confirmed Product truth.
- Dependency: P4.2 and P4.3 `PASSED`.
- Exact scope: business-owned Product Type aliases; business-owned Tag aliases; alias stripping, nonblank validation, case-insensitive uniqueness, canonical-name collision prevention, same-Business validation, and recognition through aliases.
- Explicit exclusions: alias-management UI, automatic alias learning, Product type/tag assignment, confirmation UI, material alias policy, material fact persistence, size/color choices, stock, availability, buyer replies, public catalog, chatbot, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/models.py`, `catalog/recognition.py`, `catalog/tests.py`, catalog migration files when schema changes, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: aliases are scoped to one Business; aliases point only to canonical Product Types or Tags in the same Business; aliases and canonical names cannot collide in the same destination; recognition returns canonical unconfirmed candidates.
- Frontend/UX acceptance criteria where relevant: none for backend-only vocabulary/recognition.
- Automated verification: Django system check, migration dry-run check, focused alias model/recognition tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none unless an approved UI is added in a later slice.
- Failure cases: cross-business alias leak; alias/name collision persists; alias recognition confirms Product truth; material aliases are silently introduced without owner-approved policy.
- Documentation updates: update live checkpoint and development notes only when required by the documentation matrix.
- Proposed commit message: `feat: add business scoped alias recognition`.
- Rollback/recovery note: revert alias models, migration, recognition, and tests together if normalization or Business isolation fails.
- Stop gate relation: required before aliases can support create/edit recognition feedback.
- Status: PASSED.

#### P4.5a Confirmed Material Fact Model Baseline

- Objective: persist material as a typed confirmed Product fact without using ordinary Tags or unconfirmed description text as buyer-facing truth.
- Dependency: P4.1 `PASSED`; Product and Business ownership boundaries exist.
- Exact scope: confirmed material fact model; canonical material; optional percentage; original seller wording; source; confirmed-only state; Product/Business scoping; nonblank, percentage, source, confirmation, and deletion-protection tests.
- Explicit exclusions: material recognition from confirmed facts, material confirmation UI, material aliases, Product form integration, readiness, buyer replies, search, size/color choices, stock, availability, measurements, public catalog, chatbot, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/models.py`, `catalog/tests.py`, catalog migration files when schema changes, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: confirmed material facts are scoped to Business and Product; material fields are normalized and validated; percentages are optional and bounded; source and confirmation state are explicit; material facts validate same-Business Product ownership.
- Frontend/UX acceptance criteria where relevant: none for backend-only persistence.
- Automated verification: Django system check, migration dry-run check, focused material model tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none.
- Failure cases: material is implemented as an ordinary Tag; unconfirmed material candidates drive replies; percentage accepts invalid values; cross-business Product/material joins are allowed.
- Documentation updates: update live checkpoint and development notes only when required by the documentation matrix; keep frozen clothing spec unchanged unless owner explicitly approves a domain amendment.
- Proposed commit message: `feat: add confirmed material fact baseline`.
- Rollback/recovery note: revert material model, migration, and tests together if confirmation, Business scoping, or validation boundaries fail.
- Stop gate relation: required before confirmed material can contribute to buyer-question coverage or deterministic replies in later phases.
- Status: PASSED.

#### P4.5b Material Recognition Candidate Baseline

- Objective: recognize material candidates from the seller's already confirmed material facts without creating or updating confirmed material truth.
- Dependency: P4.5a `PASSED`.
- Exact scope: derive material recognition terms from confirmed `ProductMaterialFact` rows for one Business; return transient unconfirmed `MATERIAL` candidates; preserve negation and cross-business isolation; prove recognition is read-only.
- Explicit exclusions: material confirmation UI, material aliases, global textile dictionary, Product form integration, readiness, buyer replies, search UI, size/color choices, stock, availability, measurements, public catalog, chatbot, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/recognition.py`, `catalog/tests.py`, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: material recognition reads only confirmed material facts for the supplied Business; duplicate material terms are normalized case-insensitively; recognition returns no confirmed facts and creates no database rows.
- Frontend/UX acceptance criteria where relevant: none for backend-only recognition behavior.
- Automated verification: Django system check, migration dry-run check, focused material recognition tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none.
- Failure cases: cross-business material facts leak; unconfirmed description text becomes material truth; material aliases or global vocabulary are silently introduced.
- Documentation updates: update live checkpoint and development notes only when required by the documentation matrix.
- Proposed commit message: `feat: recognize material candidates from confirmed facts`.
- Rollback/recovery note: revert material recognition helpers and tests if they cross the candidate/confirmed fact boundary.
- Stop gate relation: required before material candidates can be surfaced for seller confirmation in create/edit integration.
- Status: PASSED.

#### P4.6 Size/Color-to-Choice Suggestion Baseline

- Objective: recognize caller-supplied size/color candidates from product descriptions without automatically creating confirmed choice truth.
- Dependency: P4.1 `PASSED`; `docs/domain/CLOTHING_DATA_SPEC_V1.md` choice truth boundary.
- Exact scope: caller-supplied size and color recognition terms; transient `CHOICE_SIZE` and `CHOICE_COLOR` candidates; stripping and case-insensitive deduplication; candidate versus confirmed choice boundary; tests proving description size/color is not persisted as Tag or ProductChoice truth automatically.
- Explicit exclusions: `ProductChoice` model, migrations, duplicate-choice policy, automatic confirmed choice creation, Product form integration, inventory behavior, stock mutation service, UI polish, measurements, public catalog, orders, reservations, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/recognition.py`, `catalog/tests.py`, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: supplied size/color values become transient unconfirmed candidates with preserved observed text and canonical value; candidate output never creates Product choices, Tags, stock, or confirmed facts automatically; negation boundaries are preserved.
- Frontend/UX acceptance criteria where relevant: none for backend-only recognition behavior.
- Automated verification: Django system check, migration dry-run check, focused choice-suggestion recognition tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none.
- Failure cases: description size/color becomes generic Tag truth; candidate creates confirmed choice rows without seller action; duplicate choice policy is bypassed; UI implies buyer-facing availability before a confirmed choice and quantity exist.
- Documentation updates: update live checkpoint and development notes only when required by the documentation matrix; do not update README or frozen docs for backend-only suggestion work.
- Proposed commit message: `feat: add size color choice suggestions`.
- Rollback/recovery note: revert suggestion helpers and tests if they cross the candidate/confirmed choice boundary.
- Stop gate relation: supports compact create/edit flow but does not satisfy choice persistence or inventory requirements by itself.
- Status: PASSED.

#### P4.7 Product Choice Model Baseline

- Objective: add the stock-bearing Product choice/variant model that owns confirmed size, color, quantity, and active state.
- Dependency: P4.6 `PASSED`; Phase 3 Product model exists; owner policy allows duplicate size/color rows, including case-insensitive, trim-normalized matches, as distinct sellable choices.
- Exact scope: stock-bearing product choices or variants; required size and color; nonnegative quantity; active/inactive state; distinct row identity; duplicate size/color preservation; individual choice-row validation; Business/Product ownership isolation. Aggregate Product-plus-choice validation remains P4.8.
- Explicit exclusions: inventory ledger, stock mutation service, computed availability beyond this phase requirement, Product create/edit UI integration beyond the approved slice, public catalog, orders, reservations, payments, delivery, broad ERP, detailed measurements, and LLM-owned truth.
- Likely files: `catalog/models.py`, `catalog/tests.py`, catalog migration files, forms or services only if needed for model/formset validation, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: each choice belongs to one Product and Business boundary; size and color are persisted on the choice, not as generic tags; quantity is nonnegative; active/inactive state is explicit; duplicate normalized size/color rows may coexist on the same Product with distinct primary keys and quantities; rows are never merged automatically; recognition candidates create no choice rows automatically.
- Frontend/UX acceptance criteria where relevant: none for backend-only model baseline; seller-facing terminology should prefer choice/`არჩევანი` when UI is later added.
- Automated verification: Django system check, migration dry-run check, focused choice model/validation tests, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: none unless visible choice behavior is added.
- Failure cases: quantity is stored on Product; size/color is stored only as generic tags; negative quantity persists; any uniqueness constraint or validation blocks same-Product duplicate size/color rows; duplicate rows are merged automatically; recognition creates choice rows automatically; cross-business Product/choice joins are allowed; aggregate or UI-disambiguation rules are implemented prematurely.
- Documentation updates: update live checkpoint and development notes only when required by the documentation matrix; record owner duplicate-choice policy if decided.
- Proposed commit message: `feat: add size color choice model`.
- Rollback/recovery note: preserve released migration history; correct a released constraint with a forward migration rather than rewriting migration `0006`.
- Stop gate relation: required before product bundle validation, inventory, availability, workspace cards, and truthful size/color replies.
- Status: PASSED; the baseline and forward duplicate-policy correction are released, remote-aligned, and CI-passed.

#### P4.8 Product Choice Form/Formset and Bundle Validation Baseline

- Objective: validate Product plus choice rows as one safe seller product bundle without partial invalid choice state.
- Dependency: P4.7 Product Choice Model Baseline exists.
- Exact scope: Product + choices validation; form or formset boundary for size, color, quantity, and active state; minimum valid choice behavior; prevention of partial invalid choice persistence; cross-business Product/choice safety; validation-error preservation.
- Explicit exclusions: inventory ledger, stock mutation service, computed availability, public catalog, buyer replies, measurements, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Likely files: `catalog/forms.py`, `catalog/tests.py`, service module if introduced for bundle validation, `DEVELOPMENT_NOTES.md`, `changelog_checkpoint.md` when documentation matrix requires it.
- Backend acceptance criteria: invalid Product/choice combinations do not partially persist; active choice rows validate size, color, quantity, and Business/Product ownership; same-size/color rows remain distinct and are not rejected or merged; an active Product requires at least one valid active choice, while draft Product behavior remains compatible with incomplete product capture.
- Frontend/UX acceptance criteria where relevant: none unless visible form rows are added; visible row errors must stay compact and preserve seller input if UI is touched.
- Automated verification: Django system check, migration dry-run check, focused form/formset/service tests, transaction or persistence failure tests where feasible, full Django test suite, `git diff --check`.
- Manual user verification where UI changes: required only if visible choice rows or validation UI are added.
- Failure cases: Product persists without required valid choices when not allowed; partial choices persist after invalid submission; same-size/color rows are rejected or merged; cross-business Product/choice joins are allowed; validation errors appear only as generic page failures.
- Documentation updates: update live checkpoint and development notes when validation strategy changes; update BUILD_PLAN only if stop criteria or phase dependencies change.
- Proposed commit message: `feat: validate product choice bundles`.
- Rollback/recovery note: revert bundle validation changes if atomicity or error recovery is not provable; preserve earlier valid recognition services and choice model when valid.
- Stop gate relation: required before Product create/edit integration can safely save choice truth.
- Status: PASSED; implemented, integrity-audited, committed, pushed, remote-aligned, and CI-passed.

#### P4.9 Product Create/Edit Recognition and Choice Integration

- Objective: connect released recognition candidates and the ProductChoice model into the seller create/edit workflow while keeping the form compact.
- Execution rule: complete P4.9 through P4.9a through P4.9f plus the owner-approved P4.9d_expand and P4.9e_expand extensions below. Each extension shares the audit/release boundary of its owning functional slice and is not a post-push synchronization slice. Do not treat the P4.9 umbrella as one implementation-sized slice and do not skip controlled-vocabulary or confirmation boundaries between candidates and persisted facts.
- Shared exclusions: large clothing forms, measurement UI, buyer reply UI, dashboard/workspace work, inventory mutation behavior, computed availability, public catalog, chatbot, orders, payments, delivery, broad ERP, and LLM-owned truth.
- Shared stop gate: P4.9 is complete only after P4.9a through P4.9f plus P4.9d_expand and P4.9e_expand are released, remote-aligned, CI-passed, and the required owner decisions and browser verification have passed.
- Status: PASSED WITH NOTES — P4.9a through P4.9f, including P4.9d_expand and P4.9e_expand, are released, remote-aligned, CI-passed, owner/browser-reviewed, and technically accepted. Owner notes record that the Product create/edit UX remains inconvenient and not yet sufficiently assistant-like; address that through a later UX-focused slice or phase, not by reopening P4.9 technical acceptance.

##### P4.9a Product Choice Create/Edit Integration Baseline

- Objective: make the released Product/choice bundle usable through the authenticated seller Product create/edit screen.
- Dependency: P4.8 released and CI-passed.
- Exact scope: use `ProductBundle` in create/update GET and POST paths; render management data, existing choice rows, and one blank extra row; allow create, update, deactivate, and discard of unsaved rows while persisted choice deletion is blocked by the later stock-boundary contract; preserve field/formset errors, submitted values, safe return paths, and Business ownership isolation.
- Explicit exclusions: recognition feedback or confirmation, dynamic multi-row cloning, inventory ledger/service, computed availability, price, media, measurements, and later-phase workspace behavior.
- Acceptance criteria: Product and choices save atomically; active Products retain at least one active choice; drafts may have no choices; cross-Business Product/choice input cannot leak or mutate data; choice fields and recovery remain accessible and mobile-readable.
- Verification: local/test Django checks, local/test migration dry-run checks, focused create/update/bundle tests, catalog tests, full Django suite, `git diff --check`, and owner/browser review of create/edit, recovery, return paths, and a 390px viewport.
- Proposed commit message: `feat: integrate choices into product forms`.
- Status: PASSED — released, remote-aligned, and CI-passed; exact delivery metadata remains Git/GitHub authority.

##### P4.9b Product Create/Edit Recognition Preview Baseline

- Objective: show lightweight, transient Product Type, Tag, material, size, and color candidates beside the description without persisting them as facts.
- Dependency: P4.9a released and CI-passed.
- Exact scope: compose the released Business-scoped recognition services into create/edit context; preserve observed text separately; render candidate destination, canonical meaning, and confirmation-required state; update the preview automatically through a debounced HTMX request with a full-page fallback; preserve preview context on validation errors. Product Type/Tag vocabulary and aliases, confirmed material facts, and current confirmed ProductChoice size/color values remain the read-only term sources for this baseline.
- Explicit exclusions: Product Type/Tag attachment, material-fact writes, candidate-to-choice transfer, alias learning, automatic confirmation, HTMX-only behavior, and LLM interpretation.
- Acceptance criteria: preview reads only the active Business vocabulary; candidates never mutate Product facts or choices; negative phrases remain excluded; the screen remains compact, accessible, and mobile-readable.
- Verification: focused recognition-context/view tests, cross-Business non-leakage tests, error-preservation tests, full Django suite, `git diff --check`, and owner/browser preview review.
- Proposed commit message: `feat: preview product recognition candidates`.
- Status: PASSED — released, remote-aligned, and CI-passed; exact delivery metadata remains Git/GitHub authority.

##### P4.9c Business-Scoped Size/Color Vocabulary and Dropdown Baseline

- Objective: replace open-text size/color entry with seller-managed, Business-scoped canonical vocabulary and dropdown selection before candidate transfer is implemented.
- Dependency: P4.9b released and CI-passed.
- Exact scope: Business-owned canonical Size and Color vocabulary; Business-scoped multilingual aliases; dropdown-only ProductChoice form selection; compact contextual seller creation of approved values and explicit aliases; safe forward migration of existing ProductChoice text; recognition terms sourced from controlled vocabulary; preservation of duplicate ProductChoice row identity and quantities. Historical case/trim-equivalent text maps to the deterministic first canonical value within its Business without merging ProductChoice rows; semantically different values are not guessed or merged.
- Explicit exclusions: universal/global fashion dictionary, automatic alias learning, classifying every description token, candidate-to-choice transfer, automatic choice save, inventory mutations, availability computation, row merging, buyer-facing wording, and broad taxonomy administration.
- Acceptance criteria: only the active Business vocabulary appears in dropdowns; cross-Business values and aliases are rejected; existing choices migrate without stock or row-identity loss; stored choices use canonical values while recognition can match approved Georgian/English aliases; seller can add an approved value without leaving the compact Product form; duplicate ProductChoice rows remain distinct.
- Verification: migration and rollback-shape review, focused vocabulary/alias/form/migration/ownership tests, catalog tests, full Django suite, `git diff --check`, and owner/browser dropdown and contextual-add review.
- Proposed commit message: `feat: add controlled size color vocabulary`.
- Status: PASSED — released, remote-aligned, and CI-passed; non-blocking UX refinements for later automatic assistance remain deferred.

##### P4.9d Size/Color Candidate-to-Choice Transfer Baseline

- Objective: let the seller explicitly transfer a recognized size/color candidate into an editable controlled-vocabulary choice row while keeping ProductChoice as the only confirmed size/color truth.
- Dependency: P4.9c released and CI-passed.
- Exact scope: explicit seller action only; server-truth transfer into the current Product choice formset; resolve approved aliases to canonical dropdown values; preserve existing rows, management state, validation errors, duplicate-row policy, Business scope, and safe return context.
- Explicit exclusions: silent choice creation, automatic save, inventory mutations, availability computation, row merging, buyer-facing wording, and broad dynamic form-builder behavior.
- Acceptance criteria: unaccepted candidates remain transient; accepted canonical values remain editable before save; only a valid final bundle persists ProductChoice rows; duplicate size/color rows remain distinct.
- Verification: focused transfer/formset/view tests, alias, tamper, and cross-Business tests, full Django suite, `git diff --check`, and owner/browser interaction review.
- Proposed combined commit message: `feat: transfer candidates and manage choice vocabulary`.
- Status: PASSED — combined implementation with P4.9d_expand was integrity-audited, owner-reviewed, released, remote-aligned, and CI-passed; exact delivery metadata remains Git/GitHub authority.

##### P4.9d_expand Size/Color Vocabulary Management Surface

- Objective: let the seller inspect and safely maintain the complete Business-scoped Size/Color vocabulary, including which aliases resolve to each canonical value, before or during product entry.
- Dependency: P4.9c released and CI-passed; this owner-approved extension shared one audit/release boundary with P4.9d.
- Exact scope: authenticated full vocabulary route; active-Business Size and Color lists including inactive values; aliases visibly grouped under each canonical value; contextual canonical/alias creation; canonical rename; full explicit alias-list replacement; active/inactive toggle; safe return path from Product surfaces; server-side normalization, collision validation, atomic updates, and cross-Business isolation.
- Explicit exclusions: canonical deletion, automatic alias learning, silent synonym inference, canonical merge, ProductChoice row merge, Product Type/Tag/material vocabulary management, global dictionaries, bulk import/export, inventory, availability, and buyer-facing behavior.
- Acceptance criteria: the seller can see every Size/Color canonical value and its aliases; add and edit only the active Business vocabulary; rename without breaking ProductChoice foreign keys; replace/remove aliases atomically; deactivate a value without deleting existing choice truth; and receive field-level collision errors without partial writes.
- Verification: focused form/service/view ownership and atomicity tests, existing candidate-transfer tests, catalog tests, full Django suite, `git diff --check`, and owner/browser review on desktop and approximately 390px width.
- Proposed combined commit message: `feat: transfer candidates and manage choice vocabulary`.
- Status: PASSED — combined implementation with P4.9d was integrity-audited, owner-reviewed, released, remote-aligned, and CI-passed; exact delivery metadata remains Git/GitHub authority.

##### P4.9e Product Type and Tag Confirmation Attachment Baseline

- Objective: persist seller-confirmed Product Type and Tag candidates as Business-scoped Product truth.
- Dependency: P4.9d and P4.9d_expand released and CI-passed; any required Product association schema is explicitly reviewed before migration creation.
- Exact scope: approved Product-to-type/tag association boundary, explicit confirmation/correction, active-Business selection only, atomic persistence with the Product mutation, and retained observed/candidate context on errors.
- Explicit exclusions: automatic vocabulary creation from description text, alias learning, material confirmation, relations between products, readiness scoring, search UI, and buyer replies. Owner-approved Type/Tag vocabulary management is isolated in P4.9e_expand below.
- Acceptance criteria: only explicit seller confirmation writes associations; cross-Business vocabulary is rejected; candidates alone never attach; correction and removal are deterministic and tested.
- Verification: model/migration checks if required, focused form/service/view ownership tests, full Django suite, `git diff --check`, and owner/browser confirmation review.
- Proposed combined commit message: `feat: confirm and manage product classification`.
- Status: PASSED — combined with P4.9e_expand; integrity-audited, owner-reviewed, released, remote-aligned, and CI-passed; exact delivery metadata remains Git/GitHub authority.

##### P4.9e_expand Product Type and Tag Vocabulary Management Surface

- Objective: let the seller create and safely maintain the Business-scoped Product Type and Tag vocabulary required for usable recognition and explicit P4.9e confirmation.
- Dependency: P4.9e association and form boundaries are locally implemented; this owner-approved extension shares the P4.9e audit/release boundary.
- Exact scope: extend the authenticated Product vocabulary route with active-Business Product Type and Tag lists including inactive values; visibly grouped aliases; canonical and alias creation; canonical rename; full explicit alias-list replacement; activation/deactivation; safe Product-surface return paths; server-side normalization and collision validation; atomic updates; and cross-Business isolation.
- Explicit exclusions: canonical deletion or merge, automatic vocabulary or alias learning, material administration, Product Type/Tag readiness or search behavior, inventory, availability, and buyer replies.
- Acceptance criteria: the seller can create vocabulary before Product entry; only active values appear in new Product confirmation and recognition; existing confirmed Product references survive rename/deactivation and remain editable; alias replacement is atomic; and tampered/cross-Business mutations are rejected.
- Verification: local/test checks and migration checks; focused vocabulary, recognition, Product form/bundle/view, ownership, rollback, and reference-preservation tests; catalog tests; full Django suite; `git diff --check`; and owner/browser review.
- Proposed combined commit message: `feat: confirm and manage product classification`.
- Status: PASSED — combined with P4.9e; integrity-audited, owner-reviewed, released, remote-aligned, and CI-passed; exact delivery metadata remains Git/GitHub authority.

##### P4.9f Material Confirmation Attachment Baseline

- Objective: persist an explicitly confirmed material candidate through the existing confirmed `ProductMaterialFact` boundary.
- Dependency: P4.9e plus P4.9e_expand released and CI-passed; owner approved a compact inline confirmation section after recognition feedback, explicit candidate transfer into an unsaved row, and no material-alias model or automatic alias learning in this slice.
- Exact scope: explicit candidate-to-unsaved-row transfer plus confirm/correct/remove behavior for canonical material, optional approved percentage, original observed wording, source, confirmation state, Product, and active Business; atomic Product-form recovery on errors.
- Explicit exclusions: silent material writes, material-alias persistence or automatic alias learning, universal textile ontology, label OCR, image analysis, measurements, scientific composition inference, readiness, and buyer replies.
- Acceptance criteria: candidates stay transient until confirmation; persisted material facts preserve original wording and Business/Product scope; no unsupported composition claim is invented.
- Verification: focused material confirmation and ownership tests, error-recovery tests, full Django suite, `git diff --check`, and owner/browser confirmation review.
- Proposed commit message: `feat: confirm product material candidates`.
- Status: PASSED WITH NOTES — integrity-audited, locally verified, released, remote-aligned, CI-passed, and owner/browser accepted. Owner notes record broader Product create/edit UX dissatisfaction as later UX work, not a P4.9f technical blocker.

#### P4.10 Phase 4 Audit and Transition

- Objective: audit Phase 4 against `BUILD_PLAN.md` and `docs/domain/CLOTHING_DATA_SPEC_V1.md` before closing the semantic recognition and choice model phase.
- Dependency: P4.1 through P4.9 complete, released, aligned with remote, and latest relevant CI successful.
- Exact scope: audit Phase 4 against the refined roadmap and clothing spec; verify no measurement subsystem slipped in; verify no LLM truth, public catalog, orders, reservations, payments, delivery, or broad ERP scope; verify tests/checks/CI evidence; update `changelog_checkpoint.md` for phase closure only if criteria pass.
- Explicit exclusions: new feature implementation, model changes, migrations, UI changes, README changes unless public factuality requires it, frozen-doc changes without owner approval, deployment work, and post-push documentation-only slice creation for routine CI success.
- Likely files: `changelog_checkpoint.md` only if phase/gate closure criteria pass; `DEVELOPMENT_NOTES.md` only if a meaningful audit decision or workaround is recorded; `BUILD_PLAN.md` only if roadmap or gate criteria change.
- Backend acceptance criteria: all Phase 4 tests/checks pass; choice truth, material truth, Product Type/Tag vocabulary, alias scoping, and confirmed-fact boundaries match the clothing spec; no unresolved Phase 4 blocker remains; buyer replies consume no unconfirmed candidates.
- Frontend/UX acceptance criteria where relevant: create/edit recognition and choice validation remain compact, mobile-reviewable, accessible at baseline, and do not create a giant clothing form.
- Automated verification: Django system check, migration dry-run check, focused Phase 4 tests, full Django test suite, `git diff --check`, Git branch/remote alignment check, latest relevant GitHub Actions result.
- Manual user verification where UI changes: owner confirms create/edit recognition flow, compactness, validation recovery, and no unapproved measurement or buyer-reply UI if those surfaces changed.
- Failure cases: tests fail; CI fails or is pending; working tree is dirty; Phase 4 scope includes measurements, public catalog, chatbot, orders, reservations, payments, delivery, broad ERP, or LLM truth; buyer replies consume unconfirmed candidates; choice bundle validation permits partial invalid state.
- Documentation updates: update `changelog_checkpoint.md` for Phase 4 closure only when closure criteria pass; no routine post-push documentation sync; no new `.1 Post-Push...` micro-slice.
- Proposed commit message: `chore: audit phase 4 semantic recognition`.
- Rollback/recovery note: if audit fails, record the real blocker and recovery requirement instead of marking Phase 4 passed.
- Stop gate relation: closes Phase 4 only after all criteria pass; Gate 3 remains open until Phase 5 inventory and computed-availability criteria also pass.
- Status: PASSED — the code-first scope/integrity audit, focused 240-test catalog/Phase 4 suite, full 278-test regression suite, Django checks, migration checks, local Git drift checks, release, and exact-SHA CI passed without source repair.

### Phase 5: Inventory and Computed Availability

- Objective: centralize quantity mutations and availability computation.
- Dependency: Phase 4.
- Scope boundary: inventory service, adjustment ledger, +1/-1 and owner-approved direct set, computed availability, concurrency strategy.
- Current implementation state: `IN_PROGRESS`; P5.1 through P5.6 are released and exact-SHA CI-passed. Owner review confirmed P5.6 functional correctness and identified the save-before-stock workflow as the remaining quantity-management UX defect. Owner-approved P5.6A will let a seller enter starting stock for unsaved choices in the same final Product create/edit submission while retaining persisted choice identity, centralized mutation, and immutable adjustment truth. P5.7 remains a no-new-behavior transition/regression slice after P5.6A closes.
- Expected micro-slices: P5.1 availability baseline, P5.2 adjustment-ledger baseline, P5.3 atomic mutation service, P5.4 ProductBundle stock boundary, P5.5 stock route, P5.6 HTMX stock response/controls, P5.6A one-save initial-stock capture, and P5.7 transition/regression readiness before the Phase 5 audit and Gate 3 closure.
- Stop gate: all stock changes go through one service and create a complete audit trail.

#### P5.1 Pure Product Availability Service Baseline

- Objective: provide one Business-scoped, side-effect-free service that computes Product availability from approved lifecycle and choice-level stock truth.
- Dependency: Phase 4 `PASSED`.
- Scope boundary: add the `inventory` app boundary and `compute_product_availability(*, business, product)`; return available only for an active Product with at least one active, positive-quantity choice owned by the active Business; reject Business/Product mismatch; never store availability or mutate state.
- Explicit exclusions: quantity mutation, adjustment ledger, direct stock set, stock routes or HTMX UI, Product form changes, totals, readiness, buyer replies, reservations, orders, measurements, and LLM interpretation.
- Source whitelist: `config/settings/base.py`, `inventory/__init__.py`, `inventory/apps.py`, `inventory/availability.py`, and `inventory/tests.py`.
- Backend acceptance criteria: active Product plus an active positive-quantity owned choice returns true; draft, no-choice, zero-only, and inactive-only cases return false; unrelated Product stock cannot affect the result; cross-Business Products are rejected; computation performs no writes.
- UX acceptance criteria: none; this slice has no route, template, HTMX, or Alpine behavior.
- Automated verification: Django system check; migration dry-run and migration-state checks; focused availability tests; Product choice/bundle regression tests; full PostgreSQL-backed Django suite; diff checks.
- Manual owner verification: not required for this backend-only slice.
- Failure cases: stored availability, lifecycle mutation, quantity mutation, cross-Business reads, unrelated Product choices affecting the result, a model/migration change, or any excluded later-phase behavior.
- Documentation updates: `changelog_checkpoint.md` always; `BUILD_PLAN.md` for Phase 5 transition and the approved slice contract; `README.md` for material public-status accuracy; no frozen-document, UX-plan, or decision-log update.
- Proposed commit message: `feat: add product availability service`.
- Rollback/recovery note: remove the app registration and service/tests together if the audited release cannot proceed; do not leave an undocumented partial boundary.
- Stop gate relation: establishes computed availability only; it does not centralize stock mutation, create the adjustment audit trail, or pass Gate 3.
- Status: `CLOSED` after release, remote alignment, and exact-SHA CI success; delivery metadata remains in Git/GitHub.

#### P5.2 Business-Scoped Inventory Adjustment Ledger Baseline

- Objective: establish an append-only audit fact for one exact ProductChoice quantity transition without introducing stock mutation behavior.
- Dependency: P5.1 `CLOSED`.
- Scope boundary: add `InventoryAdjustment` with Business, exact ProductChoice, authenticated Business-owner actor, before/after quantities, nonzero delta, and creation timestamp; validate tenant and actor ownership; protect referenced history; enforce nonnegative and arithmetically consistent transitions in PostgreSQL; block application-level updates and deletes.
- Explicit exclusions: changing ProductChoice quantity, mutation/concurrency service, Product-bundle integration, direct stock set, reason codes, stock routes or HTMX UI, totals, availability changes, readiness, buyer replies, reservations, and orders.
- Source whitelist: `inventory/models.py`, `inventory/migrations/__init__.py`, `inventory/migrations/0001_initial.py`, and `inventory/tests.py`.
- Backend acceptance criteria: valid owned transitions persist against one distinct choice row; cross-Business choice or actor is rejected; before/after quantities are nonnegative, delta is nonzero, and `after = before + delta`; protected references and model/queryset guards preserve history; adjustment creation performs no stock write.
- UX acceptance criteria: none; this slice has no route, template, HTMX, or Alpine behavior.
- Automated verification: Django system and migration checks; focused inventory availability/ledger tests; ProductChoice and ProductBundle regressions; full PostgreSQL-backed Django suite; diff checks.
- Manual owner verification: not required for this backend-only slice.
- Failure cases: cross-Business ledger facts, ambiguous choice aggregation, inconsistent transition arithmetic, mutable/deletable application records, ProductChoice quantity mutation, reason-code policy, direct-set policy, or any excluded later-phase behavior.
- Documentation updates: `changelog_checkpoint.md` always; `BUILD_PLAN.md` for the formal slice contract; `DEVELOPMENT_NOTES.md` for the durable ledger-shape/immutability decision; `README.md` to remove a now-false public statement that the ledger has not started; no UX-plan or frozen-document update.
- Proposed commit message: `feat: add inventory adjustment ledger`.
- Rollback/recovery note: reverse the new inventory migration and remove the model/tests together if the audited release cannot proceed; no existing catalog row is transformed by this initial ledger migration.
- Stop gate relation: establishes audit-record integrity only; it does not centralize or serialize stock writes, automatically create ledger records, resolve direct set, or pass Gate 3.
- Status: `CLOSED` after release, remote alignment, and exact-SHA CI success; delivery metadata remains in Git/GitHub.

#### P5.3 Atomic Inventory Increment/Decrement Service

- Objective: centralize one safe stock increment/decrement path that records the corresponding immutable adjustment fact.
- Dependency: P5.2 `CLOSED` and P5.1 availability service `CLOSED`.
- Scope boundary: add `apply_choice_quantity_delta(*, business, choice, actor, delta)` for exactly `+1` or `-1`; lock the current owned ProductChoice row; reject invalid, unsaved, cross-Business, non-owner, and underflow requests; save quantity and `InventoryAdjustment` atomically; return the locked choice, adjustment, and computed availability.
- Explicit exclusions: direct stock set, arbitrary deltas, reason codes, Product-bundle integration, routes, HTMX/UI, totals, readiness, buyer replies, reservations, orders, lifecycle mutation, and `is_active` mutation.
- Source whitelist: `inventory/mutations.py` and `inventory/tests.py`.
- Backend acceptance criteria: only integer `+1`/`-1` deltas are accepted; the locked quantity transition and immutable ledger fact commit together; any ledger failure rolls back the quantity write; Business and actor ownership remain enforced; computed availability reflects the committed choice-level quantity without storing availability or changing lifecycle/activation; concurrent decrements serialize without lost updates or duplicate transition facts.
- UX acceptance criteria: none; this slice has no route, template, HTMX, or Alpine behavior.
- Automated verification: focused inventory suite, migration-order/concurrency reproducer, full PostgreSQL-backed Django suite, Django system and migration checks, and diff checks.
- Manual owner verification: not required for this backend-only slice.
- Failure cases: direct quantity writes outside this service, cross-Business mutation, stale/lost concurrent update, quantity/ledger divergence, arbitrary delta or reason-code policy, lifecycle/activation mutation, stock route/UI scope, or any excluded later-phase behavior.
- Documentation updates: `changelog_checkpoint.md` always; `BUILD_PLAN.md` for the formal slice contract and Phase 5 state; `DEVELOPMENT_NOTES.md` for the atomic/concurrency boundary or reusable migration-test isolation lesson; `README.md` for material public-status accuracy; no UX-plan or frozen-document update.
- Proposed commit message: `feat: add atomic inventory delta service`.
- Rollback/recovery note: remove the service and focused tests together if the audited release cannot proceed; preserve the P5.1 availability and P5.2 ledger boundaries.
- Stop gate relation: centralizes the first quantity mutation and ledger pairing but does not complete stock UI, workspace behavior, or Gate 3.
- Status: `CLOSED` after release, remote alignment, and exact-SHA CI success; delivery metadata remains in Git/GitHub.

#### P5.4 ProductBundle Stock Boundary Enforcement

- Objective: prevent ProductBundle editing from becoming a second stock-mutation path while preserving choice identity, activation, and ProductBundle transaction safety.
- Dependency: P5.3 `CLOSED`.
- Scope boundary: force new ProductChoice rows to quantity zero without creating an adjustment; preserve existing quantities by excluding stock from persisted ProductBundle updates; reject persisted choice deletion while retaining deactivation; allow unsaved extra-row discard; keep Business/Product validation and atomic Product, choice, material, and tag persistence intact.
- Explicit exclusions: direct stock set, arbitrary deltas, reason codes, inventory mutation calls from ProductBundle, stock route, HTMX response, dashboard, readiness, buyer replies, reservations, orders, and deployment work.
- Source whitelist: `catalog/forms.py`, `catalog/product_bundles.py`, `catalog/tests.py`, and `templates/catalog/_choice_section.html`.
- Acceptance: new choices persist with quantity zero and no adjustment; stale or forged quantity submissions cannot change existing stock; persisted choices cannot be deleted and must be deactivated instead; unsaved rows can be discarded; quantity is visibly read-only; Business isolation, choice identity, lifecycle separation, and existing ProductBundle regressions remain green.
- Status: `CLOSED` after owner/browser acceptance, release, remote alignment, and exact-SHA CI success; delivery metadata remains in Git/GitHub.

#### P5.5 Authenticated Stock Mutation Route

- Objective: expose a seller-authenticated, Business-scoped route for one approved choice-level stock increment/decrement action.
- Dependency: P5.4 `CLOSED`.
- Scope boundary: add one CSRF-protected, POST-only route at the inventory boundary; accept only exact `+1` or `-1`; resolve Business and actor from the authenticated request; fetch the exact choice within that Business; call `apply_choice_quantity_delta`; and redirect through a validated internal `next` value or Product-list fallback with server success/error messages.
- Explicit exclusions: direct-set UI, arbitrary quantity input, reason codes, dashboard, public catalog, buyer replies, and new architecture/dependencies.
- Source whitelist: `inventory/urls.py`, `inventory/views.py`, `inventory/tests.py`, and `config/urls.py`.
- Acceptance: authenticated owner can mutate only an owned ProductChoice and each accepted request creates one exact quantity/ledger transition; unauthenticated, GET, CSRF, cross-Business, invalid delta, underflow, missing-Business, and unresolved multiple-Business requests are rejected without writes; external return URLs cannot escape the application; success/error redirects preserve server truth and safe navigation.
- Automated verification: focused route/security tests, complete inventory service regression, Django system and migration dry-run checks, full PostgreSQL-backed suite, and diff checks.
- Manual owner verification: advisory because no visible stock-control surface is added; P5.6 owns browser-visible interaction acceptance.
- Status: `CLOSED` after release, remote alignment, and exact-SHA CI success; delivery metadata remains in Git/GitHub.

#### P5.6 HTMX Stock Response and Controls

- Objective: add the approved server-rendered HTMX response and compact choice-level control surface for the stock route.
- Dependency: P5.5 `CLOSED` and owner-approved UX responsibility for the affected surface.
- Scope boundary: owner-approved compact `+1`/`-1` controls beside persisted choices on Product edit only; retain the disabled quantity input and no-control unsaved rows; use the existing CSRF-protected stock route for both HTMX and native submit; replace only the affected control region with server truth plus loading/recovery feedback and accessible labels.
- Explicit exclusions: workspace/dashboard redesign, client-owned stock state, Alpine replacement of server truth, direct set, reason codes, and unrelated UX cleanup.
- Source whitelist: `inventory/views.py`, `inventory/tests.py`, `templates/inventory/_choice_stock_controls.html`, `templates/catalog/_choice_section.html`, `catalog/tests.py`, and `static/css/app.css`.
- Acceptance: only persisted choices render controls; the stock input remains disabled; each control sends one exact delta through P5.5 and cannot choose Business or actor; HTMX success/error responses replace only the correct Business-scoped choice state with current server quantity and accessible status/alert feedback; both controls disable while a request is pending; native fallback preserves the safe return path; unsaved and cross-Business choices gain no control; lifecycle, availability, and adjustment-fact truth remain unchanged except through the established service.
- Automated verification: focused HTMX increment/underflow/invalid-delta tests; route plus Product create/edit regression; complete inventory suite; Django system and migration dry-run checks; full PostgreSQL-backed suite; diff checks.
- Manual owner verification: required — on Product edit, confirm the quantity input stays read-only; `+1` and `-1` update a saved choice in place and persist after refresh; decrement at zero shows an inline error with no quantity change.
- Owner-observed UX limitation: functional behavior passed, but requiring a new Product or newly added choice to be saved at zero before quantity can be increased creates an inconvenient two-step workflow that does not meet the intended modern assistant-style UX. P5.6A owns the approved correction before Phase 5 audit/Gate 3 closure while preserving persisted choice identity, centralized mutation, and immutable adjustment truth.
- Status: `CLOSED` after owner/browser acceptance with the save-before-stock UX limitation transferred to P5.6A, release, remote alignment, and exact-SHA CI success; delivery metadata remains in Git/GitHub.

#### P5.6A One-Save Initial Stock Capture

- Objective: let the seller set starting stock for every new choice during the same final Product create/edit save, removing the mandatory save-then-adjust workflow.
- Dependency: P5.6 `CLOSED` and the owner-approved P5.6A interaction boundary.
- UX contract: only an unsaved choice row exposes an editable `Starting stock` non-negative integer field, defaulting to zero, with concise guidance that later changes use the saved choice's `-1`/`+1` controls. Existing choices retain read-only current quantity and the P5.6 controls. Entered starting stock survives server validation errors and no-write recognition, candidate-transfer, and contextual-vocabulary interactions. One Product submit remains the only completion action; no intermediate save is required.
- Functional boundary: validate the complete ProductBundle before writes; inside its existing atomic transaction, persist each new Business-scoped ProductChoice at zero and then pass any positive starting stock, the persisted choice, active Business, and authenticated actor to a dedicated one-time operation in the centralized inventory mutation boundary. That operation must lock and re-resolve the exact choice, require zero current quantity and no adjustment history, and create one immutable `0 -> N` InventoryAdjustment before returning server truth. A zero start creates no adjustment because no stock transition occurred. Any initialization failure rolls back Product, choices, tags, materials, quantities, and adjustment facts together.
- Integrity boundary: initial stock is a creation-only transition, not direct set. No public initialization route is added; persisted quantity remains excluded from ProductBundle updates; forged existing-row quantity is ignored; subsequent mutations remain exact `-1`/`+1` actions through P5.5/P5.6; Business, actor, choice identity, lifecycle, computed availability, and ledger ownership remain server-controlled.
- Explicit exclusions: editable/direct-set quantity for saved choices, arbitrary subsequent deltas, optimistic/client-owned stock, repeated synthetic `+1` writes to reach starting stock, bulk inventory, reason codes, orders/reservations, workspace redesign, schema changes, migrations, and new dependencies.
- Source whitelist: `catalog/forms.py`, `catalog/product_bundles.py`, `catalog/views.py`, `catalog/tests.py`, `inventory/mutations.py`, `inventory/tests.py`, `templates/catalog/_choice_section.html`, and `static/css/app.css` only if required for the approved field hierarchy/mobile layout.
- Acceptance: Product create and Product edit-with-new-choice each accept zero or positive starting stock in one final save; a positive value produces the exact saved quantity and one Business/choice/actor-scoped immutable `0 -> N` fact; zero produces quantity zero and no fact; multiple new choices retain distinct quantities/facts; negative, non-integer, forged, wrong-Business, wrong-actor, nonzero-current, or previously-adjusted initialization attempts make no partial write; existing quantities and P5.6 controls behave unchanged; invalid forms preserve entered values; no-write HTMX helper actions preserve input without stock/ledger writes; availability is computed from committed server truth.
- Automated verification: focused initialization-service precondition/rollback tests; Product create and edit integration for positive/zero/multiple/invalid starting stock; existing-row forgery and Business-isolation tests; preview/transfer/vocabulary no-write and value-preservation regression; P5.4 ProductBundle, P5.5 route, P5.6 HTMX controls, availability, adjustment-ledger, and concurrency regressions; Django system and migration dry-run checks; full PostgreSQL-backed suite; diff checks.
- Manual owner verification: required — create a Product with starting stock greater than zero and add another stocked choice to an existing Product, each with one save; confirm the saved quantities immediately show P5.6 controls, persist after refresh, and still change through `-1`/`+1`; also confirm invalid input stays visible with an inline error and creates nothing.
- Documentation on acceptance: checkpoint always; retire the active P5.6 UX-gap note in the UX plan and Build Plan only after owner/browser PASS; record the one-time-initialization decision in Development Notes; update README only when implementation and verification make the one-save behavior public reality.
- Status: `PLANNED`.

#### P5.7 Inventory Transition and Regression Readiness

- Objective: prove the complete Phase 5 stock boundary and prepare the evidence required for the Phase 5 audit and Gate 3 transition.
- Dependency: P5.4, P5.5, P5.6, and P5.6A `CLOSED`.
- Scope boundary: integrated Business-isolation, increment/decrement and one-time initialization mutation, ledger, availability, ProductBundle, route, HTMX, concurrency, rollback, and regression coverage; no new product behavior.
- Explicit exclusions: new inventory policy, direct-set approval, reason-code policy, orders, reservations, deployment, and broad UX redesign.
- Source whitelist: directly related source/tests from P5.4–P5.6A only; governance docs are updated in Prompt 4 after acceptance.
- Acceptance: all stock writes use the centralized service; every accepted transition has one immutable fact; availability remains computed; full PostgreSQL regression and targeted route/HTMX checks pass; Gate 3 evidence is complete for audit.
- Status: `PLANNED`.

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

Documentation stores stable project truth. Git and GitHub store exact delivery metadata such as commit hashes, remote alignment, CI run IDs, and CI conclusions.

| Change Type | changelog_checkpoint.md | BUILD_PLAN.md | APP_EXPERIENCE_PLAN.md | DEVELOPMENT_NOTES.md | Frozen Docs | README.md |
|---|---|---|---|---|---|---|
| Normal commit/push/CI success | No documentation update by default | No | No | No | No | No |
| Failure, divergence, or blocker | Update current blocker, recovery state, or handoff | Update only if roadmap, dependency, gate, scope, stop condition, or verification strategy changed | Update only if UX contract changed | Record meaningful trade-off or workaround if useful | No automatic edits | Fix only if public factuality changed |
| Phase or gate closure | Update current phase/gate state and next functional micro-slice | Update affected phase/gate state | Update only if UX evidence changes | Record lesson only if meaningful | No automatic edits | Update only if public status changed |
| Deployment, demo, or public release change | Update deployment/demo/release state | Update Gate 6 or Gate 7 state if relevant | Update demo UX verification if needed | Record provider trade-off if meaningful | No automatic edits | Add or correct public facts only after verification |
| Owner scope or strategy decision | Update blocker/current phase | Update affected phase or owner decisions | Update only if UX contract changes | Record meaningful trade-off if useful | Update only with owner approval | Usually no |
| Public factuality correction | Update if it affects handoff | Update only if it affects execution strategy | Update only if UX contract changes | Record decision only if it changes future behavior | Owner-approved amendment only | Correct immediately |

Routine successful Release completion must not create a documentation-only post-push cycle. `BUILD_PLAN.md` itself must not be updated for every normal slice completion unless roadmap, dependency, gate, scope, stop condition, or verification strategy changed.

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

- Final public project/repository name.
- License choice.
- Future material vocabulary/alias maintenance policy beyond P4.9f.
- Detailed measurement micro-slice timing, including measurement type, value, unit, method, and product/choice boundary.
- Whether fit guidance appears in a later approved measurement/fit micro-slice.
- Whether Product Detail remains in Portfolio V1.
- Whether product relations are V1 or deferred.
- Whether clone and archive/restore are V1.
- Exact clone stock-copy policy.
- Whether tags affect readiness or only organization/search.
- Price policy for zero, null, missing, and free products.
- Direct stock set placement.
- Dashboard first-viewport priority.
- Ready reply placement.
- Final Georgian terminology.
- Deployment provider and demo access model.
- Demo media strategy and reset cadence.
