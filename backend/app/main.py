from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api import vehicles, drivers, auth, trips, maintenance, fuel, expenses, analytics, audit, users
from app.database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TransitOps API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(drivers.router, prefix="/api/v1/drivers", tags=["drivers"])
app.include_router(trips.router, prefix="/api/v1/trips", tags=["trips"])
app.include_router(maintenance.router, prefix="/api/v1/maintenance", tags=["maintenance"])
app.include_router(fuel.router, prefix="/api/v1/fuel", tags=["fuel"])
app.include_router(expenses.router, prefix="/api/v1/expenses", tags=["expenses"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
@app.get("/api/v1/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    from app.services.trip_service import TripService
    return TripService(db).get_dashboard_stats()

@app.get("/api/v1/dashboard/operations")
def dashboard_operations(db: Session = Depends(get_db)):
    from app.services.trip_service import TripService
    return TripService(db).get_dashboard_operations_stats()

