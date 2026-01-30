import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

# --- Constants & Enums ---

class InterviewState(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"

@dataclass
class QuestionResult:
    q_id: str
    difficulty: str  # easy, medium, hard
    base_score: float  # 10, 20, 30
    answer_quality: float # 0.0 to 1.0
    time_taken: float
    max_time: float
    
    # Calculated
    raw_score: float = 0.0
    time_penalty: float = 0.0
    final_score: float = 0.0 # score after penalties
    score_percentage: float = 0.0 # 0-100 normalized for this question
    
    state: str = "COMPLETED" 

@dataclass
class InterviewContext:
    interview_id: str
    candidate_id: str
    role: str
    state: InterviewState = InterviewState.NOT_STARTED
    
    results: List[QuestionResult] = field(default_factory=list)
    state_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Adaptive State
    current_difficulty_trend: int = 0 # +1 for high score, -1 for low score. Reset on mixed.
    consecutive_low_scores: int = 0 # For termination
    termination_reason: Optional[str] = None

# --- Engine Class ---

class InterviewEngine:
    def __init__(self):
        pass

    def process_interview(self, data: dict) -> dict:
        questions = data.get("questions", [])
        
        ctx = InterviewContext(
            interview_id=data.get("candidate_id", "UNKNOWN"), # Using candidate_id as ID based on sample input
            candidate_id=data.get("candidate_id", "UNKNOWN"),
            role=data.get("role", "Software Engineer")
        )
        ctx.state = InterviewState.IN_PROGRESS

        # Difficulty Map
        base_scores = {"easy": 10, "medium": 20, "hard": 30}

        for idx, q_data in enumerate(questions):
            # Check Termination (3 consecutive low scores < 40%)
            if ctx.consecutive_low_scores >= 3:
                ctx.state = InterviewState.TERMINATED
                ctx.termination_reason = "POOR_PERFORMANCE"
                break

            q_id = q_data.get("question_id")
            difficulty = q_data.get("difficulty", "medium").lower()
            time_taken = q_data.get("time_taken", 0)
            max_time = q_data.get("max_time", 60)
            quality = q_data.get("answer_quality", 0.0)

            # 1. Base Score
            base = base_scores.get(difficulty, 20)
            
            # 2. Answer Quality Multiplier
            # "final_question_score = base_score * answer_quality"
            # Note: This implies the score is proportional.
            score_after_quality = base * quality

            # 3. Time Penalty
            # "If time_taken > max_time -> subtract 20% of question score"
            time_penalty = 0.0
            if time_taken > max_time:
                time_penalty = score_after_quality * 0.20
            
            final_q_score = max(0, score_after_quality - time_penalty)
            
            # Normalized Percentage (for 0-100 logic and adaptive triggers)
            # Max possible score for this question was 'base'.
            percent_score = (final_q_score / base) * 100 if base > 0 else 0

            # Store Result
            res = QuestionResult(
                q_id=str(q_id),
                difficulty=difficulty,
                base_score=base,
                answer_quality=quality,
                time_taken=time_taken,
                max_time=max_time,
                raw_score=round(score_after_quality, 2),
                time_penalty=round(time_penalty, 2),
                final_score=round(final_q_score, 2),
                score_percentage=round(percent_score, 2)
            )
            ctx.results.append(res)

            # 4. Adaptive Difficulty Logic
            # "Two consecutive > 80% -> Increase"
            # "Two consecutive < 40% -> Decrease"
            
            # --- Termination Tracker ---
            if percent_score < 40:
                ctx.consecutive_low_scores += 1
            else:
                ctx.consecutive_low_scores = 0 # Reset on good performance

            # Log State
            ctx.state_log.append({
                "question_id": q_id,
                "score_percent": round(percent_score, 1),
                "consecutive_low": ctx.consecutive_low_scores,
                "difficulty": difficulty
            })

        # Final Check for Termination after loop (if caused by last question)
        if ctx.state != InterviewState.TERMINATED and ctx.consecutive_low_scores >= 3:
            ctx.state = InterviewState.TERMINATED
            ctx.termination_reason = "POOR_PERFORMANCE"

        if ctx.state != InterviewState.TERMINATED:
            ctx.state = InterviewState.COMPLETED

        return self.compute_final_readiness(ctx)

    def compute_final_readiness(self, ctx: InterviewContext) -> dict:
        if not ctx.results:
            return {"error": "No questions processed"}

        # 1. Accuracy Score (60%)
        # Logic: Weighted average of normalized scores? Or Sum(Final) / Sum(Max)?
        # Let's use Sum(Final) / Sum(Base) to get a neat 0-100 accuracy metric.
        total_obtained = sum(r.final_score for r in ctx.results)
        total_base = sum(r.base_score for r in ctx.results)
        accuracy_raw = (total_obtained / total_base * 100) if total_base > 0 else 0
        
        # 2. Time Efficiency (20%)
        # Logic: Average of efficiency per question.
        # Efficiency = max(0, (Max - Taken + Bonus?))
        # Simple metric: If Taken < Max, 100%. If Taken > Max, penalize.
        # Prompt doesn't give precise formula for efficiency COMPONENT, only penalty on score.
        # Let's define Efficiency = 1 - (max(0, TimeTaken - MaxTime) / MaxTime).
        # i.e. 100% if within limit. Lower if over.
        # Or better: (MaxTime / TimeTaken) clamped?
        # Let's go with: 100% if taken <= max. 
        # If taken > max, efficiency drops. e.g. taken=1.5x -> 50%?
        # Let's use: max(0, 100 - (OverTimePercentage * 100))
        # Where OverTime = (Taken - Max)/Max.
        time_scores = []
        for r in ctx.results:
            if r.time_taken <= r.max_time:
                time_scores.append(100)
            else:
                extra = r.time_taken - r.max_time
                ratio = extra / r.max_time
                eff = max(0, 100 - (ratio * 100)) # If double time, 0 efficiency
                time_scores.append(eff)
        
        time_efficiency = sum(time_scores) / len(time_scores) if time_scores else 0

        # 3. Consistency (20%)
        # Logic: Based on variance of scores.
        # 100 - StandardDeviation (roughly).
        # Valid scores are 0-100. StdDev can be ~30-40 max usually.
        # Formula: 100 - StdDev. (So 0 variation = 100 consistency).
        scores = [r.score_percentage for r in ctx.results]
        if len(scores) > 1:
            mean_s = sum(scores) / len(scores)
            variance = sum((x - mean_s) ** 2 for x in scores) / len(scores)
            std_dev = math.sqrt(variance)
            consistency = max(0, 100 - std_dev)
        else:
            consistency = 100 # 1 question is perfectly consistent

        # Final Calculation
        # Score = (Acc * 0.6) + (Time * 0.2) + (Cons * 0.2)
        final_score = (accuracy_raw * 0.6) + (time_efficiency * 0.2) + (consistency * 0.2)
        final_score = round(final_score, 1)

        # Recommendation
        rec = "Not Ready"
        if final_score >= 85:
            rec = "Strong Hire"
        elif final_score >= 70:
            rec = "Hire"
        elif final_score >= 50:
            rec = "Borderline"
        
        # Breakdown
        output_results = []
        for r in ctx.results:
            output_results.append({
                "question_id": r.q_id,
                "difficulty": r.difficulty,
                "score_percentage": round(r.score_percentage, 1),
                "time_taken": r.time_taken,
                "time_limit": r.max_time,
                "status": "Passed" if r.score_percentage >= 40 else "Failed",
                "penalties": {
                    "time": r.time_penalty
                }
            })

        return {
            "interview_id": ctx.interview_id, # "candidate_id" from input, reused
            "candidate_id": ctx.candidate_id,
            "role": ctx.role,
            "final_score": final_score,
            "recommendation": rec,
            "metrics": {
                "accuracy": round(accuracy_raw, 1),
                "time_efficiency": round(time_efficiency, 1),
                "consistency": round(consistency, 1)
            },
            "termination_reason": ctx.termination_reason,
            "questions": output_results,
            "status": ctx.state.value,
            "state_log": ctx.state_log
        }
