from sqlalchemy.orm import Session
from app.models.models import Driver
from .base_repo import BaseRepository
from datetime import datetime

class DriverRepository(BaseRepository):
    def get_by_id(self, id: int):
        return self.db.query(Driver).filter(Driver.id == id, Driver.deleted_at.is_(None)).first()
    def get_by_license(self, license_number: str):
        return self.db.query(Driver).filter(Driver.license_number == license_number, Driver.deleted_at.is_(None)).first()
    def get_all(self):
        return self.db.query(Driver).filter(Driver.deleted_at.is_(None)).all()
    def create(self, driver: Driver):
        self.db.add(driver)
        self.db.commit()
        self.db.refresh(driver)
        return driver
    def update(self, driver: Driver):
        self.db.commit()
        self.db.refresh(driver)
        return driver
    def soft_delete(self, driver: Driver):
        driver.deleted_at = datetime.utcnow()
        self.db.commit()
