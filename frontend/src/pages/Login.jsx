import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { heroBackground } from "../assets";
import Section from "../components/Section";
import { Rings } from "../components/design/Hero";

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("User logged in:", formData);
    const userData = {
      username: "Jaini",
      email: "jainishah1641@gmail.com",
    };
    localStorage.setItem("user", JSON.stringify(userData));

    navigate("/"); // Redirect after login
    window.location.reload(); // Reload to update header UI
  };

  return (
    <Section className="relative min-h-screen flex flex-col items-center justify-center p-6 text-center">
      {/* Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <img
          src={heroBackground}
          alt="hero background"
          className="w-full object-cover blur-lg"
          width={1440}
          height={1800}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 bg-white bg-opacity-10 backdrop-blur-lg shadow-xl rounded-xl p-8 max-w-lg w-full">
        <h2 className="text-4xl font-extrabold text-white mb-6">Log In</h2>
        <p className="text-lg opacity-70 mb-6">
          Welcome back! Continue sharpening your interview skills with AI-driven
          insights
        </p>
        {error && <p className="text-red-500 text-center">{error}</p>}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
          />

          <button
            type="submit"
            className="w-full px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105"
          >
            Log In
          </button>
        </form>

        <p className="text-white mt-8">
          Don't have an account?{" "}
          <button
            onClick={() => navigate("/signup")}
            className="text-purple-300 underline"
          >
            Sign Up
          </button>
        </p>

        <p className="text-white mt-5">
          <button
            onClick={() => navigate("/forgetpassword")}
            className="text-purple-300 underline"
          >
            Forgot Password?
          </button>
        </p>
      </div>
      <Rings />
    </Section>
  );
};

export default Login;
