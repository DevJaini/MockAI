import React, { useState, useRef } from "react";
import axios from "axios";

const AudioRecorder = ({ currentQuestion }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      setAudioBlob(blob);
      chunksRef.current = [];
    };

    mediaRecorderRef.current = recorder;
    recorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendForEvaluation = async () => {
    if (!audioBlob || !currentQuestion) return alert("Record first!");

    const formData = new FormData();
    formData.append("file", audioBlob, "answer.webm");
    formData.append("question", currentQuestion);

    try {
      const res = await axios.post(
        "http://localhost:8000/submit-answer",
        formData
      );
      setEvaluation(res.data);
    } catch (err) {
      console.error("Evaluation failed", err);
    }
  };

  return (
    <div className="mt-4 text-white text-left space-y-4">
      <div className="flex gap-3">
        <button
          onClick={startRecording}
          disabled={isRecording}
          className="px-4 py-2 bg-green-600 rounded-md"
        >
          🎙 Start Recording
        </button>
        <button
          onClick={stopRecording}
          disabled={!isRecording}
          className="px-4 py-2 bg-yellow-500 rounded-md"
        >
          ⏹ Stop
        </button>
        <button
          onClick={sendForEvaluation}
          disabled={!audioBlob}
          className="px-4 py-2 bg-blue-500 rounded-md"
        >
          🚀 Evaluate
        </button>
      </div>

      {evaluation && (
        <div className="mt-4 bg-white bg-opacity-10 p-4 rounded-lg shadow-lg">
          <h3 className="text-xl font-bold mb-2">📝 Evaluation</h3>
          <p>
            <strong>Clarity:</strong> {evaluation.clarity_score}/10
          </p>
          <p>
            <strong>Technical:</strong> {evaluation.technical_score}/10
          </p>
          <p>
            <strong>Structure:</strong> {evaluation.structure_score}/10
          </p>
          <p>
            <strong>Face Confidence:</strong> {evaluation.face_confidence}/10
          </p>
          <p>
            <strong>Final Score:</strong> {evaluation.final_score}/10
          </p>

          {evaluation?.mispronounced_words?.length > 0 && (
            <div className="mt-4 text-red-400">
              <h4 className="font-bold mb-1">🗣 Mispronounced Words:</h4>
              <ul className="list-disc list-inside">
                {evaluation.mispronounced_words.map((w, i) => (
                  <li key={i}>
                    <span className="font-semibold">{w.word}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="mt-2">
            <strong>Feedback:</strong>
            {evaluation.feedback.gpt}
          </div>
        </div>
      )}
    </div>
  );
};

export default AudioRecorder;
