import pdfplumber
from docx import Document
import pyttsx3
import os
import pathlib
from dotenv import load_dotenv
import openai

tts_engine = pyttsx3.init()
load_dotenv()


# def read_docx(file_path):
#     doc = Document(file_path)
#     text = "\n".join([para.text for para in doc.paragraphs])
#     return text


# print(read_docx("sample.docx"))

# defining current directory
thisdir = pathlib.Path(__file__).parent.absolute()
client = openai.Client(api_key=os.getenv("OPENAPI_KEY"))


def generate_interview_questions(resume_text, job_description):
    prompt = f"""
    You are an AI job interview coach. Generate 5 technical and behavioral interview questions 
    based on the following resume and job description:

    Resume: {resume_text}

    Job Description: {job_description}

    Format your response as:
    1. [Question]
    2. [Question]
    3. [Question]
    4. [Question]
    5. [Question]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an expert interview coach."},
                  {"role": "user", "content": prompt}]
    )
    print(response.choices[0].message.content.split("\n"))
    return response.choices[0].message.content.split("\n")


def read_pdf_tables(file_path):
    print(client)
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:  # Ensure there is text before speaking
                text += page_text + "\n"
                ques = generate_interview_questions(
                    page_text, "Software Engineer")
                # tts_engine.say(page_text)  # Queue the text to be spoken

    # tts_engine.runAndWait()  # Process the queued text-to-speech commands
    return ques


# Call the function
read_pdf_tables("/Users/kp/capstone/backend/My current resume.pdf")
