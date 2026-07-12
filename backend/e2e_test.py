import requests
import datetime
import time

BASE_URL = "http://localhost:8000/api/v1"

# 1. Login
print("Logging in...")
login_response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "admin@transitops.com",
    "password": "password123"
})
if login_response.status_code != 200:
    print("Login failed:", login_response.text)
    exit(1)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("Login successful.")

# 2. Create Vehicle
print("Creating vehicle...")
vehicle_data = {
    "registration_number": f"TEST-{int(time.time())}",
    "model": "Test Truck",
    "vehicle_type": "Truck",
    "capacity": 5000,
    "odometer": 10000,
    "purchase_cost": 50000
}
v_res = requests.post(f"{BASE_URL}/vehicles/", json=vehicle_data, headers=headers)
if v_res.status_code != 201:
    print("Vehicle creation failed:", v_res.text)
    exit(1)
vehicle = v_res.json()
print(f"Vehicle created: {vehicle['id']}")

# 3. Create Driver
print("Creating driver...")
driver_data = {
    "name": "Test Driver",
    "license_number": f"LIC-{int(time.time())}",
    "license_category": "Heavy",
    "license_expiry": (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%Y-%m-%d"),
    "phone": f"555-{int(time.time()) % 10000}"
}
d_res = requests.post(f"{BASE_URL}/drivers/", json=driver_data, headers=headers)
if d_res.status_code != 201:
    print("Driver creation failed:", d_res.text)
    exit(1)
driver = d_res.json()
print(f"Driver created: {driver['id']}")

# 4. Create Trip
print("Creating trip...")
trip_data = {
    "source": "New York",
    "destination": "Boston",
    "vehicle_id": vehicle["id"],
    "driver_id": driver["id"],
    "cargo_weight": 2000,
    "planned_distance": 250
}
t_res = requests.post(f"{BASE_URL}/trips/", json=trip_data, headers=headers)
if t_res.status_code != 201:
    print("Trip creation failed:", t_res.text)
    exit(1)
trip = t_res.json()
trip_id = trip["id"]
print(f"Trip created: {trip_id}, status: {trip['status']}")

# 5. Dispatch Trip
print("Dispatching trip...")
disp_res = requests.put(f"{BASE_URL}/trips/{trip_id}/dispatch", json={"remarks": "Go!"}, headers=headers)
if disp_res.status_code != 200:
    print("Trip dispatch failed:", disp_res.text)
    exit(1)
print(f"Trip dispatched, status: {disp_res.json()['status']}")

# 6. Check Dashboard Stats
print("Checking dashboard stats...")
stats_res = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
if stats_res.status_code != 200:
    print("Stats fetch failed:", stats_res.text)
    exit(1)
stats = stats_res.json()
print(f"Active trips: {stats['active_trips']}")

# 7. Complete Trip
print("Completing trip...")
comp_data = {
    "actual_distance": 260,
    "fuel_consumed": 40,
    "final_odometer": 10260,
    "remarks": "Completed successfully"
}
comp_res = requests.put(f"{BASE_URL}/trips/{trip_id}/complete", json=comp_data, headers=headers)
if comp_res.status_code != 200:
    print("Trip complete failed:", comp_res.text)
    exit(1)
print(f"Trip completed, status: {comp_res.json()['status']}")

print("All E2E tests passed!")
