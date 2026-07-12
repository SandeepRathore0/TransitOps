import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import Vehicle, Driver, Trip, FuelLog, Expense, MaintenanceLog, AuditLog, User

# Ensure tables exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    admin_user = db.query(User).filter(User.email == "admin@transitops.com").first()
    if not admin_user:
        print("Please run seed_db.py first to create the admin user.")
        exit()
    admin_id = admin_user.id

    print("Generating Indian Mock Data...")

    # --- VEHICLES ---
    vehicle_templates = [
        ("MH 12 AB 1234", "Tata Prima 2830.K", "Heavy Truck", 28000, 3500000),
        ("DL 01 C 1111", "Ashok Leyland Dost+", "Mini Truck", 1500, 750000),
        ("KA 03 HG 8899", "Mahindra Bolero Pik-Up", "Pickup", 1700, 900000),
        ("GJ 01 XX 9999", "Eicher Pro 2049", "Light Truck", 4900, 1200000),
        ("TN 07 BQ 5555", "Tata Ace Gold", "Mini Truck", 750, 500000),
    ]
    
    vehicles = []
    for reg, model, v_type, cap, cost in vehicle_templates:
        if not db.query(Vehicle).filter(Vehicle.registration_number == reg).first():
            v = Vehicle(
                registration_number=reg, model=model, vehicle_type=v_type,
                capacity=cap, odometer=random.randint(5000, 50000),
                purchase_cost=cost, status=random.choice(["Available", "On Trip", "In Shop"])
            )
            db.add(v)
            vehicles.append(v)
    db.commit()
    vehicles = db.query(Vehicle).all()

    # --- DRIVERS ---
    driver_names = ["Rajesh Kumar", "Amit Singh", "Suresh Patel", "Vikram Reddy", "Manoj Sharma", "Arun Kumar", "Dinesh Verma"]
    drivers = []
    for i, name in enumerate(driver_names):
        lic = f"DL14{2010+i}{random.randint(1000000, 9999999)}"
        if not db.query(Driver).filter(Driver.license_number == lic).first():
            d = Driver(
                name=name, license_number=lic, license_category=random.choice(["HMV", "LMV", "Transport"]),
                license_expiry=datetime.now().date() + timedelta(days=random.randint(100, 1000)),
                phone=f"+91 9{random.randint(100000000, 999999999)}",
                safety_score=random.randint(75, 100),
                status=random.choice(["Available", "On Trip", "Off Duty"])
            )
            db.add(d)
            drivers.append(d)
    db.commit()
    drivers = db.query(Driver).all()

    # --- TRIPS ---
    routes = [
        ("Mumbai, MH", "Pune, MH", 150),
        ("Delhi, DL", "Jaipur, RJ", 280),
        ("Bangalore, KA", "Chennai, TN", 350),
        ("Ahmedabad, GJ", "Surat, GJ", 260),
        ("Hyderabad, TS", "Vijayawada, AP", 275)
    ]
    
    trips = []
    for i in range(15): # Create 15 trips
        v = random.choice(vehicles)
        d = random.choice(drivers)
        route = random.choice(routes)
        
        trip_num = f"TRP-{datetime.now().strftime('%Y%m')}-{random.randint(1000, 9999)}"
        if not db.query(Trip).filter(Trip.trip_number == trip_num).first():
            t = Trip(
                trip_number=trip_num, vehicle_id=v.id, driver_id=d.id,
                source=route[0], destination=route[1],
                cargo_weight=random.uniform(500, v.capacity),
                planned_distance=route[2],
                actual_distance=route[2] * random.uniform(1.0, 1.1),
                status=random.choice(["Completed", "In Transit", "Draft", "Cancelled"]),
                created_by=admin_id
            )
            
            if t.status == "Completed":
                t.fuel_consumed = t.actual_distance / random.uniform(4.0, 12.0)
                
            db.add(t)
            trips.append(t)
    db.commit()
    trips = db.query(Trip).all()

    # --- FUEL LOGS ---
    stations = ["Indian Oil", "Bharat Petroleum", "Hindustan Petroleum", "Jio-bp", "Nayara Energy"]
    for t in trips:
        if t.status == "Completed" and t.fuel_consumed:
            liters = t.fuel_consumed
            price = random.uniform(89.5, 105.0) # Approx Indian diesel prices in rupees
            f = FuelLog(
                trip_id=t.id, vehicle_id=t.vehicle_id, driver_id=t.driver_id,
                fuel_station=random.choice(stations), liters=liters,
                cost_per_liter=price, total_cost=liters * price,
                odometer=t.vehicle.odometer, fuel_date=datetime.now().date() - timedelta(days=random.randint(1, 30))
            )
            db.add(f)
    db.commit()

    # --- EXPENSES ---
    expense_types = ["Toll Tax", "Parking", "Food Allowance", "Minor Repair", "Fines"]
    for t in trips:
        if t.status == "Completed":
            # Add 1-3 expenses per trip
            for _ in range(random.randint(1, 3)):
                e = Expense(
                    trip_id=t.id, vehicle_id=t.vehicle_id,
                    expense_type=random.choice(expense_types),
                    amount=random.uniform(150, 1500), # Rupees
                    description="En-route operational expense",
                    expense_date=datetime.now().date() - timedelta(days=random.randint(1, 30)),
                    created_by=admin_id
                )
                db.add(e)
    db.commit()

    # --- MAINTENANCE LOGS ---
    workshops = ["Tata Authorized Service", "Ashok Leyland Care", "Local Garage - Sharma Motors", "Bosch Car Service"]
    for v in vehicles:
        if random.random() > 0.5: # 50% chance vehicle has maintenance history
            m = MaintenanceLog(
                vehicle_id=v.id,
                maintenance_type=random.choice(["Preventive Maintenance", "Oil Change", "Tyre Replacement", "Brake Overhaul"]),
                description="Routine service",
                workshop_name=random.choice(workshops),
                estimated_cost=random.uniform(2000, 15000),
                actual_cost=random.uniform(2000, 15000),
                start_date=datetime.now().date() - timedelta(days=random.randint(5, 60)),
                status="Completed",
                created_by=admin_id
            )
            db.add(m)
    db.commit()

    # --- AUDIT LOGS ---
    for i in range(20):
        db.add(AuditLog(
            user_id=admin_id,
            action=random.choice(["LOGIN", "CREATE_TRIP", "UPDATE_VEHICLE", "ADD_FUEL_LOG"]),
            entity=random.choice(["Auth", "Trip", "Vehicle", "FuelLog"]),
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
            ip_address=f"192.168.1.{random.randint(10, 255)}"
        ))
    db.commit()

    print("✅ Indian Mock Data successfully seeded!")

except Exception as e:
    print(f"Error seeding mock data: {e}")
finally:
    db.close()
