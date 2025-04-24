# MockAI - AI-Powered Job Interview Simulator

## Overview

MockAI is an AI-driven job interview simulator that customizes interview questions based on user resumes and job descriptions. The platform evaluates body language, speech, and overall performance, providing feedback for improvement. The system uses advanced AI tools like OpenAI GPT-4, MediaPipe, and pyttsx3 to simulate real-world job interviews.

## Features

- **Resume-Based Question Generation**: Custom interview questions based on resumes and job descriptions.
- **Live AI Video Interview**: Real-time interview simulation using speech recognition.
- **Body Language & Gesture Analysis**: Evaluates facial expressions and movements for confidence assessment.
- **Performance Feedback**: Provides insights on strengths, weaknesses, and areas for improvement.
- **Speech Analysis**: Analyzes tone, clarity, and confidence during the interview.

## Technology Stack

- **Frontend**: React.js
- **Backend**: FastAPI (Python)
- **AI/ML Models**: OpenAI GPT-4 for question generation
- **Video Processing**: MediaPipe (for gesture analysis), pyttsx3 (for speech-to-text and text-to-speech)

## Getting Started

### Prerequisites

1. **Node.js** (for React.js frontend)
2. **Python 3.8+** (for backend and AI integration)
3. **FastAPI**: Install FastAPI by running `pip install fastapi`.
4. **OpenAI API**: You will need an OpenAI API key for question generation.
5. **MediaPipe**: Install MediaPipe via `pip install mediapipe`.
6. **pyttsx3**: Install pyttsx3 via `pip install pyttsx3`.

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/MockAI.git
   cd MockAI
   ```

2. **Frontend Setup**:
   Navigate to the `frontend` directory and install dependencies:

   ```bash
   cd frontend
   npm install
   ```

3. **Backend Setup**:
   Navigate to the `backend` directory and set up your environment:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Running the Application**:

   - Start the frontend server on vite:
     ```bash
     npm run dev
     ```
   - Run the FastAPI backend:
     ```bash
     uvicorn main:app --reload
     ```

   The application should now be running at `http://localhost:5173` for the frontend and `http://localhost:8000` for the backend.

## User Manual

### Step 1: Upload Your Resume

- Navigate to the homepage and click on "Start Interview."
- Upload your resume in the supported format (PDF, DOCX).

### Step 2: Interview Simulation

- Once your resume is uploaded, the platform will generate a set of job-specific interview questions.

### Step 3: Performance Feedback

- After the interview, you will receive detailed feedback on your performance

## About the Developers

- **Jaini Shah**: Frontend Developer
- **Kathan Pathak**: AI/ML and Backend Developer
- **Krutik Doshi**: UI/UX Designer and Documentation Specialist

## Upcoming Updates

- Refining UI/UX based on user feedback.
- Enhancing AI capabilities for more personalized feedback.
- Expanding speech analysis to include tone and cadence in deeper detail.
- Integrating additional AI models for more diverse interview scenarios.

## Acknowledgements

- **Professor Amy Harry**: Project guidance and mentorship.
- **OpenAI**: For providing the GPT-4 API.
- **MediaPipe**: For body language and gesture analysis tools.
- **pyttsx3**: For speech-to-text and text-to-speech functionalities.

---
