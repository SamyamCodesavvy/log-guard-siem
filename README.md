# 🛡️ LogGuard-SIEM

**A mini Security Information & Event Management (SIEM) platform, built from scratch.**

LogGuard-SIEM ingests security logs (SSH auth, sudo, nginx access logs), parses them into structured fields with a custom regex engine, runs them through a rule-based detection pipeline, and surfaces alerts and log activity through a REST API and a live web dashboard — the same core loop that commercial tools like Splunk and Wazuh are built around, implemented end-to-end by one person.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639?style=flat&logo=nginx&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=flat&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=flat&logo=grafana&logoColor=white)
![CI](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?style=flat&logo=githubactions&logoColor=white)
![Tests](https://img.shields.io/badge/pytest-passing-brightgreen?style=flat&logo=pytest&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-lightgrey)


---

## Table of Contents

- [Why This Project](#why-this-project)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Screenshots](#screenshots)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Detection Rules](#detection-rules)
- [Testing & CI/CD](#testing--cicd)
- [Monitoring](#monitoring)
- [Project Structure](#project-structure)
- [Skills Demonstrated](#skills-demonstrated)
- [Roadmap](#roadmap)
- [License](#license)

---

## Why This Project

Most portfolio projects are CRUD apps. LogGuard-SIEM is a small but complete **security engineering** system: it takes unstructured log text, extracts meaning from it, correlates events across time windows, and turns raw noise into actionable alerts — while being packaged the way a real backend service would be (containerized, monitored, tested, and continuously integrated).

It demonstrates the full loop a security engineer / backend engineer is expected to own:

**ingest → parse → detect → alert → visualize → ship (Docker) → monitor (Prometheus/Grafana) → verify (pytest) → automate (CI/CD)**

---

## Architecture

```
                    ┌─────────────┐
   Log sources ───▶ │   Nginx     │  reverse proxy, port 80
 (auth.log, nginx)  └──────┬──────┘
                           │
                    ┌──────▼──────┐        ┌──────────────┐
                    │  FastAPI    │◀──────▶│  PostgreSQL  │
                    │  app        │        │  (SQLAlchemy │
                    │             │        │   + Alembic) │
                    │  ┌────────┐ │        └──────────────┘
                    │  │ Regex  │ │
                    │  │ Parser │ │
                    │  └───┬────┘ │
                    │  ┌───▼────┐ │
                    │  │Detection│ │  5 correlation rules
                    │  │ Engine │ │  (brute force, priv-esc, etc.)
                    │  └───┬────┘ │
                    │  ┌───▼────┐ │
                    │  │ Alerts │ │
                    │  └────────┘ │
                    └──────┬──────┘
                           │ /metrics
                    ┌──────▼──────┐      ┌─────────┐
                    │ Prometheus  │─────▶│ Grafana │
                    └─────────────┘      └─────────┘
```


---

## Features

- **JWT authentication** with bcrypt password hashing and role-based access control (admin / analyst / viewer)
- **Host management** — register and track monitored machines (CRUD)
- **Log ingestion API** — single and batch ingestion, with a regex-based parser extracting hostname, program, user, source IP, and action from raw syslog/nginx lines
- **Rule-based detection engine** — every ingested log is evaluated against 5 correlation rules in real time (see [Detection Rules](#detection-rules))
- **Dashboard API** — aggregate stats, logs-per-hour, top attacker IPs, top failed-login users
- **Search API** — filter logs by keyword, IP, username, hostname, severity
- **Web frontend** (Jinja2 + Tailwind + Chart.js) — dark-themed dashboard, live logs table, alerts table with inline status resolution (Investigating / Resolved / False Positive)
- **Containerized deployment** — 5-service Docker Compose stack (app, PostgreSQL, Nginx, Prometheus, Grafana), single-command startup
- **Observability** — Prometheus scraping `/metrics`, Grafana dashboards for request rate/latency/error rate
- **Automated testing** — pytest suite covering auth flows, log parsing, and detection logic, run against an in-memory SQLite DB
- **CI/CD pipeline** — GitHub Actions runs tests, linting, and a Docker build on every push/PR

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Database | PostgreSQL 15 |
| ORM / migrations | SQLAlchemy 2.0 + Alembic |
| Auth | JWT (`python-jose`) + bcrypt (`passlib`) |
| Frontend | Jinja2, Tailwind CSS, Chart.js |
| Containerization | Docker + Docker Compose (5 services) |
| Reverse proxy | Nginx |
| Monitoring | Prometheus + Grafana |
| Testing | pytest, pytest-cov, SQLite (test DB) |
| CI/CD | GitHub Actions (test → lint → Docker build) |
| Environment | Kali Linux, Python 3.13 |

---

## Screenshots

| Dashboard | Logs |
|---|---|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Logs](docs/screenshots/logs.png) |

| Log Detail | Alerts |
|---|---|
| ![Log Detail](docs/screenshots/log_detail.png) | ![Alerts](docs/screenshots/alerts.png) |

| Alert Detail |
|---|
| ![Alert Detail](docs/screenshots/alert_detail.png) |


---

## Quick Start

```bash
# 1. Clone and enter the repo
git clone https://github.com/SamyamCodesavvy/log-guard-siem.git
cd log-guard-siem

# 2. Configure environment
cp .env.example .env   # set SECRET_KEY to a long random string

# 3. Build and start the full stack (FastAPI + PostgreSQL + Nginx + Prometheus + Grafana)
docker compose up --build -d

# 4. Check every service is healthy
docker compose ps
```

Then visit:

| Service | URL |
|---|---|
| Web UI | `http://localhost/ui/dashboard` |
| API docs (Swagger) | `http://localhost/docs` |
| Health check | `http://localhost/health` |
| Prometheus | `http://localhost:9090` |
| Grafana | `http://localhost:3000` (admin / admin on first login) |

### Local development (without Docker)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker run -d --name siem-postgres -e POSTGRES_USER=siem_user \
  -e POSTGRES_PASSWORD=siem_pass -e POSTGRES_DB=siem_db -p 5432:5432 postgres:15
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login, get JWT token | No |
| GET | `/auth/me` | Get current user | Yes |
| POST | `/hosts/` | Register a host | Yes |
| GET | `/hosts/` | List hosts | Yes |
| PUT | `/hosts/{id}` | Update host | Yes |
| DELETE | `/hosts/{id}` | Delete host | Yes |
| POST | `/logs/` | Ingest a single log | Yes |
| POST | `/logs/batch` | Ingest multiple logs | Yes |
| GET | `/logs/` | List logs (with filters) | Yes |
| GET | `/logs/{id}` | Get log detail | Yes |
| GET | `/alerts/` | List alerts | Yes |
| GET | `/alerts/{id}` | Get alert detail | Yes |
| PUT | `/alerts/{id}/resolve` | Update alert status | Yes |
| GET | `/dashboard/` | Dashboard statistics | Yes |
| GET | `/search/` | Search logs | Yes |
| GET | `/health` | Health check | No |
| GET | `/metrics` | Prometheus metrics | No |

---

## Detection Rules

Every log that hits `/logs` or `/logs/batch` is run through the detection engine immediately after parsing:

| Rule | Trigger | Severity |
|---|---|---|
| SSH Brute Force | 5+ failed logins from the same IP within 5 minutes | Critical |
| Privilege Escalation Attempt | Failed sudo authentication | High |
| Root Login Detected | Root session opened or root login succeeds | High |
| Credential Sharing Detected | 3+ distinct usernames logging in from the same IP within 1 hour | Medium |
| Possible Web Attack | 10+ HTTP 401/403 responses from the same IP within 10 minutes (nginx logs) | High |

---

## Testing & CI/CD

- **pytest suite** covers registration/login/token flows, protected-route enforcement, and log-parser correctness (failed login, successful login, sudo failure) against an isolated in-memory SQLite database — no PostgreSQL/Docker needed to run tests locally.

```bash
pytest tests/ -v
pytest tests/ --cov=app --cov-report=term-missing
```

- **GitHub Actions** (`.github/workflows/ci.yml`) runs on every push and pull request to `main`/`develop`:
  1. **test** — installs dependencies, runs the full pytest suite with coverage
  2. **lint** — flake8 static analysis
  3. **docker** — builds the production Docker image to catch build breakage before merge

A green checkmark on the Actions tab means the app installs cleanly, passes all tests, and builds — the same gate a real engineering team would enforce before merging.

---

## Monitoring

- `prometheus-fastapi-instrumentator` exposes request count, latency, and error-rate metrics at `/metrics`.
- Prometheus scrapes the FastAPI app every 15 seconds (`prometheus/prometheus.yml`).
- Grafana is pre-wired to Prometheus as a data source; import dashboard ID `12900` (or build a custom one) for request-rate/latency/error panels.

---

## Project Structure

```
log-guard-siem/
├── app/
│   ├── api/             # FastAPI routers (auth, hosts, logs, alerts, dashboard, search, ui)
│   ├── authentication/  # JWT + bcrypt logic
│   ├── detection/       # Rule-based detection engine
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic (host, dashboard)
│   ├── static/js/       # Frontend auth/fetch helpers
│   ├── templates/       # Jinja2 pages (login, dashboard, logs, alerts)
│   ├── utils/           # DB session, log parser
│   ├── config.py
│   └── main.py
├── tests/                # pytest suite (auth, detection/parser)
├── alembic/               # DB migrations
├── nginx/nginx.conf        # Reverse proxy config
├── prometheus/prometheus.yml
├── .github/workflows/ci.yml # GitHub Actions pipeline
├── docker-compose.yml       # 5-service stack
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Skills Demonstrated

| Skill Area | Evidence in this Project |
|---|---|
| Backend Development | FastAPI REST API with 15+ endpoints, Pydantic validation, background-triggered detection on ingest |
| Database Engineering | PostgreSQL schema design, SQLAlchemy 2.0 ORM, Alembic migrations |
| Security Engineering | JWT auth, bcrypt hashing, role-based access control, regex-based log parsing, 5-rule threat detection engine |
| Linux & Networking | SSH/syslog log format parsing, IP-based correlation, Nginx reverse proxy configuration |
| DevOps & Containerization | Multi-service Docker Compose (app, DB, proxy, monitoring), custom Dockerfile, container health checks |
| Monitoring & Observability | Prometheus metrics instrumentation, Grafana dashboarding |
| CI/CD | GitHub Actions pipeline — automated test, lint, and Docker build on every push |
| Testing | pytest unit + integration tests, FastAPI `TestClient`, isolated SQLite test database |

---

## Roadmap

- [x] Phase 0 — Environment setup (Kali Linux, Python 3.13, Docker, Git)
- [x] Phase 1 — Project scaffold & FastAPI foundation
- [x] Phase 2 — Database models & Alembic migrations
- [x] Phase 3 — JWT authentication
- [x] Phase 4 — Host management API
- [x] Phase 5 — Log ingestion & parser
- [x] Phase 6 — Detection engine & alerts
- [x] Phase 7 — Dashboard & search APIs
- [x] Phase 8 — Interactive Jinja2 frontend
- [x] Phase 9 — Dockerizing everything (5-service Compose stack)
- [x] Phase 10 — Nginx reverse proxy
- [x] Phase 11 — Prometheus & Grafana monitoring
- [x] Phase 12 — pytest test suite
- [x] Phase 13 — GitHub Actions CI/CD

---

## License

Built by **Samyam Giri** 💙 as a personal learning / portfolio project demonstrating full-stack security engineering: from raw log line to correlated alert to containerized, monitored, continuously-integrated service.

MIT License.