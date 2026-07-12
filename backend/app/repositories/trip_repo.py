from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from app.models.models import Trip, TripHistory, ActivityLog
from .base_repo import BaseRepository
from datetime import datetime


class TripRepository(BaseRepository):
    def get_by_id(self, id: int):
        return (
            self.db.query(Trip)
            .options(joinedload(Trip.vehicle), joinedload(Trip.driver))
            .filter(Trip.id == id, Trip.deleted_at.is_(None))
            .first()
        )

    def get_by_trip_number(self, trip_number: str):
        return (
            self.db.query(Trip)
            .filter(Trip.trip_number == trip_number, Trip.deleted_at.is_(None))
            .first()
        )

    def get_all(self, status: str = None, search: str = None):
        query = (
            self.db.query(Trip)
            .options(joinedload(Trip.vehicle), joinedload(Trip.driver))
            .filter(Trip.deleted_at.is_(None))
        )
        if status:
            query = query.filter(Trip.status == status)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Trip.source.ilike(search_pattern),
                    Trip.destination.ilike(search_pattern),
                    Trip.trip_number.ilike(search_pattern),
                )
            )
        return query.order_by(Trip.created_at.desc()).all()

    def create(self, trip: Trip):
        self.db.add(trip)
        self.db.flush()
        return trip

    def update(self, trip: Trip):
        self.db.flush()
        return trip

    def soft_delete(self, trip: Trip):
        trip.deleted_at = datetime.utcnow()
        self.db.flush()

    def generate_trip_number(self):
        max_id = self.db.query(func.max(Trip.id)).scalar()
        next_number = (max_id or 0) + 1
        return f"TR{next_number:04d}"

    def create_history(self, history: TripHistory):
        self.db.add(history)
        self.db.flush()
        return history

    def create_activity_log(self, log: ActivityLog):
        self.db.add(log)
        self.db.flush()
        return log

    def get_trip_history(self, trip_id: int):
        return (
            self.db.query(TripHistory)
            .filter(TripHistory.trip_id == trip_id)
            .order_by(TripHistory.changed_at.desc())
            .all()
        )

    def get_all_history(self):
        return (
            self.db.query(TripHistory)
            .order_by(TripHistory.changed_at.desc())
            .limit(200)
            .all()
        )

    def get_trip_activity_logs(self, trip_id: int):
        return (
            self.db.query(ActivityLog)
            .filter(ActivityLog.entity_type == "Trip", ActivityLog.entity_id == trip_id)
            .order_by(ActivityLog.created_at.desc())
            .all()
        )
