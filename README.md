# TransitOps - Smart Transport Operations Platform (Version 2)

TransitOps is a Smart Transport Operations Platform designed to manage Vehicles, Drivers, Trips, Maintenance, and Analytics.

**Version 2 (Transport Management & Dispatch Engine)** builds upon the foundational Version 1 (Auth & Fleet DB). V2 introduces robust, transaction-safe trip lifecycle management, real-world business rule validations, a Kanban-style Dispatch Board, and comprehensive fleet analytics.

## 🌟 What's New in Version 2

- **Trip Management System**: Full CRUD for trips, tracking planned routes, cargo, and estimated durations.
- **Dynamic Dispatch Engine**: Advanced business logic enforcing rules (e.g., driver license expiry, vehicle capacity, availability) with atomic database transactions guaranteeing data integrity during dispatch, complete, and cancel operations.
- **Kanban Dispatch Board**: A dynamic 4-column drag-and-drop-style UI for visualizing operational workflow (Draft → Dispatched → Completed / Cancelled).
- **Fleet Analytics Dashboard**: Real-time KPI metrics calculating fleet utilization, active trips, and vehicle status.
- **Audit Logging**: Immutable historical tracking of all status transitions via `trip_history` and `activity_logs`.

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
*Note: The default connection string expects the credentials `root:2006`. If your credentials differ, update the `DATABASE_URL` in `backend/app/config.py`.*

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
Run the seed script to automatically create the tables, roles, the initial Admin user, and populate test vehicles and drivers:

```bash
python backend/seed_db.py
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

Before you start working on future versions (e.g., Maintenance, Financials), please adhere to the following architectural rules established in Versions 1 & 2:

### 1. Backend Architecture (Strict Layering)
* **Do NOT write SQL queries in API Routers.**
* **Routers (`app/api/`)**: Handle HTTP requests, responses, and dependency injection (like RBAC).
* **Services (`app/services/`)**: Contain all business logic and validations. Ensure operations modifying multiple tables (like dispatching a trip and updating vehicle/driver statuses) are wrapped in `db.commit()` blocks and caught with `db.rollback()` on failure to guarantee atomic transactions.
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
