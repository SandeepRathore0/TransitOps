# Changelog

## 6.0 - rebuilt to the product spec ("TransitOps - smart transport operations platform")

### Product (matches the design diagram)
- **Four roles, no Admin**: Fleet Manager, Dispatcher, Safety Officer, Financial Analyst, with exactly the diagram's RBAC matrix
  (pinned by a test). Fleet Managers own Settings, the team and the audit log. Existing Admins become Fleet Managers (migration `0003`).
- **Login**: role (RBAC) picker that must match the account, remember me, forgot password, "attempts left" messages and
  **account lockout after 5 failed attempts** (persisted; a Fleet Manager can unlock or reset the password).
- **Dashboard**: the seven KPIs, filters by vehicle type / status / region, recent trips with live ETAs ("45 min", "1h 10m", "Awaiting vehicle"), status donut.
- **Fleet**: region, capacity as `500 kg` / `5 Ton`, Indian digit grouping, uniqueness and dispatch-pool rules shown.
- **Drivers & Safety Profiles**: licence expiry flags, masked contacts, trip-completion rate, status toggle, compliance counters.
- **Trips**: drafts can be saved without a vehicle or driver, **live capacity validation** ("Capacity exceeded by 200 kg - dispatch blocked"),
  dispatch pool of Available vehicles and licence-valid Available drivers only, live board, per-trip timeline, trip revenue.
- **Maintenance**: *Available -> In Shop -> Available* (or Retired), one active record per vehicle.
- **Fuel & Expenses**: fuel by total cost, per-trip toll / other / linked-maintenance table, **Total operational cost = Fuel + Maintenance**.
- **Analytics**: fuel efficiency (km/l), utilization, operational cost, **Vehicle ROI = (Revenue - (Maintenance + Fuel)) / Acquisition cost**,
  monthly revenue vs cost, costliest vehicles, CSV export of vehicles / drivers / trips / fuel / expenses. Formulas are tested with hand-computed numbers.
- **Settings**: depot name, currency, distance unit (stored in the database), RBAC matrix, team management, audit log.
- Demo data (`seed_db.py --mock`) is the spec's own depot: Gandhinagar, VAN-05 / TRUCK-11 / MINI-03, Alex / John / Priya / Suresh, Ahmedabad / Sanand / Kalol routes.

### UI
- Complete redesign: "control tower" design system, light and dark themes, route-grid sidebar, animated login hero, KPI cards with gauges,
  route cards with moving trucks, slide-over drawers, toasts, skeleton loaders, empty states, global search (`/`), responsive down to phones.
- Self-hosted fonts (Plus Jakarta Sans, JetBrains Mono), inlined Lucide icons, vendored Chart.js: nothing loads from a CDN.
- Safe-by-default templating: an escaping `html` tag replaces string concatenation; `scripts/check_frontend.py` rejects direct `innerHTML`,
  unused/missing imports, inline scripts and CDN assets.

### Fixes found while testing the new build
- Unlocking an account (or resetting its password) now also clears the in-memory login throttle; before, the user stayed blocked for up to 15 minutes.
- Header buttons of Fuel & Expenses were wired to the wrong container and did nothing.
- Validation messages are readable ("cargo_weight: Input should be greater than 0").

### Upgrade notes
See "Upgrading from v5" in the README. Trip numbers for new trips are `TR001`-style; maintenance state `Scheduled` / `In Progress` became `In Shop`.

---

## 5.0 — security & correctness release

### Security
- **No more hardcoded secrets.** `SECRET_KEY` / `DATABASE_URL` come from the environment; the app refuses to start without a
  real secret. Credentials removed from the README and config; `.env.example` added.
- **No default admin password.** `seed_db.py` takes `ADMIN_PASSWORD` from the environment or generates one (printed once).
- Dashboard endpoints (`/dashboard/stats`, `/dashboard/operations`) now require authentication and the right role.
- Login throttling (429 + `Retry-After`), equal-time failed logins, inactive/deleted users can no longer log in or keep using tokens.
- CORS restricted to an allow-list (no more `*` + credentials); security headers; `/docs` off in production.
- Stored XSS fixed: all dynamic HTML is escaped (`esc()`), toasts use `textContent`, query-string ids sanitised.
- Token moved from `localStorage` to `sessionStorage`, default lifetime 8 h (was 7 days). Chart.js vendored (no CDN).
- CSV export neutralises spreadsheet formula injection; unknown export names return 404.
- Internal error text is no longer returned to clients (generic 500, details logged).
- Passwords: bcrypt used directly (unmaintained `passlib` removed), min 10 chars with mixed case + digit.

### Correctness
- **Audit log actually works**: logins, failed logins, every mutation, exports and permission denials are recorded with IP;
  rows are append-only (ORM guard + MySQL triggers). Previously nothing was ever written.
- Race-safe dispatch/complete/cancel using row locks (`SELECT … FOR UPDATE`), verified on MariaDB: without the locks
  concurrent dispatches double-book a vehicle. Trip numbers derive from the primary key (no `max(id)+1` collisions).
- Vehicle/driver status can no longer be edited into or out of "On Trip"; odometer cannot be rolled back; deleting
  something with open trips/maintenance is refused; maintenance can't start on a vehicle that is on a trip.
- Fuel logs and expenses are soft-deleted like everything else; analytics exclude soft-deleted rows.
- Fuel logs record the real user (was hardcoded user id 1); trip completion accepts a fuel price (falls back to the
  vehicle's last price, then `DEFAULT_FUEL_PRICE_PER_LITER`) instead of a hardcoded ₹100.
- Strict request validation: enum statuses, positive quantities, date ordering, string lengths.
- Duplicate unique values (e.g. phone) return 409 instead of 500.

### Roles & UI
- Seeded admin now has the **Admin** role; Admin can use every module (was excluded from trips/fuel/expenses/maintenance).
- Permissions live in one table (`auth/roles.py`); the UI builds navigation and hides controls from `GET /auth/me`.
- Dashboard shows only real data (the utilisation chart used hardcoded numbers) and works for roles without analytics access.
- CSV export on the dashboard works (it read the wrong token key). Validation errors are readable.
- Users: update / deactivate / delete endpoints, last-admin and self-lockout protection, change-password endpoint.

### Engineering
- Alembic migrations (baseline `0001` = the old schema, `0002` = this release); `seed_db.py` adopts legacy databases.
- Repositories flush, services own transactions (previously vehicle/driver repos committed).
- ~80 pytest tests, MySQL race test, GitHub Actions CI, Dockerfile + docker-compose, pinned dependencies.
- `seed_db.py --mock` builds demo data through the real workflow (consistent statuses, no fake audit rows) in one script.
- Removed: stale generator scripts (`generate_*.py`, `build_all.py`), `e2e_test.py` (replaced by pytest), empty `docs/` and a
  stale `database/schema.sql`, the empty `TransitOps/TransitOps` folder, the committed `venv/`.
