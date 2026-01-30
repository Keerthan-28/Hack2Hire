from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
from interview_engine import InterviewEngine

app = FastAPI(title="Interview Simulation Engine")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = InterviewEngine()

# Input Models
class QuestionInput(BaseModel):
    question_id: int
    difficulty: str
    time_taken: float
    max_time: float
    answer_quality: float

class InterviewLog(BaseModel):
    candidate_id: str
    role: str
    questions: List[QuestionInput]

@app.get("/")
def read_root():
    return {"status": "System Ready", "message": "Interview Engine API is running"}

@app.post("/api/process")
def process_interview(data: InterviewLog):
    try:
        # Convert Pydantic model to dict for engine
        result = engine.process_interview(data.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
