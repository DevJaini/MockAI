import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { heroBackground } from "../assets";
import Section from "../components/Section";
import { Rings } from "../components/design/Hero";

const Signup = () => {
  const navigate = useNavigate();

  // Form data state for signup
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [error, setError] = useState("");

  // Update form values dynamically
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle signup form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    console.log("User signed up:", formData);
    navigate("/login"); // Redirect to login after signup
  };

  return (
    <Section className="relative min-h-screen flex flex-col items-center justify-center p-6 text-center">
      {/* Background image with blur */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <img
          src={heroBackground}
          alt="hero background"
          className="w-full object-cover blur-lg"
          width={1440}
          height={1800}
        />
      </div>

      {/* Signup Form */}
      <div className="relative z-10 bg-white bg-opacity-10 backdrop-blur-lg shadow-xl rounded-xl p-8 max-w-lg w-full">
        <h2 className="text-4xl font-extrabold text-white mb-6">Sign Up</h2>

        {error && <p className="text-red-500 text-center">{error}</p>}

        <p className="text-lg opacity-70 mb-6">
          Join MockAI and take your job interview preparation to the next level!
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            name="username"
            placeholder="Full Name"
            value={formData.username}
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
          />
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
          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            className="w-full p-3 border border-gray-300 rounded-lg shadow-sm bg-white text-gray-900"
          />

          <button
            type="submit"
            className="w-full px-6 py-3 bg-purple-500 text-white font-bold rounded-lg shadow-md hover:bg-purple-600 transition transform hover:scale-105"
          >
            Sign Up
          </button>
        </form>

        {/* Redirect link for existing users */}
        <p className="text-white mt-8">
          Already have an account?{" "}
          <button
            onClick={() => navigate("/login")}
            className="text-purple-300 underline"
          >
            Log in
          </button>
        </p>
      </div>

      {/* Decorative background animation */}
      <Rings />
    </Section>
  );
};

export default Signup;
