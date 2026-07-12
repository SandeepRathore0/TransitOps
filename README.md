# TransitOps - Smart Transport Operations Platform (Version 1)

TransitOps is a Smart Transport Operations Platform designed to manage Vehicles, Drivers, Trips, Maintenance, and Analytics. 

**Version 1** establishes the secure, scalable foundation of the application including Database Models, Authentication, Role-Based Access Control (RBAC), and the core Fleet/Driver modules.

## Technology Stack
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
*Note: The default connection string expects the credentials `root`:`2006`. If your credentials differ, update the `DATABASE_URL` in `backend/app/config.py`.*

### 2. Environment Setup
Clone the repository and set up your Python virtual environment:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Initialize the Database (Seeding)
Run the seed script to automatically create the tables, roles, and the initial Admin user:
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
*API Documentation available at: [http://localhost:8000/docs](http://localhost:8000/docs)*

**Terminal 2 (Frontend):**
```bash
cd frontend
python -m http.server 3000
```
*Access the application at: [http://localhost:3000/pages/login.html](http://localhost:3000/pages/login.html)*

**Default Login:**
* Email: `admin@transitops.com`
* Password: `password123`

---

## 🛠️ Contribution Guidelines for Teammates

Before you start working on Version 2 (Trips, Maintenance, etc.), please adhere to the following architectural rules established in Version 1:

### 1. Backend Architecture (Strict Layering)
* **Do NOT write SQL queries in API Routers.** 
* **Routers (`app/api/`)**: Handle HTTP requests, responses, and dependency injection (like RBAC).
* **Services (`app/services/`)**: Contain all business logic and validations.
* **Repositories (`app/repositories/`)**: Contain all SQLAlchemy database interactions.

### 2. Security & RBAC
* Never hardcode roles inside functions. Use the `RoleChecker` dependency injection in your routers.
* Never delete records permanently. Always use the `soft_delete()` method in the repositories to set the `deleted_at` timestamp.

### 3. Frontend Standards
* **No Frameworks:** We are using Vanilla JS (ES6) with pure HTML/CSS. Do not install React, Vue, or Tailwind.
* **Design System:** You must strictly follow the variables in `frontend/css/index.css`.
  * Backgrounds must use `--bg-primary` or `--bg-card`.
  * We use a strict **4px grid** system for margins and padding (e.g., 4px, 8px, 12px, 16px, 24px, 32px).
* **API Calls:** Always use the wrapper inside `frontend/js/api.js` to make network requests. It automatically attaches the JWT Authentication token and handles unauthorized redirects.
