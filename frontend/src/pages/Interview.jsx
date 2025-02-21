import { useState, useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import Section from "../components/Section";
import { Rings } from "../components/design/Hero";

const Interview = () => {
  const navigate = useNavigate();
  const location = useLocation(); // Hook to get current location (route)
  const videoRef = useRef(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [timer, setTimer] = useState(0);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState([
    "Tell me about yourself.",
    "Why do you want to work here?",
    "What are your strengths and weaknesses?",
    "Where do you see yourself in 5 years?",
    "Tell me about a challenge you've faced and how you overcame it.",
  ]);
  const [isInterviewStarted, setIsInterviewStarted] = useState(false);

  // Handle start/stop of the video camera
  const toggleCamera = () => {
    if (isCameraOn) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsCameraOn(true);
    } catch (error) {
      console.error("Error accessing media devices.", error);
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
      setIsCameraOn(false);
    }
  };

  // Listen for route change and turn off camera if not on /interview page
  useEffect(() => {
    if (location.pathname !== "/interview" && isCameraOn) {
      stopCamera();
    }
  }, [location, isCameraOn]);

  // Handle timer for the interview session
  useEffect(() => {
    let interval;
    if (timer > 0) {
      interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [timer]);

  const handleStartInterview = () => {
    setIsInterviewStarted(true);
    setTimer(600); // Start the interview with a 10-minute timer (600 seconds)
  };

  const handleEndInterview = () => {
    stopCamera();
    setTimer(0); // Reset timer
    setIsInterviewStarted(false);
    alert("Interview Ended!");
    navigate("/"); // Redirect to home or another page after interview ends
  };

  const handleNextQuestion = () => {
    if (questionIndex < questions.length - 1) {
      setQuestionIndex(questionIndex + 1);
    } else {
      alert("You've completed all questions.");
      handleEndInterview(); // End interview after last question
    }
  };

  return (
    <Section className="relative min-h-screen flex flex-col items-center justify-center p-6 text-center">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[50%] left-1/2 w-[200%] -translate-x-1/2 md:-top-[40%] md:w-[130%] lg:-top-[80%]">
          <img
            src="your-background-image-url"
            alt="hero background"
            className="w-full object-cover blur-lg"
            width={1440}
            height={1800}
          />
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 bg-white bg-opacity-10 backdrop-blur-lg shadow-xl rounded-xl p-8 w-full h-full flex flex-col items-center justify-center">
        <h2 className="text-4xl font-extrabold text-white mb-6">Interview</h2>

        <div className="flex flex-col items-center">
          {/* Video stream */}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full rounded-lg shadow-lg"
            style={{
              height: "400px",
              objectFit: "cover",
              marginBottom: "20px",
            }}
          />

          <div className="flex flex-col items-center w-full max-w-lg">
            {/* Timer and Interview Controls */}
            <div className="text-xl text-white mb-4">
              {isInterviewStarted ? (
                <>
                  <div>
                    Time Remaining: {Math.floor(timer / 60)}:{timer % 60}
                  </div>
                  <div className="text-white mt-4 mb-6">
                    {questions[questionIndex]}
                  </div>
                </>
              ) : (
                <div className="text-xl text-white mb-4">
                  Start your interview
                </div>
              )}
            </div>

            <div className="flex gap-4">
              {/* Start/Stop Camera Button */}
              {!isCameraOn && (
                <button
                  onClick={toggleCamera}
                  className="w-full px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105 mb-4"
                >
                  Turn on Camera
                </button>
              )}

              {/* Start Interview Button */}
              {!isInterviewStarted && isCameraOn && (
                <button
                  onClick={handleStartInterview}
                  className="w-full px-6 py-3 bg-green-500 text-white font-bold rounded-lg shadow-md hover:bg-green-600 transition transform hover:scale-105 mb-4"
                >
                  Start Interview
                </button>
              )}

              {/* Next Question Button */}
              {isInterviewStarted && questionIndex < questions.length - 1 && (
                <button
                  onClick={handleNextQuestion}
                  className="w-full px-6 py-3 bg-blue-500 text-white font-bold rounded-lg shadow-md hover:bg-blue-600 transition transform hover:scale-105 mb-4"
                >
                  Next Question
                </button>
              )}

              {/* End Interview Button */}
              {isInterviewStarted && (
                <button
                  onClick={handleEndInterview}
                  className="w-full px-6 py-3 bg-red-500 text-white font-bold rounded-lg shadow-md hover:bg-red-600 transition transform hover:scale-105 mb-4"
                >
                  End Interview
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <Rings />
    </Section>
  );
};

export default Interview;
