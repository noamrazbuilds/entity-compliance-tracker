# Entity Compliance Tracker

Centralized registry for corporate entities and subsidiaries with compliance calendar, interactive org chart, and automated deadline reminders.

Built for in-house legal teams, legal ops, and paralegals who manage corporate entity portfolios.

---

## Getting Started

### Option 1: Hosted Version

> Coming soon — a hosted instance will be available at a public URL.

### Option 2: Run Locally (One Command)

**macOS / Linux:**
```bash
git clone https://github.com/lquantprojects/entity-compliance-tracker.git
cd entity-compliance-tracker
./start.sh
```

**Windows:**
```cmd
git clone https://github.com/lquantprojects/entity-compliance-tracker.git
cd entity-compliance-tracker
start.bat
```

This will:
- Create a virtual environment and install dependencies (first run only)
- Start the API and frontend
- Open the app in your browser at `http://localhost:8501`
- Load sample data automatically on first run

### Option 3: Docker

```bash
docker compose up
```

- Frontend: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Deploy Your Own

### Railway (One-Click Cloud Deploy)

1. Fork this repo
2. Connect your GitHub to [Railway](https://railway.app)
3. Create a new project from your fork
4. Railway will auto-detect the `railway.json` config and deploy

---

## Features

### Entity Registry
- Centralized records for all corporate entities: name, jurisdiction, type, formation date, registered agent, officers/directors, filings, governance documents
- Full CRUD with search and filters
- Good-standing status tracking

### Compliance Calendar
- Calendar and list views of all filing deadlines across entities
- Color-coded urgency: overdue (red), due soon (orange/yellow), on track (green)
- Filter by entity, jurisdiction, filing type, date range

### Dashboard
- Portfolio-wide compliance overview
- Key metrics: total entities, upcoming deadlines, overdue items, good standing percentage
- Charts by jurisdiction and entity type

### Interactive Org Chart
- D3.js-powered visual corporate structure
- Collapsible tree with zoom and pan
- Color-coded by entity type
- Ownership percentages on links

### Automated Reminders
- Email (SMTP) and Slack (webhook) notifications
- Configurable reminder intervals (default: 30, 14, 7 days before deadline)
- Global defaults with per-entity overrides
- Deduplication to prevent repeat notifications

---

## For Developers

### Project Structure

```
ect_app/                  # FastAPI backend
├── main.py               # App factory, lifespan, router mounting
├── config.py             # Pydantic settings
├── database.py           # SQLAlchemy engine, session, Base
├── models/               # ORM models
├── schemas/              # Pydantic schemas
├── routers/              # API route handlers
├── services/             # Business logic
└── notifications/        # Email, Slack, scheduler

ect_frontend/             # Streamlit frontend
├── app.py                # Main app entry
├── pages/                # Dashboard, Registry, Calendar, Org Chart, Settings
├── components/           # D3.js org chart component
└── utils/                # API client, formatters

data/sample/              # Synthetic sample data
tests/                    # pytest tests
```

### API Documentation

Start the API and visit http://localhost:8000/docs for interactive Swagger documentation.

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Frontend:** Streamlit
- **Database:** SQLite (prototype), PostgreSQL-ready
- **Org Chart:** D3.js v7
- **Notifications:** APScheduler, aiosmtplib, Slack webhooks
- **Deployment:** Docker, Railway

---

## License

MIT License — Copyright (c) 2026 Noam Raz and Pleasant Secret Labs
