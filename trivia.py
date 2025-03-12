import json
import random
from fastapi import FastAPI, HTTPException
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