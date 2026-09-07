# FixNet Backend Service

[![CI Pipeline](https://github.com/fixnet-rwanda/fixnet-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/fixnet-rwanda/fixnet-backend/actions)
[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/django-5.1-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

FixNet is a digital platform connecting skilled technicians and clients across Rwanda. This repository hosts the core REST API, business logic engine, asynchronous task worker, and database models.

---

## 📚 Technical Documentation

The complete specifications from the design phase are version-controlled in the [`docs/`](docs/) directory:
- [API Design Specification (v1 REST endpoints)](docs/API_DESIGN_SPECIFICATION.md)
- [Authentication & Authorization Design (OTP, MFA & RBAC Matrix)](docs/AUTHENTICATION_AUTHORIZATION_DESIGN.md)
- [Business Logic Rules Detailed (Catalog AUTH-01 through ADMIN-04)](docs/BUSINESS_LOGIC_RULES.md)
- [Error Handling & Logging Strategy](docs/ERROR_HANDLING_LOGGING_STRATEGY.md)
- [Original Design Files & Customer DFD Flowchart](docs/design/)

---

## 🏗 System Architecture & Technology Stack

- **Framework**: Python 3.13 / Django 5.1 / Django REST Framework (DRF)
- **Authentication**: JWT (SimpleJWT with rotating refresh tokens), Passwordless SMS OTP, Admin TOTP MFA
- **Database**: PostgreSQL 16 (stored in integer RWF currency units to prevent floating-point inaccuracies)
- **Caching & Brokers**: Redis 7
- **Background Jobs**: Celery 5.4 (SMS failover, billing retries, AI embeddings)
- **WebSockets / Realtime**: Django Channels & channels-redis (in-app customer-technician negotiation)
- **Integrations**: MTN/Airtel Mobile Money aggregator, Africa's Talking / Twilio SMS, Firebase Cloud Messaging, Sentry

---

## 📁 Repository Structure

```text
fixnet-backend/
├── .github/workflows/ci.yml      # CI/CD Automated Test & Linting Pipeline
├── apps/
│   ├── users/                    # Auth, Custom User model, SMS OTP, Admin MFA
│   ├── technicians/              # Profiles, Verification Gate, Categories, Content
│   ├── conversations/            # Chat threads, Contact Masking, Quotes
│   ├── payments/                 # Booking Deposits, Webhook, MoMo, Subscriptions
│   ├── jobs/                     # Job Lifecycles, Re-booking, Ratings & Reviews
│   ├── admin_portal/             # Verification, Content Moderation, Disputes, Pricing
│   └── ai_assistant/             # AI Technician Assistant (RAG boundaries)
├── config/
│   ├── settings/
│   │   ├── base.py               # Shared settings & business constants
│   │   ├── development.py        # Local SQLite/Postgres & debug configs
│   │   └── production.py         # Production TLS, Sentry, Redis configs
│   ├── urls.py                   # Root /v1/ API URL routing
│   ├── asgi.py                   # ASGI application
│   ├── wsgi.py                   # WSGI application
│   └── celery.py                 # Celery app initialization
├── core/
│   ├── exceptions.py             # Standardized error response handler
│   ├── permissions.py            # RBAC permissions (IsCustomer, IsTechnician, etc.)
│   ├── middleware.py             # X-Request-ID correlation middleware
│   ├── pagination.py             # Limit/page pagination
│   └── utils.py                  # Regex contact masking utilities
├── docs/                         # Specifications and architecture docs
├── requirements/
│   ├── base.txt                  # Core dependencies
│   └── local.txt                 # Testing and linting tools
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Local dev stack (Web, DB, Redis, Celery)
├── manage.py                     # Django management script
└── README.md
```

---

## 🚀 Quickstart Guide

### Option 1: Running with Docker Compose (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/nshh123/fixnet-backend.git
   cd fixnet-backend
   ```

2. **Setup environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Start services**:
   ```bash
   docker compose up --build
   ```
   The API will be available at `http://localhost:8000/v1/`. Health check is at `http://localhost:8000/health/`.

---

### Option 2: Running Locally with Virtualenv

1. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements/local.txt
   ```

3. **Run database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Run development server**:
   ```bash
   python manage.py runserver
   ```

5. **Run test suite**:
   ```bash
   python manage.py test
   ```

---

## 🤝 Contributing Workflow

Please read [`CONTRIBUTING.pdf`](../CONTRIBUTING.pdf) for the full developer operating procedures.

### Golden Rules:
1. **Never push directly to `main` or `dev`**. All changes must go through a Pull Request.
2. Note: The staging branch is named **`dev`** (not `develop`).
3. Always create a feature branch off `dev`:
   ```bash
   git checkout dev
   git pull upstream dev
   git checkout -b feat/your-feature-name
   # or fix/your-bug-fix
   # or chore/your-maintenance-task
   ```
4. Commit with descriptive messages and push to your fork:
   ```bash
   git push origin feat/your-feature-name
   ```
5. Open a Pull Request targeting `fixnet-rwanda/fixnet-backend` on the `dev` branch.
6. Ensure automated CI checks pass before requesting peer review.