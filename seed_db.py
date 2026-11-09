#!/usr/bin/env python3
"""Prepare the database and create the first Fleet Manager (who owns Settings and users).

    python seed_db.py            # migrate + roles + first Fleet Manager
    python seed_db.py --mock     # ...plus the demo depot from the product spec (only if the DB is empty)

First account: ADMIN_EMAIL / ADMIN_PASSWORD (env or .env), role Fleet Manager. If ADMIN_PASSWORD is not
set, a random one is generated and printed ONCE. With --mock, one demo user per role is also created with
DEMO_PASSWORD (or a random password printed once).
"""
import argparse
import os
import random
import secrets
import sys
from datetime import date, timedelta
from pathlib import Path

BACKEND = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND))

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from dotenv import dotenv_values  # noqa: E402
from sqlalchemy import inspect  # noqa: E402

from app.auth.auth import hash_password  # noqa: E402
from app.auth.roles import DISPATCHER, FINANCIAL_ANALYST, FLEET_MANAGER, SAFETY_OFFICER  # noqa: E402
from app.config import ROOT_DIR  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402
from app.models.models import Driver, Expense, FuelLog, Role, Trip, TripHistory, User, Vehicle  # noqa: E402
from app.schemas.schemas import (  # noqa: E402
    DriverBase, DriverCreate, ExpenseCreate, FuelLogCreate, MaintenanceCreate, SettingsUpdate,
    TripCancel, TripComplete, TripCreate, TripDispatch, VehicleCreate, _check_password,
)
from app.services.driver_service import DriverService  # noqa: E402
from app.services.expense_service import ExpenseService  # noqa: E402
from app.services.fuel_service import FuelService  # noqa: E402
from app.services.maintenance_service import MaintenanceService  # noqa: E402
from app.services.settings_service import SettingsService  # noqa: E402
from app.services.trip_service import TripService  # noqa: E402
from app.services.user_service import ensure_roles  # noqa: E402
from app.services.vehicle_service import VehicleService  # noqa: E402
from app.utils.time import utcnow  # noqa: E402


def env(name: str, default: str = "") -> str:
    if name in os.environ:
        return os.environ[name]
    for candidate in (ROOT_DIR / ".env", BACKEND / ".env"):
        if candidate.exists():
            value = dotenv_values(candidate).get(name)
            if value:
                return value
    return default


def migrate() -> None:
    cfg = Config(str(BACKEND / "alembic.ini"))
    tables = set(inspect(engine).get_table_names())
    if "users" in tables and "alembic_version" not in tables:
        print("Existing un-versioned database detected -> stamping baseline 0001")
        command.stamp(cfg, "0001")
    command.upgrade(cfg, "head")


def strong_random() -> str:
    return secrets.token_urlsafe(12) + "aA1"


def ensure_manager(db) -> User:
    email = env("ADMIN_EMAIL", "admin@transitops.com").strip().lower()
    role = db.query(Role).filter(Role.name == FLEET_MANAGER).one()
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        password = env("ADMIN_PASSWORD")
        generated = not password
        password = password or strong_random()
        try:
            _check_password(password)
        except ValueError as exc:
            sys.exit(f"ADMIN_PASSWORD rejected: {exc}")
        user = User(name=env("ADMIN_NAME", "Depot Manager"), email=email, password_hash=hash_password(password), role_id=role.id, is_active=True)
        db.add(user)
        db.commit()
        print(f"Created Fleet Manager {email}")
        if generated:
            print(f"  Generated password (shown once, change it after first login): {password}")
    elif user.role_id != role.id:
        user.role_id = role.id
        db.commit()
        print(f"Existing user {email} set to the Fleet Manager role")
    else:
        print(f"Fleet Manager {email} already exists (password untouched)")
    return user


def ensure_demo_users(db) -> None:
    demo = [("Raven K.", "raven.k@transitops.in", DISPATCHER), ("Meera Joshi", "safety@transitops.in", SAFETY_OFFICER),
            ("Kabir Shah", "finance@transitops.in", FINANCIAL_ANALYST)]
    password = env("DEMO_PASSWORD")
    generated = not password
    password = password or strong_random()
    try:
        _check_password(password)
    except ValueError as exc:
        sys.exit(f"DEMO_PASSWORD rejected: {exc}")
    created = []
    for name, email, role_name in demo:
        if db.query(User).filter(User.email == email).first():
            continue
        role = db.query(Role).filter(Role.name == role_name).one()
        db.add(User(name=name, email=email, password_hash=hash_password(password), role_id=role.id, is_active=True))
        created.append(f"{email} ({role_name})")
    db.commit()
    if created:
        print("Created demo users: " + ", ".join(created))
        print(f"  Demo password for them: {password}" + (" (generated, shown once)" if generated else ""))


# ---------------------------------------------------------------- demo depot (from the product spec)
#            reg no          name/model  type     kg    odometer  acquisition  region
VEHICLES = [
    ("GJ01AB4521", "VAN-05",   "Van",   500,   74000,  620000,  "Gandhinagar"),
    ("GJ01AB9981", "TRUCK-11", "Truck", 5000, 182000, 2450000,  "Ahmedabad"),
    ("GJ01AB1120", "MINI-03",  "Mini",  1000,  66000,  410000,  "Gandhinagar"),
    ("GJ01AB0087", "VAN-09",   "Van",   750,  241900,  590000,  "Gandhinagar"),   # retired
    ("GJ01CD3312", "TRK-12",   "Truck", 7500, 156000, 3150000,  "Sanand"),
    ("GJ01CD7788", "MINI-08",  "Mini",  1000,  48000,  430000,  "Ahmedabad"),
    ("GJ01CD2045", "TRUCK-04", "Truck", 5000, 129000, 2380000,  "Sanand"),
    ("GJ18EF6150", "VAN-02",   "Van",   600,   92000,  560000,  "Gandhinagar"),
    ("GJ18EF8841", "TRUCK-07", "Truck", 9000, 205000, 3600000,  "Ahmedabad"),
    ("GJ18EF1907", "MINI-10",  "Mini",  1200,  31000,  470000,  "Sanand"),
]
#            name      licence   cat    expiry (mm/yyyy)   phone prefix  safety
DRIVERS = [
    ("Alex",   "DL-88213", "LMV", date(2028, 12, 31), "98765", 96),
    ("John",   "DL-44120", "HMV", date(2025, 3, 31),  "98220", 81),     # expired + suspended (set after history)
    ("Priya",  "DL-77031", "LMV", date(2027, 8, 31),  "99110", 99),
    ("Suresh", "DL-90045", "HMV", date(2027, 1, 31),  "97440", 88),     # off duty (set after history)
    ("Meera",  "DL-51207", "HMV", date(2028, 5, 31),  "98250", 94),
    ("Kiran",  "DL-63318", "LMV", date(2027, 11, 30), "98980", 91),
    ("Rohan",  "DL-72954", "HMV", date(2029, 2, 28),  "99090", 97),
    ("Anita",  "DL-30871", "LMV", date(2026, 11, 20), "98790", 93),     # licence expiring soon -> compliance flag
]
ROUTES = [("Gandhinagar Depot", "Ahmedabad Hub", 28), ("Vatva Industrial Area", "Sanand Warehouse", 42),
          ("Ahmedabad Hub", "Changodar GIDC", 24), ("Mansa", "Kalol Depot", 21), ("Gandhinagar Depot", "Mehsana Yard", 68),
          ("Sanand Warehouse", "Narol Godown", 36), ("Ahmedabad Hub", "Surat Terminal", 265), ("Kalol Depot", "Vatva Industrial Area", 54)]
EXPENSE_KINDS = [("Toll", "Highway toll plaza"), ("Parking", "Hub yard parking"), ("Toll", "Expressway toll"), ("Miscellaneous", "Loading charges")]


def seed_mock(db, manager_id: int) -> None:
    if db.query(Vehicle).count() or db.query(Driver).count():
        print("Mock data skipped: database already has vehicles/drivers")
        return
    rnd = random.Random(2026)
    now = utcnow()
    vs, ds, ts, ms, es, fs = VehicleService(db), DriverService(db), TripService(db), MaintenanceService(db), ExpenseService(db), FuelService(db)

    veh = {}
    for reg, name, vtype, cap, odo, cost, region in VEHICLES:
        veh[name] = vs.create_vehicle(VehicleCreate(
            registration_number=reg, model=name, vehicle_type=vtype, capacity=cap, odometer=odo, purchase_cost=cost,
            region=region, status="Retired" if name == "VAN-09" else "Available"))
    drv = {}
    for name, lic, cat, expiry, prefix, score in DRIVERS:
        drv[name] = ds.create_driver(DriverCreate(
            name=name, license_number=lic, license_category=cat, license_expiry=date.today() + timedelta(days=400) if name == "John" else expiry,
            phone=f"+91 {prefix}{rnd.randint(10000, 99999)}", safety_score=score))

    pool_v = [veh[n] for n in ("TRUCK-11", "MINI-03", "TRK-12", "TRUCK-04", "VAN-02", "TRUCK-07", "MINI-10")]
    pool_d = [drv[n] for n in ("Alex", "John", "Priya", "Suresh", "Meera", "Kiran", "Rohan", "Anita")]
    freight = {"Van": (18000, 40000), "Mini": (22000, 55000), "Truck": (40000, 110000)}   # demo freight charge per trip (INR)

    def plan(vehicle, driver, route=None, **extra):
        src, dst, dist = route or rnd.choice(ROUTES)
        cap = vehicle.capacity if vehicle else 500
        return ts.create_trip(TripCreate(
            source=src, destination=dst, vehicle_id=vehicle.id if vehicle else None, driver_id=driver.id if driver else None,
            cargo_weight=round(rnd.uniform(0.3, 0.9) * cap), planned_distance=dist, estimated_duration=f"{max(1, dist // 45)}h",
            **extra), manager_id), dist

    def backdate(trip_id, start, end):
        t = db.get(Trip, trip_id)
        t.created_at, t.dispatch_time, t.completion_time = start - timedelta(hours=3), start, end
        for h in db.query(TripHistory).filter(TripHistory.trip_id == t.id):
            h.changed_at = {"Draft": start - timedelta(hours=3), "Dispatched": start, "Completed": end, "Cancelled": end}[h.new_status]
        for f in db.query(FuelLog).filter(FuelLog.trip_id == t.id):
            f.fuel_date = end.date()
        db.flush()
        return t

    # ---- completed history: ~5 months, 6 in the last week so the 7-day chart has data
    windows = []
    for i in range(30):
        v, d = pool_v[i % len(pool_v)], pool_d[(i * 3 + i // 4) % len(pool_d)]
        trip, dist = plan(v, d)
        ts.dispatch_trip(trip.id, TripDispatch(), manager_id)
        actual = round(dist * rnd.uniform(1.0, 1.06), 1)
        revenue = round(rnd.uniform(*freight[v.vehicle_type]), -2)
        ts.complete_trip(trip.id, TripComplete(
            actual_distance=actual, fuel_consumed=round(actual / rnd.uniform(5.5, 11), 1),
            fuel_cost_per_liter=round(rnd.uniform(89.5, 98.0), 2), revenue=revenue), manager_id)
        days_ago = rnd.randint(0, 6) if i < 6 else rnd.randint(7, 150)
        start = now - timedelta(days=days_ago, hours=rnd.randint(1, 9))
        end = start + timedelta(hours=dist // 40 + 2)
        t = backdate(trip.id, start, end)
        windows.append((v.model, t.dispatch_time.date(), t.id))
        if i % 2 == 0:
            for kind, text in rnd.sample(EXPENSE_KINDS, rnd.randint(1, 2)):
                es.create_expense(ExpenseCreate(trip_id=t.id, vehicle_id=v.id, expense_type=kind, amount=round(rnd.uniform(80, 420), 0),
                                                description=text, expense_date=end.date()), manager_id)
        db.commit()

    # ---- cancelled history (John has a few, which gives him an honest completion rate)
    for i in range(4):
        trip, _ = plan(pool_v[i], drv["John"] if i < 3 else drv["Rohan"])
        ts.dispatch_trip(trip.id, TripDispatch(), manager_id)
        ts.cancel_trip(trip.id, TripCancel(remarks="Customer postponed the shipment"), manager_id)
        backdate(trip.id, now - timedelta(days=rnd.randint(3, 60)), now - timedelta(days=rnd.randint(1, 2)))

    # ---- driver compliance states from the spec
    j = drv["John"]
    ds.update_driver(j.id, DriverBase(name=j.name, license_number=j.license_number, license_category=j.license_category,
                                      license_expiry=date(2025, 3, 31), phone=j.phone, safety_score=81, status="Suspended"))
    ds.set_status(drv["Suresh"].id, "Off Duty")

    # ---- maintenance: history (one linked to a TRUCK-11 trip window), then vehicles currently In Shop
    link = next((w for w in windows if w[0] == "TRUCK-11"), windows[0])
    for name, service, cost, start in [("TRUCK-11", "Engine Repair", 18000, link[1]), ("TRK-12", "Tyre Replace", 9400, date.today() - timedelta(days=40)),
                                       ("TRUCK-04", "Oil Change", 3100, date.today() - timedelta(days=65)), ("TRUCK-07", "Brake Service", 7200, date.today() - timedelta(days=20))]:
        ms.create_maintenance(MaintenanceCreate(vehicle_id=veh[name].id, maintenance_type=service, estimated_cost=cost, actual_cost=cost,
                                                start_date=start, end_date=start + timedelta(days=2), status="Completed",
                                                workshop_name=rnd.choice(["Tata Authorized Service", "Ashok Leyland Care", "Shree Auto Works"])), manager_id)
    for name, service, cost in [("MINI-03", "Tyre Replace", 6200), ("VAN-02", "Oil Change", 2500)]:
        ms.create_maintenance(MaintenanceCreate(vehicle_id=veh[name].id, maintenance_type=service, estimated_cost=cost,
                                                start_date=date.today() - timedelta(days=1)), manager_id)

    # ---- live board: two trips on the road with real ETAs, drafts at each stage, one cancelled-unassigned
    for name, driver, route, duration, minutes_ago in [("VAN-05", "Alex", ROUTES[0], "1h 30m", 45), ("MINI-08", "Priya", ROUTES[2], "2h", 50),
                                                       ("TRUCK-11", "Meera", ROUTES[4], "2h 30m", 35), ("TRK-12", "Kiran", ROUTES[5], "1h 45m", 20)]:
        v = veh[name]
        trip = ts.create_trip(TripCreate(source=route[0], destination=route[1], vehicle_id=v.id, driver_id=drv[driver].id,
                                         cargo_weight=round(v.capacity * 0.6), planned_distance=route[2], estimated_duration=duration), manager_id)
        ts.dispatch_trip(trip.id, TripDispatch(), manager_id)
        db.get(Trip, trip.id).dispatch_time = now - timedelta(minutes=minutes_ago)
        db.flush()
    ts.create_trip(TripCreate(source="Vatva Industrial Area", destination="Sanand Warehouse", vehicle_id=veh["TRUCK-04"].id,
                              cargo_weight=3200, planned_distance=42, estimated_duration="1h"), manager_id)                  # awaiting driver
    ts.create_trip(TripCreate(source="Gandhinagar Depot", destination="Mehsana Yard", cargo_weight=300, planned_distance=68,
                              estimated_duration="1h 30m"), manager_id)                                                       # awaiting vehicle
    ts.create_trip(TripCreate(source="Ahmedabad Hub", destination="Changodar GIDC", vehicle_id=veh["TRUCK-07"].id, driver_id=drv["Rohan"].id,
                              cargo_weight=4000, planned_distance=24, estimated_duration="1h"), manager_id)                  # ready to dispatch
    gone = ts.create_trip(TripCreate(source="Mansa", destination="Kalol Depot", cargo_weight=250, planned_distance=21), manager_id)
    ts.cancel_trip(gone.id, TripCancel(remarks="Vehicle went to shop"), manager_id)

    # ---- fuel logs entered by hand (the spec's examples)
    for name, days, liters, cost in [("VAN-05", 3, 42, 3150), ("TRUCK-11", 2, 110, 8400), ("MINI-08", 2, 28, 2050)]:
        fs.create_fuel_log(FuelLogCreate(vehicle_id=veh[name].id, liters=liters, total_cost=cost,
                                         fuel_date=date.today() - timedelta(days=days), fuel_station=rnd.choice(["Indian Oil", "HP Petrol Pump", "Jio-bp"])), manager_id)

    SettingsService(db).update(SettingsUpdate(depot_name="Gandhinagar Depot GJ4", currency="INR", distance_unit="km"))
    db.commit()
    print(f"Demo depot created: {db.query(Vehicle).count()} vehicles, {db.query(Driver).count()} drivers, {db.query(Trip).count()} trips, "
          f"{db.query(Expense).count()} expenses, {db.query(FuelLog).count()} fuel logs - all produced through the real workflow")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mock", action="store_true", help="also create the demo depot + one demo user per role")
    parser.add_argument("--skip-migrate", action="store_true", help="do not run Alembic first")
    args = parser.parse_args()
    if not args.skip_migrate:
        migrate()
    db = SessionLocal()
    try:
        ensure_roles(db)
        manager = ensure_manager(db)
        if args.mock:
            ensure_demo_users(db)
            seed_mock(db, manager.id)
    finally:
        db.close()


if __name__ == "__main__":
    main()
