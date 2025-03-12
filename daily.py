import json
import datetime
import traceback
import logging
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["https://your-framer-site.com"] in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

allow_origins=["https://energized-location-546589.framer.app"]
logging.basicConfig(level=logging.ERROR)

# Define Submission Model
class Submission(BaseModel):
    user: str
    code: str

# Load challenges

def load_challenges():
    try:
        with open("challenges.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Challenges file not found or corrupted.")

# Load submissions
def load_submissions():
    try:
        with open("submissions.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save submissions
def save_submissions(data):
    with open("submissions.json", "w") as file:
        json.dump(data, file, indent=4)

# Function to get today's challenge (rotates daily)
def get_today_challenge():
    challenges = load_challenges()
    challenge_ids = list(challenges.keys())
    
    if not challenge_ids:
        raise HTTPException(status_code=500, detail="No challenges available.")
    
    today_index = datetime.datetime.today().day % len(challenge_ids)
    challenge_id = challenge_ids[today_index]
    return {"challenge_id": challenge_id, **challenges[challenge_id]}

# Endpoint to fetch today's challenge
@app.get("/challenge/today")
def fetch_todays_challenge():
    return get_today_challenge()

# Code execution function
def execute_code(user_code: str, test_cases: List[Dict[str, Any]]):
    try:
        results = []
        local_env = {}

        exec(user_code, {}, local_env)

        if "solve" not in local_env or not callable(local_env["solve"]):
            return {"message": "Error: Function 'solve' not defined or not callable", "status": "error"}

        solve_func = local_env["solve"]
        is_correct = True
        
        for case in test_cases:
            input_data = case["input"]
            expected_output = case["expected_output"]

            try:
                user_output = solve_func(input_data)
                passed = user_output == expected_output
                results.append({
                    "input": input_data,
                    "expected_output": expected_output,
                    "user_output": user_output,
                    "pass": passed
                })
                if not passed:
                    is_correct = False
            except Exception as e:
                return {"message": f"Runtime Error: {str(e)}", "status": "error"}

        return {"message": "All test cases passed!" if is_correct else "Some test cases failed.", "status": "correct" if is_correct else "incorrect", "details": results}
    except Exception as e:
        logging.error(traceback.format_exc())
        return {"message": "An internal error occurred while executing the code.", "status": "error"}

# Endpoint to submit a solution
@app.post("/submit")
def submit_solution(submission: Submission):
    challenge = get_today_challenge()
    challenge_id = challenge["challenge_id"]
    test_cases = challenge["test_cases"]

    result = execute_code(submission.code, test_cases)

    if result["status"] == "error":
        return result

    submissions = load_submissions()
    new_submission = {
        "user": submission.user,
        "challenge_id": challenge_id,
        "code": submission.code,
        "status": result["status"]
    }
    submissions.append(new_submission)
    save_submissions(submissions)

    return result