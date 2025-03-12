# API Documentation for Our Website

Notice: This code can only be executed when the user has google autherization file
## Overview
This API provides various endpoints for coding challenges, AI-generated buggy code, trivia games, and fast coding challenges. It is built using FastAPI and utilizes Vertex AI for generating buggy code.

---

## Base URL
```
https://energized-location-546589.framer.app
```

---

## Authentication
Currently, the API does not require authentication. Future versions may include API keys or user authentication.

---

# **API Documentation**

## **Trivia Endpoints**  
1. **GET `/trivia`**  
   - **Description:** Returns a random trivia question along with multiple-choice options.  

2. **POST `/trivia/answer`**  
   - **Description:** Checks if the submitted answer is correct and returns a message indicating correctness.  
   - **Request Body:**  
     ```json
     {
       "selected_answer": "Your chosen answer"
     }
     ```  

---

## **Daily Challenge Endpoints**  
3. **GET `/challenge/today`**  
   - **Description:** Returns today's coding challenge, including test cases.  

4. **POST `/submit`**  
   - **Description:** Evaluates the submitted code against predefined test cases and returns pass/fail results.  
   - **Request Body:**  
     ```json
     {
       "user": "username",
       "code": "your submitted solution"
     }
     ```  

---

## **AI-Powered Coding Explanation**  
5. **POST `/get_info`**  
   - **Description:** Generates an AI-powered explanation of the given coding concept in a simplified way.  
   - **Request Body:**  
     ```json
     {
       "topic": "Concept name (e.g., Recursion)"
     }
     ```  

---

## **Buggy Code Debugging**  
6. **GET `/get_buggy_code`**  
   - **Description:** Returns a randomly generated buggy code snippet along with its corrected version.  

7. **POST `/submit_code`**  
   - **Description:** Compares user-submitted code with the correct code and returns feedback.  
   - **Request Body:**  
     ```json
     {
       "user_code": "Your submitted buggy code",
       "correct_code": "Expected correct version"
     }
     ```  

---

## **Fast Coding Challenge**  
8. **GET `/get_fast_coding_question`**  
   - **Description:** Returns a short coding question with test cases and function signature.  

9. **POST `/submit_fast_coding_solution`**  
   - **Description:** Runs the function against test cases and returns pass/fail results.  
   - **Request Body:**  
     ```json
     {
       "user_code": "Your function implementation"
     }
     ```  
---
# Tech Stack
# - FastAPI (Backend API framework)
# - Vertex AI (Google Cloud AI Model)
# - React.js (Frontend framework)
# - Tailwind CSS (Styling)
# - Framer (UI animations)
# - Python (Backend programming language)
# - openai (used in trivia)

---


## Error Handling
The API returns appropriate error messages in case of invalid requests.

### Example Error Response
```json
{
    "detail": "Invalid input provided. Please check your request."
}
```

---

## Future Enhancements
- Add authentication for user-specific data.
- Implement rate limiting.
- Expand the AI explanations with more details.

---

For questions or issues, contact our development team. 🚀
