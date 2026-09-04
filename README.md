# system-reporter-api

A small FastAPI-based service that collects and exposes simple system reports backed by PostgreSQL.

Contents
- Overview
- Quick start (Docker)
- Local development
- Tests
- File-by-file senior-level walkthrough
- Deployment notes

Overview
This repository implements a lightweight metrics collection API. It provides endpoints to ingest system reports and to query stored reports. The API uses SQLAlchemy for ORM models, Pydantic schemas for validation, and PostgreSQL as the persistence layer.

Quick start (Docker)
1. Ensure Docker and Docker Compose are installed.
2. From the repository root run:

```bash
docker compose up --build
```

This starts two services:
- `db`: Postgres 16 (volume-backed)
- `api`: the FastAPI application (exposed on port 8000)

Local development
- Python requirements are in `requirements.txt`.
- The app reads `DATABASE_URL` from the environment; `docker-compose.yaml` sets this for the `api` service.
- To run locally without Docker, create a virtualenv, install requirements, and set `DATABASE_URL` to a running Postgres instance.

Tests
- Tests live in `tests/test_api.py`. Run them with:

```bash
pytest -q
```

Senior-level code walkthrough
Below are concise, technical explanations of the main modules and design choices. If you want deeper changes or refactors, tell me which area to prioritize.

- `app/main.py`: Entrypoint that builds and runs the FastAPI application. It wires routes, middleware, and startup/shutdown events. Keep this file thin: application composition only, business logic lives elsewhere.

- `app/__init__.py`: Package initializer. Ensures the `app` package is importable; may expose the `create_app()` or `app` instance depending on implementation.

- `app/collector.py`: Responsible for collecting incoming payloads and any lightweight enrichment prior to persistence. This is a good place for input normalization, timestamping, and lightweight validation that supplements Pydantic schema checks.

- `app/crud.py`: Implements the database operations (Create, Read, Update, Delete) using SQLAlchemy sessions. Keep transactions short and explicit here; return lightweight domain objects or ORM models but avoid embedding request/response concerns in CRUD functions.

- `app/database.py`: Sets up the SQLAlchemy engine, session factory, and any helpers for transactional scope. Prefer explicit session management (dependency injection into endpoints) and ensure sessions are closed on request finish.

- `app/models.py`: SQLAlchemy model definitions that map to Postgres tables. Use explicit column types, indexes for query-heavy fields, and declarative constraints. Models are the single source of truth for persistence schema.

- `app/schemas.py`: Pydantic models for request validation and response serialization. Keep these separate from ORM models to avoid accidental DB coupling. Use response models on FastAPI routes to control what is exposed via the API.

- `app/crud.py` & `app/schemas.py` separation rationale: Schemas validate and sanitize external input, CRUD functions accept validated schemas or dicts and return ORM models, and route layer is responsible for converting ORM models back to response schemas.

- `tests/test_api.py`: Integration-style tests for the API surface. They demonstrate expected endpoints and responses. Prefer test fixtures that spin up a test database or use transactional rollbacks to keep tests hermetic.

Key design notes and recommendations
- Keep business logic out of request handlers: route handlers should orchestrate validation (schemas), persistence (crud), and any background work (collector or tasks).
- Use dependency injection to manage DB sessions in FastAPI (one session per request pattern).
- Add proper logging and structured logs for production debugging; avoid print statements.
- Add alembic for schema migrations if you expect schema evolution; for small projects it's tempting to use `create_all()` but migrations are safer long-term.

Next steps I can take for you
- Add a more detailed architecture diagram.
- Add CI steps and a GitHub Actions workflow for tests and linting.
- Add Alembic and a migration example.

If you'd like, I can now run the test suite and/or add a `docker-compose.override.yml` for development.
