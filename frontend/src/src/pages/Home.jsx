import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
      <h1 className="text-5xl font-extrabold text-center text-gray-800 mb-4">
        Ace Your Next Interview with MockAI!
      </h1>
      <p className="text-xl text-gray-600 mb-8 text-center">
        Practice with AI-powered mock interviews and receive instant feedback.
      </p>
      <Link
        to="/upload"
        className="bg-purple-600 text-white px-8 py-4 rounded-lg shadow-lg hover:bg-purple-700 transition"
      >
        Start Interview
      </Link>
    </div>
  );
};

export default Home;
