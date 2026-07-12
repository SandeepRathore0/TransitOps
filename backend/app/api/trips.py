from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import (
    TripResponse, TripCreate, TripUpdate, TripDispatch,
    TripComplete, TripCancel, TripHistoryResponse,
)
from app.services.trip_service import TripService
from app.middleware.rbac import RoleChecker

router = APIRouter()

allow_dispatch = RoleChecker(["Fleet Manager", "Dispatcher"])
allow_read = RoleChecker(["Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"])
allow_manager = RoleChecker(["Fleet Manager"])


@router.get("/", response_model=List[TripResponse])
def get_trips(
    status: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    user=Depends(allow_read),
):
    return TripService(db).get_all_trips(status, search)


@router.get("/history", response_model=List[TripHistoryResponse])
def get_all_trip_history(db: Session = Depends(get_db), user=Depends(allow_read)):
    return TripService(db).get_trip_history()


@router.get("/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), user=Depends(allow_read)):
    return TripService(db).get_dashboard_stats()


@router.get("/{id}", response_model=TripResponse)
def get_trip(id: int, db: Session = Depends(get_db), user=Depends(allow_read)):
    return TripService(db).get_trip(id)


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    data: TripCreate,
    db: Session = Depends(get_db),
    user=Depends(allow_dispatch),
):
    return TripService(db).create_trip(data, user.id)


@router.put("/{id}", response_model=TripResponse)
def update_trip(
    id: int,
    data: TripUpdate,
    db: Session = Depends(get_db),
    user=Depends(allow_dispatch),
):
    return TripService(db).update_trip(id, data, user.id)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(id: int, db: Session = Depends(get_db), user=Depends(allow_manager)):
    TripService(db).delete_trip(id)


@router.put("/{id}/dispatch", response_model=TripResponse)
def dispatch_trip(
    id: int,
    data: TripDispatch = None,
    db: Session = Depends(get_db),
    user=Depends(allow_dispatch),
):
    if data is None:
        data = TripDispatch()
    return TripService(db).dispatch_trip(id, data, user.id)


@router.put("/{id}/complete", response_model=TripResponse)
def complete_trip(
    id: int,
    data: TripComplete,
    db: Session = Depends(get_db),
    user=Depends(allow_dispatch),
):
    return TripService(db).complete_trip(id, data, user.id)


@router.put("/{id}/cancel", response_model=TripResponse)
def cancel_trip(
    id: int,
    data: TripCancel = None,
    db: Session = Depends(get_db),
    user=Depends(allow_dispatch),
):
    if data is None:
        data = TripCancel()
    return TripService(db).cancel_trip(id, data, user.id)
