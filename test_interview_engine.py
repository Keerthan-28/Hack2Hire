import unittest
from interview_engine import InterviewEngine

class TestInterviewEngine(unittest.TestCase):
    def setUp(self):
        self.engine = InterviewEngine()

    def test_perfect_candidate(self):
        # All 95%+, no penalties
        data = {
            "interview_id": "TEST_1",
            "candidate_id": "C1",
            "role": "Backend Engineer",
            "questions": [
                {"q_id": "Q1", "type": "CODING", "max_score": 100, "time_limit": 100, "adaptive_weight": 1.0},
                {"q_id": "Q2", "type": "BEHAVIORAL", "max_score": 50, "time_limit": 60}
            ],
            "responses": [
                {
                    "q_id": "Q1", "start_time": 0, "end_time": 90, 
                    "ai_feedback": {"correctness": 1.0, "completeness": 1.0, "complexity": 1.0},
                    "interruptions": 0
                },
                {
                    "q_id": "Q2", "start_time": 100, "end_time": 150,
                    "ai_feedback": {"clarity": 1.0, "relevance": 1.0, "specificity": 1.0},
                    "interruptions": 0
                }
            ],
            "system_events": []
        }
        res = self.engine.process_interview(data)
        # Q1: Raw=(0.5+0.3+0.2)*100 = 100. W=1.0. Final=100. Ratio=1.0. Next W +0.2 = 1.2
        # Q2: Raw=(0.4+0.4+0.2)*50=50. W=1.2. Final=60.
        # Total Weighted = (100*1.3) + (60*0.9) = 130 + 54 = 184.
        # Total Max = 100 + 50 = 150. 
        # Score = (184/150)*100 = 122.66 -> Rounded 122.7
        # Wait, if multiplier > 1, score > 100. Prompt logic: "Perfect... Expected Score >= 90" (consistent).
        self.assertGreaterEqual(res["final_score"], 90)
        self.assertFalse(res["performance_summary"]["early_termination"])

    def test_time_management_issues(self):
        # 30% over time -> 0.25 * ratio * raw penalty
        data = {
            "interview_id": "TEST_2",
            "candidate_id": "C2",
            "role": "Frontend Engineer",
            "questions": [
                {"q_id": "Q1", "type": "CODING", "max_score": 100, "time_limit": 100, "adaptive_weight": 1.0}
            ],
            "responses": [
                {
                    "q_id": "Q1", "start_time": 0, "end_time": 130, # 30% over
                    "ai_feedback": {"correctness": 0.8, "completeness": 0.8, "complexity": 0.8},
                    "interruptions": 0
                }
            ],
            "system_events": [{"type": "TIMEOUT", "q_id": "Q1"}]
        }
        res = self.engine.process_interview(data)
        # Raw = 80.
        # Time Penalty: Ratio=0.3. Tier 20-50%: 0.25 * ratio * raw = 0.25 * 0.3 * 80 = 6.0
        # Weighted = (80 - 6) * 1.0 = 74.
        # Tech Role coding mult 1.3 -> 74 * 1.3 = 96.2
        # Final = 96.2 / 100 = 96.2%
        
        breakdown = res["score_breakdown"][0]
        self.assertAlmostEqual(breakdown["time_penalty"], 6.0)

    def test_early_termination_poor_performance(self):
        # Avg score < 30%
        data = {
            "interview_id": "TEST_3",
            "candidate_id": "C3",
            "role": "General",
            "questions": [
                {"q_id": "Q1", "type": "CODING", "max_score": 100, "time_limit": 300, "adaptive_weight": 1.0}, # Fail
                {"q_id": "Q2", "type": "CODING", "max_score": 100, "time_limit": 300}, # Fail
                {"q_id": "Q3", "type": "CODING", "max_score": 100, "time_limit": 300}  # Should skip
            ],
            "responses": [
                {
                    "q_id": "Q1", "start_time": 0, "end_time": 10, 
                    "ai_feedback": {"correctness": 0.1, "completeness": 0.1, "complexity": 0.1},
                    "interruptions": 0
                },
                 {
                    "q_id": "Q2", "start_time": 0, "end_time": 10, 
                    "ai_feedback": {"correctness": 0.2, "completeness": 0.2, "complexity": 0.2},
                    "interruptions": 0
                }
            ],
            "system_events": [{"type": "EARLY_TERMINATION", "reason": "POOR_PERFORMANCE"}]
        }
        res = self.engine.process_interview(data)
        self.assertTrue(res["performance_summary"]["early_termination"])
        self.assertEqual(res["performance_summary"]["attempted_questions"], 2)
        # Q3 should not be in breakdown or state log as COMPLETED
        q3_check = any(x["q_id"] == "Q3" for x in res["score_breakdown"])
        self.assertFalse(q3_check)

    def test_weight_rollercoaster(self):
        # High -> Low -> High
        data = {
            "interview_id": "TEST_4",
            "candidate_id": "C4",
            "role": "Dev",
            "questions": [
                {"q_id": "Q1", "type": "CODING", "max_score": 100, "time_limit": 300, "adaptive_weight": 1.0},
                {"q_id": "Q2", "type": "CODING", "max_score": 100, "time_limit": 300},
                {"q_id": "Q3", "type": "CODING", "max_score": 100, "time_limit": 300}
            ],
            "responses": [
                { "q_id": "Q1", "start_time":0, "end_time":10, "ai_feedback": {"correctness":1.0, "completeness":1.0, "complexity":1.0}}, # 100% -> +0.2 -> 1.2
                { "q_id": "Q2", "start_time":0, "end_time":10, "ai_feedback": {"correctness":0.1, "completeness":0.1, "complexity":0.1}}, # 10% -> -0.3 -> 0.9
                { "q_id": "Q3", "start_time":0, "end_time":10, "ai_feedback": {"correctness":1.0, "completeness":1.0, "complexity":1.0}}  # 100%
            ],
            "system_events": []
        }
        res = self.engine.process_interview(data)
        log = res["state_log"]
        # Log captures weight AT START of Q.
        # Q1: 1.0 (input)
        # Q2: 1.2 (from Q1 perf)
        # Q3: 0.9 (from Q2 perf)
        
        # We need to find entries where state=IN_PROGRESS to see the active weight
        w1 = next(l["weight"] for l in log if l["question"]=="Q1" and l["state"]=="IN_PROGRESS")
        w2 = next(l["weight"] for l in log if l["question"]=="Q2" and l["state"]=="IN_PROGRESS")
        w3 = next(l["weight"] for l in log if l["question"]=="Q3" and l["state"]=="IN_PROGRESS")
        
        self.assertEqual(w1, 1.0)
        self.assertEqual(w2, 1.2)
        self.assertEqual(w3, 0.9)

if __name__ == '__main__':
    unittest.main()
