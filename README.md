# TransitOps — Smart Transport Operations Platform

Vehicles, drivers, trips, maintenance, fuel & expenses and fleet analytics for a transport depot, with
role-based access, a security audit trail and a UI designed to be used all day.

**Stack:** FastAPI · SQLAlchemy 2 · Alembic · MySQL/MariaDB · JWT + bcrypt · vanilla JS (ES modules, no build step) · Chart.js and Lucide icons (vendored) · self-hosted fonts

The product follows the "TransitOps — smart transport operations platform" design spec: eight screens, four roles.

| Screen | What it does |
|---|---|
| **Login** | Email, password, **role (RBAC)** picker, remember me, forgot password. Account locks after 5 failed attempts. |
| **Dashboard** | KPIs (active / available / in maintenance vehicles, active / pending trips, drivers on duty, fleet utilization), filters by type · status · region, recent trips with live ETAs, vehicle-status donut. |
| **Fleet** (vehicle registry) | Unique registration numbers, capacity (`500 kg`, `5 Ton`), odometer, acquisition cost in Indian grouping (`6,20,000`), status. |
| **Drivers & Safety Profiles** | Licence expiry flags, masked contacts, trip-completion rate, safety score, one-click status (Available / Off Duty / Suspended). Expired or suspended drivers are blocked from trips. |
| **Trips** (dispatcher) | Create form with **live capacity validation**, lifecycle Draft → Dispatched → Completed → Cancelled, live board with route + ETA, completion flow *odometer → fuel log → expenses → vehicle & driver available*. |
| **Maintenance** | Service records; *Available → In Shop → Available* (or Retired). In Shop vehicles leave the dispatch pool. |
| **Fuel & Expenses** | Fuel logs, per-trip toll/other/linked-maintenance costs, **Total operational cost (auto) = Fuel + Maintenance**. |
| **Analytics** | Fuel efficiency, utilization, operational cost, **Vehicle ROI = (Revenue − (Maintenance + Fuel)) ÷ Acquisition cost**, monthly revenue vs cost, costliest vehicles, CSV export. |
| **Settings** | Depot name, currency, distance unit · RBAC matrix · team management (create, role, disable, **unlock**, reset password) · audit log. |

Extras beyond the wireframes: light/dark theme, global search (press `/`), toasts, skeleton loaders, empty states, responsive layout, keyboard-friendly dialogs.

---

## Quick start

### Option A — Docker (API + MySQL + nginx)

```bash
cp .env.example .env
# edit .env: DB_PASSWORD, DB_ROOT_PASSWORD (URL-safe characters) and SECRET_KEY, e.g.
#   python -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose up --build
```

Open <http://localhost:8080>. If `ADMIN_PASSWORD` is empty the generated password is printed once in `docker compose logs backend`.
*(The compose file and the nginx → API wiring were checked locally, but `docker compose` itself was not run where this was prepared.)*

### Option B — Local development

```bash
python -m venv .venv && source .venv/bin/activate          # Windows: .\.venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env          # fill in DATABASE_URL and SECRET_KEY
mysql -u root -p -e "CREATE DATABASE transitops CHARACTER SET utf8mb4"
python seed_db.py --mock      # migrate + roles + first Fleet Manager + the demo depot from the spec
```

```bash
cd backend && uvicorn app.main:app --reload       # terminal 1: API on :8000 (docs at /docs in development)
cd frontend && python -m http.server 3000        # terminal 2: UI  -> http://localhost:3000/pages/login.html
```

**There are no default passwords.** The first account is `ADMIN_EMAIL` (role **Fleet Manager**) with `ADMIN_PASSWORD`; with
`--mock` the seeder also creates `raven.k@transitops.in` (Dispatcher), `safety@transitops.in` (Safety Officer) and
`finance@transitops.in` (Financial Analyst) with `DEMO_PASSWORD`. If either password is empty a random one is generated and
printed **once**.

The frontend finds the API at `http://<same host>:8000/api/v1` (or same-origin `/api/v1` when served on the default web port).
Override with `<script>window.TRANSITOPS_API_URL = "https://api.example.com/api/v1"</script>` before the page module loads.

## Roles & permissions

One table (`backend/app/auth/roles.py`) drives the API checks, the sidebar, the hidden buttons and the Settings matrix
(generated here from that table). *Every role can open the Dashboard.*

| Role | Fleet | Drivers | Trips | Fuel / Exp. | Analytics |
|---|:-:|:-:|:-:|:-:|:-:|
| **Fleet Manager** | ✅ | ✅ | — | — | ✅ |
| **Dispatcher** | 👁 view | — | ✅ | — | — |
| **Safety Officer** | — | ✅ | 👁 view | — | — |
| **Financial Analyst** | 👁 view | — | — | ✅ | ✅ |

Edit a cell by changing the capability lists in `roles.py`; `backend/tests/test_rbac.py` pins this matrix to the product spec,
so a deliberate change needs its test updated too.

## Configuration (`.env`)

| Variable | Required | Notes |
|---|:-:|---|
| `DATABASE_URL` | ✅ | `mysql+pymysql://user:pass@localhost:3306/transitops` (URL-encode special characters) |
| `SECRET_KEY` | ✅ | ≥ 32 chars. The app **refuses to start** without it or with a known placeholder. |
| `ENVIRONMENT` | | `production` hides `/docs`, `/redoc`, `/openapi.json` |
| `CORS_ORIGINS` | | Comma-separated browser origins allowed to call the API |
| `ACCESS_TOKEN_EXPIRE_MINUTES`, `REMEMBER_ME_DAYS` | | 8 h session token; 7-day token when *Remember me* is ticked |
| `LOGIN_MAX_ATTEMPTS`, `LOGIN_LOCK_MINUTES` | | Lock after 5 failures for 15 min (stored in the database, survives restarts) |
| `DEFAULT_FUEL_PRICE_PER_LITER` | | Fallback when a trip is completed without a fuel price |
| `ADMIN_NAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `DEMO_PASSWORD` | | Used by `seed_db.py` |
| `TRUST_PROXY_HEADERS` | | `true` only behind a proxy you control (audit IPs from `X-Forwarded-For`) |

Depot name, currency and distance unit are **Settings in the app** (stored in the database), not environment variables.
Currency and unit change how values are *displayed*; stored amounts and kilometres are not converted.

## Database migrations

```bash
cd backend
alembic revision --autogenerate -m "describe change"   # review the generated file
alembic upgrade head
alembic check                                          # CI fails if models and migrations drift
```

`seed_db.py` runs `alembic upgrade head` for you and adopts databases created by older versions. On MySQL/MariaDB migration `0002`
installs triggers that make `audit_logs` append-only at the database level (best effort: needs the `TRIGGER` privilege and, with
binary logging on, `log_bin_trust_function_creators=1`; the compose file sets it).

### Upgrading from v5

Run `python seed_db.py`. Migration `0003` converts **Admin → Fleet Manager** (the Admin role no longer exists; Fleet Managers now own
Settings, the team and the audit log), renames maintenance states to *In Shop / Completed*, and adds regions, trip revenue, drafts
without a vehicle, account-lock fields and the settings table. Trips and vehicles keep their data. Trip numbers for new trips use
the `TR001` format. Rotate any password or `SECRET_KEY` that was ever committed.

## Testing

```bash
cd backend && python -m pytest -q                 # ~110 tests on SQLite, incl. the spec RBAC matrix and the ROI/efficiency formulas
python scripts/check_frontend.py                  # static checks on the frontend (needs Node)
# real-database race test (SELECT ... FOR UPDATE needs a real server):
TEST_MYSQL_URL=mysql+pymysql://user:pw@localhost/some_empty_db python -m pytest -q tests/test_mysql_concurrency.py
```

CI (`.github/workflows/ci.yml`) runs lint, the suite, migration up/down/up + `alembic check` on MySQL 8.4, idempotent seeding, the race
test and the frontend checks.

## Security model

* **Auth:** JWT (HS256); the **role is read from the database on every request**, so demoting or disabling a user applies immediately.
  Passwords: bcrypt, ≥ 10 characters with mixed case and a digit. The login role picker must match the account's role.
* **Lockout:** 5 failed sign-ins lock the account for 15 minutes (persisted). A Fleet Manager can unlock it, or reset the password, in
  *Settings → Team*. An in-memory per-client/email throttle sits in front of it (per process; use Redis for multiple workers).
* **Audit trail:** logins (success / failure / blocked), every create / update / delete / dispatch / complete / cancel / export and every
  permission denial is stored with user, IP and details. Rows are append-only (ORM guard + DB triggers). A failed audit write is logged
  but does not undo an already-committed change.
* **Browser:** token in `sessionStorage` (or `localStorage` with *Remember me*), sent as a Bearer header; no cookies, so CORS is an
  allow-list with credentials off. All dynamic HTML goes through an escaping `html` template tag; `scripts/check_frontend.py` rejects
  direct `innerHTML`. No CDN assets: fonts, icons and Chart.js are vendored.
* **Not included:** MFA, password-reset e-mail, token revocation lists, server-side pagination (the UI filters client-side).

## Project layout

```
backend/app/
  api/            HTTP layer only: parse, call a service, write the audit row
  services/       business rules; every unit of work runs inside services.base.transaction()
  repositories/   all SQLAlchemy queries; they flush(), never commit()
  auth/           JWT + bcrypt (auth.py) and the permission table (roles.py)
  middleware/     RoleChecker / require("capability") / require_any(...)
  models/ schemas/ domain.py    tables, request/response validation, allowed statuses
backend/migrations/  backend/tests/
frontend/pages/     9 thin HTML shells
frontend/js/        api · session · layout (shell, nav, search) · ui (html tag, modals, toasts) · fmt · charts · icons
frontend/js/pages/  one module per screen
frontend/css/app.css  design system (light/dark tokens, components)
seed_db.py          migrate + roles + first Fleet Manager (+ --mock demo depot)
```

## Contribution rules

**Backend**
* No SQL in routers; routers call services, services own the transaction (`with transaction(...)`), repositories only query (`flush()`).
* Authorise with `Depends(require("<capability>"))` (add capabilities to `PERMISSIONS` and `PAGES` in `roles.py`); never compare role names in handlers.
* Mutating endpoints call `AuditService.record(...)`. Never hard-delete: use `soft_delete()`.
* `On Trip` / `In Shop` belong to the trip and maintenance workflows, not to CRUD edits. Lock rows (`for_update=True`) when a check-then-write could race.
* Validate in the schemas (`Field(gt=0)`, `Literal` statuses), not ad hoc in handlers.

**Frontend**
* Vanilla JS. Build markup with ``html`...` `` (values are escaped automatically); use `raw()` / `ic()` only for trusted markup. Never assign `innerHTML` outside `ui.js`.
* Network calls go through `js/api.js`; storage through `js/storage.js`; numbers and dates through `js/fmt.js`.
* Tag role-restricted controls with `data-requires="<capability>"`; the shell hides them for roles that lack it.
* Every page calls `mount({ page, title, subtitle })` first. `python scripts/check_frontend.py` enforces the basics.
