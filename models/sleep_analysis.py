from pydantic import BaseModel
from datetime import datetime
from typing import List
from database import MongoDB

class SleepStageAnalysis(BaseModel):
    rem_minutes: int
    deep_minutes: int
    core_minutes: int
    awake_minutes: int
    awake_count: int

class SleepScoreInput(BaseModel):
    total_sleep_minutes: int
    stages: SleepStageAnalysis
    avg_heart_rate: float
    sound_level: float
    temperature: float
    
class SleepScoreResult(BaseModel):
    score: float
    breakdown: dict
    stages: SleepStageAnalysis

def calculate_sleep_score(data: SleepScoreInput) -> SleepScoreResult:
    """Calculate sleep score based on multiple factors"""
    # Same calculation logic as the Dart version but in Python
    time_score = min(data.total_sleep_minutes / 480, 1) * 30
    rem_score = min(data.stages.rem_minutes / 120, 1) * 20
    deep_score = min(data.stages.deep_minutes / 90, 1) * 25
    disturbance_score = 25 - min(data.stages.awake_count * 0.5, 25)
    
    # Environment penalty calculation
    env_penalty = 0
    if data.sound_level > 45: env_penalty += 10
    elif data.sound_level > 55: env_penalty += 20
    if data.temperature < 16 or data.temperature > 24: env_penalty += 10
    elif data.temperature < 14 or data.temperature > 26: env_penalty += 20
    
    environment_score = 25 - env_penalty
    heart_rate_score = 25 - min((data.avg_heart_rate - 50) / 2, 25)
    
    total = time_score + rem_score + deep_score + disturbance_score + environment_score + heart_rate_score
    final_score = max(0, min(100, total))
    
    return SleepScoreResult(
        score=final_score,
        breakdown={
            "time_score": time_score,
            "rem_score": rem_score,
            "deep_score": deep_score,
            "disturbance_score": disturbance_score,
            "environment_score": environment_score,
            "heart_rate_score": heart_rate_score
        }
    )