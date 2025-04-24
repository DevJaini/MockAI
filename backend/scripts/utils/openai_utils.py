import openai
import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
import re

load_dotenv()

client_openai = openai.Client(api_key=os.getenv("OPEN_API_KEY"))
client_claude = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))


def generate_questions(resume, jd, keywords):
    try:
        prompt = f"""
        You are an expert job interviewer AI. Based on this resume and job description, and these important keywords: {keywords}, generate 8 technical and behavioral interview questions from medium to advanced level.

        Format:
        1. [Question]
        2. [Question]
        ...
        8. [Question]

        Resume: {resume}
        Job Description: {jd}
        """

        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're an expert interviewer AI."},
                {"role": "user", "content": prompt}
            ]
        )

        return [line.strip() for line in response.choices[0].message.content.split("\n") if line.strip()]
    
    except Exception as e:
        print("❌ OpenAI Error:", e)
        raise e  # or raise HTTPException(...) from here


def evaluate_with_chatgpt(question: str, answer: str):
    prompt = f"""
        You are an AI interview evaluator. Score the following answer on:
        - Clarity (1–10)
        - Technical Depth (1–10)
        - Structure (1–10)

        Then provide concise feedback.

        Respond ONLY in valid JSON:
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
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're an AI interview evaluator."},
                {"role": "user", "content": prompt}
            ]
        )

        print("📥 GPT response:", response)
        print("📄 Raw:", response.choices[0].message.content)

        content = response.choices[0].message.content.strip()

        # ✅ Remove triple backticks if present
        if content.startswith("```"):
            content = re.sub(r"^```(json)?", "", content)
            content = content.strip("`").strip()

        return json.loads(content)
    except Exception as e:
        print("❌ GPT Evaluation Error:", e)
        return {"clarity": 0, "technical_depth": 0, "structure": 0, "feedback": str(e)}

def evaluate_with_claude(question: str, answer: str):
    prompt = f"""
        Evaluate this interview answer.

        Return JSON:
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
        response = client_claude.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        output = response.content[0].text.strip()

        # ✅ Remove triple backticks if present
        if output.startswith("```"):
            output = re.sub(r"^```(json)?", "", output)
            output = output.strip("`").strip()
            
        return json.loads(output)
    except Exception as e:
        print("❌ Claude Evaluation Error:", e)
        return {"clarity": 0, "technical_depth": 0, "structure": 0, "feedback": str(e)}
    
def summarize_feedback_with_gpt(gpt_feedbacks, claude_feedbacks):
    combined_prompt = f"""
    You are an expert interview coach.

    Below is a list of feedbacks generated from GPT and Claude for 8 interview questions.

    GPT Feedbacks:
    {json.dumps(gpt_feedbacks, indent=2)}

    Claude Feedbacks:
    {json.dumps(claude_feedbacks, indent=2)}

    Now please summarize the candidate's overall performance, key strengths, and improvement areas based on both models. Output should be 1 paragraph of final overall feedback.
    Dont mention AI name in response.
    """

    try:
        response = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful interview evaluator."},
                {"role": "user", "content": combined_prompt}
            ]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ GPT Summary Error:", e)
        return "Unable to generate summary due to an error."

