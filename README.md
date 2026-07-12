# TransitOps - Smart Transport Operations Platform (Version 3)

TransitOps is a Smart Transport Operations Platform designed to manage Vehicles, Drivers, Trips, Maintenance, Fuel Logs, Expenses, and operational analytics.

**Version 3 (Smart Operations)** builds upon Version 2 (Dispatch Engine) and Version 1 (Auth & Fleet Foundation). Version 3 introduces automated fleet operations after dispatch, transaction-safe maintenance lifecycles, fuel log validations, operational expense tracking, and an operational summary dashboard.

## 🌟 What's New in Version 3

- **Automated Trip Completion Lifecycle**: Atomically logs fuel consumption, updates vehicle final odometer readings, and restores both vehicle and driver status to "Available" upon trip completion under a single database transaction.
- **Vehicle Maintenance Engine**: Full CRUD for scheduling, starting, and completing maintenance. Automates vehicle availability transitions (`Available` ↔ `In Shop`), prevents duplicate active bookings, and locks modifications to authorized managers.
- **Fuel Tracking & Validations**: Tracks fuel logging with validation checks preventing odometer values lower than the vehicle's last recorded odometer state.
- **Expense Logging & Audit**: Categories tracking for tolls, parking, repairs, and fines tied to vehicles, with role-based access control.
- **Operational Summary Dashboard**: Real-time KPI cards calculating total operational spending, maintenance logs, fuel cost totals, and fleet-wide average fuel efficiency (L/100km).
- **Audit Logging**: Immutable historical tracking of all status transitions via `trip_history`, `maintenance_logs`, and `activity_logs`.

---

## 🛠️ Technology Stack
* **Backend**: Python, FastAPI, SQLAlchemy
* **Database**: MySQL (PyMySQL)
* **Authentication**: JWT (JSON Web Tokens), Bcrypt
* **Frontend**: Vanilla JavaScript (ES6 Modules), HTML5, CSS3 (Strict Dark Theme)

---

## 🚀 Local Development Setup

### 1. Database Setup
Ensure you have MySQL installed and running locally. Log into MySQL and create the database:

```sql
CREATE DATABASE transitops;
```
*Note: The default connection string expects the credentials `root:Gunjan2005@`. If your credentials differ, update the `DATABASE_URL` in `backend/app/config.py`.*

### 2. Environment Setup
Clone the repository and set up your Python virtual environment:

```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Initialize the Database (Seeding)
Run the seed script to automatically create the tables, roles, initial admin user, and populate test vehicles and drivers:

```bash
python seed_db.py
```

### 4. Run the Application
You need to run the backend API server and a frontend static server.

**Terminal 1 (Backend):**
```bash
cd backend
uvicorn app.main:app --reload
```
API Documentation available at: http://localhost:8000/docs

**Terminal 2 (Frontend):**
```bash
cd frontend
python -m http.server 3000
```
Access the application at: http://localhost:3000/pages/login.html

**Default Login:**
* **Email:** admin@transitops.com
* **Password:** password123

---

## 🤝 Contribution Guidelines for Teammates

Before you start working on future versions (e.g., Financials, Customer Management), please adhere to the following architectural rules established:

### 1. Backend Architecture (Strict Layering)
* **Do NOT write SQL queries in API Routers.**
* **Routers (`app/api/`)**: Handle HTTP requests, responses, and dependency injection (like RBAC).
* **Services (`app/services/`)**: Contain all business logic and validations. Ensure operations modifying multiple tables (like completing a trip and updating vehicle/driver/fuel logs) are wrapped in `db.commit()` blocks and caught with `db.rollback()` on failure to guarantee atomic transactions.
* **Repositories (`app/repositories/`)**: Contain all SQLAlchemy database interactions. Use `db.flush()` instead of `db.commit()` in base repository methods when part of a multi-table transaction.

### 2. Security & RBAC
* Never hardcode roles inside functions. Use the `RoleChecker` dependency injection in your routers.
* Never delete records permanently. Always use the `soft_delete()` method in the repositories to set the `deleted_at` timestamp.

### 3. Frontend Standards
* **No Frameworks**: We are using Vanilla JS (ES6) with pure HTML/CSS. Do not install React, Vue, or Tailwind.
* **Design System**: You must strictly follow the variables in `frontend/css/index.css`. Backgrounds must use `--bg-primary` or `--bg-card`.
* **Micro-Animations**: Enhance user experience with micro-animations on interactive elements (e.g., hover states on Kanban cards).
* **Grid Layouts**: We use a strict 4px grid system for margins and padding (e.g., 4px, 8px, 12px, 16px, 24px, 32px).
* **API Calls**: Always use the wrapper inside `frontend/js/api.js` to make network requests. It automatically attaches the JWT Authentication token, handles unauthorized redirects, and properly formats `204 No Content` responses.
