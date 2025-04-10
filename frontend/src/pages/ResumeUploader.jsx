import { useState } from "react";
import { heroBackground } from "../assets";
import Section from "../components/Section";
import { Rings } from "../components/design/Hero";
import { useNavigate } from "react-router-dom";

const ResumeUploader = () => {
  const navigate = useNavigate();

  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false); // Track upload status

  const handleResumeChange = (e) => {
    setResume(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!resume || !jobDescription) {
      alert("Please upload a resume and enter job description.");
      return;
    }

    setIsAnalyzing(true);
    setIsUploaded(false);

    const formData = new FormData();
    formData.append("file", resume);
    formData.append("job_description", jobDescription);

    try {
      const response = await fetch("http://localhost:8000/upload-resume", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        console.error("❌ Backend error:", data);
        alert(data.detail || "Something went wrong.");
        setIsAnalyzing(false);
        return;
      }

      console.log("✅ Upload success:", data);
      setIsUploaded(true); // Show "Start Interview" button
    } catch (error) {
      console.error("❌ Upload failed:", error);
      alert("Server error. Please try again.");
      setIsAnalyzing(false);
    }
  };

  const handleStartInterview = () => {
    navigate("/interview");
  };

  return (
    <Section className="relative min-h-screen flex flex-col items-center justify-center p-6 text-center">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute -top-[50%] left-1/2 w-[200%] -translate-x-1/2 
                        md:-top-[40%] md:w-[130%] lg:-top-[80%]"
        >
          <img
            src={heroBackground}
            alt="hero background"
            className="w-full object-cover blur-lg"
            width={1440}
            height={1800}
          />
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 bg-white bg-opacity-10 backdrop-blur-lg shadow-xl rounded-xl p-8 max-w-lg w-full">
        <h2 className="text-4xl font-extrabold text-white mb-6">
          Upload Your Resume
        </h2>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="text-left">
            <label className="block text-white font-semibold mb-1">
              Resume:
            </label>
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleResumeChange}
              className="w-full p-3 border border-gray-300 rounded-lg shadow-sm text-white"
              required
            />
          </div>

          <div className="text-left">
            <label className="block text-white font-semibold mb-1">
              Job Description:
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows="4"
              className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
              placeholder="Enter the job description..."
              required
            />
          </div>

          <button
            type="submit"
            disabled={isAnalyzing}
            className={`w-full px-6 py-3 font-bold rounded-lg shadow-md transition transform ${
              isAnalyzing
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-purple-500 text-white hover:bg-purple-600 hover:scale-105"
            }`}
          >
            {isAnalyzing ? "Analyzing Resume..." : "Submit Resume"}
          </button>
        </form>
      </div>

      {/* Instruction Modal */}
      {(isAnalyzing || isUploaded) && (
        <div className="fixed inset-0 bg-opacity-70 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-10 w-[90%] max-w-xl text-left animate-fadeIn">
            <h3 className="text-3xl font-bold text-purple-700 mb-6">
              Interview Instructions
            </h3>
            <ul className="list-disc list-inside text-gray-800 space-y-3 text-lg">
              <li>
                You will be asked <strong>8 interview questions</strong>.
              </li>
              <li>
                Total interview time is <strong>30 minutes</strong>.
              </li>
              <li>
                After each question is spoken, click{" "}
                <strong>"Start Recording"</strong> to record your answer.
              </li>
              <li>
                Click <strong>"Stop Recording"</strong> to stop and
                automatically submit your response.
              </li>
              <li>
                You can click <strong>"Next Question"</strong> after recording
                each answer to proceed.
              </li>
              <li>All answers will be recorded for analysis.</li>
              <li>
                You may end the interview early, but evaluation will be based
                only on attempted answers.
              </li>
              <li>
                Keep your face centered and speak clearly for best results.
              </li>
              <li>
                Make sure your camera and microphone are working properly.
              </li>
            </ul>

            <p className="mt-6 font-bold text-red-800">
              ⚠️ It is mandatory to record an answer for each question.
              Unrecorded responses will not be evaluated.
            </p>
            <p className="mt-8 text-sm text-gray-600">
              Don’t worry — this is for practice and growth. Just do your best!
              😊
            </p>

            <div className="mt-8 flex justify-end">
              {isUploaded ? (
                <button
                  onClick={handleStartInterview}
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition"
                >
                  Start Your Interview
                </button>
              ) : (
                <button
                  disabled
                  className="px-6 py-3 bg-gray-400 text-white rounded-lg font-semibold cursor-not-allowed"
                >
                  Analyzing Resume...
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      <Rings />
    </Section>
  );
};

export default ResumeUploader;
