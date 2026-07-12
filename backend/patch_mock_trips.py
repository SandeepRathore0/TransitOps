from datetime import datetime, timedelta
import random
from app.database import SessionLocal
from app.models.models import Trip, TripHistory

db = SessionLocal()

try:
    trips = db.query(Trip).all()
    for t in trips:
        if not t.dispatch_time:
            # Add basic metrics
            t.dispatch_time = t.created_at + timedelta(hours=1)
            t.estimated_duration = f"{random.randint(4, 12)} Hours"
            
            # Create Dispatch History
            h1 = TripHistory(
                trip_id=t.id, previous_status="Draft", new_status="In Transit",
                changed_by=1, changed_at=t.dispatch_time, remarks="Vehicle left terminal"
            )
            db.add(h1)

            if t.status == "Completed":
                t.completion_time = t.dispatch_time + timedelta(hours=random.randint(4, 12))
                t.final_odometer = t.vehicle.odometer + int(t.actual_distance)
                
                # Create Completion History
                h2 = TripHistory(
                    trip_id=t.id, previous_status="In Transit", new_status="Completed",
                    changed_by=1, changed_at=t.completion_time, remarks="Trip finished successfully"
                )
                db.add(h2)

    db.commit()
    print("Mock trips patched with rich history and metrics.")
except Exception as e:
    print(f"Error patching trips: {e}")
finally:
    db.close()
