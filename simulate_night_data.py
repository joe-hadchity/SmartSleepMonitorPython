from datetime import datetime, timedelta
import random
from database import DatabaseManager

# Connect using your existing manager
MONGODB_URI = "mongodb+srv://hadchityjoe64:9YERvGvxd0BNaf0G@cluster0.vnit7lj.mongodb.net/sleep_monitor?retryWrites=true&w=majority&appName=Cluster0"
db_manager = DatabaseManager.get_instance(MONGODB_URI)
db_manager.connect()
collection = db_manager.get_database()["sleep_data"]

user_id = "ZTokXgPSOhQmRSnthClZec1gOXL2"
device_id = "virtual_device_001"
source = "simulated"

# Simulate a night with 1-min intervals (23:00 to 08:00 = 9 hours = 540 minutes)
start_time = datetime(2025, 5, 5, 23, 0)
end_time = datetime(2025, 5, 6, 8, 0)
interval = timedelta(minutes=1)

def simulate_entry(ts):
    hour = ts.hour
    if hour <= 1 or hour >= 7:
        bpm = random.randint(70, 85)
        accel = [round(random.uniform(-0.3, 0.3), 3) for _ in range(3)]
    elif hour in [3, 4]:
        bpm = random.randint(40, 55)
        accel = [round(random.uniform(-0.05, 0.05), 3) for _ in range(3)]
    else:
        bpm = random.randint(55, 70)
        accel = [round(random.uniform(-0.1, 0.1), 3) for _ in range(3)]

    return {
        "timestamp": ts.isoformat() + "Z",
        "user_id": user_id,
        "temp_c": round(random.uniform(19.0, 22.0), 1),
        "humidity": round(random.uniform(40.0, 55.0), 1),
        "light": round(random.uniform(0.0, 0.5), 2),
        "sound_db": round(random.uniform(30.0, 38.0), 1),
        "heart_bpm": bpm,
        "accel_x": accel[0],
        "accel_y": accel[1],
        "accel_z": accel[2],
        "source": source,
        "device_id": device_id
    }

# Generate and insert
current = start_time
data = []
while current <= end_time:
    data.append(simulate_entry(current))
    current += interval

collection.insert_many(data)
print(f"Inserted {len(data)} records (1-min interval) for user {user_id}.")

db_manager.disconnect()
