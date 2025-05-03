from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from database import DatabaseManager  # Import the DatabaseManager

# Pydantic model for data validation
class SleepData(BaseModel):
    user_id: int
    start_time: str
    end_time: str

# Initialize the database manager with the MongoDB URI from environment variable
MONGODB_URI = "mongodb+srv://hadchityjoe64:9YERvGvxd0BNaf0G@cluster0.vnit7lj.mongodb.net/sleep_monitor?retryWrites=true&w=majority&appName=Cluster0" # Hardcoded for this example
db_manager = DatabaseManager.get_instance(MONGODB_URI)

# FastAPI application
app = FastAPI()

# Dependency to get the database connection
def get_db():
    """
    FastAPI dependency to get the database session.
    """
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
    """
    API endpoint to check the database connection.
    """
    return {"status": "ok"}