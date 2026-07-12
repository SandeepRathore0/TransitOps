from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.repositories.expense_repo import ExpenseRepository
from app.repositories.vehicle_repo import VehicleRepository
from app.repositories.trip_repo import TripRepository
from app.models.models import Expense, ActivityLog
from app.schemas.schemas import ExpenseCreate

class ExpenseService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ExpenseRepository(db)
        self.vehicle_repo = VehicleRepository(db)
        self.trip_repo = TripRepository(db)

    def get_expense(self, id: int) -> Expense:
        expense = self.repo.get_by_id(id)
        if not expense:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        return expense

    def get_all_expenses(self, vehicle_id: int = None, trip_id: int = None, expense_type: str = None):
        return self.repo.get_all(vehicle_id, trip_id, expense_type)

    def create_expense(self, data: ExpenseCreate, user_id: int) -> Expense:
        # Validations
        if data.amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expense amount must be positive")
        if data.expense_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expense date cannot be in the future")
        if not data.description or not data.description.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Description is required")

        allowed_types = ["Toll", "Repair", "Parking", "Fine", "Insurance", "Miscellaneous"]
        if data.expense_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid expense type. Allowed types are: {', '.join(allowed_types)}"
            )

        if data.vehicle_id:
            vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)
            if not vehicle:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
        if data.trip_id:
            trip = self.trip_repo.get_by_id(data.trip_id)
            if not trip:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")

        expense = Expense(
            trip_id=data.trip_id,
            vehicle_id=data.vehicle_id,
            expense_type=data.expense_type,
            amount=data.amount,
            description=data.description,
            expense_date=data.expense_date,
            receipt_reference=data.receipt_reference,
            created_by=user_id
        )

        try:
            self.repo.create(expense)

            # Activity Log
            act_log = ActivityLog(
                user_id=user_id,
                action="Expense Logged",
                entity_type="Vehicle" if data.vehicle_id else "Trip",
                entity_id=data.vehicle_id if data.vehicle_id else data.trip_id,
                details=f"Logged {data.expense_type} expense of amount {data.amount} ({data.description})"
            )
            self.db.add(act_log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create expense: {str(e)}")

        self.db.refresh(expense)
        return expense

    def update_expense(self, id: int, data: ExpenseCreate, user_id: int) -> Expense:
        expense = self.get_expense(id)

        # Validations
        if data.amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expense amount must be positive")
        if data.expense_date > date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Expense date cannot be in the future")
        if not data.description or not data.description.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Description is required")

        allowed_types = ["Toll", "Repair", "Parking", "Fine", "Insurance", "Miscellaneous"]
        if data.expense_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid expense type. Allowed types are: {', '.join(allowed_types)}"
            )

        expense.trip_id = data.trip_id
        expense.vehicle_id = data.vehicle_id
        expense.expense_type = data.expense_type
        expense.amount = data.amount
        expense.description = data.description
        expense.expense_date = data.expense_date
        expense.receipt_reference = data.receipt_reference

        try:
            self.repo.update(expense)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update expense: {str(e)}")

        self.db.refresh(expense)
        return expense

    def delete_expense(self, id: int):
        expense = self.get_expense(id)
        try:
            self.repo.delete(expense)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete expense: {str(e)}")
