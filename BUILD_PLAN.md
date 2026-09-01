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
| Phase 5 | Inventory and Computed Availability | Centralize stock mutations and computed availability | PASSED | Gate 3 | Inventory service tests and ledger tests |
| Phase 6 | Operational Product Workspace | Build seller product workspace with compact product cards | IN_PROGRESS | Gate 4 | Workspace UI, HTMX stock checks, UX audit notes |
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
- Current dependency state: Gate 1, Gate 2, and Gate 3 are passed. P2.1 through P2.5 and the Environment-Gated Demo Seller Access Bootstrap are released and `PASSED`; Phase 3, Phase 4, and Phase 5 are `PASSED`.
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
- Current implementation state: Phase 4 and Phase 5 are `PASSED`. P4.1 through P4.9f, including P4.9d_expand and P4.9e_expand, are released, owner-reviewed, and `PASSED`; P4.10 passed its code-first scope/integrity audit, local PostgreSQL verification, release, and exact-SHA CI without source repair. P5.1 through P5.8 are released, owner-reviewed where required, integrity-audited, and exact-SHA CI-passed; Gate 3 is `PASSED`. Phase 6 is `IN_PROGRESS`: P6.1 through P6.6 and P6.7a are `CLOSED`, P6.7 is `IN_PROGRESS`, and P6.7b is approved awaiting implementation after the governance release. The Workspace is now the first availability UI consumer; readiness and buyer replies do not exist, and exact delivery metadata remains Git/GitHub authority.
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
- Stop gate relation: Phase 4 closed after its criteria passed; Gate 3 passed only after the Phase 5 inventory and computed-availability criteria also passed.
- Status: PASSED — the code-first scope/integrity audit, focused 240-test catalog/Phase 4 suite, full 278-test regression suite, Django checks, migration checks, local Git drift checks, release, and exact-SHA CI passed without source repair.

### Phase 5: Inventory and Computed Availability

- Objective: centralize quantity mutations and availability computation.
- Dependency: Phase 4.
- Scope boundary: inventory service, adjustment ledger, +1/-1 and owner-approved direct set, computed availability, concurrency strategy.
- Current implementation state: `PASSED`; P5.1 through P5.8 are released and exact-SHA CI-passed. P5.8 closed the two boundary gaps found by the code-first audit, and the Phase 5/Gate 3 transition is complete.
- Expected micro-slices: P5.1 availability baseline, P5.2 adjustment-ledger baseline, P5.3 atomic mutation service, P5.4 ProductBundle stock boundary, P5.5 stock route, P5.6 HTMX stock response/controls, P5.6A one-save initial-stock capture, P5.7 transition/regression readiness, and audit-required P5.8 inventory boundary hardening before the Phase 5/Gate 3 closure.
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
- Owner-observed UX limitation: resolved by P5.6A's one-save starting-stock flow; the broader Product create/edit surface still remains a later assistant-style UX improvement area.
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
- Documentation on acceptance: checkpoint always; retire the resolved P5.6 UX-gap note in the UX plan and Build Plan after owner/browser PASS; retain the one-time-initialization decision in Development Notes; update README because the one-save behavior is now public reality.
- Status: `CLOSED` after owner/browser acceptance, release, remote alignment, and exact-SHA CI success; delivery metadata remains in Git/GitHub.

#### P5.7 Inventory Transition and Regression Readiness

- Objective: prove the complete Phase 5 stock boundary and prepare the evidence required for the Phase 5 audit and Gate 3 transition.
- Dependency: P5.4, P5.5, P5.6, and P5.6A `CLOSED`.
- Scope boundary: integrated Business-isolation, increment/decrement and one-time initialization mutation, ledger, availability, ProductBundle, route, HTMX, concurrency, rollback, and regression coverage; no new product behavior.
- Explicit exclusions: new inventory policy, direct-set approval, reason-code policy, orders, reservations, deployment, and broad UX redesign.
- Source whitelist: `catalog/tests.py`; governance docs are updated in Prompt 4 after acceptance.
- Acceptance: the integrated Product create → one-save initialization → authenticated HTMX `-1/+1` transition path produces one ordered immutable fact per transition; availability flips only at the computed quantity boundary; lifecycle and activation remain unchanged; cross-Business mutation is rejected without writes; focused Phase 5 and full PostgreSQL regressions pass.
- Automated verification: integrated transition test 1/1; focused Phase 5 regression 113/113; complete inventory suite 46/46; full PostgreSQL suite 336/336; Django system check, migration dry-run, and diff checks pass.
- Manual owner verification: advisory — create with starting stock `2`, decrement to `0`, increment to `1`, and refresh to confirm persisted server truth.
- Post-CI governance closure: completed in the allowed governance docs after successful P5.7 exact-SHA CI; no new functional slice was created.
- Status: `CLOSED` after release, remote alignment, exact-SHA CI success, and governance closure; no production source changes.

#### P5.8 Inventory Boundary Hardening

- Objective: close the ORM batch-isolation and quantity-overflow gaps found by the Phase 5 code-first audit before Gate 3 transition.
- Dependency: P5.7 `CLOSED` and owner approval of the audit recovery plan.
- Scope boundary: validate every pending InventoryAdjustment bulk-create row against Business/choice/actor ownership before any insert; reject bulk conflict modes that could hide or rewrite immutable facts; validate one-time initialization and `+1` results against the configured ProductChoice quantity storage range before any stock or ledger write; preserve the existing route/HTMX `ValidationError` recovery path.
- Explicit exclusions: direct stock set, arbitrary subsequent deltas, reason codes, new stock routes or UI, workspace behavior, schema/migrations, dependencies, orders, reservations, and lifecycle/availability policy changes.
- Source whitelist: `inventory/models.py`, `inventory/mutations.py`, and `inventory/tests.py`; governance docs are synchronized after local acceptance.
- Acceptance: a mixed valid/cross-Business or wrong-actor bulk batch creates no facts; conflict-ignore/update modes cannot suppress or mutate ledger history; initialization above the storage range and `+1` at the maximum return controlled validation errors with unchanged quantity and no fact; HTMX returns authoritative current controls instead of a server error; existing arithmetic constraints, atomicity, concurrency, Business isolation, lifecycle separation, and computed availability remain green.
- Automated verification: complete inventory suite 52/52; full PostgreSQL suite 342/342; Django system check, migration dry-run, unapplied-migration check, and diff checks pass with no schema change.
- Manual owner verification: not required; this backend hardening adds no interaction and preserves the owner-accepted P5.6A/P5.7 workflow.
- Post-CI governance closure: completed after successful P5.8 exact-SHA CI in the allowed governance documents; Phase 5 and Gate 3 are `PASSED`.
- Proposed commit message: `fix: harden inventory integrity boundaries`.
- Status: `CLOSED` after release, remote alignment, exact-SHA CI success, and the Phase 5/Gate 3 governance transition.

### Phase 6: Operational Product Workspace

- Refined objective: turn the existing authenticated Product list into the seller's mobile-first daily operational cockpit for finding one Product, understanding its lifecycle and computed availability, inspecting exact choice stock, making approved +1/-1 stock changes, and returning from correction work without losing Workspace context.
- Dependency and current state: Phase 5 and Gate 3 are PASSED; the Product core, confirmed classification/material/choice truth, one-save initial stock, centralized subsequent stock mutation, immutable adjustment history, and computed availability are released. Phase 6 is IN_PROGRESS; P6.1 through P6.6 and P6.7a are CLOSED, P6.7 is IN_PROGRESS, and P6.7b is approved awaiting implementation after the governance release.
- Scope boundary: authenticated Business-scoped server-rendered Product listing, compact operational cards, exact-choice stock controls, deterministic search, owner-approved bounded filters, canonical URL/query state, explicit edit return paths, HTMX server-truth refresh, Phase 6 empty/loading/error/recovery states, mobile-first behavior, accessibility baseline, and a Phase 6-specific UX/regression gate.
- Source-of-truth boundary: Product lifecycle remains stored and separate from computed availability; ProductChoice remains the quantity owner; duplicate same-size/color choices remain distinct identities; all subsequent quantity writes continue through the released Phase 5 inventory route and mutation service; no client state may own quantity, availability, lifecycle, Business scope, or confirmed facts.
- Cross-phase firewall: no Dashboard or attention queue, readiness, buyer-question coverage, ready reply, Product Detail dependency, clone, archive/restore, direct stock set, arbitrary quantity mutation, reason codes, bulk stock editing, Product relations, measurements, fit guidance, media expansion, analytics, public buyer behavior, chatbot, LLM interpretation, orders, reservations, payments, or delivery.
- Owner-decision boundary: the owner approved the exact P6.5 set as stored lifecycle plus computed availability. Product Type and Tag filters remain excluded unless a later bounded change is separately approved. Phase 6 does not depend on any other unresolved optional feature.
- Delivery order: P6.1 establishes the Workspace/query boundary; P6.2 establishes truthful compact cards; P6.3 makes exact choice stock actionable through a truthful full-page fallback; P6.4 adds retrieval by search; P6.5 adds only the approved bounded filters; P6.6 adds coherent HTMX results refresh; P6.7 performs the Phase 6-only UX, navigation, accessibility, and regression gate through P6.7a first-viewport/mobile repair, P6.7b canonical return-path hardening, P6.7c accessibility/recovery hardening, and the P6.7d integrated closure gate.

#### P6.1 Product Workspace Route and Query Baseline

- Objective: establish a stable authenticated, Business-scoped Product Workspace read boundary at /products/ with deterministic server-rendered results and explicit Workspace return context.
- Dependency: Phase 5 and Gate 3 PASSED; no Phase 6 slice is required.
- Why this slice exists: the current Product list proves authentication and ownership isolation but has no dedicated query-state boundary or reusable results surface for cards, search, filters, and coherent later refreshes.
- Seller job / user value: open Products and immediately see the seller's own catalog or one useful empty-state action without an implicit Business selection, unrelated data, or route ambiguity.
- Exact scope: preserve the existing /products/ route and active navigation; introduce one Product Workspace query/read helper; render a Workspace shell plus reusable results partial; apply explicit deterministic name-then-id ordering; preserve no-Business, unsupported-multiple-Business, and true empty-catalog states; generate a canonical internal Workspace return URL for Add/Edit links; keep the existing simple identity rows until P6.2.
- Backend responsibilities: resolve the active Business once through the released selector; apply Business filtering before all other Product query work; expose a small typed/validated Workspace state contract that later slices can extend; discard unsupported query keys from generated Workspace return context; keep the view thin and side-effect free.
- UI/UX responsibilities: make Products visibly current in global navigation; place the page identity and Add Product action before secondary vocabulary management; show the first result or the appropriate empty state early; provide one useful Add Product recovery action when the Business has no Products.
- Data/state/source-of-truth boundaries: read Product identity and stored lifecycle only in this baseline; do not compute new product state, mutate Product/choice data, or infer readiness, availability labels, candidate facts, or later-phase signals.
- Business isolation requirements: an authenticated seller may query only Products owned by the one resolved active Business; another Business's Product must never render through path or query tampering; no Business is created on GET; the unresolved multiple-Business state remains an explicit 409 policy block.
- Navigation / return-path contract: Add Product and each baseline Edit action receive a canonical safe /products/ return URL; cancel and successful Product save return to that URL; browser Back is not the primary path; an external or non-Workspace return target falls back safely.
- HTMX contract where relevant: none in P6.1; the results partial is created as a server-rendered boundary for later use, while the accepted behavior remains a normal full-page GET.
- Alpine contract where relevant: none; no local interaction state is required.
- Mobile-first requirements: at approximately 390px, the heading, primary Add action, and first result or empty-state recovery appear without horizontal page scrolling; primary and secondary page actions wrap rather than create an uncontrolled horizontal row.
- Accessibility requirements: retain semantic main/section/heading/list structure, active navigation with aria-current, link semantics for navigation, visible keyboard focus, and role status/alert semantics for no-Business and policy-blocked states.
- Performance/query considerations: use one Business-first Product queryset with explicit deterministic ordering; do not add per-Product queries; do not introduce pagination or a hidden result cap without owner approval; record unbounded-list scaling as a later risk rather than silently hiding Products.
- Explicit exclusions: rich Product cards, choice display, computed availability, stock controls, search, filters, result counts, HTMX behavior, Dashboard, and any unresolved Product action.
- Likely source whitelist: catalog/workspace.py, catalog/views.py, templates/catalog/product_list.html, templates/catalog/_product_results.html, static/css/app.css, and catalog/test_workspace.py; catalog/urls.py only if preserving the existing route name requires a direct correction.
- Backend acceptance criteria: anonymous GET redirects to login; a one-Business seller receives 200; no-Business receives 200 without a write; multiple Businesses receive 409 without implicit selection; only owned Products are returned; ordering is stable for equal and unequal names; unsupported query keys do not survive the canonical return URL.
- UI/UX acceptance criteria: the Workspace clearly identifies itself; the current Product navigation state is exposed; true catalog-empty state is distinct from ownership-policy states; Add Product is the single recovery action in the empty catalog; a 390px viewport has no horizontal page overflow.
- Automated verification: focused view/query tests for authentication, Business isolation, no-Business behavior, multiple-Business policy, deterministic ordering, canonical return context, unsupported/tampered query parameters, template selection, and empty state; run the existing Product list and Product create/edit return-path regressions.
- Manual owner/browser verification: advisory — inspect populated, empty-catalog, and no-Business states on desktop and approximately 390px mobile; follow Workspace to Add/Edit and return without browser Back.
- Failure cases: unsupported active-Business policy returns the existing explicit block; malformed or unknown query input cannot expand scope and is removed from canonical state; an unsafe return target uses /products/; template failure must not mutate data.
- Regression risks: changing current Product ordering, losing the active navigation marker, breaking existing Product list tests, or weakening create/edit next handling.
- Documentation update expectations: changelog_checkpoint.md after acceptance and BUILD_PLAN.md for the real slice status transition; no DEVELOPMENT_NOTES.md, APP_EXPERIENCE_PLAN.md, or README.md change is expected unless implementation reveals a material contract change.
- Proposed commit message: feat: establish product workspace query baseline
- Rollback/recovery note: revert the query helper and Workspace template/result split together; no schema, migration, dependency, or persisted data rollback is required.
- Stop gate relation: opens the Phase 6 delivery sequence but does not satisfy the Product card, stock, retrieval, HTMX, accessibility, or owner UX stop conditions.
- Status: CLOSED; released and exact-SHA CI-passed.

#### P6.2 Compact Product Card and Availability Baseline

- Objective: give each Product a compact operational card that separates stored lifecycle from computed availability and exposes enough exact choice truth for a seller to decide what to inspect or correct.
- Dependency: P6.1 CLOSED.
- Why this slice exists: Phase 6 is the first UI consumer of computed availability, and the seller needs more than a name/lifecycle row before stock work can safely move into the Workspace.
- Seller job / user value: identify a Product in seconds, distinguish whether it is enabled from whether it has sellable stock, inspect active choice quantities, and reach one obvious correction action without opening a new Product Detail surface.
- Exact scope: add a reusable Product card partial with Product name, a compact description excerpt, optional confirmed Product Type label, separately named Lifecycle and Availability states, active-choice count, active-choice total stock, compact read-only active choice rows, inactive-choice count, and one Edit/correction link. Each active row shows stable Choice #id, canonical size, canonical color, and authoritative quantity. Tags and material are deliberately omitted from the card baseline because they do not earn first-card space for routine stock decisions.
- Backend responsibilities: build one reusable card read model from the Business-scoped Product queryset; prefetch ProductChoice rows with size/color and select Product Type; compute active total and availability through the shared inventory availability boundary or a shared read adapter rather than template logic; ensure the batch/read result matches the released single-Product availability service.
- UI/UX responsibilities: use the information order Product identity, Lifecycle and Availability, choice/stock truth, then Edit; label active Products with positive active choice stock as Available, active Products without positive active choice stock as Sold out, and drafts as Not sellable rather than Sold out; expose unusual no-active-choice state with Edit as recovery; avoid badge and action sprawl.
- Data/state/source-of-truth boundaries: lifecycle reads Product.lifecycle; availability is never stored and is derived from lifecycle plus active positive choice stock; total stock sums active choices only; choice size/color/quantity/is_active come from ProductChoice and controlled vocabulary; recognition candidates never appear as card facts.
- Business isolation requirements: card queries, prefetched choices, Product Type, and all totals must be restricted to the resolved active Business; a forged relation or accidental cross-Business row must not be exposed.
- Navigation / return-path contract: Edit carries the current canonical Workspace URL and save/cancel return to the same list context; Product name is not made a Product Detail dependency.
- HTMX contract where relevant: none yet; cards are full-page server-rendered truth. P6.6 owns partial replacement after all membership-affecting query contracts exist.
- Alpine contract where relevant: none; the baseline card has no disclosure or client-owned state.
- Mobile-first requirements: cards use one-column flow at approximately 390px; state labels wrap; active choice rows remain readable without horizontal scrolling; description and secondary metadata cannot push stock truth behind an uncontrolled action cluster.
- Accessibility requirements: each card is an article with a logical heading; Lifecycle and Availability include text labels and are not color-only; each choice identity is readable in DOM order; the Edit action is a link with an unambiguous accessible name; status styles preserve contrast and focus visibility.
- Performance/query considerations: eliminate per-card availability, Product Type, size, color, and choice queries through select_related/prefetch_related or an equivalent shared read adapter; add a query-growth regression proving that adding Products does not add one query per card; avoid speculative caching and pagination.
- Explicit exclusions: Product media/price placeholders that have no current model truth, full description/detail view, Tag/material chips, readiness, replies, stock mutation, filters, clone, archive, and lifecycle actions.
- Likely source whitelist: catalog/workspace.py, catalog/views.py, inventory/availability.py, templates/catalog/_product_results.html, templates/catalog/_product_card.html, templates/catalog/product_list.html, static/css/app.css, catalog/test_workspace.py, and inventory/tests.py.
- Backend acceptance criteria: the card read model matches compute_product_availability for active-positive, active-zero, inactive-positive-only, and draft-positive cases; active totals ignore inactive choice stock; duplicate same-size/color ProductChoice rows remain separate Choice #id rows; no per-card query growth occurs; cross-Business facts never enter card context.
- UI/UX acceptance criteria: Lifecycle and Availability are visibly different concepts; active zero-stock shows Sold out without a manual lifecycle action; drafts never receive a Sold out lifecycle implication; each visible choice shows exact identity, size, color, and quantity; no active choices produces one clear Edit recovery; no Phase 7 or 8 content appears.
- Automated verification: focused card/read-model tests for each lifecycle/availability combination, total calculations, duplicate identities, inactive choices, missing Product Type, no-choice state, Business isolation, deterministic choice ordering, template semantics, and bounded query growth; rerun the complete availability suite.
- Manual owner/browser verification: advisory — compare active/available, active/sold-out, draft-with-stock, duplicate-choice, many-choice, and no-active-choice cards on desktop and approximately 390px mobile.
- Failure cases: malformed or legacy Product state renders a truthful correction state rather than raising; unavailable Product Type remains optional; a failed related-data fetch must not substitute guessed availability or quantity.
- Regression risks: duplicating the availability rule in catalog code, labeling drafts as sold out, aggregating duplicate choices, triggering N+1 queries, or overloading cards with every confirmed fact.
- Documentation update expectations: changelog_checkpoint.md after acceptance and BUILD_PLAN.md for the real slice status transition; DEVELOPMENT_NOTES.md only if the shared availability read adapter creates a durable architectural decision; no UX-plan or README change is expected before Phase 6 acceptance.
- Proposed commit message: feat: add compact product workspace cards
- Rollback/recovery note: remove the card/read-model layer and restore the P6.1 result rows together; shared availability behavior and persisted Product/choice data remain unchanged.
- Stop gate relation: satisfies the Product-card and first availability-consumer foundation, but stock action, retrieval, coherent partial refresh, and final owner UX acceptance remain open.
- Status: CLOSED; released and exact-SHA CI-passed.

#### P6.3 Choice-Level Workspace Stock Controls

- Objective: make approved exact-choice +1/-1 stock work available from Product cards while preserving the Phase 5 mutation, ledger, ownership, and server-truth boundaries.
- Dependency: P6.2 CLOSED.
- Why this slice exists: stock mutation is the highest-frequency Product-card action, but it must be attached only after cards can identify a precise ProductChoice and display the full-page recomputed result truthfully.
- Seller job / user value: decrement after a sale or increment after a restock directly on the correct visible choice without opening Product Edit.
- Exact scope: place semantic -1 and +1 submit controls on persisted active choice rows; retain inactive choices as read-only state with Edit recovery; include Choice #id plus canonical size/color in visible and accessible control names; submit to the existing inventory choice adjustment route with the canonical current Workspace URL; initially accept native full-page POST/redirect behavior so quantity, availability, totals, and later filter membership are all recomputed together. P6.6 adds the in-place HTMX enhancement.
- Backend responsibilities: reuse ChoiceStockMutationView and apply_choice_quantity_delta unchanged as the only subsequent stock-write boundary; do not create a catalog mutation service or ProductBundle quantity path; preserve row locking, exact delta validation, underflow protection, immutable InventoryAdjustment creation, and computed availability return.
- UI/UX responsibilities: classify stock as PRIMARY OPERATIONAL, Edit as LOW-FREQUENCY SECONDARY, lifecycle/destructive actions as absent, and later-phase actions as DEFERRED; show authoritative quantity beside each choice; expose successful full-page feedback and specific failure messages; do not offer direct set.
- Data/state/source-of-truth boundaries: every button targets one persisted ProductChoice primary identity; duplicate same-size/color rows never share a control or aggregate quantity; quantity remains server-owned; stock mutation does not change Product lifecycle or choice activation; availability is recomputed and never written.
- Business isolation requirements: the route resolves the authenticated owner's active Business, loads the choice within that Business, and returns 404/409 without writes for cross-Business, missing-Business, or unsupported-multiple-Business requests; hidden ids and next values never choose ownership.
- Navigation / return-path contract: successful and expected-failure native submissions return to the exact canonical search/filter-ready Workspace URL; the seller stays in Product Workspace context; an unsafe return URL falls back to /products/.
- HTMX contract where relevant: Workspace HTMX is deliberately not enabled in P6.3. The accepted fallback is native POST to the released endpoint followed by a complete Workspace GET, preventing a newly introduced stale Availability card. Existing Product Edit HTMX behavior remains unchanged until P6.6 adds an explicit Workspace response scope.
- Alpine contract where relevant: none; standard form submission and server messages own this slice.
- Mobile-first requirements: stock buttons meet an approximately 44-by-44-pixel target in Workspace cards, do not sit beside destructive actions, remain usable one-handed, and keep Choice #id, size, color, and quantity readable at approximately 390px.
- Accessibility requirements: use buttons inside valid POST forms with CSRF; accessible names include action plus exact choice identity; quantities use output/text announced after navigation; success is role status, failure is role alert; keyboard users can reach every active-choice control in logical order.
- Performance/query considerations: one mutation locks and refreshes one exact ProductChoice; the redirect performs the normal bounded Workspace query path; no duplicate card query or client-side quantity loop is added.
- Explicit exclusions: HTMX Workspace swapping, optimistic quantity, arbitrary delta, direct set, inactive-choice activation, initial stock, reason codes, batch controls, Product lifecycle actions, and Dashboard synchronization.
- Likely source whitelist: templates/catalog/_product_card.html, templates/catalog/_product_results.html when isolated include context must carry CSRF, templates/inventory/_choice_stock_controls.html, catalog/workspace.py, catalog/views.py, static/css/app.css, catalog/test_workspace.py, and inventory/tests.py; inventory/views.py only if a narrowly scoped canonical Workspace return validation is required.
- Backend acceptance criteria: each +1/-1 request calls the released mutation boundary, changes only the targeted owned choice, creates one exact adjustment, preserves duplicate peers, blocks underflow/invalid delta/cross-Business access with no write, and leaves lifecycle/is_active unchanged.
- UI/UX acceptance criteria: every active choice has two unmistakable controls and one authoritative quantity; inactive choices show state without a mutation control; duplicate-looking rows remain distinguishable by stable Choice #id; success and failure return to the same Workspace state; no stale quantity or availability remains after the full-page redirect.
- Automated verification: Product Workspace integration tests for control rendering, exact ids, duplicate choices, active versus inactive state, CSRF/native POST, safe next, success/error messages, underflow, invalid delta, cross-Business mutation, ledger facts, lifecycle preservation, and full-page sold-out/restock truth; rerun Phase 5 route/service regressions.
- Manual owner/browser verification: advisory — from one card, decrement 1 to 0 and increment 0 to 1, then repeat on one of two duplicate-looking choices and confirm only the intended Choice #id changes.
- Failure cases: double submission is serialized by the Phase 5 row lock and produces only committed transitions; underflow returns unchanged server truth and an error; external next is rejected; network interruption can be recovered by reloading the same URL and reading persisted truth.
- Regression risks: nesting invalid forms, accidentally enabling the choice-level HTMX target on Workspace cards before P6.6, losing Product Edit controls, mutating inactive state, or adding a second stock write path.
- Documentation update expectations: changelog_checkpoint.md after acceptance and BUILD_PLAN.md for the real slice status transition; README.md only for the material public Workspace reality and prior stale-status correction; DEVELOPMENT_NOTES.md only if the shared stock-control rendering contract requires a durable choice; no frozen UX change is expected.
- Proposed commit message: feat: add workspace choice stock controls
- Rollback/recovery note: remove the card-hosted forms while retaining the released inventory route/service and Product Edit controls; no inventory facts or schema need rollback.
- Stop gate relation: satisfies native exact-choice stock action and fallback integrity; the Phase 6 HTMX loading, focus, error, availability, and filter-membership coherence gate remains P6.6.
- Status: CLOSED; released and exact-SHA CI-passed.

#### P6.4 Product Workspace Search Baseline

- Objective: let the seller retrieve owned Products through a controlled, URL-backed, server-rendered search contract using already approved Product and confirmed catalog truth.
- Dependency: P6.3 CLOSED.
- Why this slice exists: a daily cockpit is not usable once the seller must visually scan the entire catalog, and search must be defined before filter composition and partial-refresh state can be safe.
- Seller job / user value: find a Product by the wording the seller remembers, see the applied query, act on a result, and return from Edit to the same searched Workspace.
- Exact scope: add optional GET parameter q through a small validated search form/state object; trim and collapse whitespace; enforce a bounded query/token length; use deterministic case-insensitive AND-across-tokens and OR-across-approved-fields behavior; search Product name and description, confirmed Product Type canonical/aliases, confirmed Tag canonical/aliases, ProductChoice size/color canonical/aliases, and confirmed material canonical/original wording. Lifecycle/status remains a filter concern. Show active query, result count, Clear search, and a distinct search no-result state with one recovery action.
- Backend responsibilities: extend the P6.1 Workspace query helper rather than the view; keep Business filtering first; query only confirmed associations and controlled aliases; use distinct/Exists/subquery strategy as appropriate to prevent duplicate Product rows; bind and validate q without database writes; keep result ordering deterministic rather than inventing relevance ranking.
- UI/UX responsibilities: provide a plainly labeled search input and submit button above results without pushing the first card far below the fold; show the exact applied query and result count; Clear search preserves any later valid filter state; no-result copy suggests a simpler term and offers one Clear search recovery.
- Data/state/source-of-truth boundaries: description is searchable observed text but does not become a confirmed card fact; aliases support retrieval but do not replace canonical display; only persisted confirmed Type/Tag/material/choice relations drive structured-field matches; recognition candidates and unconfirmed preview state are excluded.
- Business isolation requirements: every search subquery and relation is constrained to the resolved active Business; aliases, vocabulary, materials, and choices from another Business cannot match or leak through counts, snippets, or result ordering.
- Navigation / return-path contract: q is canonicalized in the Workspace URL; result Edit links carry that canonical URL; save/cancel return to the same q; stock native fallback keeps q; Clear search removes only q and never relies on browser Back.
- HTMX contract where relevant: none required; search submits as a native GET and remains fully usable without JavaScript. P6.6 does not need to turn search into live-as-you-type behavior.
- Alpine contract where relevant: none; query state belongs to the URL and server.
- Mobile-first requirements: at approximately 390px the search label, input, submit, and compact active-query summary wrap into a readable single-column control without horizontal scrolling or multiple suggestion rows.
- Accessibility requirements: the input has a persistent label, validation errors are associated with it, submit is a semantic button, result count/no-result text is announced as status, and Clear search is a descriptive link with visible focus.
- Performance/query considerations: cap normalized q at 120 characters and at most eight non-empty tokens; avoid one query per searchable relation or Product; add query-growth coverage for multiple Products/choices/tags; do not add Elasticsearch, external services, trigram/fuzzy indexes, or speculative PostgreSQL extensions.
- Explicit exclusions: fuzzy matching, typo correction, Georgian morphology, AI search, external search service, autocomplete/datalist, search suggestions, relevance analytics, pagination, lifecycle keyword interpretation, and public catalog search.
- Likely source whitelist: catalog/forms.py, catalog/workspace.py, catalog/views.py, templates/catalog/product_list.html, templates/catalog/_product_results.html, static/css/app.css, and catalog/test_workspace.py.
- Backend acceptance criteria: each approved field can retrieve an owned Product; multiple tokens require every token to match at least one approved field; duplicate joins yield one Product; cross-Business vocabulary and facts never match; blank q behaves as the unsearched Workspace; overlong, repeated, malformed, or unsupported parameters produce a controlled validation state without a server error or scope expansion.
- UI/UX acceptance criteria: applied q and result count are visible; search survives refresh and Edit round-trip; clearing q restores the unsearched list; catalog-empty and search-no-result states are distinct; no-result exposes exactly one primary recovery action; no search behavior implies candidate confirmation.
- Automated verification: field-by-field search tests, alias and observed-description tests, multi-token composition, blank/whitespace/overlong/malformed input, duplicate-row elimination, Business isolation, URL persistence, Clear search, no-result template, result count, edit return, native fallback, and bounded query-growth regression.
- Manual owner/browser verification: advisory — search by Product name, description wording, Type alias, Tag alias, size, color, and confirmed material; open Edit, save, and confirm the exact q remains on desktop and approximately 390px mobile.
- Failure cases: invalid q displays correction feedback and does not execute an unbounded token query; database/search failure renders no optimistic local result; unsupported morphology receives no false promise and can recover through Clear search.
- Regression risks: treating candidates as facts, leaking cross-Business aliases, join duplicates, slow query multiplication, losing q in stock/edit return paths, or allowing search controls to dominate the first mobile viewport.
- Documentation update expectations: changelog_checkpoint.md after acceptance and BUILD_PLAN.md for the real slice status transition; DEVELOPMENT_NOTES.md only for a durable search-tokenization trade-off; no APP_EXPERIENCE_PLAN.md or README.md change is expected before Phase 6 closure.
- Proposed commit message: feat: add product workspace search
- Rollback/recovery note: remove q parsing and search UI while leaving the P6.1-P6.3 unsearched Workspace intact; no schema or persisted data changes require recovery.
- Stop gate relation: satisfies the Phase 6 search and searched-return foundation; bounded filters and HTMX state coherence remain open.
- Status: CLOSED; the source release remained unchanged while CI-R1 added only `workflow_dispatch`, retaining the existing push and pull-request triggers, jobs, permissions, services, and commands. The owner-approved current-main recovery SHA completed CI successfully after the original source workflow's zero-job startup failure.

#### P6.5 V1 Product Workspace Filter Baseline

- Objective: add only the owner-approved highest-value operational filters and make them compose predictably with search through canonical server-owned URL state.
- Dependency: P6.4 CLOSED and explicit owner approval of the exact bounded filter set.
- Why this slice exists: search retrieves remembered Products, while a very small filter set lets the seller isolate daily lifecycle/stock states; uncontrolled field-to-filter expansion would recreate the prototype's dense mobile filter wall.
- Seller job / user value: narrow the Workspace to active, draft, available, or sold-out work, see exactly what is active, combine that state with search, and recover with one clear action.
- Exact scope: the owner-approved set is one stored lifecycle filter with Active/Draft values and one computed availability filter with Available/Sold out values. Sold out means an active Product with no positive active choice stock; drafts are not relabeled sold out. Use one value per filter, visible active-state summary, Clear filters that preserves q, and Clear all for combined no-match recovery. Product Type, Tag, material, size, color, readiness, low-stock threshold, and arbitrary database-field filters are excluded.
- Backend responsibilities: validate only enumerated lifecycle/availability values; extend the shared Workspace state/query helper; derive availability through the shared inventory rule/read adapter rather than a stored field; compose filters with q using AND semantics; keep canonical URLs stable and discard unsupported/repeated values safely.
- UI/UX responsibilities: place the two controls in one compact native filter disclosure or equivalent single block; keep active filters visible even when collapsed; avoid multiple horizontal chip rows; display a distinct filter-no-match or combined search/filter-no-match state with one Clear all recovery action.
- Data/state/source-of-truth boundaries: lifecycle comes only from Product.lifecycle; Available/Sold out is computed from lifecycle plus active choice stock; filter state belongs to URL query parameters; no client code or template stores availability; no readiness/attention semantics are inferred.
- Business isolation requirements: filtering begins from the owned Business queryset; choice-stock existence subqueries are Business-constrained; invalid ids or tampered parameters cannot select or reveal another Business.
- Navigation / return-path contract: q, lifecycle, and availability serialize in a canonical order; Edit save/cancel, native stock mutation, refresh, Clear search, and Clear filters preserve or remove only their documented keys; browser Back remains optional rather than required.
- HTMX contract where relevant: none in this slice; filter submission is a native GET fallback. P6.6 later enhances only stock truth refresh and must preserve the same canonical URL.
- Alpine contract where relevant: none; use native disclosure where practical. If implementation needs Alpine solely for open/closed filter presentation, it may own only that local disclosure state and never query values or results.
- Mobile-first requirements: at approximately 390px active-state summary and filter trigger fit without horizontal page scroll; opening filters does not create multiple uncontrolled rows; closing filters leaves active state and Clear action visible; first Product remains reachable without excessive setup copy.
- Accessibility requirements: use a labeled GET form, fieldset/legend or equivalent grouping, native controls, keyboard-operable disclosure with expanded state, text labels in addition to color, associated validation errors, visible focus, and a status announcement for result/no-match changes after navigation.
- Performance/query considerations: represent availability with one shared Exists/subquery or prefetched read contract, not per-Product service calls; retain deterministic ordering and duplicate elimination; add composition/query-growth tests; do not add indexes, caching, pagination, or a generic filtering framework without measured need.
- Explicit exclusions: Product Type/Tag filters unless separately owner-approved, multi-select filter matrices, low-stock policy, readiness, Dashboard signals, price/material/size/color filters, saved views, sorting controls, pagination, and client-owned filter state.
- Likely source whitelist: catalog/forms.py, catalog/workspace.py, catalog/views.py, templates/catalog/product_list.html, templates/catalog/_product_results.html, static/css/app.css, and catalog/test_workspace.py.
- Backend acceptance criteria: only approved enum values apply; Available returns active Products with positive active choice stock; Sold out returns active Products without it and excludes drafts; lifecycle and availability combine predictably with q; malformed/unknown/repeated values do not error or widen Business scope; URL serialization is stable.
- UI/UX acceptance criteria: active filters are visible when controls are collapsed; Clear filters preserves q; Clear all removes q and filters; filter-empty, search-empty, combined-empty, and true catalog-empty states remain distinguishable; no unapproved filter appears; a 390px viewport has no horizontal overflow.
- Automated verification: each lifecycle/availability state, cross-product stock isolation, inactive-choice stock, draft-with-stock, search/filter composition, invalid/tampered/repeated params, canonical URL order, Clear filters/Clear all, edit/native-stock return context, no-result state, Business isolation, and bounded query-growth regression.
- Manual owner/browser verification: required before implementation approval for the exact filter set, then required for acceptance — test Active, Draft, Available, Sold out, combined q/filter, Clear filters, Clear all, sold-out/restock membership, and mobile density at approximately 390px.
- Failure cases: no filter implementation begins without owner approval; invalid values render a controlled non-applied state and clear recovery; contradictory valid filters may truthfully return no results; query failure cannot fall back to client-side filtering.
- Regression risks: silently adding optional Type/Tag filters, conflating draft with sold out, losing q during clear actions, filter controls burying cards, stale membership after stock mutation, or duplicating availability logic.
- Documentation update expectations: changelog_checkpoint.md after acceptance and BUILD_PLAN.md for the approved scope/status transition; APP_EXPERIENCE_PLAN.md must record the owner-approved exact filter set; DEVELOPMENT_NOTES.md records the bounded-set trade-off if materially decided; README.md waits for released public reality.
- Proposed commit message: feat: add product workspace filters
- Rollback/recovery note: remove filter parsing/UI while preserving q and the unfiltered Workspace; no schema or data rollback is needed. If owner rejects the recommended set, stop and revise the roadmap/UX contract before implementation.
- Stop gate relation: supplies the approved filter contract required before truthful membership-aware HTMX refresh; it cannot close until required owner/browser acceptance, release, and exact-SHA CI succeed.
- Status: CLOSED; the owner-approved Lifecycle + Availability set is released and exact-SHA CI-passed, with delivery metadata retained in Git/GitHub.

#### P6.6 HTMX Workspace Truth Refresh and State Coherence

- Objective: progressively enhance Workspace stock controls so each accepted or rejected mutation leaves quantity, Product availability, totals, result count, and availability-filter membership visibly consistent with committed server truth.
- Dependency: P6.5 CLOSED with its owner-approved query contract.
- Why this slice exists: replacing only one quantity control would reproduce the prototype's stale-state defect when a final decrement or first restock changes the card badge, total, result count, or current filter membership.
- Seller job / user value: update one exact choice in place, see a clear loading state, receive authoritative success/error feedback, and remain in the same searched/filtered Workspace without contradictory stock or availability.
- Exact scope: add an explicit Workspace response scope to the existing stock POST; progressively enhance P6.3 controls with HTMX; after mutation or expected validation failure, re-run the shared Workspace query for the canonical current URL and replace the complete Product results region. The results region is the smallest uniform truthful boundary because it contains cards, quantities, availability, totals, result count, no-match state, and membership. Preserve native POST/redirect fallback and add minimal transport-error/focus recovery behavior without new dependencies.
- Backend responsibilities: continue to mutate only through apply_choice_quantity_delta; strictly validate that the submitted return/query context resolves to /products/ and only approved P6.4/P6.5 keys; use the public Workspace read helper rather than importing catalog view internals; render authoritative results after the transaction commits; associate expected stock error feedback with the exact Choice #id.
- UI/UX responsibilities: show an in-control Updating status; disable the relevant card's stock controls while the request is in flight; announce success or error; if a Product leaves the current availability filter, show a concise status explaining that it moved out of the current results; expose a full-refresh recovery link for transport/server failure; never render an optimistic quantity.
- Data/state/source-of-truth boundaries: HTMX carries intent and query context only; the server owns final quantity, total, lifecycle, availability, and result membership; Alpine/JavaScript cannot compute stock or availability; mutation never changes lifecycle/is_active; ledger behavior remains identical to Phase 5.
- Business isolation requirements: mutation choice, response Product queryset, card facts, query count, and all filter subqueries remain scoped to the resolved active Business; response-scope or return-URL tampering cannot render another Business or arbitrary internal page.
- Navigation / return-path contract: stock mutation does not push or replace the current Workspace URL; successful, expected-error, transport-error, and native-fallback paths retain the same q/lifecycle/availability context; a rejected context falls back safely to the unfiltered Product Workspace.
- HTMX contract where relevant: trigger is a persisted active-choice -1/+1 button; endpoint is the released /inventory/choices/<choice_pk>/adjust/ POST; Business scope is the authenticated resolved Business; server mutation is the released delta service followed by the shared Workspace read query; target is #product-workspace-results; swap is outerHTML; loading uses an HTMX indicator plus disabled semantics; success returns the complete authoritative results partial and status; expected validation/underflow returns the same partial with unchanged quantity and role alert; transport/non-HTMX server failure exposes refresh recovery; native fallback is the P6.3 POST/redirect/full GET.
- Alpine contract where relevant: none required. Any minimal JavaScript owns only HTMX transport feedback and focus restoration; it cannot hold quantity, availability, lifecycle, active filters, or confirmed facts.
- Mobile-first requirements: loading/error text remains adjacent to the acted choice without causing horizontal overflow; controls cannot be repeatedly tapped during an in-flight request; result replacement does not jump the seller to the top unnecessarily; the same control regains focus when present, otherwise focus moves to the results status when membership changes.
- Accessibility requirements: use aria-busy/disabled semantics during requests, live status for authoritative success, role alert for expected/transport failures, preserved accessible choice names, logical post-swap focus, visible focus indicators, and a keyboard-operable full-refresh recovery link.
- Performance/query considerations: one mutation plus one bounded Workspace results query is accepted; do not refetch the global shell or Dashboard; serialize/drop accidental overlapping results-region requests to prevent out-of-order swaps; assert bounded response query growth; do not add WebSockets, polling, global live sync, or client caching.
- Explicit exclusions: Dashboard synchronization, live search, HTMX-only navigation, optimistic updates, global counts outside Product Workspace, background polling, direct set, bulk mutation, lifecycle changes, readiness, and ready replies.
- Likely source whitelist: inventory/views.py, inventory/tests.py, templates/inventory/_choice_stock_controls.html, catalog/workspace.py, catalog/views.py, templates/catalog/product_list.html, templates/catalog/_product_results.html, templates/catalog/_product_card.html, static/css/app.css, static/js/product_workspace.js, templates/base.html if a page-script block is needed, and catalog/test_workspace.py.
- Backend acceptance criteria: an HTMX increment/decrement mutates only the exact choice and returns the results partial; duplicate peers remain unchanged; final decrement and first restock recompute availability; availability-filter membership and result count update in the same response; underflow/invalid delta preserves quantity and ledger; cross-Business and malformed response scope do not write or leak; native fallback remains green.
- UI/UX acceptance criteria: one accepted action cannot leave a card badge, total, choice quantity, result count, or current availability-filter membership contradictory; loading blocks accidental repeat input; success/error is announced; failure never shows optimistic stock; filtered/search URL remains unchanged; disappearance from a filter has an understandable status/recovery.
- Automated verification: HTMX response-template/target contract, authoritative quantity, full results swap, sold-out/restock card and membership transitions, last-result empty state, result count, duplicate identity, underflow, invalid delta, storage limit, cross-Business, malformed context, native fallback, focus/transport hooks as template assertions, ledger integrity, lifecycle preservation, and existing Phase 5 concurrency/service regressions.
- Manual owner/browser verification: required — throttle the browser/network, observe disabled/loading state, test rapid repeated taps, force one failed request, decrement the last available choice under Available filter, restock under Sold out filter, verify search/filter URL stability, and repeat with keyboard at approximately 390px.
- Failure cases: expected validation returns current authoritative results with an alert and no write; 404/409/5xx/network timeout shows recovery without changing displayed quantity; a stale submitted query is revalidated; overlapping requests cannot produce an older final DOM than committed server truth.
- Regression risks: circular/private cross-app imports, replacing too small a fragment, losing focus, out-of-order swaps, dropping current q/filter state, breaking Product Edit's choice-only HTMX response, or accidentally synchronizing later-phase surfaces.
- Documentation update expectations: changelog_checkpoint.md after acceptance and BUILD_PLAN.md for the real slice status transition; DEVELOPMENT_NOTES.md records the results-region stale-state decision and rejected smaller swap if it is implemented as planned; no APP_EXPERIENCE_PLAN.md change is needed unless owner changes the approved interaction contract.
- Proposed commit message: feat: keep product workspace state coherent
- Rollback/recovery note: remove the Workspace HTMX response scope and enhancement while retaining P6.3 native POST/redirect controls; no mutation service, ledger, schema, or persisted data rollback is required.
- Stop gate relation: closes the Phase 6 server-truth and stale-state implementation boundary, leaving only the Phase 6-specific owner UX/accessibility/regression audit.
- Status: CLOSED; released and exact-SHA CI-passed after implementation, audit hardening, local PostgreSQL verification, and required owner/browser acceptance. Delivery metadata remains Git/GitHub authority.

#### P6.7 Phase 6 Workspace UX, Navigation, Accessibility, and Regression Gate

- Objective: prove and, where necessary, repair only the Product Workspace behavior delivered by P6.1-P6.6 before Phase 7 begins.
- Dependency: P6.1-P6.6 CLOSED.
- Why this slice exists: Product Workspace usefulness depends on first-viewport hierarchy, exact stock interaction, return trust, mobile density, accessibility, and stale-state recovery that cannot be proven by unit/view assertions alone.
- Seller job / user value: use the complete Workspace confidently on phone or desktop to find, inspect, update, and correct Products without contradictory truth, hidden context loss, or unrelated administrative clutter.
- Exact scope: perform the Phase 6 acceptance matrix; add missing Phase 6 regression coverage; inspect the first viewport, card hierarchy/density, search/filter density, choice identity, sold-out/restock transitions, loading/error/recovery, explicit Edit return, empty/no-result states, mobile behavior, keyboard basics, semantic announcements, query growth, and Business isolation; repair only defects that prevent P6.1-P6.6 acceptance.
- Backend responsibilities: audit the shared Workspace query/state helper, Business-first scoping, controlled parameters, availability consistency, exact inventory-service reuse, results-region response, deterministic ordering, safe next handling, and query behavior; make only the smallest Phase 6 correction supported by failing evidence.
- UI/UX responsibilities: verify that Product identity and stock work dominate the card; Lifecycle and Availability remain understandable; Edit is the one correction action; search/filter controls do not bury cards; duplicate choices remain distinguishable; every empty/error state has one useful recovery; no Phase 7/8 action appears.
- Data/state/source-of-truth boundaries: confirm that quantity is Phase 5 service-owned, availability is computed, lifecycle is separate, duplicate choice rows are not merged, observed/candidate/confirmed boundaries remain intact, and no template/JavaScript owns operational truth.
- Business isolation requirements: rerun route, query, search, filter, card, inventory, return-context, and HTMX isolation tests; attempt direct cross-Business Product/choice/query tampering and require no data or existence leak.
- Navigation / return-path contract: manually and automatically verify unfiltered, searched, filtered, and combined Workspace to Edit to save/cancel round-trips; stock mutation remains in context; unsafe external next falls back; browser Back is never the only return mechanism.
- HTMX contract where relevant: audit trigger, endpoint, Business scope, mutation, results target, outerHTML swap, loading, success, expected error, transport failure, native fallback, focus recovery, and stale membership; repair only Phase 6 contract defects.
- Alpine contract where relevant: confirm no Alpine/client state owns Product or inventory truth; any local disclosure/transport behavior may reset after results swap without losing server state or accessibility.
- Mobile-first requirements: owner verification at approximately 390px must show no horizontal page scrolling, readable Product/choice identity, compact first viewport, wrapping active filters, approximately 44-pixel stock targets, safe one-handed controls, no hover-only action, and no destructive action near stock.
- Accessibility requirements: semantic forms/buttons/links/headings; accessible names include exact choice identity; keyboard reaches every action; visible focus survives or recovers after swap; status is not color-only; loading uses busy/disabled semantics; success/error is announced; DOM order is logical; text and controls remain readable on mobile. No broad WCAG claim is made.
- Performance/query considerations: retain Business-first query plans and bounded query counts independent of card count; run the query-growth regressions with representative Products, choices, Type, Tags, and materials; record pagination as a scaling risk because it is not owner-approved, without silently adding it during the audit.
- Explicit exclusions: Dashboard, attention signals, readiness, buyer replies, Product Detail, Product create/edit redesign, final Georgian terminology freeze, Phase 9-wide mobile/accessibility redesign, new filters, new domain rules, deployment, analytics, and opportunistic refactoring.
- Likely source whitelist: only files already introduced or changed by P6.1-P6.6, principally catalog/workspace.py, catalog/views.py, catalog/forms.py, inventory/availability.py, inventory/views.py, Product Workspace/card/results/stock templates, static/css/app.css, static/js/product_workspace.js, catalog/test_workspace.py, catalog/tests.py, and inventory/tests.py; expand only with owner approval if a verified Phase 6 defect cannot be fixed inside this boundary.
- Backend acceptance criteria: all focused Workspace/search/filter/return/HTMX/inventory tests pass; full PostgreSQL regression passes; Django system check, migration dry-run, and unapplied-migration check pass; no query-growth, Business isolation, ledger, availability, ProductBundle, or Phase 4 recognition/choice regression remains.
- UI/UX acceptance criteria: an owner can identify a Product quickly; distinguish Lifecycle from Availability; identify and mutate one exact duplicate-looking choice; see server truth after sold-out/restock; preserve q/filters through Edit; recover from no-result and failed request; complete keyboard basics; and operate at approximately 390px without horizontal page scrolling or card/action overload.
- Automated verification: focused P6 test module; existing Product list/create/edit, ProductBundle, recognition/choice truth, availability, InventoryAdjustment, mutation route, HTMX, concurrency, and Business selector suites; then the full PostgreSQL suite plus system/migration/diff checks. Exact counts and pass claims are recorded only from executed evidence.
- Manual owner/browser verification: required — desktop plus approximately 390px mobile, populated and empty states, keyboard-only basics, slow request, forced failure, exact duplicate choice, 1-to-0 and 0-to-1 transition, search, each approved filter, combined state, Clear actions, and Edit-return round-trip.
- Failure cases: any critical stale truth, cross-Business leak, wrong-choice mutation, lost URL context, inaccessible stock action, mobile horizontal overflow, misleading lifecycle/availability label, or Phase 7/8 leakage blocks Phase 6; only the smallest Phase 6 defect fix is allowed.
- Regression risks: disguising broad Phase 9 work as audit repair, opportunistically redesigning Product create/edit, weakening Phase 5 inventory guarantees, changing approved filter scope, or declaring browser/accessibility success without evidence.
- Documentation update expectations: changelog_checkpoint.md always after acceptance; BUILD_PLAN.md records Phase 6 completion without marking Gate 4 passed; README.md updates only when the released Workspace is material public reality; DEVELOPMENT_NOTES.md records only durable audit decisions/lessons; APP_EXPERIENCE_PLAN.md changes only for separately owner-approved UX-contract changes.
- Proposed commit message: test: verify product workspace release readiness
- Rollback/recovery note: revert only the failing Phase 6 audit repair or added regression assertion with evidence; never roll back released Phase 5 facts or broaden into another phase to make the gate pass.
- Stop gate relation: this is the Phase 6 completion gate. Passing it permits Phase 7 planning, but Gate 4 remains open because it spans later UX-relevant phases and the Phase 9 stabilization gate.
- Controlled execution order: P6.7a first-viewport/mobile repair -> P6.7b canonical return-path hardening -> P6.7c accessibility/recovery hardening -> P6.7d integrated regression and owner closure gate. Each functional repair requires its own approval, implementation, audit/docs sync, exact release set, push, and exact-SHA CI before the next begins. P6.7d cannot absorb discovered repairs: a failing defect creates the smallest separately approved P6.7 recovery slice and leaves the gate open.
- Status: IN_PROGRESS; P6.7a is CLOSED, P6.7b is APPROVED and awaiting implementation after the governance release, and P6.7c/P6.7d are NOT_STARTED.

##### P6.7a Workspace First-Viewport and Mobile-Density Repair

- Objective: make daily Product and exact-choice stock work dominate the first viewport while reducing responsive density without changing server-owned behavior.
- Exact scope: move Add Product into the Workspace heading for populated results; keep search compact; keep valid filters collapsed while canonical active state and clear actions remain visible; open invalid filters with their errors; place Lifecycle and computed Availability before the description excerpt; move vocabulary management after Product results; harden card, choice, and stock-control wrapping and tap targets at mobile width.
- Explicit exclusions: backend/query/state changes, new filters, Product create/edit redesign, Dashboard, readiness, replies, final Georgian terminology, broad Phase 9 work, dependencies, schema, and deployment behavior.
- Source whitelist: `catalog/test_workspace.py`, `static/css/app.css`, `templates/catalog/product_list.html`, `templates/catalog/_product_results.html`, and `templates/catalog/_product_card.html`.
- Acceptance: populated DOM order is Add Product, search/filter, Product cards, then vocabulary settings; valid active filter state remains visible with a collapsed disclosure; invalid filters open with errors; Lifecycle and Availability precede secondary description text; exact-choice controls remain readable with approximately 44-pixel targets and no horizontal page overflow at approximately 390px; existing empty/error, canonical URL, native stock, and HTMX results contracts remain intact.
- Automated verification: focused Workspace and inventory route/HTMX suite; full PostgreSQL regression; Django system check, migration dry-run, unapplied-migration check, and diff checks.
- Manual owner/browser verification: required on desktop and approximately 390px mobile for populated and filtered states, invalid-filter recovery, keyboard basics, exact-choice controls, wrapping, tap targets, and horizontal overflow.
- Proposed commit message: `fix: improve product workspace hierarchy`.
- Status: CLOSED; released and exact-SHA CI-passed after implementation, integrity audit, focused 74-test verification, full 402-test PostgreSQL regression, and required owner/browser acceptance. Delivery metadata remains Git/GitHub authority.

##### P6.7b Canonical Workspace Return-Path Hardening

- Objective: ensure Product Add/Edit correction flows preserve only validated canonical Product Workspace context.
- Dependency: P6.7a CLOSED.
- Exact scope: distinguish the existing generic safe internal return behavior used by vocabulary recovery from the stricter Product Workspace return boundary; Product Add/Edit must accept only one exact local `/products/` URL containing canonical `q`, Lifecycle, and Availability state; preserve that state through Back, Cancel, validation errors, existing HTMX preview/transfer rerenders, and successful save; fall back to unfiltered `/products/` for external, non-Workspace, fragmented, repeated, unknown, invalid, or non-canonical return input.
- Explicit exclusions: vocabulary return behavior, Dashboard or future drilldown return contexts, global navigation redesign, new filters, Product create/edit redesign, stock mutation/results behavior, client-owned navigation state, schema, dependencies, and broad accessibility work.
- Source whitelist: `catalog/views.py` and `catalog/tests.py`.
- Boundaries: reuse `ProductWorkspaceState` as the canonical server-owned validator; retain Business-scoped Product reads/writes, atomic ProductBundle persistence, safe fallback, and all observed/candidate/confirmed and choice-stock boundaries; do not broaden the accepted Workspace query-key set.
- Acceptance: unfiltered, searched, lifecycle-filtered, availability-filtered, and combined canonical Workspace URLs survive Product Add/Edit GET, rendered Back/Cancel/hidden return state, invalid-form and existing HTMX rerenders, and successful POST exactly; unsupported return targets fall back to `/products/`; cross-Business Product access and writes remain blocked.
- Automated verification: focused Workspace-state and Product create/edit return-path matrix; ProductBundle, recognition/transfer, Business-isolation, and inventory-return regressions; then full PostgreSQL regression, Django system check, migration dry-run, unapplied-migration check, and diff checks.
- Manual owner/browser verification: required — open a combined searched/filtered Workspace, enter Edit, verify Cancel returns exactly, repeat and save one benign correction, and confirm the same canonical Workspace state returns without browser Back.
- Documentation update expectations: `changelog_checkpoint.md` always after acceptance and `BUILD_PLAN.md` for status/order; `DEVELOPMENT_NOTES.md` only if implementation confirms a durable generic-safe-versus-workflow-canonical return lesson; no `APP_EXPERIENCE_PLAN.md` or `README.md` change is expected.
- Proposed commit message: `fix: constrain product workspace return paths`.
- Stop gate relation: closes the explicit Workspace-to-correction navigation boundary but does not close the accessibility or integrated regression gates.
- Status: APPROVED; begin implementation only after this governance release is closed.

##### P6.7c Workspace Accessibility and Recovery Hardening

- Objective: make the released Workspace interactions keyboard-operable and expose authoritative loading, success, error, and recovery state through a bounded accessibility baseline.
- Dependency: P6.7b CLOSED.
- Exact scope: audit and repair only verified Phase 6 gaps in semantic heading/form/control structure, search/filter error association and disclosure behavior, exact-choice accessible names, visible focus, HTMX busy/disabled state, success/error announcements, post-swap focus restoration, transport recovery, and logical keyboard order; preserve native fallback and the P6.7a responsive hierarchy.
- Explicit exclusions: broad WCAG compliance claims, global accessibility redesign, final Georgian terminology, Product create/edit redesign, new interactions, client-owned Product/inventory truth, Phase 9 stabilization, schema, and dependencies.
- Expected source whitelist: `templates/catalog/product_list.html`, `templates/catalog/_product_results.html`, `templates/catalog/_product_card.html`, `static/css/app.css`, `static/js/product_workspace.js`, `catalog/test_workspace.py`, and `inventory/tests.py`; include only files required by failing evidence in the approved Prompt 2 release contract.
- Boundaries: HTML semantics and minimal JavaScript may own disclosure, transport feedback, and focus only; Django/HTMX responses remain authoritative for quantity, availability, lifecycle, filters, errors, and Business scope.
- Acceptance: every Workspace action is keyboard reachable with visible focus; exact duplicate-looking choices remain distinguishable to assistive technology; invalid filters expose associated errors; in-flight stock actions expose busy/disabled state; accepted, expected-error, membership-change, and transport-failure paths announce authoritative state and place focus on the same control or one explicit recovery/status target; native fallback remains functional.
- Automated verification: focused template/JS contract assertions plus Workspace and inventory HTMX/native regressions; full PostgreSQL regression, Django system/migration checks, JavaScript syntax check, and diff checks.
- Manual owner/browser verification: required — keyboard-only desktop and approximately 390px mobile checks for search/filter disclosure, exact-choice -1/+1, slow request, expected underflow, forced transport failure, membership change, visible focus, announcements, recovery, wrapping, and horizontal overflow.
- Documentation update expectations: `changelog_checkpoint.md` always after acceptance and `BUILD_PLAN.md` for status/order; `DEVELOPMENT_NOTES.md` only for a durable focus/announcement decision or workaround; no `APP_EXPERIENCE_PLAN.md` change without owner-approved UX-contract change and no `README.md` change is expected.
- Proposed commit message: `fix: harden workspace accessibility recovery`.
- Stop gate relation: closes the bounded Phase 6 accessibility/recovery repair boundary but does not itself declare Phase 6 passed.
- Status: NOT_STARTED; do not contract or implement before P6.7b is CLOSED.

##### P6.7d Phase 6 Integrated Regression and Owner Closure Gate

- Objective: prove the complete released P6.1-P6.7c Workspace contract and close Phase 6 only from executed automated, browser, release, and exact-SHA CI evidence.
- Dependency: P6.7b and P6.7c CLOSED.
- Exact scope: execute the Phase 6 acceptance matrix across authentication and Business isolation, canonical search/filter/return state, Product cards and exact duplicate choice identity, native and HTMX stock transitions, loading/error/recovery/focus, empty states, query growth, responsive behavior, and keyboard accessibility; add only missing regression assertions inside the established Phase 6 test boundary.
- Explicit exclusions: bundled source repair, new Product behavior, Dashboard, readiness, replies, Product Detail, new filters, terminology freeze, broad Phase 9 work, deployment, schema, dependencies, opportunistic refactoring, and automatic Gate 4 closure.
- Gate failure rule: any functional, security, integrity, navigation, accessibility, responsive, or stale-truth defect produces FAIL and the smallest separately approved P6.7 recovery slice; P6.7d must not silently repair or broaden itself.
- Expected test whitelist: `catalog/test_workspace.py`, `catalog/tests.py`, and `inventory/tests.py`; exact Prompt 2 may narrow this set and must not add application source unless a separate recovery slice is approved.
- Acceptance: the focused Phase 6 matrix and full PostgreSQL suite pass; Django system/migration and diff checks pass; required desktop and approximately 390px owner review passes; the audited release is committed and pushed; the tree is clean and local HEAD equals actual remote main; required CI succeeds for the exact release SHA; only then may Phase 6 become PASSED while Gate 4 remains open.
- Documentation update expectations: `changelog_checkpoint.md` and `BUILD_PLAN.md` record the accepted pre-release gate in Prompt 4; `README.md` changes only if the released Workspace materially changes public-facing capability reality; post-CI Phase 6 governance closure is permitted inside Prompt 5 only when Prompt 4 explicitly requires it; no hash/run ledger or recursive sync commit.
- Proposed commit message: `test: verify product workspace release readiness`.
- Stop gate relation: final Phase 6 closure gate; success permits Phase 7 planning but does not pass Gate 4.
- Status: NOT_STARTED; do not contract before P6.7b and P6.7c are CLOSED.

#### Phase 6 Measurable Stop Condition

Phase 6 may be marked PASSED only when all seven P6.1-P6.7 slices are accepted and released with executed evidence showing:

- /products/ is authenticated, side-effect free, and strictly scoped to the one resolved active Business.
- Product cards are useful and compact; they expose Product identity, separate Lifecycle and computed Availability, exact active choice identity/quantity, total active stock, and one Edit/correction action without later-phase content.
- Every Workspace stock control targets one exact ProductChoice and uses the released Phase 5 +1/-1 service, immutable ledger, ownership, lock, underflow, lifecycle-separation, and computed-availability rules.
- Search covers only the approved observed/confirmed fields, remains URL-backed and Business-scoped, has visible active state, result count, Clear search, and a distinct no-result recovery.
- The owner-approved bounded filter set is implemented with predictable search composition, visible state, Clear filters/Clear all, canonical URL behavior, and no filter sprawl.
- Unfiltered, searched, filtered, and combined Workspace URLs survive Edit save/cancel and native/HTMX stock paths through explicit safe return context.
- HTMX returns server-rendered authoritative results and cannot leave choice quantity, card totals, Availability, result count, or current availability-filter membership stale; loading, success, expected failure, transport recovery, native fallback, focus, and repeated-click behavior are verified.
- True catalog-empty, search-no-result, filter-no-match, combined-no-match, no-active-choice, no-Business, multiple-Business, and request-failure states remain distinct and each provides one useful recovery where applicable.
- Desktop and approximately 390px owner/browser checks pass with no horizontal page scrolling, acceptable first-viewport density, readable Georgian-capable wrapping, safe tap targets, and no hover-only critical behavior.
- The Phase 6 accessibility baseline passes for semantic controls/forms/headings, exact-choice accessible names, keyboard reachability, visible focus, non-color-only state, busy/disabled semantics, status/error announcements, readable typography, and logical DOM order.
- Focused Phase 6, Phase 4 Product/choice, Phase 5 inventory/availability/ledger/concurrency, ProductBundle, return-path, and Business-isolation regressions plus the full PostgreSQL suite, Django checks, migration checks, and relevant exact-SHA CI all pass from executed evidence.
- The owner completes and accepts the P6.7 Product Workspace UX review.

Phase 6 completion does not pass or close Gate 4. Dashboard, attention signals, readiness, deterministic buyer replies, broad terminology/accessibility/mobile stabilization, and later UX work remain in their controlling later phases.

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
