from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import vehicles, drivers, auth
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TransitOps API")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(vehicles.router, prefix="/api/v1/vehicles", tags=["vehicles"])
app.include_router(drivers.router, prefix="/api/v1/drivers", tags=["drivers"])
