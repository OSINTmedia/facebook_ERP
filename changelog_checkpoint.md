# Changelog Checkpoint

## Document Metadata

- Status: LIVE
- Owner: osMit
- Project: Social Commerce Seller Operations Assistant
- Rebuild workspace: `/home/giga/Desktop/OSINT/GITHUB_MVP_ERP/`
- Source prototype: `/home/giga/Desktop/OSINT/facebook_MVP/`
- Update rule: after every approved implementation or documentation checkpoint
- Read first in every new Codex chat: yes

## 1. Current Project State

- Discovery audits completed.
- Owner-controlled planning documents are frozen for the Phase 1 starting baseline.
- Execution roadmap, public README, and live checkpoint exist.
- Documentation structure normalized for context transfer.
- Clothing domain owner review completed for `docs/domain/CLOTHING_DATA_SPEC_V1.md`.
- Clothing direction is description-first semantic recognition with observed text, candidate meaning, and confirmed structured fact layers.
- Material is a small typed semantic fact when confirmed.
- Detailed garment measurements are deferred to a separate approved micro-slice.
- GitHub repository already exists: `https://github.com/OSINTmedia/facebook_ERP`.
- GitHub repository visibility: public.
- GitHub default branch: `main`.
- Remote contains the preserved initial README commit `dce852b`.
- Phase 1 Django/PostgreSQL foundation and CI is `PASSED`.
- P1.1 Python and Django Dependency Baseline is `PASSED`.
- P1.2 Clean Django Project Scaffold is `PASSED`.
- P1.3 Settings and Environment Structure is `PASSED`.
- P1.4 PostgreSQL and Test Database Baseline is `PASSED`.
- P1.5 Base Application Shell is `PASSED`.
- P1.6 CI and Initial Test Harness is `PASSED`.
- Phase 2 User and Business Ownership is `PASSED` locally; P2.5 Git checkpoint and CI remain pending.
- P2.1 Accounts App and Custom Seller User Model Baseline is `PASSED`.
- P2.2 Business Model and Ownership Boundary Baseline is `PASSED`.
- P2.3 Login Flow Baseline is `PASSED`.
- Environment-Gated Demo Seller Access Bootstrap is `PASSED`.
- P2.4 Owner-Scoped Query Helper Baseline is `PASSED`.
- P2.5 Cross-Business Access Test Baseline is `PASSED` locally.
- CI workflow is committed and pushed in `.github/workflows/django.yml`.
- Local P1.6 verification commands passed.
- Latest checked GitHub Actions run `30626190659` passed for committed `HEAD` `41cbd3e62f55f40d432b7ed12b07fb4a2d957b29`.
- Online demo is not deployed.
- Private workflow prompt `codex_prompt_ERP.txt` exists locally and is intentionally ignored by Git.

## 2. Current Phase

- Phase: Phase 2 - User and Business Ownership
- Status: PASSED locally; Git checkpoint pending for P2.5
- Current micro-slice: P2.5 Cross-Business Access Test Baseline (`PASSED` locally)
- Next concrete micro-slice: P3.1 Product Model Baseline next-step report
- Started: 2026-07-27
- Last updated: 2026-07-31

## 3. Completed Work

- Phase 1A repository map and evidence inventory completed in `docs/discovery/DISCOVERY_REPORT.md`.
- Phase 1B backend, domain, state, and ownership audit completed in `docs/discovery/backend.md`.
- Phase 1C frontend, navigation, and seller UX audit completed in `docs/discovery/frontend.md`.
- Phase 1D draft rebuild documents completed:
  - `docs/Portfolio_MVP_V1.md`
  - `docs/Technical_Planning_v1.md`
  - `docs/User_Journey_Freeze_v1.md`
  - `APP_EXPERIENCE_PLAN.md`
- Phase 1E draft execution documents completed:
  - `BUILD_PLAN.md`
  - `README.md`
  - `changelog_checkpoint.md`
- Documentation restructuring completed:
  - `DEVELOPMENT_NOTES.md`
  - `docs/`
  - `docs/discovery/`
  - `docs/archive/old_docs/`
- Clothing and Git reality documentation sync completed:
  - `docs/domain/CLOTHING_DATA_SPEC_V1.md`
  - active planning references to the clothing spec
  - GitHub remote reality and reconciliation blockers
- Repository hygiene sync completed:
  - `.gitignore`
  - verified local branch/remote reality
- Documentation baseline committed and pushed:
  - `549db75 docs: add portfolio rebuild planning baseline`
  - preserved `dce852b Initial commit`
- Clothing recognition scope documentation committed and pushed:
  - `9f5a5e2 docs: align planning with clothing recognition scope`
- Documentation governance corrective sync committed and pushed:
  - `accc24b docs: sync governance before phase 1`
- Phase 1 readiness checkpoint committed and pushed:
  - `0c04cbd docs: mark phase 1 ready`
- P1.1 Python and Django Dependency Baseline implemented, committed, and pushed:
  - `69e968e chore: define python and django dependency baseline`
- P1.2 Clean Django Project Scaffold implemented, committed, and pushed:
  - `4914f2b chore: scaffold clean django project`
- P1.3 Settings and Environment Structure implemented, committed, and pushed:
  - `a01e246 chore: configure environment-aware django settings`
- P1.4 PostgreSQL and Test Database Baseline implemented and pushed:
  - `323c268 chore: document postgresql database baseline`
- P1.4 corrective local environment and runtime verification completed, committed, and pushed:
  - local/test settings require PostgreSQL configuration and contain no SQLite fallback
  - non-PostgreSQL `DATABASE_URL` values are rejected during settings import
  - missing `DATABASE_URL` fails clearly with `ImproperlyConfigured`
  - project-specific local PostgreSQL identity verified as host `127.0.0.1`, port `5432`, role `facebook_erp_dev`, database `facebook_erp_dev`
  - direct Django database connection passed
  - default Django migrations are applied
- P1.5 Base Application Shell implemented and verified locally:
  - root route renders the minimal private seller-workspace shell
  - base and page templates render successfully
  - message region, active navigation state, and disabled future placeholders exist
  - `static/css/app.css` is found and served over local HTTP
  - root route returns `200`; unknown routes return `404`, not `500`
  - shell does not introduce public catalog, marketing, broad ERP, orders, payments, delivery, analytics, auth behavior, Product CRUD, or HTMX behavior
  - committed and pushed with P1.4 runtime correction as `dc21677 feat: establish postgresql runtime and application shell`
- P1.6 CI and Initial Test Harness local implementation completed and verified locally:
  - GitHub Actions workflow added at `.github/workflows/django.yml`
  - workflow runs on push and pull request to `main`
  - workflow provisions a PostgreSQL service container
  - workflow installs dependencies from `requirements.txt`
  - workflow runs `pip check`, Django system check, migration dry-run check, migration apply, migration check, and Django tests
  - local equivalent verification passed
  - committed and pushed as `23fb3ca ci: add django verification workflow`
  - GitHub Actions run `30537591111` completed successfully for commit `23fb3ca166b86dd1842d653ca9db44f75f696469`
  - P1.6 is marked `PASSED`; Gate 1 is passed
- Owner-controlled documents frozen for Phase 1 baseline:
  - `docs/Portfolio_MVP_V1.md`
  - `docs/Technical_Planning_v1.md`
  - `docs/domain/CLOTHING_DATA_SPEC_V1.md`
  - `docs/User_Journey_Freeze_v1.md`
- P2.4 Owner-Scoped Query Helper Baseline implemented and verified locally:
  - owner-scoped Business queryset helper exists;
  - active-business resolver returns the only owned business, returns `None` when no Business exists, and refuses multiple-business ambiguity pending owner-approved policy;
  - owned-business lookup hides another seller's Business with `Http404`;
  - no Business is created by read-side resolution.
- P2.5 Cross-Business Access Test Baseline implemented and verified locally:
  - Business selector tests now explicitly cover other-owner-only state;
  - missing Business ids are hidden with `Http404`;
  - anonymous users cannot resolve an existing seller-owned Business through the owned lookup helper;
  - no source code, route, model, migration, UI, or owner-policy behavior changed.

## 4. Files Currently Available

### Audit evidence

- `docs/discovery/DISCOVERY_REPORT.md`
- `docs/discovery/backend.md`
- `docs/discovery/frontend.md`
- `docs/discovery/ASSISTANT_FIRST_PRODUCT_DESIGN_SYNTHESIS.md`
- `docs/domain/CLOTHING_DATA_SPEC_V1.md`

### Rebuild documents and source

- `.env.example`
- `APP_EXPERIENCE_PLAN.md`
- `DEVELOPMENT_NOTES.md`
- `BUILD_PLAN.md`
- `README.md`
- `changelog_checkpoint.md`
- `accounts/`
- `businesses/`
- `config/`
- `.github/workflows/django.yml`
- `templates/`
- `static/`
- `manage.py`
- `requirements.txt`
- `docs/Portfolio_MVP_V1.md`
- `docs/Technical_Planning_v1.md`
- `docs/User_Journey_Freeze_v1.md`

### Private local workflow

- `codex_prompt_ERP.txt` exists locally for owner-run Codex workflow prompts.
- It is intentionally ignored and must not be staged or committed.

### Local environment

- `.env` exists locally, is ignored by Git, has permission `0600`, and must not be printed, staged, or committed.

## 5. Current Verification

- Required planning and evidence documents: present in the normalized structure.
- Clothing domain spec: owner-reviewed, revised as version `1.1`, and frozen as an owner-controlled domain boundary.
- Historical docs: archived under `docs/archive/old_docs/` and used as non-canonical context only.
- Source project unchanged: yes.
- Source code copied: no.
- Git status at P2.5 integrity audit: initialized on `main`, tracking `origin/main`; current committed `HEAD` and `origin/main` are aligned at `41cbd3e62f55f40d432b7ed12b07fb4a2d957b29`; working tree contains uncommitted P2.5 test changes plus this live checkpoint sync. Exact current `HEAD` and `origin/main` alignment must always be read from Git commands, and Git commands override hardcoded checkpoint hashes.
- Remote repository status: existing public GitHub repository with preserved initial README commit `dce852b`, pushed baseline commit `549db75`, clothing scope commit `9f5a5e2`, governance commit `accc24b`, Phase 1 readiness checkpoint commit `0c04cbd`, checkpoint sync commit `1048175`, dependency baseline commit `69e968e`, scaffold commit `4914f2b`, settings commit `a01e246`, PostgreSQL baseline commit `323c268`, P1.4/P1.5 runtime-shell checkpoint commit `dc21677`, P1.6 CI workflow commit `23fb3ca`, P1.6 documentation sync commit `41b6fe4`, P2.1 custom user baseline commit `54d8bfc`, P2.2 business ownership baseline commit `a3d19cc`, P2.3 login flow baseline commit `9f8fb8c`, demo-access bootstrap commit `bfaacae`, repository handoff checkpoint commit `66a143a`, P2.4 owner-scoped query helper commit `6b88e8b`, and P2.4 post-push checkpoint sync commit `41cbd3e`.
- Local remote status: `ssh://git@ssh.github.com:443/OSINTmedia/facebook_ERP.git`.
- GitHub authentication status: SSH authentication works through `ssh.github.com` on port `443`.
- CI status: configured and passing on latest checked GitHub Actions run `30626190659` for committed `HEAD` `41cbd3e62f55f40d432b7ed12b07fb4a2d957b29`; P2.5 is locally verified but not yet committed or run in CI.
- Online demo status: not deployed.

### P1.4 verification

- Project runs through `.venv`.
- Python resolves to `.venv/bin/python`.
- Django and psycopg resolve from `.venv`.
- `.env` exists locally, is ignored by Git, and has permission `0600`.
- Missing `DATABASE_URL` fails clearly with `ImproperlyConfigured`.
- No executable placeholder database credentials remain.
- No SQLite fallback exists.
- Active local database backend is PostgreSQL.
- Project-specific local PostgreSQL identity:
  - host: `127.0.0.1`
  - port: `5432`
  - role: `facebook_erp_dev`
  - database: `facebook_erp_dev`
- Direct Django database connection passed.
- `current_user` is `facebook_erp_dev`.
- `current_database` is `facebook_erp_dev`.
- PostgreSQL server version is `18.4`.
- `python manage.py check` passed.
- `python manage.py migrate --check` passed.
- `python manage.py showmigrations` passed.
- Default Django migrations are applied.
- `python manage.py test config -v 2` passed with 1 test.
- Local Django server starts successfully.
- Previous `social_commerce` credential blocker is resolved.

### P1.5 verification

- Root route returns HTTP `200`.
- Unknown route returns HTTP `404`, not `500`.
- `base.html` and `shell/home.html` render successfully.
- `static/css/app.css` is found by Django.
- `/static/css/app.css` returns HTTP `200` with CSS content.
- Shell includes application identity, Dashboard direction, Products direction, Add product placeholder, Account placeholder, Sign out placeholder, main landmark, page heading, message region, and active navigation indication.
- Disabled future controls use valid placeholder semantics and do not claim that later-phase functionality exists.
- Shell is a private seller-workspace foundation, not a storefront, marketing page, broad ERP, order, payment, delivery, or analytics UI.
- Minor mobile navigation clipping and final responsive polish are deferred UX refinements, not P1.5 blockers.
- Authentication, Product CRUD, Account, Sign out, dashboard data, Product Workspace behavior, and HTMX interactions remain later-phase functionality.

### P1.6 local verification

- `.github/workflows/django.yml` exists in the repository and is the only source file from the P1.6 implementation.
- Workflow uses GitHub Actions on push and pull request to `main`.
- Workflow uses a disposable PostgreSQL service with no repository secrets.
- Workflow preserves the PostgreSQL-only settings boundary through `config.settings.test`.
- Local verification results from the P1.6 implementation and integrity audit:
  - `.venv/bin/python -m pip check` passed with `No broken requirements found.`
  - `.venv/bin/python manage.py check --settings=config.settings.test` passed with no issues.
  - `.venv/bin/python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `.venv/bin/python manage.py migrate --check --settings=config.settings.test` passed with no output.
  - `.venv/bin/python manage.py test --settings=config.settings.test -v 2` passed with 1 test.
- GitHub Actions run `30537591111` completed with `status: completed` and `conclusion: success`.
- README now reflects that CI is configured and passing; no badge was added.

### P2.1 verification

- P2.1 Accounts App and Custom Seller User Model Baseline implementation exists locally.
- Owner-approved PostgreSQL unblock completed after the initial audit:
  - disposable local development database `facebook_erp_dev` was rebuilt with no seller or product data to preserve;
  - local-only role `facebook_erp_dev` can create and destroy the test database for local verification;
  - existing ignored `.env` credentials were preserved;
  - production configuration was not modified;
  - SQLite was not introduced.
- Files created by P2.1:
  - `accounts/__init__.py`
  - `accounts/apps.py`
  - `accounts/models.py`
  - `accounts/admin.py`
  - `accounts/tests.py`
  - `accounts/migrations/__init__.py`
  - `accounts/migrations/0001_initial.py`
- Files modified by P2.1:
  - `config/settings/base.py`
- Scope audit result:
  - `accounts.User` is a minimal custom email-based seller identity model.
  - `AUTH_USER_MODEL` is set to `accounts.User`.
  - No Business model, login/logout UI, route protection, Product CRUD, domain model, HTMX behavior, Tailwind tooling, deployment configuration, public catalog, chatbot, orders, payments, delivery, broad ERP, or AI-truth behavior was added.
- Verification commands run during P2.1 post-unblock integrity audit:
  - `source .venv/bin/activate && python manage.py check` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py check --settings=config.settings.test` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py migrate --check` passed with no output.
  - `source .venv/bin/activate && python manage.py showmigrations` showed all `accounts`, `admin`, `auth`, `contenttypes`, and `sessions` migrations applied.
  - `source .venv/bin/activate && python manage.py showmigrations --plan` showed `accounts.0001_initial` applied before `admin.0001_initial`.
  - `source .venv/bin/activate && python manage.py shell -c "<user model check>"` resolved `accounts.User`, `USERNAME_FIELD` as `email`, no accidental `auth.User`, and no `username` field.
  - `source .venv/bin/activate && python manage.py test accounts --settings=config.settings.test -v 2` created `test_facebook_erp_dev`, applied the clean migration graph, ran 5 tests, passed, and destroyed the test database.
  - `source .venv/bin/activate && python manage.py test --settings=config.settings.test -v 2` created `test_facebook_erp_dev`, applied the clean migration graph, ran 6 tests, passed, and destroyed the test database.
- Resolved blockers:
  - Previous `InconsistentMigrationHistory` is resolved.
  - Previous test database permission blocker is resolved.
  - Local `CREATEDB` permission is documented as a local test-environment capability only, not a production database role policy.
- Result: P2.1 is `PASSED`.

### P2.2 verification

- P2.2 Business Model and Ownership Boundary Baseline implementation exists locally.
- Files created by P2.2:
  - `businesses/__init__.py`
  - `businesses/apps.py`
  - `businesses/models.py`
  - `businesses/admin.py`
  - `businesses/tests.py`
  - `businesses/migrations/__init__.py`
  - `businesses/migrations/0001_initial.py`
- Files modified by P2.2:
  - `config/settings/base.py`
- Scope audit result:
  - `businesses.Business` is a minimal ownership boundary with `owner`, `name`, `created_at`, and `updated_at`.
  - `Business.owner` targets `settings.AUTH_USER_MODEL`, which resolves to `accounts.User`.
  - The migration depends on `migrations.swappable_dependency(settings.AUTH_USER_MODEL)`.
  - No active business resolver, switcher, login/logout UI, route protection, owner-scoped query helper, Product CRUD, domain model, HTMX behavior, Tailwind tooling, deployment configuration, public catalog, chatbot, orders, payments, delivery, broad ERP, or AI-truth behavior was added.
- Verification commands run during P2.2 implementation and integrity audit:
  - `source .venv/bin/activate && python manage.py check` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py check --settings=config.settings.test` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py test businesses --settings=config.settings.test -v 2` ran 4 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test --settings=config.settings.test -v 2` ran 10 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py shell -c "<business owner model check>"` resolved both `get_user_model()` and `Business.owner` to `accounts.User`; `Business.owner.on_delete` is `PROTECT`.
- Result: P2.2 is `PASSED`.

### P2.3 verification

- P2.3 Login Flow Baseline implementation exists locally.
- Files created by P2.3:
  - `accounts/forms.py`
  - `accounts/views.py`
  - `accounts/urls.py`
  - `templates/accounts/login.html`
- Files modified by P2.3:
  - `accounts/tests.py`
  - `config/settings/base.py`
  - `config/tests.py`
  - `config/urls.py`
  - `config/views.py`
  - `static/css/app.css`
  - `templates/base.html`
  - `BUILD_PLAN.md`
  - `DEVELOPMENT_NOTES.md`
  - `README.md`
  - `changelog_checkpoint.md`
- Scope audit result:
  - Minimal server-rendered email/password login and POST logout were added for the existing custom user model.
  - The root shell is protected by Django authentication and anonymous users are redirected to the login page.
  - Safe internal `next` redirects are allowed and unsafe external redirects are rejected through Django auth behavior.
  - Anonymous users do not see seller navigation before authentication.
  - No signup, password reset, email verification, social auth, demo account, Business selector/resolver, owner-scoped query helper, cross-business access matrix, Product CRUD, domain model, HTMX behavior, Tailwind tooling, deployment configuration, public catalog, chatbot, orders, payments, delivery, broad ERP, or AI-truth behavior was added.
- Verification commands run during P2.3 implementation and integrity audit:
  - `source .venv/bin/activate && python manage.py check` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py check --settings=config.settings.test` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py test accounts --settings=config.settings.test -v 2` ran 13 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test config --settings=config.settings.test -v 2` ran 2 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test --settings=config.settings.test -v 2` ran 19 tests, passed, and created/destroyed `test_facebook_erp_dev`.
- Result: P2.3 is `PASSED`.

### Environment-Gated Demo Seller Access Bootstrap verification

- Environment-Gated Demo Seller Access Bootstrap implementation exists locally.
- Files created by this support slice:
  - `accounts/management/__init__.py`
  - `accounts/management/commands/__init__.py`
  - `accounts/management/commands/seed_demo_user.py`
- Files modified by this support slice:
  - `.env.example`
  - ignored local `.env`
  - `accounts/tests.py`
  - `accounts/views.py`
  - `config/settings/base.py`
  - `templates/accounts/login.html`
  - `DEVELOPMENT_NOTES.md`
  - `changelog_checkpoint.md`
- Scope audit result:
  - Demo access is disabled by default through environment-backed settings.
  - Committed configuration contains placeholders only.
  - The ignored local `.env` enables the approved synthetic demo seller for local/manual verification and must not be staged.
  - The demo seller account is created or reset only by the explicit `seed_demo_user` management command.
  - The command uses `accounts.User`, normalizes email, hashes the configured password with Django password handling, forces active regular-user flags, and does not print the configured password or password hash.
  - The login page displays demo credentials only when demo access is enabled and fully configured.
  - No data migration, automatic startup seed, Business object, Product CRUD, owner-scoped query helper, public registration, password reset, email verification, auth bypass, HTMX behavior, Tailwind tooling, deployment configuration, public catalog, chatbot, orders, payments, delivery, broad ERP, or AI-truth behavior was added.
- Verification commands run during implementation and integrity audit:
  - `source .venv/bin/activate && python manage.py check` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py check --settings=config.settings.test` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py seed_demo_user` passed and reported `Demo user updated.`
  - `source .venv/bin/activate && python manage.py shell -c "<demo user boolean auth check>"` confirmed the local synthetic demo user exists, is active, is not staff, is not superuser, and authenticates successfully.
  - `source .venv/bin/activate && python manage.py shell -c "<plaintext password boolean check>"` confirmed the configured demo password is not stored as plaintext.
  - `source .venv/bin/activate && python manage.py test accounts --settings=config.settings.test -v 2` ran 22 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test --settings=config.settings.test -v 2` ran 28 tests, passed, and created/destroyed `test_facebook_erp_dev`.
- Result: Environment-Gated Demo Seller Access Bootstrap is `PASSED`.

### P2.4 verification

- P2.4 Owner-Scoped Query Helper Baseline implementation exists locally.
- Files created by P2.4:
  - `businesses/selectors.py`
- Files modified by P2.4:
  - `businesses/tests.py`
- Scope audit result:
  - `businesses_owned_by(user)` returns only businesses owned by an authenticated seller and returns an empty queryset for anonymous users.
  - `resolve_active_business(user)` returns `None` when the seller owns no Business, returns the only owned Business when exactly one exists, and raises `MultipleBusinessesUnsupported` when multiple businesses exist because an active-business switcher/policy is not owner-approved.
  - `get_owned_business_or_404(user, business_id)` returns an owned Business by id and raises `Http404` for another seller's Business without leaking the object.
  - No Business creation, Business switcher, onboarding flow, shell integration, Product CRUD, catalog model, domain model, HTMX behavior, Tailwind tooling, deployment configuration, public catalog, chatbot, orders, payments, delivery, broad ERP, stock/lifecycle/availability logic, or AI-truth behavior was added.
- Verification commands run during implementation and integrity audit:
  - `source .venv/bin/activate && python manage.py check` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py check --settings=config.settings.test` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py test businesses --settings=config.settings.test -v 2 --noinput` ran 11 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test config --settings=config.settings.test -v 2 --noinput` ran 2 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test --settings=config.settings.test -v 2 --noinput` ran 35 tests, passed, and created/destroyed `test_facebook_erp_dev`.
- Verification note:
  - An initial parallel launch of multiple Django test commands collided on the shared PostgreSQL test database and produced `database "test_facebook_erp_dev" already exists`; this was a verification-process issue, not a code failure. The required tests were rerun sequentially with `--noinput` and passed.
- Result: P2.4 Owner-Scoped Query Helper Baseline is `PASSED`.

### P2.5 verification

- P2.5 Cross-Business Access Test Baseline implementation exists locally.
- Files created by P2.5:
  - none
- Files modified by P2.5:
  - `businesses/tests.py`
- Scope audit result:
  - Business selector coverage now explicitly proves `resolve_active_business(user)` ignores another seller's Business and returns `None` rather than leaking or creating a workspace.
  - `get_owned_business_or_404(user, business_id)` returns `Http404` for missing ids and for anonymous lookup of an existing seller-owned Business.
  - Existing tests continue to prove owner-only queryset scoping, single-owned-business resolution, no Business auto-creation, multiple-business ambiguity, and cross-owner 404 behavior.
  - No Business switcher, onboarding flow, route/view integration, Product CRUD, catalog model, domain model, migration, HTMX behavior, Tailwind tooling, deployment configuration, public catalog, chatbot, orders, payments, delivery, broad ERP, stock/lifecycle/availability logic, or AI-truth behavior was added.
- Verification commands run during implementation and integrity audit:
  - `source .venv/bin/activate && python manage.py check` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py check --settings=config.settings.test` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py test businesses --settings=config.settings.test -v 2 --noinput` ran 14 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test --settings=config.settings.test -v 2 --noinput` ran 38 tests, passed, and created/destroyed `test_facebook_erp_dev`.
- Result: P2.5 Cross-Business Access Test Baseline is `PASSED` locally.

## 6. Current Blockers

- No current P1 blocker remains.
- No current P2.1 blocker remains.
- No current P2.2 blocker remains.
- No current P2.3 blocker remains.
- No current demo-access bootstrap blocker remains.
- No current P2.4 blocker remains.
- No current P2.5 blocker remains.
- The old P2.1 local migration-history blocker is `RESOLVED`.
- The old P2.1 test database permission blocker is `RESOLVED`.
- Existing remote initial README commit must remain preserved.
- No force push is allowed.
- Gate 1 is passed after local P1.6 checks and successful GitHub Actions verification.
- Gate 2 is passed locally after P2.5 access-control tests; P2.5 Git checkpoint and CI remain pending.
- Do not proceed to P3.1 Product Model Baseline implementation until the owner approves the next-step report.
- OWNER_DECISION_REQUIRED items remain:
  - final project/repository name;
  - license;
  - one-business-per-seller policy versus active business switcher policy;
  - Product Detail inclusion;
  - product relations inclusion;
  - clone inclusion and stock-copy policy;
  - archive/restore inclusion and hidden/archive terminology;
  - type/tag management page inclusion;
  - tag readiness policy;
  - price zero/null/missing/free policy;
  - duplicate size/color choice policy;
  - exact material confirmation UI and alias policy;
  - measurement micro-slice timing, convention, and product/choice boundary;
  - fit guidance inclusion and wording if approved later;
  - direct stock set placement;
  - dashboard first-viewport priority;
  - ready reply placement;
  - final Georgian terminology;
  - deployment provider and demo access model.

## 7. Next Concrete Micro-Slice

Phase 2 has passed locally. P2.1, P2.2, P2.3, the Environment-Gated Demo Seller Access Bootstrap, P2.4, and P2.5 have passed.

Next concrete step after the P2.5 Git checkpoint: prepare the next-step report for P3.1 Product Model Baseline, derived from the Phase 3 expected micro-slice order in `BUILD_PLAN.md`.

Do not implement P3.1 until owner approval. The P3.1 report must surface any owner decision required by product price or lifecycle scope instead of resolving it silently.

## 8. Scope Guardrails

- Build from zero.
- Do not copy source prototype code, migrations, media, database, or private config.
- Keep V1 seller-side and source-of-truth focused.
- Defer public catalog, chatbot, orders, payments, delivery, accounting, supplier management, broad ERP, and microservices.
- Do not stage, commit, push, or implement code until owner approval.
- Do not force push or replace remote history.

## 9. Known Risks

- Existing remote initial commit must remain preserved.
- README must remain honest until seller features and the online demo actually exist; CI is now configured and verified.
- Prototype behavior may tempt scope creep if copied wholesale.
- Source project contains media/backups and `.env`; these must not be copied or published.
- Future demo must use synthetic data only.
- Measurement implementation can easily bloat the first product form unless kept as a separate approved micro-slice.
- Minor shell mobile navigation clipping is deferred UX refinement, not a P1.5 blocker.
- Local PostgreSQL `CREATEDB` is allowed only for this local test-environment role; it is not a production database role policy.
- Multiple businesses per seller are blocked by the P2.4 resolver until an owner-approved active-business policy or switcher exists.

## 10. Documentation Priority for New Chats

1. `changelog_checkpoint.md`
2. `BUILD_PLAN.md`
3. `APP_EXPERIENCE_PLAN.md`
4. `DEVELOPMENT_NOTES.md`
5. `docs/Portfolio_MVP_V1.md`
6. `docs/Technical_Planning_v1.md`
7. `docs/domain/CLOTHING_DATA_SPEC_V1.md`
8. `docs/User_Journey_Freeze_v1.md`
9. relevant source files
10. `README.md` for public context only

Private local prompt:

- `codex_prompt_ERP.txt` may be used by the owner to drive Codex workflow prompts.
- It is not repository authority and must not be staged or committed.

## 11. Last Operation

- Operation: P2.5 Cross-Business Access Test Baseline implementation and integrity audit.
- Files created by this operation:
  - none
- Files modified by this operation:
  - `businesses/tests.py`
  - `BUILD_PLAN.md`
  - `changelog_checkpoint.md`
- Files intentionally not modified:
  - frozen docs under `docs/`
  - `APP_EXPERIENCE_PLAN.md`
  - `DEVELOPMENT_NOTES.md`
  - `README.md`
  - `.github/workflows/django.yml`
  - `.gitignore`
  - `manage.py`
  - `accounts/`
  - `config/`
  - `templates/`
  - `static/`
  - Product/catalog modules
  - `codex_prompt_ERP.txt`
- Source project modified: no.
- Scope audit result: the operation remained limited to Business selector access tests plus live planning/checkpoint status sync; no selector code, models, migrations, dependencies, README, frozen docs, UI, deployment configuration, Business switcher, onboarding, Product CRUD, catalog model, HTMX behavior, public catalog, chatbot, orders, payments, delivery, broad ERP, stock/lifecycle/availability logic, deterministic replies, or AI-truth behavior was added.
- Verification commands run during P2.5 implementation and integrity audit:
  - `source .venv/bin/activate && python manage.py check` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py check --settings=config.settings.test` passed with `System check identified no issues (0 silenced).`
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py makemigrations --check --dry-run --settings=config.settings.test` passed with `No changes detected`.
  - `source .venv/bin/activate && python manage.py test businesses --settings=config.settings.test -v 2 --noinput` ran 14 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - `source .venv/bin/activate && python manage.py test --settings=config.settings.test -v 2 --noinput` ran 38 tests, passed, and created/destroyed `test_facebook_erp_dev`.
  - Public GitHub Actions API showed run `30626190659` completed successfully for committed `HEAD` `41cbd3e62f55f40d432b7ed12b07fb4a2d957b29`; P2.5 is not yet committed, so CI has not run for P2.5.
  - Documentation drift firewall checks confirmed `changelog_checkpoint.md` and `BUILD_PLAN.md` agree that Phase 2 is passed locally and P3.1 Product Model Baseline next-step reporting is next after the P2.5 Git checkpoint.
- Known issues from this operation:
  - Online demo is not deployed.
  - Multiple businesses per seller remain unsupported by the resolver until an owner-approved active-business policy or switcher exists.
  - P3.1 Product Model Baseline requires an owner-approved next-step report before implementation.
  - P2.5 source/test/doc changes are not yet committed or pushed.
- Result: Phase 2 is `PASSED` locally; P2.5 Cross-Business Access Test Baseline is implemented, locally verified, and `PASSED`; repository is ready for Git checkpoint review but P2.5 is not yet committed or pushed.

## 12. Git Checkpoint

- Git repository initialized: yes
- Current branch: `main`
- Branch tracking: `main...origin/main`
- Latest committed checkpoint before current P2.5 implementation: `41cbd3e docs: sync checkpoint after p2.4 push`
- Last known committed `HEAD` before a future P2.5 commit: `41cbd3e62f55f40d432b7ed12b07fb4a2d957b29`
- Last known `origin/main` before a future P2.5 commit: `41cbd3e62f55f40d432b7ed12b07fb4a2d957b29`
- Last known actual remote `main` before a future P2.5 commit: `41cbd3e62f55f40d432b7ed12b07fb4a2d957b29`
- Remote configured locally: yes, `ssh://git@ssh.github.com:443/OSINTmedia/facebook_ERP.git`
- GitHub repository exists: yes, `https://github.com/OSINTmedia/facebook_ERP`
- GitHub repository visibility: public
- GitHub default branch: `main`
- Remote history: preserved initial README commit `dce852b`; baseline commit `549db75`, clothing scope commit `9f5a5e2`, governance commit `accc24b`, Phase 1 readiness checkpoint commit `0c04cbd`, checkpoint sync commit `1048175`, dependency baseline commit `69e968e`, scaffold commit `4914f2b`, settings commit `a01e246`, PostgreSQL baseline commit `323c268`, P1.4/P1.5 runtime-shell checkpoint commit `dc21677`, P1.6 CI workflow commit `23fb3ca`, P1.6 documentation sync commit `41b6fe4`, P2.1 custom user baseline commit `54d8bfc`, P2.2 business ownership baseline commit `a3d19cc`, P2.3 login flow baseline commit `9f8fb8c`, demo-access bootstrap commit `bfaacae`, repository handoff checkpoint commit `66a143a`, P2.4 owner-scoped query helper commit `6b88e8b`, and P2.4 post-push checkpoint sync commit `41cbd3e` pushed on top.
- Push status: latest committed checkpoint `41cbd3e` was pushed normally to `origin/main`; no force push was used.
- Current uncommitted P2.5 state:
  - `businesses/tests.py` is modified by P2.5 cross-business access tests.
  - `BUILD_PLAN.md` and `changelog_checkpoint.md` are modified for documentation sync.
  - Current branch is `main`.
  - Committed `HEAD`, `origin/main`, and actual remote `main` are aligned before this P2.5 implementation commit.
- Documentation checkpoint state:
  - P2.5 Cross-Business Access Test Baseline is implemented, locally verified, and marked `PASSED`.
  - P2.5 source/test/doc changes are not yet committed or pushed.
  - Exact staged, committed, and pushed state must be read from Git commands.
- Ignored local files:
  - `.env`, `.venv/`, Python cache, and `codex_prompt_ERP.txt` remain ignored local files.
- Exact current `HEAD` after any future P2.5 commit must be read from Git; do not hardcode a future commit hash into this checkpoint.

## 13. Handoff Instruction

A new Codex chat must:

1. read this file first;
2. verify branch, `HEAD`, `origin/main`, and working tree state with Git commands;
3. confirm P1.1 through P1.6 are `PASSED`;
4. confirm Gate 1 is passed, Phase 2 is locally `PASSED`, P2.1 through P2.5 and the Environment-Gated Demo Seller Access Bootstrap are `PASSED`;
5. if the working tree contains only the P2.5 source/test/doc changes listed in the Git Checkpoint, proceed only with owner-approved Git checkpoint for P2.5;
6. after the P2.5 implementation is committed and pushed, prepare the next-step report for P3.1 Product Model Baseline;
7. if the working tree is already clean and aligned after P2.5 commit/push, the standard new-chat pre-prompt may be used before P3.1 planning;
8. do not implement P3.1 until owner approval.
