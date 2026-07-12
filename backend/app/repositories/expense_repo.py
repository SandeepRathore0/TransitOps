from sqlalchemy.orm import Session
from app.models.models import Expense
from .base_repo import BaseRepository

class ExpenseRepository(BaseRepository):
    def get_by_id(self, id: int) -> Expense:
        return self.db.query(Expense).filter(Expense.id == id).first()

    def get_all(self, vehicle_id: int = None, trip_id: int = None, expense_type: str = None):
        query = self.db.query(Expense)
        if vehicle_id:
            query = query.filter(Expense.vehicle_id == vehicle_id)
        if trip_id:
            query = query.filter(Expense.trip_id == trip_id)
        if expense_type:
            query = query.filter(Expense.expense_type == expense_type)
        return query.order_by(Expense.expense_date.desc()).all()

    def create(self, expense: Expense) -> Expense:
        self.db.add(expense)
        self.db.flush()
        return expense

    def update(self, expense: Expense) -> Expense:
        self.db.flush()
        return expense

    def delete(self, expense: Expense):
        self.db.delete(expense)
        self.db.flush()
