import csv
from io import StringIO
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.models.models import Vehicle, Driver, Trip

class ReportService:
    @staticmethod
    def generate_csv(db: Session, entity: str):
        output = StringIO()
        writer = csv.writer(output)
        
        if entity == "vehicles":
            writer.writerow(["ID", "Reg Number", "Model", "Type", "Status"])
            for v in db.query(Vehicle).filter(Vehicle.deleted_at == None).all():
                writer.writerow([v.id, v.registration_number, v.model, v.vehicle_type, v.status])
        
        elif entity == "drivers":
            writer.writerow(["ID", "Name", "License", "Category", "Status"])
            for d in db.query(Driver).filter(Driver.deleted_at == None).all():
                writer.writerow([d.id, d.name, d.license_number, d.license_category, d.status])
                
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]), 
            media_type="text/csv", 
            headers={"Content-Disposition": f"attachment; filename={entity}_report.csv"}
        )
