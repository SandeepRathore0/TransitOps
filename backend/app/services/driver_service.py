from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.driver_repo import DriverRepository
from app.schemas.schemas import DriverCreate, DriverBase
from app.models.models import Driver

class DriverService:
    def __init__(self, db: Session):
        self.repo = DriverRepository(db)
    def get_all_drivers(self):
        return self.repo.get_all()
    def get_driver(self, id: int):
        driver = self.repo.get_by_id(id)
        if not driver: raise HTTPException(status_code=404, detail="Driver not found")
        return driver
    def create_driver(self, data: DriverCreate):
        if self.repo.get_by_license(data.license_number):
            raise HTTPException(status_code=409, detail="License number already exists")
        driver = Driver(**data.dict())
        return self.repo.create(driver)
    def update_driver(self, id: int, data: DriverBase):
        driver = self.get_driver(id)
        for key, value in data.dict().items(): setattr(driver, key, value)
        return self.repo.update(driver)
    def delete_driver(self, id: int):
        driver = self.get_driver(id)
        self.repo.soft_delete(driver)
