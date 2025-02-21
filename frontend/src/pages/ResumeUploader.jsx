import { useState } from "react";
import { heroBackground } from "../assets";
import Section from "../components/Section";
import { Rings } from "../components/design/Hero";
import { useNavigate } from "react-router-dom";

const ResumeUploader = () => {
  const navigate = useNavigate();

  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");

  const handleResumeChange = (e) => {
    setResume(e.target.files[0]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Resume file:", resume);
    console.log("Job Description:", jobDescription);
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
            className="w-full px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105"
          >
            Start Your Interview! Be Ready!
          </button>
        </form>
      </div>
      <Rings />
    </Section>
  );
};

export default ResumeUploader;
