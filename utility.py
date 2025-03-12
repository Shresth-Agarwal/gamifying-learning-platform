from fastapi import FastAPI, HTTPException
from vertexai.preview.generative_models import GenerativeModel
import tempfile
import subprocess
import os
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import json
import random
import time
import datetime
import logging
import traceback
from typing import List, Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load questions from JSON file
def load_questions():
    try:
        with open("trivia.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Trivia file not found or corrupted.")

questions = load_questions()
current_question = {}  # Store the current question for validation

# Model for answer submission
class AnswerSubmission(BaseModel):
    selected_answer: str

# Endpoint to fetch a random trivia question
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

#daily

class TopicRequest(BaseModel):
    topic: str

class CodeSubmission(BaseModel):
    user_code: str
    correct_code: str


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Shresth Agarwal\\OneDrive\\Documents\\Project\\edu.json"
model = GenerativeModel("gemini-2.0-pro-exp-02-05")


def generate_buggy_code():
    """Uses Vertex AI to generate a buggy Python script."""
    prompt = "Generate a small Python script with one or two intentional bugs. Make the response as small as possible. Every time the response must be different andonly ever return the codes. No additional sentences"
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_correct_code(buggy_code):
    """Uses Vertex AI to generate the correct version of the buggy script."""
    prompt = f"Fix the bugs in the following Python script and return only the corrected code:\n{buggy_code}"
    response = model.generate_content(prompt)
    return response.text.strip()

def evaluate_user_code(user_code, correct_code):
    """Runs the user-submitted code and compares output with correct version."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
        temp.write(user_code.encode())
        temp.flush()
        try:
            result = subprocess.run(["python3", temp.name], capture_output=True, text=True, timeout=5)
            user_output = result.stdout.strip()
        except Exception:
            return {"status": "Failed", "message": "Error while executing."}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp_correct:
        temp_correct.write(correct_code.encode())
        temp_correct.flush()
        correct_result = subprocess.run(["python3", temp_correct.name], capture_output=True, text=True, timeout=5)
        correct_output = correct_result.stdout.strip()
    
    if user_output == correct_output:
        if user_code.strip() == correct_code.strip():
            return {"status": "Perfect Score!"}
        else:
            return {"status": "Partial Fix", "message": "Output correct, but structure differs."}
    else:
        return {"status": "Failed", "message": "Output incorrect. Keep debugging!"}


#debug

# Sample fast coding question (Replace dynamically as needed)
FAST_CODING_QUESTION = {
    "question": "Write a function solve(a: int, b: int) that returns the sum of a and b.",
    "function_signature": "def solve(a: int, b: int):",
    "test_cases": [
        {"input": (2, 3), "expected_output": 5},
        {"input": (10, 20), "expected_output": 30},
        {"input": (-5, 5), "expected_output": 0}
    ]
}



def run_user_function(user_code):
    """Injects the user function into a test runner and evaluates output."""
    # Generate test runner script
    test_script = f"""
{user_code}

import json

test_cases = {FAST_CODING_QUESTION["test_cases"]}

results = []
for test in test_cases:
    input_values = test["input"]
    expected_output = test["expected_output"]
    try:
        user_output = solve(*input_values)
        results.append({{"input": input_values, "expected": expected_output, "actual": user_output, "passed": user_output == expected_output}})
    except Exception as e:
        results.append({{"input": input_values, "expected": expected_output, "actual": str(e), "passed": False}})

print(json.dumps(results))
"""

    # Run the script
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
        temp.write(test_script.encode())
        temp.flush()

        try:
            result = subprocess.run(
                ["python3", temp.name],
                capture_output=True,
                text=True,
                #timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            return str(e)

@app.post("/submit_fast_coding_solution")
def submit_fast_coding_solution(submission: CodeSubmission):
    """Evaluates user function automatically with test cases and checks time limit."""
    current_time = time.time()

    test_results = run_user_function(submission.user_code)

    return {
        "status": "Completed",
        "message": "All Test Cases Passed",
        "results": test_results
    }
#fastc
@app.get("/get_fast_coding_question")
def get_fast_coding_question():
    """Returns the fast coding challenge with test cases and start time."""
    return {
        "question": FAST_CODING_QUESTION["question"],
        "function_signature": FAST_CODING_QUESTION["function_signature"],
        "test_cases": FAST_CODING_QUESTION["test_cases"],
    }
@app.get("/get_buggy_code")
def get_buggy_code():
    buggy_code = generate_buggy_code()
    correct_code = generate_correct_code(buggy_code)
    return {"buggy_code": buggy_code, "correct_code": correct_code}

@app.post("/submit_code")
def submit_code(submission: CodeSubmission):
    result = evaluate_user_code(submission.user_code, submission.correct_code)
    return result

@app.post("/get_info")
def ai_info(request: TopicRequest):
    # Extract the topic from the JSON request body
    topic = request.topic
    
    # Create a prompt using the extracted topic
    prompt = f"Explain the concept of {topic} in coding in a simple and detailed way. Include examples, analogies if necessary, and break down the explanation step by step. Make sure to explain why and how it's used, as well as its importance in programming. For example, talk about practical applications or scenarios where this concept is commonly used. Explain in minimum lines possible(not more than 15 lines)."
    
    # Generate response (simulated)
    response = model.generate_content(prompt)
    
    # Return the stripped response
    return {"response": response.text.strip()}
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
# Endpoint to fetch today's challenge
@app.get("/challenge/today")
def fetch_todays_challenge():
    return get_today_challenge()
@app.get("/trivia")
def get_trivia():
    global current_question
    current_question = random.choice(questions)  # Pick a random question
    return {
        "question": current_question["question"],
        "options": current_question["options"]
    }

# Endpoint to check the submitted answer
@app.post("/trivia/answer")
def check_answer(submission: AnswerSubmission):
    if not current_question:
        raise HTTPException(status_code=400, detail="No question has been sent yet.")

    correct_answer = current_question["correct_answer"]
    is_correct = submission.selected_answer == correct_answer

    return {
        "correct": is_correct,
        "message": "Correct!" if is_correct else f"Wrong! The correct answer was {correct_answer}."
    }
#trivia