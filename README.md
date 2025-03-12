import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

const FastCodingChallenge = () => {
  const [question, setQuestion] = useState("");
  const [functionSignature, setFunctionSignature] = useState("");
  const [testCases, setTestCases] = useState([]);
  const [userCode, setUserCode] = useState("");
  const [timeLeft, setTimeLeft] = useState(60);
  const [challengeStarted, setChallengeStarted] = useState(false);
  const [results, setResults] = useState(null);

  const fetchQuestion = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/get_fast_coding_question");
      const data = await response.json();
      setQuestion(data.question);
      setFunctionSignature(data.function_signature);
      setTestCases(data.test_cases);
      setUserCode(data.function_signature + "\n    # Write your code here");
      setTimeLeft(60);
      setChallengeStarted(true);
    } catch (error) {
      console.error("Error fetching question:", error);
    }
  };

  useEffect(() => {
    if (challengeStarted && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [challengeStarted, timeLeft]);

  const submitSolution = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/submit_fast_coding_solution", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_code: userCode }),
      });
      const data = await response.json();
      setResults(data);
      setChallengeStarted(false);
    } catch (error) {
      console.error("Error submitting solution:", error);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <Button onClick={fetchQuestion}>Start Challenge</Button>
      
      {question && (
        <Card className="w-full max-w-lg p-4">
          <CardContent>
            <h2 className="text-xl font-bold">{question}</h2>
            <p className="text-sm text-gray-500">{functionSignature}</p>
            <p className="mt-2 text-red-500">Time left: {timeLeft}s</p>
            <Textarea
              value={userCode}
              onChange={(e) => setUserCode(e.target.value)}
              className="w-full h-40 mt-2"
            />
            <Button className="mt-4" onClick={submitSolution} disabled={timeLeft <= 0}>
              Submit Code
            </Button>
          </CardContent>
        </Card>
      )}

      {results && (
        <Card className="w-full max-w-lg p-4">
          <CardContent>
            <h3 className="text-lg font-bold">Results</h3>
            <pre className="text-sm bg-gray-100 p-2 rounded">{JSON.stringify(results, null, 2)}</pre>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default FastCodingChallenge;
