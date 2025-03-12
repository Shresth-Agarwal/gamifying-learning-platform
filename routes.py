from debug import get_buggy_code, submit_code, ai_info
from daily import fetch_todays_challenge, submit_solution
from fastc import get_fast_coding_question, submit_fast_coding_solution
from trivia import get_trivia, check_answer
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class CodeSubmission(BaseModel):
    user_code: str

class Submission(BaseModel):
    user: str
    code: str

class AnswerSubmission(BaseModel):
    selected_answer: str

@app.get("/get_buggy_code")
def get_buggy_code_endpoint():
    return get_buggy_code()

@app.post("/submit_code")
def submit_code_endpoint(submission: CodeSubmission):
    return submit_code(submission)

@app.get("/challenge/today")
def fetch_todays_challenge_endpoint():
    return fetch_todays_challenge()

@app.post("/submit")
def submit_solution_endpoint(submission: Submission):
    return submit_solution(submission)

@app.get("/get_fast_coding_question")
def get_fast_coding_question_endpoint():
    return get_fast_coding_question()

@app.post("/submit_fast_coding")
def submit_fast_coding_solution_endpoint(submission: CodeSubmission):
    return submit_fast_coding_solution(submission)


@app.post("/ai_info")
def ai_info_endpoint():
    return ai_info()


@app.get("/trivia")
def get_trivia_endpoint():
    return get_trivia()


@app.post("/trivia/answer")
def check(submission: AnswerSubmission):
    return check_answer(submission)

@app.get("/")
def home():
    return {"Message": "Welcome to our site"}


