# Social Commerce Seller Operations Assistant

## One-Sentence Definition

A seller-first catalog and inventory cockpit for small Facebook and Instagram sellers who need reliable product, choice, stock, readiness, and buyer-answer data before any public catalog or automation layer can be trusted.

## Why This Project Exists

Small social-commerce sellers often manage product details, stock, buyer questions, and availability through memory, Messenger threads, Instagram DMs, spreadsheets, and photos. That creates stale product information, repeated buyer questions, missed sold-out states, and avoidable manual work.

This project focuses on making seller-maintained catalog truth practical enough for daily use.

## Why Seller-First

Public catalogs, chatbots, orders, payments, and delivery workflows are only useful if the underlying product truth is reliable. Price, size, color, stock, lifecycle, and availability must come from seller-maintained data and deterministic application logic, not from guesses or an LLM.

## Portfolio Purpose

This rebuild is intended to demonstrate:

- product reasoning before implementation;
- seller workflow analysis;
- Django and Python engineering;
- relational data modeling;
- source-of-truth and state-boundary design;
- operational UI/UX discipline;
- testing and failure-path planning;
- documentation-first development;
- AI-assisted but owner-controlled engineering workflow;
- honest Git/GitHub history;
- online demo readiness after deployment is approved and implemented.

## Current Status

Status: Planning and documented rebuild.

- Product discovery completed from an earlier private prototype.
- Owner-controlled planning documents are frozen for the Phase 1 starting baseline.
- Implementation has not started.
- GitHub repository already exists at `https://github.com/OSINTmedia/facebook_ERP`.
- The GitHub repository is public, uses default branch `main`, and preserves the initial README commit `dce852b`.
- Documentation baseline commit `549db75 docs: add portfolio rebuild planning baseline` has been pushed.
- Local Git repository is initialized.
- Local branch `main` tracks `origin/main`.
- Local remote is `ssh://git@ssh.github.com:443/OSINTmedia/facebook_ERP.git`.
- GitHub SSH authentication works through `ssh.github.com` on port `443`.
- CI is not configured yet.
- Online demo is not deployed yet.
- Existing remote history must be preserved; no force push is allowed.
- Future commits should continue the documented micro-slice workflow without rewriting history.

## Planned Portfolio V1

Frozen baseline scope:

- seller login and private workspace;
- business-owned product data;
- product creation and editing;
- description-first product input with lightweight semantic recognition;
- Product Type, Tag, and material confirmation from recognized seller wording;
- clothing-first size/color choices, with size/color truth stored on choices rather than generic tags;
- detailed garment measurements kept as a later approved micro-slice;
- variant-level stock as the stock source of truth;
- computed availability;
- operational product workspace;
- dashboard attention/readiness signals;
- deterministic seller-side buyer replies based only on stored facts;
- tests for critical ownership, state, inventory, and reply behavior;
- safe synthetic demo data and reset/reseed path before deployment.

Some prototype behaviors, including Product Detail, product relations, clone modes, archive/restore, direct stock set, and separate type/tag management pages, remain owner-decision-required and are not included automatically in the frozen baseline scope.

## Explicit Non-Goals

Portfolio V1 does not include:

- public buyer catalog implementation;
- chatbot or messaging integration;
- LLM-based product truth;
- orders or reservations;
- payments;
- delivery workflow;
- accounting;
- supplier management;
- analytics BI;
- multi-staff permission system;
- broad ERP functionality;
- microservices;
- fake pilot/adoption metrics.

## Architecture Direction

The proposed direction is a Django modular monolith with PostgreSQL, Django Templates, HTMX for small server-truth updates, Alpine.js for local UI state, and Tailwind CSS for a compact mobile-first seller interface.

The architecture will keep lifecycle, availability, readiness, and buyer-answer readiness separate. Stock changes should go through one inventory service and create a complete adjustment trail.

## Development Workflow

The rebuild follows a documentation-first micro-slice workflow:

1. read the live checkpoint;
2. confirm the active micro-slice;
3. get owner approval;
4. implement only the approved slice;
5. run automated verification;
6. perform manual owner testing where needed;
7. audit scope, UX, security, and regression risk;
8. update documentation;
9. commit with one clear intention;
10. update the checkpoint for the next chat.

## AI-Assisted Development

AI supports analysis, planning, implementation drafts, testing suggestions, audits, and documentation.

The owner controls product scope, architecture approval, acceptance criteria, source review, manual testing, Git approval, release timing, and deployment decisions.

AI output is not trusted without source inspection and verification. An LLM must not be the source of truth for price, stock, size, color, availability, lifecycle, or ownership.

## Documentation Map

- [Portfolio_MVP_V1.md](docs/Portfolio_MVP_V1.md)
- [Technical_Planning_v1.md](docs/Technical_Planning_v1.md)
- [User_Journey_Freeze_v1.md](docs/User_Journey_Freeze_v1.md)
- [CLOTHING_DATA_SPEC_V1.md](docs/domain/CLOTHING_DATA_SPEC_V1.md)
- [APP_EXPERIENCE_PLAN.md](APP_EXPERIENCE_PLAN.md)
- [DEVELOPMENT_NOTES.md](DEVELOPMENT_NOTES.md)
- [BUILD_PLAN.md](BUILD_PLAN.md)
- [changelog_checkpoint.md](changelog_checkpoint.md)

Internal discovery evidence also exists in `docs/discovery/DISCOVERY_REPORT.md`, `docs/discovery/backend.md`, and `docs/discovery/frontend.md`.

## Online Demo

Not deployed yet.

Demo URL: not available yet.

The future demo must use synthetic data, no real seller/customer data, no source prototype media, production-safe settings, and a backend-capable hosting environment.

## Local Setup

Application setup instructions will be added after the foundation phase creates and verifies the clean Django project.

No setup commands are listed yet because implementation has not started.

## Roadmap Summary

1. Documentation governance and baseline freeze.
2. Repository foundation and hygiene.
3. Django/PostgreSQL foundation and CI.
4. User and Business ownership.
5. Product semantic recognition and clothing choice model.
6. Inventory and computed availability.
7. Product workspace and dashboard.
8. Deterministic seller replies.
9. UX stabilization and portfolio hardening.
10. Deployment and public release.

## License / Portfolio Notice

License: OWNER_DECISION_REQUIRED.

This repository is intended as a portfolio rebuild. Licensing and reuse terms must be approved by the owner before public release.

## Project History Note

An earlier private discovery prototype was used to investigate seller workflows, backend state boundaries, UI risks, and product scope. This repository is a clean portfolio-grade rebuild from that evidence.

The GitHub repository preserves the initial README commit `dce852b`, followed by the first substantive rebuild-planning commit `549db75`. Historical commits are not being fabricated or backdated, and future work must preserve the existing remote history.
