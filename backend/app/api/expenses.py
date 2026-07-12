from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.schemas import ExpenseResponse, ExpenseCreate
from app.services.expense_service import ExpenseService
from app.middleware.rbac import RoleChecker
from app.models.models import User

router = APIRouter()

allow_read = RoleChecker(["Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"])
allow_write = RoleChecker(["Fleet Manager", "Financial Analyst"])
allow_manager = RoleChecker(["Fleet Manager"])

@router.get("/", response_model=List[ExpenseResponse])
def get_all_expenses(
    vehicle_id: int = None,
    trip_id: int = None,
    expense_type: str = None,
    db: Session = Depends(get_db),
    user: User = Depends(allow_read)
):
    return ExpenseService(db).get_all_expenses(vehicle_id, trip_id, expense_type)

@router.get("/{id}", response_model=ExpenseResponse)
def get_expense(id: int, db: Session = Depends(get_db), user: User = Depends(allow_read)):
    return ExpenseService(db).get_expense(id)

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(allow_write)
):
    return ExpenseService(db).create_expense(data, user.id)

@router.put("/{id}", response_model=ExpenseResponse)
def update_expense(
    id: int,
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    return ExpenseService(db).update_expense(id, data, user.id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(allow_manager)
):
    ExpenseService(db).delete_expense(id)
