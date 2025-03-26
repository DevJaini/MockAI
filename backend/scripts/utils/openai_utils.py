import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.Client(api_key=os.getenv("OPEN_API_KEY"))

def generate_questions(resume, jd, keywords):
    try:
        prompt = f"""
        You are an expert job interviewer AI. Based on this resume and job description, and these important keywords: {keywords}, generate 15 technical and behavioral interview questions from medium to advanced (technical + behavioral). Format:
        1. [Question]
        2. [Question]
        ...
        15. [Question]
         
        Resume: {resume}
        Job Description: {jd}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You're an expert AI interviewer."},
                {"role": "user", "content": prompt}
            ]
        )

        raw_lines = response.choices[0].message.content.split("\n")

            # 🔥 Remove blank lines + strip each line
        cleaned_questions = [line.strip() for line in raw_lines if line.strip()]

        return cleaned_questions

    except Exception as e:
        print("❌ OpenAI Error:", e)
        raise e  # or raise HTTPException(...) from here

def evaluate_answer(answer_text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an interview coach evaluating responses."},
            {"role": "user", "content": f"Evaluate this answer and give feedback on tone, content, fluency: {answer_text}"}
        ]
    )
    return response.choices[0].message.content

