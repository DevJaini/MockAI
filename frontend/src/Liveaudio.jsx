import React, { useState, useRef } from "react";
import axios from "axios";

const RecordAudio = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [transcription, setTranscription] = useState("");
    const [evaluation, setEvaluation] = useState(null);
    const [finalScore, setFinalScore] = useState(null);
    const [question, setQuestion] = useState("Tell me about a project where you used Python."); // Placeholder
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
                setAudioBlob(audioBlob);
                audioChunksRef.current = [];
            };

            mediaRecorderRef.current = mediaRecorder;
            mediaRecorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const uploadAudio = async () => {
        if (!audioBlob) {
            alert("No audio recorded!");
            return;
        }

        const formData = new FormData();
        formData.append("file", audioBlob, "recording.webm");

        try {
            const response = await axios.post("http://127.0.0.1:8000/upload-audio", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setTranscription(response.data.transcription);
        } catch (error) {
            console.error("Error uploading audio:", error);
        }
    };

    const evaluateAudio = async () => {
        if (!audioBlob || !question) {
            alert("Missing audio or question.");
            return;
        }

        const formData = new FormData();
        formData.append("file", audioBlob, "recording.webm");
        formData.append("question", question);

        try {
            const response = await axios.post("http://127.0.0.1:8000/evaluate-response", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setEvaluation(response.data);
        } catch (error) {
            console.error("Error evaluating audio:", error);
        }
    };

    const getFinalEvaluation = async () => {
        if (!audioBlob || !question) {
            alert("Missing audio or question.");
            return;
        }

        const formData = new FormData();
        formData.append("file", audioBlob, "recording.webm");
        formData.append("question", question);

        try {
            const response = await axios.post("http://127.0.0.1:8000/final-evaluation", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setFinalScore(response.data);
        } catch (error) {
            console.error("Error fetching final score:", error);
        }
    };

    return (
        <div>
            <h2>Audio Recorder</h2>
            <button onClick={startRecording} disabled={isRecording}>Start Recording</button>
            <button onClick={stopRecording} disabled={!isRecording}>Stop Recording</button>
            <button onClick={uploadAudio} disabled={!audioBlob}>Upload & Transcribe</button>
            <button onClick={evaluateAudio} disabled={!audioBlob}>Evaluate Answer</button>
            <button onClick={getFinalEvaluation} disabled={!audioBlob}>Final Evaluation Score</button>



            {transcription && (
                <div>
                    <h3>Transcription:</h3>
                    <p>{transcription}</p>
                </div>
            )}

            {evaluation && (
                <div style={{ marginTop: "20px", padding: "10px", backgroundColor: "#f9f9f9", borderRadius: "8px" }}>
                    <h3>Ensemble Evaluation Summary:</h3>
                    <p><strong>Final Score:</strong> {evaluation.final_score}</p>
                    <p><strong>ChatGPT Score:</strong> {evaluation.gpt_score}</p>
                    <p><strong>Claude Score:</strong> {evaluation.claude_score}</p>

                    <h4>ChatGPT Feedback:</h4>
                    <p>{evaluation.gpt_feedback}</p>

                    <h4>Claude Feedback:</h4>
                    <p>{evaluation.claude_feedback}</p>

                    <h4>Combined Feedback:</h4>
                    <p>{evaluation.combined_feedback}</p>
                </div>
            )}


            {finalScore && (
                <div>
                    <h3> Final Evaluation Breakdown</h3>
                    <p><strong>Face Confidence (avg):</strong> {finalScore.face_avg}</p>
                    <p><strong>Answer Score:</strong> {finalScore.answer_score}</p>
                    <p><strong>Clarity Score:</strong> {finalScore.clarity_score}</p>
                    <p><strong>Pronunciation Score:</strong> {finalScore.pronunciation_score}</p>
                    <p><strong>Final Score:</strong> {finalScore.final_score}</p>

                    <h4>AI Feedback:</h4>
                    <ul>
                        {Object.entries(finalScore.feedback).map(([key, value]) => (
                            <li key={key}><strong>{key}:</strong> {value}</li>
                        ))}
                    </ul>
                </div>
            )}

        </div>
    );
};

export default RecordAudio;
