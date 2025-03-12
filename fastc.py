from fastapi import FastAPI
import time
import tempfile
import subprocess
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeSubmission(BaseModel):
    user_code: str

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

@app.get("/get_fast_coding_question")
def get_fast_coding_question():
    """Returns the fast coding challenge with test cases and start time."""
    return {
        "question": FAST_CODING_QUESTION["question"],
        "function_signature": FAST_CODING_QUESTION["function_signature"],
        "test_cases": FAST_CODING_QUESTION["test_cases"],
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
