import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Section from "../components/Section";

const Interview = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const [isCameraOn, setIsCameraOn] = useState(false);
  const [timer, setTimer] = useState(0);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);
  const [user, setUser] = useState(null);

  const [audioUrl, setAudioUrl] = useState(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(false);

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
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
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

  // 💡 Stop camera when leaving route
  useEffect(() => {
    if (location.pathname !== "/interview") {
      stopCamera();
    }
  }, [location]);

  // ⏲ Interview timer
  useEffect(() => {
    let interval;
    if (timer > 0) {
      interval = setInterval(() => setTimer((prev) => prev - 1), 1000);
    }
    return () => clearInterval(interval);
  }, [timer]);

  // 🚀 Fetch next question from backend
  const fetchNextQuestion = async () => {
    try {
      setIsLoadingQuestion(true);
      const res = await fetch("http://localhost:8000/play-question");
      const data = await res.json();

      if (data.audio_url) {
        console.log("🎧 Playing:", data.audio_url);
        setAudioUrl(data.audio_url);
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
    setTimer(600); // 10 mins
    setQuestionIndex(0);
    await fetchNextQuestion(); // play question 1
  };

  // ⏭ Next question
  const handleNextQuestion = async () => {
    setQuestionIndex((prev) => prev + 1);
    await fetchNextQuestion();
  };

  const handleGenerateResult = () => {
    stopCamera();
    setTimer(0);
    setIsInterviewStarted(false);
    navigate("/results");
  };

  const handleEndInterview = () => {
    stopCamera();
    setTimer(0);
    setIsInterviewStarted(false);
    alert("Interview Ended!");
    navigate("/");
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
                  <div>
                    Time Remaining: {Math.floor(timer / 60)}:{timer % 60}
                  </div>
                  <div className="text-white mt-4 mb-2">
                    {isLoadingQuestion ? (
                      "Loading question..."
                    ) : audioUrl ? (
                      <audio controls autoPlay src={audioUrl}>
                        <source src={audioUrl} type="audio/mpeg" />
                        Your browser does not support audio.
                      </audio>
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

              {isInterviewStarted && (
                <>
                  <button
                    onClick={handleNextQuestion}
                    className="px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition"
                  >
                    Next Question
                  </button>

                  <button
                    onClick={handleGenerateResult}
                    className="px-6 py-3 bg-yellow-500 text-white font-bold rounded-lg shadow-md hover:bg-yellow-600 transition"
                  >
                    Generate Evaluation
                  </button>

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
