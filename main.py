from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from database import DatabaseManager
from sleep_api import router as sleep_router  # ✅ import your sleep API router
from fastapi.middleware.cors import CORSMiddleware


# Pydantic model for data validation
class SleepData(BaseModel):
    user_id: int
    start_time: str
    end_time: str

# Initialize database manager
MONGODB_URI = "mongodb+srv://hadchityjoe64:9YERvGvxd0BNaf0G@cluster0.vnit7lj.mongodb.net/sleep_monitor?retryWrites=true&w=majority&appName=Cluster0"
db_manager = DatabaseManager.get_instance(MONGODB_URI)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for testing, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database connection
def get_db():
    try:
        db_manager.connect()
        db = db_manager.get_database()
        yield db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")
    finally:
        db_manager.disconnect()

@app.get("/health")
async def health_check(db=Depends(get_db)):
    return {"status": "ok"}

app.include_router(sleep_router)
