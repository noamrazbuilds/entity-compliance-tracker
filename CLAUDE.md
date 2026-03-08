# CLAUDE.md — Entity Compliance Tracker

## Project Overview

Corporate Entity & Subsidiary Compliance Tracker — a centralized registry for corporate entities with compliance calendar, org chart visualization, and automated deadline reminders. Part of the Legal Quant portfolio.

**Target users:** Non-technical legal professionals (in-house counsel, legal ops, paralegals).
**Design principle:** "Can a lawyer with no engineering background use this in under 2 minutes?"

## Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Database:** SQLAlchemy 2.0 ORM with SQLite (prototype), designed for PostgreSQL migration
- **Frontend:** Streamlit (thin client calling API via HTTP)
- **Validation:** Pydantic v2
- **Testing:** pytest
- **Deployment:** Docker + Railway
- **Package management:** pyproject.toml (PEP 621)

## Architecture

**API-first:** FastAPI backend handles all business logic. Streamlit is a thin HTTP client.
- API is independently usable (Swagger docs, curl, integrations)
- Frontend can be swapped later without touching business logic

## Package Naming

This project uses prefixed package names to prevent module collisions across the portfolio:

| Standard | This project |
|---|---|
| `app/` | `ect_app/` |
| `frontend/` | `ect_frontend/` |

- Backend entry: `uvicorn ect_app.main:app`
- Frontend entry: `streamlit run ect_frontend/app.py`
- Imports: `from ect_app.config import settings`

## Project Structure

```
entity-compliance-tracker/
├── ect_app/                  # FastAPI backend
│   ├── main.py               # App factory, middleware, router mounting
│   ├── config.py             # Settings via pydantic-settings
│   ├── database.py           # SQLAlchemy engine, session, Base
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── routers/              # FastAPI route modules
│   ├── services/             # Business logic layer
│   └── notifications/        # Email/Slack reminder logic
├── ect_frontend/             # Streamlit frontend
│   ├── app.py                # Main Streamlit app
│   ├── pages/                # Streamlit multipage app pages
│   └── utils/                # API client, helpers
├── data/
│   └── sample/               # Synthetic sample data (JSON)
├── tests/                    # pytest tests
├── start.sh                  # One-command launch (macOS/Linux)
├── start.bat                 # One-command launch (Windows)
├── Dockerfile                # API container
├── Dockerfile.railway        # Combined container for Railway
├── docker-compose.yml        # Multi-service local Docker
├── railway.json              # Railway deployment config
├── railway_start.sh          # Railway container startup
├── pyproject.toml            # PEP 621 package config
├── CLAUDE.md                 # This file
├── README.md                 # User-facing docs (non-technical first)
└── LICENSE                   # MIT — Copyright (c) 2026 Noam Raz and Pleasant Secret Labs
```

## Coding Conventions

- Type hints on all function signatures
- Pydantic v2 for all request/response validation
- SQLAlchemy 2.0 style: `mapped_column`, `DeclarativeBase`, `Mapped[]`
- FastAPI dependency injection for DB sessions
- Keep modules small and focused
- No over-engineering — minimum complexity for current requirements

## Dependency Classification

Core `[project.dependencies]` — required at runtime (FastAPI, uvicorn, SQLAlchemy, Pydantic, Streamlit, requests, etc.)
Dev `[project.optional-dependencies]` — testing/linting only (pytest, ruff, httpx for test client)
**Rule:** If Docker would crash without it, it's a core dependency.

## Security Considerations

- No authentication in MVP (single-user/team behind VPN)
- All user inputs validated via Pydantic before reaching the database
- SQLAlchemy ORM for all queries — no raw SQL to prevent injection
- CORS restricted to known origins in production
- No real company data in the repo — sample data only
- `.env` files excluded via .gitignore
- File upload paths sanitized if document storage is added
- Rate limiting on API endpoints in production deployment

## Git & Open Source

- MIT License: `Copyright (c) 2026 Noam Raz and Pleasant Secret Labs`
- Never commit real company data, client names, or internal policies
- `.gitignore` excludes: `.env`, `data/real/`, `data/*.db`, `data/generated/`, `__pycache__/`
- All sample data must be synthetic

## Key Commands

```bash
# Local development
./start.sh                              # One-command launch (API + frontend)
uvicorn ect_app.main:app --reload       # API only
streamlit run ect_frontend/app.py       # Frontend only

# Testing
pytest                                  # Run all tests
pytest tests/ -v                        # Verbose

# Docker
docker compose up                       # All services
docker compose up --build               # Rebuild and run

# Linting
ruff check .                            # Lint
ruff format .                           # Format
```

## Standards Reference

See PORTFOLIO_STANDARDS.md for cross-project patterns and conventions (gitignored — internal build context only).
