# facebook_MVP

Stage 0 scaffold for the Solo Clothing Inventory Cockpit MVP-Freeze v0.1.

## Local setup

1. Create and activate the virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy environment example:
   - `cp .env.example .env`
4. Update `DATABASE_URL` in `.env` for your local PostgreSQL instance.
5. Run migrations:
   - `python manage.py migrate`
6. Create an admin user:
   - `python manage.py createsuperuser`
7. Start the development server:
   - `python manage.py runserver`

## Current scope

This repository is currently scaffolded only for:

- Django + PostgreSQL foundation
- custom email-login user model
- app/module structure for the inventory cockpit MVP
- templates/static/media/admin foundation

Stage 1 adds the initial business/catalog/inventory models.

