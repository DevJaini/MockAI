import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Section from "../components/Section";

const Interview = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [isCameraOn, setIsCameraOn] = useState(false);
  const [timer, setTimer] = useState(() => {
    const saved = localStorage.getItem("interview-timer");
    return saved ? parseInt(saved, 10) : 1800;
  });
  const [currentQuestion, setCurrentQuestion] = useState("");
  const [audioUrl, setAudioUrl] = useState(null);
  const [isInterviewStarted, setIsInterviewStarted] = useState(
    () => localStorage.getItem("interview-started") === "true"
  );
  const [questionIndex, setQuestionIndex] = useState(() => {
    const saved = localStorage.getItem("interview-question-index");
    return saved ? parseInt(saved, 10) : 0;
  });
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);
  const [attemptedQuestions, setAttemptedQuestions] = useState(() => {
    const saved = localStorage.getItem("interview-attempted");
    return saved ? parseInt(saved, 10) : 0;
  });
  const [totalQuestions, setTotalQuestions] = useState(8);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const [user, setUser] = useState(null);

  // 🔁 Get user info from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // 📷 Start camera
  const startCamera = async () => {
    try {
      // Stop any previous stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      // For Safari and older browsers: ensure play
      const playPromise = videoRef.current.play();
      if (playPromise !== undefined) {
        playPromise.catch((e) => console.warn("Auto-play was prevented:", e));
      }

      streamRef.current = stream;
      setIsCameraOn(true);
    } catch (error) {
      console.error("Error accessing media devices.", error);
    }
  };

  // 🛑 Stop camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
  };

  useEffect(() => {
    if (isInterviewStarted && timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => {
          const updated = prev - 1;
          localStorage.setItem("interview-timer", updated);
          return updated;
        });
      }, 1000);
      return () => clearInterval(interval);
    } else if (timer === 0) {
      handleGenerateResult(true);
    }

    if (location.pathname !== "/interview") {
      stopCamera();
    }
  }, [isInterviewStarted, timer, location]);

  const fetchNextQuestion = async () => {
    try {
      setIsLoadingQuestion(true);
      const res = await fetch("http://localhost:8000/play-question");
      const data = await res.json();

      if (data.audio_url) {
        console.log("🎧 Playing:", data.audio_url);
        setCurrentQuestion(data.question_text);
        setAudioUrl(data.audio_url);
        setAttemptedQuestions((prev) => {
          const updated = prev + 1;
          localStorage.setItem("interview-attempted", updated);
          return updated;
        });
      } else {
        alert(data.message || "No more questions.");
      }
    } catch (err) {
      console.error("❌ Failed to fetch question:", err);
      alert("Failed to load question.");
    } finally {
      setIsLoadingQuestion(false);
    }
  };

  // ▶️ Start interview
  const handleStartInterview = async () => {
    setIsInterviewStarted(true);

    // setTimer(600); // 10 mins
    setQuestionIndex(1);
    localStorage.setItem("interview-started", "true");
    localStorage.setItem("interview-question-index", questionIndex);
    await fetchNextQuestion(); // play question 1
  };

  // ⏭ Next question
  const handleNextQuestion = async () => {
    if (questionIndex + 1 < totalQuestions) {
      const nextIndex = questionIndex + 1;
      setQuestionIndex(nextIndex);
      localStorage.setItem("interview-question-index", nextIndex);
      await fetchNextQuestion();
    }
  };

  const handleGenerateResult = (timeout = false) => {
    stopCamera();
    localStorage.clear();
    if (timeout) alert("⏰ 30 minutes is over. Showing evaluation so far.");
    navigate("/results");
  };

  const handleEndInterview = () => {
    stopCamera();
    localStorage.clear();
    alert("Interview Ended! Showing attempted questions evaluation.");
    navigate("/results");
  };

  const toggleRecording = async () => {
    if (isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    } else {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        chunksRef.current = [];
        const formData = new FormData();
        formData.append("file", blob, "answer.webm");
        formData.append("question", currentQuestion);

        try {
          const res = await fetch("http://localhost:8000/submit-answer", {
            method: "POST",
            body: formData,
          });
          const result = await res.json();
          console.log("✅ Evaluation Result:", result);
        } catch (err) {
          console.error("❌ Evaluation error:", err);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    }
  };

  return (
    <Section className="relative min-h-screen flex flex-col items-center justify-center p-4 text-center">
      <div className="relative z-10 bg-opacity-10 backdrop-blur-lg shadow-xl rounded-xl p-4 w-full h-full flex flex-col items-center justify-center">
        <h2 className="text-4xl font-extrabold text-white mb-2">Interview</h2>

        <div className="flex flex-col items-center">
          {/* Video Feed */}
          <div
            className="flex flex-col items-center justify-center text-white text-xl rounded-lg shadow-lg mb-2 
             w-full max-w-screen-lg h-auto md:h-[500px] lg:h-[600px] xl:h-[700px]"
            style={{ height: "850px", width: "1800px", objectFit: "cover" }}
          >
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className={`w-full rounded-lg shadow-lg ${
                !isCameraOn ? "hidden" : ""
              }`}
              style={{
                height: "100%",
                objectFit: "contain",
                transform: "scaleX(-1)",
              }}
            />

            {!isCameraOn && (
              <>
                <p className="mb-2">Waiting for camera...</p>
                {user ? <p>{user.username}</p> : <p>Loading user...</p>}
              </>
            )}
          </div>

          {/* Interview Panel */}
          <div className="flex flex-col items-center w-full max-w-lg">
            <div className="text-xl text-white mb-2">
              {isInterviewStarted ? (
                <>
                  <div className="text-xl text-white mb-4">
                    Time Remaining: {Math.floor(timer / 60)}:
                    {String(timer % 60).padStart(2, "0")}
                  </div>
                  <div className="text-white mt-4 mb-2">
                    {isLoadingQuestion ? (
                      "Loading question..."
                    ) : audioUrl ? (
                      <div>
                        <p className="mb-2 font-semibold">
                          Question: {currentQuestion}
                        </p>
                        <audio src={audioUrl} autoPlay hidden />

                        <button
                          onClick={toggleRecording}
                          className={`mt-3 px-4 py-2 font-semibold rounded-md ${
                            isRecording
                              ? "bg-red-600 text-white"
                              : "bg-green-600 text-white"
                          }`}
                        >
                          {isRecording
                            ? "⏹ Stop Recording"
                            : "🎙 Start Recording"}
                        </button>
                      </div>
                    ) : (
                      "Waiting for question..."
                    )}
                  </div>
                </>
              ) : (
                <div className="text-xl text-white mb-2">
                  Start your interview
                </div>
              )}
            </div>

            {/* Buttons */}
            <div className="flex gap-4 flex-wrap justify-center">
              {!isCameraOn && (
                <button
                  onClick={startCamera}
                  className="px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition"
                >
                  Turn on Camera
                </button>
              )}

              {isCameraOn && !isInterviewStarted && (
                <button
                  onClick={handleStartInterview}
                  className="px-6 py-3 bg-green-500 text-white font-bold rounded-lg shadow-md hover:bg-green-600 transition"
                >
                  Start Interview
                </button>
              )}

              {isCameraOn && isInterviewStarted && (
                <>
                  {questionIndex + 1 < totalQuestions ? (
                    <button
                      onClick={handleNextQuestion}
                      className="px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition"
                    >
                      Next Question
                    </button>
                  ) : (
                    <button
                      onClick={() => handleGenerateResult(false)}
                      className="px-6 py-3 bg-yellow-500 text-white font-bold rounded-lg shadow-md hover:bg-yellow-600 transition"
                    >
                      Generate Evaluation
                    </button>
                  )}

                  <button
                    onClick={handleEndInterview}
                    className="px-6 py-3 bg-red-500 text-white font-bold rounded-lg shadow-md hover:bg-red-600 transition"
                  >
                    End Interview
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </Section>
  );
};

export default Interview;
