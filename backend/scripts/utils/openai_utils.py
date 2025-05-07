import os
import re
import json
from dotenv import load_dotenv
from anthropic import Anthropic
import openai

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI and Claude clients using API keys
client_openai = openai.Client(api_key=os.getenv("OPEN_API_KEY"))
client_claude = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def generate_questions(resume, jd, keywords, num_questions=2):
    """
    Generates a list of interview questions based on resume, job description, and keywords.
    Uses OpenAI's GPT model to produce output in clean numbered format.
    """
    try:
        # Compose prompt for question generation
        prompt = f"""
You are an expert job interviewer AI. Based on the following resume, job description, and keywords, generate {num_questions} technical and behavioral interview questions (easy to medium level). 
Return only questions in numbered format. Do NOT include labels like 'Technical Question:' or use markdown.

Resume: {resume}
Job Description: {jd}
Keywords: {keywords}
        """

        # Send request to OpenAI chat model
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're an expert interviewer AI."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse text line-by-line, cleaning any formatting
        raw_lines = [line.strip() for line in response.choices[0].message.content.split("\n") if line.strip()]
        cleaned_questions = []

        for line in raw_lines:
            line = re.sub(r"^\d+\.\s*", "", line)  # Remove leading number (e.g., "1. ")
            line = re.sub(r"\*\*(.*?)\*\*[:：]?", "", line)  # Remove bold/label formats
            line = re.sub(r"^[:：\s]+", "", line)  # Clean extra colons or spaces
            if line:
                cleaned_questions.append(line)

        return cleaned_questions

    except Exception as e:
        print("OpenAI Error in generate_questions:", e)
        return []  # Fail silently with empty list if model fails

def evaluate_with_chatgpt(question: str, answer: str):
    """
    Evaluates the quality of an answer based on clarity, technical depth, and structure using OpenAI GPT.
    Expects structured JSON output.
    """
    prompt = f"""
You are an AI interview evaluator. Rate the following answer on:
- Clarity (1–10)
- Technical Depth (1–10)
- Structure (1–10)

Then give concise feedback.

Respond ONLY in valid JSON format:
{{
  "clarity": <1-10>,
  "technical_depth": <1-10>,
  "structure": <1-10>,
  "feedback": "<Your feedback here>"
}}

Question: {question}
Answer: {answer}
    """

    try:
        # Query GPT for evaluation
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're an AI interview evaluator."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        # Strip Markdown formatting if present (e.g., ```json)
        if content.startswith("```"):
            content = re.sub(r"^```(json)?", "", content).strip("`").strip()

        return json.loads(content)

    except Exception as e:
        print("GPT Evaluation Error:", e)
        return {
            "clarity": 0,
            "technical_depth": 0,
            "structure": 0,
            "feedback": str(e)
        }

def evaluate_with_claude(question: str, answer: str):
    """
    Evaluates the same answer using Claude AI for a second opinion.
    Also expects structured JSON output.
    """
    prompt = f"""
Evaluate the following interview response.

Return JSON only:
{{
  "clarity": <1-10>,
  "technical_depth": <1-10>,
  "structure": <1-10>,
  "feedback": "<feedback>"
}}

Question: {question}
Answer: {answer}
    """

    try:
        # Claude API call
        response = client_claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        output = response.content[0].text.strip()

        # Handle markdown if present
        if output.startswith("```"):
            output = re.sub(r"^```(json)?", "", output).strip("`").strip()

        return json.loads(output)

    except Exception as e:
        print("Claude Evaluation Error:", e)
        return {
            "clarity": 0,
            "technical_depth": 0,
            "structure": 0,
            "feedback": str(e)
        }

def summarize_feedback_with_gpt(gpt_feedbacks, claude_feedbacks):
    """
    Generates an overall summary of feedback using both GPT and Claude feedback responses.
    Output is a natural-language paragraph summarizing candidate performance.
    """
    prompt = f"""
You are an expert interview coach.

Below is a list of feedbacks generated from multiple interview answers.

GPT Feedbacks:
{json.dumps(gpt_feedbacks, indent=2)}

Claude Feedbacks:
{json.dumps(claude_feedbacks, indent=2)}

Now summarize the candidate's overall performance, key strengths, and areas for improvement.
Respond in a short, professional paragraph. Do not mention GPT or Claude.
    """

    try:
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful interview evaluator."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("GPT Summary Error:", e)
        return "Unable to generate summary due to an error."
