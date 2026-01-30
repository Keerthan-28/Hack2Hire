import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/process"

def test_interview_logic():
    print("Running Verification Tests...")

    # Test Case 1: Perfect Score
    payload_perfect = {
        "candidate_id": "TEST_PERFECT",
        "role": "Software Engineer",
        "questions": [
            {"question_id": 1, "difficulty": "medium", "time_taken": 30, "max_time": 60, "answer_quality": 1.0},
            {"question_id": 2, "difficulty": "hard", "time_taken": 50, "max_time": 100, "answer_quality": 1.0}
        ]
    }
    try:
        res = requests.post(BASE_URL, json=payload_perfect)
        data = res.json()
        print(f"[TEST 1] Perfect Score: {data['final_score']} (Expected > 95)")
        assert data['final_score'] > 95, "Score should be near 100"
        assert data['recommendation'] == "Strong Hire", "Should be Strong Hire"
    except Exception as e:
        print(f"[FAIL] Test 1: {e}")
        return False

    # Test Case 2: Termination (3 low scores)
    payload_term = {
        "candidate_id": "TEST_TERM",
        "role": "Software Engineer",
        "questions": [
            {"question_id": 1, "difficulty": "easy", "time_taken": 10, "max_time": 60, "answer_quality": 0.1}, # 10%
            {"question_id": 2, "difficulty": "easy", "time_taken": 10, "max_time": 60, "answer_quality": 0.1}, # 10%
            {"question_id": 3, "difficulty": "easy", "time_taken": 10, "max_time": 60, "answer_quality": 0.1}, # 10%
            {"question_id": 4, "difficulty": "medium", "time_taken": 10, "max_time": 60, "answer_quality": 1.0} # Should not be reached/counted if terminated?
        ]
    }
    try:
        res = requests.post(BASE_URL, json=payload_term)
        data = res.json()
        print(f"[TEST 2] Termination Status: {data['status']}")
        print(f"         Termination Reason: {data.get('termination_reason')}")
        assert data['status'] == "TERMINATED", "Should be TERMINATED"
        assert data['termination_reason'] == "POOR_PERFORMANCE", "Reason should be POOR_PERFORMANCE"
    except Exception as e:
        print(f"[FAIL] Test 2: {e}")
        return False

    print("\nVerification Passed! System is functionally correct.")
    return True

if __name__ == "__main__":
    success = test_interview_logic()
    if not success:
        sys.exit(1)
