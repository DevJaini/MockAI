import { useNavigate } from "react-router-dom";
import Section from "../components/Section";
import { Rings } from "../components/design/Hero";
import { heroBackground } from "../assets";
import { Bar } from "react-chartjs-2"; // Importing Chart.js for Bar Chart
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Results = () => {
  const navigate = useNavigate();

  const handleBackToUpload = () => {
    navigate("/resumeuploader"); // Navigate back to the resume upload page
  };

  // Data for the bar chart
  const data = {
    labels: [
      "Technical Skills",
      "Communication Skills",
      "Problem-Solving",
      "Overall Impression",
    ],
    datasets: [
      {
        label: "Score",
        data: [8, 7, 9, 8], // Example scores for the categories
        backgroundColor: ["#4caf50", "#ffeb3b", "#2196f3", "#9c27b0"],
        borderColor: ["#4caf50", "#ffeb3b", "#2196f3", "#9c27b0"],
        borderWidth: 1,
        color: "white",
      },
    ],
  };

  // Options for the bar chart
  const options = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: "Interview Evaluation Scores",
        font: { size: 20 },
        color: "white",
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        ticks: {
          stepSize: 1,
          color: "white",
        },
      },
      x: {
        ticks: {
          color: "white", // X-axis ticks color set to white
        },
      },
    },
    aspectRatio: 2, // Controls the aspect ratio of the chart
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
            src={heroBackground} // You can change this to the desired background
            alt="hero background"
            className="w-full object-cover blur-lg"
            width={1440}
            height={1800}
          />
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 bg-white bg-opacity-10 backdrop-blur-lg shadow-xl rounded-xl p-8 max-w-auto w-full">
        <h2 className="text-5xl font-extrabold text-white mb-12">
          Interview Evaluation Results
        </h2>

        {/* Score Breakdown and Detailed Feedback */}
        <div className="flex flex-wrap gap-6 mb-6">
          {/* Score Breakdown */}
          <div className="flex-1">
            <h3 className="text-3xl font-semibold text-white mb-4">
              Score Breakdown
            </h3>
            <div className="mb-6 w-full h-[300px]">
              {" "}
              {/* Chart container */}
              <Bar data={data} options={options} />
            </div>
          </div>

          {/* Detailed Feedback */}
          <div className="flex-1">
            <h3 className="text-3xl font-semibold text-white mb-36">
              Detailed Feedback
            </h3>
            <div className="space-y-6">
              <div className="flex justify-between">
                <span className="font-bold">Voice Tone:</span>
                <div className="w-1/2 bg-gray-300 rounded-full h-4 overflow-hidden">
                  <div className="bg-green-600 h-4 w-[70%]" />
                </div>
                <span className="text-green-600">7/10</span>
              </div>

              <div className="flex justify-between">
                <span className="font-bold">Confidence Level:</span>
                <div className="w-1/2 bg-gray-300 rounded-full h-4 overflow-hidden">
                  <div className="bg-yellow-600 h-4 w-[60%]" />
                </div>
                <span className="text-yellow-600">6/10</span>
              </div>

              <div className="flex justify-between">
                <span className="font-bold">Clarity of Speech:</span>
                <div className="w-1/2 bg-gray-300 rounded-full h-4 overflow-hidden">
                  <div className="bg-orange-600 h-4 w-[80%]" />
                </div>
                <span className="text-orange-600">8/10</span>
              </div>

              <div className="flex justify-between">
                <span className="font-bold">Engagement Level:</span>
                <div className="w-1/2 bg-gray-300 rounded-full h-4 overflow-hidden">
                  <div className="bg-red-600 h-4 w-[50%]" />
                </div>
                <span className="text-red-600">5/10</span>
              </div>
            </div>
          </div>
        </div>

        {/* Improvement Tips, Detailed Report, and Positive Aspects Sections */}
        <div className="text-left text-white mb-6">
          <h3 className="text-3xl font-semibold mb-4">Improvement Tips</h3>
          <ul className="list-disc pl-6 space-y-2">
            <li>
              Work on reducing monotone voice. Try varying tone based on
              context.
            </li>
            <li>
              Increase engagement by making eye contact and showing enthusiasm.
            </li>
            <li>
              Spend more time organizing your thoughts before answering system
              design questions.
            </li>
          </ul>
        </div>

        <div className="text-left text-white mb-6">
          <h3 className="text-3xl font-semibold mb-4">Detailed Report</h3>
          <p className="font-semibold text-lg">Mistakes Made:</p>
          <ul className="list-decimal pl-8 space-y-3 text-lg">
            <li>
              <span className="font-bold">Minute 5:</span> Incorrect explanation
              of the algorithm -{" "}
              <span className="text-red-600">
                Need to review sorting algorithms.
              </span>
            </li>
            <li>
              <span className="font-bold">Minute 12:</span> Rushed answer to the
              question on system design -{" "}
              <span className="text-yellow-600">
                Take more time to organize thoughts.
              </span>
            </li>
            <li>
              <span className="font-bold">Minute 20:</span> Misunderstood
              question on testing frameworks -{" "}
              <span className="text-red-600">
                Clarify the question before answering.
              </span>
            </li>
          </ul>
        </div>

        <div className="text-left text-white mb-6">
          <h3 className="text-3xl font-semibold mb-4">Positive Aspects</h3>
          <ul className="list-decimal pl-8 space-y-3 text-lg">
            <li>
              <span className="font-bold">Minute 10:</span> Clear understanding
              of the technical challenge -{" "}
              <span className="text-green-600">Keep up the good work.</span>
            </li>
            <li>
              <span className="font-bold">Minute 18:</span> Well-organized
              answer to the question on system architecture -{" "}
              <span className="text-green-600">
                Excellent explanation of architecture.
              </span>
            </li>
            <li>
              <span className="font-bold">Minute 22:</span> Confident handling
              of a problem-solving question -{" "}
              <span className="text-green-600">Great performance!</span>
            </li>
          </ul>
        </div>

        {/* Button to navigate back to the upload page */}
        <div className="mt-8 text-center">
          <button
            onClick={handleBackToUpload}
            className="px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105"
          >
            Back to Upload Page
          </button>
        </div>
      </div>

      <Rings />
    </Section>
  );
};

export default Results;
