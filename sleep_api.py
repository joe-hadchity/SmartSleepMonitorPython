from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from database import DatabaseManager

router = APIRouter()

# Dependency to get DB
def get_db():
    db_manager = DatabaseManager.get_instance()
    db_manager.connect()
    try:
        yield db_manager.get_database()
    finally:
        db_manager.disconnect()

@router.get("/sleep-session/{user_id}")
def get_sleep_session(user_id: str, date: str = Query(...), db=Depends(get_db)):
    try:
        base_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    start_time = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = base_date + timedelta(days=1)

    sleep_data = db["sleep_data"]

    try:
        raw_data = list(sleep_data.find({
            "user_id": user_id,
            "timestamp": {
                "$gte": start_time.isoformat() + "Z",
                "$lt": end_time.isoformat() + "Z"
            }
        }).sort("timestamp", 1))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")

    if not raw_data:
        raise HTTPException(status_code=404, detail="No sleep data found for this date.")

    try:
        stages = process_sleep_stages(raw_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sleep stage processing failed: {e}")

    return {
        "user_id": user_id,
        "date": date,
        "start_time": raw_data[0]["timestamp"],
        "end_time": raw_data[-1]["timestamp"],
        "stages": stages
    }

def process_sleep_stages(data):
    stages = []
    for doc in data:
        bpm = doc.get("heart_bpm", 0)
        movement = abs(doc.get("accel_x", 0)) + abs(doc.get("accel_y", 0)) + abs(doc.get("accel_z", 0))

        if bpm > 80 or movement > 1.2:
            stage = "Awake"
        elif bpm > 65:
            stage = "REM"
        elif bpm > 50:
            stage = "Core"
        else:
            stage = "Deep"

        stages.append({
            "timestamp": doc["timestamp"],
            "stage": stage
        })

    return stages
