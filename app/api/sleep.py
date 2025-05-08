from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from models.sleep_analysis import (
    SleepStageAnalysis,
    SleepScoreInput,
    SleepScoreResult,
    calculate_sleep_score
)
from database import get_db

router = APIRouter()

@router.get("/sleep/analysis/{user_id}", response_model=SleepScoreResult)
async def get_sleep_analysis(user_id: str, db=Depends(get_db)):
    try:
        # Get sleep data from last night (10pm to 8am example)
        start_time = datetime.now().replace(hour=22, minute=0, second=0) - timedelta(days=1)
        end_time = start_time + timedelta(hours=10)
        
        sleep_data = await db["sleep_data"].find({
            "user_id": user_id,
            "timestamp": {
                "$gte": start_time,
                "$lt": end_time
            }
        }).to_list(length=None)
        
        if not sleep_data:
            raise HTTPException(status_code=404, detail="No sleep data found")
        
        # Calculate averages and stages
        stages = analyze_sleep_stages(sleep_data)
        avg_heart = sum(d["heart_bpm"] for d in sleep_data) / len(sleep_data)
        avg_sound = sum(d["sound_db"] for d in sleep_data) / len(sleep_data)
        avg_temp = sum(d["temp_c"] for d in sleep_data) / len(sleep_data)
        total_minutes = 8 * 60  # Simplified - real calculation would use timestamps
        
        score_input = SleepScoreInput(
            total_sleep_minutes=total_minutes,
            stages=stages,
            avg_heart_rate=avg_heart,
            sound_level=avg_sound,
            temperature=avg_temp
        )
        
        return calculate_sleep_score(score_input)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_sleep_stages(raw_data) -> SleepStageAnalysis:
    # Simplified implementation - real version would analyze HRV, movement etc.
    return SleepStageAnalysis(
        rem_minutes=112,
        deep_minutes=86,
        core_minutes=201,
        awake_minutes=18,
        awake_count=3
    )