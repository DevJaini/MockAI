import React, { useEffect, useState } from "react";
import Section from "../components/Section";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Results = () => {
  const [report, setReport] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const res = await fetch("http://localhost:8000/interview-report");
        const data = await res.json();
        setReport(data);
      } catch (err) {
        console.error("Error fetching report:", err);
      }
    };

    fetchReport();
  }, []);

  if (!report)
    return <div className="text-white p-8">Loading evaluation...</div>;
  if (report.message)
    return <div className="text-white p-8">{report.message}</div>;

  const feedback = report.feedback;
  const data = {
    labels: [
      "Clarity",
      "Technical",
      "Structure",
      "Pronunciation",
      "Face Confidence",
    ],
    datasets: [
      {
        label: "Score",
        data: [
          feedback?.clarity_score || 0,
          feedback?.technical_score || 0,
          feedback?.structure_score || 0,
          feedback?.pronunciation_score || 0,
          report.face_confidence || 0,
        ],
        backgroundColor: [
          "#4caf50",
          "#2196f3",
          "#ff9800",
          "#9c27b0",
          "#e91e63",
        ],
      },
    ],
  };

  const options = {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        max: 10,
        ticks: { stepSize: 1, color: "white" },
      },
      x: {
        ticks: { color: "white" },
      },
    },
    plugins: {
      legend: { labels: { color: "white" } },
      title: {
        display: true,
        text: "Interview Evaluation Scores",
        color: "white",
        font: { size: 20 },
      },
    },
  };

  return (
    <div className="mt-6 bg-white bg-opacity-10 rounded-lg p-6 shadow-lg">
      <h3 className="text-2xl font-semibold mb-4">Your Evaluation</h3>

      <p className="text-lg mb-2">
        <strong>Q:</strong> {report.question}
      </p>
      <p className="text-md mb-2 italic">
        <strong>Transcript:</strong> {report.transcription}
      </p>

      <div className="mb-4">
        <h4 className="text-xl font-semibold">🤖 AI Feedback:</h4>
        <p>{report.feedback}</p>
      </div>

      {report.mispronounced_words?.length > 0 && (
        <div className="mb-4">
          <h4 className="text-xl font-semibold">❌ Mispronounced Words:</h4>
          <ul className="list-disc list-inside text-red-400">
            {report.mispronounced_words.map((word, idx) => (
              <li key={idx}>
                <span className="font-semibold">{word.word}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-6">
        <Bar data={data} options={options} />
      </div>
    </div>
  );
};

export default Results;
