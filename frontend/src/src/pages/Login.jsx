import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    // Replace this with your actual login logic
    console.log("Logging in with", email, password);
    navigate("/profile"); // after successful login, redirect to profile or dashboard
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-lg shadow-md w-96"
      >
        <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center">
          Login
        </h2>
        <input
          type="email"
          placeholder="Email"
          className="w-full p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:border-blue-600"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full p-3 border border-gray-300 rounded mb-4 focus:outline-none focus:border-blue-600"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button
          type="submit"
          className="w-full bg-purple-600 text-white py-3 rounded hover:bg-purple-700 transition"
        >
          Login
        </button>
        <div className="mt-4 text-center">
          <Link to="/forgot-password" className="text-blue-600 hover:underline">
            Forgot Password?
          </Link>
        </div>
      </form>
    </div>
  );
};

export default Login;
