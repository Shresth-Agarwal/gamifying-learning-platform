from fastapi import FastAPI, HTTPException
from vertexai.preview.generative_models import GenerativeModel
import tempfile
import subprocess
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
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

@app.get("/get_buggy_code")
def get_buggy_code():
    buggy_code = generate_buggy_code()
    correct_code = generate_correct_code(buggy_code)
    return {"buggy_code": buggy_code, "correct_code": correct_code}

@app.post("/submit_code")
def submit_code(user_code: str, correct_code: str):
    result = evaluate_user_code(user_code, correct_code)
    return result
